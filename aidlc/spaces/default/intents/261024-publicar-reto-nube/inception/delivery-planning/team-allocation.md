# Quién construye cada Bolt

Un **Bolt** es una pasada de construcción sobre un pedazo del trabajo, que termina en algo que
funciona (`bolt-plan.md`). Este alcance (`classic`) no tiene etapa de formación de equipos, así que
todos los Bolts los construye el agente desarrollador (`aidlc-developer-agent`, IA). Los Bolts de una
misma tanda corren en paralelo, cada uno en su propia copia de trabajo.

## Asignación

| Bolt | Unidad | Construye | Decide y aprueba |
|---|---|---|---|
| B1 | U1 | aidlc-developer-agent | El humano: ADR de la opción y punto de control del corte |
| B2 | U2 | aidlc-developer-agent | El humano |
| B3 | U11 | aidlc-developer-agent | El humano: ADR de la opción y punto de control del corte |
| B4 | U4 | aidlc-developer-agent | El humano |
| B5, B6 | U15, U16 | aidlc-developer-agent | El humano |
| B7 | U3 | aidlc-developer-agent | El humano |
| B8 a B12 | U5, U6, U12, U13, U14 | aidlc-developer-agent | El humano |
| B13 | U17 | aidlc-developer-agent | El humano: ADR final de elección |

**Revisión del 2026-10-25:** quedan B4, B9, B11, B2 y B13, todos del agente desarrollador; B3, B7, B8,
B10 y B12 se saltan.

## Lo que solo hace una persona

Según Q8-A:

- crear la cuenta gratuita de cada hosting (Cloudflare y GitHub) antes de su corte;
- cargar la clave docente (`CLAVE_DOCENTE`) como secreto de Cloudflare. El asistente nunca la ve;
- aprobar que se salten U7 a U10 (Apps Script, Q2-A);
- subir a `develop` cuando lo pida. El humano y el asistente suben directo; el resto del equipo, por PR
  (`team.md`, «Corrections»).
