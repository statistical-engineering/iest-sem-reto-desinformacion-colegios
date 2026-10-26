# Monitoreo — U4

- Igual que U1: salud en `GET /api/publico`, registros con `npx wrangler@4.148.0 tail` solo para
  arranque, cambios de estado y errores 500 (U1-O1, U1-O2). Las reglas no registran nada (U4-O1).
- Un error de regla en producción aparece como «Error interno:» con la traza en `tail`; el único
  esperado es el `RangeError` de tipo desconocido, que `validar_banco` impide al arrancar (U4-R3).
- La cobertura de `src/reglas/` se ve en cada corrida de `verificar.sh` y es la cifra que U17 pone en la
  fila NFR12 de `COMPARACION.md` (U4-O3).
- La prueba común (U2) mide contra Workers que los puntos y el orden coinciden con la versión local
  (U4-R1); el JSON de C3 lo registra en `comprobaciones[]` con `parte: "nfr"`.
