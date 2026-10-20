# Guía docente — Reto «Detectives de la desinformación»

Reto de **90 minutos** para estudiantes de **9.° a 11.°**, con calificación automática, puntajes
sin empates y podio para premiar el 1.°, 2.° y 3.° puesto.

---

## 1. De qué se trata

El centro del reto es la **desinformación**. Los estudiantes trabajan con:

- **2.980 chequeos reales de Colombiacheck** (2020–2026): afirmaciones que circularon en redes y
  el veredicto del verificador.
- **Datos oficiales del DANE (ENTIC 2024) y del Banco Mundial** sobre uso de internet y redes,
  como contexto: ¿por dónde nos llega la desinformación y por qué se difunde?
- **El estudio de Arechar et al. (2023), *Nature Human Behaviour***: un experimento en 16 países con
  34.286 personas que mostró que la gente comparte titulares falsos que reconocería como
  falsos si se detuviera a pensar, y que un simple «recordatorio de exactitud» ayuda.

Estructura: **10 expedientes** = **3 de desinformación y lectura** (34 % del puntaje) + **7 casos
estadísticos** (64 %).

1. **La clase repite ese experimento sin saberlo** (Exp. 01). Los estudiantes deciden primero si
   compartirían 10 afirmaciones reales (sin puntos) y después si son verdaderas (con puntos). A
   la mitad, elegida al azar, se le muestra antes un recordatorio de exactitud. Al final, el
   tablero proyecta lo que hizo la clase y lo compara con el estudio.
2. **Laboratorio estadístico** (Exp. 03–09). Siete casos, cada uno con un *encargo* (una situación
   real: un concejal, un influencer, un periódico, una fundación) y **una mecánica distinta**, para
   que no sea siempre «mirar un gráfico y responder». Todo con datos reales de Colombiacheck y del DANE.

### Los siete casos estadísticos

| Exp. | Caso | Mecánica | Idea estadística |
|---|---|---|---|
| 03 | 1 · ¿Las elecciones disparan la desinformación? | **Hipótesis primero**: la evidencia está sellada hasta que el estudiante anota qué cree | Conteo vs. proporción: el volumen casi no cambia en elecciones (+15 %), la parte electoral se multiplica |
| 04 | 2 · ¿Más falso… o distinto? | **Simulador de mezclas**: un deslizador muestra cómo se mueve el promedio total | Promedio ponderado y efecto de composición |
| 05 | 3 · La era de la IA | **Proyección** de un año incompleto | Año incompleto, conteo vs. proporción, «ausencia de evidencia ≠ evidencia de ausencia» |
| 06 | 4 · ¿Quién está más expuesto? | Cruzar 4 gráficos y armar la conclusión | Correlación débil (r = 0,17) y qué NO se concluye con datos de uso |
| 07 | 5 · ¿Falso porque es IA, o IA porque es falso? | **Apuesta primero** + tabla de doble entrada | Probabilidad condicional: P(Falso \| IA) = 98 % pero P(IA \| Falso) = 5 % (falacia de la probabilidad inversa) |
| 08 | 6 · El ranking que no era | Comparar **intervalos de confianza**; combinar dos gráficos para ordenar | Margen de error, tamaño de muestra, porcentaje vs. cantidad |
| 09 | 7 · El taller del gráfico | Taller: cada pregunta trae su propio gráfico | Elegir el gráfico adecuado, eje cortado, *cherry picking*, media vs. mediana (mediana = 1, promedio = 11,4) |

Las preguntas siguen siendo accesibles para 9.° a 11.°: todo se resuelve con porcentajes,
divisiones, lectura de tablas y razonamiento, con un glosario a la vista en cada caso.

### Competencias que trabaja

| Competencia | Dónde |
|---|---|
| Distinguir verdadero de falso y reconocer el impulso de compartir | Exp. 01 |
| Leer como verificador: tácticas de engaño (IA, fuera de contexto, estafas, citas falsas, alarmas) | Exp. 02 |
| Formular hipótesis y contrastarlas con evidencia | Casos 1 y 5 |
| Promedios ponderados, composición, proyecciones | Casos 2, 3 y 4 |
| Probabilidad condicional y tablas de doble entrada | Caso 5 |
| Incertidumbre de las encuestas, intervalos de confianza | Caso 6 |
| Elegir y criticar gráficos, medidas de tendencia central | Caso 7 |
| Distinguir lo respaldado, lo contradicho y lo que no se puede saber; construir conclusiones con evidencia y limitaciones | Casos 1–5 |
| Comprensión de un artículo científico, diseño experimental (asignación al azar) | Exp. 10 |

---

## 2. Qué se necesita

| Elemento | Detalle |
|---|---|
| **1 computador para el docente** (servidor) | Windows, con **Python 3.9 o superior** (gratis en python.org; al instalar marcar «Add python.exe to PATH»). No hay que instalar nada más. |
| **Red** | El computador del docente y los dispositivos de los estudiantes en la **misma red wifi**. **No se necesita internet**: todo funciona en la red local. |
| **Estudiantes** | Celular, tableta o computador con navegador (Chrome, Edge, Firefox, Safari). Individual o en equipos. |
| **Proyector** | Para el tablero (inscripción, cuenta regresiva, podio y experimento). |
| Capacidad | Probado con 60 estudiantes respondiendo a la vez (4.320 peticiones en 10 segundos, sin errores). Un salón o un auditorio pequeño caben de sobra. |

> Si la red del colegio aísla los dispositivos entre sí (pasa en muchas redes institucionales:
> los celulares no «ven» al computador), usa un **router propio** o el **punto de acceso
> (hotspot) del computador o de un celular**. El tráfico es local y casi no consume datos.

---

## 3. Antes del día del reto (30 minutos, una sola vez)

1. Copia la carpeta `Reto_Desinformacion_Colegios` al computador del docente.
2. Doble clic en **`2_Aplicacion_Reto/PROBAR_ANTES_DEL_RETO.bat`**. Hace un simulacro con 40
   estudiantes ficticios (no toca datos reales) y debe terminar con **«TODO BIEN: el reto está listo»**.
3. Doble clic en **`2_Aplicacion_Reto/INICIAR_RETO.bat`**. Se abre una ventana negra con:
   - la dirección para estudiantes (por ejemplo `http://192.168.0.102:8000`);
   - el **código de sala** (4 letras);
   - la dirección del **tablero** y del **panel docente**, y la **clave docente**.

   Si Windows pregunta por el **firewall**, pulsa **«Permitir acceso»** (redes privadas).
4. Con un celular conectado a la misma wifi, abre la dirección de estudiantes y haz una
   inscripción de prueba. Luego, en el panel docente, bórrala (botón «Eliminar»).
5. Configura el computador para que **no se suspenda** durante la sesión.
6. Decide y anuncia las reglas del día (sección 5).

---

## 4. Agenda sugerida (bloque de 2 horas)

| Tiempo | Actividad |
|---|---|
| 0:00 – 0:10 | Inicias el servidor, proyectas el tablero (`/tablero`). Los estudiantes se inscriben con el código de sala. **Que anoten su código de detective.** |
| 0:10 – 0:15 | Lees el reglamento (hoja aparte). En el panel docente pulsas **«Abrir el reto»** y pides que todos pulsen **«Comenzar»** a la vez. |
| 0:15 – 1:45 | **Reto: 90 minutos.** Reloj global: arranca cuando pulsas «Abrir el reto» y termina a la misma hora para todos (se puede cambiar a reloj individual en Configuración, solo antes de abrir). Lo lleva el servidor; al vencerse, el intento se entrega solo. Tú vigilas el panel. |
| 1:45 – 1:50 | **«Cerrar el reto»** en el panel (entrega a quien no lo haya hecho). Revisas las «salidas de pestaña». |
| 1:50 – 2:00 | **«Publicar resultados»**: el tablero muestra el podio y las diapositivas del experimento. Discusión final (sección 8). Premiación. |

---

## 5. Reglas que debes decidir y anunciar antes

| Decisión | Recomendación |
|---|---|
| ¿Individual o en equipos? | Ambos funcionan. En equipo, se inscriben una sola vez con el nombre del equipo y escriben los integrantes. No mezclar equipos e individuales en el mismo premio. |
| ¿Se puede usar buscador / internet? | **Recomendado: no.** El Exp. 01 mide criterio propio, como en el estudio. El panel muestra cuántas veces cada estudiante salió de la pestaña o cambió de aplicación. |
| ¿Calculadora? | Sí: varias preguntas del laboratorio piden divisiones y porcentajes (Casos 1, 2, 3, 5 y 7). La del celular cuenta como «salida de pestaña» si es otra app: mejor calculadora física o permitirlo explícitamente. |
| ¿Papel y lápiz? | Recomendado: ayuda a tomar notas de los gráficos antes de armar las conclusiones. |
| ¿Retroalimentación inmediata? | Activada por defecto: al enviar, el estudiante ve si acertó (sin la explicación). Hace el reto más motivante. Se desactiva en el panel. |
| ¿Modo sorpresa? | Activado por defecto: el tablero no muestra la clasificación hasta publicar resultados. |
| ¿Premio general o por grado? | La app da la clasificación general; en el panel, el filtro por grado muestra el puesto **dentro** de cada grado (para premiar 1.°, 2.° y 3.° de 9.°, de 10.° y de 11.°). |

---

## 6. Cómo se califica (automático)

### Puntos por expediente (total 1.000)

| Expediente | Preguntas | Puntos |
|---|---:|---:|
| 01 · ¿Lo compartirías? *(desinformación)* | 1 (+1 sin puntos; +1 del grupo B) | 120 |
| 02 · Detectives de chequeos *(desinformación)* | 2 | 140 |
| 03 · Caso 1 · ¿Las elecciones disparan la desinformación? | 3 (+ hipótesis sin puntos) | 90 |
| 04 · Caso 2 · ¿Más falso… o distinto? | 4 | 95 |
| 05 · Caso 3 · La era de la IA | 4 | 90 |
| 06 · Caso 4 · ¿Quién está más expuesto? | 3 | 90 |
| 07 · Caso 5 · ¿Falso porque es IA, o IA porque es falso? | 4 (+ apuesta sin puntos) | 95 |
| 08 · Caso 6 · El ranking que no era | 4 | 90 |
| 09 · Caso 7 · El taller del gráfico | 6 (+ informe escrito sin puntos) | 90 |
| 10 · Lo que dice la ciencia *(lectura)* | 6 | 100 |
| **Total** | **37 con puntos** | **1.000** |

Las hipótesis y apuestas (Casos 1 y 5) no dan puntos: sirven para que el estudiante se comprometa
con una idea antes de ver los datos y luego la contraste. El informe escrito del Caso 7 tampoco.

### Tipos de pregunta y crédito parcial

| Tipo | Cómo puntúa |
|---|---|
| Opción única | Todo o nada |
| Marcar varias | Cada correcta suma, cada incorrecta resta (mínimo 0) |
| Clasificar (publicaciones, trampas, veredictos) | Proporcional a los ítems bien clasificados |
| **Evaluar afirmaciones** (respaldada / contradicha / no se puede saber) | Proporcional a las afirmaciones bien evaluadas |
| **Armar la conclusión** (afirmación + evidencia + limitación) | Un tercio por cada pieza correcta |
| **Comparar intervalos** (Caso 6) | Proporcional a las parejas bien juzgadas |
| **Simulador** (Caso 2) | El simulador no se califica: ayuda a encontrar el número que se escribe en la respuesta |
| Ordenar | Proporcional a los pares que quedaron en el orden correcto |
| Estimar con deslizador | Continuo: más cerca = más puntos (0 si se aleja más que la tolerancia) |
| Número | Completo si está dentro de la tolerancia; la mitad si está cerca (hasta 3 veces la tolerancia) |
| **Informe del detective** (Caso 4) | Sin puntos. El texto queda en el CSV de respuestas para que lo leas; sirve para evaluar la argumentación o para la discusión |

Las claves del laboratorio no son opiniones: cada afirmación «respaldada» o «contradicha» se
comprueba contra los datos al construir el banco (si los datos cambian y la clave deja de ser
cierta, el banco no se genera). En las piezas de conclusión, las opciones incorrectas son
igual de largas y elaboradas que la correcta (saltos causales, generalizaciones, leer mal un año
incompleto), para que no se pueda adivinar por la forma.

### Bono de tiempo (hasta 20 puntos)

`bono = 20 × (puntos ÷ 1000) × (1 − minuto de la última respuesta ÷ 90)`

- Es **pequeño a propósito**: una sola pregunta bien respondida vale más que todo el bono. El
  estudio de Nature muestra que pensar despacio ayuda; el reto no debe premiar el apuro.
- Es **proporcional a lo acertado**: responder rápido y mal no da bono.
- Se mide con el momento exacto (al milisegundo) de la **última respuesta**, no con el botón
  «Entregar». Si alguien termina a los 50 minutos y olvida entregar, no pierde el bono.

### Puntajes únicos y desempate

Puntaje total = puntos + bono, con decimales. El orden de la clasificación es **siempre
total** (nunca dos personas en el mismo puesto):

1. mayor **puntaje total**;
2. si empatan: más **puntos** en preguntas;
3. si siguen empatados: quien respondió su **última pregunta antes**;
4. después, quien entregó antes; por último, quien se inscribió antes.

El reglamento de los estudiantes explica estas reglas: conviene leerlas en voz alta antes de empezar.

### Nota en escala colombiana

El panel y el CSV traen una **nota de 1,0 a 5,0** (`1 + 4 × puntos/1000`) por si se quiere usar
como calificación de clase. El bono no entra en la nota.

### Contra la copia

- Las respuestas correctas **nunca llegan al navegador** durante el reto: no se pueden ver en el
  código de la página.
- Cada pregunta se responde **una sola vez**.
- Se baraja por estudiante el orden de las opciones, de las afirmaciones a evaluar y de las
  piezas de cada conclusión; además, el Exp. 02 tiene 4 versiones equivalentes con casos
  distintos. Dos vecinos ven las mismas preguntas en distinto orden.
- El panel cuenta las **salidas de pestaña** (cambiar de pestaña o de aplicación). Úsalo como
  alerta para conversar, no como prueba automática de trampa.

---

## 7. Durante y después del reto: el panel docente

Abre `http://localhost:8000/admin` en el computador del docente (la clave sale en la ventana negra).

- **Control del reto**: Inscripción → Abierto → Cerrado → Resultados. Cada botón pide
  confirmación (doble clic).
- **Tabla en vivo**: progreso, puntos, tiempo restante y salidas de pestaña de cada participante.
  Acciones: *Entregar* (fuerza la entrega), *Anular* (lo saca de la clasificación; reversible con
  *Reactivar*), *Eliminar* (solo inscripciones que no empezaron).
- **Si un estudiante cierra el navegador o se le apaga el celular**: entra de nuevo, pestaña
  «Ya tengo código», con su código de 5 letras. Sigue donde iba; **su reloj nunca se detiene**.
- **Si se apaga el computador del docente**: vuelve a abrir `INICIAR_RETO.bat`. Todo quedó
  guardado; los relojes siguieron corriendo y el tiempo vencido se entrega solo.
- **Exportar**: «Resultados (CSV)» (clasificación, puntos, bono, nota, tiempos, salidas y puntos
  por pregunta) y «Respuestas detalladas (CSV)». Se abren en Excel.
- **Otro grupo después**: «Reiniciar todo el reto» (escribiendo BORRAR). Antes guarda una copia
  automática en `2_Aplicacion_Reto/datos/`.

### Para premiar

1. Cierra el reto.
2. Revisa en la tabla a los primeros puestos: salidas de pestaña altas, respuestas en tiempos
   imposibles (el CSV detallado tiene los segundos de cada respuesta).
3. Publica resultados y descarga el CSV.
4. Llena el **ACTA_DE_PREMIACION.md** (en esta carpeta).

---

## 8. Cierre: discusión de 10 minutos con el tablero

El tablero pasa solo por estas diapositivas (flechas ← → para moverse, espacio para pausar,
F para pantalla completa):

1. **Podio**.
2. **Clasificación** (top 10).
3. **¿Creer es lo mismo que compartir?** — De las publicaciones falsas, cuántas compartiría la
   clase vs. cuántas creyó verdaderas. Pregunta: *¿alguien compartió algo que después marcó como
   falso? ¿Por qué pasa eso?* (Respuesta del estudio: al compartir no pensamos en la exactitud.)
4. **El recordatorio de exactitud** — Grupo con vs. sin recordatorio. Pregunta: *si funciona algo
   tan simple, ¿qué podrían hacer las plataformas? ¿qué puedes hacer tú antes de reenviar?*
   Ojo: con pocos estudiantes la diferencia puede ser azar; es una buena conversación sobre
   tamaño de muestra.
5. **La sabiduría de la multitud** — ¿Acertó más la clase votando junta que el estudiante promedio?

Para discutir el laboratorio (puedes proyectar las figuras de `1_Analisis_de_datos/01_Colombiacheck_chequeos_verificados/figuras/`):

- *Caso 1:* «En elecciones todo se llena de noticias falsas». ¿Qué parte de esa frase respaldan los
  datos y qué parte no? (El verificador cambia de tema, no de volumen; lo que circuló no se midió.)
- *Caso 2:* ¿Dónde más aparece el efecto de composición? (Promedios de notas de un colegio que
  recibe muchos estudiantes nuevos, promedio salarial de un país…)
- *Caso 3:* ¿Por qué «hay menos casos en 2026» y «2026 es el año con más IA» pueden ser ciertas a la vez?
- *Caso 4:* ¿Qué tendríamos que medir para poder decir quién es más vulnerable a la desinformación?
- *Caso 5:* ¿Cuántos apostaron un número alto? ¿Dónde más se confunde P(A | B) con P(B | A)? (Pruebas
  médicas: «si el examen sale positivo, ¿qué tan probable es estar enfermo?».)
- *Caso 6:* ¿Un ranking de colegios por puntaje en una prueba tendría el mismo problema?
- *Caso 7:* ¿Qué número usarían para describir los «likes» típicos de una cuenta: promedio o mediana?
- Lee en voz alta (sin nombres) dos o tres «informes del analista» del CSV de respuestas.

Tres hábitos para llevarse:

- **Pausa y pregunta:** antes de reenviar, «¿esto es cierto?».
- **Lee lateralmente:** busca quién más lo dice y si un verificador ya lo revisó.
- **Desconfía de lo que te emociona demasiado** y de los gráficos sin eje en cero.

---

## 9. Contenido revisado

- Las afirmaciones de los Expedientes 01 y 02 son **reales** (Colombiacheck) y se escogieron temas
  aptos para colegio: salud, ciencia, estafas, fotos y videos fuera de contexto, IA. Se evitó
  contenido violento y de campaña electoral.
- La respuesta «correcta» de las preguntas de veredicto es **la calificación oficial de
  Colombiacheck**; las de datos se calculan directamente de los archivos (nadie las escribió a mano).
- El resumen del estudio de Nature en el Expediente 10 es una paráfrasis propia; la cifra «unas 15
  calificaciones por titular, más del 90 % de acierto» viene de la versión preliminar del artículo.

## 10. Datos personales y ética

- La app solo guarda nombre, colegio, grado, integrantes (si es equipo) y las respuestas.
- Al terminar, exporta lo necesario y usa «Reiniciar» o borra la carpeta `2_Aplicacion_Reto/datos/`.
- El experimento del Expediente 01 es una **demostración educativa**. Si el semillero quiere usar los
  datos para investigación, necesita consentimiento informado de acudientes, asentimiento de
  los estudiantes (son menores de edad) y aval de un comité de ética.
- Limitación conocida: la duración es la misma para todos; no hay tiempo extra individual. Si un
  estudiante lo necesita por una condición particular, puede presentar el reto en otra sesión
  (reiniciando la duración desde el panel antes de abrir).

## 11. Problemas frecuentes

| Síntoma | Solución |
|---|---|
| Los celulares no abren la página | Misma wifi; firewall permitido; red con aislamiento de clientes → usar hotspot/router propio. Prueba la dirección en el navegador del propio computador. |
| «El código de sala no es correcto» | Míralo en el tablero (4 letras, mayúsculas o minúsculas da igual). |
| «Ya hay alguien inscrito con ese nombre…» | Esa persona ya se inscribió: que entre con su código. Si es otra persona, que agregue su segundo apellido. |
| Un estudiante perdió su código | En el panel docente aparece en la columna «Código». |
| La letra se ve distinta | Las tipografías se descargan de internet; sin internet se usan las del sistema. Todo funciona igual. |
| Hay que cambiar una pregunta | Edita `4_Codigo_y_datos/scripts/construir_banco.py`, ejecuta `4_Codigo_y_datos/REGENERAR_TODO.bat` y reinicia el servidor. Hazlo **antes** de abrir el reto. |
