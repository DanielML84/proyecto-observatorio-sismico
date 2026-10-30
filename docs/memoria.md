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

## 5. Calidad de datos ⬜
## 6. Modelo conceptual, lógico y físico ⬜
## 7. Análisis y conclusiones ⬜
## 8. Complejidad, mediciones, costes y mejoras ⬜
## 9. Evidencias de las pruebas de aceptación ⬜
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
