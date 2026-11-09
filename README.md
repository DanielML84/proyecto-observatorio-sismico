# Observatorio de actividad sísmica

Proyecto de Sistemas de Big Data · Curso de especialización en IA y Big Data · CPIFP Alan Turing (Málaga).
Autor: **Daniel Meléndez Loreto**. Trabajo individual.

**Pregunta:** ¿dónde se está registrando actividad sísmica y cómo se compara con un periodo histórico equivalente (2025)?

```text
USGS feed (cada 60 s) → productor (Python) → Kafka → consumidor (Python) → PostgreSQL → API (FastAPI) → ngrok (HTTPS) → panel (Angular + Leaflet, Netlify)
```

| Enlace | Dirección |
|---|---|
| Panel publicado | https://adorable-zabaione-a69bde.netlify.app/ |
| API pública (túnel) | https://unbolted-decorated-heaving.ngrok-free.dev/api/salud — **solo responde con el equipo del autor encendido** |
| Memoria | [`docs/memoria.md`](docs/memoria.md) |
| Evidencias | [`docs/evidencias/`](docs/evidencias/) (mapa al final de este README) |

**Contenido de este README:** [cómo se cumple la rúbrica](#cómo-se-cumple-la-rúbrica-enunciado-13) ·
[las tres conclusiones](#resultados-las-tres-conclusiones) · [pruebas de aceptación](#pruebas-de-aceptación-enunciado-11) ·
[ciclo de desarrollo con IA](#ciclo-de-desarrollo-cómo-se-ha-construido) · [activar el sistema](#activar-el-sistema-para-la-demostración-guía-de-entregables-32) ·
instalación y uso (§1–§9) · [estructura](#10-estructura-del-repositorio) · [evidencias](#11-dónde-está-cada-evidencia).

### Vista del panel

| Datos reales del feed, con filtros, estado del sistema y mapa | Estadísticas: ventanas de 1 h UTC, país, magnitud y profundidad |
|---|---|
| ![Panel con datos reales](docs/evidencias/fase9-bloque1-normal.png) | ![Estadísticas del panel](docs/evidencias/fase9-bloque4-estadisticas.png) |

---

## Cómo se cumple la rúbrica (enunciado §13)

| Criterio | Qué se ha hecho | Dónde comprobarlo |
|---|---|---|
| **Extracción** | Feed `all_day.geojson` cada 60 s publicando **solo novedades** por `(id, updated)`, con reintentos 2/4/8 s y originales comprimidos con retención de 24 h. Histórico 2025 (mundial, M ≥ 4, `earthquake`): **18.302 eventos** en 12 consultas mensuales con `count` previo, sin truncar y deduplicados. Catálogo Natural Earth integrado por punto en polígono. Exploración de tipos, unidades y campos opcionales | [memoria §2–§4](docs/memoria.md) · [`productor.py`](backend/src/productor.py) · [`historico_descargar.py`](backend/src/historico_descargar.py) · [notebook](analisis/01_exploracion_feed.ipynb) · `fase7-historico.txt` |
| **Calidad** | 15 reglas de validación con motivo fijo; cuarentena con el mensaje original (`invalido` / `excluido`); análisis de las **6 dimensiones** con consultas SQL, tabla antes → acción → después y limitaciones (la exactitud no es verificable). Magnitudes y profundidades negativas estudiadas y conservadas; nulos sin rellenar | [memoria §5](docs/memoria.md) · [`validacion.py`](backend/src/validacion.py) · [`calidad.sql`](analisis/calidad.sql) · `fase13-calidad.txt` |
| **Modelado** | Modelo conceptual, lógico y físico: hecho `evento_actual` (1 fila = 1 terremoto), historial `evento_version` (1 fila = 1 versión), dimensiones `pais` y `fecha`, cuarentena y estado de ingesta. **Idempotencia:** claves primarias + UPSERT con `WHERE updated_ms <`, transacción y offset confirmado **después** de escribir. País por `covered_by` con STRtree. Índices justificados y medidos | [memoria §3bis, §6](docs/memoria.md) · [`01_esquema.sql`](sql/01_esquema.sql) · [`db.py`](backend/src/db.py) · `fase5-faq12-idempotencia.txt` · `fase6-paises.txt` |
| **Análisis** | Ventanas fijas de 1 h UTC por hora de ocurrencia, distribuciones con «sin valor», recuentos por país y subregión con «Sin país asignado», comparación con 2025 con mismos filtros (media, **mediana, P10–P90 y % de días**) y avisos cuando el porcentaje engaña. **Tres conclusiones** con cifras, filtros y periodo, una de ellas contrastada después con el catálogo | [memoria §7 y §7bis](docs/memoria.md) · [abajo](#resultados-las-tres-conclusiones) · [`api.py`](backend/src/api.py) |
| **Reflexión** | Complejidad de 3 operaciones (lista frente a diccionario ≈23 000×, STRtree ≈8×, índice B-tree ≈2 000×) medidas con 3 tamaños; qué pasaría con 100 millones; costes medidos y supuestos (≈46 €/mes + desarrollo); propuesta de escalado; limitaciones en cada apartado | [memoria §8](docs/memoria.md) · [`medir.py`](backend/src/medir.py) · `data/mediciones/` |

Revisión completa requisito a requisito (enunciado, guía de entregables y FAQ): [`docs/revision-enunciado.md`](docs/revision-enunciado.md).

## Resultados: las tres conclusiones

Detalle con datos, filtros, periodo, denominador, interpretación y limitaciones en la [memoria §7](docs/memoria.md).
Ninguna es una predicción ni una evaluación de riesgo.

1. **El pico de julio y agosto de 2025 se concentra en Kamchatka.** Histórico 2025, mundial, `earthquake`, M ≥ 4
   (18.302 eventos). La zona (lat 45–60, lon 150–170) pasa de 19,3 eventos/mes (enero–junio) a 1.375 en julio y 1.254 en
   agosto, tras el M8,8 del 29/07/2025; el resto del mundo no tiene pico. Consecuencia: la media diaria de 2025 (50,14)
   está inflada por esa secuencia (sin la zona, 39,25).
2. **Sin filtro de magnitud, el recuento por país mide sobre todo dónde hay más sensores.** Feed del 30/10 al 01/11/2026:
   sin filtro, **75,1 %** de los terremotos en EE. UU.; con M ≥ 4, **3,3 %** (histórico 2025: 0,4 %). Las redes densas de
   EE. UU. registran magnitudes que en otras regiones no se detectan: para comparar regiones hay que usar el mismo umbral.
3. **El recuento de 24 h está en la parte baja del rango de 2025, pero no es excepcional.** 30/10/2026 09:28 → 31/10/2026
   09:28 UTC, M ≥ 4: **25** en el feed frente a una media de **50,14** (−50,1 %), pero con mediana 43 y P10 31. Contrastado
   el 03/11 con el catálogo FDSN: **28** (−44,2 %), y el 7,4 % de los días de 2025 tuvo 28 o menos. La mediana describe mejor un
   día típico que la media; el feed en tiempo real se quedó corto en 3 de 28.

## Pruebas de aceptación (enunciado §11)

Las 11 se han **ejecutado** y tienen evidencia (detalle: [memoria §9](docs/memoria.md)). Los casos sintéticos van
marcados (`PRUEBA-…`) y la API nunca los devuelve.

| Prueba | Resultado observado | Evidencia |
|---|---|---|
| Evento nuevo · misma versión · versión posterior · versión antigua | `insertado` · `ignorado` · `actualizado` (4,2 → 4,6) · `ignorado` (sigue 4,6) | `fase5-faq12-idempotencia.txt` |
| Magnitud nula · coordenadas inválidas | Guardado con `mag` NULL y «ND» en el panel · cuarentena `lat_fuera_de_rango` | ídem; `fase9-panel.txt` |
| Evento marítimo | «Sin país asignado» y presente en todos los recuentos | `fase9-bloque4-estadisticas.png` |
| Reiniciar consumidor | LAG 99 con el consumidor parado → 0 al arrancar; recuentos iguales | `fase11-reproduccion.txt` |
| Cerrar / reabrir el túnel | Aviso rojo conservando la última lectura → recuperación sola, sin recargar | `fase11-tunel-*.png` |
| Reproducción histórica | 96 eventos por `terremotos.replay` → esquema `replay`; duplicado y revisión controlados; los datos actuales no cambian | `fase11-reproduccion.txt` |

| Túnel cerrado: el panel avisa y conserva la última lectura | Modo «REPRODUCCIÓN», aislado de los datos actuales |
|---|---|
| ![Túnel cerrado](docs/evidencias/fase11-tunel-cerrado.png) | ![Reproducción](docs/evidencias/fase11-panel-reproduccion.png) |

## Ciclo de desarrollo (cómo se ha construido)

El proyecto se ha desarrollado **con ayuda de IA (Claude, de Anthropic)**, usándola como herramienta y no como sustituto:
el alumno decide, comprueba y hace los commits; la IA explica, propone y genera, y cada decisión queda documentada.

**Herramientas**

| Herramienta | Para qué |
|---|---|
| **Proyecto de Claude** (claude.ai) con documentos de contexto: el enunciado, la guía, la FAQ, [`docs/prompt-principal.md`](docs/prompt-principal.md) (reglas y decisiones), el roadmap, la bitácora y la memoria | Planificar, entender cada pieza, comparar opciones y redactar la documentación. Al empezar cada conversación se cargan el prompt, el roadmap y la bitácora para no perder el contexto |
| **Claude Code** en VS Code, con las reglas de [`CLAUDE.md`](CLAUDE.md) | Las fases con mucho ir y venir de pruebas (panel, despliegue, reproducción): ejecuta Docker, npm y curl en el Windows del alumno y enseña la evidencia |
| **Claude de escritorio** con acceso a la carpeta del proyecto | Estudio guiado y revisión final punto por punto contra el enunciado |
| Git y GitHub | Historial: el primer commit (`5c052ff`) es el material del profesor sin modificar, para distinguir lo reutilizado de lo propio |

**Reglas de trabajo** ([`prompt-principal.md`](docs/prompt-principal.md) §1): no inventar nada y referenciar cada decisión
(enunciado, FAQ o documentación oficial), decir «no lo sé» cuando no se sabe, **la IA nunca hace commits, push ni
entregas**, y antes de dar algo por bueno se verifica con un comando, una consulta SQL o una captura.

**Ciclo de cada pieza:** concepto → decisión (opciones, elección y referencia) → generación → verificación →
commit del alumno → [bitácora](docs/bitacora.md). El plan por fases está en el [roadmap](docs/roadmap.md) y las
decisiones técnicas en el [Anexo A de la memoria](docs/memoria.md) (D1–D46).

**Fases:** 0 preparación → 1 exploración de datos → 2–3 contrato y Kafka → 4–5 PostgreSQL e idempotencia → 6 país y calidad
→ 7 histórico → 8 API → 9 panel → 10 despliegue → 11 reproducción y pruebas → 12 mediciones y costes → 13 memoria. A partir
del 30/10 el método pasó a **«construir primero, estudiar después»**: terminar el sistema completo y después estudiarlo con
una [guía de 12 bloques](docs/guia-estudio.md) y preguntas de autoevaluación ([`defensa.md`](docs/defensa.md)).

**Control humano: errores de la IA detectados y corregidos** (bitácora):
- El punto en polígono con `predicate="covers"` dejaba todo sin país: la propia prueba frente a un bucle simple lo detectó → `covered_by`.
- Una consulta de verificación usaba una columna que no existe (`updated_at` en `evento_version`).
- La conciliación contó un caso sintético (`PRUEBA-EXPLOSION`) como real; desde entonces los sintéticos se separan por prefijo.
- Textos del panel en modo reproducción que decían más de lo que mostraban los datos («secuencia»), corregidos al revisar la captura.
- Fallos visuales del panel (barras estrechas, desbordamiento a 320 px) encontrados al probar.

**Decisiones del alumno** (Anexo A): lista fija de países del catálogo en el panel (D33), campos de cobertura y de
magnitudes excluidas en la API (D31–D32), mostrar el porcentaje con aviso en lugar de ocultarlo (D39) y el umbral
propio `BASE_MINIMA` (D40), ngrok en contenedor tras fallar la instalación en Windows (D43) y contrastar la
Conclusión 3 con el catálogo días después. Trazabilidad: más de 45 commits desde el 28/10/2026 y una entrada de
bitácora por sesión.

---

## Activar el sistema para la demostración (guía de entregables §3.2)

El backend corre en el equipo del autor: si está apagado, el panel de Netlify carga pero muestra el aviso rojo de
«La API no responde». Para la demostración, en PowerShell y desde la carpeta del proyecto:

| Paso | Qué hacer | Qué hay que ver |
|---|---|---|
| 1 · Arrancar y comprobar | Abrir Docker Desktop · `docker compose --profile tunel up -d` · `docker compose --profile tunel ps` | 7 servicios `Up`; `api`, `kafka`, `postgres` y `productor` en `(healthy)` |
| 2 · Datos e ingesta | `curl.exe http://localhost:8000/api/salud` · `docker compose logs productor --since 5m` | `"base_datos": "ok"` y `"datos_desactualizados": false` (última ingesta hace menos de 5 min); líneas `OK eventos=… publicados=…` cada minuto |
| 3 · Túnel | Abrir http://localhost:4040 y comparar la URL pública con `apiUrl` de [`frontend/public/config.json`](frontend/public/config.json) · abrir `https://…ngrok-free.dev/api/salud` | La misma URL en los dos sitios; `/api/salud` responde desde internet |
| 4 · Panel | Abrir https://adorable-zabaione-a69bde.netlify.app/ | Terremotos en el mapa, filtros y tabla funcionando; estado «Última consulta completada» sin aviso rojo |
| 5 · Reproducción (cuando se pida) | Vaciar el esquema `replay` (comando del §8) · `docker compose run --rm productor-replay` · en el panel, selector **«Datos» → «REPRODUCCIÓN»** | Banda naranja «REPRODUCCIÓN»; 96 eventos de la ventana del M8,8 de Kamchatka (29/07/2025), con sus fechas originales. Los datos actuales no cambian |

Detalle de cada paso: §3 (arranque), §5 (estado y logs), §7 (túnel), §8 (reproducción). Para parar al terminar:
`docker compose --profile tunel stop` (no borra datos, §9).

## 1. Requisitos y versiones

| Herramienta | Versión usada | Para qué |
|---|---|---|
| Docker Desktop (con Docker Compose v2) | la del equipo del autor, en Windows 11 + WSL2 | Todos los servicios del backend |
| Git | — | Clonar el repositorio |
| Node.js | 22.12 o superior (el `package.json` admite 22.x y 24.x) | Solo para el panel en desarrollo |
| Cuenta de ngrok (gratuita) | — | Túnel HTTPS hacia la API |
| Cuenta de Netlify (gratuita) | — | Publicar el panel |

Versiones fijadas dentro de los contenedores: Kafka `apache/kafka:4.1.2` (KRaft, sin ZooKeeper), PostgreSQL `postgres:17-alpine`,
Python 3.12 (`python:3.12-slim`) con las dependencias exactas de [`backend/requirements.txt`](backend/requirements.txt),
ngrok `ngrok/ngrok:latest` (imagen probada: `sha256:ff3b5c3674432d14a786349908b7bdf28ee56c25662637afcbe7180d471993ef`; la imagen no declara número de versión). Panel: Angular 20.3, ngx-leaflet 20, Leaflet 1.9.4.

## 2. Configuración local (`.env`)

```bash
git clone https://github.com/DanielML84/proyecto-observatorio-sismico.git
cd proyecto-observatorio-sismico
cp .env.example .env          # PowerShell: Copy-Item .env.example .env
```

Edita `.env`:

| Variable | Qué poner |
|---|---|
| `POSTGRES_DB`, `POSTGRES_USER` | Se pueden dejar (`observatorio`) |
| `POSTGRES_PASSWORD` | Una contraseña propia |
| `CORS_ORIGINS` | Orígenes que pueden leer la API, separados por coma, sin espacios y **sin barra final**. En desarrollo: `http://localhost:4200`. Con Netlify: `http://localhost:4200,https://TU-SITIO.netlify.app` |
| `NGROK_AUTHTOKEN` | Tu token de https://dashboard.ngrok.com (solo si vas a abrir el túnel) |

`.env` está en `.gitignore`: **no se sube nunca** (contraseña y token).

## 3. Construir y arrancar

```bash
docker compose up --build -d
docker compose ps
```

- La **primera vez**, con el volumen vacío, PostgreSQL ejecuta solo los scripts de [`sql/`](sql/): crea las tablas,
  los índices, la dimensión fecha (2024–2027) y el esquema `replay`. No hay que crear nada a mano.
- `kafka-init` crea los topics `terremotos.live` y `terremotos.replay` (3 particiones) y termina (`Exited (0)` es correcto).
- En 1–2 minutos deben aparecer como `healthy` `kafka`, `postgres`, `api` y `productor`, y en marcha los dos consumidores.
  El orden de arranque se controla con *healthchecks* y `depends_on`, y los servicios reintentan las conexiones.
- El productor empieza a descargar el feed cada 60 s.

> **Si la base ya existía antes de `sql/02_reproduccion.sql`** (los scripts solo se ejecutan con el volumen vacío),
> aplícalo a mano (se puede repetir sin problema):
> `Get-Content sql/02_reproduccion.sql | docker compose exec -T postgres psql -U observatorio -d observatorio`

## 4. Carga histórica (2025)

Con el sistema en marcha:

```bash
docker compose run --rm productor python -m src.historico_descargar   # 12 consultas mensuales a la API FDSN → data/historico/
docker compose run --rm productor python -m src.historico_cargar      # deduplica y publica por Kafka (el consumidor los guarda)
```

- Se descargan **18 302** terremotos (2025, mundial, M ≥ 4, `earthquake`). Antes de cada descarga se pide el `count`;
  si un mes superara 20 000 eventos, el intervalo se divide solo. Registro: `data/historico/manifest.json` y tabla `consulta_ingesta`.
- Los archivos (13 MB) **no se suben a Git**: se regeneran con el primer comando. Si ya existen, se reutilizan.
- Volver a cargarlos no duplica nada (consumidor idempotente).

## 5. Comprobar el estado y ver los logs

```bash
docker compose ps                                  # estado y healthchecks
docker compose logs -f productor                   # una línea por consulta: eventos y publicados
docker compose logs -f consumidor                  # una línea por mensaje: insertado / actualizado / ignorado / cuarentena
curl http://localhost:8000/api/salud               # PowerShell: curl.exe ...
```

- API local: http://localhost:8000/api/salud · `/api/eventos` · `/api/estadisticas` · documentación automática en http://localhost:8000/docs
- La API solo se publica en `127.0.0.1:8000`. Kafka y PostgreSQL **no** se publican al exterior.
- Consultas útiles a la base de datos: [`docs/chuleta-comandos.md`](docs/chuleta-comandos.md).

## 6. Panel (Angular)

**Desarrollo:**

```bash
cd frontend
npm ci
npm start            # http://localhost:4200
```

El panel lee la dirección de la API de [`frontend/public/config.json`](frontend/public/config.json) (`apiUrl` **sin** `/api` al final).
Para trabajar contra la API local: `"apiUrl": "http://localhost:8000"`. Con `"mode": "demo"` usa un GeoJSON de ejemplo y no necesita backend.

**Publicación en Netlify** (el repositorio ya incluye [`frontend/netlify.toml`](frontend/netlify.toml) y `_redirects`):

1. Netlify → *Add new project* → *Import from Git* → este repositorio.
2. **Base directory: `frontend`** · Build command: `npm run build` · Publish directory: `frontend/dist/observatorio/browser`.
3. Los proyectos nuevos de Netlify son **privados** por defecto: *Project configuration → General → Visitor access →
   Project visibility → Public*.
4. Cada `git push` vuelve a publicar el panel.

## 7. Túnel ngrok y URL de la API

El túnel corre en un contenedor (servicio `tunel`, decisión D43) que apunta a `http://api:8000` dentro de la red de Compose:

```bash
docker compose --profile tunel up -d tunel
```

1. Abre http://localhost:4040: ahí aparece tu URL pública `https://….ngrok-free.dev` (cada cuenta tiene la suya).
2. Ponla en `frontend/public/config.json` → `apiUrl`, **sin** `/api` al final, y haz `git push` (Netlify vuelve a publicar).
3. Añade el origen exacto de Netlify a `CORS_ORIGINS` en `.env` y recrea la API: `docker compose up -d api`
   (`restart` no vuelve a leer el `.env`).
4. Comprueba: `https://TU-URL.ngrok-free.dev/api/salud`.

El token de ngrok solo está en `.env`; nunca en Git ni en el panel. La URL pública sí puede estar en `config.json`.

## 8. Pruebas y reproducción histórica

| Qué | Comando | Dónde se explica |
|---|---|---|
| Casos sintéticos de idempotencia (FAQ 12: duplicado, revisión, versión antigua, magnitud nula, latitud imposible, explosión) | `docker compose run --rm productor-prueba python -m src.pruebas_faq12` | memoria §9 · `fase5-faq12-idempotencia.txt` |
| **Reproducción histórica** (ventana del M8,8 de Kamchatka, 96 eventos + 3 casos controlados, 1 cada 2 s) | `docker compose run --rm productor-replay` | memoria §10 · `fase11-reproduccion.txt` |
| Ver la reproducción en el panel | Selector **«Datos» → «REPRODUCCIÓN»** | `fase11-panel-reproduccion.png` |
| Repetir la reproducción desde cero (solo vacía el esquema `replay`) | `docker compose exec postgres psql -U observatorio -d observatorio -c "TRUNCATE replay.evento_actual, replay.evento_version, replay.cuarentena"` | memoria §10 |
| Reiniciar el consumidor sin duplicar | `docker compose stop consumidor-replay` → reproducción → `kafka-consumer-groups.sh --describe` → `docker compose start consumidor-replay` | `fase11-reproduccion.txt` |
| Cerrar y reabrir el túnel | `docker compose stop tunel` / `docker compose start tunel` | `fase11-tunel-*.png` |
| Análisis de calidad (solo lectura) | `Get-Content analisis/calidad.sql \| docker compose exec -T postgres psql -U observatorio -d observatorio` | memoria §5.4 |
| Mediciones de rendimiento (3 tamaños) | `docker compose run --rm medir` | memoria §8 |
| Contraste feed en vivo frente a catálogo FDSN (Conclusión 3) | `docker compose run --rm productor python -m src.contrastar_fdsn` | memoria §7 · `fase13-contraste-fdsn.txt` |

Los datos sintéticos van siempre marcados (`PRUEBA-…`, `source = 'prueba-…'`, `SINT-…`) y la API nunca los devuelve.
La reproducción vive en topic, consumidor y esquema propios y nunca toca los datos actuales.

## 9. Detener el sistema y qué se conserva

```bash
docker compose --profile tunel stop      # para todo, incluido el túnel. Se reanuda con: docker compose --profile tunel up -d
```

| Dato | Dónde | ¿Se conserva al parar o reiniciar? |
|---|---|---|
| Tablas y datos | volumen `pg-data` | Sí (también con `docker compose down`) |
| Mensajes de Kafka y offsets | volumen `kafka-data` | Sí; los mensajes se borran a los 7 días o al pasar de 512 MB por partición |
| Estado del productor (`version_publicada`) | PostgreSQL | Sí: al reiniciar no vuelve a publicar lo ya enviado |
| Respuestas originales del feed | `data/raw/` (comprimidas) | Sí, pero se borran a las 24 h (retención) |
| Histórico descargado | `data/historico/` | Sí; regenerable (§4) |

- ⚠️ `docker compose down -v` **borra los volúmenes**: se pierde todo y hay que volver a cargar el histórico.
- Una parada de **menos de 24 h** se recupera sola en la primera descarga (el feed contiene las últimas 24 h; comprobado
  en memoria §5.2bis). Con más de 24 h queda un hueco que habría que pedir al catálogo FDSN.

## 10. Estructura del repositorio

| Ruta | Contenido |
|---|---|
| `compose.yaml` | Los 5 servicios obligatorios + `kafka-init`, `consumidor-replay`, `tunel` y los de *profile* (`productor-prueba`, `productor-replay`, `medir`) |
| `backend/` | Imagen Python común (`Dockerfile`, `requirements.txt`) y código en `src/`: `productor.py`, `consumidor.py`, `validacion.py`, `geografia.py`, `db.py`, `api.py`, `mensajes.py`, histórico, reproducción, pruebas y mediciones |
| `sql/` | `01_esquema.sql` (tablas, claves, índices, dimensión fecha) y `02_reproduccion.sql` (esquema `replay`) |
| `frontend/` | Panel Angular + Leaflet (base del profesor, ampliada) |
| `analisis/` | Notebook de exploración del feed y `calidad.sql` |
| `docs/memoria.md` | Memoria: diccionario, procedencia, calidad, modelo, análisis y conclusiones, panel, complejidad y costes, pruebas, reproducción y decisiones (Anexo A) |
| `docs/evidencias/` | Logs, consultas y capturas de cada prueba |
| `docs/contrato-mensaje.md` | Formato de los mensajes de Kafka |
| `docs/roadmap.md`, `docs/bitacora.md` | Plan por fases y diario de cada sesión (problemas y soluciones) |
| `docs/defensa.md` | Preguntas previsibles y respuestas de estudio |
| `docs/material-profesor/` | Enunciado, FAQ, guía, contrato de la API y ejemplos, **sin modificar** |
| `data/` | Descargas regenerables (`raw/`, `historico/`: no se suben) y resultados de `mediciones/` |

## 11. Dónde está cada evidencia

| Requisito | Evidencia |
|---|---|
| Pipeline funcionando (Kafka, productor, consumidor) | `fase3-*.png`, `fase3-pipeline-python.txt` |
| Esquema creado | `fase4-postgres-esquema.txt` |
| Idempotencia y casos de FAQ 12 | `fase5-faq12-idempotencia.txt`, `fase5-conciliacion.txt` |
| País por punto en polígono | `fase6-paises.txt` |
| Histórico 2025 (count = descargados) | `fase7-historico.txt` |
| Comparación histórica | `fase8-comparacion-historica.txt` |
| Panel | `fase9-*.png`, `fase9-panel.txt` |
| Despliegue (ngrok, Netlify, CORS, móvil) | `fase10-tunel-ngrok.txt`, `fase10-movil-netlify.png` |
| Las 11 pruebas de aceptación | memoria §9 · `fase11-*` |
| Recuperación tras una parada | `recuperacion-parada-nocturna.txt` |
| Calidad por dimensiones | `fase13-calidad.txt` · memoria §5.4 |
| Mediciones | `data/mediciones/*.json` · memoria §8 |
| Contraste de la Conclusión 3 con el catálogo FDSN | `fase13-contraste-fdsn.txt` |
| Conclusión 2 (por país, con y sin umbral) | `fase13-conclusion2.txt` |
| Revisión requisito a requisito | [`docs/revision-enunciado.md`](docs/revision-enunciado.md) |

## 12. Fuentes y licencias

Datos sísmicos: USGS Earthquake Hazards Program (feed GeoJSON y API FDSN). Fronteras: Natural Earth (dominio público),
copia entregada por el profesor. Mapa base: © OpenStreetMap contributors. Detalle: `docs/material-profesor/FUENTES-Y-LICENCIAS.md`.
Uso de IA: el proyecto se ha desarrollado con ayuda de Claude (Anthropic); las decisiones están razonadas en la memoria (Anexo A)
y el proceso, en la bitácora.
