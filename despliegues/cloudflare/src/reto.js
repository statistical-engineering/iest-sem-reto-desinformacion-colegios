/**
 * Durable Object «Reto»: un solo objeto con su base SQLite para todo el servicio (ADR-W1). Tiene la
 * tabla de rutas con el nivel de acceso de cada una (BR1.1), el acceso con claves (BR1.2, BR1.3), las
 * salas, la inscripción, el examen y el SQL (ADR-W3). Las reglas puras están en reglas.js.
 *
 * «Sin cruzarse»: cada petición se atiende entera dentro de blockConcurrencyWhile, así que dos
 * peticiones nunca se mezclan, igual que el candado LOCK de servidor.py.
 * Las horas se guardan en segundos desde 1970 y la entrega por tiempo se aplica en cada petición.
 */
import { DurableObject } from "cloudflare:workers";

import banco from "./banco.json";
import huella_copiada from "./banco_huella.json";
import * as R from "./reglas.js";

const TOPE_CUERPO = 65536;
const ESPERA_CODIGO_MS = 600;
const LETRAS_SALA = R.ALFABETO.slice(0, 24);
const PREGUNTAS = new Map(banco.misiones.flatMap((m) => m.preguntas.map((q) => [q.id, q])));
const META_BANCO = { bono_max: banco.bono_tiempo_max, puntos_totales: banco.puntos_totales };
const MENSAJE_CLAVE = "Clave de docente incorrecta.";
const MENSAJE_SESION = "Sesión no encontrada. Vuelve a entrar con tu código.";
const MENSAJE_REPETIDO = "Ya hay alguien inscrito con ese nombre en ese colegio y grado. Si eres tú, entra con tu "
  + "código; si no, agrega tu segundo apellido.";

/** Tabla de rutas del corte (functional-spec.md, «Rutas del corte»). Lo que no está aquí da 404. */
const RUTAS = {
  "GET /api/publico": { nivel: "publico", funcion: "publico" },
  "GET /api/colegios": { nivel: "publico", funcion: "colegios" },
  "POST /api/registro": { nivel: "publico", funcion: "registrar" },
  "POST /api/entrar": { nivel: "publico", funcion: "entrar" },
  "GET /api/estado": { nivel: "token", funcion: "estado" },
  "POST /api/comenzar": { nivel: "token", funcion: "comenzar" },
  "POST /api/responder": { nivel: "token", funcion: "responder" },
  "POST /api/finalizar": { nivel: "token", funcion: "finalizar" },
  "POST /api/evento": { nivel: "token", funcion: "evento" },
  "POST /api/admin/login": { nivel: "clave", funcion: "login" },
  "POST /api/admin/salas/crear": { nivel: "semillero", funcion: "crear_sala" },
  "POST /api/admin/colegios": { nivel: "sala", funcion: "agregar_colegio" },
  "POST /api/admin/estado": { nivel: "sala", funcion: "cambiar_estado" },
};

/** Esquema SQLite del objeto (entities.md). Las restricciones UNIQUE hacen cumplir la unicidad en todo el servicio. */
const ESQUEMA = [
  `CREATE TABLE IF NOT EXISTS salas (
    id_sala INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    estado TEXT NOT NULL DEFAULT 'inscripcion' CHECK (estado IN ('inscripcion', 'abierto', 'cerrado', 'resultados')),
    clave_huella TEXT NOT NULL,
    evento TEXT,
    duracion_min REAL NOT NULL,
    reloj_global INTEGER NOT NULL DEFAULT 1,
    retro INTEGER NOT NULL DEFAULT 1,
    modo_sorpresa INTEGER NOT NULL DEFAULT 1,
    creada REAL NOT NULL,
    abierta REAL,
    cerrada REAL)`,
  `CREATE TABLE IF NOT EXISTS colegios (
    id_colegio TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    nombre_normalizado TEXT NOT NULL UNIQUE,
    provisional INTEGER NOT NULL DEFAULT 1,
    creado REAL NOT NULL)`,
  `CREATE TABLE IF NOT EXISTS sala_colegios (
    id_sala INTEGER NOT NULL REFERENCES salas (id_sala),
    id_colegio TEXT NOT NULL REFERENCES colegios (id_colegio),
    PRIMARY KEY (id_sala, id_colegio))`,
  `CREATE TABLE IF NOT EXISTS participantes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_sala INTEGER NOT NULL REFERENCES salas (id_sala),
    codigo TEXT NOT NULL UNIQUE,
    token TEXT NOT NULL UNIQUE,
    semilla TEXT NOT NULL,
    nombre TEXT NOT NULL,
    id_colegio TEXT NOT NULL REFERENCES colegios (id_colegio),
    grado TEXT NOT NULL,
    integrantes TEXT,
    grupo TEXT NOT NULL,
    estado TEXT NOT NULL DEFAULT 'registrado',
    creado REAL NOT NULL,
    inicio REAL,
    fin REAL,
    motivo_fin TEXT,
    puntos REAL NOT NULL DEFAULT 0,
    bono REAL NOT NULL DEFAULT 0,
    total REAL NOT NULL DEFAULT 0,
    tiempo_usado REAL,
    tiempo_respuestas REAL,
    salidas INTEGER NOT NULL DEFAULT 0)`,
  `CREATE UNIQUE INDEX IF NOT EXISTS participante_unico ON participantes (id_sala, lower(nombre), id_colegio, grado)`,
  `CREATE INDEX IF NOT EXISTS participantes_estado ON participantes (estado)`,
  `CREATE TABLE IF NOT EXISTS respuestas (
    participante_id INTEGER NOT NULL REFERENCES participantes (id),
    pregunta_id TEXT NOT NULL,
    variante INTEGER NOT NULL,
    respuesta TEXT NOT NULL,
    fraccion REAL NOT NULL,
    puntos REAL NOT NULL,
    max_puntos REAL NOT NULL,
    momento REAL NOT NULL,
    PRIMARY KEY (participante_id, pregunta_id))`,
  `CREATE TABLE IF NOT EXISTS eventos (
    id_evento INTEGER PRIMARY KEY AUTOINCREMENT,
    participante_id INTEGER NOT NULL REFERENCES participantes (id),
    tipo TEXT NOT NULL,
    momento REAL NOT NULL)`,
];

/** Error que ve el navegador: mensaje en español, código HTTP y claves extra (por ejemplo «existente»). */
class ErrorAPI extends Error {
  /**
   * @param {string} mensaje
   * @param {number} [codigo]
   * @param {object} [extra]
   */
  constructor(mensaje, codigo = 400, extra = {}) {
    super(mensaje);
    this.codigo = codigo;
    this.extra = extra;
    this.esperar_ms = 0;
  }
}

/**
 * Única salida de respuestas: JSON con las cabeceras de hoy (U1-S8, U1-S9).
 * @param {number} codigo
 * @param {unknown} cuerpo
 * @returns {Response}
 * Justificación: reutilizada en Reto.atender y en worker.js.
 */
export function respuesta_json(codigo, cuerpo) {
  return new Response(JSON.stringify(cuerpo), {
    status: codigo,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
    },
  });
}

/**
 * Lee el cuerpo JSON con tope de 65.536 bytes (U1-S7). Un cuerpo vacío es {}.
 * @param {Request} peticion
 * @returns {Promise<object>}
 */
async function leer_cuerpo(peticion) {
  if (Number(peticion.headers.get("Content-Length") || 0) > TOPE_CUERPO) {
    throw new ErrorAPI("Petición demasiado grande.", 413);
  }
  const partes = [];
  let total = 0;
  const lector = peticion.body ? peticion.body.getReader() : null;
  for (let leido = lector && (await lector.read()); leido && !leido.done; leido = await lector.read()) {
    total += leido.value.length;
    if (total > TOPE_CUERPO) {
      await lector.cancel();
      throw new ErrorAPI("Petición demasiado grande.", 413);
    }
    partes.push(leido.value);
  }
  const texto = new TextDecoder().decode(await new Blob(partes).arrayBuffer());
  return texto.trim() === "" ? {} : leer_json(texto);
}

/**
 * @param {string} texto
 * @returns {object} el objeto JSON; un JSON roto o que no es objeto da 400.
 */
function leer_json(texto) {
  let datos;
  try {
    datos = JSON.parse(texto);
  } catch (error) {
    if (error instanceof SyntaxError) throw new ErrorAPI("JSON no válido.");
    throw error;
  }
  if (datos === null || typeof datos !== "object" || Array.isArray(datos)) throw new ErrorAPI("JSON no válido.");
  return datos;
}

/**
 * Texto al azar con el generador seguro de Web Crypto, sin sesgo (descarta bytes fuera de rango).
 * @param {string} alfabeto
 * @param {number} largo
 * @returns {string}
 */
function al_azar(alfabeto, largo) {
  const limite = 256 - (256 % alfabeto.length);
  let salida = "";
  while (salida.length < largo) {
    for (const byte of crypto.getRandomValues(new Uint8Array(largo * 2))) {
      if (byte < limite && salida.length < largo) salida += alfabeto[byte % alfabeto.length];
    }
  }
  return salida;
}

/**
 * @param {number} cantidad
 * @returns {Uint8Array} bytes al azar.
 */
function bytes_al_azar(cantidad) {
  return crypto.getRandomValues(new Uint8Array(cantidad));
}

/**
 * @param {number} valor
 * @param {number} decimales
 * @returns {number}
 */
function redondear(valor, decimales) {
  const escala = 10 ** decimales;
  return Math.round(valor * escala) / escala;
}

/**
 * Clave del semillero (secreto CLAVE_SEMILLERO): al menos 12 caracteres y sin guion (U1-S4, BR1.2).
 * @param {unknown} valor
 * @returns {string} la clave en mayúsculas.
 */
function clave_semillero(valor) {
  const clave = String(valor || "").trim().toUpperCase();
  if (clave.length < 12 || clave.includes("-")) {
    throw new Error("CLAVE_SEMILLERO no está configurada o no sirve: necesita 12 caracteres o más y sin guion.");
  }
  return clave;
}

/**
 * Revisa al arrancar que el banco sume 1.000 puntos y que su huella coincida con la de copiar.sh (BR6.3).
 * @returns {Promise<string | null>} el motivo por el que no arranca, o null si está bien.
 */
async function revisar_banco() {
  const errores = R.validar_banco(banco);
  if ((await R.huella_banco(banco)) !== huella_copiada.sha256) {
    errores.push("La huella de src/banco.json no coincide: vuelve a correr herramientas/copiar.sh.");
  }
  return errores.length ? errores.join(" ") : null;
}

export class Reto extends DurableObject {
  /**
   * @param {DurableObjectState} ctx
   * @param {object} env
   */
  constructor(ctx, env) {
    super(ctx, env);
    this.sql = ctx.storage.sql;
    this.examenes = new Map();
    this.error_arranque = null;
    ctx.blockConcurrencyWhile(async () => {
      for (const sentencia of ESQUEMA) this.sql.exec(sentencia);
      this.error_arranque = await revisar_banco();
      if (this.error_arranque) console.error("El servicio no arranca:", this.error_arranque);
      else console.log(`Arranque: banco ${banco.version}, ${PREGUNTAS.size} preguntas.`);
    });
  }

  /**
   * Atiende una petición sin cruzarse con otra; la espera de «entrar» va después, fuera del bloqueo.
   * @param {Request} peticion
   * @returns {Promise<Response>}
   */
  async fetch(peticion) {
    const { salida, esperar_ms } = await this.ctx.blockConcurrencyWhile(() => this.atender(peticion));
    if (esperar_ms) await new Promise((listo) => setTimeout(listo, esperar_ms));
    return salida;
  }

  /**
   * Punto único de entrada y de errores: nunca lanza (un error dentro de blockConcurrencyWhile
   * reiniciaría el objeto).
   * @param {Request} peticion
   * @returns {Promise<{salida: Response, esperar_ms?: number}>}
   */
  async atender(peticion) {
    try {
      if (this.error_arranque) throw new Error(this.error_arranque);
      const url = new URL(peticion.url);
      const ruta = RUTAS[`${peticion.method} ${url.pathname}`];
      if (!ruta) throw new ErrorAPI("No encontrado.", 404);
      const datos = peticion.method === "POST" ? await leer_cuerpo(peticion) : {};
      const contexto = { url, ahora: Date.now() / 1000, datos };
      this.vencer_tiempos(contexto.ahora);
      await this.dar_acceso(ruta.nivel, peticion, contexto);
      return { salida: respuesta_json(200, await this[ruta.funcion](contexto)) };
    } catch (error) {
      if (error instanceof ErrorAPI) {
        const cuerpo = { error: error.message, ...error.extra };
        return { salida: respuesta_json(error.codigo, cuerpo), esperar_ms: error.esperar_ms };
      }
      console.error("Error interno:", error instanceof Error ? error.stack || error.message : String(error));
      return { salida: respuesta_json(500, { error: "Error interno del servidor." }) };
    }
  }

  /**
   * @param {string} consulta
   * @param {...unknown} valores
   * @returns {any} la primera fila o null.
   */
  una(consulta, ...valores) {
    return this.sql.exec(consulta, ...valores).toArray()[0] ?? null;
  }

  /**
   * @param {string} consulta
   * @param {...unknown} valores
   * @returns {any[]} todas las filas.
   */
  todas(consulta, ...valores) {
    return this.sql.exec(consulta, ...valores).toArray();
  }

  /**
   * Genera un código al azar que no exista (la consulta recibe el código y devuelve una fila si existe).
   * @param {string} consulta
   * @param {number} largo
   * @param {string} alfabeto
   * @returns {string}
   */
  codigo_libre(consulta, largo, alfabeto) {
    for (;;) {
      const codigo = al_azar(alfabeto, largo);
      if (!this.una(consulta, codigo)) return codigo;
    }
  }

  /**
   * @param {unknown} texto código de sala que llega en ?sala= o en el cuerpo.
   * @param {string} mensaje mensaje del 404.
   * @param {number} [codigo_http]
   * @returns {any} la sala.
   */
  sala_por_codigo(texto, mensaje = "No existe esa sala.", codigo_http = 404) {
    const sala = this.una("SELECT * FROM salas WHERE codigo = ?", R.normalizar_codigo(texto));
    if (!sala) throw new ErrorAPI(mensaje, codigo_http);
    return sala;
  }

  /**
   * @param {any} participante
   * @returns {any} la sala del participante.
   */
  sala_de(participante) {
    return this.una("SELECT * FROM salas WHERE id_sala = ?", participante.id_sala);
  }

  /**
   * Aplica el nivel de la ruta (BR1.1) y deja en el contexto el participante, el acceso o la sala.
   * @param {string} nivel publico, token, clave, semillero o sala.
   * @param {Request} peticion
   * @param {any} contexto
   * @returns {Promise<void>}
   */
  async dar_acceso(nivel, peticion, contexto) {
    if (nivel === "publico") return;
    if (nivel === "token") {
      const autorizacion = peticion.headers.get("Authorization") || "";
      const token = autorizacion.startsWith("Bearer ") ? autorizacion.slice(7) : "";
      contexto.participante = token ? this.una("SELECT * FROM participantes WHERE token = ?", token) : null;
      if (!contexto.participante) throw new ErrorAPI(MENSAJE_SESION, 401);
      return;
    }
    contexto.acceso = await this.acceso_admin(peticion);
    if (nivel === "semillero" && contexto.acceso.rol !== "semillero") throw new ErrorAPI(MENSAJE_CLAVE, 403);
    if (nivel === "sala") contexto.sala = this.sala_de_acceso(contexto.acceso, contexto.url);
  }

  /**
   * Clave de la cabecera X-Clave-Admin, en mayúsculas y en tiempo constante (BR1.2). ?clave= no se lee.
   * @param {Request} peticion
   * @returns {Promise<{rol: "sala" | "semillero", sala?: any}>}
   */
  async acceso_admin(peticion) {
    const semillero = clave_semillero(this.env.CLAVE_SEMILLERO);
    const clave = (peticion.headers.get("X-Clave-Admin") || "").trim().toUpperCase();
    const codificar = (texto) => new TextEncoder().encode(texto);
    const forma = /^([A-Z0-9]{3,8})-(.+)$/.exec(clave);
    if (forma) {
      const huella = await R.sha256_hex(forma[2]);
      const sala = this.una("SELECT * FROM salas WHERE codigo = ?", forma[1]);
      const coincide = sala && R.iguales_en_tiempo_constante(codificar(huella), codificar(sala.clave_huella));
      if (coincide) return { rol: "sala", sala };
      throw new ErrorAPI(MENSAJE_CLAVE, 403);
    }
    const [dada, esperada] = await Promise.all([R.sha256_hex(clave), R.sha256_hex(semillero)]);
    if (clave && R.iguales_en_tiempo_constante(codificar(dada), codificar(esperada))) return { rol: "semillero" };
    throw new ErrorAPI(MENSAJE_CLAVE, 403);
  }

  /**
   * Con la clave de una sala solo se actúa sobre esa sala; con la del semillero hay que nombrarla (BR1.3).
   * @param {{rol: string, sala?: any}} acceso
   * @param {URL} url
   * @returns {any} la sala sobre la que se actúa.
   */
  sala_de_acceso(acceso, url) {
    const pedida = url.searchParams.has("sala") ? R.normalizar_codigo(url.searchParams.get("sala")) : null;
    if (acceso.rol === "sala") {
      if (pedida && pedida !== acceso.sala.codigo) throw new ErrorAPI("Esa clave no es de esta sala.", 403);
      return acceso.sala;
    }
    if (!pedida) throw new ErrorAPI("Falta la sala.");
    return this.sala_por_codigo(pedida);
  }

  /**
   * Entrega por tiempo de todo intento vencido, antes de cada operación (BR4.2), como vencer_tiempos().
   * @param {number} ahora
   */
  vencer_tiempos(ahora) {
    const en_curso = this.todas(
      "SELECT p.*, s.duracion_min FROM participantes p JOIN salas s ON s.id_sala = p.id_sala "
        + "WHERE p.estado = 'en_curso'",
    );
    for (const participante of en_curso) {
      const entrega = R.hora_de_entrega(ahora, participante.inicio, participante.duracion_min * 60, null);
      if (entrega) this.cerrar(participante, entrega.hora, entrega.motivo);
    }
  }

  /**
   * @param {number} id_participante
   * @returns {number} los puntos, recalculados desde sus respuestas.
   */
  recalcular_puntos(id_participante) {
    const consulta = "SELECT COALESCE(SUM(puntos), 0) AS suma FROM respuestas WHERE participante_id = ?";
    const { suma } = this.una(consulta, id_participante);
    this.sql.exec("UPDATE participantes SET puntos = ?, total = ? + bono WHERE id = ?", suma, suma, id_participante);
    return suma;
  }

  /**
   * Cierra el intento (BR4.3), como finalizar() de servidor.py.
   * @param {any} participante
   * @param {number} ahora
   * @param {string} motivo entrega o tiempo.
   */
  cerrar(participante, ahora, motivo) {
    if (participante.estado !== "en_curso") return;
    const sala = this.sala_de(participante);
    const consulta = "SELECT MAX(momento) AS ultima FROM respuestas WHERE participante_id = ?";
    const { ultima } = this.una(consulta, participante.id);
    this.ctx.storage.transactionSync(() => {
      const puntos = this.recalcular_puntos(participante.id);
      const datos = { ahora, inicio: participante.inicio, duracion: sala.duracion_min * 60, ultima, puntos };
      const cierre = R.cerrar_intento(datos, META_BANCO);
      this.sql.exec(
        "UPDATE participantes SET estado = 'finalizado', fin = ?, tiempo_usado = ?, tiempo_respuestas = ?, bono = ?, "
          + "total = ?, motivo_fin = ? WHERE id = ?",
        cierre.fin, cierre.tiempo_usado, cierre.tiempo_respuestas, cierre.bono, cierre.total, motivo, participante.id,
      );
    });
  }

  /**
   * @param {number} id_participante
   * @param {string} pregunta_id
   * @returns {boolean}
   */
  ya_respondida(id_participante, pregunta_id) {
    const consulta = "SELECT 1 FROM respuestas WHERE participante_id = ? AND pregunta_id = ?";
    return !!this.una(consulta, id_participante, pregunta_id);
  }

  /**
   * Examen del participante: se arma una vez por semilla y queda en memoria (U1-P4); los dossiers se
   * bloquean en cada petición.
   * @param {any} participante
   * @param {Set<string>} respondidas
   * @returns {Promise<any[]>}
   */
  async examen_de(participante, respondidas) {
    if (!this.examenes.has(participante.semilla)) {
      this.examenes.set(participante.semilla, await R.armar_misiones(banco, participante.semilla, participante.grupo));
    }
    return R.aplicar_bloqueos(banco, this.examenes.get(participante.semilla), respondidas);
  }

  /**
   * Respuesta guardada (ids del banco) tal como sale al navegador: con su id opaco (BR6.1).
   * @param {any} participante
   * @param {any} fila fila de respuestas.
   * @returns {Promise<unknown>}
   */
  async respuesta_publica(participante, fila) {
    const valor = JSON.parse(fila.respuesta);
    const { cuerpo } = await R.resolver(participante.semilla, PREGUNTAS.get(fila.pregunta_id));
    if (typeof valor !== "string" || !cuerpo.opciones) return valor;
    const mapa = await R.opacos_de(participante.semilla, fila.pregunta_id, cuerpo.opciones.map((o) => o.id));
    return mapa.get(valor) ?? valor;
  }

  /** F9, BR7.1: salud sin ?sala=; con ?sala=, lo básico del tablero con las claves de hoy. */
  publico(contexto) {
    if (!contexto.url.searchParams.has("sala")) return { ok: true };
    const sala = this.sala_por_codigo(contexto.url.searchParams.get("sala"));
    const cuenta = Object.fromEntries(this.todas(
      "SELECT estado, COUNT(*) AS n FROM participantes WHERE id_sala = ? GROUP BY estado", sala.id_sala,
    ).map((fila) => [fila.estado, fila.n]));
    const todos = Object.values(cuenta).reduce((suma, n) => suma + n, 0);
    return {
      evento: sala.evento,
      titulo: banco.titulo,
      estado: sala.estado,
      sala: sala.codigo,
      urls: [contexto.url.origin],
      duracion_min: sala.duracion_min,
      abierto_en: sala.abierta || 0,
      cerrado_en: sala.cerrada || 0,
      servidor_ahora: contexto.ahora,
      modo_sorpresa: !!sala.modo_sorpresa,
      reloj_global: !!sala.reloj_global,
      conteo: {
        inscritos: todos - (cuenta.descalificado || 0),
        en_curso: cuenta.en_curso || 0,
        finalizados: cuenta.finalizado || 0,
      },
    };
  }

  /** F4: colegios que ofrece la sala, para la lista de la inscripción. */
  colegios(contexto) {
    if (!contexto.url.searchParams.has("sala")) throw new ErrorAPI("Falta la sala.");
    const sala = this.sala_por_codigo(contexto.url.searchParams.get("sala"));
    const colegios = this.todas(
      "SELECT c.id_colegio, c.nombre FROM sala_colegios sc JOIN colegios c ON c.id_colegio = sc.id_colegio "
        + "WHERE sc.id_sala = ? ORDER BY c.nombre COLLATE NOCASE",
      sala.id_sala,
    );
    return { colegios };
  }

  /** F4: inscripción (BR3.1 a BR3.4), revisada y escrita sin cruzarse con otra. */
  registrar(contexto) {
    const datos = contexto.datos;
    const sala = this.sala_por_codigo(datos.sala, "El código de sala no es correcto. Míralo en el tablero.", 400);
    if (!["inscripcion", "abierto"].includes(sala.estado)) throw new ErrorAPI("Las inscripciones están cerradas.");
    const nombre = R.limpiar(datos.nombre, 60);
    const grado = R.limpiar(datos.grado, 10);
    if (Array.from(nombre).length < 3) throw new ErrorAPI("Escribe tu nombre (o el del equipo).");
    if (!["9", "10", "11"].includes(grado)) throw new ErrorAPI("Elige el grado: 9, 10 u 11.");
    const colegio = this.una(
      "SELECT id_colegio FROM sala_colegios WHERE id_sala = ? AND id_colegio = ?",
      sala.id_sala, String(datos.colegio ?? ""),
    );
    if (!colegio) throw new ErrorAPI("Elige tu colegio de la lista.");
    const repetido = this.una(
      "SELECT 1 FROM participantes WHERE id_sala = ? AND lower(nombre) = lower(?) AND id_colegio = ? AND grado = ?",
      sala.id_sala, nombre, colegio.id_colegio, grado,
    );
    if (repetido) throw new ErrorAPI(MENSAJE_REPETIDO);
    const { n } = this.una("SELECT COUNT(*) AS n FROM participantes WHERE id_sala = ?", sala.id_sala);
    const codigo = this.codigo_libre("SELECT 1 FROM participantes WHERE codigo = ?", 5, R.ALFABETO);
    const token = btoa(String.fromCharCode(...bytes_al_azar(24))).replace(/\+/g, "-").replace(/\//g, "_");
    const semilla = Array.from(bytes_al_azar(8), (b) => b.toString(16).padStart(2, "0")).join("");
    this.sql.exec(
      "INSERT INTO participantes (id_sala, codigo, token, semilla, nombre, id_colegio, grado, integrantes, grupo, "
        + "estado, creado) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'registrado', ?)",
      sala.id_sala, codigo, token, semilla, nombre, colegio.id_colegio, grado, R.limpiar(datos.integrantes, 200),
      "AB"[n % 2], contexto.ahora,
    );
    return { token, codigo };
  }

  /** F5: volver a entrar con el código personal; si no existe, 404 después de una espera corta (BR3.4). */
  entrar(contexto) {
    const codigo = R.normalizar_codigo(contexto.datos.codigo);
    const fila = this.una("SELECT token, codigo FROM participantes WHERE codigo = ?", codigo);
    if (!fila) {
      const error = new ErrorAPI("No encontramos ese código. Revísalo (son 5 caracteres).", 404);
      error.esperar_ms = ESPERA_CODIGO_MS;
      throw error;
    }
    return { token: fila.token, codigo: fila.codigo };
  }

  /** F7: estado del participante con las claves de hoy, misiones e ids opacos (BR6.1, BR6.2). */
  async estado(contexto) {
    const participante = contexto.participante;
    const sala = this.sala_de(participante);
    const colegio = this.una("SELECT nombre FROM colegios WHERE id_colegio = ?", participante.id_colegio);
    const filas = this.todas("SELECT * FROM respuestas WHERE participante_id = ?", participante.id);
    const retro = !!sala.retro || sala.estado === "resultados";
    const respuestas = {};
    for (const fila of filas) {
      const item = { respuesta: await this.respuesta_publica(participante, fila) };
      if (retro) {
        item.puntos = redondear(fila.puntos, 2);
        item.max = fila.max_puntos;
        item.fraccion = redondear(fila.fraccion, 4);
      }
      respuestas[fila.pregunta_id] = item;
    }
    const en_curso = participante.estado === "en_curso";
    const datos = {
      reto: {
        titulo: banco.titulo, evento: sala.evento, estado: sala.estado, n_misiones: banco.misiones.length,
        duracion_min: sala.duracion_min, puntos_totales: banco.puntos_totales, bono_max: banco.bono_tiempo_max,
        retro, reloj_global: !!sala.reloj_global,
      },
      participante: {
        codigo: participante.codigo, nombre: participante.nombre, colegio: colegio ? colegio.nombre : "",
        grado: participante.grado, estado: participante.estado, tiempo_usado: participante.tiempo_usado,
        restante_seg: en_curso ? Math.max(0, participante.inicio + sala.duracion_min * 60 - contexto.ahora) : null,
      },
      respuestas,
      servidor_ahora: contexto.ahora,
    };
    if (en_curso || participante.estado === "finalizado") {
      datos.misiones = await this.examen_de(participante, new Set(filas.map((f) => f.pregunta_id)));
    }
    if (participante.estado === "finalizado" && retro) {
      Object.assign(datos.participante, {
        puntos: redondear(participante.puntos, 2),
        bono: redondear(participante.bono, 2),
        total: redondear(participante.total, 2),
      });
    }
    return datos;
  }

  /** F6: comenzar guarda la hora del servidor (BR4.1). */
  comenzar(contexto) {
    const participante = contexto.participante;
    if (participante.estado !== "registrado") return { ok: true };
    const sala = this.sala_de(participante);
    if (sala.estado !== "abierto") throw new ErrorAPI("El reto todavía no ha empezado. Espera la señal del docente.");
    let inicio = contexto.ahora;
    if (sala.reloj_global) {
      if (sala.abierta) inicio = sala.abierta;
      if (contexto.ahora >= inicio + sala.duracion_min * 60) throw new ErrorAPI("El tiempo del reto ya terminó.");
    }
    this.sql.exec("UPDATE participantes SET estado = 'en_curso', inicio = ? WHERE id = ?", inicio, participante.id);
    return { ok: true };
  }

  /** F8: responder una sola vez, en orden y solo lo visible (BR5.1); en el corte solo «opcion» (BR5.2). */
  async responder(contexto) {
    const { participante, datos } = contexto;
    if (participante.estado !== "en_curso") throw new ErrorAPI("Tu intento ya terminó.");
    const sala = this.sala_de(participante);
    if (sala.estado !== "abierto") throw new ErrorAPI("El reto está cerrado.");
    const pregunta = typeof datos.pregunta === "string" ? PREGUNTAS.get(datos.pregunta) : undefined;
    if (!pregunta) throw new ErrorAPI("Pregunta desconocida.");
    if (!R.visible_para(pregunta, participante.grupo)) throw new ErrorAPI("Pregunta no disponible.");
    if (this.ya_respondida(participante.id, pregunta.id)) throw new ErrorAPI("Esa pregunta ya fue respondida.");
    if (pregunta.requiere && !this.ya_respondida(participante.id, pregunta.requiere)) {
      throw new ErrorAPI("Primero responde la parte anterior de esta misión.");
    }
    const { variante, cuerpo } = await R.resolver(participante.semilla, pregunta);
    const traducida = cuerpo.tipo === "opcion"
      ? await R.traducir_opaco(participante.semilla, pregunta.id, cuerpo.opciones.map((o) => o.id), datos.respuesta)
      : null;
    const revisada = R.validar_respuesta(cuerpo, traducida);
    if (revisada.error === "tipo") throw new ErrorAPI("Tipo de pregunta aún no disponible.");
    if (revisada.error) throw new ErrorAPI("Respuesta incompleta o con formato no válido.");
    const parte = R.fraccion(cuerpo, revisada.valor);
    const puntos = parte * pregunta.puntos;
    this.ctx.storage.transactionSync(() => {
      this.sql.exec(
        "INSERT INTO respuestas (participante_id, pregunta_id, variante, respuesta, fraccion, puntos, max_puntos, "
          + "momento) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        participante.id, pregunta.id, variante, JSON.stringify(revisada.valor), parte, puntos, pregunta.puntos,
        contexto.ahora,
      );
      this.recalcular_puntos(participante.id);
    });
    if (!sala.retro) return { ok: true };
    return { ok: true, puntos: redondear(puntos, 2), max: pregunta.puntos, fraccion: redondear(parte, 4) };
  }

  /** F10: entregar (BR4.3). */
  finalizar(contexto) {
    this.cerrar(contexto.participante, contexto.ahora, "entrega");
    return { ok: true };
  }

  /** F11: salida de pantalla (BR4.4); siempre responde ok, como hoy. */
  evento(contexto) {
    const participante = contexto.participante;
    if (contexto.datos.tipo === "salida" && participante.estado === "en_curso") {
      this.ctx.storage.transactionSync(() => {
        this.sql.exec("UPDATE participantes SET salidas = salidas + 1 WHERE id = ?", participante.id);
        const insertar = "INSERT INTO eventos (participante_id, tipo, momento) VALUES (?, 'salida', ?)";
        this.sql.exec(insertar, participante.id, contexto.ahora);
      });
    }
    return { ok: true };
  }

  /** Contrato C1: entrar al panel; dice el rol y, con clave de sala, la sala. */
  login(contexto) {
    const { rol, sala } = contexto.acceso;
    return rol === "sala" ? { ok: true, rol, sala: sala.codigo } : { ok: true, rol };
  }

  /** F1: crear una sala (solo semillero, BR2.1). La clave se devuelve una sola vez; se guarda su huella. */
  async crear_sala(contexto) {
    const secreto = al_azar(R.ALFABETO, 16);
    const huella = await R.sha256_hex(secreto);
    const codigo = this.codigo_libre("SELECT 1 FROM salas WHERE codigo = ?", 4, LETRAS_SALA);
    this.sql.exec(
      "INSERT INTO salas (codigo, estado, clave_huella, evento, duracion_min, creada) "
        + "VALUES (?, 'inscripcion', ?, ?, ?, ?)",
      codigo, huella, R.limpiar(contexto.datos.evento, 80) || "Sala de verificación", banco.duracion_min,
      contexto.ahora,
    );
    return { sala: codigo, clave: `${codigo}-${secreto}` };
  }

  /** F2: agregar un colegio provisional a la sala, sin repetir nombres normalizados (BR2.3). */
  agregar_colegio(contexto) {
    const { datos, sala } = contexto;
    if (datos.accion !== "provisional") throw new ErrorAPI("Esa acción llega en otra versión.");
    const nombre = R.limpiar(datos.nombre, 80);
    if (Array.from(nombre).length < 3) throw new ErrorAPI("Escribe el nombre del colegio (al menos 3 letras).");
    const normalizado = R.normalizar_nombre(nombre);
    const consulta = "SELECT id_colegio, nombre, provisional FROM colegios WHERE nombre_normalizado = ?";
    const existente = this.una(consulta, normalizado);
    if (existente) {
      const colegio = { ...existente, provisional: !!existente.provisional };
      throw new ErrorAPI("Ese colegio ya existe.", 400, { existente: colegio });
    }
    const id_colegio = "c" + this.codigo_libre("SELECT 1 FROM colegios WHERE id_colegio = 'c' || ?", 8, R.ALFABETO);
    this.ctx.storage.transactionSync(() => {
      this.sql.exec(
        "INSERT INTO colegios (id_colegio, nombre, nombre_normalizado, provisional, creado) VALUES (?, ?, ?, 1, ?)",
        id_colegio, nombre, normalizado, contexto.ahora,
      );
      this.sql.exec("INSERT INTO sala_colegios (id_sala, id_colegio) VALUES (?, ?)", sala.id_sala, id_colegio);
    });
    return { ok: true, id_colegio };
  }

  /** F3: cambiar el estado de la sala; en el corte solo inscripción → abierto (BR2.2). */
  cambiar_estado(contexto) {
    const { datos, sala } = contexto;
    if (!R.ESTADOS_SALA.includes(datos.estado)) throw new ErrorAPI("Estado no válido.");
    if (datos.estado === sala.estado) return { ok: true };
    if (!R.transicion_permitida(sala.estado, datos.estado)) {
      throw new ErrorAPI("Ese cambio de estado llega en otra versión.");
    }
    this.sql.exec(
      "UPDATE salas SET estado = ?, abierta = CASE WHEN ? = 'abierto' THEN COALESCE(abierta, ?) ELSE abierta END "
        + "WHERE id_sala = ?",
      datos.estado, datos.estado, contexto.ahora, sala.id_sala,
    );
    console.log(`Cambio de estado de una sala: ${sala.estado} -> ${datos.estado}`);
    return { ok: true };
  }
}
