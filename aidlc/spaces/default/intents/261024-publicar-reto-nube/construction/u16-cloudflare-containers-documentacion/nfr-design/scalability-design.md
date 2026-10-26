# Escala — diseño U16

Diseño no funcional de U16 (solo documentación sobre Cloudflare Containers). Los requisitos están en
`../nfr-requirements/`.

Cómo se calcula la fila «Consumo frente a la cuota» (U16-E2 a U16-E4) con la instancia `lite` (1/16 vCPU,
256 MiB, 2 GB; https://developers.cloudflare.com/containers/platform-details/limits/) y el uso incluido en
Workers Paid (https://developers.cloudflare.com/containers/pricing/):

| Recurso | Incluido al mes | Una sesión de 90 min | Porcentaje | Siempre encendido (744 h) | Excedente y costo |
|---|---|---|---|---|---|
| Memoria | 25 GiB-h | 0,25 GiB × 1,5 h = 0,375 GiB-h | 1,5 % | 186 GiB-h | 161 GiB-h × 3.600 × US$ 0,0000025 ≈ US$ 1,45 |
| vCPU | 375 vCPU-min | ≤ 1/16 × 90 = 5,6 vCPU-min | 1,5 % | ≤ 2.790 vCPU-min si estuviera al 100 %; en reposo casi 0 | se cobra solo CPU activa |
| Disco | 200 GB-h | 2 GB × 1,5 h = 3 GB-h | 1,5 % | 1.488 GB-h | 1.288 GB-h × 3.600 × US$ 0,00000007 ≈ US$ 0,32 |
| Salida | 1 TB (NA y EU) | ≈ 0,3 GB | 0,03 % | igual por sesión | 0 |

Decisión: la casilla trae las dos lecturas. La sesión sola queda muy por debajo del 50 %, pero el plan
cuesta US$ 5 al mes (NFR6) y, para no perder SQLite, habría que no dormir nunca, lo que excede el incluido
en memoria y disco (≈ US$ 1,77 adicionales al mes). Las peticiones HTTP pasan además por el Worker y
cuentan en los 10 millones incluidos de Workers Paid (https://developers.cloudflare.com/workers/platform/pricing/):
60.600 por sesión es 0,6 %.
