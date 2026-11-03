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

## Fase 8 · API (📘 respuestas modelo)
| Pregunta | Respuesta modelo | Evidencia |
|---|---|---|
| ¿Qué diferencia hay entre `generated` y `last_ingestion`? | `generated` = cuándo la API creó ESTA respuesta (cambia en cada consulta). `last_ingestion` = última descarga correcta de USGS (se congela si se para el productor). Una respuesta recién generada puede contener datos antiguos; por eso el panel enseña las dos y avisa si la ingesta tiene más de 5 min. | `api.py`; FAQ 31 |
| ¿Cómo garantizas que el mapa y los gráficos usan los mismos filtros? | Las tres rutas construyen el WHERE con la misma función `filtros()`. Es imposible que diverjan. | `api.py` |
| ¿Qué devuelve la API si se cae la base de datos? | Un 503 con un mensaje de error explícito, nunca «0 eventos», porque eso parecería un resultado válido. | Contrato API; prueba con BD caída |
| ¿Por qué solo publicas el puerto de la API y en 127.0.0.1? | Es lo único que debe ser accesible (para ngrok en el equipo). Kafka y PostgreSQL no se exponen. `127.0.0.1` = solo desde este equipo, no desde la red local. | Enunciado §9 |
| ¿Por qué la comparación usa mag ≥ 4 aunque el usuario filtre mag ≥ 2? | Porque el histórico solo tiene mag ≥ 4. Comparar todo lo reciente con un histórico filtrado no sería equivalente (FAQ 23). Se usa max(4, filtro). | `api.py` |
| Hoy hay un 50 % menos que la media de 2025, ¿hay menos terremotos? | No se puede decir así. La media (50,14) está inflada por días extremos (645 el día del M8,8). Comparado con la distribución diaria de 2025, 25 está en la parte baja (mediana 43; solo el 2,7 % de los días tuvieron 25 o menos; el 7,9 % sin Kamchatka): bajo, pero no excepcional. Además, el feed reciente puede completarse más tarde. Probé la hipótesis de que faltaban sobre todo terremotos de 4,0–4,5 subiendo el filtro a 4,5, y no se confirmó (−44,6 %). | `fase8-comparacion-historica.txt`; memoria §7 |
| ¿Por qué usar la mediana además de la media? | La media se deja arrastrar por los valores extremos; la mediana es el valor del medio y representa mejor un día típico cuando hay picos. | Ídem |
| ¿Para qué te sirvió la tabla `fecha`? | Para contar los 365 días con un LEFT JOIN, incluidos los días con 0 eventos. Sin ella, esos días no aparecerían y los percentiles saldrían mal. | Ídem; FAQ 23 |

## Fase 9 · Panel (📘 respuestas modelo)
| Pregunta | Respuesta modelo | Evidencia |
|---|---|---|
| Aplicas M≥6 con la API caída: el formulario dice 6 y «Filtros de esta lectura» dice 4,5. ¿Qué muestra el mapa? | Los terremotos con M≥4,5: los de la **última lectura correcta**. La petición con M≥6 nunca respondió. El formulario dice lo que se PIDIÓ; «Filtros de esta lectura» (que sale de la respuesta de la API) dice lo que realmente se está viendo. Comparación: pides el periódico nuevo, pero no llega; sigues leyendo el de ayer. | `frontend/src/app/estado-sistema/` |
| Eliges Japón y el mapa sale vacío. ¿Cómo sabes que no es un fallo? | Porque la API respondió bien con 0 eventos: aparece «Sin resultados» (no el aviso rojo), «Último acceso correcto» se actualiza a ahora y «Filtros de esta lectura» dice Japón. Si fuera un fallo: aviso rojo, la hora se queda en la anterior y los filtros siguen siendo los de antes. | Ídem |
| ¿Por qué es importante distinguir «no hay datos» de «no he podido obtener datos»? | Porque un mapa vacío puede significar las dos cosas y el usuario se engañaría. El contrato de la API lo exige («no cero eventos como si fuera un resultado válido») y es una prueba de aceptación (cerrar el túnel). | Contrato API; enunciado §11 |
| ¿Por qué solo hay un archivo (`api.service.ts`) que hable con la API? | Para que la URL y la forma de pedir datos estén en un solo sitio: al pasar a ngrok solo cambia `config.json`, y todos los componentes piden los datos con los mismos filtros. | `api.service.ts` |
| ¿Por qué la lista de países es fija (177 + «Sin país asignado») y no depende de los filtros? | Para que el usuario encuentre siempre su país; si no hay eventos, el panel lo dice («Sin resultados»). La lista sale del mismo catálogo que las fronteras y la tabla `pais` (mismos 177 códigos, comprobado). | Memoria, Anexo A |
| Filtras todo 2025 y ordenas la tabla por magnitud: el máximo sale 7,8. ¿Por qué no aparece el M8,8 de Kamchatka? | Porque la respuesta está **truncada**: la API envía como mucho 5.000 eventos (los más recientes) de 18.302, y el del 29/07 queda fuera. La tabla ordena solo esos 5.000 y lo avisa. Por eso las estadísticas NO se calculan en el navegador con la muestra truncada: las calcula la API sobre todos los eventos (enunciado / contrato API). | `fase9-bloque3-tabla.png` |
| Si filtras M≥4, ¿qué pasa con los terremotos que no tienen magnitud? | No cumplen el filtro (desconocido no es ≥4), pero no se esconden: la API los cuenta aparte con el mismo periodo y país (`sin_valor.magnitud_excluidos_por_filtro`) y el panel lo dice. Lo exige el contrato de la API. Lo detectó Claude Code en el bloque 4 y se corrigió en la API. | `api.py`; contrato API |
| Comparas «la última semana» y sale −94 %. ¿Ha bajado la actividad? | No: el sistema solo tiene datos del feed desde su primera descarga (menos 24 h). La API lo indica (`periodo_cubierto: false`, `cobertura_feed_desde`) y el panel avisa de que el recuento puede estar incompleto. Un porcentaje sin cobertura no es un hallazgo. | `api.py`; memoria D32 |
| ¿Y si el sistema estuvo apagado 3 días? | Habría un hueco que `cobertura_feed_desde` no detecta (limitación documentada). Se recuperaría descargando ese intervalo del catálogo FDSN (por ejemplo con `updatedafter` o `starttime`/`endtime`) y publicándolo por Kafka como el histórico; el consumidor, al ser idempotente, no duplicaría nada. | Enunciado §5 |
| ¿Por qué se ve un 414 % de aumento en EE. UU. con un solo terremoto? | Porque se esperaban 0,19: con una base tan pequeña, un terremoto mueve el porcentaje cientos de puntos. El panel lo avisa («Base muy pequeña») si se espera menos de 1 terremoto. Ese umbral, `BASE_MINIMA = 1`, es un **criterio nuestro**, no del enunciado; solo añade un aviso y no cambia ningún cálculo. | Memoria §7bis, D40 |
| ¿Por qué mostráis el porcentaje aunque sepáis que engaña? | Porque preferimos no ocultar el cálculo de la API y explicar cómo leerlo. Ocultarlo o cambiarlo por ND haría parecer que no hay dato. ND se reserva para cuando no se puede calcular (`variacion_pct` null). | Memoria D39 |
| ¿Qué significa `periodo_cubierto: false`? | Que el recuento puede estar incompleto. Tiene dos causas: el periodo empieza antes de los datos del feed o termina en el futuro. El panel usa además `cobertura_feed_desde` para distinguirlas y dar el aviso correcto; en un periodo que cruza de 2025 a 2026 salen dos avisos. | `comparacion-historica.component.ts`; `fase9-panel.txt` |
| ¿Por qué aparece un tramo de magnitud 3,5–4,0 con 0 si la API no lo envía? | Porque la API solo envía los tramos con eventos, y dibujar solo esos escondería el hueco. Un 0 también es un dato, así que el panel rellena los tramos intermedios. | `estadisticas.component.ts`; D38 |
| ¿Qué es una ventana parcial? | Una ventana de 1 h que el periodo no cubre entera (normalmente la primera y la última). Sale en tono claro para que no parezca que hubo menos actividad. Si eliges horas exactas, no aparece ninguna. | `grafico-horas.component.ts`; D42 |
| ¿Cómo evitas peticiones solapadas? | El siguiente refresco se programa cuando termina el anterior, no con un intervalo fijo. Si cambias filtros durante una consulta, esta no se pinta y se repite al acabar con los filtros nuevos. Probado con tres cambios seguidos: nunca hubo dos ciclos a la vez y ganó el último. | `app.component.ts`; D37 |
| ¿Por qué no usas una librería de gráficos? | El encargo pide evitar dependencias si es razonable. Las barras son tablas HTML, así que el gráfico es a la vez su alternativa accesible. Las horas son un solo trazado SVG, porque un elemento por barra pesaría demasiado con 8.760 ventanas. | D35 |
| ¿Por qué `Promise.allSettled` y no `Promise.all`? | `Promise.all` falla entero si falla una llamada. Con `allSettled` espero a todas y sé cuál ha fallado: si solo caen las estadísticas, el mapa y la tabla se actualizan igual y el panel marca las estadísticas como antiguas. | `app.component.ts` |
| ¿Cómo sabes que el panel funciona, además de compilar? | Lo probé en un navegador real comparando cada resultado con la API, paré de verdad el contenedor de la API para ver el aviso y la recuperación, y probé también el build de producción. Las situaciones difíciles de provocar se simularon, y en la memoria consta cuáles. | `fase9-panel.txt`; memoria §7bis |
| Apagaste el sistema por la noche. ¿Perdiste los terremotos de esas horas? | No, porque la parada fue de menos de 24 h: el feed siempre trae las últimas 24 h y la primera descarga al volver publicó las 175 novedades (lo vi en `consulta_ingesta`). Con más de 24 h parado sí habría un hueco, que rellenaría desde el catálogo. | `recuperacion-parada-nocturna.txt` |

### Fase 10 · Túnel ngrok
| Pregunta | 📘 Respuesta modelo (para estudiar) | Evidencia |
|---|---|---|
| ¿Por qué el túnel apunta a `http://api:8000` y no a `http://localhost:8000`? | Porque ngrok corre en su propio contenedor. Dentro de un contenedor, `localhost` es **ese mismo contenedor**, no mi PC ni la API. En la red de Compose cada servicio se encuentra por su **nombre** (`api`), igual que el consumidor encuentra a `kafka` y a `postgres`. | `compose.yaml` (servicio `tunel`) |
| Si apagas el sistema 30 horas, ¿se recuperan solos los terremotos? | **No todos.** El feed solo contiene las últimas 24 h: al arrancar se recuperan las últimas 24 h, pero las ~6 primeras horas de la parada quedan fuera (hueco). Habría que rellenarlo desde el catálogo FDSN con `starttime`/`endtime` (o `updatedafter`). | `recuperacion-parada-nocturna.txt` |
| ¿Por qué ngrok en Docker y no instalado en Windows? | Ambas opciones están permitidas por el enunciado. En mi equipo la Store/winget fallaban y Defender bloqueaba el .exe (falso positivo conocido). En Docker uso la imagen oficial, no instalo nada y se levanta igual que el resto. | `fase10-tunel-ngrok.txt` |
| ¿Dónde está el authtoken de ngrok? | Solo en mi `.env`, que está en `.gitignore`. Compose lo pasa como variable de entorno al contenedor. No está en Git ni en el frontend (`config.json` solo lleva la URL pública, que no es secreta). | `.gitignore`, `.env.example` |
| ¿La URL de ngrok es HTTPS? ¿Tiene certificado FastAPI? | La URL pública es HTTPS y el certificado lo gestiona ngrok. FastAPI sigue en HTTP dentro de la red Docker; el tramo ngrok–agente va cifrado (enunciado §9). | — |
| Si la lista de orígenes CORS no es secreta, ¿por qué no subes el `.env`? | Porque en el mismo archivo están la contraseña de PostgreSQL y el token de ngrok, y porque es configuración **de cada equipo** (otro alumno o el profesor tendrá su token y su URL). En Git va `.env.example`, que documenta las variables sin valores reales. | `.gitignore`, `.env.example` |
| ¿Qué es CORS y qué cambiaste para Netlify? | El navegador bloquea que una web (Netlify) lea respuestas de otro origen (ngrok) si la API no lo autoriza. Añadí el origen exacto `https://adorable-zabaione-a69bde.netlify.app` a `CORS_ORIGINS` y recreé la API (`docker compose up -d api`; `restart` no relee el `.env`). CORS **no es autenticación**: cualquiera puede llamar a la API con curl; solo impide que otras webs la lean desde el navegador. | `fase10-tunel-ngrok.txt` |
| ¿Para qué sirven Netlify y ngrok? ¿Qué pasa si apago el PC? | Netlify aloja los archivos fijos del panel (Angular); ngrok es un túnel que da URL pública HTTPS a la API de mi PC. El móvil descarga el panel de Netlify y el panel pide los datos a ngrok. Si apago el PC o cierro el túnel, la web **carga** pero **sin datos** (el panel muestra el error). | `fase10-movil-netlify.png` |
| En tu prueba con una web falsa, la API respondió 200. ¿Entonces CORS no funciona? | Sí funciona: CORS no impide que la petición llegue ni que el servidor responda. Lo que hace es **no enviar** la cabecera `access-control-allow-origin` a un origen no autorizado, y entonces es el **navegador** quien impide que esa web lea la respuesta. curl no es un navegador, por eso ve los datos: CORS no es autenticación. | `fase10-tunel-ngrok.txt` |

### Fase 11 · Reproducción histórica
| Pregunta | 📘 Respuesta modelo (para estudiar) | Evidencia |
|---|---|---|
| ¿Qué pasaría si la reproducción escribiera en las mismas tablas que el live? | Los 96 eventos de Kamchatka ya estaban en public (histórico 2025): la idempotencia los ignoraría (mismo id + updated). Pero la **revisión sintética** (updated + 1 h, mag 4.3) es «más nueva» y **machacaría un terremoto real** con datos inventados; la comparación con 2025 (que cuenta `source='usgs-fdsn'`) perdería ese evento. Y si se reprodujera algo no cargado, inflaría las cifras. Por eso se aísla: esquema `replay` + topic `terremotos.replay` + grupo de consumidores propio. | `fase11-reproduccion.txt` |
| ¿Cómo aíslas la reproducción? | Topic propio (`terremotos.replay`), grupo de consumidores propio (`consumidor-replay`) y **esquema PostgreSQL propio** (`replay`, mismas tablas). Es el **mismo código** del consumidor: solo cambian variables de entorno (`KAFKA_TOPIC`, `DB_ESQUEMA`, `MODO_ESPERADO`). El `search_path` de PostgreSQL hace que las mismas consultas lean/escriban en `replay` (y pais/fecha sigan en public). Además, un mensaje con `mode` que no corresponde al topic va a cuarentena. | `compose.yaml`, `sql/02_reproduccion.sql` |
| ¿Qué selección reproduces y por qué? | La ventana temporal del M8,8 de Kamchatka (29/07/2025 23:24 UTC): de 1 h antes a 2 h después = 96 eventos reales M≥4 de **todo el mundo** (90 en la zona de Kamchatka y 6 en otras regiones), como habrían llegado en vivo. Es la Conclusión 1 de la memoria y garantiza actividad en la demostración. Ordenados por fecha original; 1 cada 2 s (~3 min). | `productor_replay.py` |
| ¿Cambias las fechas para que se vean? | No. Se conserva `event_time` original y se añade `replayed_at`. La API, en `mode=replay` y sin fechas, usa el intervalo de los eventos reproducidos (si no, el filtro de «últimas 24 h» de 2026 no mostraría nada). | API `/api/eventos?mode=replay` |
| ¿Cómo se ve que es una reproducción? | Selector «Datos» en el panel; banda naranja «REPRODUCCIÓN · No son actividad actual»; en cada terremoto, «REPRODUCIDO (UTC)»; la comparación con 2025 se desactiva (los datos ya son de 2025). | captura del panel |
| ¿Cómo demostraste que el consumidor reanuda sin duplicar? | Paré `consumidor-replay`, envié 99 mensajes y `kafka-consumer-groups.sh --describe` mostró LAG 99 (Kafka los guarda). Al arrancarlo, el LAG bajó a 0 empezando en el último offset confirmado (no desde 0) y los recuentos no cambiaron (96/97/0). Funciona porque el offset se confirma DESPUÉS de guardar y la base es idempotente. | `fase11-reproduccion.txt` |
| ¿Qué es el LAG? | Mensajes que hay en el topic y el grupo aún no ha confirmado: LOG-END-OFFSET − CURRENT-OFFSET, por partición. | ídem |
| Si cierro el túnel, ¿qué ve el usuario? ¿Y al reabrirlo? | Una banda roja «La API no responde: datos antiguos» con la hora de la última lectura correcta; el mapa y la tabla NO se borran. Al reabrir (misma URL, el plan gratuito da un dominio fijo) el refresco automático (60 s) vuelve a consultar y se recupera sin recargar. | `fase11-tunel-*.png` |
| ¿Por qué hay peticiones OPTIONS antes de cada GET? | Es el *preflight* de CORS: como el panel envía la cabecera `ngrok-skip-browser-warning`, el navegador pregunta antes a la API si lo permite. CORSMiddleware lo responde con 200. | `fase11-tunel-reabierto-ngrok.png` |

### Fase 12 · Complejidad, mediciones y costes
| Pregunta | 📘 Respuesta modelo (para estudiar) | Evidencia |
|---|---|---|
| ¿Por qué buscar un id que no existe es el peor caso para la lista y no para el diccionario? | La lista compara uno a uno: si el id existe, de media lo encuentra a mitad (N/2); si no existe, tiene que mirarlos todos (N) para estar segura. El diccionario calcula el hash del id y mira directamente en un «cajón»: exista o no, una sola mirada. Medido: lista 789 → 1 606 µs (el doble); diccionario ≈0,03 µs en los dos casos. | memoria §8.2 |
| ¿Qué significa O(N), O(1) y O(log N)? | Cómo crece el coste al crecer N. O(N): el doble de datos, el doble de tiempo (lista, tabla sin índice). O(1): no depende de N (diccionario, de media). O(log N): crece muy despacio; ×1 000 datos ≈ +10 pasos (B-tree de PostgreSQL, STRtree). | §8.2–8.5 |
| ¿Por qué el STRtree es más rápido si da el mismo resultado? | Compara primero rectángulos envolventes, que es muy barato, y solo hace la prueba exacta punto-en-polígono con los pocos países candidatos. La fuerza bruta la hace con los 177. Medido ≈8× y 8 000/8 000 resultados idénticos. | §8.3 |
| ¿Qué cuesta un índice? | Espacio (en la prueba, los dos índices ≈ lo mismo que la tabla: 162 frente a 181 MB), tiempo al crearlo (2,6 s con 3 M filas) y escrituras algo más lentas (eso no lo medimos). A cambio, buscar por id pasa de 61 ms a 0,03 ms. | §8.5 |
| ¿Qué pasaría con 100 millones de registros? | Una lista sería inviable (≈1,6 s por búsqueda). Un diccionario en memoria necesitaría ≈10 GB, así que mejor la PK de PostgreSQL. Sin índice, cada consulta tardaría ≈2 s; con índice, la búsqueda por id sigue en milisegundos. Propuesta: particionar por fecha, tablas de agregados por hora, más consumidores (uno por partición) y servidor dedicado. Son extrapolaciones lineales, no medidas. | §8.6 |
| ¿Por qué usaste datos sintéticos y cómo los separaste? | Para medir con 1 M y 3 M filas sin tenerlas reales. Ids `SINT-…`, en un esquema aparte `bench` que el script borra al acabar (DROP SCHEMA … CASCADE): nunca tocan el análisis real (enunciado §10). | `medir.py` |
| ¿El proyecto cuesta 0 € porque ngrok y Netlify son gratis? | No. El PC tiene que estar encendido 24 h (luz), hay hardware, ≈5,9 GB/mes de descarga y horas de desarrollo y mantenimiento. Las cuotas gratuitas solo eliminan la factura de esos servicios. | §8.8 |

### Fase 13 · Calidad y conclusiones
| Pregunta | 📘 Respuesta modelo (para estudiar) | Evidencia |
|---|---|---|
| ¿Qué dimensiones de calidad analizaste? | Las 6 del enunciado: completitud (% por campo), unicidad (0 versiones repetidas, filas = ids), validez (rangos, negativos, rechazos), consistencia (claves, días, el actual = la última versión), actualidad (61 s de mediana entre la actualización de USGS y nuestra descarga) y exactitud (no verificable: solo contrastamos `count` FDSN y STRtree frente a fuerza bruta). | memoria §5.4, `analisis/calidad.sql` |
| ¿Por qué el 76 % de los terremotos no tiene país? ¿Es un error? | No. El histórico es M ≥ 4 de todo el mundo y la mayoría ocurre en el mar (subducción). No inventamos país: «Sin país asignado», y siguen en todos los recuentos. | §5.4 nota 1 |
| ¿Por qué no rellenas la magnitud nula con 0? | Porque sería un valor que la fuente no da y cambiaría las medias y los recuentos por magnitud. Se conserva el nulo, se muestra «ND» y se cuenta aparte. | §5.1 |
| ¿Por qué dices que la mediana de 453 min de retraso es engañosa? | Porque incluye las cargas de golpe (primera descarga con 24 h hacia atrás y la recuperación tras la noche) y porque `ingested_at` es el de la última versión. Medido solo con el productor en marcha: 61 s. | §5.4 nota 2 |
| ¿Puedes asegurar que las magnitudes son exactas? | No. Que sea numérica y esté en rango no demuestra que sea exacta, y no tenemos otra fuente independiente. Además, USGS las revisa (un terremoto de Alaska tuvo 33 versiones) y hay escalas distintas. | §5.4 nota 3 |
| Conclusión 2: ¿EE. UU. tiembla más que el resto del mundo? | No se puede decir. Sin filtro es el 75 % del feed, pero con M ≥ 4 baja al 3,3 % (y al 0,4 % en 2025): mide la densidad de sensores. Por eso hay que comparar siempre con el mismo umbral de magnitud. | §7, `fase13-conclusion2.txt` |
| ¿Estaba completo el feed el día de la Conclusión 3? | No del todo. El 31/10 dio 25 terremotos M ≥ 4; tres días después, nuestra base tenía 27 (2 llegaron después por el propio feed) y el catálogo oficial, 28 (uno nunca apareció en el feed). Con 28 la conclusión se mantiene: −44,2 % frente a la media, pero 27 días de 2025 (7,4 %) tuvieron 28 o menos. Lo comprobé con `contrastar_fdsn.py`. | `fase13-contraste-fdsn.txt` |
