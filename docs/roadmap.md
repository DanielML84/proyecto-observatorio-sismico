# Roadmap · Observatorio de actividad sísmica

**Entrega:** cierre jueves 19/11/2026 00:00 → último día real **miércoles 18/11**.
**Ritmo previsto:** mínimo 3 días/semana × 4 h. Fechas orientativas.

Leyenda: `[ ]` pendiente · `[~]` en curso · `[x]` hecho · ⚑ = hacer commit al terminar

---

## Semana 1 · 28/10 – 03/11 · Base y primer recorrido

### Fase 0 · Preparación
- [x] Leer todo el material del profesor y los repos de referencia de Juan
- [x] Organizar la carpeta del proyecto
- [x] Crear roadmap, bitácora y prompt principal
- [x] Renombrar carpeta a `proyecto-observatorio-sismico`
- [x] `git init` + commit 1: material del profesor sin modificar ⚑ (`5c052ff`)
- [x] Commit 2: documentos propios ⚑ (`d792b78`)
- [x] Crear repo en GitHub y primer push
- [x] Añadir `.gitattributes` (finales de línea LF) ⚑

### Fase 1 · Mapa demo y exploración de los datos  *(FAQ paso 1–2)*
- [x] Arrancar el frontend en modo demo (`npm ci`, `npm start`) → ver 4 puntos y fronteras ⚑
      Evidencia: `docs/evidencias/fase1-mapa-demo.png`
- [x] Explorar el JSON del feed: campos, tipos, unidades, opcionales (`analisis/01_exploracion_feed.ipynb`)
- [ ] Explorar el catálogo de países: unicidad de `ADM0_A3`, atributos
- [ ] Anotar hallazgos (explosiones, profundidades negativas, nulos…) ⚑

### Fase 2 · Especificación y plan (a mano, Markdown)
- [ ] `docs/spec.md`: qué hace el sistema, reglas de negocio, pruebas de aceptación
- [ ] `docs/plan.md`: decisiones técnicas, servicios, topics, tablas, puertos
- [x] `docs/contrato-mensaje.md`: formato del mensaje Kafka ⚑

### Fase 3 · Kafka + productor + consumidor mínimos  *(FAQ paso 3)*
- [x] `compose.yaml` con Kafka (KRaft, volumen, retención limitada)
- [x] Prueba con consola: topic `pruebas`, productor → consumidor (evidencias `fase3-*.png`)
- [x] Comprobar persistencia con `docker compose down` + `up` (los mensajes siguen ahí)
- [x] Productor mínimo que publica un evento de prueba (`backend/src/productor_prueba.py`)
- [x] Consumidor mínimo que lo muestra en el log (`backend/src/consumidor.py`)
- [x] Evidencia: `docs/evidencias/fase3-pipeline-python.txt` ⚑
- [x] Experimento: reenviar el mismo evento → offset 1 → Kafka NO deduplica (motiva la Fase 5)

## Semana 2 · 04/11 – 10/11 · Datos correctos

### Fase 4 · PostgreSQL y modelo  *(FAQ paso 4)*
- [x] Modelo conceptual → lógico → físico (`sql/01_esquema.sql`)
- [x] Tablas: evento actual, versiones, país, fecha, cuarentena, versión publicada, consulta de ingesta
- [x] PostgreSQL en compose (volumen `pg-data`, healthcheck, `.env`) + prueba de UNIQUE (`fase4-postgres-esquema.txt`) ⚑
- [x] Consumidor escribe en PostgreSQL → consulta SQL lo muestra ⚑

### Fase 5 · Duplicados y revisiones  *(FAQ paso 5 · lo más importante)*
- [x] Productor real: USGS cada 60 s, compara `id` + `updated`, reintentos (`backend/src/productor.py`)
- [x] Consumidor idempotente: transacción + upsert + offset después de escribir (`backend/src/db.py`)
- [x] Probar la secuencia de la FAQ 12 + magnitud nula, latitud 145 y explosión (`fase5-faq12-idempotencia.txt`) ⚑

### Fase 6 · País y calidad  *(FAQ paso 6)*
- [x] Punto en polígono (Shapely, STRtree) → `country_id` o «Sin país asignado» (`backend/src/geografia.py`, `fase6-paises.txt`)
- [x] Reglas de validación + cuarentena con motivo (`backend/src/validacion.py`)
- [x] Filtrar `type == earthquake` y registrar exclusiones ⚑

### Fase 7 · Histórico 2025
- [x] Descarga por meses (mag ≥ 4), registro de consultas, deduplicación (`historico_descargar.py`, `manifest.json`)
- [x] Carga con las mismas reglas de limpieza, por Kafka (`historico_cargar.py`) ⚑

### Fase 8 · API FastAPI  *(FAQ paso 7)*
- [x] `/api/eventos` según contrato, con filtros y paginación (`backend/src/api.py`)
- [x] `/api/salud` y `/api/estadisticas`
- [x] CORS ⚑
- [ ] ~03/11: volver a descargar del CATÁLOGO las 24 h del 30/10 09:28 → 31/10 09:28 UTC y compararlas con el feed → medir el retraso y la completitud (Actualidad)

## Semana 3 · 11/11 – 18/11 · Panel, pruebas y memoria

### Fase 9 · Panel Angular  *(FAQ pasos 8–9)*
- [x] Conectar a la API (modo `api`, `frontend/src/app/api.service.ts`)
- [x] Filtros (fecha, magnitud, país), tabla, gráficos, comparación histórica
- [x] Estado del sistema (última ingesta, avisos) ⚑
- [x] Revisión final: pruebas repetidas, build de producción, CORS, móvil y modo demo (`docs/evidencias/fase9-panel.txt`)

### Fase 10 · Despliegue  *(FAQ paso 10)*
- [ ] Cuentas ngrok y Netlify
- [ ] Túnel + publicación + prueba desde otro dispositivo ⚑

### Fase 11 · Reproducción y pruebas de aceptación  *(FAQ paso 11)*
- [ ] Replay acelerado aislado («REPRODUCCIÓN»)
- [ ] Ejecutar las 11 pruebas y guardar evidencias en `docs/evidencias/` ⚑

### Fase 12 · Complejidad, mediciones y costes
- [ ] 3 tamaños de entrada: tiempo y memoria
- [ ] Búsqueda lista vs diccionario / consulta sin vs con índice
- [ ] Costes y propuesta de escalado ⚑

### Fase 13 · Memoria y entrega
- [ ] `docs/memoria.md` completa (diccionario, procedencia, calidad, modelo, análisis, 3 conclusiones, reflexión)
- [ ] README reproducible
- [ ] Lista final de comprobación de la guía de entregables
- [ ] `docs/guia-estudio.md`: recorrido completo, archivo por archivo, con autoevaluación
- [ ] Semana de estudio: Daniel repasa la guía y responde `defensa.md` en voz alta
- [ ] Preparar la defensa: flujo completo + una decisión técnica propia ⚑
