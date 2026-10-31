"""Acceso a PostgreSQL del consumidor. Todo el SQL está aquí, comentado.

Idempotencia (FAQ 12 y 13): procesar dos veces el mismo mensaje deja la base IGUAL, gracias a
  - evento_version: PRIMARY KEY (event_id, updated_ms) + ON CONFLICT DO NOTHING
  - evento_actual:  PRIMARY KEY (event_id) + ON CONFLICT ... DO UPDATE ... WHERE la versión nueva es POSTERIOR
  - cuarentena:     UNIQUE (topic, partición, offset) + ON CONFLICT DO NOTHING
"""

import asyncio
import os

import psycopg
from psycopg.types.json import Jsonb

CONNINFO = (
    f"host={os.environ.get('POSTGRES_HOST', 'postgres')} "
    f"dbname={os.environ['POSTGRES_DB']} "
    f"user={os.environ['POSTGRES_USER']} "
    f"password={os.environ['POSTGRES_PASSWORD']}"
)

# 1) Historial: guarda la versión si no estaba. Si ya estaba (mismo event_id + updated_ms), no hace nada.
SQL_VERSION = """
INSERT INTO evento_version (event_id, updated_ms, mag, depth_km, lon, lat, event_time, status, source, ingested_at, raw)
VALUES (%(event_id)s, %(updated_ms)s, %(mag)s, %(depth_km)s, %(lon)s, %(lat)s, %(event_time)s, %(status)s,
        %(source)s, %(ingested_at)s, %(raw)s)
ON CONFLICT (event_id, updated_ms) DO NOTHING
"""

# 2) Estado actual: UPSERT = "inserta, y si ya existe, actualiza".
#    El WHERE final es la clave: SOLO actualiza si la versión que llega es MÁS NUEVA (updated_ms mayor).
#    Así una versión antigua que llega tarde NO pisa a la reciente (FAQ 12, mensaje 4).
#    EXCLUDED = la fila que intentábamos insertar.
#    RETURNING (xmax = 0): truco de PostgreSQL -> true si fue INSERT nuevo, false si fue UPDATE.
#    Si no se insertó ni actualizó (versión igual o antigua), no devuelve ninguna fila.
SQL_ACTUAL = """
INSERT INTO evento_actual (event_id, updated_ms, event_time, updated_at, fecha_id, mag, mag_type, depth_km,
                           lon, lat, place, status, country_id, source, ingested_at)
VALUES (%(event_id)s, %(updated_ms)s, %(event_time)s, %(updated_at)s, %(fecha_id)s, %(mag)s, %(mag_type)s,
        %(depth_km)s, %(lon)s, %(lat)s, %(place)s, %(status)s, %(country_id)s, %(source)s, %(ingested_at)s)
ON CONFLICT (event_id) DO UPDATE SET
    updated_ms = EXCLUDED.updated_ms, event_time = EXCLUDED.event_time, updated_at = EXCLUDED.updated_at,
    fecha_id = EXCLUDED.fecha_id, mag = EXCLUDED.mag, mag_type = EXCLUDED.mag_type,
    depth_km = EXCLUDED.depth_km, lon = EXCLUDED.lon, lat = EXCLUDED.lat, place = EXCLUDED.place,
    status = EXCLUDED.status, country_id = EXCLUDED.country_id, source = EXCLUDED.source,
    ingested_at = EXCLUDED.ingested_at, processed_at = now()
WHERE evento_actual.updated_ms < EXCLUDED.updated_ms
RETURNING (xmax = 0) AS insertado
"""

SQL_CUARENTENA = """
INSERT INTO cuarentena (tipo, motivo, event_id, kafka_topic, kafka_partition, kafka_offset, raw)
VALUES (%s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (kafka_topic, kafka_partition, kafka_offset) DO NOTHING
"""


async def conectar(reintentos: int = 30, espera_s: float = 2.0) -> psycopg.AsyncConnection:
    """Conecta con reintentos: aunque compose espera a que PostgreSQL esté sano, puede fallar un momento."""
    for intento in range(1, reintentos + 1):
        try:
            # autocommit=True: cada operación se confirma sola SALVO dentro de "async with conn.transaction()"
            return await psycopg.AsyncConnection.connect(CONNINFO, autocommit=True)
        except psycopg.OperationalError as exc:
            print(f"[db] intento {intento}/{reintentos} fallido: {exc}")
            await asyncio.sleep(espera_s)
    raise RuntimeError("No se pudo conectar a PostgreSQL")


async def guardar_evento(conn: psycopg.AsyncConnection, campos: dict, evento_original: dict) -> str:
    """Guarda versión + estado actual en UNA transacción (o las dos cosas o ninguna). Devuelve qué pasó."""
    async with conn.transaction():                      # BEGIN ... COMMIT (ROLLBACK si hay excepción)
        cur = await conn.execute(SQL_VERSION, {**campos, "raw": Jsonb(evento_original)})
        version_nueva = cur.rowcount == 1               # 1 = se insertó; 0 = ya existía
        cur = await conn.execute(SQL_ACTUAL, campos)
        fila = await cur.fetchone()                     # None si no se insertó ni actualizó
    if fila is None:
        return "ignorado: version_repetida" if not version_nueva else "ignorado: version_antigua"
    return "insertado" if fila[0] else "actualizado"


async def guardar_cuarentena(conn, tipo, motivo, event_id, topic, particion, offset, raw_texto) -> None:
    await conn.execute(SQL_CUARENTENA, (tipo, motivo, event_id, topic, particion, offset, raw_texto))


# =====================================================================================
# Funciones del PRODUCTOR
# =====================================================================================

async def cargar_versiones_publicadas(conn) -> dict[str, int]:
    """Lee de PostgreSQL lo que el productor ya publicó: {event_id: updated_ms}.
    Se guarda en un diccionario para buscar en O(1) de media (en vez de O(N) recorriendo una lista)."""
    cur = await conn.execute("SELECT event_id, updated_ms FROM version_publicada")
    return {event_id: updated_ms for event_id, updated_ms in await cur.fetchall()}


SQL_MARCAR_PUBLICADA = """
INSERT INTO version_publicada (event_id, updated_ms) VALUES (%s, %s)
ON CONFLICT (event_id) DO UPDATE SET updated_ms = EXCLUDED.updated_ms, published_at = now()
WHERE version_publicada.updated_ms < EXCLUDED.updated_ms
"""


async def marcar_publicada(conn, event_id: str, updated_ms: int) -> None:
    """Se llama SOLO después de que Kafka confirme el envío (enunciado §5.5)."""
    await conn.execute(SQL_MARCAR_PUBLICADA, (event_id, updated_ms))


SQL_CONSULTA = """
INSERT INTO consulta_ingesta (fuente, url, http_status, ok, n_eventos, n_publicados, duracion_ms, error)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""


async def registrar_consulta(conn, fuente, url, http_status, ok, n_eventos, n_publicados, duracion_ms, error) -> None:
    """Una fila por cada intento de consulta a USGS (correcto o fallido)."""
    await conn.execute(SQL_CONSULTA, (fuente, url, http_status, ok, n_eventos, n_publicados, duracion_ms, error))


# =====================================================================================
# Dimensión PAÍS
# =====================================================================================

SQL_PAIS = """
INSERT INTO pais (country_id, nombre_es, admin, continente, subregion)
VALUES (%(country_id)s, %(nombre_es)s, %(admin)s, %(continente)s, %(subregion)s)
ON CONFLICT (country_id) DO UPDATE SET nombre_es = EXCLUDED.nombre_es, admin = EXCLUDED.admin,
    continente = EXCLUDED.continente, subregion = EXCLUDED.subregion
"""


async def cargar_paises(conn, paises: list[dict]) -> None:
    """Carga (o actualiza) los 177 países. Idempotente: ejecutarlo varias veces deja la tabla igual."""
    async with conn.transaction():
        async with conn.cursor() as cur:
            await cur.executemany(SQL_PAIS, paises)
