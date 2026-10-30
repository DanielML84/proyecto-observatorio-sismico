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

## Fase 3 · Kafka
| Pregunta | Respuesta (Daniel) | Dónde está la evidencia |
|---|---|---|
| ¿Para qué sirve Kafka si podrías guardar directamente en la base de datos? | | FAQ 11 |
| ¿Qué es un topic? ¿Y un offset? ¿El offset es el id del terremoto? | | FAQ 14 |
| ¿Qué pasa con los mensajes si el consumidor está parado 2 minutos? ¿Y 2 semanas? | | `compose.yaml` (retención) |
| ¿Por qué los contenedores usan `kafka:9092` y no `localhost:9092`? | | FAQ 28 |
| ¿Cómo demuestras que los mensajes sobreviven a un reinicio? | | Bitácora, sesión 2 |
| Si envías dos veces el mismo terremoto, ¿Kafka lo detecta? ¿Qué consecuencias tiene? | *(Daniel: «se duplicarían los 187 terremotos» → completar con el porqué)* | `docs/evidencias/fase3-pipeline-python.txt`; memoria |
| ¿Por qué el consumidor confirma el offset después de procesar y no antes? | | Memoria, D13; FAQ 13 |
| ¿Por qué el id del terremoto siempre va a la misma partición? | | Contrato (clave) |

## Fase 2 · Contrato del mensaje
| Pregunta | Respuesta (Daniel) | Dónde está la evidencia |
|---|---|---|
| ¿Qué clave usas en Kafka y por qué? | | `docs/contrato-mensaje.md` |
| ¿Por qué el productor no filtra las explosiones? | | Memoria, D9 |
| ¿Qué diferencia hay entre `ingested_at` y `time`? | | Contrato; enunciado §6 («separa tiempo de ocurrencia y de procesamiento») |
| ¿Cómo separas los datos de la reproducción de los reales? | | Memoria, D10 |
