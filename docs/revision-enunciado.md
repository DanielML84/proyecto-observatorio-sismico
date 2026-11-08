# Revisión del enunciado punto por punto

> **Qué es:** cada requisito del documento del profesor (*Proyecto observatorio actividad sismica.docx*, revisión 2)
> cruzado con **dónde se cumple** en el proyecto y **con qué evidencia**. Preparada por Claude el 05/11/2026,
> leyendo el código, la memoria y las evidencias. **Se revisa con Daniel el domingo 08/11.**
>
> Leyenda: ✅ cumplido con evidencia · ⚠️ cumplido a medias o mejorable · ❌ falta · ⏳ pendiente (depende de Daniel) · ℹ️ nota para la defensa

## Resumen

| ✅ Cumplidos | ⚠️ Mejorables | ❌ Faltan | ⏳ Pendientes |
|:---:|:---:|:---:|:---:|
| 102 | 1 | 0 | 1 |

104 requisitos del enunciado revisados (contando como uno cada fila de las tablas de abajo).
Además, el 08/11 se revisaron enteras la **guía de entregables** y la **FAQ del alumnado** (apartados al final):
1 punto nuevo resuelto (procedimiento de la defensa) y **2 sin comprobar (❓)**: el arranque desde un entorno limpio y el acceso al repositorio.

## 🔧 Lo que hay que resolver (por prioridad)

| # | Estado | Requisito (sección) | Qué pasa | Propuesta | Tiempo |
|---|---|---|---|---|---|
| 1 | ✅ (08/11) | §5 · Documentar la limitación de eventos eliminados, fusionados o revisados cuando ya están fuera del feed, y que «no aparecer en la siguiente ventana» no es «USGS lo ha eliminado» | No hay ningún párrafo sobre esto en la memoria ni en el README (búsqueda de «eliminad», «fusionad», «desaparec», «reconcil»: 0 resultados) | Añadir un párrafo corto en la memoria §3 o §5. Se puede citar el caso real de la Conclusión 3 (`us7000tumn`, nunca apareció en el feed) | 10–15 min |
| 2 | ⚠️ | §12 · «Análisis con al menos tres conclusiones **y capturas de los filtros usados**» | Las 3 conclusiones (memoria §7) citan evidencias `.txt`, pero ninguna enlaza una captura del panel con sus filtros. Hay capturas del panel (`fase9-*.png`), pero no están ligadas a cada conclusión | Hacer una captura por conclusión con sus filtros y citarla en §7. **Encaja con la visita guiada al panel del 09/11.** Ojo: el panel filtra por fecha, magnitud y país, no por rectángulo lat/lon, así que para la Conclusión 1 (zona de Kamchatka) habrá que ver si sirve `fase9-bloque4-kamchatka.png` | 30 min |
| 3 | ✅ (08/11, documentado) | §9 · «Dependencias fijadas» | Todo está fijado (Kafka `4.1.2`, `requirements.txt` con `==`, `package-lock.json`) **salvo el túnel**: `ngrok/ngrok:latest` en `compose.yaml` | Fijar la versión de la imagen de ngrok, o anotarlo como limitación en la memoria | 10 min |
| 4 | ✅ (08/11) | §4.1 · Documentar respuesta, tipos, unidades, campos opcionales, frecuencia, errores y latencia | Está todo, pero **repartido**: tipos y unidades en §2, estructura y campos poco informados en §4, frecuencia en §3, latencia en §5.4 (Actualidad), errores en §3/§5.4 | Añadir en §4 una línea que remita a cada sitio, para que el profesor lo encuentre de un vistazo | 5 min |
| 5 | ⏳ | §12 · Explicación individual del flujo completo y de una decisión técnica propia | Depende de Daniel | Semana de estudio (bloques 1–12) y simulacro del 17/11 | — |
| 6 | ✅ (08/11) | Guía §3.2 · Procedimiento breve para activar el sistema en la defensa | Los pasos estaban repartidos por el README | Añadida la sección «Activar el sistema para la defensa» al principio del README (5 pasos con qué hay que ver) | — |
| 7 | ❓ | Guía (lista final) y FAQ 35 · «El README permite arrancar el sistema **desde un entorno limpio**» | **Nunca se ha probado** clonando el repositorio desde cero | Probarlo en el bloque 10 (sáb. 14/11), en otra carpeta y con otro nombre de proyecto (`-p`), y con el sistema principal parado, para no tocar los volúmenes ni chocar con los puertos 8000 y 4040 | 45 min |
| 8 | ❓ | Guía (lista final) · «El profesor puede acceder al repositorio» | No se ha podido comprobar desde aquí | Daniel: abrir el repositorio en una ventana de incógnito sin iniciar sesión | 1 min |

**Orden de la casa (resuelto el 08/11):** en el roadmap estaban sin marcar «Explorar el catálogo de países:
unicidad de `ADM0_A3`» y «Anotar hallazgos», pero están hechos (memoria §3bis: 177/177; memoria §4). `docs/spec.md` y
`docs/plan.md` nunca se crearon: eran parte del método propio (bitácora sesión 1), el enunciado no los pide.

---

## Revisión completa

### §2 · Arquitectura obligatoria

| Requisito | Dónde se cumple | Evidencia | |
|---|---|---|---|
| Productor Python + aiokafka | `backend/src/productor.py`, `aiokafka==0.12.0` | `fase3-pipeline-python.txt` | ✅ |
| Kafka como broker | servicio `kafka` (`apache/kafka:4.1.2`, KRaft) | `fase3-*.png` | ✅ |
| Consumidor Python + aiokafka: validación, limpieza, enriquecimiento y escritura | `consumidor.py`, `validacion.py`, `geografia.py`, `db.py` | `fase5-faq12-idempotencia.txt`, `fase6-paises.txt` | ✅ |
| PostgreSQL: datos preparados, originales y estado | `sql/01_esquema.sql` (`evento_version.raw`, `version_publicada`) | `fase4-postgres-esquema.txt` | ✅ |
| API FastAPI de consulta | `backend/src/api.py` | memoria §7bis, `/docs` | ✅ |
| Túnel ngrok (equipo o contenedor) | servicio `tunel` en contenedor (D43) | `fase10-tunel-ngrok.txt` | ✅ |
| Panel Angular + Leaflet en Netlify | `frontend/`, `netlify.toml`, `_redirects` | `fase10-movil-netlify.png` | ✅ |
| 5 servicios separados en Docker Compose, en el equipo del alumno | `compose.yaml`: `productor`, `kafka`, `consumidor`, `postgres`, `api` | README §3 | ✅ |
| Arranque conjunto con `docker compose up --build -d` | README §3 | — | ✅ |
| Imagen reproducible por servicio Python (se puede compartir) | `backend/Dockerfile` (`python:3.12-slim`) + `requirements.txt` con `==`; imagen común `observatorio-backend` | — | ✅ |
| Comprobaciones de salud y reintentos | healthchecks en `kafka`, `postgres`, `productor` (latido) y `api`; `depends_on` con condiciones; `db.conectar` reintenta 30 × 2 s; `restart: unless-stopped` | — | ✅ ℹ️ |
| SPA compilada y publicada; el navegador consulta la API por ngrok | `config.json` → URL de ngrok | `fase10-*` | ✅ |
| Kafka y PostgreSQL no se publican por el túnel | `tunel` apunta solo a `http://api:8000`; sin `ports` en Kafka ni PostgreSQL | `docker compose ps` | ✅ |
| Productor y consumidor funcionan aunque el panel esté cerrado | Son servicios independientes del panel | `recuperacion-parada-nocturna.txt` | ✅ |

ℹ️ Los consumidores no tienen healthcheck propio. Si el profesor pregunta: dependen de `kafka-init` (terminado) y de
`postgres` (sano), reintentan la conexión a la base y Docker los reinicia si fallan.

### §3 · Material de partida

| Requisito | Dónde se cumple | Evidencia | |
|---|---|---|---|
| Implementar pipeline, persistencia, API, filtros, gráficos y métricas | Todo el repositorio | memoria §1–§10 | ✅ |
| Documentar resultados en memoria o notebook | `docs/memoria.md` + `analisis/01_exploracion_feed.ipynb` | — | ✅ |
| La muestra ficticia no sustituye a los datos reales | Panel con datos reales desde Netlify | `fase10-movil-netlify.png` (224 eventos) | ✅ |
| Material reutilizado distinguible del propio | `docs/material-profesor/` sin modificar, commit `5c052ff` | memoria §1 | ✅ |

### §4.1 · Datos recientes

| Requisito | Dónde se cumple | Evidencia | |
|---|---|---|---|
| GET a `all_day.geojson` cada ~60 s | `productor.py`, `INTERVALO_S: 60` | `consulta_ingesta`, logs | ✅ |
| Entender que es una ventana móvil de 24 h con revisiones | memoria §3, §5.2bis | `recuperacion-parada-nocturna.txt` | ✅ |
| Identificar `id`, `time`, `updated`, `mag`, `magType`, `type`, `place`, `coordinates` | memoria §2 (diccionario) | — | ✅ |
| Documentar respuesta, tipos, unidades, opcionales, frecuencia, errores y latencia | memoria §4 (índice a §2, §3, §5.4 y D20) | notebook | ✅ |
| Filtrar `type == "earthquake"` y conservar el motivo | `validacion.py` línea 70; tabla `cuarentena` | `type=explosion` 11 y `type=quarry blast` 12 reales (consulta del 04/11) | ✅ |

### §4.2 · Histórico

| Requisito | Dónde se cumple | Evidencia | |
|---|---|---|---|
| Año completo: 2025, mundial, M ≥ 4, earthquake | `historico_descargar.py` | memoria §3 (18.302 eventos) | ✅ |
| Dividir en meses; subdividir si > 20.000; no truncar | `count` previo y división automática | memoria §3: `count` = descargados en los 12 meses | ✅ |
| Deduplicar los eventos de las fronteras entre intervalos | `historico_cargar.py` (se queda el `updated` mayor) | caso sintético probado; 0 repetidos reales | ✅ |
| Guardar consultas, fecha de extracción y número de registros | `data/historico/manifest.json` + `consulta_ingesta` | tabla de memoria §3 | ✅ |
| Descargar una vez y reutilizar | reutiliza los archivos existentes | README §4 | ✅ |
| Explicar que el histórico es una instantánea | memoria §3 | — | ✅ |

### §4.3 · Catálogo geográfico

| Requisito | Dónde se cumple | Evidencia | |
|---|---|---|---|
| Usar la copia de Natural Earth entregada | `frontend/public/datos/paises.geojson`, montado en solo lectura | SHA-256 verificado (memoria §3) | ✅ |
| Punto en polígono; no usar `place` | `geografia.py` (Shapely, STRtree) | `fase6-paises.txt` | ✅ |
| Coordenadas compatibles (WGS84) | memoria §3bis | — | ✅ |
| Documentar la regla de frontera y de varias coincidencias | memoria §3bis: `covered_by`; desempate alfabético | 0 coincidencias múltiples | ✅ |
| `ADM0_A3` como clave tras comprobar unicidad; no asumir ISO | memoria §3bis (177/177) y §2.3 | — | ✅ |
| «Sin país asignado» sin tratarlo como error ni asignar el más cercano | `country_id` NULL; `LEFT JOIN` en la API | memoria §3bis, prueba «Evento marítimo» | ✅ |

### §5 · Extracción e ingesta

| Requisito | Dónde se cumple | Evidencia | |
|---|---|---|---|
| Variables de entorno para Kafka, topic y frecuencia | `compose.yaml` (`KAFKA_BOOTSTRAP_SERVERS`, `KAFKA_TOPIC`, `INTERVALO_S`) | — | ✅ |
| Conservar el GeoJSON original y metadatos; retención; registrar consultas | `data/raw/*.geojson.gz` (24 h, solo si cambian los `features`); `consulta_ingesta` | logs `original=…` | ✅ |
| Comparar `id` + `updated` con estado persistente | `productor.py` líneas 143–145; `version_publicada` | logs `estado cargado: N` | ✅ |
| Clave Kafka = id; mensaje con `source`, `ingested_at`, `mode` y el evento original | `mensajes.py`, `docs/contrato-mensaje.md` | — | ✅ |
| Esperar confirmación de Kafka antes de marcar; el consumidor tolera el reenvío | `send_and_wait` → `marcar_publicada`; consumidor idempotente | `fase5-faq12-idempotencia.txt` | ✅ |
| Timeout, 429/5xx, espera progresiva, JSON roto; no borrar el estado válido | `ErrorReintentable`, esperas 2/4/8 s, `consulta_ingesta` | memoria §5.4 (1 fallo DNS recuperado) | ✅ |
| Documentar la limitación de eliminados/fusionados/revisados fuera del feed | memoria §5.2bis («Limitación: lo que sale de la ventana no se reconcilia») | — | ✅ |
| Explicar cómo recuperar el hueco tras una parada > 24 h | memoria §3 (`updatedafter`), §5.2bis, D32; README §9 | `defensa.md` | ✅ |

### §6 · Calidad y transformación

| Requisito | Dónde se cumple | Evidencia | |
|---|---|---|---|
| Reglas explícitas de validación y transformación en el consumidor | `validacion.py` (15 reglas con motivo fijo) | memoria §5.1 | ✅ |
| Análisis con código o consultas, resultados antes/después y decisiones | memoria §5.4 + `analisis/calidad.sql` | `fase13-calidad.txt`; tabla «Antes → acción → después» | ✅ |
| Las 6 dimensiones (o justificar las que no se puedan verificar) | memoria §5.4 | `fase13-calidad.txt` | ✅ |
| No rellenar nulos con cero | magnitud NULL → «ND» | prueba «Magnitud nula» | ✅ |
| Magnitud y profundidad negativas estudiadas, no rechazadas | `validacion.py` líneas 88–96; D3; FAQ de USGS en memoria §4 | 7 y 9 negativas conservadas | ✅ |
| Cuarentena con motivo y referencia al original | `cuarentena`: `motivo`, `raw`, `kafka_topic`/`partition`/`offset` con UNIQUE | consulta del 04/11 | ✅ |
| Casos de prueba dañados separados e identificados | prefijo `PRUEBA-`, `source='prueba-…'`; la API los excluye | `PRUEBA-LAT145`, `PRUEBA-EXPLOSION` | ✅ |
| Fechas a UTC; separar ocurrencia y procesamiento | `event_time` frente a `ingested_at` | memoria §2 | ✅ |
| Registrar qué transformaciones cambian los datos y cuántos registros afectan | memoria §5.1 y tabla «Antes → acción → después» (§5.4) | — | ✅ |

### §7 · Integración y modelado

| Requisito | Dónde se cumple | Evidencia | |
|---|---|---|---|
| Modelo conceptual, lógico y físico | memoria §6, `sql/01_esquema.sql` | — | ✅ |
| Grano, claves, relaciones e índices explicados | memoria §2 y §6 | — | ✅ |
| Integración de terremotos con el catálogo geográfico | `country_id` → tabla `pais` | `fase6-paises.txt` | ✅ |
| Actualizar el estado solo si la versión es más reciente; conservar la versión recibida | UPSERT con `WHERE updated_ms <`; `evento_version` con `ON CONFLICT DO NOTHING` | prueba «versión antigua» | ✅ |
| Escritura transaccional y offset después de escribir | `db.py` (transacción) + `consumidor.py` línea 81 | `fase11-reproduccion.txt` (LAG 99 → 0) | ✅ |
| Repetir un mensaje no aumenta el recuento (UNIQUE + upsert) | claves primarias y UNIQUE | prueba «Reenviar la misma versión» | ✅ |
| Al menos una vez + escritura idempotente; el orden por clave no sustituye la comparación | `consumidor.py` docstring; contrato del mensaje | — | ✅ |

### §8 · Análisis y panel

| Requisito | Dónde se cumple | Evidencia | |
|---|---|---|---|
| El panel consulta nuestra API, no USGS | `api.service.ts` | memoria §7bis | ✅ |
| Mapa: fondo, fronteras, círculos, ficha; tamaño por magnitud, color por profundidad, leyenda, nulos | `app.component` (base del profesor ampliada) | `fase1-mapa-demo.png`, `fase9-bloque1-normal.png` | ✅ |
| Recuentos por país/subregión y ventanas de 1 h UTC por tiempo del evento, con «Sin país asignado» | `/api/estadisticas` + `estadisticas/` | memoria §7bis (sumas = 218) | ✅ |
| Distribuciones de magnitud y profundidad con registros sin valor | `estadisticas/` | `fase9-bloque4-estadisticas.png` | ✅ |
| Comparación histórica; denominador con días a cero; aviso de periodo incompleto | `/api/estadisticas` (`nota` sobre retrasos de USGS, `periodo_cubierto`); `comparacion-historica` | `fase9-bloque5-comparacion.png` | ✅ |
| Filtros de fecha, magnitud y país aplicados a mapa y gráficos | `filtros/`, `api.service.ts` | `fase9-bloque2-filtros.png` | ✅ |
| Estado del sistema: último acceso, última ingesta, periodo, avisos | `estado-sistema/` | `fase9-bloque1-api-caida.png`, `fase11-tunel-cerrado.png` | ✅ |
| Tabla consultable de eventos | `tabla-eventos/` | `fase9-bloque3-tabla.png` | ✅ |
| Agregaciones desde el estado actual (no contar mensajes) | `api.py` consulta `evento_actual` | — | ✅ |
| Al menos 3 conclusiones con cifras, filtros y periodo; muestras equivalentes; no predicción | memoria §7 | `fase7-historico.txt`, `fase13-conclusion2.txt`, `fase8-…`, `fase13-contraste-fdsn.txt` | ✅ |

### §9 · Despliegue y funcionamiento

| Requisito | Dónde se cumple | Evidencia | |
|---|---|---|---|
| `compose.yaml`, inicialización de la base y `.env.example` sin credenciales | `sql/` en `docker-entrypoint-initdb.d`; `.env.example` con `CAMBIAR_EN_LOCAL` | — | ✅ |
| Dependencias fijadas | Python con `==`, `package-lock.json`, Kafka `4.1.2`, PostgreSQL `17-alpine` | README §1; memoria D43 (huella de la imagen de ngrok) | ✅ (ngrok `latest` documentado con su huella) |
| Volúmenes persistentes y retención limitada de Kafka | `kafka-data`, `pg-data`; 7 días o 512 MB | memoria §2, README §9 | ✅ |
| Nombres de servicio dentro de Compose (no `localhost`) | `kafka:9092`, `postgres`, `api:8000` | — | ✅ |
| Exponer solo la API (`127.0.0.1:8000:8000`) | `compose.yaml` | `docker compose ps` | ✅ |
| ngrok en contenedor con `http://api:8000` | servicio `tunel` | — | ✅ |
| Uvicorn en `0.0.0.0:8000` | `compose.yaml`, servicio `api` | — | ✅ |
| Sin certificado en FastAPI; Angular usa la URL HTTPS | `config.json` con `https://…ngrok-free.dev` | — | ✅ |
| Netlify con la URL de ngrok en `config.json` | `frontend/public/config.json` | — | ✅ |
| CORS: origen exacto de Netlify y de desarrollo, OPTIONS, `ngrok-skip-browser-warning` | `api.py` líneas 38–41; `CORS_ORIGINS` en `.env` | prueba con curl (bitácora sesión 5) | ✅ |
| No exponer administración, secretos, base de datos ni broker; authtoken fuera de Angular y Git | token solo en `.env` (en `.gitignore`) | README §7 | ✅ |
| El mapa consulta la API cada 60 s | `config.json` `refreshMs: 60000` | memoria §7bis (+0, +60,1, +120,1 s) | ✅ |
| Limitación: activo durante la demo; tratamiento del error | README §7, §9 | `fase11-tunel-*.png` | ✅ |

### §10 · Complejidad, rendimiento y costes

| Requisito | Dónde se cumple | Evidencia | |
|---|---|---|---|
| Justificar 3 estructuras: búsqueda por id, integración geográfica, ventanas; coste medio y peor caso | memoria §8.2–8.4 | `data/mediciones/*.json` | ✅ |
| Tiempo y memoria con 3 tamaños; equipo y procedimiento | memoria §8.1–8.5, `medir.py` | — | ✅ |
| Datos sintéticos marcados y fuera del análisis | esquema `bench`, borrado al terminar | memoria §8.5 | ✅ |
| Secuencial frente a diccionario; sin/con índice; 100 millones | memoria §8.2, §8.5, §8.6 | — | ✅ |
| Costes: hardware, luz, almacenamiento, transferencia, mantenimiento, desarrollo; supuestos; escalado; ROI no inventado | memoria §8.8 y §8.6 | — | ✅ |

### §11 · Pruebas de aceptación y reproducción

| Requisito | Dónde se cumple | Evidencia | |
|---|---|---|---|
| Las 11 pruebas con su resultado esperado | memoria §9 (las 11 filas) | `fase5-…`, `fase9-…`, `fase11-…` | ✅ |
| Reproducción acelerada ordenada por fecha | `productor_replay.py` (Kamchatka, 1 cada 2 s) | `fase11-reproduccion.txt` | ✅ |
| Tiempo original + tiempo de reproducción | `event_time` + `replayed_at` | ídem | ✅ |
| Topic y esquema separados | `terremotos.replay` → esquema `replay` | ídem | ✅ |
| Etiqueta «REPRODUCCIÓN» | banda naranja en el panel | `fase11-panel-reproduccion.png` | ✅ |
| Reutiliza el procesamiento del consumidor | mismo código (`consumidor-replay`) | `compose.yaml` | ✅ |
| Casos controlados de duplicado y revisión | casos a), b) y c) | `fase11-reproduccion.txt` | ✅ |

### §12 · Entregables

| Requisito | Dónde se cumple | Evidencia | |
|---|---|---|---|
| Repositorio con código, Dockerfile, compose, dependencias, `.env.example` e instrucciones | GitHub `DanielML84/proyecto-observatorio-sismico`, README | — | ✅ |
| URL del panel y procedimiento para activar backend y túnel | README (tabla inicial, §3 y §7) | — | ✅ |
| Diccionario de datos y registro de consultas y procedencia | memoria §2 y §3 | — | ✅ |
| Apartado de calidad con código, antes/después, decisiones y registros de ejemplo | memoria §5 | `fase13-calidad.txt` | ✅ |
| Modelo, SQL y justificación de índices | memoria §6, `sql/` | — | ✅ |
| Tres conclusiones **y capturas de los filtros usados** | memoria §7 | — | ⚠️ (ver #2) |
| Complejidad, mediciones, costes y mejoras | memoria §8 | — | ✅ |
| Evidencias de pruebas y reproducción | memoria §9 y §10, `docs/evidencias/` | — | ✅ |
| Explicación individual del flujo y de una decisión propia | — | — | ⏳ |
| Sin `node_modules`, credenciales, volúmenes ni grandes descargas en Git; datos regenerables | `.gitignore` (`node_modules/`, `.env`, `data/raw/`…); 121 archivos en Git, el mayor 1,5 MB (muestra de enero de 2025) | README §4 | ✅ |

### §13 · Evaluación (dónde está cada criterio de la rúbrica)

| Criterio | Dónde mirar |
|---|---|
| Extracción | memoria §3, §4 · `productor.py`, `historico_*.py` |
| Calidad | memoria §5 · `validacion.py`, `analisis/calidad.sql` |
| Modelado | memoria §3bis, §6 · `sql/01_esquema.sql`, `db.py` |
| Análisis | memoria §7, §7bis · panel |
| Reflexión | memoria §8 y limitaciones de cada sección |

---

## Guía de entregables (revisada entera el 08/11)

La guía dice que «no añade nuevas tareas ni modifica la rúbrica». Cruce de sus apartados:

| Apartado | Dónde se cumple | |
|---|---|---|
| 1.1 Código de los componentes; material reutilizado distinguible | `backend/src/`, `frontend/`; `docs/material-profesor/` y commit `5c052ff` | ✅ |
| 1.2 Dockerfile y `compose.yaml`; `up --build -d`; pasos previos; persistencia, salud y reintentos | README §2–§4; `compose.yaml` | ✅ |
| 1.3 Dependencias con versiones; `.env.example` con nombres coherentes con el código | `requirements.txt`, `package-lock.json`, `.env.example` (las variables de Kafka van en `compose.yaml`) | ✅ |
| 1.4 README con los 9 puntos; no subir secretos ni descargas grandes | README §1–§9; `.gitignore` | ✅ |
| 2.1 Objetivo, flujo y decisiones de alcance | memoria §1 | ✅ |
| 2.2 Diccionario con significado, tipo, unidades y ausencias | memoria §2 | ✅ |
| 2.3 Procedencia: URLs, parámetros, nº de registros y fecha de extracción | memoria §3 | ✅ |
| 2.4 Calidad: comprobaciones, consultas, resultados, decisiones; denominador; sintéticos separados | memoria §5.4 (denominador: terremotos reales) | ✅ |
| 2.5 Modelo conceptual/lógico/físico; grano; SQL enlazado; índices justificados con medición | memoria §6, §8.5; `sql/` | ✅ |
| 2.6 Tres conclusiones con periodo, ámbito, filtros y denominador **y capturas con los filtros** | memoria §7 | ⚠️ (= hueco 2) |
| 2.7 Complejidad, 3 tamaños, costes medidos/supuestos, mejoras ligadas a problemas | memoria §8 (§8.6 propuesta de escalado) | ✅ |
| 2.8 Pruebas: esperado, observado, evidencia y cómo repetirlas | memoria §9; README §8 | ✅ |
| 2.9 Reproducción: selección, velocidad, separación, «REPRODUCCIÓN», resultados | memoria §10; `fase11-reproduccion.txt` | ✅ |
| 3.1 URL de Netlify, abierta desde otro dispositivo | README; `fase10-movil-netlify.png` | ✅ |
| 3.2 Procedimiento breve para la defensa | README, sección «Activar el sistema para la defensa» (08/11) | ✅ |
| 3.3 Explicación individual | — | ⏳ |
| Lista final · acceso al repositorio | — | ❓ (ver #8) |
| Lista final · arrancar desde un entorno limpio | — | ❓ (ver #7) |

## FAQ del alumnado (revisada entera el 08/11)

La FAQ dice que «aclara el enunciado: no añade requisitos». Lo que concreta, y dónde está:

| FAQ | Qué aclara | Dónde se cumple | |
|---|---|---|---|
| 8 · 10 · 11 | Ventana móvil; decisiones del productor; estado que sobrevive a reinicios; Kafka separa ritmos | `productor.py`, `version_publicada`; bloque 3 | ✅ |
| 12 · 13 · 14 | Secuencia de duplicados y revisiones; orden validar → transacción → offset; offset ≠ id | `fase5-faq12-idempotencia.txt`; `consumidor.py` | ✅ |
| 15 | No borrar lo que sale del feed; explicar la limitación de retiradas y fusiones | memoria §5.2bis (añadido el 08/11) | ✅ |
| 16 | Tabla de casos de limpieza (nulos, negativos, lat 145, tipos, UTC) | `validacion.py`; memoria §5.1 | ✅ |
| 16 · contrato | La magnitud nula se excluye de los filtros **y se cuenta aparte** | API `sin_valor.magnitud_excluidos_por_filtro` (D31) | ✅ |
| 17 | Calidad en la memoria; denominador; actualidad con la salvedad de las revisiones; exactitud no verificable | memoria §5.4 (notas 2 y 3) | ✅ |
| 19 · 20 | País por punto en polígono; modelo orientativo y claves | memoria §3bis, §6 | ✅ |
| 21 | Histórico: una carga inicial, documentar Kafka o batch | D29 (por Kafka). `contrato-mensaje.md` decía «se decidirá»: **actualizado el 08/11** | ✅ |
| 22 | Ventanas fijas `[hh:00, hh+1:00)` por hora de ocurrencia, desde `evento_actual` | `api.py` líneas 244–252 | ✅ |
| 23 | Media con días a cero; ND si la media es 0; mismo filtro M ≥ 4 en los dos periodos | memoria §7, §7bis | ✅ |
| 25 · 26 · contrato | El panel usa nuestra API; `apiUrl` sin `/api`; `start` inclusivo, `end` exclusivo; `truncated`, total y paginación | `api.py` (líneas 70, 128–169); `config.json` | ✅ |
| 28 · 29 · 30 | Nombres de servicio; ngrok `http://api:8000`; CORS exacto + OPTIONS + cabecera de ngrok | `compose.yaml`; `api.py` líneas 38–41 | ✅ |
| 31 | Distinguir última consulta del panel, generación y última ingesta | `estado-sistema/`; `generated` / `last_ingestion` | ✅ |
| 32 | Replay aislado, «REPRODUCCIÓN», sin cambiar fechas, consultando el intervalo histórico | memoria §10; el panel en modo replay usa el intervalo reproducido | ✅ |
| 33 | Complejidad, 3 tamaños, costes con supuestos explicados | memoria §8 | ✅ |
| 35 | Lista previa a la entrega | Todo ✅ salvo «arrancan siguiendo mis instrucciones» (❓, ver #7) y la explicación individual (⏳) | ⚠️ |
