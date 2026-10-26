/**
 * Pruebas de las reglas puras de la opción Cloudflare Workers (src/reglas.js), con node:test de Node 24
 * (ADR-W2). Desde la raíz del repositorio:
 *   node --test --experimental-test-coverage despliegues/cloudflare/pruebas/reglas.test.js
 *
 * Las pruebas de calificación usan un banco inventado aquí (banco_de_prueba). Del banco real
 * (src/banco.json, copiado por herramientas/copiar.sh) solo se revisan la estructura, los 1.000 puntos,
 * la huella y que el examen público no traiga claves secretas: ninguna respuesta del banco se copia aquí.
 */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { describe, test } from "node:test";

import {
  aplicar_bloqueos, armar_misiones, bono, cerrar_intento, examen_publico, fraccion, hora_de_entrega,
  huella_banco, iguales_en_tiempo_constante, limpiar, normalizar_codigo, normalizar_nombre, opaco_de,
  opacos_de, resolver, transicion_permitida, traducir_opaco, validar_banco, validar_respuesta,
  visible_para,
} from "../src/reglas.js";

const leer_json = (ruta) => JSON.parse(readFileSync(new URL(ruta, import.meta.url), "utf8"));
const BANCO_REAL = leer_json("../src/banco.json");
const HUELLA_REAL = leer_json("../src/banco_huella.json");
const SECRETAS = ["respuesta", "explicacion", "tolerancia", "solo_grupo", "variantes"];
const FORMA_OPACA = /^o[a-z2-7]{11}([a-z2-7]{5})?$/;

/**
 * Banco mínimo inventado: 1.000 puntos, un caso con dossier, una pregunta solo para el grupo B, una con
 * variantes y una de ordenar.
 * @returns {any}
 */
function banco_de_prueba() {
  const opciones = [{ id: "a", texto: "Uno" }, { id: "b", texto: "Dos" }, { id: "c", texto: "Tres" }];
  return {
    titulo: "Banco de prueba", version: "prueba", duracion_min: 90, bono_tiempo_max: 20, puntos_totales: 1000,
    misiones: [
      {
        id: "c1",
        titulo: "Caso inventado",
        dossier: { titulo: "Evidencia", revelar_tras: "c1_hip", graficos: [{}, {}] },
        preguntas: [
          { id: "c1_hip", tipo: "opcion", enunciado: "¿Qué crees?", puntos: 0, opciones },
          {
            id: "c1_q", tipo: "opcion", enunciado: "¿Cuál?", puntos: 500, opciones, respuesta: "b", explicacion: "Sí.",
          },
          {
            id: "c1_solo_b", tipo: "opcion", enunciado: "Solo B", puntos: 100, opciones, respuesta: "a",
            solo_grupo: "B",
          },
        ],
      },
      {
        id: "c2",
        titulo: "Otro caso",
        preguntas: [
          {
            id: "c2_var", tipo: "clasificar", enunciado: "Clasifica", puntos: 200,
            categorias: [{ id: "V", texto: "Sí" }],
            variantes: [1, 2, 3].map((n) => ({
              items: [{ id: `x${n}`, texto: `Ítem ${n}` }], respuesta: { [`x${n}`]: "V" }, explicacion: "E",
            })),
          },
          {
            id: "c2_orden", tipo: "ordenar", enunciado: "Ordena", puntos: 100, respuesta: ["i1", "i2"],
            items: [{ id: "i1", texto: "Primero" }, { id: "i2", texto: "Segundo" }],
          },
          {
            id: "c2_estimar", tipo: "estimar", enunciado: "Estima", puntos: 100, min: 0, max: 10,
            respuesta: 5, tolerancia: 2,
          },
        ],
      },
    ],
  };
}

/**
 * @param {unknown} valor
 * @returns {string[]} todas las claves de objetos, a cualquier profundidad.
 */
function claves_de(valor) {
  if (valor === null || typeof valor !== "object") return [];
  const propias = Array.isArray(valor) ? [] : Object.keys(valor);
  return [...propias, ...Object.values(valor).flatMap(claves_de)];
}

/**
 * @param {any[]} misiones
 * @returns {string[]} ids de opciones, ítems, publicaciones y partes que ve el navegador.
 */
function ids_publicos(misiones) {
  return misiones.flatMap((m) => m.preguntas).flatMap((q) => [
    ...(q.opciones || []), ...(q.items || []), ...(q.publicaciones || []), ...(q.partes || []),
    ...(q.partes || []).flatMap((p) => p.opciones),
  ]).map((o) => o.id);
}

describe("banco", () => {
  test("el banco real tiene la estructura esperada y suma exactamente 1.000 puntos", () => {
    const suma = BANCO_REAL.misiones.flatMap((m) => m.preguntas).reduce((s, q) => s + q.puntos, 0);
    assert.deepEqual(validar_banco(BANCO_REAL), []);
    assert.equal(suma, 1000);
  });

  test("la huella del banco copiado coincide con la que guardó copiar.sh", async () => {
    assert.equal(await huella_banco(BANCO_REAL), HUELLA_REAL.sha256);
  });

  test("validar_banco rechaza un banco que no suma 1.000 puntos", () => {
    const banco = banco_de_prueba();
    banco.misiones[0].preguntas[1].puntos = 499;
    assert.deepEqual(validar_banco(banco), ["Las preguntas suman 999, no 1.000."]);
  });

  test("validar_banco rechaza ids repetidos, falta de versión y un banco vacío", () => {
    const banco = banco_de_prueba();
    banco.misiones[1].preguntas[0].id = "c1_q";
    delete banco.version;
    assert.deepEqual(validar_banco(banco), ["El banco no tiene versión.", "Pregunta repetida: c1_q."]);
    assert.deepEqual(validar_banco({ misiones: [] }), ["El banco no tiene misiones."]);
  });

  test("examen_publico no trae ninguna clave secreta y todos sus ids son opacos", async () => {
    const misiones = await examen_publico(banco_de_prueba(), "semilla01", "B", new Set(["c1_hip"]));
    const claves = new Set(claves_de(misiones));
    assert.deepEqual(SECRETAS.filter((k) => claves.has(k)), []);
    assert.ok(ids_publicos(misiones).every((id) => FORMA_OPACA.test(id)));
  });

  test("el examen público del banco real tampoco trae claves secretas ni ids del banco", async () => {
    const misiones = await examen_publico(BANCO_REAL, "0123456789abcdef", "B", new Set());
    const claves = new Set(claves_de(misiones));
    assert.deepEqual(SECRETAS.filter((k) => claves.has(k)), []);
    assert.ok(ids_publicos(misiones).every((id) => FORMA_OPACA.test(id)));
  });

  test("los ids opacos dependen de la semilla y siempre dan lo mismo con la misma semilla", async () => {
    const a = await opaco_de("semilla01", "c1_q", "b");
    assert.equal(a, await opaco_de("semilla01", "c1_q", "b"));
    assert.notEqual(a, await opaco_de("semilla02", "c1_q", "b"));
    assert.match(a, FORMA_OPACA);
  });

  test("traducir_opaco devuelve el id del banco y null si el id no corresponde", async () => {
    const ids = ["a", "b", "c"];
    const opacos = await opacos_de("semilla01", "c1_q", ids);
    assert.equal(await traducir_opaco("semilla01", "c1_q", ids, opacos.get("c")), "c");
    assert.equal(await traducir_opaco("semilla01", "c1_q", ids, "b"), null);
    assert.equal(await traducir_opaco("semilla02", "c1_q", ids, opacos.get("c")), null);
  });

  test("el dossier sigue bloqueado hasta responder la pregunta que lo revela", async () => {
    const banco = banco_de_prueba();
    const misiones = await armar_misiones(banco, "semilla01", "A");
    const bloqueado = { titulo: "Evidencia", bloqueado: true, n: 2 };
    assert.deepEqual(aplicar_bloqueos(banco, misiones, new Set())[0].dossier, bloqueado);
    assert.equal(aplicar_bloqueos(banco, misiones, new Set(["c1_hip"]))[0].dossier.graficos.length, 2);
  });

  test("la pregunta solo_grupo B no la ve el grupo A", async () => {
    const ids = (misiones) => misiones[0].preguntas.map((q) => q.id);
    const para = async (grupo) => ids(await examen_publico(banco_de_prueba(), "s", grupo, new Set()));
    assert.deepEqual(await para("A"), ["c1_hip", "c1_q"]);
    assert.deepEqual(await para("B"), ["c1_hip", "c1_q", "c1_solo_b"]);
    assert.equal(visible_para({ solo_grupo: "B" }, "A"), false);
  });

  test("resolver elige una variante fija por semilla y quita la lista de variantes", async () => {
    const pregunta = banco_de_prueba().misiones[1].preguntas[0];
    const uno = await resolver("semilla01", pregunta);
    assert.deepEqual(await resolver("semilla01", pregunta), uno);
    assert.deepEqual(Object.keys(uno.cuerpo.respuesta), [`x${uno.variante + 1}`]);
    assert.equal("variantes" in uno.cuerpo, false);
  });

  test("«ordenar» nunca se muestra en el orden de la respuesta", async () => {
    const banco = banco_de_prueba();
    const semillas = Array.from({ length: 12 }, (_, i) => `semilla${i}`);
    const ordenes = await Promise.all(semillas.map(async (s) => {
      const misiones = await armar_misiones(banco, s, "A");
      const opacos = await opacos_de(s, "c2_orden", ["i1", "i2"]);
      const mostrado = misiones[1].preguntas[1].items.map((it) => it.id).join("|");
      return mostrado === [opacos.get("i1"), opacos.get("i2")].join("|");
    }));
    assert.deepEqual(ordenes.filter(Boolean), []);
  });
});

describe("calificacion", () => {
  const pregunta = banco_de_prueba().misiones[0].preguntas[1];

  test("una opción correcta da fracción 1 y una incorrecta da 0", () => {
    assert.equal(fraccion(pregunta, "b"), 1);
    assert.equal(fraccion(pregunta, "a"), 0);
  });

  test("una pregunta sin puntos da 0 aunque se elija cualquier opción", () => {
    assert.equal(fraccion(banco_de_prueba().misiones[0].preguntas[0], "a"), 0);
  });

  test("validar_respuesta acepta un id de la pregunta y rechaza otro id, otro tipo de dato y otro tipo", () => {
    assert.deepEqual(validar_respuesta(pregunta, "c"), { valor: "c" });
    assert.deepEqual(validar_respuesta(pregunta, "z"), { error: "formato" });
    assert.deepEqual(validar_respuesta(pregunta, null), { error: "formato" });
    assert.deepEqual(validar_respuesta({ tipo: "estimar" }, 5), { error: "tipo" });
  });

  test("calificar un tipo que el corte no trae es un error de programación", () => {
    assert.throws(() => fraccion({ tipo: "estimar", puntos: 100 }, 5), RangeError);
  });

  test("el bono es 20 con todo bien al instante, 0 al final del tiempo o sin puntos", () => {
    assert.equal(bono(1000, 0, 5400), 20);
    assert.equal(bono(1000, 5400, 5400), 0);
    assert.equal(bono(0, 0, 5400), 0);
    assert.equal(bono(500, 2700, 5400), 5);
  });

  test("cerrar_intento mide el bono con la última respuesta y lo topa en la duración", () => {
    const antes = cerrar_intento({ ahora: 1000 + 600, inicio: 1000, duracion: 5400, ultima: 1000 + 270, puntos: 500 });
    assert.deepEqual(antes, { fin: 1600, tiempo_usado: 600, tiempo_respuestas: 270, bono: 9.5, total: 509.5 });
    const vencido = cerrar_intento({ ahora: 9000, inicio: 1000, duracion: 5400, ultima: null, puntos: 0 });
    assert.deepEqual(vencido, { fin: 6400, tiempo_usado: 5400, tiempo_respuestas: 5400, bono: 0, total: 0 });
  });
});

describe("ciclo", () => {
  test("en el corte la sala solo pasa de inscripción a abierto", () => {
    assert.equal(transicion_permitida("inscripcion", "abierto"), true);
    assert.equal(transicion_permitida("abierto", "cerrado"), false);
    assert.equal(transicion_permitida("inscripcion", "resultados"), false);
    assert.equal(transicion_permitida("desconocido", "abierto"), false);
  });

  test("hora_de_entrega: nada antes del final, por tiempo al vencer y por cierre si la sala cerró antes", () => {
    assert.equal(hora_de_entrega(1100, 1000, 300, null), null);
    assert.deepEqual(hora_de_entrega(1300, 1000, 300, null), { hora: 1300, motivo: "tiempo" });
    assert.deepEqual(hora_de_entrega(9999, 1000, 300, null), { hora: 1300, motivo: "tiempo" });
    assert.deepEqual(hora_de_entrega(1250, 1000, 300, 1200), { hora: 1200, motivo: "cierre" });
  });

  test("limpiar junta espacios, quita invisibles, pasa a NFC y recorta en caracteres", () => {
    assert.equal(limpiar("  Ana\t\n  María  "), "Ana María");
    assert.equal(limpiar("Jo​sé"), "José");
    assert.equal(limpiar("José").length, 4);
    assert.equal(limpiar("😀😀😀", 2), "😀😀");
    assert.equal(limpiar(null), "");
  });

  test("normalizar_nombre iguala mayúsculas y tildes; normalizar_codigo deja el código en mayúsculas", () => {
    assert.equal(normalizar_nombre("Colegio  San JOSÉ"), normalizar_nombre("colegio san jose"));
    assert.notEqual(normalizar_nombre("Colegio San José"), normalizar_nombre("Colegio San Juan"));
    assert.equal(normalizar_codigo("  kqmt "), "KQMT");
    assert.equal(normalizar_codigo("abcdefghijklmn"), "ABCDEFGHIJ");
  });

  test("iguales_en_tiempo_constante compara bytes y rechaza largos distintos", () => {
    const a = new Uint8Array([1, 2, 3]);
    assert.equal(iguales_en_tiempo_constante(a, new Uint8Array([1, 2, 3])), true);
    assert.equal(iguales_en_tiempo_constante(a, new Uint8Array([1, 2, 4])), false);
    assert.equal(iguales_en_tiempo_constante(a, new Uint8Array([1, 2])), false);
  });
});
