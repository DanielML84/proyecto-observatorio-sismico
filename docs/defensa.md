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

## Fase 4 · Modelo de datos
| Pregunta | Respuesta (Daniel) | Dónde está la evidencia |
|---|---|---|
| ¿Qué diferencia hay entre un terremoto y una versión? | | FAQ 12 y 20 |
| ¿Qué es el grano de una tabla? Dime el grano de cada una de tus tablas | | Memoria §6 |
| Para contar terremotos por país, ¿qué tabla usas y por qué? | *(⚠️ trabajada en la sesión 2: estado actual, NO versiones)* | FAQ 20 y 22 |
| Con la secuencia de la FAQ 12, ¿cuántas filas hay en cada tabla? | | FAQ 12 |
| ¿Cuál es la tabla de hechos y cuáles son las dimensiones? | | Memoria §6; notebook de modelado dimensional de Juan |
| ¿Cómo impides que haya dos filas del mismo terremoto? Demuéstralo | | `fase4-postgres-esquema.txt` |
| ¿Por qué guardas el JSON original de cada versión? | | Enunciado §7; tabla `evento_version.raw` |
| ¿Dónde guarda el productor lo que ya ha publicado? ¿Por qué no en un diccionario? | | Memoria, D16; FAQ 10 |
| ¿Por qué no publicas PostgreSQL fuera de Docker? | | Enunciado §9 |

## Fase 5 · Idempotencia (📘 respuestas modelo «para estudiar»)
| Pregunta | Respuesta modelo | Evidencia |
|---|---|---|
| ¿Qué es un UPSERT y por qué lleva un `WHERE`? | «INSERT … ON CONFLICT DO UPDATE»: inserta y, si el id ya existe, actualiza. El `WHERE evento_actual.updated_ms < EXCLUDED.updated_ms` hace que SOLO se actualice si la versión que llega es posterior; así una versión antigua que llega tarde no pisa a la nueva. | `backend/src/db.py`; FAQ 12 |
| ¿Por qué guardar la versión y el estado actual en una transacción? | Para que se guarden las dos cosas o ninguna. Si falla a mitad, no queda un historial sin estado actual ni al revés. | `db.guardar_evento` |
| ¿Qué pasa si el consumidor se cae después de guardar y antes de confirmar el offset? | Kafka le reenvía el mensaje al volver. La versión ya existe (`ON CONFLICT DO NOTHING`) y el UPSERT no actualiza (mismo `updated`) → la base queda igual. Es procesamiento «al menos una vez» con escritura idempotente. | FAQ 13; enunciado §7 |
| De 8 mensajes de prueba, solo 3 filas en `evento_actual`. ¿Qué pasó con los otros 5? | 2 eran repeticiones de una versión ya guardada (ignorados), 1 era una revisión que **actualizó** E1 (no crea fila, cambia la existente), 1 era una explosión (excluida, en cuarentena con tipo `excluido`) y 1 tenía latitud 145 (inválido, en cuarentena). | `fase5-faq12-idempotencia.txt` |
| ¿Kafka garantiza el orden? | Solo dentro de una partición. Con la clave = id, todas las versiones de un terremoto van a la misma partición y llegan en orden; entre terremotos distintos no hay orden global (se vio en el log). Aun así comparamos `updated`, porque el orden no sustituye a la comparación de versiones. | Log del consumidor; enunciado §7 |

## Fase 5 · Productor real (📘 respuestas modelo)
| Pregunta | Respuesta modelo | Evidencia |
|---|---|---|
| Si reinicias el productor, ¿vuelve a publicar todo? | No. Al arrancar lee la tabla `version_publicada` de PostgreSQL («estado cargado: N versiones») y la pone en un diccionario. Solo publica ids desconocidos o con `updated` mayor. *(Los archivos de `data/raw` NO se usan para esto: son solo el archivo de originales.)* | Log del productor; `db.cargar_versiones_publicadas` |
| ¿Por qué un diccionario y no una lista? | Buscar un id en una lista cuesta O(N) (hay que recorrerla); en un diccionario, O(1) de media, a cambio de algo más de memoria. Con 220 eventos por minuto da igual, con millones no. | Enunciado §10; FAQ 33 |
| ¿Qué pasa si USGS no responde? | Se reintenta con espera progresiva (2, 4 y 8 s); cada intento queda en `consulta_ingesta` con su error; no se borra nada y se vuelve a intentar en el siguiente ciclo. | `productor.descargar_feed` |
| ¿Cómo evitas guardar copias idénticas del original? | Huella SHA-256 de los `features`; solo se guarda si cambia. Se excluye `metadata.generated`, que USGS cambia en cada respuesta (lo descubrimos con los datos reales). | Memoria, D21 |
| ¿Cómo demuestras que no se pierde ni se duplica ningún terremoto? | Con una conciliación: publicados = actuales + cuarentena, y un LEFT JOIN que busca los ids publicados que no están en ninguna de las dos tablas → 0 filas. | `fase5-conciliacion.txt` |
| Si arrancas dos productores por error, ¿se duplican los datos? | Se publicarían mensajes repetidos en Kafka, pero la base no cambia: clave primaria + UPSERT con `WHERE updated_ms <` = escritura idempotente. | Memoria §5 y §9 |

## Fase 6 · País (📘 respuestas modelo)
| Pregunta | Respuesta modelo | Evidencia |
|---|---|---|
| ¿Cómo asignas el país a un terremoto? | Construyo un punto con (longitud, latitud) y busco qué polígono del catálogo Natural Earth lo cubre (punto en polígono, Shapely). No uso el texto de `place`. | `geografia.py` |
| ¿Y si está en el mar? | No lo cubre ningún polígono → `country_id` NULL → «Sin país asignado». Se conserva en el análisis; no se asigna al país más cercano. | Enunciado §4.3 |
| ¿Por qué `LEFT JOIN` y no `INNER JOIN` al contar por país? | `INNER JOIN` solo devuelve filas con pareja en `pais`, así que **eliminaría** los 44 terremotos sin país y desaparecerían del análisis. El enunciado exige mantener la categoría «Sin país asignado». `LEFT JOIN` conserva todos y `COALESCE` les pone el nombre. | `fase6-paises.txt` |
| ¿Qué es el STRtree y por qué lo usas? | Un índice espacial: agrupa los polígonos por sus rectángulos envolventes y descarta de golpe los lejanos, en vez de probar los 177 uno a uno. Medido: mismo resultado y ≈10 veces más rápido. | Memoria §8 |
| ¿Qué pasa con un punto justo en la frontera? | `covered_by` lo cuenta como dentro; si lo cubren dos países, gana el `country_id` alfabéticamente menor (regla determinista). En datos reales: 0 casos. | Memoria §3bis |
| ¿Por qué el 77 % de los terremotos son de EE. UU.? | Porque el feed incluye magnitudes muy pequeñas que solo detectan las redes densas de EE. UU. Es un sesgo de cobertura de detección, no de actividad sísmica real. Para comparar regiones hay que filtrar, por ejemplo, magnitud ≥ 4. | Enunciado §8 |

## Fase 7 · Histórico (📘 respuestas modelo)
| Pregunta | Respuesta modelo | Evidencia |
|---|---|---|
| ¿Por qué la media diaria se divide entre 365 y no entre los días con terremotos? | Porque queremos la media de **todos los días** del periodo, incluidos los que no tuvieron ningún evento (enunciado §8.4; FAQ 23). Si dividiera solo entre los días con eventos, quitaría los ceros y la media saldría **inflada**. Ejemplo: 10 terremotos en un periodo de 10 días, todos en 2 de ellos → media real 1/día; mal calculada, 5/día. A escala mundial con mag ≥ 4 casi todos los días tienen eventos, pero en un país concreto (p. ej. España) habría muchos días a cero y el error sería grande. | `fase7-historico.txt` |
| ¿Cómo descargaste el histórico sin pasarte del límite? | Por meses; antes de cada uno, `/count` con los mismos parámetros; si pasara de 20.000 se parte en dos automáticamente. Máximo real: 2.684. count = descargados en los 12 meses. | `manifest.json`; memoria §3 |
| ¿Por qué hay que deduplicar si no salió ningún repetido? | Porque `starttime` y `endtime` son inclusivos: un evento justo a las 00:00:00 del día 1 aparecería en dos meses. Esta vez no hubo ninguno, pero la regla está implementada y probada. | Memoria D27–D30 |
| ¿Por qué el filtro reciente es `mag >= 4` y no `> 4`? | Porque `minmagnitude=4` de USGS incluye el 4,0 (lo comprobé: 70 eventos con 4,0 en enero). Para comparar igual con igual, el filtro reciente tiene que ser el mismo. | Memoria D30 |
| ¿Por qué hay casi el doble de terremotos en julio de 2025? | Por el M8,8 de Kamchatka (29/07/2025). Lo comprobé separando la zona del resto del mundo: la zona pasa de ~19 eventos/mes a 1.375 en julio (×71) y luego baja mes a mes; el resto del mundo no cambia. Es una secuencia de réplicas localizada, que supone el 21,7 % de todo el año. | `fase7-historico.txt`; memoria §7 |
| Entonces, ¿2025 es un buen año de referencia? | Es el que propone el enunciado, pero hay que saber que su media (50,14/día) está inflada por Kamchatka; sin la zona sería 39,25. Al comparar el periodo reciente lo menciono como limitación, o comparo también sin la zona. | Memoria §7 |
