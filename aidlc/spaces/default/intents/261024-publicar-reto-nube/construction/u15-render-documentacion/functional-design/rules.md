# Reglas — U15 `u15-render-documentacion`

Reglas para llenar la columna Render de `despliegues/COMPARACION.md` sin desplegar nada. Salen de
`requirements.md` (FR12.2a, FR12.4, FR12.5, NFR4, NFR5, NFR6) y de `unit-of-work.md` («U15 y U16»).
Decisiones tomadas por el asistente con la potestad que dio el humano (2026-10-25).

```yaml
rules:
  - id: BR15.1
    statement: 'Cada cifra de la columna Render lleva su URL oficial de render.com, su cita textual y la fecha de consulta.'
    category: validation
    applies_to: 'todas las filas de la columna Render'
    trigger: al llenar una casilla
    logic: 'IF la cifra no sale de una página de render.com (docs o pricing) THEN no entra en la tabla; la casilla dice «sin cifra oficial» y el motivo; una cifra de memoria o de un foro nunca vale'
    violation: 'la casilla no se llena'
    source: 'FR12.4, NFR6'
  - id: BR15.2
    statement: 'Render no se despliega ni genera cargos mientras el humano no apruebe un monto y un tope.'
    category: policy
    applies_to: 'toda la unidad'
    trigger: siempre
    logic: 'IF no hay aprobación escrita de monto y tope THEN las filas que exigen medir (corte delgado, prueba común, latencias, reinicio medido) dicen «sin medir: no se despliega (FR12.2a)»'
    violation: 'no aplica: no hay comando que ejecutar'
    source: 'FR12.2a'
  - id: BR15.3
    statement: 'El veredicto de NFR6 para Render es «no cumple» mientras el plan que da disco sea de pago.'
    category: calculation
    applies_to: 'fila «Costo en US$» y fila «Consumo frente a la cuota»'
    trigger: al llenar la columna
    logic: 'IF la documentación dice que el disco persistente solo va en un servicio de pago THEN costo = precio del plan más barato con disco + disco, prorrateado como diga la documentación, y veredicto NFR6 = no_cumple'
    violation: 'no aplica'
    source: 'NFR6, FR12.2a'
  - id: BR15.4
    statement: 'El plan gratuito de Render se evalúa aparte, con su propia cifra de sueño, despertar y sistema de archivos.'
    category: calculation
    applies_to: 'filas «Sobrevive a un reinicio» y «Arranque en frío»'
    trigger: al llenar la columna
    logic: 'IF el plan gratuito duerme la instancia y pierde el sistema de archivos THEN NFR4 = no_cumple en gratuito; IF el tiempo de despertar documentado > 30 s THEN NFR5 = no_cumple en gratuito; la casilla trae las dos lecturas (gratuito y de pago)'
    violation: 'no aplica'
    source: 'NFR4, NFR5'
  - id: BR15.5
    statement: 'El consumo estimado de una sesión de 90 minutos se compara con la cuota que aplique y se dice qué pasa si se agota a mitad del reto.'
    category: calculation
    applies_to: 'fila «Consumo frente a la cuota gratuita»'
    trigger: al llenar la columna
    logic: 'horas-instancia = 1,5 h por sesión, pero un servicio con enlace fijo consume 24 h por día encendido; se compara con las 750 horas gratis por mes; ancho de banda ≈ 60.600 peticiones × 5 KB ≈ 0,3 GB por sesión frente a los GB incluidos del plan de espacio de trabajo; se anota la conducta documentada al agotar la cuota'
    violation: 'no aplica'
    source: 'NFR6, scalability-design.md de U1 (estimación de 60.600 peticiones)'
  - id: BR15.6
    statement: 'La columna nunca lleva claves, respuestas del banco ni datos de participantes.'
    category: policy
    applies_to: 'toda la unidad'
    trigger: siempre
    logic: 'solo cifras de la documentación y comandos públicos'
    violation: 'se quita antes del push'
    source: 'project.md («Forbidden»)'
```

## Resumen

| Regla | Qué cubre |
|---|---|
| BR15.1 | URL, cita y fecha en cada cifra |
| BR15.2 | Nada se despliega ni se paga |
| BR15.3 | NFR6: el disco es de pago |
| BR15.4 | NFR4 y NFR5 del plan gratuito |
| BR15.5 | Consumo estimado frente a la cuota |
| BR15.6 | Sin claves ni respuestas |
