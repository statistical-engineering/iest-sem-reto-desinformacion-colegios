# Integración y despliegue — U1

- No hay despliegue automático: se despliega a mano y solo sin reto en curso (`project.md`, «Mandated»).
- Antes de desplegar: `node --test despliegues/cloudflare/pruebas/` y el simulacro local en
  «TODO BIEN». La revisión de PR (`.github/workflows/revisar-pr.yml`) no cambia.
- Después: la prueba común contra el enlace.
