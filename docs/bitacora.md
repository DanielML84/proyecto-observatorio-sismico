# Bitácora · Observatorio de actividad sísmica

Una entrada por sesión, la más reciente arriba.
Formato: qué se hizo · decisiones · problemas y solución · commits · dudas · siguiente paso.

---

## Sesión 3 · Sábado 31/10/2026

### Qué se hizo
- **Consumidor → PostgreSQL (idempotente):**
  - `validacion.py`: reglas con motivos fijos (schema, id, updated, time, type, geometría, rangos, profundidad, magnitud, fecha).
  - `db.py`: versión con `ON CONFLICT DO NOTHING`; UPSERT en `evento_actual` con `WHERE updated_ms <` y
    `RETURNING (xmax = 0)` para distinguir insertado/actualizado; cuarentena con UNIQUE (topic, partición, offset);
    todo en una transacción.
  - `consumidor.py`: valida → guarda → confirma el offset.
  - Imagen única `observatorio-backend`; `psycopg[binary]==3.2.3`.
  - Comprobado antes en el entorno de Claude: los 8 casos clasificados bien; muestra real del 28/10 = 185 válidos + 2 excluidos (explosion); SQL validado con pglast.
- **Prueba FAQ 12 + calidad** (`pruebas_faq12.py`, datos sintéticos `PRUEBA-*`): 8 mensajes → 3 actuales
  (E1 = 4,6), 4 versiones y 2 en cuarentena. Evidencia: `docs/evidencias/fase5-faq12-idempotencia.txt`.
  - Observación: el consumidor intercala particiones; dentro de la partición 0 el orden de E1 se mantiene.

### Problemas y solución
- Una consulta de verificación pedía `updated_at` en `evento_version` (no existe esa columna): error de Claude.
  Corregida con `to_timestamp(updated_ms / 1000.0)`.

- **Productor real** (`productor.py`): diccionario en memoria + `version_publicada` en PostgreSQL; publicar →
  confirmación de Kafka → marcar como publicada; reintentos 2/4/8 s (timeout, red, 429, 5xx, JSON); cada intento
  en `consulta_ingesta`; originales `.geojson.gz` en `data/raw/` con retención de 24 h; healthcheck por latido.
  - Simulación previa con la muestra (sin red): ciclo 1 → 187 publicados; ciclo 2 → 0; revisión simulada → 1.
  - **Con datos reales (31/10, 06:48–06:53 UTC):** 220 eventos por respuesta; tras la primera carga, 0 publicados
    por minuto; cuarentena: `type=explosion` (1), **`type=quarry blast` (1, tipo nuevo no visto en la muestra)** y el caso sintético `lat_fuera_de_rango`.
- **Problema:** se guardaba un original por minuto aunque no hubiera cambios, porque USGS cambia
  `metadata.generated` en cada respuesta y el hash del archivo completo siempre era distinto.
  **Solución:** huella calculada solo sobre `features`. Probado: si solo cambia `generated` → no se guarda; si cambia un terremoto → sí.
- **Observación sin explicar:** las consultas salen cada ~55 s en lugar de 60 s (diferencias entre
  `solicitada_at`). Causa no confirmada (¿reloj de la VM de Docker Desktop?). Pendiente de medir.

- Productor reconstruido: `estado cargado: 222 versiones` → `publicados=0` (confirma la persistencia del estado).
- **Conciliación (Consistencia):** 222 publicados = 221 actuales + 1 cuarentena real; 0 ids perdidos.
  Primero pareció un descuadre: Claude contó `PRUEBA-EXPLOSION` como real. Los datos sintéticos se separan por el prefijo.
  Evidencia: `docs/evidencias/fase5-conciliacion.txt`.
- Duda de Daniel: ¿`up -d --build productor` duplica servicios? No: recrea el contenedor. Y aunque hubiera
  dos productores, la idempotencia del consumidor evitaría duplicar datos.

- **Fase 6 · país:** `geografia.py` (Shapely 2.0.6, STRtree, `covered_by`, desempate alfabético, None = sin país);
  el consumidor carga los 177 países al arrancar y asigna el país; `rellenar_paises.py` para los ya guardados;
  catálogo montado en solo lectura.
  - **Hallazgo:** las geometrías de USA y SDN no son válidas (autointersección); se reparan en memoria con
    `make_valid` (el área no cambia).
  - **Error de Claude detectado por su propia prueba:** con `predicate="covers"` todo salía sin país (el sentido
    del predicado está invertido en `STRtree.query`). Corregido a `covered_by`. Verificado frente a un bucle simple:
    mismo resultado en 185/185; STRtree ~10 veces más rápido.
  - Resultado real: 225 eventos → 181 con país, 44 sin país, 0 coincidencias múltiples. Por país (reales):
    EE. UU. 170, sin país 44, Puerto Rico 2…
  - **Observación para el análisis:** el 77 % de los eventos son de EE. UU. porque el feed incluye magnitudes muy
    pequeñas que solo detectan las redes densas de EE. UU. Es un sesgo de **cobertura de detección**, no de actividad (enunciado §8).
  - Reproducibilidad: `numpy` (dependencia de shapely) no estaba fijado → `numpy==2.5.4`.

- **Fase 7 · histórico 2025:** `historico_descargar.py` (count previo, división si > 20.000, archivos tal cual,
  `manifest.json`, `consulta_ingesta`, reutiliza lo ya descargado) y `historico_cargar.py` (deduplica por id con el
  `updated` mayor y publica por Kafka con `source='usgs-fdsn'`). El productor monta ahora `./data:/data`;
  `data/historico/` fuera de Git.
  - Comprobado en la muestra de enero: `minmagnitude=4` incluye mag = 4,0 (70 eventos) → filtro `mag >= 4`.
  - Deduplicación probada con un caso sintético de frontera (se queda la versión con el `updated` mayor).
  - Real: 12 consultas, 18.302 eventos (13 MB), count = descargados en todos los meses, 0 repetidos entre meses;
    máximo mensual 2.684 (julio). Primera media diaria provisional (mientras el consumidor seguía procesando): 41,16.
  - **Llama la atención:** julio (2.684) y agosto (2.222) casi duplican al resto de meses (~1.200–1.600). Pendiente de
    investigar con datos (¿réplicas de un gran terremoto?).

  - Carga completa: 18.302 guardados + 0 en cuarentena = 18.302 ✓. **Media diaria 2025 (mag ≥ 4) = 50,14.**
  - Pico de julio y agosto: el terremoto más fuerte del periodo es el **M8,8 de Kamchatka del 29/07/2025**, más otro
    M7,4 en el este de Kamchatka (20/07). Hipótesis: réplicas → pendiente de confirmar con la distribución espacial.
  - La pregunta de por qué se divide entre 365 no la sabía → explicada (los días con cero eventos también cuentan).
  - Evidencia: `docs/evidencias/fase7-historico.txt`.

  - **Hipótesis confirmada:** en la zona de Kamchatka (lat 45–60, lon 150–170) se pasa de 19,3 eventos/mes (ene–jun)
    a 1.375 en julio y 1.254 en agosto, y luego baja; el resto del mundo es estable. La zona = 21,7 % del año. La media
    diaria sin la zona sería 39,25 (frente a 50,14). → **Primera conclusión redactada** (memoria §7).

- **Fase 8 · API:** `api.py` (FastAPI 0.115.6, Uvicorn): `/api/eventos` (GeoJSON, filtros start/end/min_mag/country_id,
  `SIN_PAIS`, paginación, máximo 5.000), `/api/estadisticas` (totales, nulos, país, subregión, ventanas de 1 h UTC con
  `generate_series`, tramos de magnitud de 0,5, clases de profundidad, comparación con 2025 usando `mag >= max(4, min_mag)`),
  `/api/salud`. Una sola función de filtros para todas las rutas. Excluye las fuentes `prueba…`. Si la BD falla → 503.
  CORS por variable de entorno. Puerto publicado solo `127.0.0.1:8000`.
  - Probada antes en el entorno de Claude con un **PostgreSQL embebido (pgserver)** y el mismo `01_esquema.sql`: filtros,
    nulos, SIN_PAIS, paginación, estadísticas, CORS (permitido/rechazado), 422 y 503 → todo correcto.
  - Real (31/10 09:28 UTC): 208 terremotos en 24 h (156 EE. UU., 45 sin país); **comparación mag ≥ 4: 25 frente a la
    media de 2025 de 50,14 → −50,1 %**.
  - **Hipótesis:** la diferencia se debe sobre todo a que el feed en tiempo real está incompleto para M4–4,5 fuera de
    EE. UU. (el catálogo de 2025 ya está revisado). Por comprobar: (1) comparación con `min_mag=4.5`; (2) volver a descargar
    del catálogo ese mismo periodo dentro de unos días.
  - Observación sin explicar: 0 eventos entre 3,5 y 4,0 en esas 24 h (13 entre 4,0 y 4,5).
  - Pregunta generated/last_ingestion: Daniel las tenía al revés (generated cambia siempre; last_ingestion se congela). Corregido.

  - Con mag ≥ 4,5: 13 frente a 23,45 (−44,6 %) → la hipótesis de que faltan sobre todo M4,0–4,5 **no se confirma**.
  - Distribución diaria de 2025 (dimensión fecha): mediana 43, p10 31, máximo 645; solo 10/365 días ≤ 25 (sin Kamchatka:
    mediana 37, p10 26, 29/365). → **Conclusión 3 redactada**: bajo, pero no excepcional; la media exagera.
  - API mejorada: `dias_2025` (mediana, p10, p90, % de días ≤ recuento reciente cuando el periodo es de 24 h). Probado con pgserver.

### Siguiente paso
- Commit Fase 8; Fase 9: panel Angular.

---

## Sesión 2 · Viernes 30/10/2026

### Qué se hizo
- Comprobado que los documentos «nuevos» del profesor (guía y FAQ) y la carpeta de `Downloads` son idénticos
  a los del repositorio → no hay versión nueva del enunciado.
- Notebook `01_exploracion_feed.ipynb` reescrito con explicación conceptual por apartado y comentarios
  línea a línea (Daniel se agobiaba con el pandas sin comentar).
- Creados `docs/memoria.md` (memoria que se rellena por fases, con un registro de decisiones en el Anexo A) y
  `docs/defensa.md` (preguntas probables del profesor; las responde Daniel).
- **Fase 3, paso 1:** `compose.yaml` solo con Kafka (`apache/kafka:4.1.2`, KRaft, volumen `kafka-data`,
  retención de 7 días o 512 MB, sin publicar puertos al host, topics sin creación automática).
  - `docker compose up -d kafka` → healthy.
  - Topic `pruebas` creado a mano.
  - Productor de consola → consumidor de consola: los mensajes «hola terremoto» y «bienvenido kafka» llegan.
  - Evidencias: `docs/evidencias/fase3-docker-desktop-kafka.png`, `fase3-productor-consola.png`,
    `fase3-consumidor-consola.png`.
  - Tras cerrar y volver a abrir los contenedores, los mensajes siguen ahí.

### Problemas y solución
- Docker Desktop avisa de que su versión ya no tiene soporte. No impide trabajar; se actualizará más adelante,
  en un momento en que no haya contenedores con datos importantes.

- **Persistencia confirmada:** `docker compose down` + `up` → los mensajes del topic `pruebas` siguen ahí (volumen `kafka-data`).
- Explicado dónde ver `(healthy)`: columna STATUS de `docker compose ps`.
- **Fase 2:** creado `docs/contrato-mensaje.md` (v1): topics `terremotos.live` y `terremotos.replay`;
  clave = id del evento; valor = `schema_version`, `source`, `mode`, `ingested_at`, `replayed_at` y `event`
  (el Feature original sin modificar). El productor no filtra ni transforma.

- **Fase 3, paso 2:** imagen Python común (`backend/Dockerfile`, `aiokafka==0.12.0`), `src/mensajes.py`
  (construye mensajes según el contrato), `src/productor_prueba.py` (envía us7000ttlm y termina) y
  `src/consumidor.py` (muestra cada mensaje; `enable_auto_commit=False` y commit DESPUÉS de procesar).
  `compose.yaml`: `kafka-init` crea `terremotos.live` y `terremotos.replay` (3 particiones, `--if-not-exists`);
  `productor-prueba` con perfil `pruebas` (se lanza con `docker compose run --rm productor-prueba`).
  - Resultado: publicado en partición 1, offset 0; el consumidor lo recibe en partición 1, offset 0.
  - Evidencia: `docs/evidencias/fase3-pipeline-python.txt`.
  - Aviso de Kafka sobre mezclar «.» y «_» en los nombres de topics: sin impacto (solo usamos «.»).
- **Experimento clave:** al reenviar el mismo evento, Kafka lo guarda otra vez (offset 1). Kafka es un
  registro de mensajes y **no deduplica**. Con un INSERT simple habría 2 filas del mismo terremoto; con el
  feed cada 60 s, 187 × 60 × 24 = 269.280 inserciones al día de eventos repetidos.
  Daniel lo dedujo él solo. → Motiva las dos defensas: productor con estado `(id, updated)` y consumidor idempotente.

### Mejora pendiente (menor)
- `docker compose` construye dos imágenes iguales (`…-consumidor` y `…-productor-prueba`) desde el mismo
  Dockerfile. Se puede dar un nombre común con `image:` para construir una sola.

- **Fase 4 (conceptos, sin código):** niveles conceptual/lógico/físico, entidades (Terremoto, Versión, País,
  Día, Cuarentena, Estado de ingesta), el **grano** de cada tabla y la relación con el modelo dimensional
  (hecho = terremoto; dimensiones = país y día).
  - Confusión trabajada: Daniel pensaba que para contar terremotos se usa la tabla de versiones. Se corrigió
    (estado actual = 1 fila por terremoto; versiones = historial, como `git log`). Segundo ejercicio con la
    FAQ 12: razonamiento correcto (estado actual = 2 y la magnitud es la de la última versión), pero contó
    «3 versiones por terremoto» en lugar de 3 en total → hay que repasar la tabla de la FAQ 12.

- **Fase 4 · base de datos levantada:** `sql/01_esquema.sql` (7 tablas, 3 índices, dimensión fecha con
  1.461 días de 2024 a 2027), `.env.example` y servicio `postgres:17-alpine` en compose (volumen `pg-data`,
  `sql/` montado en `/docker-entrypoint-initdb.d`, healthcheck `pg_isready`, sin puertos publicados).
  - Sintaxis del SQL validada antes con `pglast`.
  - En el equipo de Daniel: 7 tablas creadas; `\d evento_actual` muestra PK, índices, CHECK y FK; fecha = 1461 filas.
  - Prueba: el segundo INSERT del mismo `event_id` falla con `duplicate key value violates unique constraint`.
  - Evidencia: `docs/evidencias/fase4-postgres-esquema.txt`.
- ⚠️ Recordatorio: el SQL de `/docker-entrypoint-initdb.d` solo se ejecuta con el volumen vacío. Si se cambia
  el esquema: `docker compose down -v` (borra los volúmenes) o una migración.

### Cambio de método (decisión de Daniel, 30/10)
«Construir primero, estudiar después»: terminar el proyecto completo y funcionando en bloques grandes,
y dedicar los últimos días a estudiarlo de principio a fin con una guía de estudio. Registrado en el
prompt principal. Objetivo: tener todo funcionando hacia el 12–13/11 y dejar unos 5 días de estudio.

### Siguiente paso (próxima sesión)
1. Consumidor → PostgreSQL: UPSERT en `evento_actual` condicionado por `updated_ms` + INSERT en
   `evento_version` (ON CONFLICT DO NOTHING), todo en una transacción; commit del offset después.
2. Probar la secuencia completa de la FAQ 12 (5 mensajes → 3 versiones → 2 terremotos; E1 = 4,6).
3. Pendientes menores: dar un nombre común a la imagen Python (`image:`); responder en `defensa.md` las preguntas de las Fases 1–4.

---

## Sesión 1 · Miércoles 28/10/2026

### Qué se hizo
- Lectura completa del material: enunciado (Word = «biblia»), guía de entregables, FAQ,
  contrato de la API, validación, fuentes y código Angular de partida.
- Estudio de los repositorios de referencia de Juan:
  - `juanarrow/binance-kafka`: productor Python + aiokafka, Kafka 4.1.2 en modo KRaft,
    healthchecks y reintentos. Hecho con Spec-Driven Development (constitución, spec, plan, tareas).
  - `juanarrow/BigData-notebooks`: sesiones 1–8 (las que consolida este proyecto) y
    `Solucion_modelado_dimensional_ecommerce.ipynb`.
- Organización de la carpeta del proyecto (ver README).
- Creación de roadmap, bitácora y prompt principal.

### Decisiones
| Decisión | Motivo |
|---|---|
| Trabajo individual | Indicado por Daniel (de momento) |
| Memoria en Markdown (`docs/memoria.md`) | Preferencia de Daniel; la guía lo permite |
| Spec y plan escritos a mano en Markdown, sin Spec Kit | Entender cada parte del método SDD paso a paso |
| Material del profesor en `docs/material-profesor/`, sin modificar | Poder demostrar qué es reutilizado y qué es propio (guía §1.1) |
| Primer commit solo con el material del profesor | El historial de Git prueba qué venía hecho |
| Ejemplos renombrados: `feed-all_day-2026-10-28.geojson`, `historico-2025-01-mag4.geojson` | Nombres descriptivos; fecha sacada de `metadata.generated` |

### Problemas y solución
- **Tablas del Word que parecían cortadas:** se leyeron con `python-docx`. Las 5 tablas están
  completas y son idénticas a las de `ENUNCIADO.md`. Solo era la visualización de Word.
- **FAQ duplicada:** `FAQ-observatorio-sismico .md` era idéntica a `FAQ-ALUMNADO.md` → borrada.
- **Archivos ocultos:** solo había `frontend/.gitignore`, que sigue en su sitio. La huella SHA-256 de
  `paises.geojson` coincide con la de `FUENTES-Y-LICENCIAS.md` → catálogo íntegro.
- **Carpeta renombrada** a `proyecto-observatorio-sismico` (nombre elegido por Daniel, igual que el repo).
- **Avisos `LF will be replaced by CRLF` al hacer `git add`:** no son errores. Git en Windows convierte
  los finales de línea. Se añade `.gitattributes` con `eol=lf` para que todo quede en formato Linux,
  porque un script con CRLF puede fallar dentro de un contenedor Docker.
- **El terminal de Claude en el escritorio es un Linux aislado sin Docker:** Docker, npm y git
  se ejecutan en el Windows de Daniel (terminal de VS Code o Claude Code).

### Hallazgos en los datos (primeras observaciones, a confirmar en la Fase 1)
- Feed de ejemplo: 187 eventos; al menos 2 tienen `type = "explosion"`.
- Hay profundidades negativas (p. ej. −2,31 km y −0,54 km): no rechazar sin estudiar.
- Histórico de enero 2025 (mag ≥ 4): 1.413 eventos, muy por debajo del límite de 20.000.

### Commits
- `5c052ff` Material inicial del profesor sin modificar
- `d792b78` Organización del proyecto: README, .gitignore, roadmap, bitácora y prompt principal
- Push a https://github.com/DanielML84/proyecto-observatorio-sismico (rama `main`)

### Fase 1 · Mapa demo (FAQ paso 1) ✅
- `npm ci` + `npm start` en `frontend/`; el panel abre en http://localhost:4200.
- Resultado: catálogo de países cargado, 4 eventos dibujados, 0 omitidos; la ficha, el zoom y las capas funcionan.
- Evidencia: `docs/evidencias/fase1-mapa-demo.png`.
- Angular CLI preguntó si se comparten estadísticas de uso y se respondió «y». **Corrección:** sí modificó
  `frontend/angular.json` (añadió `"cli": {"analytics": "<id>"}`); la primera comprobación se hizo antes
  de que se escribiera. Se revierte para dejar el archivo del profesor intacto y se desactiva a nivel global.
- Problema: un `git status` lanzado desde el terminal de Claude dejó un `.git/index.lock` huérfano, que
  bloquearía los commits. Se borró. Solución para el futuro: Claude usa `git --no-optional-locks`.
- Qué demuestran los 4 puntos ficticios (`terremotos-demo.geojson`), y cómo dibuja el mapa:
  | id | Profundidad | Mag | País | Cómo se ve |
  |---|---|---|---|---|
  | demo-1 | 12 km | 3,2 | España | amarillo (< 70 km) |
  | demo-2 | 95 km | 5,1 | Japón | naranja (70–300 km) |
  | demo-3 | 350 km | 6,0 | Chile | morado (≥ 300 km), el más grande |
  | demo-4 | 8 km | **null** | **null** (océano) | círculo mínimo; ficha «ND» y «Sin país asignado» |

### Fase 1 · Exploración del feed (en curso)
- Creado `analisis/01_exploracion_feed.ipynb` (pandas): estructura, tipos, completitud, unicidad,
  `type`, magnitud, coordenadas, profundidades negativas, tiempos, `status` e `ids`.
- **Problema:** al aplanar con `json_normalize` aparecen **dos columnas `type`** (la del Feature, siempre
  "Feature", y `properties.type`). Provocaba `ValueError: Grouper for 'type' not 1-dimensional`.
  **Solución:** renombrar a `feature_type` y `geom_type` antes de quitar el prefijo `properties.`.
- Resultados (muestra del 28/10, 187 eventos): 187 id únicos; 185 earthquake y 2 explosion; mag de 0,22 a 6,0,
  sin nulos en esta muestra; 28 con mag ≥ 4; 3 profundidades negativas (2 explosiones y 1 terremoto de
  −2,31 km); `updated − time` con mediana de 3,6 min y máximo de 925,8 min; 120 automatic y 67 reviewed;
  8 eventos con más de un id asociado.
- **Documentación oficial FDSN (API del histórico)** aportada por Daniel. Datos útiles:
  - `limit` máximo 20.000: si se supera, la API responde **HTTP 400** (no trunca en silencio).
  - Método `count`: permite saber cuántos eventos hay **antes** de descargarlos.
  - `starttime` = «on or after» y `endtime` = «on or before» → **los dos extremos son inclusivos**,
    por eso hay que deduplicar los eventos que caen en el límite entre meses.
  - `mindepth`/`maxdepth` admiten de −100 a 1000 km → la propia API contempla profundidades negativas.
  - `updatedafter`: permite pedir solo lo actualizado después de una fecha → candidato para recuperar
    un hueco tras una parada de más de 24 h.
  - `eventtype=earthquake` filtra los eventos que no son terremotos; `includedeleted` y el HTTP 409 tienen que ver con los eventos borrados.
- Pregunta de comprobación (misma versión en dos consultas seguidas): Daniel respondió bien
  (0 terremotos nuevos). Matiz: no es porque «no haya terminado», sino porque el feed devuelve toda la
  ventana de 24 h en cada consulta; mismo `id` + mismo `updated` = misma versión, ya publicada.

### Dudas abiertas
- Significado oficial de la profundidad negativa y si `mag` puede ser nula o negativa: pendiente de la
  descripción por campo de https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php

### Siguiente paso
1. Instalar la extensión Jupyter en VS Code y ejecutar el notebook.
2. Rellenar las conclusiones del notebook y hacer commit.
