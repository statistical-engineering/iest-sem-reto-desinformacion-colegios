/* Panel docente. La clave se guarda solo en esta pestaña (sessionStorage).
   Con la clave de una sala se maneja solo esa sala. Con la del semillero se ven todas las salas: se crean, se
   les cambia la clave, se borran, y se entra al panel de cualquiera (las peticiones llevan ?sala=). */
(function () {
  "use strict";
  const app = document.getElementById("app");
  const A = { clave: null, rol: null, sala: null, datos: null, filtroGrado: "", filtroColegio: "", busqueda: "", montado: false, pausaHasta: 0, recibido: 0 };
  const PASOS = [
    ["inscripcion", "Inscripción", "Los estudiantes se inscriben y esperan"],
    ["abierto", "Reto abierto", "Corre el reloj de esta sala"],
    ["cerrado", "Cerrado", "Se entregan todos los intentos"],
    ["resultados", "Resultados", "Podio y revisión de respuestas"],
  ];
  const ESTADOS = { registrado: "Inscrito", en_curso: "Respondiendo", finalizado: "Entregó", descalificado: "Anulado", no_inicio: "No inició" };

  function h(tag, attrs, ...hijos) {
    const e = document.createElement(tag);
    for (const k in attrs || {}) {
      const v = attrs[k];
      if (v == null || v === false) continue;
      if (k === "class") e.className = v;
      else if (k === "text") e.textContent = v;
      else if (k.startsWith("on")) e.addEventListener(k.slice(2), v);
      else e.setAttribute(k, v === true ? "" : v);
    }
    for (const c of hijos.flat()) if (c != null && c !== false) e.append(c.nodeType ? c : document.createTextNode(String(c)));
    return e;
  }
  const num = (v, d = 0) => (v == null ? "—" : Number(v).toLocaleString("es-CO", { minimumFractionDigits: d, maximumFractionDigits: d }));
  const mmss = (s) => (s == null ? "—" : `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, "0")}`);
  const ses = { get: (k) => { try { return sessionStorage.getItem(k); } catch (e) { return null; } }, set: (k, v) => { try { sessionStorage.setItem(k, v); } catch (e) { /* nada */ } } };

  // la sala va en la URL; la clave, siempre en la cabecera (nunca en la URL)
  const conSala = (ruta) => (A.sala ? ruta + (ruta.includes("?") ? "&" : "?") + "sala=" + encodeURIComponent(A.sala) : ruta);
  async function api(ruta, datos, sinSala) {
    const op = { headers: { "Content-Type": "application/json", "X-Clave-Admin": A.clave || "" } };
    if (datos !== undefined) { op.method = "POST"; op.body = JSON.stringify(datos); }
    const r = await fetch(sinSala ? ruta : conSala(ruta), op);
    const j = await r.json().catch(() => ({}));
    if (!r.ok) throw Object.assign(new Error(j.error || "Error " + r.status), { codigo: r.status });
    return j;
  }
  function confirmarDoble(boton, texto, accion) {
    let armado = false;
    const original = boton.textContent;
    boton.addEventListener("click", async () => {
      if (!armado) {
        armado = true; boton.classList.add("confirmar"); boton.textContent = texto;
        A.pausaHasta = Date.now() + 4200; // no redibujar mientras se espera la confirmación
        setTimeout(() => { armado = false; boton.classList.remove("confirmar"); boton.textContent = original; }, 4000);
        return;
      }
      boton.disabled = true;
      A.pausaHasta = 0;
      try { await accion(); } catch (e) { alert(e.message); }
      boton.disabled = false; armado = false; boton.classList.remove("confirmar"); boton.textContent = original;
      refrescar();
    });
    return boton;
  }

  // ---------------------------------------------------------------- login
  function login(msg) {
    A.montado = false;
    const f = h("form", { class: "tarjeta", id: "login", onsubmit: async (ev) => {
      ev.preventDefault();
      A.clave = f.clave.value.trim().toUpperCase();
      try { await entrar(); refrescar(); } catch (e) { login(e.message); }
    } },
      h("div", { class: "antetitulo", text: "Acceso docente" }),
      h("h2", { style: "font-size:32px;margin-bottom:12px", text: "Panel del reto" }),
      h("p", { class: "nota", text: "Escribe la clave de tu sala (empieza con el código de la sala, por ejemplo KQMT-…): te la entrega el semillero. Con la clave del semillero ves todas las salas. No la compartas con estudiantes." }),
      h("label", { class: "campo" }, h("span", { text: "Clave docente" }), h("input", { class: "entrada codigo", name: "clave", autocomplete: "off", required: true })),
      h("button", { class: "boton grande", type: "submit" }, "Entrar"),
      msg ? h("div", { class: "aviso", text: msg }) : null);
    app.replaceChildren(f);
    f.clave.focus();
  }

  async function entrar() {
    const r = await api("/api/admin/login", {}, true);
    A.rol = r.rol;
    A.sala = r.rol === "sala" ? r.sala : ses.get("reto_sala") || null;
    ses.set("reto_clave", A.clave);
  }
  function irASala(codigo) {
    A.sala = codigo; ses.set("reto_sala", codigo || ""); A.montado = false; A.datos = null;
    A.filtroColegio = ""; A.busqueda = "";
    refrescar();
  }

  // ---------------------------------------------------------------- salas (solo semillero)
  async function pintarSalas(nueva) {
    A.montado = false;
    const { salas } = await api("/api/admin/salas", undefined, true);
    const evento = h("input", { class: "entrada", placeholder: "Nombre del colegio o del evento", maxlength: 80 });
    const crear = h("button", { class: "boton" }, "＋ Crear sala");
    crear.onclick = async () => {
      crear.disabled = true;
      try { pintarSalas(await api("/api/admin/salas/crear", { evento: evento.value.trim() }, true)); }
      catch (e) { alert(e.message); crear.disabled = false; }
    };
    const enSala = async (codigo, ruta, datos) => {
      A.sala = codigo;
      try { return await api(ruta, datos); } finally { A.sala = null; }
    };
    const fila = (s) => {
      const acciones = h("div", { class: "acciones-fila" });
      const abrir = h("button", { type: "button" }, "Abrir panel");
      abrir.onclick = () => irASala(s.sala);
      const clave = h("button", { type: "button", title: "La clave anterior deja de servir" }, "Nueva clave");
      confirmarDoble(clave, "¿Cambiar la clave?", async () => pintarSalas(await enSala(s.sala, "/api/admin/salas/clave", {})));
      acciones.append(abrir, clave);
      if (s.estado === "cerrado" || s.estado === "resultados") {
        const borrar = h("button", { type: "button" }, "Borrar");
        borrar.onclick = async () => {
          if (prompt(`Para borrar la sala ${s.sala} con todos sus datos y copias, escribe BORRAR`) !== "BORRAR") return;
          try { await enSala(s.sala, "/api/admin/salas/borrar", { confirmar: "BORRAR" }); } catch (e) { alert(e.message); }
          pintarSalas();
        };
        acciones.append(borrar);
      }
      const paso = PASOS.find((x) => x[0] === s.estado);
      return h("tr", {}, h("td", { class: "maquina", text: s.sala }), h("td", { text: s.evento }),
        h("td", { text: paso ? paso[1] : s.estado }), h("td", { class: "n", text: s.inscritos }), h("td", {}, acciones));
    };
    app.replaceChildren(
      h("div", { class: "antetitulo", text: "Semillero · todas las salas" }),
      h("h2", { style: "font-size:30px;margin-bottom:8px", text: "Salas del reto" }),
      h("p", { class: "nota", text: "Crea una sala por colegio. Cada sala tiene su código, su clave de docente, su reloj, su tablero y su podio. Entrega a cada docente el código y la clave de su sala." }),
      nueva ? h("div", { class: "aviso", style: "margin:12px 0" }, `Sala ${nueva.sala} · clave del docente: `, h("b", { class: "maquina", text: nueva.clave }),
        " · Anótala y entrégasela al docente: no se vuelve a mostrar.") : "",
      h("div", { class: "controles", style: "margin:16px 0" }, evento, crear),
      h("div", { class: "tabla-wrap" }, h("table", { class: "participantes" },
        h("thead", {}, h("tr", {}, ...["Sala", "Evento", "Estado", "Inscritos", ""].map((x) => h("th", { text: x })))),
        h("tbody", {}, ...salas.map(fila),
          salas.length ? null : h("tr", {}, h("td", { colspan: 5, class: "nota", style: "text-align:center;padding:24px", text: "Aún no hay salas." }))))));
  }

  // ---------------------------------------------------------------- panel
  async function refrescar() {
    try {
      if (!A.rol) await entrar();
      if (A.rol === "semillero" && !A.sala) return await pintarSalas();
      A.datos = await api("/api/admin/resumen");
      A.recibido = performance.now();
      if (!A.montado) montar();
      actualizar();
    } catch (e) {
      if (e.codigo === 403) return login("Clave incorrecta.");
      if (e.codigo === 404 && A.rol === "semillero") return irASala(null); // la sala ya no existe
    }
  }
  setInterval(() => { if (A.clave && A.montado && Date.now() > A.pausaHasta) refrescar(); }, 3000);
  // reloj de la sala en vivo (entre refrescos se descuenta localmente)
  setInterval(() => {
    const el = document.getElementById("reloj-adm");
    if (!el || !A.datos || !A.datos.reloj || A.datos.reloj.restante_seg == null) return;
    const r = A.datos.reloj;
    const rest = r.pausado ? r.restante_seg : Math.max(0, r.restante_seg - (performance.now() - A.recibido) / 1000);
    el.textContent = r.pausado ? "⏸ " + mmss(rest) : mmss(Math.ceil(rest));
    el.className = "reloj-adm" + (r.pausado ? " pausa" : rest <= 120 ? " critico" : rest <= 600 ? " alerta" : "");
  }, 250);

  function montar() {
    A.montado = true;
    const volver = A.rol === "semillero" ? h("button", { class: "boton chico claro", style: "margin-bottom:12px", onclick: () => irASala(null) }, "← Todas las salas") : null;
    app.replaceChildren(volver || "",
      h("div", { class: "antetitulo", text: `Control del reto · sala ${A.sala}` }),
      h("div", { class: "pasos", id: "pasos" }),
      h("div", { class: "controles", id: "controles" }),
      h("div", { class: "rejilla-adm" },
        h("div", { class: "tarjeta", id: "acceso" }),
        h("div", { class: "tarjeta", id: "config" }),
        h("div", { class: "tarjeta", id: "experimento" })),
      h("div", { class: "kpis", id: "kpis", style: "margin-bottom:20px" }),
      h("div", { class: "filtros" },
        h("h2", { style: "font-size:26px;margin-right:auto", text: "Participantes y clasificación" }),
        h("select", { class: "entrada", id: "f-grado", onchange: (e) => { A.filtroGrado = e.target.value; actualizarTabla(); } },
          h("option", { value: "" }, "Todos los grados"), h("option", { value: "9" }, "Grado 9.°"), h("option", { value: "10" }, "Grado 10.°"), h("option", { value: "11" }, "Grado 11.°")),
        h("select", { class: "entrada", id: "f-colegio", onchange: (e) => { A.filtroColegio = e.target.value; actualizarTabla(); } }),
        h("input", { class: "entrada", id: "f-busca", placeholder: "Buscar nombre, colegio o código", oninput: (e) => { A.busqueda = e.target.value.toLowerCase(); actualizarTabla(); } }),
        h("a", { class: "boton chico claro", href: "#", id: "exp-res" }, "⬇ Resultados (CSV)"),
        h("a", { class: "boton chico claro", href: "#", id: "exp-resp" }, "⬇ Respuestas detalladas (CSV)")),
      h("div", { class: "tabla-wrap" }, h("table", { class: "participantes" },
        h("thead", {}, h("tr", {}, ...["Puesto", "Código", "Participante", "Exp.", "Estado", "Progreso", "Puntos", "Bono", "Total", "Nota", "Tiempo", "Salidas", ""].map((t) => h("th", { text: t })))),
        h("tbody", { id: "cuerpo" }))),
      h("p", { class: "nota", text: "Desempate automático: puntaje total ↓ → puntos ↓ → momento de la última respuesta ↑ → hora de entrega ↑. «Salidas» cuenta cuántas veces el estudiante dejó la pestaña del reto (≥ 3 se marca en rojo): revísalo antes de premiar. «Exp.» es el grupo del experimento del Expediente 01 (B recibió el recordatorio de exactitud)." }),
      h("div", { class: "peligro-zona", id: "peligro" }));
    const descargar = (ruta, nombre) => async (ev) => {
      ev.preventDefault();
      const r = await fetch(conSala(ruta), { headers: { "X-Clave-Admin": A.clave } });
      const blob = await r.blob();
      const a = h("a", { href: URL.createObjectURL(blob), download: nombre });
      document.body.append(a); a.click(); a.remove();
    };
    document.getElementById("exp-res").onclick = descargar("/api/admin/resultados.csv", `resultados_reto_${A.sala}.csv`);
    document.getElementById("exp-resp").onclick = descargar("/api/admin/respuestas.csv", `respuestas_detalle_${A.sala}.csv`);
    const reset = h("input", { class: "entrada", placeholder: "Escribe BORRAR", style: "max-width:220px" });
    const bReset = h("button", { class: "boton peligro" }, "Reiniciar esta sala");
    bReset.onclick = async () => {
      try { const r = await api("/api/admin/reiniciar", { confirmar: reset.value.trim() }); alert("Sala reiniciada. Copia de seguridad: datos/copias/" + r.copia); reset.value = ""; refrescar(); }
      catch (e) { alert(e.message); }
    };
    document.getElementById("peligro").append(h("b", { text: "Zona de peligro. " }),
      h("span", { class: "nota", text: "Borra las inscripciones y respuestas de ESTA sala para hacer un reto nuevo; las demás salas no se tocan. Antes se guarda en el servidor una copia automática de los datos de la sala." }),
      h("div", { class: "controles", style: "margin-top:10px" }, reset, bReset));
  }

  function actualizar() {
    const d = A.datos, c = d.config, estado = c.estado;
    const idx = PASOS.findIndex((p) => p[0] === estado);
    document.getElementById("pasos").replaceChildren(...PASOS.map((p, i) =>
      h("div", { class: "paso" + (i < idx ? " hecho" : i === idx ? " actual" : "") }, h("b", { text: p[1] }), h("span", { text: p[2] }))));

    const ctrl = document.getElementById("controles");
    ctrl.replaceChildren();
    const cambiar = (nuevo) => () => api("/api/admin/estado", { estado: nuevo });
    if (estado === "inscripcion")
      ctrl.append(confirmarDoble(h("button", { class: "boton grande" }, "▶ Abrir el reto"), "¿Abrir ya? Toca otra vez", cambiar("abierto")),
        h("span", { class: "nota", text: "Cuando abras, cada estudiante verá el botón «Comenzar». Pídeles que lo pulsen todos a la vez." }));
    if (estado === "abierto") {
      const r = d.reloj, reloj = (datos) => () => api("/api/admin/reloj", datos);
      const boton = (txt, datos, clase) => {
        const b = h("button", { class: "boton " + (clase || "") }, txt);
        b.onclick = async () => { b.disabled = true; try { await reloj(datos)(); } catch (e) { alert(e.message); } b.disabled = false; refrescar(); };
        return b;
      };
      ctrl.append(
        h("div", { class: "reloj-caja" }, h("small", { text: "Reloj de la sala " + c.sala }), h("div", { id: "reloj-adm", class: "reloj-adm", text: "--:--" })),
        r.pausado ? boton("▶ Reanudar", { accion: "reanudar" }, "grande")
          : confirmarDoble(h("button", { class: "boton grande claro" }, "⏸ Pausar"), "¿Pausar la sala? Toca otra vez", reloj({ accion: "pausar" })),
        boton("+5 min", { accion: "sumar", minutos: 5 }, "claro"), boton("+1 min", { accion: "sumar", minutos: 1 }, "claro"),
        boton("−1 min", { accion: "sumar", minutos: -1 }, "claro"), boton("−5 min", { accion: "sumar", minutos: -5 }, "claro"),
        confirmarDoble(h("button", { class: "boton grande peligro" }, "■ Cerrar el reto"), "Se entregará a toda la sala. ¿Seguro?", cambiar("cerrado")),
        h("span", { class: "nota", style: "flex-basis:100%", text: `Duración ${num(r.duracion_seg / 60, 1)} min${Number(c.extra_seg) ? ` (incluye ${num(Number(c.extra_seg) / 60, 0)} min de ajuste)` : ""} · corridos ${mmss(r.transcurrido_seg)}. En pausa nadie puede enviar respuestas y el reloj no avanza. Al llegar a cero, el reto se cierra solo para toda la sala.` }));
    }
    if (estado === "cerrado")
      ctrl.append(confirmarDoble(h("button", { class: "boton grande" }, "🏆 Publicar resultados"), "¿Publicar podio? Toca otra vez", cambiar("resultados")),
        h("span", { class: "nota", text: "Revisa la tabla (salidas de pestaña) antes de publicar. Al publicar, el tablero muestra el podio y los estudiantes ven su puesto y la revisión." }));
    if (estado === "resultados")
      ctrl.append(h("span", { class: "nota", text: "Resultados publicados. Descarga los CSV para el acta de premiación." }));

    const urls = d.urls.map((u) => h("div", {}, h("span", { class: "url", text: u })));
    const enLinea = d.urls.length > 0 && !/^http:\/\/(\d|localhost|\[)/.test(d.urls[0]);
    const porColegio = d.por_colegio || [];
    document.getElementById("acceso").replaceChildren(
      h("h3", { style: "font-size:20px;margin-bottom:8px", text: "Cómo entran los estudiantes" }),
      h("p", { class: "nota", style: "margin:0 0 6px", text: enLinea ? "Desde cualquier celular o computador con internet, en cualquier colegio, abren:" : "Con el celular o computador conectado a la MISMA red wifi, abren:" }), ...urls,
      h("p", { style: "margin:14px 0 4px" }, "Código de sala: ", h("span", { class: "url", style: "font-size:24px", text: c.sala })),
      h("p", { class: "nota", style: "margin:6px 0 0" }, "Enlace con la sala ya puesta: ", h("span", { class: "url", text: `${d.urls[0]}/?sala=${c.sala}` })),
      h("p", { class: "nota", style: "margin:10px 0 0" }, "Proyecta el tablero: ", h("a", { href: "/tablero?sala=" + encodeURIComponent(c.sala), target: "_blank", rel: "noopener", text: `${d.urls[0]}/tablero?sala=${c.sala}` })),
      h("p", { class: "nota", style: "margin:6px 0 0", text: `Banco de preguntas v${d.banco.version}: ${d.banco.preguntas} preguntas, ${d.banco.puntos_totales} puntos + bono hasta ${d.banco.bono_max}.` }),
      porColegio.length ? h("div", { style: "margin-top:12px" }, h("b", { text: "Inscritos por colegio" }),
        ...porColegio.map((x) => h("div", { class: "exp-fila" }, h("span", { text: x.colegio }), h("b", { text: x.n })))) : "");
    document.getElementById("ir-tablero").href = "/tablero?sala=" + encodeURIComponent(c.sala);
    const fCol = document.getElementById("f-colegio");
    const opciones = ["", ...new Set([...(d.colegios || []), ...porColegio.map((x) => x.colegio)])];
    if (fCol.options.length !== opciones.length) fCol.replaceChildren(...opciones.map((o) => h("option", { value: o }, o || "Todos los colegios")));
    fCol.value = A.filtroColegio;

    if (!document.getElementById("cfg-montado")) montarConfig();
    sincronizarConfig();
    pintarExperimento();

    const ps = d.participantes;
    const cuenta = (e) => ps.filter((p) => p.estado === e).length;
    const fin = ps.filter((p) => p.estado === "finalizado");
    document.getElementById("kpis").replaceChildren(
      h("div", {}, h("span", { text: "Inscritos" }), h("b", { text: ps.filter((p) => p.estado !== "descalificado").length })),
      h("div", {}, h("span", { text: "Respondiendo ahora" }), h("b", { text: cuenta("en_curso") })),
      h("div", {}, h("span", { text: "Entregaron" }), h("b", { text: fin.length })),
      h("div", {}, h("span", { text: "Promedio de puntos (entregados)" }), h("b", { text: fin.length ? num(fin.reduce((a, p) => a + p.puntos, 0) / fin.length, 1) : "—" })));
    actualizarTabla();
  }

  function montarConfig() {
    const box = document.getElementById("config");
    box.replaceChildren(h("span", { id: "cfg-montado", class: "oculto" }),
      h("h3", { style: "font-size:20px;margin-bottom:4px", text: "Configuración" }),
      interruptor("modo_sorpresa", "Modo sorpresa", "El tablero oculta la clasificación hasta publicar resultados."),
      interruptor("retro", "Retroalimentación inmediata", "El estudiante ve si acertó cada pregunta al enviarla (sin la explicación)."),
      filaCfg("evento", "Nombre del evento", "text"),
      filaCfg("duracion_min", "Duración (minutos) · solo antes de abrir", "number"),
      filaColegios());
  }
  function filaColegios() {
    const ta = h("textarea", { class: "entrada", id: "cfg-colegios", rows: 5, placeholder: "Un colegio por línea (al menos uno): los estudiantes solo pueden elegir de esta lista." });
    const b = h("button", { class: "boton chico", type: "button" }, "Guardar lista");
    b.onclick = async () => {
      try { await api("/api/admin/config", { colegios: ta.value }); ta.dataset.editando = ""; } catch (e) { alert(e.message); }
      refrescar();
    };
    ta.addEventListener("input", () => { ta.dataset.editando = "1"; });
    return h("div", { style: "margin-top:12px" }, h("label", { class: "campo" }, h("span", { text: "Colegios participantes (los estudiantes eligen de esta lista)" }), ta), b);
  }
  function interruptor(clave, titulo, ayuda) {
    const inp = h("input", { type: "checkbox", id: "cfg-" + clave, onchange: async (e) => {
      try { await api("/api/admin/config", { [clave]: e.target.checked }); } catch (er) { alert(er.message); }
      refrescar();
    } });
    return h("label", { class: "interruptor" }, h("span", {}, h("b", { text: titulo }), h("small", { text: ayuda })), inp);
  }
  function filaCfg(clave, titulo, tipo) {
    const inp = h("input", { class: "entrada", id: "cfg-" + clave, type: tipo });
    const b = h("button", { class: "boton chico", type: "button" }, "Guardar");
    b.onclick = async () => {
      try { await api("/api/admin/config", { [clave]: tipo === "number" ? Number(inp.value) : inp.value }); inp.dataset.editando = ""; }
      catch (e) { alert(e.message); }
      refrescar();
    };
    inp.addEventListener("input", () => { inp.dataset.editando = "1"; });
    return h("div", { class: "fila-cfg" }, h("label", { class: "campo" }, h("span", { text: titulo }), inp), b);
  }
  function sincronizarConfig() {
    const c = A.datos.config;
    document.getElementById("cfg-modo_sorpresa").checked = c.modo_sorpresa === "1";
    document.getElementById("cfg-retro").checked = c.retro === "1";
    for (const k of ["evento", "duracion_min"]) {
      const inp = document.getElementById("cfg-" + k);
      if (!inp.dataset.editando && document.activeElement !== inp) inp.value = c[k];
    }
    document.getElementById("cfg-duracion_min").disabled = c.estado !== "inscripcion";
    const ta = document.getElementById("cfg-colegios");
    if (!ta.dataset.editando && document.activeElement !== ta) ta.value = (A.datos.colegios || []).join("\n");
  }

  function pintarExperimento() {
    const x = A.datos.experimento, box = document.getElementById("experimento");
    const pct = (v) => (v == null ? "—" : num(v, 0) + " %");
    if (!x.listo) {
      box.replaceChildren(h("h3", { style: "font-size:20px;margin-bottom:8px", text: "Experimento de la clase" }),
        h("p", { class: "nota", text: `Aparece cuando al menos 2 estudiantes completen el Expediente 01 (van ${x.n}). Replica el estudio de Nature: ¿compartimos cosas que reconoceríamos como falsas?` }));
      return;
    }
    const c = x.clase, a = x.grupo_sin_recordatorio, b = x.grupo_con_recordatorio;
    box.replaceChildren(h("h3", { style: "font-size:20px;margin-bottom:8px", text: `Experimento de la clase (n = ${x.n})` }),
      h("div", { class: "exp-fila" }, h("span", { text: "Compartirían publicaciones FALSAS" }), h("b", { text: pct(c.comparte_falsas) })),
      h("div", { class: "exp-fila" }, h("span", { text: "Creyeron verdaderas las FALSAS" }), h("b", { text: pct(c.cree_falsas) })),
      h("div", { class: "exp-fila" }, h("span", { text: "Sin recordatorio: comparten falsas" }), h("b", { text: a ? `${pct(a.comparte_falsas)} (n=${a.n})` : "—" })),
      h("div", { class: "exp-fila" }, h("span", { text: "Con recordatorio: comparten falsas" }), h("b", { text: b ? `${pct(b.comparte_falsas)} (n=${b.n})` : "—" })),
      h("div", { class: "exp-fila" }, h("span", { text: "Aciertos de la multitud (promedio de la clase)" }), h("b", { text: `${x.multitud.aciertos_multitud}/${x.total_posts}` })),
      h("div", { class: "exp-fila" }, h("span", { text: "Aciertos del estudiante promedio" }), h("b", { text: `${num(x.multitud.promedio_individual, 1)}/${x.total_posts}` })),
      h("p", { class: "nota", style: "margin:8px 0 0", text: "Es una demostración de clase, no una investigación: con pocos estudiantes, las diferencias pueden ser azar." }));
  }

  function actualizarTabla() {
    const d = A.datos;
    let filas = d.participantes.slice();
    if (A.filtroGrado) filas = filas.filter((p) => p.grado === A.filtroGrado);
    if (A.filtroColegio) filas = filas.filter((p) => p.colegio === A.filtroColegio);
    if (A.busqueda) filas = filas.filter((p) => `${p.nombre} ${p.colegio} ${p.codigo}`.toLowerCase().includes(A.busqueda));
    filas.sort((x, y) => (x.puesto || 1e6) - (y.puesto || 1e6) || x.id - y.id);
    let rel = 0;
    const cuerpo = document.getElementById("cuerpo");
    cuerpo.replaceChildren(...filas.map((p) => {
      const puestoMostrado = p.puesto ? (A.filtroGrado || A.filtroColegio ? ++rel : p.puesto) : null;
      const acciones = h("div", { class: "acciones-fila" });
      const accion = (txt, ac, confirmar) => {
        const b = h("button", { type: "button", title: confirmar }, txt);
        confirmarDoble(b, "¿Seguro?", () => api("/api/admin/participante", { id: p.id, accion: ac }));
        acciones.append(b);
      };
      if (p.estado === "en_curso") { accion("Entregar", "finalizar", "Entrega el intento ahora"); accion("Anular", "descalificar", "Anula la participación"); }
      if (p.estado === "finalizado") accion("Anular", "descalificar", "Anula la participación");
      if (p.estado === "descalificado") accion("Reactivar", "reactivar", "Devuelve la participación");
      if (p.estado === "registrado" || p.estado === "no_inicio") accion("Eliminar", "eliminar", "Borra la inscripción");
      const tiempo = p.estado === "en_curso" ? "respondiendo" : p.tiempo_usado != null ? mmss(p.tiempo_usado) : "—";
      return h("tr", { class: puestoMostrado && puestoMostrado <= 3 ? `podio-${puestoMostrado}` : "" },
        h("td", { class: "puesto", text: puestoMostrado ? puestoMostrado + "." : "" }),
        h("td", { class: "maquina", text: p.codigo }),
        h("td", { class: "quien" }, h("b", { text: p.nombre }), h("small", { text: `${p.colegio} · ${p.grado}.°${p.integrantes ? " · " + p.integrantes : ""}` })),
        h("td", { text: p.grupo }),
        h("td", {}, h("span", { class: "estado " + p.estado, text: ESTADOS[p.estado] || p.estado })),
        h("td", {}, h("div", { class: "progreso", title: `${p.respondidas}/${p.total_preguntas}` }, h("i", { style: `width:${(100 * p.respondidas) / p.total_preguntas}%` })), h("small", { text: `${p.respondidas}/${p.total_preguntas}` })),
        h("td", { class: "n", text: num(p.puntos, 2) }),
        h("td", { class: "n", text: p.estado === "finalizado" ? num(p.bono, 3) : "—" }),
        h("td", { class: "n" }, h("b", { text: p.estado === "finalizado" ? num(p.total, 3) : "—" })),
        h("td", { class: "n", text: p.nota != null ? num(p.nota, 1) : "—" }),
        h("td", { class: "n", text: tiempo }),
        h("td", { class: "n" + (p.salidas >= 3 ? " alerta-salidas" : ""), text: p.salidas }),
        h("td", {}, acciones));
    }));
    if (!filas.length) cuerpo.append(h("tr", {}, h("td", { colspan: 13, class: "nota", style: "text-align:center;padding:24px", text: "Aún no hay participantes." })));
  }

  A.clave = ses.get("reto_clave"); // el rol y la sala se vuelven a pedir al servidor en refrescar()
  if (A.clave) refrescar(); else login();
})();
