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

*(Se completa al cerrar el modelo.)*

## 3bis. Integración geográfica (enunciado §4.3) 🟡

- **Método:** punto en polígono con Shapely 2.0.6 sobre el catálogo Natural Earth del profesor (WGS84 en
  ambos lados). Índice espacial STRtree. Código: `backend/src/geografia.py`.
- **Unicidad de la clave:** `ADM0_A3` es único (177/177) → se usa como `country_id` (no se asume que sea ISO).
- **Regla de frontera:** `covered_by` (un punto sobre la frontera cuenta como dentro). Con varias coincidencias,
  gana el `country_id` menor alfabéticamente y se cuenta. Observado: 0 coincidencias múltiples.
- **Sin país:** NULL = «Sin país asignado» (mar, costa simplificada o territorio no incluido); no se asigna el
  país más cercano ni se usa el texto de `place`. En datos reales: 44 de 225 eventos (20 %).
- **Calidad del catálogo:** USA y SDN tienen polígonos con autointersección (no válidos para GEOS); se reparan
  en memoria con `make_valid` sin cambiar el área. El archivo original no se toca.
- **Verificación:** STRtree y un bucle simple sobre los 177 polígonos dan el mismo país en 185/185 puntos.
- Evidencia: `docs/evidencias/fase6-paises.txt`.
- **Limitación:** las fronteras son simplificadas (escala 1:110M), así que un terremoto costero puede quedar sin país o
  en el país vecino. No se afirma precisión cartográfica.

*(Se completa cuando exista el modelo físico, Fase 4.)*

## 3. Procedencia y registro de consultas 🟡

| Conjunto | Fuente | Periodo y filtros | Extracción |
|---|---|---|---|
| Recientes (muestra de exploración) | Feed USGS `all_day.geojson` | Ventana móvil de 24 h; sin filtros | Una respuesta guardada el 28/10/2026, 11:36 UTC (`metadata.generated`): `docs/material-profesor/ejemplos/feed-all_day-2026-10-28.geojson` (187 eventos) |
| Histórico (muestra) | API FDSN de USGS | Enero de 2025, mag ≥ 4, `eventtype=earthquake`, `orderby=time-asc` | Una consulta (URL del enunciado), 1.413 eventos: `docs/material-profesor/ejemplos/historico-2025-01-mag4.geojson` |
| Geografía | Natural Earth Admin 0, copia del profesor | 177 entidades, escala 1:110 M | `frontend/public/datos/paises.geojson`; SHA-256 verificado contra `FUENTES-Y-LICENCIAS.md` |
| Recientes (producción) | Feed USGS | — | ⬜ Fase 5 |
| Histórico 2025 completo | API FDSN `fdsnws/event/1/query` | 2025-01-01 → 2026-01-01, `minmagnitude=4`, `eventtype=earthquake`, `orderby=time-asc`, mundo | 12 consultas mensuales el 31/10/2026 (~07:19 UTC); 18.302 eventos; ver la tabla siguiente |

**Registro de consultas del histórico** (`data/historico/manifest.json`; regenerable con
`docker compose run --rm productor python -m src.historico_descargar`; cada petición también en `consulta_ingesta`):

| Intervalo [inicio, fin] | `count` previo | Descargados | Extraído (UTC) |
|---|---:|---:|---|
| 2025-01-01 → 2025-02-01 | 1413 | 1413 | 2026-10-31T07:18:36Z |
| 2025-02-01 → 2025-03-01 | 1394 | 1394 | 2026-10-31T07:18:38Z |
| 2025-03-01 → 2025-04-01 | 1178 | 1178 | 2026-10-31T07:18:41Z |
| 2025-04-01 → 2025-05-01 | 1316 | 1316 | 2026-10-31T07:18:43Z |
| 2025-05-01 → 2025-06-01 | 1228 | 1228 | 2026-10-31T07:18:45Z |
| 2025-06-01 → 2025-07-01 | 1156 | 1156 | 2026-10-31T07:18:47Z |
| 2025-07-01 → 2025-08-01 | 2684 | 2684 | 2026-10-31T07:18:49Z |
| 2025-08-01 → 2025-09-01 | 2222 | 2222 | 2026-10-31T07:18:52Z |
| 2025-09-01 → 2025-10-01 | 1604 | 1604 | 2026-10-31T07:18:54Z |
| 2025-10-01 → 2025-11-01 | 1509 | 1509 | 2026-10-31T07:18:57Z |
| 2025-11-01 → 2025-12-01 | 1321 | 1321 | 2026-10-31T07:18:59Z |
| 2025-12-01 → 2026-01-01 | 1277 | 1277 | 2026-10-31T07:19:01Z |
| **Total** | | **18.302** | |

- Ningún intervalo supera 20.000 (máximo: 2.684, julio) → no hizo falta subdividir (el código lo haría automáticamente).
- `count` = descargados en los 12 intervalos → sin truncamiento.
- Repetidos entre archivos (frontera de mes): **0** (la deduplicación está implementada y probada con un caso sintético).
- `minmagnitude=4` **incluye** la magnitud 4,0 (70 eventos con mag = 4,0 en enero) → el filtro equivalente en el periodo reciente es `mag >= 4`.
- Los archivos (13 MB) no se suben a Git (enunciado §12); se regeneran con el comando anterior. El histórico es una
  **instantánea** del catálogo en la fecha de extracción.

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

Primeros datos reales del productor (31/10/2026, 06:48 UTC, 220 eventos por respuesta): exclusiones
`type=explosion` (1) y **`type=quarry blast` (1)**. Es un tipo de evento que no aparecía en la muestra de exploración;
la regla genérica `type != earthquake` lo excluye sin cambiar el código.

### 5.3 Conciliación entre tablas (Consistencia)
Todo lo publicado por el productor debe acabar en `evento_actual` o en `cuarentena`.
Resultado (31/10, ~07:00 UTC): **222 publicados = 221 terremotos + 1 exclusión real (`quarry blast`)**, y
**0 ids perdidos**. Evidencia y consultas: `docs/evidencias/fase5-conciliacion.txt`.
Los casos sintéticos se separan por el prefijo `PRUEBA-`. Sin esa marca, la conciliación habría dado un falso descuadre.

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
## 7. Análisis y conclusiones 🟡

**Referencia histórica (comparación §8.4):** 2025, mundial, `type = earthquake`, `mag >= 4` → **18.302 eventos**
→ **media diaria = 18.302 / 365 = 50,14** (el denominador incluye los días con cero eventos, FAQ 23).
Evidencia: `docs/evidencias/fase7-historico.txt`.

**Candidatas a conclusión (pendientes de redactar con filtros, periodo y denominador):**
1. ✅ **El pico de julio y agosto de 2025 se concentra en Kamchatka.** *Datos:* histórico 2025, mundial, `type = earthquake`,
   `mag >= 4`, 18.302 eventos; zona = rectángulo lat 45–60, lon 150–170 (aproximación propia). Entre enero y junio la zona
   registra 19,3 eventos/mes de media; en julio 1.375 (×71) y en agosto 1.254 (×65), tras el M8,8 del 29/07/2025, y después
   baja mes a mes (596, 287, 233, 114). En el resto del mundo no hay pico en julio (968–1.393 al mes). La zona aporta el
   **21,7 %** de los eventos del año. *Interpretación:* el aumento es compatible con una secuencia de réplicas localizada,
   no con un aumento global. *Consecuencia para la comparación:* la media diaria de 2025 (50,14) incluye esta secuencia;
   sin la zona sería 39,25. Hay que tenerlo en cuenta al comparar el periodo reciente con 2025. No es una predicción ni
   una evaluación de riesgo. Evidencia: `docs/evidencias/fase7-historico.txt`.
2. *Sesgo de cobertura:* en el feed de 24 h sin filtro de magnitud, el 77 % de los eventos son de EE. UU. (redes de
   detección densas). Para comparar regiones hay que filtrar por magnitud (Fase 6).
3. ✅ **El recuento de las últimas 24 h está en la parte baja del rango de 2025, pero no es excepcional; la comparación
   con la media exagera la diferencia.** *Datos:* periodo 30/10/2026 09:28 → 31/10/2026 09:28 UTC, mundial, earthquake,
   mag ≥ 4 → **25** eventos. Media diaria de 2025 = 50,14 (−50,1 %); pero la **mediana** de los 365 días de 2025 es 43 y el
   p10 es 31; solo **10 de 365 días (2,7 %)** tuvieron 25 o menos. Excluyendo la secuencia de Kamchatka: media 39,25,
   mediana 37, p10 26 y **29 días (7,9 %)** con 25 o menos. Con mag ≥ 4,5: 13 frente a 23,45 (−44,6 %). *Interpretación:* la
   media está inflada por días extremos (máximo 645, el día del M8,8); la mediana y los percentiles describen mejor un día
   típico. *Limitaciones:* un solo día es una muestra muy pequeña; el feed en tiempo real puede completarse más tarde
   (pendiente: volver a descargar el periodo del catálogo hacia el 03/11 para medirlo). No es una predicción ni una
   evaluación de riesgo. Evidencia: `docs/evidencias/fase8-comparacion-historica.txt`.
   → *Mejora aplicada:* `/api/estadisticas` devuelve ahora la mediana, el p10, el p90 y el % de días de 2025 con un recuento ≤ al reciente.
## 8. Complejidad, mediciones, costes y mejoras ⬜

*Datos ya recogidos:*
- Búsqueda de versiones: diccionario O(1) de media frente a lista O(N) (productor, D19).
- Integración geográfica: STRtree frente a bucle sobre los 177 polígonos → 22,3 ms frente a 224,3 ms para 185 puntos
  (≈10x; entorno de Claude, medición única → hay que repetirla en el equipo de Daniel con 3 tamaños).
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
| D19 | Estado del productor: diccionario en memoria (O(1)) + copia en `version_publicada` | Solo lista o solo BD | Velocidad en cada ciclo y persistencia ante reinicios | Enunciado §10; FAQ 10 y 33 |
| D20 | Reintentos 2/4/8 s solo para fallos temporales (timeout, red, 429, 5xx, JSON); 4xx no se reintenta | Reintentar siempre / nunca | Espera progresiva sin insistir en errores que no se arreglan esperando | Enunciado §5.6 |
| D21 | Originales `.geojson.gz` en `data/raw/`, guardados solo si cambian los `features`, con retención de 24 h | Guardar cada respuesta sin comprimir | Conservar el original sin copias idénticas; `metadata.generated` cambia siempre, por eso se compara solo `features` | Enunciado §5.2 |
| D22 | No publicar features sin `id` o `updated` (se cuentan en `consulta_ingesta.error`) | Publicarlos | Sin id/updated no hay control de versiones y se reenviarían cada minuto | Enunciado §5.3 |
| D23 | Shapely + STRtree para el punto en polígono | GeoPandas `sjoin`; bucle simple | Dependencia ligera; mismo resultado que el bucle y ≈10x más rápido | Enunciado §4.3 y §10 |
| D24 | Regla de frontera `covered_by` + desempate alfabético | `within` (excluye el borde); el país más cercano | Determinista y documentada; el país más cercano está prohibido | Enunciado §4.3 |
| D25 | Reparar USA/SDN con `make_valid` en memoria | Editar el GeoJSON; ignorar el error | No modificar el material del profesor; área idéntica | — |
| D26 | Fijar también `numpy` (dependencia indirecta) | Solo las dependencias directas | Build reproducible | Enunciado §9 |
| D27 | Histórico en dos pasos: descargar (archivos + manifiesto) y cargar | Descargar y cargar a la vez | «Descarga una vez y reutiliza»; la carga se puede repetir sin volver a pedir a USGS | Enunciado §4.2 |
| D28 | `count` previo y división automática del intervalo si > 20.000 | Confiar en que ningún mes lo supere | No truncar en silencio | Enunciado §4.2; documentación FDSN (`limit`) |
| D29 | Carga del histórico por Kafka con el mismo consumidor (`source = 'usgs-fdsn'`) | Proceso batch directo a PostgreSQL | Una sola ruta de calidad, país e idempotencia para los dos accesos a USGS | FAQ 21 |
| D30 | Comparación con `mag >= 4` en los dos periodos | `mag > 4` | Es lo que hace realmente `minmagnitude=4` (incluye 4,0) | Muestra de enero |
| D31 | Con `min_mag`, contar aparte los eventos sin magnitud (`magnitud_excluidos_por_filtro`) | Esconderlos | El contrato exige contabilizarlos por separado; detectado en la revisión del bloque 4 del panel | Contrato API |
| D32 | La API devuelve `cobertura_feed_desde` (primera ingesta correcta − 24 h) y `periodo_cubierto` | Que el panel adivine la cobertura | Avisar con exactitud cuando un periodo no está cubierto por datos y el recuento puede ser incompleto. Limitación: no detecta huecos por paradas > 24 h (recuperables con el catálogo, `updatedafter`) | Enunciado §5 y §8.4 |

### Evidencia del problema de duplicados (Fase 3)
Al enviar dos veces el mismo evento (`us7000ttlm`, mismo `updated`), Kafka lo almacenó en los offsets 0 y 1
de la partición 1: **Kafka no deduplica**. Como el feed devuelve toda la ventana de 24 h en cada consulta,
un consumidor ingenuo insertaría cada minuto los ~187 eventos de nuevo (≈ 269.280 filas repetidas al día).
Esto justifica el control de versiones en el productor y la escritura idempotente en el consumidor (Fase 5).
