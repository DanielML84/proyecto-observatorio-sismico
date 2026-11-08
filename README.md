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

---

## Activar el sistema para la defensa (guía de entregables §3.2)

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

## 12. Fuentes y licencias

Datos sísmicos: USGS Earthquake Hazards Program (feed GeoJSON y API FDSN). Fronteras: Natural Earth (dominio público),
copia entregada por el profesor. Mapa base: © OpenStreetMap contributors. Detalle: `docs/material-profesor/FUENTES-Y-LICENCIAS.md`.
Uso de IA: el proyecto se ha desarrollado con ayuda de Claude (Anthropic); las decisiones están razonadas en la memoria (Anexo A)
y el proceso, en la bitácora.
