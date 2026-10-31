"""Reglas de VALIDACIÓN y TRANSFORMACIÓN del consumidor (enunciado §6).

Función principal: `validar(mensaje)` recibe el mensaje ya leído de Kafka (dict) y devuelve UNA de tres cosas:
  - Valido(campos)            -> se guarda en evento_actual / evento_version
  - Rechazo('excluido', motivo) -> válido pero fuera de alcance (type != earthquake)
  - Rechazo('invalido', motivo) -> no se puede tratar -> cuarentena

Funciones "puras": no tocan Kafka ni la base de datos, así se pueden probar solas.
Cada regla tiene un MOTIVO con nombre fijo, que es lo que se guarda en cuarentena y se cuenta en la memoria.
"""

import math
from dataclasses import dataclass
from datetime import date, datetime, timezone

# Rango de la dimensión fecha (sql/01_esquema.sql). Fuera de él no hay fila en `fecha` a la que apuntar.
FECHA_MIN = date(2024, 1, 1)
FECHA_MAX = date(2027, 12, 31)


@dataclass
class Valido:
    campos: dict            # columnas listas para la base de datos


@dataclass
class Rechazo:
    tipo: str               # 'invalido' o 'excluido'
    motivo: str             # p. ej. 'lat_fuera_de_rango', 'type=explosion'
    event_id: str | None    # si se pudo leer


def _es_entero(x) -> bool:
    """True si es un entero de verdad. Ojo: en Python True/False son enteros; los excluimos."""
    return isinstance(x, int) and not isinstance(x, bool)


def _es_numero(x) -> bool:
    """True si es int o float finito (no NaN ni infinito) y no es booleano."""
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def ms_a_utc(ms: int) -> datetime:
    """Milisegundos Unix (como los da USGS) -> fecha/hora UTC. Se divide entre 1000 porque Python usa segundos (FAQ 9)."""
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)


def validar(mensaje: dict) -> Valido | Rechazo:
    # --- 1. Sobre: ¿cumple el contrato del mensaje? (docs/contrato-mensaje.md)
    if not isinstance(mensaje, dict) or mensaje.get("schema_version") != 1:
        return Rechazo("invalido", "schema_version_desconocida", None)
    evento = mensaje.get("event")
    if not isinstance(evento, dict):
        return Rechazo("invalido", "sin_evento", None)

    # --- 2. Identidad y versión: sin id o sin updated no podemos controlar duplicados
    event_id = evento.get("id")
    if not isinstance(event_id, str) or not event_id.strip():
        return Rechazo("invalido", "sin_id", None)
    props = evento.get("properties")
    if not isinstance(props, dict):
        return Rechazo("invalido", "sin_properties", event_id)
    if not _es_entero(props.get("updated")):
        return Rechazo("invalido", "updated_invalido", event_id)
    if not _es_entero(props.get("time")):
        return Rechazo("invalido", "time_invalido", event_id)

    # --- 3. Tipo de evento: solo terremotos (enunciado §4.1). No es un error: se EXCLUYE y se registra el motivo.
    tipo_evento = props.get("type")
    if tipo_evento != "earthquake":
        return Rechazo("excluido", f"type={tipo_evento}", event_id)

    # --- 4. Geometría: debe ser un Point con al menos [lon, lat]
    geom = evento.get("geometry")
    if not isinstance(geom, dict) or geom.get("type") != "Point":
        return Rechazo("invalido", "geometria_no_point", event_id)
    coords = geom.get("coordinates")
    if not isinstance(coords, list) or len(coords) < 2:
        return Rechazo("invalido", "coordenadas_incompletas", event_id)
    lon, lat = coords[0], coords[1]
    if not _es_numero(lon) or not _es_numero(lat):
        return Rechazo("invalido", "coordenadas_no_numericas", event_id)
    if not (-90 <= lat <= 90):
        return Rechazo("invalido", "lat_fuera_de_rango", event_id)
    if not (-180 <= lon <= 180):
        return Rechazo("invalido", "lon_fuera_de_rango", event_id)

    # --- 5. Profundidad (3ª coordenada): puede faltar (-> NULL). Negativa se ACEPTA (USGS la explica; memoria D3).
    depth = coords[2] if len(coords) >= 3 else None
    if depth is not None and not _es_numero(depth):
        return Rechazo("invalido", "profundidad_no_numerica", event_id)

    # --- 6. Magnitud: NULL se conserva (no es 0, FAQ 16). Negativa se acepta. Si viene texto u otra cosa -> inválida.
    mag = props.get("mag")
    if mag is not None and not _es_numero(mag):
        return Rechazo("invalido", "mag_no_numerica", event_id)

    # --- 7. Transformación: fechas a UTC y día para la dimensión fecha
    event_time = ms_a_utc(props["time"])
    if not (FECHA_MIN <= event_time.date() <= FECHA_MAX):
        return Rechazo("invalido", "fecha_fuera_de_dimension", event_id)

    return Valido({
        "event_id": event_id,
        "updated_ms": props["updated"],
        "event_time": event_time,
        "updated_at": ms_a_utc(props["updated"]),
        "fecha_id": event_time.date(),
        "mag": float(mag) if mag is not None else None,
        "mag_type": props.get("magType"),
        "depth_km": float(depth) if depth is not None else None,
        "lon": float(lon),
        "lat": float(lat),
        "place": props.get("place"),
        "status": props.get("status"),
        "country_id": None,                      # se asignará en la Fase 6 (punto en polígono)
        "source": mensaje.get("source") or "desconocida",
        "ingested_at": mensaje.get("ingested_at"),
    })
