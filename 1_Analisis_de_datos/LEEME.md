# Análisis de los datos del reto «Detectives de la desinformación»

Esta carpeta explica **qué datos usa el reto, de dónde salen y cómo se comportan**. Cada
subcarpeta tiene su `ANALISIS.md`, los datos limpios (`datos/`), tablas resumen (`tablas/`) y
gráficas (`figuras/`). Todo se regenera con:

```
python ../4_Codigo_y_datos/scripts/generar_analisis.py
```

## El centro es la desinformación; internet es el contexto

| # | Carpeta | Papel en el reto | Qué responde |
|---|---|---|---|
| 1 | `01_Colombiacheck_chequeos_verificados/` | **Núcleo** | ¿Qué desinformación se verifica en Colombia, cómo se califica y cómo cambia? |
| 2 | `02_DANE_ENTIC_horas_uso_internet/` | Contexto de exposición | ¿Cuánto tiempo pasamos conectados? |
| 3 | `03_DANE_ENTIC_actividades_internet/` | Contexto de exposición | ¿Por qué puertas entra la información (redes vs medios)? |
| 4 | `04_DANE_ENTIC_actividades_redes_sociales/` | Contexto de difusión | ¿Para qué usamos las redes? ¿Por qué se reenvían las cadenas? |
| 5 | `05_BancoMundial_conectividad/` | Contexto histórico | ¿Qué tan rápido nos conectamos? |
| 6 | `06_Marco_estudio_Nature_Arechar2023/` | **Marco científico** | ¿Por qué creemos y compartimos falsedades y qué ayuda? |

## Diez ideas clave (calculadas de los datos)

1. Colombiacheck publicó **2.980 chequeos verificados** entre 01-2020 y 09-2026.
2. **76,6 %** terminan en «Falso» y 20,3 % en «Cuestionable».
3. …pero eso **no** mide cuánta desinformación hay en redes: el verificador elige qué revisar (sesgo de selección).
4. La desinformación cambia de tema: títulos con COVID‑19/vacunas pasan de 173 (2020) a
   1 (2026); títulos con inteligencia artificial pasan de 0 (2022) a 56 (2025).
5. Solo 4,6 % de los chequeos sale en fin de semana: eso refleja el horario de la redacción, no el de los rumores.
6. **79,3 %** de los colombianos usa internet (2024); en 2013 se superó por primera vez la mitad.
7. Los usuarios de internet pasan en promedio **4,90 horas al día** conectados
   (5,17 h urbano vs 3,28 h rural). Son horas de **internet**, no de redes.
8. **80,2 %** de los usuarios de internet usa redes sociales (31,3 millones de personas).
9. **96,8 %** usa las redes para hablar con familia y amigos: por eso las cadenas
   falsas llegan «avaladas» por gente de confianza.
10. El estudio de Nature (16 países, 34.286 personas) muestra que la gente comparte falsedades que
    reconocería como falsas si se detuviera a pensar, y que un simple recordatorio de exactitud ayuda.

## Cómo se conecta con la aplicación

La app (`../2_Aplicacion_Reto/`) arma sus preguntas leyendo los archivos limpios de estas
carpetas (`4_Codigo_y_datos/scripts/construir_banco.py`). Si se actualizan los datos: primero se
corre este análisis y después `construir_banco.py` (o todo junto con `4_Codigo_y_datos/REGENERAR_TODO.bat`).
