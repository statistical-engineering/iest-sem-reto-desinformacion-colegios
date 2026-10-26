/* Panel docente. La clave se guarda solo en esta pestaña (sessionStorage). */
(function () {
  "use strict";
  const app = document.getElementById("app");
  const A = { clave: null, datos: null, filtroGrado: "", busqueda: "", montado: false, pausaHasta: 0 };
  const PASOS = [
    ["inscripcion", "Inscripción", "Los estudiantes se inscriben y esperan"],
    ["abierto", "Reto abierto", "Pulsan «Comenzar»: corre su reloj"],
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

  async function api(ruta, datos) {
    const op = { headers: { "Content-Type": "application/json", "X-Clave-Admin": A.clave || "" } };
    if (datos !== undefined) { op.method = "POST"; op.body = JSON.stringify(datos); }
    const r = await fetch(ruta, op);
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
      try { await api("/api/admin/login", {}); ses.set("reto_clave", A.clave); refrescar(); }
      catch (e) { login(e.message); }
    } },
      h("div", { class: "antetitulo", text: "Acceso docente" }),
      h("h2", { style: "font-size:32px;margin-bottom:12px", text: "Panel del reto" }),
      h("p", { class: "nota", text: "La clave aparece en la ventana negra donde se inició el servidor (y en datos/clave_docente.txt)." }),
      h("label", { class: "campo" }, h("span", { text: "Clave docente" }), h("input", { class: "entrada codigo", name: "clave", autocomplete: "off", required: true })),
      h("button", { class: "boton grande", type: "submit" }, "Entrar"),
      msg ? h("div", { class: "aviso", text: msg }) : null);
    app.replaceChildren(f);
    f.clave.focus();
  }

  // ---------------------------------------------------------------- panel
  async function refrescar() {
    try {
      A.datos = await api("/api/admin/resumen");
      if (!A.montado) montar();
      actualizar();
    } catch (e) {
      if (e.codigo === 403) return login("Clave incorrecta.");
    }
  }
  setInterval(() => { if (A.clave && A.montado && Date.now() > A.pausaHasta) refrescar(); }, 3000);

  function montar() {
    A.montado = true;
    app.replaceChildren(
      h("div", { class: "antetitulo", text: "Control del reto" }),
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
      const r = await fetch(ruta, { headers: { "X-Clave-Admin": A.clave } });
      const blob = await r.blob();
      const a = h("a", { href: URL.createObjectURL(blob), download: nombre });
      document.body.append(a); a.click(); a.remove();
    };
    document.getElementById("exp-res").onclick = descargar("/api/admin/resultados.csv", "resultados_reto.csv");
    document.getElementById("exp-resp").onclick = descargar("/api/admin/respuestas.csv", "respuestas_detalle.csv");
    const reset = h("input", { class: "entrada", placeholder: "Escribe BORRAR", style: "max-width:220px" });
    const bReset = h("button", { class: "boton peligro" }, "Reiniciar todo el reto");
    bReset.onclick = async () => {
      try { const r = await api("/api/admin/reiniciar", { confirmar: reset.value.trim() }); alert("Reto reiniciado. Copia de seguridad: datos/" + r.copia); reset.value = ""; refrescar(); }
      catch (e) { alert(e.message); }
    };
    document.getElementById("peligro").append(h("b", { text: "Zona de peligro. " }),
      h("span", { class: "nota", text: "Borra inscripciones y respuestas para usar el reto con otro grupo. Antes se guarda una copia automática en la carpeta datos/." }),
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
        h("span", { class: "nota", text: c.reloj_global === "1" ? `Reloj global: al abrir arranca el reloj de ${num(c.duracion_min)} min para TODOS y termina a la misma hora. Pídeles que pulsen «Comenzar» enseguida.` : "Cuando abras, cada estudiante verá el botón «Comenzar». Pídeles que lo pulsen todos a la vez." }));
    if (estado === "abierto")
      ctrl.append(confirmarDoble(h("button", { class: "boton grande peligro" }, "■ Cerrar el reto"), "Se entregará a TODOS. ¿Seguro?", cambiar("cerrado")),
        h("span", { class: "nota", text: `Abierto hace ${mmss(d.servidor_ahora - Number(c.abierto_en))}. ` + (c.reloj_global === "1" ? `Reloj global: el reto termina a los ${num(c.duracion_min)} min de haberlo abierto, para todos; al vencerse se entrega solo.` : `Cada estudiante tiene ${num(c.duracion_min)} min desde que pulsó «Comenzar»; al vencerse se entrega solo.`) }));
    if (estado === "cerrado")
      ctrl.append(confirmarDoble(h("button", { class: "boton grande" }, "🏆 Publicar resultados"), "¿Publicar podio? Toca otra vez", cambiar("resultados")),
        h("span", { class: "nota", text: "Revisa la tabla (salidas de pestaña) antes de publicar. Al publicar, el tablero muestra el podio y los estudiantes ven su puesto y la revisión." }));
    if (estado === "resultados")
      ctrl.append(h("span", { class: "nota", text: "Resultados publicados. Descarga los CSV para el acta de premiación." }));

    const urls = d.urls.map((u) => h("div", {}, h("span", { class: "url", text: u })));
    document.getElementById("acceso").replaceChildren(
      h("h3", { style: "font-size:20px;margin-bottom:8px", text: "Cómo entran los estudiantes" }),
      h("p", { class: "nota", style: "margin:0 0 6px", text: d.urls[0].startsWith("https") ? "Desde cualquier celular o computador con internet, abren:" : "Con el celular o computador conectado a la MISMA red wifi, abren:" }), ...urls,
      h("p", { style: "margin:14px 0 4px" }, "Código de sala: ", h("span", { class: "url", style: "font-size:24px", text: c.sala })),
      h("p", { class: "nota", style: "margin:10px 0 0" }, "Proyecta el tablero: ", h("a", { href: "/tablero", target: "_blank", rel: "noopener", text: d.urls[0] + "/tablero" })),
      h("p", { class: "nota", style: "margin:6px 0 0", text: `Banco de preguntas v${d.banco.version}: ${d.banco.preguntas} preguntas, ${d.banco.puntos_totales} puntos + bono hasta ${d.banco.bono_max}.` }));

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
      interruptor("reloj_global", "Reloj global · solo antes de abrir", "Un solo reloj para todos: corre desde que abres el reto y termina a la misma hora en todos los sitios. Si lo apagas, cada estudiante tiene su propio reloj desde que pulsa «Comenzar»."),
      filaCfg("sala", "Código de sala", "text"),
      filaCfg("evento", "Nombre del evento", "text"),
      filaCfg("duracion_min", "Duración (minutos) · solo antes de abrir", "number"));
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
    document.getElementById("cfg-reloj_global").checked = c.reloj_global === "1";
    document.getElementById("cfg-reloj_global").disabled = c.estado !== "inscripcion";
    for (const k of ["sala", "evento", "duracion_min"]) {
      const inp = document.getElementById("cfg-" + k);
      if (!inp.dataset.editando && document.activeElement !== inp) inp.value = c[k];
    }
    document.getElementById("cfg-duracion_min").disabled = c.estado !== "inscripcion";
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
    if (A.busqueda) filas = filas.filter((p) => `${p.nombre} ${p.colegio} ${p.codigo}`.toLowerCase().includes(A.busqueda));
    filas.sort((x, y) => (x.puesto || 1e6) - (y.puesto || 1e6) || x.id - y.id);
    let rel = 0;
    const cuerpo = document.getElementById("cuerpo");
    cuerpo.replaceChildren(...filas.map((p) => {
      const puestoMostrado = p.puesto ? (A.filtroGrado ? ++rel : p.puesto) : null;
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
      const tiempo = p.estado === "en_curso" ? `quedan ${mmss(p.restante_seg)}` : p.tiempo_usado != null ? mmss(p.tiempo_usado) : "—";
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

  A.clave = ses.get("reto_clave");
  if (A.clave) refrescar(); else login();
})();
