/**
 * Reglas puras del reto para la opción Cloudflare Workers: las «calculadoras» del contrato C4
 * (contract-summary.md) que necesita el corte delgado (U1).
 *
 * Ninguna función lee la base ni el reloj: reciben los datos y la hora como argumentos (ADR-001,
 * ADR-W3). Las que usan HMAC o SHA-256 son asíncronas porque usan Web Crypto (ADR-W4), que existe
 * igual en Workers y en Node 24, donde corren las pruebas (pruebas/reglas.test.js).
 *
 * Los nombres siguen la forma de C4 (snake_case), la misma en las tres opciones de hosting.
 */

export const ALFABETO = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
export const ESTADOS_SALA = ["inscripcion", "abierto", "cerrado", "resultados"];
export const PUNTOS_TOTALES = 1000;

const BASE32 = "abcdefghijklmnopqrstuvwxyz234567";
const LARGO_OPACO = 11;
const LARGO_OPACO_SIN_CHOQUE = 16;
const CLAVES_MISION = ["id", "titulo", "subtitulo", "intro", "glosario", "lectura", "dossier"];
const CLAVES_PREGUNTA = [
  "id", "tipo", "enunciado", "puntos", "unidad", "min", "max", "paso", "grafico", "tabla", "categorias",
  "estilo", "requiere", "experimento", "entero", "simulador",
];
const CLAVES_ANIDADAS = {
  opciones: ["id", "texto"],
  items: ["id", "texto", "detalle", "encabezado"],
  publicaciones: ["id", "texto", "encabezado"],
  categorias: ["id", "texto"],
  partes: ["id", "etiqueta"],
};
const TRANSICIONES = { inscripcion: ["abierto"] };
const codificador = new TextEncoder();

/**
 * Limpia un texto que escribió una persona (FR10.2): forma NFC, caracteres de control como espacio,
 * invisibles (ancho cero) fuera, espacios juntados y recorte al largo, contado en caracteres.
 * No cambia mayúsculas ni tildes.
 * @param {unknown} texto
 * @param {number} [largo]
 * @returns {string}
 * Justificación: reutilizada en normalizar_codigo, normalizar_nombre y en reto.js (registro, colegios).
 */
export function limpiar(texto, largo = 80) {
  const limpio = String(texto ?? "")
    .normalize("NFC")
    .replace(/\p{Cc}/gu, " ")
    .replace(/\p{Cf}/gu, "")
    .replace(/\s+/gu, " ")
    .trim();
  return Array.from(limpio).slice(0, largo).join("");
}

/**
 * Código que escribe una persona (sala o código personal), como hoy: limpio, 10 caracteres y en
 * mayúsculas (BR1.4).
 * @param {unknown} texto
 * @returns {string}
 * Justificación: reutilizada en reto.js (registro, entrar y ?sala=).
 */
export function normalizar_codigo(texto) {
  return limpiar(texto, 10).toUpperCase();
}

/**
 * Nombre normalizado de un colegio para detectar duplicados (BR2.3, FR10.3): limpio, sin tildes y en
 * minúsculas. Solo sirve para comparar; lo que se muestra es el nombre limpio.
 * @param {unknown} texto
 * @returns {string}
 * Justificación: paso aislado, probado en reglas.test.js («normalizar_nombre iguala mayúsculas y tildes»).
 */
export function normalizar_nombre(texto) {
  return limpiar(texto, 80).normalize("NFD").replace(/\p{M}/gu, "").toLowerCase();
}

/**
 * Revisa la estructura del banco y que sume exactamente 1.000 puntos (BR6.3).
 * @param {any} banco
 * @returns {string[]} lista de errores; vacía si el banco está bien.
 * Justificación: paso aislado, probado en reglas.test.js (grupo «banco»).
 */
export function validar_banco(banco) {
  if (!banco || !Array.isArray(banco.misiones) || banco.misiones.length === 0) {
    return ["El banco no tiene misiones."];
  }
  const errores = [];
  if (!banco.version) errores.push("El banco no tiene versión.");
  if (banco.puntos_totales !== PUNTOS_TOTALES) errores.push("puntos_totales no es 1.000.");
  const ids = new Set();
  let suma = 0;
  for (const pregunta of banco.misiones.flatMap((m) => m.preguntas || [])) {
    if (ids.has(pregunta.id)) errores.push(`Pregunta repetida: ${pregunta.id}.`);
    ids.add(pregunta.id);
    if (typeof pregunta.puntos !== "number") errores.push(`Pregunta sin puntos: ${pregunta.id}.`);
    else suma += pregunta.puntos;
  }
  if (Math.abs(suma - PUNTOS_TOTALES) > 1e-9) errores.push(`Las preguntas suman ${suma}, no 1.000.`);
  return errores;
}

/**
 * SHA-256 en hexadecimal.
 * @param {string} texto
 * @returns {Promise<string>}
 * Justificación: reutilizada en huella_banco, variante_de y en reto.js (huella de la clave de sala).
 */
export async function sha256_hex(texto) {
  const resumen = new Uint8Array(await crypto.subtle.digest("SHA-256", codificador.encode(texto)));
  return Array.from(resumen, (b) => b.toString(16).padStart(2, "0")).join("");
}

/**
 * Huella del banco: SHA-256 del banco serializado con JSON.stringify. La calcula también
 * herramientas/copiar.sh al copiar el banco; si no coinciden, el Worker no arranca (BR6.3).
 * @param {any} banco
 * @returns {Promise<string>}
 * Justificación: paso aislado, probado en reglas.test.js («la huella del banco copiado coincide»).
 */
export async function huella_banco(banco) {
  return sha256_hex(JSON.stringify(banco));
}

/**
 * Compara dos secuencias de bytes en tiempo constante (BR1.2, ADR-W4).
 * @param {Uint8Array} a
 * @param {Uint8Array} b
 * @returns {boolean}
 * Justificación: paso aislado, probado en reglas.test.js («iguales_en_tiempo_constante»).
 */
export function iguales_en_tiempo_constante(a, b) {
  if (a.length !== b.length) return false;
  let diferencia = 0;
  for (let i = 0; i < a.length; i++) diferencia |= a[i] ^ b[i];
  return diferencia === 0;
}

/**
 * @param {Uint8Array} bytes
 * @param {number} largo
 * @returns {string} los primeros `largo` caracteres en base32 (RFC 4648, minúsculas).
 */
function a_base32(bytes, largo) {
  let salida = "";
  let valor = 0;
  let bits = 0;
  for (const byte of bytes) {
    valor = (valor << 8) | byte;
    bits += 8;
    while (bits >= 5 && salida.length < largo) {
      salida += BASE32[(valor >>> (bits - 5)) & 31];
      bits -= 5;
    }
    valor &= (1 << bits) - 1;
    if (salida.length >= largo) break;
  }
  return salida;
}

/**
 * @param {string} semilla
 * @returns {Promise<CryptoKey>} clave HMAC-SHA256 hecha con la semilla del participante.
 */
async function clave_hmac(semilla) {
  return crypto.subtle.importKey(
    "raw", codificador.encode(semilla), { name: "HMAC", hash: "SHA-256" }, false, ["sign"],
  );
}

/**
 * @param {CryptoKey} clave
 * @param {string} ambito
 * @param {string} id
 * @returns {Promise<string>} los 16 caracteres base32 de HMAC(semilla, «ambito|id»).
 */
async function firma_base32(clave, ambito, id) {
  const firma = await crypto.subtle.sign("HMAC", clave, codificador.encode(`${ambito}|${id}`));
  return a_base32(new Uint8Array(firma), LARGO_OPACO_SIN_CHOQUE);
}

/**
 * Ids opacos de un grupo de ids del banco (BR6.1): «o» + 11 caracteres; si dos chocan, 16 para todo el
 * grupo.
 * @param {CryptoKey} clave
 * @param {string} ambito
 * @param {string[]} ids
 * @returns {Promise<Map<string, string>>} id del banco → id opaco.
 */
async function mapa_opaco(clave, ambito, ids) {
  const largos = await Promise.all(ids.map((id) => firma_base32(clave, ambito, id)));
  const cortos = largos.map((texto) => texto.slice(0, LARGO_OPACO));
  const elegidos = new Set(cortos).size === cortos.length ? cortos : largos;
  return new Map(ids.map((id, i) => [id, "o" + elegidos[i]]));
}

/**
 * Id opaco de un id del banco: «o» + 11 caracteres base32 de HMAC-SHA256 con clave la semilla y mensaje
 * «ambito|id» (ADR-006, ADR-W4). El ámbito es el id de la pregunta.
 * @param {string} semilla
 * @param {string} ambito
 * @param {string} id
 * @returns {Promise<string>}
 * Justificación: paso aislado, probado en reglas.test.js («los ids opacos dependen de la semilla»).
 */
export async function opaco_de(semilla, ambito, id) {
  return "o" + (await firma_base32(await clave_hmac(semilla), ambito, id)).slice(0, LARGO_OPACO);
}

/**
 * Ids opacos de todos los ids de una pregunta, con la regla de choque de BR6.1.
 * @param {string} semilla
 * @param {string} ambito
 * @param {string[]} ids
 * @returns {Promise<Map<string, string>>} id del banco → id opaco.
 * Justificación: reutilizada en traducir_opaco y en reto.js (respuestas guardadas que salen opacas).
 */
export async function opacos_de(semilla, ambito, ids) {
  return mapa_opaco(await clave_hmac(semilla), ambito, ids);
}

/**
 * Traduce un id opaco que llega del navegador al id del banco (BR6.1).
 * @param {string} semilla
 * @param {string} ambito
 * @param {string[]} ids ids del banco que puede ser la respuesta.
 * @param {unknown} opaco
 * @returns {Promise<string | null>} el id del banco, o null si no corresponde a ninguno.
 * Justificación: reutilizada en reto.js (responder) y probada en reglas.test.js.
 */
export async function traducir_opaco(semilla, ambito, ids, opaco) {
  const mapa = await opacos_de(semilla, ambito, ids);
  for (const [id, valor] of mapa) if (valor === opaco) return id;
  return null;
}

/**
 * Variante de una pregunta para un participante: sha256(«semilla|id|var») módulo el número de variantes,
 * como variante_de() de servidor.py.
 * @param {string} semilla
 * @param {any} pregunta
 * @returns {Promise<number>}
 */
async function variante_de(semilla, pregunta) {
  if (!pregunta.variantes) return 0;
  const hex = await sha256_hex(`${semilla}|${pregunta.id}|var`);
  return Number(BigInt("0x" + hex) % BigInt(pregunta.variantes.length));
}

/**
 * Pregunta completa (con respuesta) para un participante: la variante que da su semilla.
 * @param {string} semilla
 * @param {any} pregunta pregunta del banco.
 * @returns {Promise<{variante: number, cuerpo: any}>}
 * Justificación: reutilizada en armar_misiones y en reto.js (responder).
 */
export async function resolver(semilla, pregunta) {
  const variante = await variante_de(semilla, pregunta);
  const { variantes, ...cuerpo } = pregunta;
  return { variante, cuerpo: variantes ? { ...cuerpo, ...variantes[variante] } : cuerpo };
}

/**
 * @param {any} pregunta
 * @param {string} grupo grupo A/B del participante.
 * @returns {boolean} si el participante ve la pregunta (solo_grupo).
 * Justificación: reutilizada en armar_misiones y en reto.js (responder).
 */
export function visible_para(pregunta, grupo) {
  return pregunta.solo_grupo == null || pregunta.solo_grupo === grupo;
}

/**
 * @param {any} objeto
 * @param {string[]} claves
 * @returns {any} copia con solo las claves de la lista blanca (BR6.2).
 */
function elegir(objeto, claves) {
  const copia = {};
  for (const clave of claves) if (clave in objeto) copia[clave] = objeto[clave];
  return copia;
}

/**
 * @param {any} pregunta
 * @returns {string} ámbito de ítems y publicaciones: las del Exp. 01 comparten «m1_posts», para que
 *   «¿lo compartirías?» y «¿es verdad?» muestren el mismo orden, como hoy.
 */
function ambito_items(pregunta) {
  return pregunta.id.startsWith("m1_") ? "m1_posts" : pregunta.id;
}

/**
 * Lista pública con ids opacos, ordenada por id opaco: el orden depende de la semilla y no del banco
 * (ADR-W4).
 * @param {CryptoKey} clave
 * @param {string} ambito
 * @param {any[]} objetos
 * @param {string[]} claves lista blanca de cada objeto.
 * @returns {Promise<{publico: any, id_banco: string}[]>}
 */
async function lista_opaca(clave, ambito, objetos, claves) {
  const mapa = await mapa_opaco(clave, ambito, objetos.map((o) => o.id));
  const lista = objetos.map((o) => ({ publico: { ...elegir(o, claves), id: mapa.get(o.id) }, id_banco: o.id }));
  return lista.sort((a, b) => (a.publico.id < b.publico.id ? -1 : 1));
}

/**
 * En «ordenar», el orden que se muestra nunca es la respuesta: si coincide, el primero pasa al final.
 * @param {any} cuerpo
 * @param {{publico: any, id_banco: string}[]} lista
 * @returns {any[]}
 */
function sin_orden_correcto(cuerpo, lista) {
  const coincide = cuerpo.tipo === "ordenar" && lista.map((x) => x.id_banco).join("|") === cuerpo.respuesta.join("|");
  const final = coincide ? [...lista.slice(1), lista[0]] : lista;
  return final.map((x) => x.publico);
}

/**
 * Partes de «construir»: se mantiene el orden de las partes; sus ids y los de sus opciones son opacos.
 * @param {CryptoKey} clave
 * @param {any} pregunta
 * @param {any[]} partes
 * @returns {Promise<any[]>}
 */
async function partes_publicas(clave, pregunta, partes) {
  const ids = await mapa_opaco(clave, `${pregunta.id}|partes`, partes.map((p) => p.id));
  return Promise.all(partes.map(async (parte) => ({
    ...elegir(parte, CLAVES_ANIDADAS.partes),
    id: ids.get(parte.id),
    opciones: (await lista_opaca(clave, `${pregunta.id}|${parte.id}`, parte.opciones, CLAVES_ANIDADAS.opciones))
      .map((x) => x.publico),
  })));
}

/**
 * Lo que ve el navegador de una pregunta: lista blanca de claves, sin respuesta, explicación ni
 * tolerancia, e ids opacos (BR6.1, BR6.2).
 * @param {CryptoKey} clave
 * @param {string} semilla
 * @param {any} pregunta
 * @returns {Promise<any>}
 */
async function pregunta_publica(clave, semilla, pregunta) {
  const { cuerpo } = await resolver(semilla, pregunta);
  const publica = elegir(cuerpo, CLAVES_PREGUNTA);
  if (cuerpo.categorias) publica.categorias = cuerpo.categorias.map((c) => elegir(c, CLAVES_ANIDADAS.categorias));
  if (cuerpo.opciones) {
    publica.opciones = (await lista_opaca(clave, pregunta.id, cuerpo.opciones, CLAVES_ANIDADAS.opciones))
      .map((x) => x.publico);
  }
  if (cuerpo.publicaciones) {
    publica.publicaciones = (await lista_opaca(clave, ambito_items(pregunta), cuerpo.publicaciones,
      CLAVES_ANIDADAS.publicaciones)).map((x) => x.publico);
  }
  if (cuerpo.items) {
    const lista = await lista_opaca(clave, ambito_items(pregunta), cuerpo.items, CLAVES_ANIDADAS.items);
    publica.items = sin_orden_correcto(cuerpo, lista);
  }
  if (cuerpo.partes) publica.partes = await partes_publicas(clave, pregunta, cuerpo.partes);
  return publica;
}

/**
 * Misiones públicas de un participante, con todos los dossiers abiertos. reto.js las guarda en
 * memoria por semilla y aplica los bloqueos en cada petición.
 * @param {any} banco
 * @param {string} semilla
 * @param {string} grupo
 * @returns {Promise<any[]>}
 * Justificación: reutilizada en examen_publico y en reto.js (examen en memoria).
 */
export async function armar_misiones(banco, semilla, grupo) {
  const clave = await clave_hmac(semilla);
  const misiones = [];
  for (const mision of banco.misiones) {
    const visibles = mision.preguntas.filter((q) => visible_para(q, grupo));
    const publica = elegir(mision, CLAVES_MISION);
    publica.preguntas = await Promise.all(visibles.map((q) => pregunta_publica(clave, semilla, q)));
    publica.puntos = visibles.reduce((suma, q) => suma + q.puntos, 0);
    misiones.push(publica);
  }
  return misiones;
}

/**
 * Bloquea el dossier de cada caso hasta que el participante responda la pregunta que lo revela
 * (BR6.2). No modifica las misiones que recibe.
 * @param {any} banco
 * @param {any[]} misiones salida de armar_misiones.
 * @param {Set<string>} respondidas ids del banco ya respondidos.
 * @returns {any[]}
 * Justificación: reutilizada en examen_publico y en reto.js (examen en memoria).
 */
export function aplicar_bloqueos(banco, misiones, respondidas) {
  return misiones.map((mision, i) => {
    const dossier = banco.misiones[i].dossier;
    if (!dossier || !dossier.revelar_tras || respondidas.has(dossier.revelar_tras)) return mision;
    return { ...mision, dossier: { titulo: dossier.titulo, bloqueado: true, n: dossier.graficos.length } };
  });
}

/**
 * Examen público de un participante (C4, «Banco»).
 * @param {any} banco
 * @param {string} semilla
 * @param {string} grupo
 * @param {Set<string>} respondidas
 * @returns {Promise<any[]>} misiones con ids opacos y sin claves secretas.
 * Justificación: paso aislado, probado en reglas.test.js («examen_publico no trae ninguna clave secreta»).
 */
export async function examen_publico(banco, semilla, grupo, respondidas) {
  return aplicar_bloqueos(banco, await armar_misiones(banco, semilla, grupo), respondidas);
}

/**
 * Revisa una respuesta ya traducida a ids del banco (BR5.2). En el corte solo se acepta «opcion».
 * @param {any} pregunta pregunta resuelta.
 * @param {unknown} respuesta
 * @returns {{valor: string} | {error: "tipo" | "formato"}}
 * Justificación: reutilizada en reto.js (responder) y probada en reglas.test.js.
 */
export function validar_respuesta(pregunta, respuesta) {
  if (pregunta.tipo !== "opcion") return { error: "tipo" };
  const ids = pregunta.opciones.map((o) => o.id);
  if (typeof respuesta !== "string" || !ids.includes(respuesta)) return { error: "formato" };
  return { valor: respuesta };
}

/**
 * Fracción de acierto, de 0 a 1 (BR5.2): una pregunta sin puntos da 0; «opcion» da 1 si coincide.
 * @param {any} pregunta pregunta resuelta.
 * @param {string} respuesta respuesta validada, con ids del banco.
 * @returns {number}
 * Justificación: reutilizada en reto.js (responder) y probada en reglas.test.js.
 */
export function fraccion(pregunta, respuesta) {
  if (!pregunta.puntos) return 0;
  if (pregunta.tipo === "opcion") return respuesta === pregunta.respuesta ? 1 : 0;
  throw new RangeError(`El corte no califica preguntas de tipo ${pregunta.tipo}.`);
}

/**
 * Bono de tiempo (BR4.3): bono_max × (puntos / puntos_totales) × (1 − tiempo_respuestas / duración).
 * @param {number} puntos
 * @param {number} tiempo_respuestas segundos desde el inicio hasta la última respuesta.
 * @param {number} duracion segundos.
 * @param {{bono_max?: number, puntos_totales?: number}} [banco] valores del banco.
 * @returns {number}
 * Justificación: reutilizada en cerrar_intento y probada en reglas.test.js.
 */
export function bono(puntos, tiempo_respuestas, duracion, { bono_max = 20, puntos_totales = PUNTOS_TOTALES } = {}) {
  return bono_max * (puntos / puntos_totales) * (1 - tiempo_respuestas / duracion);
}

/**
 * Números con los que se cierra un intento (BR4.3), como finalizar() de servidor.py.
 * @param {{ahora: number, inicio: number, duracion: number, ultima: number | null, puntos: number}} datos
 * @param {{bono_max?: number, puntos_totales?: number}} [banco]
 * @returns {{fin: number, tiempo_usado: number, tiempo_respuestas: number, bono: number, total: number}}
 * Justificación: reutilizada en reto.js (entregar y entrega por tiempo) y probada en reglas.test.js.
 */
export function cerrar_intento({ ahora, inicio, duracion, ultima, puntos }, banco = {}) {
  const fin = Math.min(ahora, inicio + duracion);
  const tiempo_usado = Math.max(0, fin - inicio);
  const tiempo_respuestas = Math.min(duracion, Math.max(0, (ultima ?? fin) - inicio));
  const extra = bono(puntos, tiempo_respuestas, duracion, banco);
  return { fin, tiempo_usado, tiempo_respuestas, bono: extra, total: puntos + extra };
}

/**
 * Si un cambio de estado de sala está permitido (BR2.2). En el corte solo inscripción → abierto; U5
 * completa las demás.
 * @param {string} actual
 * @param {string} nuevo
 * @returns {boolean}
 * Justificación: reutilizada en reto.js (cambiar estado) y probada en reglas.test.js.
 */
export function transicion_permitida(actual, nuevo) {
  return (TRANSICIONES[actual] || []).includes(nuevo);
}

/**
 * Cuándo se entrega solo un intento (BR4.2): por cierre de la sala o por tiempo.
 * @param {number} ahora
 * @param {number} inicio
 * @param {number} duracion segundos.
 * @param {number | null} cierre hora de cierre de la sala; en el corte siempre es null (U5).
 * @returns {{hora: number, motivo: "cierre" | "tiempo"} | null}
 * Justificación: reutilizada en reto.js (entrega por tiempo) y probada en reglas.test.js.
 */
export function hora_de_entrega(ahora, inicio, duracion, cierre) {
  const fin = inicio + duracion;
  if (cierre != null && cierre <= ahora && cierre < fin) return { hora: cierre, motivo: "cierre" };
  if (ahora >= fin) return { hora: fin, motivo: "tiempo" };
  return null;
}
