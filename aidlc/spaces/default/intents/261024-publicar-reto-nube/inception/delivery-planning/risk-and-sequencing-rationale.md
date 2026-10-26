# Por qué este orden

Un **Bolt** es una pasada de construcción sobre un pedazo del trabajo, que termina en algo que
funciona (`bolt-plan.md`). Un **corte delgado** es la versión mínima de punta a punta que demuestra que
todo encaja.

## Criterio

**Primero lo más riesgoso** (Q1-A), al estilo de Cohn: se hace antes lo que más puede cambiar el plan.
No se usó un puntaje formal (por ejemplo WSJF, que divide valor y urgencia por tamaño): hay una sola
meta, elegir la opción que pasa todo, y el riesgo de cada opción es lo que la decide.

1. **El corte de Workers (U1) va primero.** Lo eligió el humano en Units Generation, y es la primera
   unidad sin dependencias en orden alfabético (`unit-of-work-dependency.md`, «Corte delgado»). Crea
   la prueba común mínima y el contrato de la API que usan todas.
2. **Después, los cortes de las otras opciones y la prueba común** (tanda 1). Si una opción no pasa su
   corte, se sabe antes de construir sus otras tres unidades.
3. **Las cadenas de cada opción** siguen sus dependencias: reglas, salas, resultados.
4. **La comparación (U17) va al final**, porque necesita las mediciones de todas.

## Desvíos del grafo de dependencias

Ninguno: cada tanda solo tiene unidades cuyas dependencias ya están hechas. El único cambio es que no
se construye Apps Script (U7 a U10, Q2-A). Se saltan con aprobación del humano, como prevé
`unit-of-work-dependency.md` («Si se abandona una opción»).

## Riesgos y qué se hace

| Riesgo | Qué se hace | Dónde |
|---|---|---|
| Apps Script no puede cumplir el contrato (C-01) | Queda «no pasa» con la evidencia, sin construirse | Q2-A, B13 |
| El corte de Workers no pasa | Se termina la prueba común contra la versión local y las otras opciones siguen | Q5-A, B1 |
| GitHub Pages en otro dominio que la API (C-04) | CORS y URL base de la API se resuelven en su corte | B3 |
| Las reglas no coinciden entre opciones (C-05) | La forma de los datos queda fija en U1; U4 y U12 van en paralelo sobre ella | B1, B4, B8 |
| Fugas de respuestas en rutas nuevas (C-14) | Toda clave nueva que llega al navegador tiene su comprobación de fugas | B2 |
| Cada corrida de la prueba común tarda al menos 10 minutos (C-09) | Se acepta; se corre una vez por opción en cada punto de control | B2 |
| Un push sin revisión de PR rompe algo | Antes de cada push: ganchos, simulacro y prueba común si toca una opción | `bolt-plan.md`, «Reglas para todos los Bolts» |
| Cambiar algo con un reto en curso | No se despliega con un reto en curso (`project.md`, «Mandated») | Todos |
