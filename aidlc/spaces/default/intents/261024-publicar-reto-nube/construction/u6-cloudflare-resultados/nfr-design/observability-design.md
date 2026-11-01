# Observación — diseño U6

> **Revisión 2026-10-27 (una sola sala).** Sin código de sala en los registros de reiniciar y sin «Borrar
> la sala»: el cierre se comprueba con la lista de copias vacía y el resumen vacío (D7, NFR10.1).

Diseño no funcional de U6. Las decisiones están en `../decisions.md` (ADR-W14 a ADR-W18 y ADR-W21); los requisitos en `../nfr-requirements/`.

- `console.log` solo en reiniciar (`id_copia` y bytes), en borrar una copia (`id_copia`), en la migración
  3 («Migración v3 aplicada.») y en el arranque (commit de `version.json`, junto a la línea de U5);
  `console.error` en «copia dañada» (U6-O1). Ninguna descarga se registra (U6-O2).
- `metadatos.json` lleva `version_banco`, `huella_banco`, `version_app`, `version_esquema`, `estado` y
  `generado` (U6-O3): con eso se sabe con qué código y banco se jugó cada reto sin consultar nada más.
- Cierre verificable (U6-O4): después de guardar el paquete, «Reiniciar» y borrar todas las copias, el
  docente abre la tarjeta «Copias» (vacía) y el panel (sin participantes ni colegios). U6 deja esos pasos
  en `despliegues/cloudflare/LEEME.md`; la guía final es de U17.
- Recorrido de las pantallas (U6-O5): `code-summary.md` de U6 lleva la tabla del recorrido con fecha,
  persona y «sí» o «no» por línea.
