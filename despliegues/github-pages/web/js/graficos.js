/* Gráficos SVG sin dependencias (funcionan sin internet).
 * Graficos.dibujar(spec, contenedor) — spec viene de banco_preguntas.json:
 *   tipo: "barras_h" | "columnas" | "lineas"
 *   etiquetas, series[{nombre, valores}], unidad, decimales, valores_visibles, tooltips,
 *   y_min / y_max (columnas y líneas), x_max (barras_h), destacar [índices]
 * Reglas de diseño: marcas delgadas, rejilla tenue, leyenda solo con 2+ series,
 * texto en tinta (nunca en el color de la serie), tooltip al pasar el cursor o tocar,
 * y vista de tabla cuando los valores pueden mostrarse.
 */
(function () {
  "use strict";
  const NS = "http://www.w3.org/2000/svg";

  function fmt(v, dec, unidad) {
    const s = Number(v).toLocaleString("es-CO", { minimumFractionDigits: dec, maximumFractionDigits: dec });
    return s + (unidad || "");
  }
  function el(nombre, attrs, padre) {
    const e = document.createElementNS(NS, nombre);
    for (const k in attrs || {}) e.setAttribute(k, attrs[k]);
    if (padre) padre.appendChild(e);
    return e;
  }
  function texto(padre, x, y, contenido, attrs) {
    const t = el("text", Object.assign({ x, y }, attrs || {}), padre);
    t.textContent = contenido;
    return t;
  }
  function pasoBonito(rango, objetivo) {
    const bruto = rango / Math.max(1, objetivo);
    const mag = Math.pow(10, Math.floor(Math.log10(bruto)));
    const n = bruto / mag;
    return (n <= 1 ? 1 : n <= 2 ? 2 : n <= 2.5 ? 2.5 : n <= 5 ? 5 : 10) * mag;
  }
  function escala(min, max, objetivo) {
    const paso = pasoBonito(max - min, objetivo || 5);
    const ticks = [];
    const ini = Math.floor(min / paso) * paso;
    for (let v = ini; v <= max + paso * 1e-6; v += paso) ticks.push(+v.toFixed(10));
    return { ticks, max: Math.max(max, ticks[ticks.length - 1]), min: ini };
  }
  function colorSerie(i) {
    return `var(--serie-${(i % 4) + 1})`;
  }

  // ------------------------------------------------------------------ tooltip compartido
  let tip = null;
  function mostrarTip(evt, html) {
    if (!tip) {
      tip = document.createElement("div");
      tip.className = "graf-tip";
      tip.setAttribute("role", "status");
      document.body.appendChild(tip);
    }
    tip.innerHTML = html;
    tip.style.display = "block";
    const x = (evt.touches ? evt.touches[0].clientX : evt.clientX) + 14;
    const y = (evt.touches ? evt.touches[0].clientY : evt.clientY) - 10;
    const w = tip.offsetWidth;
    tip.style.left = Math.min(x, window.innerWidth - w - 8) + "px";
    tip.style.top = Math.max(8, y - tip.offsetHeight) + "px";
  }
  function ocultarTip() {
    if (tip) tip.style.display = "none";
  }
  document.addEventListener("scroll", ocultarTip, { passive: true });

  function engancharTip(nodo, spec, html) {
    if (!spec.tooltips) return;
    nodo.style.cursor = "crosshair";
    nodo.setAttribute("tabindex", "0");
    nodo.addEventListener("mousemove", (e) => mostrarTip(e, html));
    nodo.addEventListener("mouseleave", ocultarTip);
    nodo.addEventListener("touchstart", (e) => mostrarTip(e, html), { passive: true });
    nodo.addEventListener("focus", () => {
      const r = nodo.getBoundingClientRect();
      mostrarTip({ clientX: r.left + r.width / 2, clientY: r.top }, html);
    });
    nodo.addEventListener("blur", ocultarTip);
  }

  // ------------------------------------------------------------------ barras horizontales
  function barrasH(spec, svg, W) {
    const vals = spec.series[0].valores;
    const n = vals.length;
    const angosto = W < 520; // en celular la etiqueta va encima de la barra
    const filaH = angosto ? 44 : 30, barra = 16;
    const izq = angosto ? 4 : Math.min(240, 18 + Math.max(...spec.etiquetas.map((e) => e.length)) * 7.2);
    const der = spec.valores_visibles ? 74 : 24;
    const arriba = 8, abajo = 28;
    const H = arriba + n * filaH + abajo;
    const maxV = spec.x_max || Math.max(...vals);
    const esc = escala(0, maxV, 5);
    const ancho = W - izq - der;
    const x = (v) => izq + (v / esc.max) * ancho;
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    esc.ticks.forEach((t) => {
      el("line", { x1: x(t), x2: x(t), y1: arriba, y2: H - abajo, class: "graf-rejilla" }, svg);
      texto(svg, x(t), H - abajo + 18, fmt(t, 0, spec.unidad === "%" ? "%" : ""), { class: "graf-eje", "text-anchor": "middle" });
    });
    vals.forEach((v, i) => {
      const y0 = arriba + i * filaH + (angosto ? filaH - barra - 4 : (filaH - barra) / 2);
      if (angosto) texto(svg, izq, y0 - 6, spec.etiquetas[i], { class: "graf-etq" });
      else texto(svg, izq - 10, y0 + barra / 2 + 4, spec.etiquetas[i], { class: "graf-etq", "text-anchor": "end" });
      const destacado = (spec.destacar || []).includes(i);
      const w = Math.max(0, x(v) - izq);
      const r = Math.min(4, w / 2);
      const d = `M${izq},${y0} h${Math.max(0, w - r)} a${r},${r} 0 0 1 ${r},${r} v${barra - 2 * r} a${r},${r} 0 0 1 -${r},${r} h-${Math.max(0, w - r)} z`;
      const p = el("path", { d, fill: destacado ? "var(--serie-2)" : "var(--serie-1)", class: "graf-marca" }, svg);
      const hit = el("rect", { x: izq, y: arriba + i * filaH, width: ancho, height: filaH, fill: "transparent" }, svg);
      engancharTip(hit, spec, `<b>${spec.etiquetas[i]}</b><br>${fmt(v, spec.decimales, spec.unidad)}`);
      hit.addEventListener("mouseenter", () => p.classList.add("activa"));
      hit.addEventListener("mouseleave", () => p.classList.remove("activa"));
      if (spec.valores_visibles)
        texto(svg, x(v) + 6, y0 + barra / 2 + 4, fmt(v, spec.decimales, spec.unidad), { class: "graf-valor" });
    });
    el("line", { x1: izq, x2: izq, y1: arriba, y2: H - abajo, class: "graf-base" }, svg);
  }

  // ------------------------------------------------------------------ columnas agrupadas (2+ series)
  function agrupadas(spec, svg, W) {
    const n = spec.etiquetas.length, k = spec.series.length;
    const H = 270, izq = 46, der = 10, arriba = 22, abajo = 40;
    const todos = spec.series.flatMap((s) => s.valores);
    const esc = escala(0, spec.y_max != null ? spec.y_max : Math.max(...todos), 5);
    const yMax = spec.y_max != null ? spec.y_max : esc.max;
    const y = (v) => arriba + (1 - v / yMax) * (H - arriba - abajo);
    const banda = (W - izq - der) / n;
    const barra = Math.min(22, (banda * 0.8) / k - 2);
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    esc.ticks.filter((t) => t <= yMax).forEach((t) => {
      el("line", { x1: izq, x2: W - der, y1: y(t), y2: y(t), class: "graf-rejilla" }, svg);
      texto(svg, izq - 8, y(t) + 4, fmt(t, 0, spec.unidad === "%" ? "%" : ""), { class: "graf-eje", "text-anchor": "end" });
    });
    spec.etiquetas.forEach((e, i) => {
      const cx = izq + banda * i + banda / 2;
      const palabras = e.split(" ");
      const mitad = Math.ceil(palabras.length / 2);
      const lineasEtq = banda < 90 && palabras.length > 1 ? [palabras.slice(0, mitad).join(" "), palabras.slice(mitad).join(" ")] : [e];
      lineasEtq.forEach((l, j) => texto(svg, cx, H - abajo + 16 + j * 13, l, { class: "graf-eje", "text-anchor": "middle" }));
      spec.series.forEach((s, j) => {
        const v = s.valores[i];
        const x0 = cx - (k * (barra + 2)) / 2 + j * (barra + 2);
        const h = Math.max(0, y(0) - y(v));
        const r = Math.min(4, h / 2, barra / 2);
        const d = `M${x0},${y(0)} v-${Math.max(0, h - r)} a${r},${r} 0 0 1 ${r},-${r} h${barra - 2 * r} a${r},${r} 0 0 1 ${r},${r} v${Math.max(0, h - r)} z`;
        el("path", { d, fill: colorSerie(j), class: "graf-marca" }, svg);
      });
      const hit = el("rect", { x: izq + banda * i, y: arriba, width: banda, height: H - arriba - abajo, fill: "transparent" }, svg);
      const filas = spec.series.map((s, j) => `<span class="graf-tip-clave" style="background:${colorSerie(j)}"></span>${s.nombre}: <b>${fmt(s.valores[i], spec.decimales, spec.unidad)}</b>`).join("<br>");
      engancharTip(hit, spec, `<b>${e}</b><br>${filas}`);
    });
    el("line", { x1: izq, x2: W - der, y1: y(0), y2: y(0), class: "graf-base" }, svg);
  }

  // ------------------------------------------------------------------ dispersión
  function dispersionG(spec, svg, W) {
    const pts = spec.puntos;
    const H = 300, izq = 50, der = 16, arriba = 16, abajo = 42;
    const xs = pts.map((p) => p.x), ys = pts.map((p) => p.y);
    const ex = escala(Math.floor(Math.min(...xs) / 10) * 10, Math.max(...xs), 5);
    const ey = escala(Math.floor(Math.min(...ys)), Math.max(...ys), 5);
    const x = (v) => izq + ((v - ex.min) / (ex.max - ex.min)) * (W - izq - der);
    const y = (v) => arriba + (1 - (v - ey.min) / (ey.max - ey.min)) * (H - arriba - abajo);
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    ey.ticks.forEach((t) => {
      el("line", { x1: izq, x2: W - der, y1: y(t), y2: y(t), class: "graf-rejilla" }, svg);
      texto(svg, izq - 8, y(t) + 4, fmt(t, 0, ""), { class: "graf-eje", "text-anchor": "end" });
    });
    ex.ticks.forEach((t) => {
      el("line", { x1: x(t), x2: x(t), y1: arriba, y2: H - abajo, class: "graf-rejilla" }, svg);
      texto(svg, x(t), H - abajo + 16, fmt(t, 0, spec.unidad_x || ""), { class: "graf-eje", "text-anchor": "middle" });
    });
    texto(svg, (izq + W - der) / 2, H - 6, spec.eje_x, { class: "graf-etq", "text-anchor": "middle" });
    const ty = texto(svg, 12, (arriba + H - abajo) / 2, spec.eje_y, { class: "graf-etq", "text-anchor": "middle" });
    ty.setAttribute("transform", `rotate(-90 12 ${(arriba + H - abajo) / 2})`);
    pts.forEach((p) => {
      const c = el("circle", { cx: x(p.x), cy: y(p.y), r: 5, fill: "var(--serie-1)", stroke: "var(--graf-fondo)", "stroke-width": 2 }, svg);
      if (p.mostrar) {
        const derecha = x(p.x) > W - 110; // cerca del borde: la etiqueta va a la izquierda del punto
        texto(svg, x(p.x) + (derecha ? -8 : 8), y(p.y) - 6, p.etiqueta, { class: "graf-valor", "text-anchor": derecha ? "end" : "start" });
      }
      const hit = el("circle", { cx: x(p.x), cy: y(p.y), r: 12, fill: "transparent" }, svg);
      engancharTip(hit, spec, `<b>${p.etiqueta}</b><br>${spec.eje_x}: ${fmt(p.x, 1, spec.unidad_x || "")}<br>${spec.eje_y}: ${fmt(p.y, 2, spec.unidad_y || "")}`);
      hit.addEventListener("mouseenter", () => c.setAttribute("r", 7));
      hit.addEventListener("mouseleave", () => c.setAttribute("r", 5));
    });
  }

  // ------------------------------------------------------------------ intervalos de confianza
  function intervalos(spec, svg, W) {
    const vals = spec.series[0].valores, mar = spec.margenes || vals.map(() => 0);
    const n = vals.length, filaH = 30;
    const angosto = W < 520;
    const izq = angosto ? 112 : Math.min(200, 18 + Math.max(...spec.etiquetas.map((e) => e.length)) * 7.2);
    const der = 16, arriba = 8, abajo = 30;
    const H = arriba + n * filaH + abajo;
    const lo = Math.min(...vals.map((v, i) => v - mar[i])), hi = Math.max(...vals.map((v, i) => v + mar[i]));
    const esc = escala(Math.floor(lo * 2) / 2, hi, 6);
    const x = (v) => izq + ((v - esc.min) / (esc.max - esc.min)) * (W - izq - der);
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    esc.ticks.forEach((t) => {
      el("line", { x1: x(t), x2: x(t), y1: arriba, y2: H - abajo, class: "graf-rejilla" }, svg);
      texto(svg, x(t), H - abajo + 18, fmt(t, 1, ""), { class: "graf-eje", "text-anchor": "middle" });
    });
    vals.forEach((v, i) => {
      const cy = arriba + i * filaH + filaH / 2;
      texto(svg, izq - 10, cy + 4, spec.etiquetas[i], { class: "graf-etq", "text-anchor": "end" });
      el("line", { x1: x(v - mar[i]), x2: x(v + mar[i]), y1: cy, y2: cy, stroke: "var(--serie-1)", "stroke-width": 4, "stroke-linecap": "round", opacity: 0.45 }, svg);
      el("line", { x1: x(v - mar[i]), x2: x(v - mar[i]), y1: cy - 6, y2: cy + 6, stroke: "var(--serie-1)", "stroke-width": 2 }, svg);
      el("line", { x1: x(v + mar[i]), x2: x(v + mar[i]), y1: cy - 6, y2: cy + 6, stroke: "var(--serie-1)", "stroke-width": 2 }, svg);
      el("circle", { cx: x(v), cy, r: 5, fill: "var(--serie-1)", stroke: "var(--graf-fondo)", "stroke-width": 2 }, svg);
      const hit = el("rect", { x: izq, y: cy - filaH / 2, width: W - izq - der, height: filaH, fill: "transparent" }, svg);
      engancharTip(hit, spec, `<b>${spec.etiquetas[i]}</b><br>${fmt(v, spec.decimales, spec.unidad)}<br>entre ${fmt(v - mar[i], spec.decimales, "")} y ${fmt(v + mar[i], spec.decimales, spec.unidad)}`);
    });
  }

  // ------------------------------------------------------------------ columnas
  function columnas(spec, svg, W) {
    if (spec.series.length > 1) return agrupadas(spec, svg, W);
    const vals = spec.series[0].valores;
    const n = vals.length;
    const H = 260, izq = 52, der = 12, arriba = 22, abajo = 34;
    const yMin = spec.y_min != null ? spec.y_min : 0;
    const esc = escala(yMin, spec.y_max != null ? spec.y_max : Math.max(...vals), 5);
    const yMax = spec.y_max != null ? spec.y_max : esc.max;
    const ticks = esc.ticks.filter((t) => t >= yMin - 1e-9 && t <= yMax + 1e-9);
    const banda = (W - izq - der) / n;
    const barra = Math.min(36, banda * 0.62);
    const y = (v) => arriba + (1 - (v - yMin) / (yMax - yMin)) * (H - arriba - abajo);
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    ticks.forEach((t) => {
      el("line", { x1: izq, x2: W - der, y1: y(t), y2: y(t), class: "graf-rejilla" }, svg);
      texto(svg, izq - 8, y(t) + 4, fmt(t, spec.decimales > 0 && yMax - yMin < 2 ? 2 : 0, ""), { class: "graf-eje", "text-anchor": "end" });
    });
    const caben = Math.max(4, Math.floor((W - izq - der) / 34));
    const saltoEtq = n > caben ? Math.ceil(n / caben) : 1;
    vals.forEach((v, i) => {
      const cx = izq + banda * i + banda / 2;
      const top = y(Math.max(v, yMin));
      const h = Math.max(0, y(yMin) - top);
      const r = Math.min(4, h / 2, barra / 2);
      const x0 = cx - barra / 2;
      const d = `M${x0},${y(yMin)} v-${Math.max(0, h - r)} a${r},${r} 0 0 1 ${r},-${r} h${barra - 2 * r} a${r},${r} 0 0 1 ${r},${r} v${Math.max(0, h - r)} z`;
      const destacado = (spec.destacar || []).includes(i);
      const p = el("path", { d, fill: destacado ? "var(--serie-2)" : "var(--serie-1)", class: "graf-marca" }, svg);
      if (i % saltoEtq === 0) texto(svg, cx, H - abajo + 18, spec.etiquetas[i], { class: "graf-eje", "text-anchor": "middle" });
      if (spec.valores_visibles && n <= 12) texto(svg, cx, top - 6, fmt(v, spec.decimales, spec.unidad), { class: "graf-valor", "text-anchor": "middle" });
      const hit = el("rect", { x: izq + banda * i, y: arriba, width: banda, height: H - arriba - abajo, fill: "transparent" }, svg);
      engancharTip(hit, spec, `<b>${spec.etiquetas[i]}</b><br>${fmt(v, spec.decimales, spec.unidad)}`);
      hit.addEventListener("mouseenter", () => p.classList.add("activa"));
      hit.addEventListener("mouseleave", () => p.classList.remove("activa"));
    });
    el("line", { x1: izq, x2: W - der, y1: y(yMin), y2: y(yMin), class: "graf-base" }, svg);
  }

  // ------------------------------------------------------------------ líneas
  function lineas(spec, svg, W) {
    const n = spec.etiquetas.length;
    const todos = spec.series.flatMap((s) => s.valores);
    const H = 270, izq = 52, der = 20, arriba = 22, abajo = 34;
    const yMin = spec.y_min != null ? spec.y_min : Math.min(0, ...todos);
    const esc = escala(yMin, spec.y_max != null ? spec.y_max : Math.max(...todos), 5);
    const yMax = spec.y_max != null ? spec.y_max : esc.max;
    const x = (i) => izq + (n === 1 ? 0.5 : i / (n - 1)) * (W - izq - der);
    const y = (v) => arriba + (1 - (v - yMin) / (yMax - yMin)) * (H - arriba - abajo);
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    esc.ticks.filter((t) => t >= yMin && t <= yMax).forEach((t) => {
      el("line", { x1: izq, x2: W - der, y1: y(t), y2: y(t), class: "graf-rejilla" }, svg);
      texto(svg, izq - 8, y(t) + 4, fmt(t, 0, spec.unidad === "%" ? "%" : ""), { class: "graf-eje", "text-anchor": "end" });
    });
    const caben = Math.max(4, Math.floor((W - izq - der) / 46));
    const saltoEtq = n > caben ? Math.ceil(n / caben) : 1;
    spec.etiquetas.forEach((e, i) => {
      if (i % saltoEtq === 0 || i === n - 1) texto(svg, x(i), H - abajo + 18, e, { class: "graf-eje", "text-anchor": "middle" });
    });
    el("line", { x1: izq, x2: W - der, y1: y(yMin), y2: y(yMin), class: "graf-base" }, svg);
    spec.series.forEach((s, k) => {
      const d = s.valores.map((v, i) => `${i ? "L" : "M"}${x(i)},${y(v)}`).join(" ");
      el("path", { d, fill: "none", stroke: colorSerie(k), "stroke-width": 2.25, "stroke-linejoin": "round", "stroke-linecap": "round" }, svg);
      s.valores.forEach((v, i) => {
        if (n <= 12 || i === n - 1)
          el("circle", { cx: x(i), cy: y(v), r: 4, fill: colorSerie(k), stroke: "var(--graf-fondo)", "stroke-width": 2 }, svg);
      });
    });
    const guia = el("line", { x1: 0, x2: 0, y1: arriba, y2: H - abajo, class: "graf-guia", visibility: "hidden" }, svg);
    const paso = (W - izq - der) / Math.max(1, n - 1);
    spec.etiquetas.forEach((e, i) => {
      const hit = el("rect", { x: x(i) - paso / 2, y: arriba, width: paso, height: H - arriba - abajo, fill: "transparent" }, svg);
      const filas = spec.series.map((s, k) => `<span class="graf-tip-clave" style="background:${colorSerie(k)}"></span>${s.nombre}: <b>${fmt(s.valores[i], spec.decimales, spec.unidad)}</b>`).join("<br>");
      engancharTip(hit, spec, `<b>${e}</b><br>${filas}`);
      hit.addEventListener("mouseenter", () => {
        if (!spec.tooltips) return;
        guia.setAttribute("x1", x(i)); guia.setAttribute("x2", x(i)); guia.setAttribute("visibility", "visible");
      });
      hit.addEventListener("mouseleave", () => guia.setAttribute("visibility", "hidden"));
    });
  }

  // ------------------------------------------------------------------ ensamblaje
  function tablaDe(spec) {
    const t = document.createElement("table");
    t.className = "graf-tabla";
    if (spec.margenes) {
      t.innerHTML = `<thead><tr><th></th><th>Estimación</th><th>Desde</th><th>Hasta</th></tr></thead><tbody>${spec.etiquetas
        .map((e, i) => { const v = spec.series[0].valores[i], m = spec.margenes[i]; return `<tr><th>${e}</th><td>${fmt(v, spec.decimales, spec.unidad)}</td><td>${fmt(v - m, spec.decimales, "")}</td><td>${fmt(v + m, spec.decimales, "")}</td></tr>`; }).join("")}</tbody>`;
      return t;
    }
    if (spec.puntos) {
      t.innerHTML = `<thead><tr><th></th><th>${spec.eje_x}</th><th>${spec.eje_y}</th></tr></thead><tbody>${spec.puntos
        .map((p) => `<tr><th>${p.etiqueta}</th><td>${fmt(p.x, 1, spec.unidad_x || "")}</td><td>${fmt(p.y, 2, spec.unidad_y || "")}</td></tr>`).join("")}</tbody>`;
      return t;
    }
    const cab = ["", ...spec.series.map((s) => s.nombre)];
    t.innerHTML = `<thead><tr>${cab.map((c) => `<th>${c}</th>`).join("")}</tr></thead><tbody>${spec.etiquetas
      .map((e, i) => `<tr><th>${e}</th>${spec.series.map((s) => `<td>${fmt(s.valores[i], spec.decimales, spec.unidad)}</td>`).join("")}</tr>`)
      .join("")}</tbody>`;
    return t;
  }

  function dibujarTabla(spec, contenedor) {
    const fig = document.createElement("figure");
    fig.className = "graf graf-con-tabla";
    const cab = document.createElement("figcaption");
    cab.innerHTML = `${spec.letra ? `<span class="graf-letra">Tabla ${spec.letra}</span>` : ""}<span class="graf-titulo">${spec.titulo || ""}</span>${spec.subtitulo ? `<span class="graf-sub">${spec.subtitulo}</span>` : ""}`;
    fig.appendChild(cab);
    const t = document.createElement("table");
    t.className = "tabla-datos tabla-evidencia";
    t.innerHTML = `<thead><tr>${spec.columnas.map((c) => `<th>${c}</th>`).join("")}</tr></thead><tbody>${spec.filas
      .map((f) => `<tr>${f.map((c, i) => (i === 0 ? `<th>${c}</th>` : `<td>${c}</td>`)).join("")}</tr>`).join("")}</tbody>`;
    fig.appendChild(t);
    if (spec.fuente) {
      const pie = document.createElement("div");
      pie.className = "graf-pie";
      pie.innerHTML = `<span>Fuente: ${spec.fuente}</span>`;
      fig.appendChild(pie);
    }
    contenedor.appendChild(fig);
    return fig;
  }

  function dibujar(spec, contenedor, opciones) {
    if (spec.tipo === "tabla") return dibujarTabla(spec, contenedor);
    const fig = document.createElement("figure");
    fig.className = "graf";
    const cab = document.createElement("figcaption");
    cab.innerHTML = `${spec.letra ? `<span class="graf-letra">Gráfico ${spec.letra}</span>` : ""}<span class="graf-titulo">${spec.titulo || ""}</span>${spec.subtitulo ? `<span class="graf-sub">${spec.subtitulo}</span>` : ""}`;
    fig.appendChild(cab);
    if (spec.series.length > 1) {
      const ley = document.createElement("div");
      ley.className = "graf-leyenda";
      ley.innerHTML = spec.series.map((s, k) => `<span><i style="background:${colorSerie(k)}"></i>${s.nombre}</span>`).join("");
      fig.appendChild(ley);
    }
    const svg = el("svg", { role: "img", "aria-label": spec.titulo || "gráfico", preserveAspectRatio: "xMidYMid meet" });
    svg.classList.add("graf-svg");
    // ancho lógico del dibujo ≈ ancho real en pantalla: así el texto conserva su tamaño en celulares
    const base = (opciones && opciones.ancho) || (contenedor.clientWidth || window.innerWidth) - 70;
    const W = Math.round(Math.min(640, Math.max(300, base)));
    ({ barras_h: barrasH, columnas, lineas, dispersion: dispersionG, intervalos }[spec.tipo] || columnas)(spec, svg, W);
    fig.appendChild(svg);
    const pie = document.createElement("div");
    pie.className = "graf-pie";
    pie.innerHTML = spec.fuente ? `<span>Fuente: ${spec.fuente}</span>` : "<span></span>";
    if (spec.tooltips || spec.valores_visibles) {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "graf-btn-tabla";
      b.textContent = "Ver tabla";
      let tabla = null;
      b.onclick = () => {
        if (tabla) { tabla.remove(); tabla = null; b.textContent = "Ver tabla"; return; }
        tabla = tablaDe(spec); fig.appendChild(tabla); b.textContent = "Ocultar tabla";
      };
      pie.appendChild(b);
    } else {
      const s = document.createElement("span");
      s.className = "graf-aviso";
      s.textContent = "Estimación a ojo: sin valores";
      pie.appendChild(s);
    }
    fig.appendChild(pie);
    contenedor.appendChild(fig);
    return fig;
  }

  window.Graficos = { dibujar, fmt };
})();
