# Reglas — U16 `u16-cloudflare-containers-documentacion`

Reglas para llenar la columna Cloudflare Containers de `despliegues/COMPARACION.md` sin desplegar nada.
Salen de `requirements.md` (FR12.2a, FR12.4, FR12.5, NFR4, NFR5, NFR6), de `unit-of-work.md` («U15 y U16»)
y de `despliegues/cloudflare-containers/LEEME.md` («Pendiente de decidir en el ADR»). Decisiones del
asistente con la potestad que dio el humano (2026-10-25).

```yaml
rules:
  - id: BR16.1
    statement: 'Cada cifra de la columna lleva su URL de developers.cloudflare.com, su cita textual y la fecha de consulta.'
    category: validation
    applies_to: 'todas las filas de la columna Cloudflare Containers'
    trigger: al llenar una casilla
    logic: 'IF la cifra no sale de developers.cloudflare.com THEN no entra en la tabla; la casilla dice «sin cifra oficial» y el motivo'
    violation: 'la casilla no se llena'
    source: 'FR12.4, NFR6'
  - id: BR16.2
    statement: 'Cloudflare Containers no se despliega ni genera cargos mientras el humano no apruebe un monto y un tope.'
    category: policy
    applies_to: 'toda la unidad'
    trigger: siempre
    logic: 'IF la documentación dice que Containers está disponible solo en Workers Paid THEN no se activa ese plan; las filas que exigen medir dicen «sin medir: de pago (FR12.2a)»'
    violation: 'no aplica: no hay comando que ejecutar'
    source: 'FR12.2a'
  - id: BR16.3
    statement: 'El veredicto de NFR6 es «no cumple» porque Containers exige el plan Workers Paid.'
    category: calculation
    applies_to: 'filas «Costo en US$» y «Consumo frente a la cuota»'
    trigger: al llenar la columna
    logic: 'costo = mínimo mensual del plan Workers Paid + lo que exceda el uso incluido según las tarifas por segundo de la documentación; el consumo de una sesión se compara con el uso incluido en ese plan, no con una cuota gratuita, porque no existe'
    violation: 'no aplica'
    source: 'NFR6, FR12.2a'
  - id: BR16.4
    statement: 'El veredicto de NFR4 con el Dockerfile actual es «no cumple»: el disco es efímero.'
    category: calculation
    applies_to: 'fila «Sobrevive a un reinicio»'
    trigger: al llenar la columna
    logic: 'IF la documentación dice que el disco se reinicia desde la imagen al dormir o al parar THEN SQLite en /data se pierde y NFR4 = no_cumple; la casilla anota las alternativas documentadas (instantáneas inmutables, montaje FUSE a R2) y dice que las dos exigen cambiar la aplicación, lo que contradice «con el Dockerfile actual» (FR12.2, opción b)'
    violation: 'no aplica'
    source: 'NFR4, FR12.2'
  - id: BR16.5
    statement: 'La fila de arranque en frío y la de apagado a mitad del reto citan la cifra y la conducta documentadas.'
    category: calculation
    applies_to: 'fila «Arranque en frío»'
    trigger: al llenar la columna
    logic: 'arranque en frío = rango documentado (1 a 3 s); apagado = sleepAfter por defecto y la advertencia de que la plataforma puede detener un contenedor activo en cualquier momento; IF la cifra de arranque ≤ 30 s THEN NFR5 = cumple (sin medir), pero el apagado se anota como riesgo para NFR4'
    violation: 'no aplica'
    source: 'NFR5, NFR4'
  - id: BR16.6
    statement: 'La estimación de consumo usa el tipo de instancia más pequeño documentado (lite) y 90 minutos encendido.'
    category: calculation
    applies_to: 'fila «Consumo frente a la cuota»'
    trigger: al llenar la columna
    logic: 'memoria GiB-h = memoria de lite × 1,5 h; vCPU-min ≤ vCPU de lite × 90; disco GB-h = disco de lite × 1,5 h; cada una se divide por el uso incluido en Workers Paid; se agrega el caso «siempre encendido» (744 h) porque es lo que exigiría no perder SQLite'
    violation: 'no aplica'
    source: 'NFR6'
  - id: BR16.7
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
| BR16.1 | URL, cita y fecha en cada cifra |
| BR16.2 | Nada se despliega ni se paga |
| BR16.3 | NFR6: exige Workers Paid |
| BR16.4 | NFR4: disco efímero con el Dockerfile actual |
| BR16.5 | NFR5 y apagado a mitad del reto |
| BR16.6 | Consumo estimado con la instancia lite |
| BR16.7 | Sin claves ni respuestas |
