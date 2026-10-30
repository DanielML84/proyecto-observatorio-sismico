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
- [ ] `docs/contrato-mensaje.md`: formato del mensaje Kafka ⚑

### Fase 3 · Kafka + productor + consumidor mínimos  *(FAQ paso 3)*
- [x] `compose.yaml` con Kafka (KRaft, volumen, retención limitada)
- [x] Prueba con consola: topic `pruebas`, productor → consumidor (evidencias `fase3-*.png`)
- [ ] Comprobar persistencia con `docker compose down` + `up`
- [ ] Productor mínimo que publica un evento de prueba
- [ ] Consumidor mínimo que lo muestra en el log
- [ ] Evidencia: log del consumidor ⚑

## Semana 2 · 04/11 – 10/11 · Datos correctos

### Fase 4 · PostgreSQL y modelo  *(FAQ paso 4)*
- [ ] Modelo conceptual → lógico → físico (SQL en `sql/`)
- [ ] Tablas: evento actual, versiones, país, fecha, cuarentena, estado de ingesta
- [ ] Consumidor escribe en PostgreSQL → consulta SQL lo muestra ⚑

### Fase 5 · Duplicados y revisiones  *(FAQ paso 5 · lo más importante)*
- [ ] Productor real: USGS cada 60 s, compara `id` + `updated`, reintentos
- [ ] Consumidor idempotente: transacción + upsert + offset después de escribir
- [ ] Probar la secuencia de la FAQ pregunta 12 (E1, E1, E1', E1, E2) ⚑

### Fase 6 · País y calidad  *(FAQ paso 6)*
- [ ] Punto en polígono (Shapely/GeoPandas) → `country_id` o «Sin país asignado»
- [ ] Reglas de validación + cuarentena con motivo
- [ ] Filtrar `type == earthquake` y registrar exclusiones ⚑

### Fase 7 · Histórico 2025
- [ ] Descarga por meses (mag ≥ 4), registro de consultas, deduplicación
- [ ] Carga con las mismas reglas de limpieza ⚑

### Fase 8 · API FastAPI  *(FAQ paso 7)*
- [ ] `/api/eventos` según contrato, con filtros
- [ ] `/api/salud` y `/api/estadisticas`
- [ ] CORS ⚑

## Semana 3 · 11/11 – 18/11 · Panel, pruebas y memoria

### Fase 9 · Panel Angular  *(FAQ pasos 8–9)*
- [ ] Conectar a la API (modo `api`)
- [ ] Filtros (fecha, magnitud, país), tabla, gráficos, comparación histórica
- [ ] Estado del sistema (última ingesta, avisos) ⚑

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
- [ ] Preparar la defensa: flujo completo + una decisión técnica propia ⚑
