"""API de CONSULTA (FastAPI). Solo lee de PostgreSQL datos YA procesados por el consumidor (enunciado §2).

Rutas (docs/material-profesor/CONTRATO-API.md):
  GET /api/eventos        -> GeoJSON FeatureCollection para el mapa y la tabla
  GET /api/estadisticas   -> recuentos por país/subregión, ventanas de 1 h UTC, distribuciones y comparación histórica
  GET /api/salud          -> estado de la API y de la última ingesta correcta de USGS

Filtros COMUNES a eventos y estadísticas (una sola función -> mapa y gráficos siempre coherentes):
  start (ISO 8601, inclusivo) · end (ISO 8601, exclusivo) · min_mag · country_id (ADM0_A3 o 'SIN_PAIS')
  Por defecto: últimas 24 horas. Los datos sintéticos (source 'prueba…') nunca se devuelven.
"""

import math
import os
from datetime import datetime, timedelta, timezone

import psycopg
from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.db import CONNINFO

MAX_PUNTOS = 5000                      # límite documentado de puntos por respuesta
INGESTA_ANTIGUA_S = 300                # si la última ingesta correcta tiene más de 5 min -> datos desactualizados
DIAS_2025 = 365

app = FastAPI(title="Observatorio de actividad sísmica · API", version="1.0")

# CORS: solo los orígenes indicados (desarrollo y Netlify). CORS NO es autenticación (enunciado §9).
ORIGENES = [o.strip() for o in os.environ.get("CORS_ORIGINS", "http://localhost:4200").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENES,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["ngrok-skip-browser-warning"],
)


# ------------------------------------------------------------------ utilidades
def ms(dt: datetime | None) -> int | None:
    """datetime -> milisegundos Unix (el formato que usa el contrato)."""
    return int(dt.timestamp() * 1000) if dt else None


def limpio(x):
    """El contrato exige null, nunca NaN/Infinity."""
    return None if isinstance(x, float) and not math.isfinite(x) else x


def periodo(start: datetime | None, end: datetime | None) -> tuple[datetime, datetime]:
    """Por defecto, las últimas 24 h. Si llega una fecha sin zona horaria, se asume UTC."""
    ahora = datetime.now(timezone.utc)
    end = end or ahora
    start = start or end - timedelta(hours=24)
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)
    return start, end


def filtros(start, end, min_mag, country_id, alias="e") -> tuple[str, list]:
    """Construye el WHERE común. Devuelve (sql, parámetros). Parámetros SIEMPRE con %s (nunca pegados al texto)."""
    w = [f"{alias}.source NOT LIKE 'prueba%%'", f"{alias}.event_time >= %s", f"{alias}.event_time < %s"]
    p = [start, end]
    if min_mag is not None:
        w.append(f"{alias}.mag >= %s")            # una magnitud NULL NO cumple el filtro (contrato)
        p.append(min_mag)
    if country_id == "SIN_PAIS":
        w.append(f"{alias}.country_id IS NULL")
    elif country_id:
        w.append(f"{alias}.country_id = %s")
        p.append(country_id)
    return " AND ".join(w), p


async def conectar():
    return await psycopg.AsyncConnection.connect(CONNINFO, autocommit=True)


async def ultima_ingesta(conn) -> datetime | None:
    cur = await conn.execute(
        "SELECT MAX(solicitada_at) FROM consulta_ingesta WHERE ok AND fuente = 'usgs-feed-all_day'")
    return (await cur.fetchone())[0]


@app.exception_handler(psycopg.Error)
async def error_bd(request: Request, exc: psycopg.Error):
    """Si la base de datos falla: error EXPLÍCITO (503), nunca «0 eventos» como si fuera válido (contrato)."""
    return JSONResponse(status_code=503, content={"error": "base de datos no disponible", "detalle": type(exc).__name__})


# ------------------------------------------------------------------ /api/eventos
@app.get("/api/eventos")
async def eventos(
    start: datetime | None = Query(None, description="ISO 8601, inclusivo"),
    end: datetime | None = Query(None, description="ISO 8601, exclusivo"),
    min_mag: float | None = None,
    country_id: str | None = Query(None, description="ADM0_A3 o SIN_PAIS"),
    limit: int = Query(MAX_PUNTOS, ge=1, le=MAX_PUNTOS),
    offset: int = Query(0, ge=0),
):
    start, end = periodo(start, end)
    where, params = filtros(start, end, min_mag, country_id)
    async with await conectar() as conn:
        cur = await conn.execute(f"SELECT COUNT(*) FROM evento_actual e WHERE {where}", params)
        total = (await cur.fetchone())[0]
        cur = await conn.execute(f"""
            SELECT e.event_id, e.lon, e.lat, e.depth_km, e.mag, e.mag_type, e.place, e.event_time, e.updated_at,
                   e.status, e.country_id, p.nombre_es, p.subregion
            FROM evento_actual e LEFT JOIN pais p ON p.country_id = e.country_id
            WHERE {where}
            ORDER BY e.event_time DESC, e.event_id
            LIMIT %s OFFSET %s""", params + [limit, offset])
        filas = await cur.fetchall()
        ingesta = await ultima_ingesta(conn)

    features = [{
        "type": "Feature",
        "id": f[0],
        "geometry": {"type": "Point", "coordinates": [f[1], f[2], limpio(f[3])]},   # [lon, lat, profundidad]
        "properties": {
            "mag": limpio(f[4]), "magType": f[5], "place": f[6],
            "time": ms(f[7]), "updated": ms(f[8]), "status": f[9],
            "country_id": f[10], "country_name": f[11], "subregion": f[12],
        },
    } for f in filas]
    truncado = offset + len(features) < total
    return {
        "type": "FeatureCollection",
        "metadata": {
            "generated": ms(datetime.now(timezone.utc)),   # cuándo se generó ESTA respuesta
            "last_ingestion": ms(ingesta),                  # última consulta correcta a USGS
            "mode": "live",
            "count": len(features), "total": total, "truncated": truncado,
            "limit": limit, "offset": offset,
            "next_offset": offset + len(features) if truncado else None,   # paginación
            "periodo": {"start": start.isoformat(), "end": end.isoformat()},
            "filtros": {"min_mag": min_mag, "country_id": country_id},
        },
        "features": features,
    }


# ------------------------------------------------------------------ /api/estadisticas
@app.get("/api/estadisticas")
async def estadisticas(
    start: datetime | None = None,
    end: datetime | None = None,
    min_mag: float | None = None,
    country_id: str | None = None,
):
    start, end = periodo(start, end)
    where, params = filtros(start, end, min_mag, country_id)
    async with await conectar() as conn:
        async def q(sql, p=params):
            cur = await conn.execute(sql, p)
            return await cur.fetchall()

        # Totales y registros sin valor (se informan siempre: denominadores honestos)
        (total, sin_mag, sin_prof, sin_pais), = await q(f"""
            SELECT COUNT(*), COUNT(*) FILTER (WHERE mag IS NULL), COUNT(*) FILTER (WHERE depth_km IS NULL),
                   COUNT(*) FILTER (WHERE country_id IS NULL)
            FROM evento_actual e WHERE {where}""")

        # Contrato: «la magnitud nula no cumple un filtro min_mag y debe contabilizarse por separado».
        # Se cuentan los eventos SIN magnitud con el mismo periodo y país, pero SIN el filtro de magnitud.
        excluidos_sin_mag = 0
        if min_mag is not None:
            w_nm, p_nm = filtros(start, end, None, country_id)
            (excluidos_sin_mag,), = await q(f"SELECT COUNT(*) FROM evento_actual e WHERE {w_nm} AND e.mag IS NULL", p_nm)

        # Recuento por país (incluye «Sin país asignado» gracias al LEFT JOIN)
        por_pais = await q(f"""
            SELECT e.country_id, COALESCE(p.nombre_es, 'Sin país asignado'), COUNT(*)
            FROM evento_actual e LEFT JOIN pais p ON p.country_id = e.country_id
            WHERE {where} GROUP BY 1, 2 ORDER BY 3 DESC, 2""")

        por_subregion = await q(f"""
            SELECT COALESCE(p.subregion, 'Sin país asignado'), COUNT(*)
            FROM evento_actual e LEFT JOIN pais p ON p.country_id = e.country_id
            WHERE {where} GROUP BY 1 ORDER BY 2 DESC, 1""")

        # Ventanas FIJAS de 1 hora UTC por tiempo de OCURRENCIA [hh:00, hh+1:00). generate_series incluye horas con 0.
        por_hora = await q(f"""
            WITH horas AS (
                SELECT generate_series(date_trunc('hour', %s::timestamptz AT TIME ZONE 'UTC'),
                                       date_trunc('hour', (%s::timestamptz - interval '1 microsecond') AT TIME ZONE 'UTC'),
                                       interval '1 hour') AS h)
            SELECT horas.h, COUNT(e.event_id)
            FROM horas LEFT JOIN evento_actual e
              ON date_trunc('hour', e.event_time AT TIME ZONE 'UTC') = horas.h AND {where}
            GROUP BY horas.h ORDER BY horas.h""", [start, end] + params)

        # Distribución de magnitud en tramos de 0,5 (los NULL se cuentan aparte)
        dist_mag = await q(f"""
            SELECT floor(mag * 2) / 2 AS desde, COUNT(*) FROM evento_actual e
            WHERE {where} AND mag IS NOT NULL GROUP BY 1 ORDER BY 1""")

        # Distribución de profundidad en las mismas clases que los colores del mapa
        dist_prof = await q(f"""
            SELECT CASE WHEN depth_km < 0 THEN 'negativa (<0 km)'
                        WHEN depth_km < 70 THEN 'superficial (0-70 km)'
                        WHEN depth_km < 300 THEN 'intermedia (70-300 km)'
                        ELSE 'profunda (>=300 km)' END AS clase, COUNT(*)
            FROM evento_actual e WHERE {where} AND depth_km IS NOT NULL GROUP BY 1""")

        # Comparación histórica: MISMOS filtros geográficos y de tipo, magnitud >= max(4, min_mag)
        # (el histórico solo contiene mag >= 4). El denominador incluye los días con cero eventos (365).
        mag_cmp = max(4.0, min_mag or 4.0)
        w_rec, p_rec = filtros(start, end, mag_cmp, country_id)
        (reciente,), = await q(f"SELECT COUNT(*) FROM evento_actual e WHERE {w_rec}", p_rec)
        w_his, p_his = filtros(datetime(2025, 1, 1, tzinfo=timezone.utc), datetime(2026, 1, 1, tzinfo=timezone.utc),
                               mag_cmp, country_id)
        (historico,), = await q(f"SELECT COUNT(*) FROM evento_actual e WHERE {w_his} AND e.source = 'usgs-fdsn'", p_his)

        # Distribución de los 365 días de 2025 (dimensión fecha + LEFT JOIN: los días con 0 eventos también cuentan).
        # La media se ve muy afectada por los picos (p. ej. 645 eventos el día del M8,8 de Kamchatka); la mediana y los
        # percentiles describen mejor un «día típico». Se usan los MISMOS filtros (país, magnitud) que el periodo reciente.
        (mediana, p10, p90, dias_menor_igual), = await q(f"""
            SELECT percentile_disc(0.5) WITHIN GROUP (ORDER BY n), percentile_disc(0.1) WITHIN GROUP (ORDER BY n),
                   percentile_disc(0.9) WITHIN GROUP (ORDER BY n), COUNT(*) FILTER (WHERE n <= %s)
            FROM (SELECT f.fecha_id, COUNT(e.event_id) AS n
                  FROM fecha f LEFT JOIN evento_actual e
                    ON e.fecha_id = f.fecha_id AND e.source = 'usgs-fdsn' AND {w_his}
                  WHERE f.anio = 2025 GROUP BY f.fecha_id) t""", [reciente] + p_his)
        ingesta = await ultima_ingesta(conn)

        # Cobertura del feed: la PRIMERA descarga correcta ya traía las 24 h anteriores (ventana móvil).
        # Limitación documentada: si el sistema estuvo parado > 24 h en medio, habría un hueco que esto no detecta.
        (primera_ingesta,), = await q(
            "SELECT MIN(solicitada_at) FROM consulta_ingesta WHERE ok AND fuente = 'usgs-feed-all_day'", [])

    cobertura_desde = primera_ingesta - timedelta(hours=24) if primera_ingesta else None
    inicio_2025, fin_2025 = datetime(2025, 1, 1, tzinfo=timezone.utc), datetime(2026, 1, 1, tzinfo=timezone.utc)
    dentro_2025 = start >= inicio_2025 and end <= fin_2025                   # cubierto por el histórico descargado
    cubierto_feed = cobertura_desde is not None and start >= cobertura_desde and end <= datetime.now(timezone.utc)

    horas_periodo = (end - start).total_seconds() / 3600
    media_diaria = historico / DIAS_2025
    esperado = media_diaria * horas_periodo / 24          # media escalada a la duración del periodo consultado
    variacion = round((reciente - esperado) / esperado * 100, 1) if esperado > 0 else None   # ND si no hay base

    return {
        "generated": ms(datetime.now(timezone.utc)),
        "last_ingestion": ms(ingesta),
        "periodo": {"start": start.isoformat(), "end": end.isoformat(), "horas": round(horas_periodo, 2)},
        "filtros": {"min_mag": min_mag, "country_id": country_id, "tipo": "earthquake"},
        "unidad": "número de terremotos (estado actual: una fila por terremoto)",
        "total": total,
        "sin_valor": {"magnitud": sin_mag, "profundidad": sin_prof, "pais": sin_pais,
                      # Eventos del mismo periodo/país que se quedan fuera SOLO por no tener magnitud (null si no hay min_mag)
                      "magnitud_excluidos_por_filtro": excluidos_sin_mag if min_mag is not None else None},
        "por_pais": [{"country_id": c, "nombre": n, "n": k} for c, n, k in por_pais],
        "por_subregion": [{"subregion": s, "n": k} for s, k in por_subregion],
        "por_hora_utc": [{"hora": h.replace(tzinfo=timezone.utc).isoformat(), "n": k} for h, k in por_hora],
        "distribucion_magnitud": {
            "tramo": 0.5,
            "tramos": [{"desde": float(d), "hasta": float(d) + 0.5, "n": k} for d, k in dist_mag],
            "sin_valor": sin_mag,
        },
        "distribucion_profundidad": {"clases": [{"clase": c, "n": k} for c, k in dist_prof], "sin_valor": sin_prof},
        "comparacion_historica": {
            "filtro_magnitud": f">= {mag_cmp}",
            "reciente": reciente,
            "historico_2025_total": historico,
            "media_diaria_2025": round(media_diaria, 2),
            "esperado_en_periodo": round(esperado, 2),
            "diferencia": round(reciente - esperado, 2),
            "variacion_pct": variacion,                     # None -> mostrar ND
            "dias_2025": {
                "mediana": mediana, "p10": p10, "p90": p90,
                # Solo tiene sentido comparar un periodo de ~24 h con días: si no, None
                "pct_dias_con_recuento_menor_o_igual": (round(dias_menor_igual / DIAS_2025 * 100, 1)
                                                         if abs(horas_periodo - 24) < 0.01 else None),
            },
            "cobertura_feed_desde": cobertura_desde.isoformat() if cobertura_desde else None,
            "periodo_cubierto": dentro_2025 or cubierto_feed,   # False -> el recuento reciente puede estar incompleto
            "nota": ("El periodo reciente puede estar incompleto por retrasos de publicación de USGS. "
                     "La media de 2025 incluye la secuencia de réplicas de Kamchatka (jul-dic). "
                     "No es una predicción ni una evaluación de riesgo."),
        },
    }


# ------------------------------------------------------------------ /api/salud
@app.get("/api/salud")
async def salud():
    ahora = datetime.now(timezone.utc)
    try:
        async with await conectar() as conn:
            ingesta = await ultima_ingesta(conn)
    except psycopg.Error as exc:
        return JSONResponse(status_code=503, content={
            "api": "ok", "base_datos": "error", "detalle": type(exc).__name__, "generated": ms(ahora)})
    edad = (ahora - ingesta).total_seconds() if ingesta else None
    return {
        "api": "ok",
        "base_datos": "ok",
        "generated": ms(ahora),
        "last_ingestion": ms(ingesta),
        "segundos_desde_ultima_ingesta": round(edad) if edad is not None else None,
        "datos_desactualizados": edad is None or edad > INGESTA_ANTIGUA_S,
    }
