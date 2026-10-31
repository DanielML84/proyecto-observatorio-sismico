"""Productor REAL: consulta el feed de USGS cada INTERVALO_S segundos y publica en Kafka SOLO las novedades.

Ciclo (enunciado §5):
  1. Descargar all_day.geojson (con timeout y reintentos con espera progresiva ante 429/5xx/timeout/JSON roto)
  2. Guardar el GeoJSON original comprimido en data/raw/ (solo si cambió) y borrar los de más de RAW_RETENCION_H horas
  3. Para cada terremoto, comparar (id, updated) con lo ya publicado:
        id desconocido           -> publicar
        updated igual            -> NO publicar (ya está)
        updated posterior        -> publicar (revisión)
        updated anterior         -> NO publicar (versión atrasada)
  4. Publicar, ESPERAR confirmación de Kafka y SOLO ENTONCES marcar como publicada en PostgreSQL
  5. Registrar la consulta (ok o error) en consulta_ingesta
Un fallo nunca borra el estado anterior: simplemente se registra y se reintenta en el siguiente ciclo.

Variables de entorno: KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC, USGS_FEED_URL, INTERVALO_S, HTTP_TIMEOUT_S,
RAW_DIR, RAW_RETENCION_H y las de PostgreSQL.
"""

import asyncio
import gzip
import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from aiokafka import AIOKafkaProducer

from src import db
from src.mensajes import construir_mensaje

BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC = os.environ.get("KAFKA_TOPIC", "terremotos.live")
URL = os.environ.get("USGS_FEED_URL", "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson")
INTERVALO_S = int(os.environ.get("INTERVALO_S", "60"))
HTTP_TIMEOUT_S = int(os.environ.get("HTTP_TIMEOUT_S", "20"))
RAW_DIR = Path(os.environ.get("RAW_DIR", "/data/raw"))
RAW_RETENCION_H = int(os.environ.get("RAW_RETENCION_H", "24"))
FUENTE = "usgs-feed-all_day"
REINTENTOS = 3                 # además del primer intento -> hasta 4 intentos por ciclo
LATIDO = Path("/tmp/latido")   # archivo que el healthcheck de Docker comprueba (si no se actualiza, el productor está atascado)


class ErrorReintentable(Exception):
    """Fallo temporal: merece la pena volver a intentarlo (timeout, red, 429, 5xx, JSON roto)."""
    def __init__(self, mensaje, http_status=None):
        super().__init__(mensaje)
        self.http_status = http_status


class ErrorDefinitivo(Exception):
    """Fallo que no se arregla esperando (p. ej. 404)."""
    def __init__(self, mensaje, http_status=None):
        super().__init__(mensaje)
        self.http_status = http_status


def _descargar_sync() -> tuple[int, bytes]:
    """Petición HTTP GET normal (bloqueante). Se ejecuta en un hilo aparte para no frenar el bucle asíncrono."""
    peticion = urllib.request.Request(URL, headers={"User-Agent": "observatorio-sismico (proyecto educativo)"})
    try:
        with urllib.request.urlopen(peticion, timeout=HTTP_TIMEOUT_S) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:                      # el servidor respondió con un código de error
        if e.code == 429 or e.code >= 500:
            raise ErrorReintentable(f"HTTP {e.code}", e.code)
        raise ErrorDefinitivo(f"HTTP {e.code}", e.code)
    except (urllib.error.URLError, TimeoutError, OSError) as e:  # sin respuesta: red caída, DNS, timeout...
        raise ErrorReintentable(f"red/timeout: {e}")


async def descargar_feed(conn) -> tuple[dict, bytes] | None:
    """Descarga y parsea el feed con reintentos. Registra CADA intento en consulta_ingesta.
    Devuelve (geojson, bytes_originales) o None si todos los intentos fallan."""
    for intento in range(REINTENTOS + 1):
        t0 = time.monotonic()
        try:
            status, cuerpo = await asyncio.to_thread(_descargar_sync)
            try:
                datos = json.loads(cuerpo)
            except json.JSONDecodeError:
                raise ErrorReintentable("JSON inválido", status)
            if not isinstance(datos, dict) or not isinstance(datos.get("features"), list):
                raise ErrorReintentable("respuesta sin 'features'", status)
            return datos, cuerpo
        except (ErrorReintentable, ErrorDefinitivo) as e:
            ms = int((time.monotonic() - t0) * 1000)
            await db.registrar_consulta(conn, FUENTE, URL, e.http_status, False, None, None, ms,
                                        f"intento {intento + 1}: {e}")
            print(f"[productor] ERROR intento {intento + 1}/{REINTENTOS + 1}: {e}")
            if isinstance(e, ErrorDefinitivo) or intento == REINTENTOS:
                return None
            espera = 2 ** (intento + 1)        # espera progresiva: 2, 4, 8 segundos
            await asyncio.sleep(espera)
    return None


_ultimo_hash = None


def guardar_original(cuerpo: bytes, features: list) -> str | None:
    """Guarda el GeoJSON tal cual llegó, comprimido, SOLO si sus TERREMOTOS cambiaron respecto al último guardado.
    La huella se calcula sobre 'features' y no sobre el archivo entero porque USGS cambia metadata.generated
    en CADA respuesta (descubierto el 31/10: se guardaba una copia por minuto sin cambios reales).
    Después borra los archivos más antiguos que RAW_RETENCION_H (retención definida, enunciado §5.2)."""
    global _ultimo_hash
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha256(json.dumps(features, sort_keys=True).encode("utf-8")).hexdigest()
    nombre = None
    if h != _ultimo_hash:
        sello = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        nombre = f"feed-all_day-{sello}.geojson.gz"
        with gzip.open(RAW_DIR / nombre, "wb") as f:
            f.write(cuerpo)
        _ultimo_hash = h
    limite = time.time() - RAW_RETENCION_H * 3600
    for archivo in RAW_DIR.glob("feed-all_day-*.geojson.gz"):
        if archivo.stat().st_mtime < limite:
            archivo.unlink()
    return nombre


async def un_ciclo(conn, productor, publicadas: dict[str, int]) -> None:
    t0 = time.monotonic()
    resultado = await descargar_feed(conn)
    if resultado is None:
        return                                   # el error ya está registrado; el estado anterior no se toca
    datos, cuerpo = resultado
    archivo = guardar_original(cuerpo, datos["features"])

    n_publicados = n_sin_identidad = 0
    for evento in datos["features"]:
        props = evento.get("properties") if isinstance(evento, dict) else None
        event_id = evento.get("id") if isinstance(evento, dict) else None
        updated = props.get("updated") if isinstance(props, dict) else None
        if not isinstance(event_id, str) or not isinstance(updated, int) or isinstance(updated, bool):
            n_sin_identidad += 1                 # sin id/updated no se puede controlar la versión
            continue

        conocido = publicadas.get(event_id)      # búsqueda O(1) en el diccionario
        if conocido is not None and updated <= conocido:
            continue                             # misma versión o atrasada -> no publicar

        mensaje = construir_mensaje(evento, source=FUENTE, mode="live")
        await productor.send_and_wait(           # 1) publicar y ESPERAR confirmación
            TOPIC,
            value=json.dumps(mensaje, ensure_ascii=False).encode("utf-8"),
            key=event_id.encode("utf-8"),
        )
        await db.marcar_publicada(conn, event_id, updated)   # 2) solo después, marcar como publicada
        publicadas[event_id] = updated
        n_publicados += 1

    ms = int((time.monotonic() - t0) * 1000)
    nota = f"sin id/updated: {n_sin_identidad}" if n_sin_identidad else None
    await db.registrar_consulta(conn, FUENTE, URL, 200, True, len(datos["features"]), n_publicados, ms, nota)
    print(f"[productor] OK eventos={len(datos['features'])} publicados={n_publicados} "
          f"sin_identidad={n_sin_identidad} original={archivo or 'sin cambios'} {ms} ms")


async def main():
    conn = await db.conectar()
    publicadas = await db.cargar_versiones_publicadas(conn)
    print(f"[productor] estado cargado: {len(publicadas)} versiones ya publicadas")
    productor = AIOKafkaProducer(bootstrap_servers=BOOTSTRAP, acks="all")
    await productor.start()
    print(f"[productor] consultando {URL} cada {INTERVALO_S} s -> topic {TOPIC}")
    try:
        while True:
            inicio = time.monotonic()
            try:
                await un_ciclo(conn, productor, publicadas)
            except Exception as e:               # cualquier fallo inesperado: se anota y se sigue en el siguiente ciclo
                print(f"[productor] fallo inesperado en el ciclo: {e!r}")
            LATIDO.touch()                       # "sigo vivo" para el healthcheck
            await asyncio.sleep(max(0, INTERVALO_S - (time.monotonic() - inicio)))
    finally:
        await productor.stop()
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
