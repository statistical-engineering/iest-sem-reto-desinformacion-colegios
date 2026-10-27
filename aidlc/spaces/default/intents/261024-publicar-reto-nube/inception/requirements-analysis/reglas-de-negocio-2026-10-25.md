# Reglas de negocio — Reto «Detectives de la desinformación»

Copia textual del documento que pegó el humano el 2026-10-25 al pedir el reajuste a una sola sala. Es la
fuente de la revisión de `requirements.md` del mismo día. Junto con el documento dijo: «lo que ya hemos ido
realizando, es que tocó hacer este ajuste. pq esto lo controla un solo profesor en un solo panel. no con
varios profesores con varios paneles. es solo una sala.» y «sí, hazlo. pero continua mediante un /loop hasta
terminar todo pero lo referente solo a cloudflare listo ?».

---

Semillero de investigación — Desinformación en redes sociales (Colombia), 2026.

## 1. Qué es

- Reto interactivo de 90 minutos para estudiantes de 9.° a 11.°.
- Usa datos reales: 2.980 chequeos de Colombiacheck (2020–2026), DANE (ENTIC 2024), Banco Mundial y el estudio de Arechar et al. (2023, Nature Human Behaviour), hecho en 16 países con 34.286 personas.
- Calificación automática, sin empates y con podio para el 1.°, 2.° y 3.° puesto, el podio es general, es decir, entre el total de grupos de todos los colegios se calcula el podio

## 2. Actores y requisitos

- Docente: un computador con Python 3.9 o superior que hace de servidor. Controla el reto desde el panel docente (/admin, con clave) y proyecta el tablero (/tablero).
- Estudiantes: entran desde cualquier navegador en la misma wifi, entran por equipos, 1 computador para cada equipo

## 3. Flujo de la actividad

Estados del reto: Inscripción → Abierto → Cerrado → Resultados. Cada cambio pide confirmación.

| Tiempo | Qué pasa |
|---|---|
| 0:00–0:10 | El docente inicia el reto. Los estudiantes se inscriben con nombre, colegio, grado y código de sala, y reciben un código de detective de 5 letras que deben anotar. |
| 0:10–0:15 | Lectura del reglamento. El docente pulsa «Abrir el reto». |
| 0:15–1:45 | Desarrollo del reto (90 minutos). |
| 1:45–1:50 | El docente cierra el reto (se entrega lo pendiente) y revisa las salidas de pestaña. |
| 1:50–2:00 | Publicación de resultados: podio, diapositivas del experimento, discusión y premiación. |

Antes del día se ejecuta PROBAR_ANTES_DEL_RETO, que simula 40 estudiantes y debe terminar con «TODO BIEN».

## 4. Reglas de juego

1. Reloj global: Empieza cuando el docente abre el reto, no se detiene si se cierra la página y al vencer entrega automáticamente. El reloj va para cada colegio según cuando ellos hayan estado listos para empezar el reto, es decir los relojes son independientes para cada colegio, lo ideal sería que todos empezaran al tiempo, pero en caso de que no, se garantiza que cada colegio tenga sus 90 min sin importar si empezaron 5 o 10 min mas tarde de lo esperado
2. Reconexión: el estudiante entra con su código de detective y continúa donde iba. Si el servidor se apaga, todo queda guardado.
3. 10 expedientes, 1.000 puntos, en cualquier orden.
4. Cada pregunta se responde una sola vez; tras confirmar queda bloqueada.
5. El Exp. 01 tiene dos partes sobre las mismas 10 afirmaciones: «¿Lo compartirías?» no da puntos (se responde con honestidad porque es el experimento de la clase) y «¿Es verdadera?» vale los 120 puntos del expediente. Tampoco dan puntos las hipótesis y apuestas (Casos 1 y 5) ni los informes escritos.
6. Las salidas de pestaña quedan registradas y sirven como alerta para conversar, no como prueba de trampa.
7. El docente decide sobre buscador (recomendado: no), calculadora (sí) y papel (recomendado).

## 5. Expedientes y puntos

| Exp. | Contenido | Puntos |
|---|---|---|
| 01 | ¿Lo compartirías? — 10 afirmaciones reales. Los 120 pts son de la parte «¿Es verdadera?»; la parte «¿Lo compartirías?» no puntúa | 120 |
| 02 | Detectives de chequeos (4 versiones equivalentes) | 140 |
| 03 | Caso 1 · Elecciones (conteo vs. proporción) | 90 |
| 04 | Caso 2 · Simulador de mezclas (promedio ponderado) | 95 |
| 05 | Caso 3 · La era de la IA (año incompleto) | 90 |
| 06 | Caso 4 · Exposición (cruzar 4 gráficos del DANE) | 90 |
| 07 | Caso 5 · IA y falsedad (probabilidad condicional) | 95 |
| 08 | Caso 6 · Ranking (márgenes de error) | 90 |
| 09 | Caso 7 · Taller del gráfico | 90 |
| 10 | Lo que dice la ciencia (lectura) | 100 |
|  | Total: 37 preguntas con puntos | 1.000 |

Experimento oculto: a la mitad de la clase, elegida al azar, se le muestra un «recordatorio de exactitud» antes del Exp. 01. Al final el tablero compara ambos grupos con los resultados del estudio.

## 6. Calificación por tipo de pregunta

- Opción única: todo o nada.
- Marcar varias: cada correcta suma y cada incorrecta resta (mínimo 0).
- Clasificar, evaluar afirmaciones y comparar intervalos: proporcional a los aciertos.
- Armar la conclusión: 1/3 por pieza (afirmación, evidencia y limitación).
- Ordenar: proporcional a los pares en orden correcto.
- Deslizador: más cerca, más puntos; 0 si supera la tolerancia.
- Número: completo dentro de la tolerancia; la mitad si está hasta 3 veces la tolerancia.
- Las claves se verifican contra los datos al construir el banco; si una deja de cumplirse, el banco no se genera.

## 7. Bono, desempate y nota

- Bono de tiempo (máx. 20 pts) = 20 × (puntos/1000) × (1 − minuto de la última respuesta/90). Se mide con la última respuesta, no con «Entregar».
- Desempate: mayor total → más puntos en preguntas → última respuesta más temprana → entrega más temprana → inscripción más temprana.
- Nota de 1,0 a 5,0 = 1 + 4 × puntos/1000 (el bono no cuenta).
- Clasificación general y por grado (premios para 9.°, 10.° y 11.°).

## 8. Controles contra la copia

- Las respuestas correctas nunca llegan al navegador.
- Se barajan por estudiante las opciones, afirmaciones y piezas de conclusión.
- Antes de premiar se revisan salidas de pestaña y tiempos imposibles en el CSV detallado.

## 9. Acciones del docente

- Entregar (forzar), Anular / Reactivar participantes y Eliminar inscripciones que no empezaron.
- Exportar resultados y respuestas detalladas en CSV.
- «Reiniciar todo» exige escribir BORRAR y guarda antes una copia automática.
- Premiación: cerrar → revisar primeros puestos → publicar resultados → llenar el ACTA_DE_PREMIACION.
- Por defecto el estudiante ve si acertó (sin explicación); el modo sorpresa oculta la clasificación hasta publicar.
