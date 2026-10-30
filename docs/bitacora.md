# Bitácora · Observatorio de actividad sísmica

Una entrada por sesión, la más reciente arriba.
Formato: qué se hizo · decisiones · problemas y solución · commits · dudas · siguiente paso.

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

### Siguiente paso
- El consumidor escribe en PostgreSQL con UPSERT condicionado por `updated` + historial de versiones (Fase 4–5).

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
