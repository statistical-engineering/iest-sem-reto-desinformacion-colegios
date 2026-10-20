/* App del estudiante. Toda la calificación ocurre en el servidor: aquí solo se
 * muestran las preguntas, se arman las respuestas y se envían. */
(function () {
  "use strict";
  const app = document.getElementById("app");
  const S = { token: null, datos: null, vista: "mapa", mision: 0, pregunta: 0, borradores: {}, reloj: null, revision: false, dossierCerrado: {} };
  const LETRAS = "ABCDEFGH";

  // ---------------------------------------------------------------- utilidades
  function h(tag, attrs, ...hijos) {
    const e = document.createElement(tag);
    for (const k in attrs || {}) {
      const v = attrs[k];
      if (v == null || v === false) continue;
      if (k === "class") e.className = v;
      else if (k === "text") e.textContent = v;
      else if (k === "html") e.innerHTML = v;
      else if (k.startsWith("on")) e.addEventListener(k.slice(2), v);
      else e.setAttribute(k, v === true ? "" : v);
    }
    for (const c of hijos.flat()) if (c != null && c !== false) e.append(c.nodeType ? c : document.createTextNode(String(c)));
    return e;
  }
  const guardar = (k, v) => { try { v == null ? localStorage.removeItem(k) : localStorage.setItem(k, v); } catch (e) { /* sin almacenamiento */ } };
  const leer = (k) => { try { return localStorage.getItem(k); } catch (e) { return null; } };
  const num = (v, d = 0) => Number(v).toLocaleString("es-CO", { minimumFractionDigits: d, maximumFractionDigits: d });

  async function api(ruta, datos) {
    const op = { headers: { "Content-Type": "application/json" } };
    if (S.token) op.headers.Authorization = "Bearer " + S.token;
    if (datos !== undefined) { op.method = "POST"; op.body = JSON.stringify(datos); }
    let r;
    try { r = await fetch(ruta, op); } catch (e) { throw Object.assign(new Error("Sin conexión con el servidor. Revisa el wifi e intenta de nuevo."), { red: true }); }
    const j = await r.json().catch(() => ({}));
    if (!r.ok) throw Object.assign(new Error(j.error || "Error " + r.status), { codigo: r.status });
    return j;
  }

  /** Igual que a_numero() del servidor: coma o punto decimal; varios puntos = miles. */
  function aNumero(texto, entero) {
    let s = String(texto).replace(/[^\d,.\-]/g, "");
    if (!/\d/.test(s)) return null;
    if (entero && /^-?\d{1,3}([.,]\d{3})+$/.test(s)) return Number(s.replace(/[.,]/g, ""));
    if (s.includes(",") && s.includes(".")) s = s.replace(/\./g, "").replace(",", ".");
    else if ((s.match(/,/g) || []).length > 1 || (s.match(/\./g) || []).length > 1) s = s.replace(/[.,]/g, "");
    else s = s.replace(",", ".");
    const n = Number(s);
    return Number.isFinite(n) ? n : null;
  }

  function pantalla(...hijos) {
    app.replaceChildren(h("section", { class: "pantalla" }, ...hijos));
    window.scrollTo({ top: 0 });
  }
  function aviso(nodo, msg, ok) {
    nodo.replaceChildren();
    if (msg) nodo.append(h("div", { class: "aviso" + (ok ? " ok" : ""), role: "alert", text: msg }));
  }

  // ---------------------------------------------------------------- cabecera y reloj
  function cabecera() {
    const d = S.datos;
    const p = d && d.participante;
    document.getElementById("cab-ficha").classList.toggle("oculto", !p);
    if (p) {
      document.getElementById("cab-nombre").textContent = p.nombre;
      document.getElementById("cab-codigo").textContent = p.codigo;
      document.getElementById("cab-evento").textContent = (d.reto.evento || "Sala de verificación").toUpperCase();
    }
    const enCurso = p && p.estado === "en_curso";
    const reloj = document.getElementById("cab-reloj");
    reloj.classList.toggle("oculto", !enCurso);
    const pts = document.getElementById("cab-puntaje");
    const mostrarPts = enCurso && d.reto.retro;
    pts.classList.toggle("oculto", !mostrarPts);
    if (mostrarPts) document.getElementById("cab-puntos").textContent = num(puntosActuales(), 1);
    if (enCurso) S.reloj = { restante: p.restante_seg, base: performance.now() };
    else S.reloj = null;
  }
  function puntosActuales() {
    return Object.values(S.datos.respuestas).reduce((a, r) => a + (r.puntos || 0), 0);
  }
  function tic() {
    if (!S.reloj) return;
    const rest = Math.max(0, S.reloj.restante - (performance.now() - S.reloj.base) / 1000);
    const t = Math.ceil(rest);
    const hh = Math.floor(t / 3600), mm = Math.floor((t % 3600) / 60), ss = t % 60;
    const r = document.getElementById("cab-reloj");
    r.textContent = (hh ? hh + ":" + String(mm).padStart(2, "0") : mm) + ":" + String(ss).padStart(2, "0");
    r.classList.toggle("alerta", rest <= 600 && rest > 120);
    r.classList.toggle("critico", rest <= 120);
    r.setAttribute("aria-label", `Quedan ${mm + hh * 60} minutos`);
    if (rest <= 0) { S.reloj = null; cargar(); }
  }
  setInterval(tic, 250);

  // ---------------------------------------------------------------- carga y enrutamiento
  async function cargar(forzarRender = true) {
    try {
      const nuevo = await api("/api/estado");
      const antes = S.datos;
      S.datos = nuevo;
      cabecera();
      const cambio = !antes || antes.participante.estado !== nuevo.participante.estado || antes.reto.estado !== nuevo.reto.estado;
      if (forzarRender || cambio) enrutar();
    } catch (e) {
      if (!e.codigo && !e.red) console.error(e);
      if (e.codigo === 401) { S.token = null; guardar("reto_token", null); S.datos = null; cabecera(); return ingreso(); }
      if (!S.datos) pantalla(h("div", { class: "tarjeta" }, h("h2", { text: "No hay conexión" }), h("p", { text: e.message }),
        h("button", { class: "boton", onclick: () => cargar() }, "Reintentar")));
    }
  }
  function enrutar() {
    const p = S.datos.participante, reto = S.datos.reto;
    if (p.estado === "registrado") return espera();
    if (p.estado === "en_curso") return S.vista === "mision" ? mision() : mapa();
    if (p.estado === "finalizado") {
      if (S.revision && reto.estado === "resultados") return S.vista === "mision" ? mision() : mapa();
      return final();
    }
    if (p.estado === "no_inicio") return mensaje("El reto ya terminó", "No alcanzaste a comenzar el reto antes de que el docente lo cerrara.");
    if (p.estado === "descalificado") return mensaje("Participación anulada", "El docente anuló esta participación. Habla con él o ella si crees que es un error.");
  }
  function mensaje(t, m) {
    pantalla(h("div", { class: "tarjeta" }, h("h2", { text: t }), h("p", { class: "nota", text: m })));
  }

  // sondeo periódico: sincroniza reloj y detecta cambios de estado sin borrar lo que se está escribiendo
  setInterval(() => {
    if (!S.token || !S.datos) return;
    const est = S.datos.participante.estado;
    if (est === "registrado" || (est === "finalizado" && S.datos.reto.estado !== "resultados")) cargar(false);
  }, 4000);
  setInterval(() => { if (S.token && S.datos && S.datos.participante.estado === "en_curso") cargar(false); }, 20000);

  // ---------------------------------------------------------------- ingreso
  function ingreso(pestana = "nuevo") {
    const msg = h("div");
    const tabs = h("div", { class: "pestanas", role: "tablist" },
      h("button", { role: "tab", "aria-selected": String(pestana === "nuevo"), onclick: () => ingreso("nuevo") }, "Inscribirme"),
      h("button", { role: "tab", "aria-selected": String(pestana === "codigo"), onclick: () => ingreso("codigo") }, "Ya tengo código"));
    let form;
    if (pestana === "nuevo") {
      form = h("form", { onsubmit: async (ev) => {
        ev.preventDefault();
        const f = new FormData(form);
        const boton = form.querySelector("button[type=submit]");
        boton.disabled = true;
        try {
          const r = await api("/api/registro", Object.fromEntries(f));
          S.token = r.token; guardar("reto_token", r.token);
          mostrarCodigo(r.codigo);
        } catch (e) { aviso(msg, e.message); boton.disabled = false; }
      } },
        h("label", { class: "campo" }, h("span", {}, "Nombre completo ", h("small", {}, "(o nombre del equipo)")),
          h("input", { class: "entrada", name: "nombre", required: true, maxlength: 60, autocomplete: "name" })),
        h("label", { class: "campo" }, h("span", { text: "Colegio" }), h("input", { class: "entrada", name: "colegio", required: true, maxlength: 80 })),
        h("div", { class: "campo" }, h("span", { text: "Grado" }),
          h("div", { class: "segmentado", role: "radiogroup", "aria-label": "Grado" },
            ...["9", "10", "11"].map((g) => h("label", {}, h("input", { type: "radio", name: "grado", value: g, required: true }), h("span", { text: g + ".°" }))))),
        h("label", { class: "campo" }, h("span", {}, "Integrantes ", h("small", {}, "(solo si participan en equipo)")),
          h("input", { class: "entrada", name: "integrantes", maxlength: 200, placeholder: "Nombres separados por comas" })),
        h("label", { class: "campo" }, h("span", {}, "Código de sala ", h("small", {}, "(está en el tablero)")),
          h("input", { class: "entrada codigo", name: "sala", required: true, maxlength: 8, autocomplete: "off", autocapitalize: "characters" })),
        h("button", { class: "boton grande", type: "submit" }, "Inscribirme"), msg);
    } else {
      form = h("form", { onsubmit: async (ev) => {
        ev.preventDefault();
        try {
          const r = await api("/api/entrar", { codigo: form.codigo.value });
          S.token = r.token; guardar("reto_token", r.token); cargar();
        } catch (e) { aviso(msg, e.message); }
      } },
        h("p", { class: "nota", text: "Si cambiaste de computador o se cerró la página, entra con el código de 5 caracteres que te dio el sistema." }),
        h("label", { class: "campo" }, h("span", { text: "Tu código de detective" }),
          h("input", { class: "entrada codigo", name: "codigo", required: true, maxlength: 5, autocomplete: "off", autocapitalize: "characters" })),
        h("button", { class: "boton grande", type: "submit" }, "Entrar"), msg);
    }
    pantalla(h("div", { class: "rejilla-2" },
      h("div", {},
        h("div", { class: "antetitulo", text: "Edición especial · 90 minutos · 1.000 puntos" }),
        h("h1", { class: "titular" }, "¿Lo ", h("span", { class: "resaltar" }, "compartirías"), "?"),
        h("p", { class: "bajada", text: "Vas a investigar desinformación real que circuló en Colombia, con los datos de Colombiacheck, el DANE y un estudio científico hecho en 16 países. Siete expedientes, un reloj y un podio." }),
        h("hr", { class: "regla" }),
        h("p", { class: "nota", text: "Pide al docente el código de sala. Si participan en equipo, inscríbanse una sola vez con el nombre del equipo." })),
      h("div", { class: "tarjeta" }, tabs, form)));
    const primero = form.querySelector("input"); if (primero && window.innerWidth > 900) primero.focus({ preventScroll: true });
  }

  function mostrarCodigo(codigo) {
    pantalla(h("div", { class: "tarjeta", style: "max-width:560px;margin:0 auto;text-align:center" },
      h("div", { class: "antetitulo", text: "Inscripción lista" }),
      h("h2", { style: "font-size:34px", text: "Tu código de detective" }),
      h("div", { class: "codigo-grande", text: codigo }),
      h("p", { class: "nota", text: "Anótalo en un papel. Con él vuelves a entrar si se cierra la página o cambias de computador. No se lo des a nadie." }),
      h("button", { class: "boton grande", onclick: () => cargar() }, "Ya lo anoté, continuar")));
  }

  // ---------------------------------------------------------------- sala de espera
  function espera() {
    const d = S.datos, abierto = d.reto.estado === "abierto";
    const mins = Math.round(d.reto.duracion_min);
    const reglas = [
      d.reto.reloj_global
        ? `El reto dura ${mins} minutos y el reloj es el mismo para todos: corre desde que el docente abre el reto y termina a la misma hora para todos los equipos, sin importar desde dónde se conecten. Si tardas en pulsar «Comenzar», pierdes ese tiempo. Si se acaba, tu reto se entrega solo con lo que hayas respondido.`
        : `Tienes ${mins} minutos desde que pulses «Comenzar». El reloj lo lleva el servidor: si se acaba, tu reto se entrega solo con lo que hayas respondido.`,
      `Hay ${d.reto.n_misiones} expedientes y ${num(d.reto.puntos_totales)} puntos. Puedes hacerlos en el orden que quieras. Los «Casos» del Laboratorio de análisis son los que más puntos dan: traen varios gráficos y piden conclusiones.`,
      "Cada pregunta se responde una sola vez: al confirmar el envío, queda bloqueada.",
      "Estimar, ordenar, clasificar y marcar varias dan puntaje parcial: acercarse también cuenta.",
      `Bono de tiempo: hasta ${d.reto.bono_max} puntos extra según qué tan pronto respondas tu última pregunta, y en proporción a lo que aciertes. Pensar bien vale mucho más que correr.`,
      "Desempate: gana el mayor puntaje total; si empatan, más puntos en preguntas; si siguen empatados, quien respondió su última pregunta antes. Nunca hay dos personas en el mismo puesto.",
      "Salir de esta pestaña o cambiar de aplicación queda registrado y el docente lo ve.",
    ];
    pantalla(h("div", { class: "rejilla-2" },
      h("div", {},
        h("div", { class: "antetitulo", text: "Sala de espera" }),
        h("h1", { class: "titular" }, "Hola, ", h("span", { class: "resaltar", text: d.participante.nombre.split(" ")[0] })),
        h("p", { class: "bajada", text: abierto ? (d.reto.reloj_global ? "El reto ya está abierto y el reloj general ya está corriendo. Pulsa «Comenzar» ahora." : "El reto está abierto. Cuando estés listo, pulsa «Comenzar»: desde ese momento corre tu reloj.") : "Estás inscrito. El reto empieza cuando el docente dé la señal." }),
        h("div", { style: "margin-top:26px" }, abierto
          ? h("button", { class: "boton grande", onclick: async (ev) => {
              ev.target.disabled = true;
              try { await api("/api/comenzar", {}); S.vista = "mapa"; await cargar(); } catch (e) { alert(e.message); ev.target.disabled = false; }
            } }, "Comenzar el reto →")
          : h("p", { class: "nota" }, h("span", { class: "espera-pulso" }), "Esperando la señal del docente…"))),
      h("div", { class: "tarjeta" }, h("h3", { style: "font-size:22px;margin-bottom:8px", text: "Reglas del reto" }), h("ol", { class: "reglas" }, ...reglas.map((r) => h("li", { text: r }))))));
  }

  // ---------------------------------------------------------------- mapa de expedientes
  function estadoMision(m) {
    const resp = S.datos.respuestas;
    const hechas = m.preguntas.filter((q) => resp[q.id]).length;
    const pts = m.preguntas.reduce((a, q) => a + ((resp[q.id] && resp[q.id].puntos) || 0), 0);
    return { hechas, total: m.preguntas.length, pts };
  }
  function mapa() {
    S.vista = "mapa";
    const d = S.datos, revisando = S.revision;
    const pendientes = d.misiones.reduce((a, m) => a + (estadoMision(m).total - estadoMision(m).hechas), 0);
    const tarjetas = d.misiones.map((m, i) => {
      const e = estadoMision(m);
      const completo = e.hechas === e.total;
      const meta = d.reto.retro ? `${num(e.pts, 1)} / ${m.puntos} pts` : `${m.puntos} pts`;
      return h("button", { class: "expediente", style: `animation-delay:${i * 60}ms`, onclick: () => { S.mision = i; S.pregunta = primeraPendiente(m); mision(); } },
        h("span", { class: "num", text: `EXP. ${String(i + 1).padStart(2, "0")} · ${m.subtitulo || ""}` }),
        h("h3", { text: m.titulo }),
        h("span", { class: "sub", text: `${m.preguntas.length} ${m.preguntas.length === 1 ? "pregunta" : "preguntas"}` }),
        completo ? h("span", { class: "sello " + (revisando ? "tinta" : "verde"), text: revisando ? "Revisar" : "Completo" }) : null,
        h("div", { class: "barra" }, h("i", { style: `width:${(100 * e.hechas) / e.total}%` })),
        h("div", { class: "meta" }, h("span", { text: `${e.hechas}/${e.total} respondidas` }), h("span", { text: meta })));
    });
    const entregar = h("button", { class: "boton peligro" }, "Entregar mi reto");
    let armado = false;
    entregar.onclick = async () => {
      if (!armado) {
        armado = true;
        entregar.classList.add("confirmar");
        entregar.textContent = pendientes ? `¿Entregar con ${pendientes} sin responder? Toca otra vez` : "¿Seguro? Toca otra vez para entregar";
        setTimeout(() => { armado = false; entregar.classList.remove("confirmar"); entregar.textContent = "Entregar mi reto"; }, 4000);
        return;
      }
      entregar.disabled = true;
      try { await api("/api/finalizar", {}); await cargar(); } catch (e) { alert(e.message); entregar.disabled = false; }
    };
    pantalla(
      h("div", { class: "antetitulo", text: revisando ? "Revisión de respuestas" : "Mesa de investigación" }),
      h("h1", { class: "titular" }, revisando ? "Revisa tus " : "Tus ", h("span", { class: "resaltar", text: "expedientes" })),
      h("p", { class: "bajada", text: revisando
        ? "Abre cada expediente para ver tu respuesta, la correcta y la explicación."
        : pendientes ? `Elige un expediente. Te quedan ${pendientes} preguntas por responder. Puedes ir y volver cuantas veces quieras.` : "¡Respondiste todo! Revisa que estés conforme y entrega el reto." }),
      h("div", { class: "mapa" }, ...tarjetas),
      revisando
        ? h("div", { style: "margin-top:34px" }, h("button", { class: "boton claro", onclick: () => { S.revision = false; final(); } }, "← Volver a mi resultado"))
        : h("div", { style: "margin-top:40px;display:flex;gap:16px;align-items:center;flex-wrap:wrap" }, entregar,
            h("span", { class: "nota", text: "Al entregar ya no podrás responder más. Si se acaba el tiempo, se entrega solo." })));
  }
  function primeraPendiente(m) {
    const i = m.preguntas.findIndex((q) => !S.datos.respuestas[q.id]);
    return i < 0 ? 0 : i;
  }

  // ---------------------------------------------------------------- misión
  function mision() {
    S.vista = "mision";
    const m = S.datos.misiones[S.mision];
    const q = m.preguntas[S.pregunta];
    const lateral = h("aside", { class: "lateral" },
      h("button", { class: "volver", onclick: () => mapa() }, "← Todos los expedientes"),
      h("div", { class: "antetitulo", text: `EXP. ${String(S.mision + 1).padStart(2, "0")} · ${m.subtitulo || ""}` }),
      h("h2", { style: "font-size:34px;margin-bottom:10px", text: m.titulo }),
      h("p", { class: "intro", text: m.intro }),
      m.glosario ? h("div", { class: "tarjeta", style: "padding:16px 18px" }, h("b", { text: "Glosario de veredictos" }),
        h("dl", { class: "glosario" }, ...m.glosario.flatMap((g) => [h("dt", { text: g.termino }), h("dd", { text: g.definicion })]))) : null,
      m.lectura ? h("div", { class: "tarjeta lectura" }, h("b", { text: m.lectura.titulo }),
        ...m.lectura.texto.split("\n\n").map((p) => h("p", { text: p })), h("cite", { text: m.lectura.cita })) : null,
      h("div", { class: "puntos-preg", role: "navigation", "aria-label": "Preguntas de la misión" },
        ...m.preguntas.map((qq, i) => h("button", {
          class: (S.datos.respuestas[qq.id] ? "hecha" : "") + (i === S.pregunta ? " actual" : ""),
          "aria-label": `Pregunta ${i + 1}${S.datos.respuestas[qq.id] ? " (respondida)" : ""}`,
          onclick: () => { S.pregunta = i; mision(); },
        }, String(i + 1)))));
    pantalla(h("div", { class: "mision" }, lateral, h("div", {}, m.dossier ? dossierDe(m) : null, tarjetaPregunta(m, q))));
  }

  /** Expediente de evidencia: los gráficos del caso, visibles en todas sus preguntas. */
  function dossierDe(m) {
    if (m.dossier.bloqueado) {
      return h("div", { class: "dossier dossier-bloqueado" },
        h("div", { class: "dossier-candado", "aria-hidden": "true", text: "🔒" }),
        h("div", {}, h("b", { text: m.dossier.titulo }),
          h("p", { text: `${m.dossier.n} piezas de evidencia selladas. Se abren cuando registres tu hipótesis (primera pregunta del caso). Así comparas lo que creías con lo que muestran los datos.` })));
    }
    const det = h("details", { class: "dossier", open: !S.dossierCerrado[m.id] },
      h("summary", {}, h("span", { text: m.dossier.titulo }), h("small", { text: `${m.dossier.graficos.length} gráficos · toca para abrir o cerrar` })));
    det.addEventListener("toggle", () => { S.dossierCerrado[m.id] = !det.open; });
    const rejilla = h("div", { class: "dossier-rejilla" });
    const anchoPagina = Math.min(window.innerWidth, 1240);
    const principal = anchoPagina - (window.innerWidth > 1000 ? 410 : 40);
    const dosColumnas = principal > 760;
    const ancho = (dosColumnas ? principal / 2 - 14 : principal) - 36;
    m.dossier.graficos.forEach((g) => {
      const completo = g.ancho_completo && dosColumnas;
      const fig = Graficos.dibujar(g, rejilla, { ancho: completo ? principal - 50 : ancho });
      if (completo) fig.classList.add("completo");
    });
    if (!dosColumnas) rejilla.classList.add("una");
    det.append(rejilla);
    return det;
  }

  function tarjetaPregunta(m, q) {
    const resp = S.datos.respuestas[q.id];
    const bloqueada = !!resp || S.datos.participante.estado !== "en_curso";
    const rev = S.datos.revision && S.datos.revision[q.id];
    const falta = q.requiere && !S.datos.respuestas[q.requiere];
    const card = h("article", { class: "tarjeta pregunta" });
    card.append(h("div", { class: "encabezado" },
      h("span", { class: "etq", text: `Pregunta ${S.pregunta + 1} de ${m.preguntas.length}` }),
      h("span", { class: "valor", text: q.puntos ? `${q.puntos} pts` : "Sin puntos" })));
    card.append(h("p", { class: "enunciado", text: q.enunciado }));
    if (falta) {
      card.append(h("p", { class: "aviso", text: "Primero responde la pregunta anterior de este expediente (está marcada en la lista de preguntas)." }));
      card.append(navegacion(m));
      return card;
    }
    if (q.grafico) Graficos.dibujar(q.grafico, card);
    if (q.tabla) card.append(tablaDatos(q.tabla));
    if (q.simulador) card.append(simulador(q.simulador));
    const valor = bloqueada ? (resp ? resp.respuesta : null) : S.borradores[q.id];
    const ctl = CONTROLES[q.tipo](q, valor, bloqueada, rev);
    card.append(ctl.nodo);
    const pie = h("div", { class: "acciones" });
    const msg = h("div");
    if (!bloqueada) {
      const enviar = h("button", { class: "boton", disabled: !ctl.valido() }, "Enviar respuesta");
      ctl.alCambiar(() => { enviar.disabled = !ctl.valido(); });
      let armado = false, temporizador;
      enviar.onclick = async () => {
        if (!armado) {
          armado = true; enviar.classList.add("confirmar"); enviar.textContent = "¿Confirmas? Toca otra vez";
          temporizador = setTimeout(() => { armado = false; enviar.classList.remove("confirmar"); enviar.textContent = "Enviar respuesta"; }, 4000);
          return;
        }
        clearTimeout(temporizador);
        enviar.disabled = true; enviar.textContent = "Enviando…";
        try {
          await api("/api/responder", { pregunta: q.id, respuesta: ctl.valor() });
          delete S.borradores[q.id];
          await cargar(false); // trae la respuesta ya normalizada por el servidor (y su puntaje, si hay retro)
          if (S.datos.participante.estado === "en_curso") mision();
        } catch (e) {
          aviso(msg, e.message);
          enviar.disabled = false; armado = false; enviar.classList.remove("confirmar"); enviar.textContent = "Enviar respuesta";
          if (e.codigo === 400 && /tiempo|terminó|cerrado/i.test(e.message)) setTimeout(() => cargar(), 1500);
        }
      };
      pie.append(enviar);
    } else if (resp) {
      pie.append(selloResultado(q, resp));
    }
    pie.append(navegacion(m));
    card.append(pie, msg);
    if (rev) card.append(revisionDe(q, rev));
    return card;
  }

  function selloResultado(q, resp) {
    if (!q.puntos) return h("span", { class: "sello tinta golpe", text: "Registrada" });
    if (resp.fraccion == null) return h("span", { class: "sello tinta golpe", text: "Respuesta guardada" });
    if (resp.fraccion >= 0.9999) return h("span", { class: "sello verde golpe", text: `Correcta +${num(resp.puntos, 0)}` });
    if (resp.fraccion > 0) return h("span", { class: "sello tinta golpe", text: `Parcial +${num(resp.puntos, 1)} de ${q.puntos}` });
    return h("span", { class: "sello golpe", text: "Incorrecta" });
  }

  function navegacion(m) {
    const n = m.preguntas.length;
    return h("div", { class: "navq" },
      S.pregunta > 0 ? h("button", { class: "boton claro", onclick: () => { S.pregunta--; mision(); } }, "← Anterior") : null,
      S.pregunta < n - 1 ? h("button", { class: "boton claro", onclick: () => { S.pregunta++; mision(); } }, "Siguiente →")
        : h("button", { class: "boton claro", onclick: () => mapa() }, "Volver a expedientes"));
  }

  /** Simulador de mezcla: total = valorA × (1 − p) + valorB × p. Ayuda a explorar; no se califica. */
  function simulador(sim) {
    const [ga, gb] = sim.grupos;
    const salida = h("output", { class: "sim-resultado" });
    const formula = h("div", { class: "sim-formula" });
    const etq = h("span", { class: "sim-p" });
    const rango = h("input", { type: "range", min: sim.min, max: sim.max, step: sim.paso, value: sim.inicial || 0, "aria-label": sim.etiqueta });
    const pintar = () => {
      const p = Number(rango.value);
      const total = ga.valor * (1 - p / 100) + gb.valor * (p / 100);
      etq.textContent = `${num(p, 1)} %`;
      salida.textContent = `${num(total, sim.decimales)} %`;
      formula.textContent = `${ga.nombre}: ${num(100 - p, 1)} % × ${num(ga.valor, 1)} %  +  ${gb.nombre}: ${num(p, 1)} % × ${num(gb.valor, 1)} %`;
    };
    rango.addEventListener("input", pintar);
    pintar();
    return h("div", { class: "simulador" },
      h("div", { class: "sim-cab" }, h("span", { class: "graf-letra", text: "Simulador" }), h("b", { text: sim.etiqueta }), etq),
      rango,
      h("div", { class: "sim-escala" }, h("span", { text: `${sim.min} %` }), h("span", { text: `${sim.max} %` })),
      h("div", { class: "sim-salida" }, h("span", { text: sim.resultado }), salida),
      formula);
  }

  function tablaDatos(t) {
    return h("div", { class: "tabla-scroll" }, h("table", { class: "tabla-datos" },
      h("thead", {}, h("tr", {}, ...t.columnas.map((c) => h("th", { text: c })))),
      h("tbody", {}, ...t.filas.map((f) => h("tr", {}, ...f.map((c) => h("td", { text: c })))))));
  }

  function construir(q, valor, bloq, rev) {
    const st = base(valor ? Object.assign({}, valor) : {});
    const caja = h("div", { class: "construir" });
    const pintar = () => caja.replaceChildren(...q.partes.map((pt, i) => h("fieldset", { class: "pieza" },
      h("legend", {}, h("span", { class: "pieza-num", text: i + 1 }), pt.etiqueta),
      h("div", { class: "opciones" }, ...pt.opciones.map((o) => {
        const sel = st.v[pt.id] === o.id;
        const b = h("button", { class: "opcion", type: "button", role: "radio", "aria-pressed": String(sel), "aria-checked": String(sel), disabled: bloq,
          onclick: () => { st.set(q.id, Object.assign({}, st.v, { [pt.id]: o.id })); pintar(); } },
          h("span", { class: "letra", text: sel ? "✓" : "·" }), h("span", { text: o.texto }));
        if (rev && rev.respuesta) { if (rev.respuesta[pt.id] === o.id) b.classList.add("correcta"); else if (sel) b.classList.add("incorrecta"); }
        return b;
      })))));
    pintar();
    return { nodo: caja, valido: () => Object.keys(st.v).length === q.partes.length, valor: () => st.v, alCambiar: (f) => st.oyentes.push(f) };
  }

  function textoLibre(q, valor, bloq) {
    const st = base(valor || "");
    const max = q.max || 700;
    const cuenta = h("div", { class: "interpretado" });
    const area = h("textarea", { class: "entrada informe", maxlength: max, rows: 7, disabled: bloq, "aria-label": "Tu informe",
      placeholder: "Mi conclusión es… La sostienen los gráficos… Una limitación es…" });
    area.value = st.v;
    const actualizar = () => { cuenta.textContent = `${area.value.length} / ${max} caracteres (mínimo 20)`; };
    area.addEventListener("input", () => { st.set(q.id, area.value); actualizar(); });
    actualizar();
    return { nodo: h("div", {}, area, bloq ? null : cuenta), valido: () => st.v.trim().length >= 20, valor: () => st.v, alCambiar: (f) => st.oyentes.push(f) };
  }

  function revisionDe(q, rev) {
    const caja = h("div", { class: "revision" });
    const r = rev.respuesta;
    let correcta = null;
    if ((q.tipo === "estimar" || q.tipo === "numero") && r != null) correcta = `${num(r, Number.isInteger(r) ? 0 : 2)} ${q.unidad || ""}`;
    if (q.tipo === "ordenar") correcta = r.map((id, i) => `${i + 1}. ${q.items.find((x) => x.id === id).texto}`).join("   ");
    if (correcta) caja.append(h("p", {}, h("b", { text: "Respuesta correcta: " }), h("span", { class: "correcta-txt", text: correcta })));
    if (rev.explicacion) caja.append(h("p", { style: "margin:0" }, h("b", { text: "Explicación: " }), rev.explicacion));
    return caja;
  }

  // ---------------------------------------------------------------- controles por tipo de pregunta
  function base(inicial) {
    const oyentes = [];
    return { v: inicial, oyentes, set(qid, v) { this.v = v; S.borradores[qid] = v; oyentes.forEach((f) => f()); } };
  }

  const CONTROLES = {
    opcion(q, valor, bloq, rev) {
      const st = base(valor);
      const lista = h("div", { class: "opciones", role: "radiogroup" });
      const pintar = () => lista.replaceChildren(...q.opciones.map((o, i) => {
        const b = h("button", { class: "opcion", type: "button", role: "radio", "aria-pressed": String(st.v === o.id), "aria-checked": String(st.v === o.id), disabled: bloq,
          onclick: () => { st.set(q.id, o.id); pintar(); } }, h("span", { class: "letra", text: LETRAS[i] }), h("span", { text: o.texto }));
        if (rev && rev.respuesta != null) { if (o.id === rev.respuesta) b.classList.add("correcta"); else if (o.id === st.v) b.classList.add("incorrecta"); }
        return b;
      }));
      pintar();
      return { nodo: lista, valido: () => !!st.v, valor: () => st.v, alCambiar: (f) => st.oyentes.push(f) };
    },
    multiple(q, valor, bloq, rev) {
      const st = base(valor ? [...valor] : []);
      const caja = h("div");
      const lista = h("div", { class: "opciones" });
      const pintar = () => lista.replaceChildren(...q.opciones.map((o, i) => {
        const sel = st.v.includes(o.id);
        const b = h("button", { class: "opcion marca-multi", type: "button", role: "checkbox", "aria-pressed": String(sel), "aria-checked": String(sel), disabled: bloq,
          onclick: () => { st.set(q.id, sel ? st.v.filter((x) => x !== o.id) : [...st.v, o.id]); pintar(); } },
          h("span", { class: "letra", text: sel ? "✓" : LETRAS[i] }), h("span", { text: o.texto }));
        if (rev) { if (rev.respuesta.includes(o.id)) b.classList.add("correcta"); else if (sel) b.classList.add("incorrecta"); }
        return b;
      }));
      pintar();
      caja.append(h("p", { class: "nota", style: "margin-top:0", text: "Marca todas las que consideres correctas. Cada correcta suma; cada incorrecta resta." }), lista);
      return { nodo: caja, valido: () => st.v.length > 0, valor: () => st.v, alCambiar: (f) => st.oyentes.push(f) };
    },
    compartir: publicaciones,
    recordatorio: publicaciones,
    construir: (...a) => construir(...a),
    texto: (...a) => textoLibre(...a),
    clasificar(q, valor, bloq, rev) {
      return q.estilo === "publicaciones" ? publicaciones(q, valor, bloq, rev) : casos(q, valor, bloq, rev);
    },
    ordenar(q, valor, bloq, rev) {
      const st = base(valor ? [...valor] : q.items.map((i) => i.id));
      if (!valor) S.borradores[q.id] = st.v;
      const lista = h("ol", { class: "orden" + (bloq ? " bloqueado" : "") });
      let arrastrado = null;
      const mover = (i, j) => { const v = [...st.v]; const [x] = v.splice(i, 1); v.splice(j, 0, x); st.set(q.id, v); pintar(); };
      const pintar = () => lista.replaceChildren(...st.v.map((id, i) => {
        const it = q.items.find((x) => x.id === id);
        const li = h("li", { draggable: String(!bloq) },
          h("span", { class: "pos", text: i + 1 }), h("span", { class: "txt", text: it.texto }),
          bloq ? null : h("span", { class: "flechas" },
            h("button", { type: "button", "aria-label": "Subir", disabled: i === 0, onclick: () => mover(i, i - 1) }, "↑"),
            h("button", { type: "button", "aria-label": "Bajar", disabled: i === st.v.length - 1, onclick: () => mover(i, i + 1) }, "↓")));
        if (!bloq) {
          li.addEventListener("dragstart", () => { arrastrado = i; li.classList.add("arrastrando"); });
          li.addEventListener("dragend", () => li.classList.remove("arrastrando"));
          li.addEventListener("dragover", (e) => { e.preventDefault(); li.classList.add("encima"); });
          li.addEventListener("dragleave", () => li.classList.remove("encima"));
          li.addEventListener("drop", (e) => { e.preventDefault(); li.classList.remove("encima"); if (arrastrado !== null && arrastrado !== i) mover(arrastrado, i); arrastrado = null; });
        }
        return li;
      }));
      pintar();
      const caja = h("div", {}, h("p", { class: "nota", style: "margin-top:0", text: "Arriba: la que MÁS se hace. Abajo: la que MENOS." }), lista);
      return { nodo: caja, valido: () => true, valor: () => st.v, alCambiar: (f) => st.oyentes.push(f) };
    },
    estimar(q, valor, bloq) {
      const st = base(valor);
      const medio = Math.round((q.min + q.max) / 2);
      const salida = h("output", { text: st.v == null ? "¿?" : num(st.v) + (q.unidad || "") });
      const rango = h("input", { type: "range", min: q.min, max: q.max, step: q.paso || 1, value: st.v == null ? medio : st.v, disabled: bloq, "aria-label": "Tu estimación" });
      rango.addEventListener("input", () => { st.set(q.id, Number(rango.value)); salida.textContent = num(st.v) + (q.unidad || ""); });
      const caja = h("div", { class: "estimador" }, salida, rango, h("div", { class: "escala" }, h("span", { text: q.min + (q.unidad || "") }), h("span", { text: q.max + (q.unidad || "") })),
        bloq ? null : h("p", { class: "nota", text: "Mueve el control hasta tu estimación." }));
      return { nodo: caja, valido: () => st.v != null, valor: () => st.v, alCambiar: (f) => st.oyentes.push(f) };
    },
    numero(q, valor, bloq) {
      const st = base(valor == null ? "" : String(valor));
      const inter = h("div", { class: "interpretado" });
      const entrada = h("input", { class: "entrada", inputmode: "decimal", autocomplete: "off", value: bloq && valor != null ? num(valor, Number.isInteger(valor) ? 0 : 2) : st.v, disabled: bloq, "aria-label": "Tu respuesta" });
      const actualizar = () => {
        const n = aNumero(entrada.value, q.entero);
        inter.textContent = entrada.value.trim() === "" ? "" : n == null ? "Eso no parece un número." : `Se enviará: ${num(n, Number.isInteger(n) ? 0 : Math.min(4, (String(n).split(".")[1] || "").length))} ${q.unidad || ""}`;
      };
      entrada.addEventListener("input", () => { st.set(q.id, entrada.value); actualizar(); });
      if (!bloq) actualizar();
      const caja = h("div", {}, h("div", { class: "numero" }, entrada, h("span", { class: "unidad", text: q.unidad || "" })), bloq ? null : inter);
      setTimeout(() => { if (!bloq) entrada.focus({ preventScroll: true }); }, 50);
      return { nodo: caja, valido: () => aNumero(st.v, q.entero) != null, valor: () => st.v, alCambiar: (f) => st.oyentes.push(f) };
    },
  };

  function publicaciones(q, valor, bloq, rev) {
    const lista = q.publicaciones || q.items;
    const st = base(valor ? Object.assign({}, valor) : {});
    const caja = h("div", { class: "posts" });
    const icono = '<svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12h12l-4-4M16 12l-4 4" fill="none" stroke="#857e6e" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    const pintar = () => caja.replaceChildren(...lista.map((p) => h("div", { class: "post" },
      h("div", { class: "post-cab" }, h("span", { class: "post-avatar", html: icono }), h("span", { text: p.encabezado || "Publicación" })),
      h("div", { class: "post-texto", text: p.texto }),
      h("div", { class: "post-elegir", role: "radiogroup", "aria-label": p.texto },
        ...q.categorias.map((c) => {
          const b = h("button", { type: "button", "aria-pressed": String(st.v[p.id] === c.id), disabled: bloq,
            onclick: () => { st.set(q.id, Object.assign({}, st.v, { [p.id]: c.id })); pintar(); } }, c.texto);
          if (rev && rev.respuesta && rev.respuesta[p.id] === c.id) b.classList.add("correcta");
          return b;
        })))));
    pintar();
    const total = lista.length;
    return { nodo: caja, valido: () => Object.keys(st.v).length === total, valor: () => st.v, alCambiar: (f) => st.oyentes.push(f) };
  }

  function casos(q, valor, bloq, rev) {
    const st = base(valor ? Object.assign({}, valor) : {});
    const caja = h("div", { class: "casos" });
    const pintar = () => caja.replaceChildren(...q.items.map((it, i) => h("div", { class: "caso" },
      h("div", { class: "caso-titulo", text: `${i + 1}. ${it.texto}` }),
      it.detalle ? h("div", { class: "caso-detalle", text: it.detalle }) : null,
      h("div", { class: "chips", role: "radiogroup", "aria-label": `Caso ${i + 1}` }, ...q.categorias.map((c) => {
        const b = h("button", { type: "button", "aria-pressed": String(st.v[it.id] === c.id), disabled: bloq,
          onclick: () => { st.set(q.id, Object.assign({}, st.v, { [it.id]: c.id })); pintar(); } }, c.texto);
        if (rev && rev.respuesta && rev.respuesta[it.id] === c.id) b.classList.add("correcta");
        return b;
      })))));
    pintar();
    return { nodo: caja, valido: () => Object.keys(st.v).length === q.items.length, valor: () => st.v, alCambiar: (f) => st.oyentes.push(f) };
  }

  // ---------------------------------------------------------------- final y resultados
  function final() {
    S.vista = "final";
    const d = S.datos, p = d.participante, res = d.reto.estado === "resultados";
    const usados = p.tiempo_usado != null ? Math.round(p.tiempo_usado / 60) : null;
    const marcador = p.total != null ? h("div", { class: "marcador" },
      h("div", {}, h("span", { text: "Puntos (de 1.000)" }), h("b", { text: num(p.puntos, 2) })),
      h("div", {}, h("span", { text: "Bono de tiempo" }), h("b", { text: "+" + num(p.bono, 2) })),
      h("div", {}, h("span", { text: "Puntaje total" }), h("b", { text: num(p.total, 2) })),
      p.nota != null ? h("div", {}, h("span", { text: "Nota (1,0 a 5,0)" }), h("b", { text: num(p.nota, 1) })) : null,
      usados != null ? h("div", {}, h("span", { text: "Tiempo usado" }), h("b", { text: usados + " min" })) : null) : null;
    if (res) {
      pantalla(h("div", { class: "rejilla-2" },
        h("div", {},
          h("div", { class: "antetitulo", text: "Resultados oficiales" }),
          h("div", { class: "puesto-final" }, h("span", { class: "resaltar", text: p.puesto ? `${p.puesto}.º` : "—" })),
          h("p", { class: "bajada", text: p.puesto && p.puesto <= 3 ? "¡Estás en el podio! Felicitaciones, detective." : "Gracias por investigar. Mira el tablero para ver el podio y el experimento de la clase." }),
          marcador),
        h("div", { class: "tarjeta" },
          h("h3", { style: "font-size:22px", text: "¿Qué aprendimos?" }),
          h("p", { class: "nota", text: "Revisa cada expediente: verás tu respuesta, la correcta y por qué. Fíjate sobre todo en el Expediente 01: ¿compartiste algo que después reconociste como falso? Eso mismo encontró el estudio de Nature en 16 países." }),
          h("button", { class: "boton grande", onclick: () => { S.revision = true; mapa(); } }, "Revisar mis respuestas"))));
      return;
    }
    pantalla(h("div", { style: "max-width:760px" },
      h("div", { class: "antetitulo", text: "Expediente cerrado" }),
      h("h1", { class: "titular" }, "Reto ", h("span", { class: "resaltar", text: "entregado" })),
      h("span", { class: "sello golpe", style: "font-size:22px;margin:18px 0", text: "Recibido" }),
      marcador || h("p", { class: "bajada", text: "Tus respuestas quedaron guardadas en el servidor." }),
      h("p", { class: "nota" }, h("span", { class: "espera-pulso" }), "Los resultados oficiales y el podio se publicarán cuando el docente cierre el reto. Esta página se actualiza sola.")));
  }

  // ---------------------------------------------------------------- salidas de pestaña
  let ultimoAviso = 0;
  document.addEventListener("visibilitychange", () => {
    if (!S.datos || S.datos.participante.estado !== "en_curso") return;
    if (document.hidden) {
      if (Date.now() - ultimoAviso > 3000) { ultimoAviso = Date.now(); api("/api/evento", { tipo: "salida" }).catch(() => {}); }
    } else {
      const a = document.getElementById("salida-aviso");
      a.classList.remove("oculto");
      setTimeout(() => a.classList.add("oculto"), 4000);
      cargar(false);
    }
  });

  // ---------------------------------------------------------------- arranque
  S.token = leer("reto_token");
  if (S.token) cargar(); else ingreso();
})();
