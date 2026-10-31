# Memoria · Observatorio de actividad sísmica

> Documento vivo: se completa al terminar cada fase. Sigue el índice de la guía de entregables (§2).
> Marcas: ✅ redactado · 🟡 en curso · ⬜ pendiente.
> Regla: todas las cifras salen de código o consultas del repositorio, nunca escritas a mano.

---

## 1. Objetivo y funcionamiento general 🟡

**Pregunta:** ¿dónde se está registrando actividad sísmica y cómo se compara con un periodo
histórico equivalente?

```text
USGS feed (cada 60 s) → productor (Python, aiokafka) → Kafka → consumidor (Python, aiokafka)
→ PostgreSQL → API (FastAPI) → ngrok (HTTPS) → panel (Angular + Leaflet, Netlify)
```

**Alcance (provisional, propuesta del enunciado §4.2):** histórico del año 2025, ámbito mundial,
magnitud ≥ 4 y tipo `earthquake`. Los mismos filtros se aplican al periodo reciente para la comparación.

**Material reutilizado y desarrollo propio:** el material del profesor está sin modificar en
`docs/material-profesor/` y en el primer commit (`5c052ff`). Todo lo posterior es desarrollo propio
o modificación, y queda trazado en el historial de Git.

## 2. Diccionario de datos ⬜

*(Se completa cuando exista el modelo físico, Fase 4.)*

## 3. Procedencia y registro de consultas 🟡

| Conjunto | Fuente | Periodo y filtros | Extracción |
|---|---|---|---|
| Recientes (muestra de exploración) | Feed USGS `all_day.geojson` | Ventana móvil de 24 h; sin filtros | Una respuesta guardada el 28/10/2026, 11:36 UTC (`metadata.generated`): `docs/material-profesor/ejemplos/feed-all_day-2026-10-28.geojson` (187 eventos) |
| Histórico (muestra) | API FDSN de USGS | Enero de 2025, mag ≥ 4, `eventtype=earthquake`, `orderby=time-asc` | Una consulta (URL del enunciado), 1.413 eventos: `docs/material-profesor/ejemplos/historico-2025-01-mag4.geojson` |
| Geografía | Natural Earth Admin 0, copia del profesor | 177 entidades, escala 1:110 M | `frontend/public/datos/paises.geojson`; SHA-256 verificado contra `FUENTES-Y-LICENCIAS.md` |
| Recientes (producción) | Feed USGS | — | ⬜ Fase 5 |
| Histórico 2025 completo | API FDSN | — | ⬜ Fase 7 |

**Características de la API FDSN relevantes** (documentación oficial de `fdsnws/event/1`):
- Máximo de 20.000 eventos por consulta. Si se supera, responde **HTTP 400** (no trunca).
- El método `count` permite conocer el tamaño de una consulta antes de descargarla.
- `starttime` («on or after») y `endtime` («on or before») son **inclusivos** → hay que deduplicar
  los eventos que caen en el límite entre intervalos.
- `updatedafter` permite recuperar los cambios posteriores a una fecha (útil tras una parada de más de 24 h).

## 4. Exploración de la fuente reciente 🟡

Notebook: `analisis/01_exploracion_feed.ipynb`. Muestra: una respuesta del feed con 187 eventos.

| Comprobación | Resultado |
|---|---|
| Estructura | `FeatureCollection` con `metadata`, `bbox` y `features[]`; cada feature con `id`, `geometry` y `properties` (26 campos) |
| Unicidad dentro de la respuesta | 187 `id` únicos de 187 |
| Tipo de evento | 185 `earthquake` y 2 `explosion` |
| Geometría | 187 `Point` con 3 coordenadas `[lon, lat, profundidad_km]`; 0 fuera de rango |
| Magnitud | 0,22 a 6,0; sin nulos en esta muestra; 28 con mag ≥ 4 |
| Tipos de magnitud | `ml` 108 · `md` 51 · `mb` 22 · `mww` 6 |
| Profundidad | −2,31 a 509,07 km; 3 negativas (2 explosiones y 1 terremoto) |
| Estado de revisión | 120 `automatic` y 67 `reviewed` |
| `updated − time` | Mediana de 3,6 min; máximo de 925,8 min |
| Identificadores asociados (`ids`) | 8 eventos con más de un id |
| Campos poco informados | `tz` 0 %, `alert` 3,2 %, `mmi` 4,8 %, `cdi` y `felt` 8,6 % |

**Profundidad negativa:** según las preguntas frecuentes de USGS, un evento muy superficial puede
reportarse con profundidad negativa porque la profundidad se calcula respecto al geoide WGS84, y puede
ser un artefacto de la baja resolución en eventos someros.
Fuente: https://usgs.gov/faqs/what-does-it-mean-earthquake-occurred-a-depth-0-km-how-can-earthquake-have-a-negative-depth
→ **Decisión:** se conserva y no se rechaza.

**Problema técnico encontrado:** al aplanar con `pd.json_normalize` aparecen dos columnas `type`
(la del Feature y `properties.type`). Se renombran a `feature_type` y `geom_type`.

## 5. Calidad de datos 🟡

### 5.1 Reglas del consumidor (`backend/src/validacion.py`)
| # | Regla | Resultado si falla | Motivo registrado | Dimensión |
|---|---|---|---|---|
| 1 | Mensaje con `schema_version = 1` y `event` | Cuarentena | `schema_version_desconocida`, `sin_evento` | Validez |
| 2 | `id` de texto no vacío | Cuarentena | `sin_id` | Unicidad |
| 3 | `updated` y `time` enteros (ms) | Cuarentena | `updated_invalido`, `time_invalido` | Validez |
| 4 | `type == "earthquake"` | **Excluido** (no es un error) | `type=<valor>` | Consistencia (alcance) |
| 5 | Geometría `Point` con lon/lat numéricas | Cuarentena | `geometria_no_point`, `coordenadas_*` | Validez |
| 6 | lat ∈ [−90, 90], lon ∈ [−180, 180] | Cuarentena | `lat_fuera_de_rango`, `lon_fuera_de_rango` | Validez |
| 7 | Profundidad numérica si existe (negativa **permitida**) | Cuarentena | `profundidad_no_numerica` | Validez |
| 8 | Magnitud numérica si existe (NULL y negativa **permitidas**) | Cuarentena | `mag_no_numerica` | Completitud / Validez |
| 9 | Fecha del evento dentro de la dimensión fecha (2024–2027) | Cuarentena | `fecha_fuera_de_dimension` | Consistencia |
| — | Mismo `(id, updated)` ya guardado | Se ignora (sin error) | log `version_repetida` | Unicidad |
| — | `updated` anterior al vigente | Se guarda en el historial; NO cambia el estado actual | log `version_antigua` | Consistencia |

**Transformaciones:** `time` y `updated` (ms) → `TIMESTAMPTZ` UTC, conservando `updated_ms`; `fecha_id` = día
UTC de ocurrencia; valores originales en `evento_version.raw` (JSONB) y en `cuarentena.raw`.

### 5.2 Prueba de las reglas sobre datos reales
Muestra del feed del 28/10 (187 eventos): **185 válidos, 2 excluidos (`type=explosion`), 0 en cuarentena**.

*(El análisis completo de las 6 dimensiones sobre los datos almacenados se hará con consultas SQL cuando el productor real lleve tiempo funcionando.)*
## 6. Modelo conceptual, lógico y físico 🟡

SQL: [`sql/01_esquema.sql`](../sql/01_esquema.sql). Evidencia: `docs/evidencias/fase4-postgres-esquema.txt`.

**Conceptual:** un *terremoto* ocurre en un *día* UTC, puede estar en un *país* (0 o 1) y tiene una o
varias *versiones* (las publicaciones sucesivas de USGS). Además, el sistema registra *rechazos* (cuarentena),
la *última versión publicada* por el productor y las *consultas* a USGS.

**Lógico (grano y claves):**

| Tabla | Tipo | Una fila = | Clave | Relaciones |
|---|---|---|---|---|
| `evento_actual` | Hecho | un terremoto con su versión más reciente | PK `event_id` | FK `fecha_id` → `fecha`; FK `country_id` → `pais` (admite NULL) |
| `evento_version` | Historial | una versión observada | PK `(event_id, updated_ms)` | — |
| `pais` | Dimensión | una entidad de Natural Earth | PK `country_id` (ADM0_A3) | — |
| `fecha` | Dimensión | un día UTC (2024–2027) | PK `fecha_id` | — |
| `cuarentena` | Calidad | un mensaje inválido o excluido | PK `id`; UNIQUE `(topic, partición, offset)` | — |
| `version_publicada` | Estado del productor | la última versión publicada de cada evento | PK `event_id` | — |
| `consulta_ingesta` | Procedencia | una petición a USGS | PK `id` | — |

**Físico:** tipos de PostgreSQL 17 (`TIMESTAMPTZ` en UTC, `BIGINT` para los milisegundos de USGS,
`DOUBLE PRECISION` para la magnitud y las coordenadas, `JSONB` para el original). Restricciones `CHECK` de rango en `lat`/`lon`.

**Índices (justificación provisional; medición en la Fase 12):**
- `ix_evento_actual_time (event_time)`: la API filtra por intervalos de tiempo y agrupa por ventanas horarias.
- `ix_evento_actual_country (country_id)`: recuentos y filtro por país.
- `ix_consulta_ok_fecha (ok, solicitada_at DESC)`: obtener la última consulta correcta para el estado del sistema.

**Comprobación:** insertar dos veces el mismo `event_id` → `duplicate key value violates unique constraint`.
## 7. Análisis y conclusiones ⬜
## 8. Complejidad, mediciones, costes y mejoras ⬜
## 9. Evidencias de las pruebas de aceptación 🟡

| Prueba (enunciado §11) | Esperado | Observado | Evidencia |
|---|---|---|---|
| Recibir un evento nuevo | Una fila actual | `PRUEBA-E1 -> insertado`; 1 fila | `fase5-faq12-idempotencia.txt` |
| Reenviar la misma versión | No aumenta el número | `ignorado: version_repetida`; sigue 1 fila | ídem |
| Recibir una versión posterior | Cambian los datos actuales | `actualizado`; mag 4,2 → 4,6 | ídem |
| Recibir después una versión antigua | No sustituye a la más reciente | `ignorado`; mag sigue en 4,6 | ídem |
| Magnitud nula | Se conserva y se muestra ND | Guardada con `mag` NULL (panel: pendiente) | ídem |
| Coordenadas inválidas | Cuarentena y motivo | `lat_fuera_de_rango`, offset 4 | ídem |
| Evento marítimo | Sin país; permanece | ⬜ Fase 6 | |
| Reiniciar consumidor | Reanuda sin duplicar | ⬜ | |
| Cerrar / reabrir el túnel | Aviso y recuperación | ⬜ Fase 10 | |
| Reproducción histórica | Por Kafka, aislada | ⬜ Fase 11 | |

Los casos son **sintéticos** (`PRUEBA-*`, `source = 'prueba-faq12'`), separados de los datos reales (enunciado §6).
## 10. Reproducción histórica ⬜

---

## Anexo A · Registro de decisiones técnicas

| # | Decisión | Alternativas | Motivo | Referencia |
|---|---|---|---|---|
| D1 | Material del profesor sin modificar en un primer commit separado | Mezclarlo con el código propio | Distinguir lo reutilizado de lo propio | Guía §1.1 |
| D2 | `.gitattributes` con `eol=lf` | Dejar los finales CRLF de Windows | Los contenedores son Linux; un script con CRLF puede fallar | Bitácora, sesión 1 |
| D3 | Conservar las profundidades negativas | Rechazarlas | USGS las explica; el enunciado prohíbe rechazarlas sin estudiarlas | Enunciado §6; FAQ de USGS |
| D4 | Exploración en un notebook con pandas | Script `.py` | Código y resultados juntos, reproducibles, en el estilo de clase | — |
| D5 | Kafka con volumen persistente (`kafka-data`) | Datos efímeros, como en binance-kafka | Los mensajes deben sobrevivir a un reinicio | Enunciado §9 |
| D6 | Retención de 7 días o 512 MB por partición | Retención por defecto o ilimitada | Retención limitada exigida; cubre una parada de fin de semana del consumidor | Enunciado §9; FAQ 11 |
| D7 | Kafka sin puertos publicados al host | Publicar 9092 como en binance-kafka | Solo lo usan los contenedores; no se expone el broker | Enunciado §2 y §9 |
| D8 | Creación automática de topics desactivada | Activada | Un nombre de topic mal escrito no crea un topic nuevo en silencio | — |
| D9 | El productor publica el evento original sin filtrar ni transformar; el consumidor valida y filtra | Que el productor descarte las explosiones | Una responsabilidad por componente; la exclusión y su motivo quedan registrados en la BD | Enunciado §2, §4.1 y §5; `docs/contrato-mensaje.md` |
| D10 | Topics separados `terremotos.live` y `terremotos.replay` | Un único topic con un campo `mode` | Aislamiento de la reproducción | Enunciado §11; FAQ 32 |
| D11 | Una sola imagen Python (`backend/`) con un comando distinto por servicio | Una imagen por servicio | Menos mantenimiento; dependencias comunes | Enunciado §2 |
| D12 | Servicio `kafka-init` que crea los topics (`--if-not-exists`) y termina | Que el productor cree el topic (como en binance-kafka) | Topics declarados en un solo sitio y visibles; el arranque es repetible | — |
| D13 | Consumidor con `enable_auto_commit=False` y commit del offset tras procesar | Commit automático | Base del procesamiento «al menos una vez» con escritura idempotente | Enunciado §7; FAQ 13 |
| D14 | 3 particiones por topic | 1 partición | El orden se garantiza por clave (id); permite repartir la carga entre varios consumidores si crece el volumen | — |
| D15 | `updated` guardado en milisegundos (`BIGINT`) además de como fecha | Solo `TIMESTAMPTZ` | Se compara exactamente el valor de la fuente, sin conversión | Enunciado §5.3 |
| D16 | Estado del productor en PostgreSQL (`version_publicada`) | Diccionario en memoria o archivo | Debe sobrevivir a un reinicio | FAQ 10 |
| D17 | Una tabla `cuarentena` con `tipo` invalido/excluido | Dos tablas | Un único sitio para todo lo que no entra en el análisis, con su motivo y referencia al mensaje | Enunciado §4.1 y §6 |
| D18 | Dimensión fecha precargada (2024–2027) con `generate_series` | Calcular la fecha en cada consulta | Modelo dimensional (como en clase); agregar por día/mes/día de la semana | FAQ 20; sesión 5 |

### Evidencia del problema de duplicados (Fase 3)
Al enviar dos veces el mismo evento (`us7000ttlm`, mismo `updated`), Kafka lo almacenó en los offsets 0 y 1
de la partición 1: **Kafka no deduplica**. Como el feed devuelve toda la ventana de 24 h en cada consulta,
un consumidor ingenuo insertaría cada minuto los ~187 eventos de nuevo (≈ 269.280 filas repetidas al día).
Esto justifica el control de versiones en el productor y la escritura idempotente en el consumidor (Fase 5).
