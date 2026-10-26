# Observación — diseño U6

Diseño no funcional de U6. Las decisiones están en `../decisions.md` (ADR-W14 a ADR-W18); los requisitos en `../nfr-requirements/`.

- `console.log` solo en reiniciar (código de sala, `id_copia`, bytes) y en el arranque (commit de
  `version.json`, junto a la línea de U5); `console.error` en «copia dañada» (U6-O1). Ninguna descarga
  se registra (U6-O2).
- `metadatos.json` lleva `version_banco`, `version_app`, `version_esquema`, `estado` y `generado`
  (U6-O3): con eso se sabe con qué código y banco se jugó cada reto sin consultar nada más.
- Cierre verificable (U6-O4): la guía (U17) pide, después de «Borrar la sala», abrir
  `/api/publico?sala=<código>` (404) y `GET /api/admin/salas` (no aparece); U6 deja esos dos pasos en el
  `LEEME.md` de la opción.
