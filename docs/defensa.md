# Preparación de la defensa

> El profesor hará preguntas sobre el proyecto. Este archivo recoge las preguntas probables por
> fase. **Las respuestas las escribe Daniel con sus palabras**; Claude las revisa y corrige.
> Ensayo: tapar la respuesta y contestar en voz alta.

## Las dos obligatorias (guía §3.3)
1. **Explica el recorrido de un terremoto desde USGS hasta el panel, componente a componente.**
   - Respuesta: *(se completa cuando el sistema esté montado)*
2. **Justifica una decisión técnica propia.**
   - Candidatas: ver el Anexo A de `memoria.md`.

## Fase 1 · Fuentes de datos
| Pregunta | Respuesta (Daniel) | Dónde está la evidencia |
|---|---|---|
| ¿Qué contiene `all_day.geojson`? ¿Es el día anterior? | | Memoria §3; FAQ 8 |
| ¿Por qué consultar el feed cada minuto no genera terremotos nuevos cada minuto? | *(respondida en la sesión: mismo `id` + mismo `updated` = misma versión)* | FAQ 10 y 12 |
| ¿Qué diferencia hay entre `time` y `updated`? ¿En qué unidad vienen? | | Notebook 01, §8 |
| ¿Por qué hay eventos con profundidad negativa? ¿Los eliminas? | | Memoria §4 |
| ¿Qué haces con las explosiones? | | Notebook 01, §5 |
| ¿Qué significa que un evento tenga varios `ids`? | | Notebook 01, §9 |
| ¿Por qué hay que deduplicar al descargar el histórico por meses? | | Memoria §3 |
