# Prueba común

Una sola prueba que corre contra la URL de cualquier versión desplegada (requisito FR12.3). Así las
cuatro opciones se miden igual.

## Qué revisa

- Las mismas comprobaciones de `2_Aplicacion_Reto/pruebas/simulacro.py`, sin debilitar ninguna.
- Las fugas de respuestas antes de «resultados» y la separación entre varias salas.
- La latencia al responder y del tablero, un reinicio a mitad de la prueba y el arranque en frío.

## Estructura prevista

```text
prueba_comun/
├── LEEME.md
├── src/        la prueba: recibe la URL y la clave por argumento o variable de entorno
└── pruebas/    pruebas unitarias de la propia prueba
```

## Pendiente de decidir en el diseño

- Cómo reemplaza las comprobaciones que hoy abren la base de datos directamente (el simulacro lee y
  cambia `config.abierto_en`), sin abrir un atajo inseguro en un servicio público.
- Qué resultado se espera contra la versión local, que no tiene las correcciones de fugas ni las salas.

Hasta que esté aprobado, no hay código aquí. `simulacro.py` no se copia ni se cambia: la prueba común se
escribe aparte.
