# Especificación funcional — U3 `u3-local-fugas`

Qué cambia en `2_Aplicacion_Reto/servidor.py` para cerrar las dos fugas de FR6, y nada más. Los datos
están en `entities.md`, las reglas en `rules.md` y las decisiones en `../decisions.md` (ADR-L1 a ADR-L3).
Sale de `unit-of-work.md` (U3), `requirements.md` (FR6.1, FR6.2, FR6.3), ADR-006 y el código actual de
`servidor.py`. Este alcance no tiene historias de usuario (`stories.md`).

## Qué demuestra

Contra la versión local, la parte de fugas de la prueba común (U2) pasa: `fuga_verdad_cerrado`,
`fuga_ids_opacos`, `fuga_orden_banco`, `csv_ids_del_banco` y `experimento_completo_resultados`; y
`python3 pruebas/simulacro.py 40` sigue en «TODO BIEN» sin tocarlo (B7 de `bolt-plan.md`).

## Flujos

### F1. Armar el examen con ids opacos (BR2.1)

1. `GET /api/estado` con token; `vencer_tiempos()` y `estado_participante(p)` como hoy.
2. `examen_publico(p, respondidas)` llama a `version_publica(p, q)` por pregunta visible, que arma `pub`
   como hoy (lista blanca de claves, orden de `rng_para`, cuidado de «ordenar», orden común de la misión
   1).
3. Nuevo último paso: `opacar_salida(pub, p["semilla"], q["id"])` reemplaza los ids de `opciones`,
   `items`, `publicaciones`, `partes` y `partes[].opciones` con `opacos_de` y los ámbitos de BR1.3.
4. `respuestas[qid].respuesta` sale por `opacar_respuesta` (BR2.2); en «resultados»,
   `revision[qid].respuesta` también.

### F2. Responder con ids opacos (BR3.1, BR3.2)

1. `POST /api/responder` con `pregunta` y `respuesta`; las comprobaciones de estado, pregunta,
   visibilidad, repetida y `requiere` siguen iguales y en el mismo orden.
2. `var, cuerpo = resolver(p, q)` como hoy; nuevo: `r = traducir_entrada(d.get("respuesta"),
   p["semilla"], cuerpo)` traduce los ids opacos conocidos al id del banco y deja igual lo demás.
3. `validar_respuesta(cuerpo, r)`, `fraccion`, `INSERT INTO respuestas` y `recalcular_puntos` como hoy,
   con ids del banco. La respuesta HTTP no cambia (`{ok, puntos, max, fraccion}` con `retro`).

### F3. Tablero en «cerrado» (BR4.1)

`GET /api/publico`: en «cerrado», `datos["experimento"] = sin_veredicto(experimento())`, que devuelve
`{"n", "listo"}`; en «resultados», `experimento()` completo; en «inscripción» y «abierto», sin la clave,
como hoy. `tablero.html` muestra lo mismo que hoy en los cuatro estados.

### F4. Lo que no cambia

`registrar`, `entrar`, `comenzar`, `finalizar`, `vencer_tiempos`, `clasificacion`, `experimento`,
`resumen_admin`, los dos CSV, `reiniciar`, `cambiar_estado`, las rutas, las pantallas de `web/` y el
esquema de la base.

## Funciones nuevas (todas puras: reciben datos, devuelven datos)

| Función | Entrada | Salida | Regla | Justificación (`python-code.md`) |
|---|---|---|---|---|
| `opaco_de(semilla, ambito, id_banco)` | textos | id opaco | BR1.1 | reutilizada en `opacos_de` y probada en `test_servidor.TestIdsOpacos` |
| `opacos_de(semilla, ambito, ids)` | textos | mapa id del banco → opaco | BR1.2 | reutilizada en `opacar_salida`, `opacar_respuesta`, `traducir_entrada` |
| `opacar_salida(pub, semilla, pregunta_id)` | pregunta pública | pregunta pública con ids opacos | BR2.1, BR1.3 | paso aislado, probado en `test_servidor.TestIdsOpacos.test_opacar_salida_cambia_solo_ids` |
| `opacar_respuesta(respuesta, semilla, cuerpo)` | respuesta con ids del banco | respuesta con ids opacos | BR2.2, BR2.3 | reutilizada en `estado_participante` (respuestas y revision) |
| `traducir_entrada(respuesta, semilla, cuerpo)` | respuesta con ids opacos o del banco | respuesta con ids del banco | BR3.1, BR2.3 | paso aislado, probado en `test_servidor.TestIdsOpacos.test_traducir_entrada_ida_y_vuelta` |
| `sin_veredicto(exp)` | experimento | `{n, listo}` | BR4.1 | paso aislado, probado en `test_servidor.TestVeredictoCerrado` |

`opacar_respuesta` y `traducir_entrada` comparten una tabla `tipo → (lista del cuerpo, cómo recorrer)`
para cumplir BR2.3 sin repetir los `if`, con complejidad ciclomática ≤ 10 por función (ruff C901).

## Pruebas (ADR-L3)

`2_Aplicacion_Reto/pruebas/test_servidor.py`, con `unittest`, preguntas inventadas y sin respuestas del
banco:

| Clase | Casos |
|---|---|
| `TestIdsOpacos` | forma `^o[a-z2-7]{11}$`; mismo valor con la misma semilla; distinto con otra semilla y con otro ámbito; choque forzado produce 16 caracteres para todo el grupo; `opacar_salida` cambia solo ids y mantiene el orden y las categorías; ida y vuelta de `opcion`, `multiple`, `clasificar`, `ordenar` y `construir`; un id inventado y un id del banco pasan igual por `traducir_entrada`; `numero` y `texto` no cambian |
| `TestVeredictoCerrado` | `sin_veredicto` deja solo `n` y `listo`; con `n < 2` devuelve lo mismo que entra; no muta el experimento original |

Aceptación: `python3 pruebas/simulacro.py 40` en «TODO BIEN» y la prueba común en modo local con la parte
base y la de fugas en «TODO BIEN» (`despliegues/prueba_comun/src/prueba.py --modo local --opcion local`).

## Estados

Sin cambios: los cuatro estados de la sala y los cinco del participante son los de hoy (FR1.1, FR1.2).
Solo cambia lo que `/api/publico` entrega en «cerrado» (F3).

## Fuera de esta unidad

Cualquier otro cambio en `2_Aplicacion_Reto/` (FR12.1): salas, catálogo, paquete, refactor, transiciones
de FR7.4 y el `?clave=` en la URL (sigue aceptado en local; solo la nube lo rechaza).
