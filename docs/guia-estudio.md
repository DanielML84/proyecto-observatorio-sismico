# Guía de estudio · Observatorio de actividad sísmica

> **Cómo usarla.** Un bloque al día, 1,5–2 h, en sesiones de 45 min con descanso. Tacha ☐ → ☒ al terminar.
> En cada bloque: **🎯 objetivo** → **📂 leer** (en ese orden) → **🔎 buscar** (comandos de terminal) →
> **🧪 hacer** (ejecutarlo de verdad) → **❓ autoevaluarte** en voz alta, **sin mirar**; después compara con
> [`defensa.md`](defensa.md). Si una respuesta no te sale, márcala con ⚠️ y repásala el día de colchón.
> Los comandos 🔎 son de PowerShell, desde la carpeta del proyecto.

## Calendario (entrega: miércoles 18/11, antes de las 00:00)

| ☐ | Día | Bloque | Tiempo |
|---|---|---|---|
| ☒ | Lun 02/11 (tarde) → hecho Mar 03/11 | 1 · Visión general y arrancar/parar | 1,5 h |
| ☒ | Mar 03/11 (tarde) | 2 · Productor y mensaje + **tarea: re-descarga FDSN (Conclusión 3)** | 2 h |
| ☐ | Mié 04/11 | 3 · Kafka | 2 h |
| — | Jue 05/11 | *(niños: descanso)* | — |
| ☐ | Vie 06/11 (tarde) | 4 · Consumidor, validación y cuarentena | 1,5 h |
| ☐ | Sáb 07/11 | 5 · PostgreSQL: modelo e idempotencia | 2 h |
| ☐ | Dom 08/11 | 🔁 Colchón: repasar los ⚠️ de los bloques 1–5 | 1 h |
| ☐ | Lun 09/11 (tarde) | 6 · Integración geográfica | 1,5 h |
| ☐ | Mar 10/11 (tarde) | 7 · Histórico, comparación y conclusiones | 2 h |
| ☐ | Mié 11/11 | 8 · API y CORS | 2 h |
| — | Jue 12/11 | *(niños: descanso)* | — |
| ☐ | Vie 13/11 (tarde) | 9 · Panel y despliegue (ngrok, Netlify) | 1,5 h |
| ☐ | Sáb 14/11 | 10 · Reproducción y pruebas de aceptación | 2 h |
| ☐ | Dom 15/11 | 🔁 Colchón: repasar los ⚠️ de los bloques 6–10 | 1 h |
| ☐ | Lun 16/11 (tarde) | 11 · Calidad, complejidad y costes | 2 h |
| ☐ | Mar 17/11 (tarde) | 12 · Simulacro de defensa | 1,5 h |
| ☐ | Mié 18/11 | ✅ Comprobación final y **entrega** | 1 h |

## El sistema en una imagen

```text
 USGS feed (24 h, cada 60 s)            USGS FDSN (2025, una vez)
        │                                      │
   [productor] ── solo novedades (id, updated) ─┤ historico_descargar / historico_cargar
        │  mensaje JSON, clave = id
        ▼
   [Kafka] topic terremotos.live (3 particiones)        topic terremotos.replay ◄── [productor-replay]
        │                                                        │
   [consumidor] validar → país → guardar → confirmar offset   [consumidor-replay] (mismo código)
        │                                                        │
   [PostgreSQL] esquema public                               esquema replay
        │
   [API FastAPI] /api/eventos · /api/estadisticas · /api/salud   (?mode=replay)
        │
   [ngrok] URL pública HTTPS  ──►  [panel Angular en Netlify]  ◄── navegador del usuario
```

---

## Bloque 1 · Visión general y arrancar/parar ☒
- 🎯 Contar en 1 minuto qué hace el sistema y por qué cada pieza.
- 📂 [`README.md`](../README.md) (entero) · [memoria §1](memoria.md) · [`compose.yaml`](../compose.yaml) (solo los comentarios de cada servicio).
- 🔎 `Select-String -Path compose.yaml -Pattern "^  [a-z-]+:$"` → lista de servicios.
- 🧪 `docker compose --profile tunel stop` → `docker compose --profile tunel up -d` → `docker compose ps` → abrir el panel de Netlify.
- ❓ ¿Cuáles son los 5 servicios obligatorios? ¿Para qué sirve `kafka-init`? ¿Qué se pierde con `down -v` y qué no con `stop`? ¿Por qué una parada < 24 h no pierde terremotos?

## Bloque 2 · Productor y mensaje ☒
- 🎯 Explicar cómo decide el productor qué publicar y en qué formato.
- 📂 [`backend/src/productor.py`](../backend/src/productor.py) · [`mensajes.py`](../backend/src/mensajes.py) · [`contrato-mensaje.md`](contrato-mensaje.md) · memoria §3.
- 🔎 `Select-String -Path backend\src\productor.py -Pattern "send_and_wait|marcar_publicada|ErrorReintentable|latido"`
- 🧪 `docker compose logs productor --tail 10` · consulta de `consulta_ingesta` en [`chuleta-comandos.md`](chuleta-comandos.md).
- ❓ ¿Por qué se marca como publicada **después** de que Kafka confirme? ¿Qué es un error reintentable y uno definitivo? ¿Dónde guarda el productor su «memoria» al reiniciarse? ¿Por qué se hashean solo los `features` y no la respuesta entera?
- 📌 **Tarea del 03/11 (con Claude):** volver a descargar del catálogo FDSN el periodo 30/10 09:28 → 31/10 09:28 UTC (M ≥ 4) y comparar con los 25 del feed (Conclusión 3).

## Bloque 3 · Kafka ☐
- 🎯 Entender topic, partición, clave, offset, grupo de consumidores y LAG.
- 📂 `compose.yaml` (servicios `kafka` y `kafka-init`) · memoria Anexo A (decisiones de Kafka) · [`fase11-reproduccion.txt`](evidencias/fase11-reproduccion.txt) (parte del LAG).
- 🔎 `Select-String -Path compose.yaml -Pattern "KAFKA_"`
- 🧪 `docker compose exec kafka /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server kafka:9092 --describe --group consumidor-observatorio`
- ❓ ¿Por qué la clave del mensaje es el `id`? ¿Kafka elimina duplicados? (no). ¿Qué es el LAG? ¿Por qué Kafka no se publica en el host? ¿Qué pasa con los mensajes si el consumidor está parado?

## Bloque 4 · Consumidor, validación y cuarentena ☐
- 🎯 Recorrer un mensaje desde que llega hasta que se guarda o va a cuarentena.
- 📂 [`consumidor.py`](../backend/src/consumidor.py) · [`validacion.py`](../backend/src/validacion.py) · memoria §5.1–5.3.
- 🔎 `Select-String -Path backend\src\validacion.py -Pattern "Rechazo\("` → todas las reglas.
- 🧪 `docker compose logs consumidor --tail 10` · `SELECT tipo, motivo, COUNT(*) FROM cuarentena GROUP BY 1, 2;`
- ❓ ¿Diferencia entre `invalido` y `excluido`? ¿Por qué no se rechaza una profundidad negativa? ¿Por qué el offset se confirma **después** de guardar? («al menos una vez»). ¿Qué hace `MODO_ESPERADO`?

## Bloque 5 · PostgreSQL: modelo e idempotencia ☐
- 🎯 Explicar las tablas, su grano y cómo se evita duplicar.
- 📂 [`sql/01_esquema.sql`](../sql/01_esquema.sql) · [`db.py`](../backend/src/db.py) · memoria §2 y §6.
- 🔎 `Select-String -Path backend\src\db.py -Pattern "ON CONFLICT|xmax|transaction"`
- 🧪 [`fase5-faq12-idempotencia.txt`](evidencias/fase5-faq12-idempotencia.txt): sigue los 8 casos uno a uno.
- ❓ ¿Qué es el «grano» de `evento_actual` y de `evento_version`? ¿Por qué `country_id` admite NULL? ¿Qué hace el `WHERE` del UPSERT? ¿Por qué hay que contar terremotos en `evento_actual` y no en `evento_version`?

## Bloque 6 · Integración geográfica ☐
- 🎯 Explicar cómo se asigna el país y sus límites.
- 📂 [`geografia.py`](../backend/src/geografia.py) · memoria §3bis y §8.3.
- 🔎 `Select-String -Path backend\src\geografia.py -Pattern "covered_by|make_valid|STRtree"`
- 🧪 `SELECT COALESCE(p.nombre_es, 'Sin país') AS pais, COUNT(*) FROM evento_actual e LEFT JOIN pais p USING (country_id) GROUP BY 1 ORDER BY 2 DESC LIMIT 10;`
- ❓ ¿Por qué `covered_by` y no `covers`? ¿Qué pasa con un punto en dos países? ¿Por qué no se usa `place`? ¿Por qué LEFT JOIN y no INNER JOIN? ¿Qué hace el STRtree y por qué es más rápido?

## Bloque 7 · Histórico, comparación y conclusiones ☐
- 🎯 Defender las 3 conclusiones con sus números, filtros y limitaciones.
- 📂 [`historico_descargar.py`](../backend/src/historico_descargar.py) · [`historico_cargar.py`](../backend/src/historico_cargar.py) · memoria §3 (tabla del histórico) y §7.
- 🔎 `Select-String -Path backend\src\historico_descargar.py -Pattern "count|20000|partir"`
- 🧪 Panel → filtros → todo 2025 y la zona de Kamchatka (fíjate en julio).
- ❓ ¿Por qué se divide entre 365 y no entre los días con terremotos? ¿Por qué hay que deduplicar entre meses? ¿Por qué la mediana describe mejor que la media un «día típico»? ¿EE. UU. tiembla más que el resto del mundo?

## Bloque 8 · API y CORS ☐
- 🎯 Explicar las 3 rutas, los filtros comunes y qué es CORS.
- 📂 [`api.py`](../backend/src/api.py) · `docs/material-profesor/CONTRATO-API.md`.
- 🔎 `Select-String -Path backend\src\api.py -Pattern "@app.get|def filtros|503|CORSMiddleware"`
- 🧪 Abrir http://localhost:8000/docs y probar `/api/estadisticas` con `min_mag=4`.
- ❓ ¿Diferencia entre `generated` y `last_ingestion`? ¿Por qué se responde 503 y no «0 eventos» si la base cae? ¿Qué es `truncated`? ¿CORS es autenticación? ¿Qué es el `OPTIONS` previo?

## Bloque 9 · Panel y despliegue ☐
- 🎯 Explicar qué hace el navegador y para qué sirven ngrok y Netlify.
- 📂 [`api.service.ts`](../frontend/src/app/api.service.ts) · [`app.component.ts`](../frontend/src/app/app.component.ts) (método `refresh`) · memoria §7bis · README §6–7.
- 🔎 `Select-String -Path frontend\src\app\app.component.ts -Pattern "allSettled|ultimoAcceso|setTimeout"`
- 🧪 `docker compose stop tunel` → mira el panel → `docker compose start tunel` → espera 1 min.
- ❓ ¿Qué pasa en el panel si se cierra el túnel? ¿Por qué el token de ngrok no está en `config.json`? ¿Por qué `apiUrl` va sin `/api`? ¿Por qué el túnel apunta a `api:8000` y no a `localhost`?

## Bloque 10 · Reproducción y pruebas de aceptación ☐
- 🎯 Hacer la demostración de la reproducción y explicar el aislamiento.
- 📂 [`productor_replay.py`](../backend/src/productor_replay.py) · [`sql/02_reproduccion.sql`](../sql/02_reproduccion.sql) · memoria §9 y §10.
- 🔎 `Select-String -Path compose.yaml -Pattern "replay"`
- 🧪 Vaciar `replay` (README §8) → `docker compose run --rm productor-replay` → panel en «REPRODUCCIÓN».
- ❓ ¿Cómo se aísla la reproducción (3 cosas)? ¿Qué pasaría sin aislarla? ¿Por qué no se cambian las fechas? Recita las 11 pruebas y su evidencia.

## Bloque 11 · Calidad, complejidad y costes ☐
- 🎯 Defender el análisis de calidad y las mediciones.
- 📂 memoria §5.4 · [`analisis/calidad.sql`](../analisis/calidad.sql) · memoria §8 · [`medir.py`](../backend/src/medir.py) (solo el docstring).
- 🧪 `Get-Content analisis/calidad.sql | docker compose exec -T postgres psql -U observatorio -d observatorio` (¿han cambiado los números?).
- ❓ Las 6 dimensiones con un dato de cada una. ¿Qué es O(N), O(1), O(log N)? ¿Qué cuesta un índice? ¿Qué pasaría con 100 millones? ¿Por qué el proyecto no cuesta 0 €?

## Bloque 12 · Simulacro de defensa ☐
- 🎯 Explicar el flujo completo **solo**, en 10 minutos, y una decisión técnica propia.
- 🧪 Cronómetro y en voz alta (o grabándote con el móvil): sigue un terremoto desde USGS hasta el panel, nombrando el archivo de cada paso.
- **Decisión técnica propia** (elige una y prepárala a fondo: problema → opciones → elección → evidencia):
  - Guardar los originales del feed hasheando solo `features` (se guardaba una copia cada minuto porque `metadata.generated` cambia siempre).
  - Reproducción aislada con un esquema PostgreSQL propio y el mismo consumidor (D44).
  - ngrok en un contenedor tras fallar la instalación en Windows (D43).
  - Mediana y percentiles además de la media en la comparación con 2025 (Conclusión 3).
- ❓ Pide a alguien (o a Claude) que te haga 10 preguntas al azar de [`defensa.md`](defensa.md).

## Miércoles 18/11 · Comprobación final ✅
- ☐ Lista final de la guía de entregables (`docs/material-profesor/Guia-entregables-observatorio-sismico.md`, final).
- ☐ `git status` limpio y `git push` hecho; el repositorio accesible para el profesor.
- ☐ Netlify carga y, con el sistema y el túnel encendidos, muestra datos.
- ☐ Entregar según indique el profesor.

---

## Glosario rápido

| Término | En una frase |
|---|---|
| Topic / partición | «Carpeta» de mensajes en Kafka / trozo del topic; el orden se garantiza dentro de cada partición |
| Clave del mensaje | Decide la partición: el mismo `id` va siempre a la misma, así sus versiones llegan en orden |
| Offset | Posición de un mensaje en su partición; el grupo confirma hasta dónde ha procesado |
| Idempotente | Procesar dos veces lo mismo deja la base igual |
| UPSERT | `INSERT … ON CONFLICT DO UPDATE`: inserta o, si ya existe, actualiza |
| Grano | Qué representa exactamente una fila de una tabla |
| Cuarentena | Tabla donde se guarda lo que no entra, con su motivo y el original |
| Esquema (PostgreSQL) | «Carpeta» de tablas dentro de la base (`public`, `replay`) |
| `search_path` | Lista de esquemas donde PostgreSQL busca una tabla sin esquema |
| STRtree | Índice espacial: descarta polígonos lejanos por su rectángulo antes de la prueba exacta |
| CORS | Regla del navegador: una web solo lee respuestas de otro origen si la API lo permite |
| Preflight (`OPTIONS`) | Pregunta previa del navegador antes de una petición con cabeceras especiales |
| Túnel (ngrok) | Dirección pública HTTPS que lleva las peticiones hasta un puerto de tu PC |
| LAG | Mensajes pendientes de un grupo: último offset del topic − offset confirmado |
| Mediana / p10 / p90 | Valor central / el 10 % de los días están por debajo / el 90 % están por debajo |
