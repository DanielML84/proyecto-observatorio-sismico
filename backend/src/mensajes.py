"""Construcción de mensajes según docs/contrato-mensaje.md (versión 1).

Este módulo es la ÚNICA puerta para crear mensajes: si el contrato cambia, se cambia aquí.
"""

from datetime import datetime, timezone  # fechas con zona horaria (siempre UTC)

SCHEMA_VERSION = 1  # versión del contrato; subirla si cambia la forma del mensaje


def ahora_utc_iso() -> str:
    """Hora actual en UTC como texto ISO 8601 con milisegundos, p. ej. '2026-10-30T18:40:00.123Z'."""
    ahora = datetime.now(timezone.utc)
    return ahora.strftime("%Y-%m-%dT%H:%M:%S.") + f"{ahora.microsecond // 1000:03d}Z"


def construir_mensaje(evento: dict, source: str, mode: str = "live", replayed_at: str | None = None) -> dict:
    """Envuelve un Feature de USGS (sin modificarlo) con los metadatos del contrato."""
    if mode not in ("live", "replay"):
        raise ValueError(f"mode inválido: {mode!r}")
    return {
        "schema_version": SCHEMA_VERSION,
        "source": source,               # de dónde viene (feed, histórico...)
        "mode": mode,                   # live o replay
        "ingested_at": ahora_utc_iso(), # cuándo lo obtuvimos NOSOTROS (hora de proceso)
        "replayed_at": replayed_at,     # solo en replay
        "event": evento,                # el terremoto tal cual lo da USGS
    }
