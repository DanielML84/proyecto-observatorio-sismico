# Contrato del mensaje Kafka · versión 1

> Acuerdo entre el **productor** (quien escribe) y el **consumidor** (quien lee).
> Si cambia la forma del mensaje, se sube `schema_version` y se actualiza este documento **antes** que el código.

## Topics

| Topic | Para qué | Quién escribe |
|---|---|---|
| `terremotos.live` | Novedades del feed `all_day.geojson` | Productor live (cada 60 s) |
| `terremotos.replay` | Reproducción acelerada de una selección histórica (demostración) | Productor de replay (Fase 11) |

Separar los topics cumple el aislamiento de la reproducción que pide el enunciado (§11).
La carga del histórico de 2025 (¿por Kafka o en batch?) se decidirá en la Fase 7 (FAQ 21).

## Clave del mensaje

`key` = el `id` del evento USGS en UTF-8 (por ejemplo, `us7000ttlm`).
**Por qué:** lo exige el enunciado (§5.4), y Kafka manda todos los mensajes con la misma clave a la
misma partición, así que **las versiones de un mismo terremoto llegan en orden**. Aun así, el orden NO
sustituye la comparación de versiones (enunciado §7).

## Valor del mensaje (JSON en UTF-8)

| Campo | Tipo | Significado | Ejemplo |
|---|---|---|---|
| `schema_version` | entero | Versión de este contrato | `1` |
| `source` | texto | De dónde viene el evento | `"usgs-feed-all_day"` o `"usgs-fdsn"` |
| `mode` | texto | `"live"` o `"replay"` | `"live"` |
| `ingested_at` | texto ISO 8601 UTC | Cuándo lo descargó el productor (**hora de proceso, no del terremoto**) | `"2026-10-30T18:40:00.123Z"` |
| `replayed_at` | texto ISO 8601 UTC o `null` | Solo en replay: cuándo se reenvió. Las fechas originales del evento no se tocan (§11) | `null` |
| `event` | objeto | **El Feature de USGS tal cual, sin modificar** | ver abajo |

## Reglas

1. **El productor no transforma ni filtra.** Publica cada versión nueva o revisada (`id` + `updated`)
   tal como la entrega USGS, incluidas las explosiones. El consumidor valida, filtra y registra el motivo.
2. **Las fechas del evento siguen en milisegundos Unix** dentro de `event`; la conversión a UTC la hace el consumidor.
3. **Un mensaje = una versión de un evento.** Si USGS revisa un terremoto, sale otro mensaje con la misma clave y un `updated` mayor.
4. Puede llegar **el mismo mensaje dos veces** (si el productor cae justo después de publicar). El consumidor debe tolerarlo (FAQ 10 y 13).

## Ejemplo real

Construido con el evento `us7000ttlm` de la muestra del 28/10. Se omiten propiedades por brevedad;
en el mensaje real van todas.

```text
key:   us7000ttlm
value:
{
  "schema_version": 1,
  "source": "usgs-feed-all_day",
  "mode": "live",
  "ingested_at": "2026-10-28T11:36:30.000Z",
  "replayed_at": null,
  "event": {
    "type": "Feature",
    "properties": {
      "mag": 6,
      "place": "214 km NW of Port-Olry, Vanuatu",
      "time": 1793154105806,
      "updated": 1793162671840,
      "status": "reviewed",
      "magType": "mww",
      "type": "earthquake",
      "ids": ",us7000ttlm,"
    },
    "geometry": {
      "type": "Point",
      "coordinates": [
        165.446,
        -13.9312,
        10
      ]
    },
    "id": "us7000ttlm"
  }
}
```
