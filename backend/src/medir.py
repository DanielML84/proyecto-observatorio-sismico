"""MEDICIONES de la Fase 12 (enunciado §10 · guía §2.7). Tiempo y memoria con TRES tamaños de entrada.

Qué se mide (cada medida = MEDIANA de varias repeticiones, tras una ejecución de calentamiento):
  A) Búsqueda de versiones por identificador: LISTA (búsqueda secuencial) frente a DICCIONARIO (lo que usa el productor).
     Tamaños 1.000 / 10.000 / 100.000 ids SINTÉTICOS («SINT-…», solo en memoria). Caso medio (id existente al azar)
     y PEOR caso (id que no existe: la lista se recorre entera).
  B) Integración geográfica: STRtree (lo que usa el consumidor) frente a comprobar los 177 polígonos uno a uno.
     Tamaños 500 / 2.000 / 8.000 coordenadas REALES leídas de public.evento_actual (solo lectura, no se modifica nada).
  C) Agregación por ventanas de 1 h (la misma consulta que /api/estadisticas) sobre datos REALES de 2025:
     1 día / 31 días / 365 días. Tiempo de ejecución de PostgreSQL (EXPLAIN ANALYZE).
  D) Consulta SIN y CON índice sobre una tabla SINTÉTICA en el esquema aparte «bench»:
     100.000 / 1.000.000 / 3.000.000 filas. Se BORRA al terminar (DROP SCHEMA bench CASCADE).
     Así los datos de prueba nunca se mezclan con el análisis real (enunciado §10).

Memoria:
  - Python: tracemalloc (memoria que reservan los objetos de Python) y, para Shapely (código en C que tracemalloc no ve),
    la memoria del proceso (VmRSS de /proc/self/status) antes y después.
  - PostgreSQL: tamaño en disco de tablas e índices (pg_relation_size).

Uso:  docker compose run --rm medir
Resultados: se imprimen como tablas Markdown y se guardan en data/mediciones/mediciones-<fecha>.json
"""

import asyncio
import json
import os
import platform
import random
import statistics
import time
import tracemalloc
from datetime import datetime, timezone
from pathlib import Path

import psycopg
from shapely.geometry import Point

from src.db import conninfo
from src.geografia import Catalogo

REPETICIONES = int(os.environ.get("MEDIR_REPETICIONES", "5"))
SALIDA = Path(os.environ.get("MEDIR_SALIDA", "/data/mediciones"))
random.seed(42)                                     # resultados reproducibles (mismos ids y búsquedas)


# ------------------------------------------------------------------ utilidades
def mediana_ms(funcion, repeticiones=REPETICIONES) -> float:
    """Ejecuta una vez para calentar y devuelve la MEDIANA (ms) de `repeticiones` ejecuciones."""
    funcion()
    tiempos = []
    for _ in range(repeticiones):
        t0 = time.perf_counter()
        funcion()
        tiempos.append((time.perf_counter() - t0) * 1000)
    return statistics.median(tiempos)


def rss_mb() -> float:
    """Memoria residente del proceso (MB). Incluye lo reservado por librerías en C como Shapely/GEOS."""
    for linea in Path("/proc/self/status").read_text().splitlines():
        if linea.startswith("VmRSS:"):
            return int(linea.split()[1]) / 1024
    return float("nan")


def equipo() -> dict:
    mem = next((l for l in Path("/proc/meminfo").read_text().splitlines() if l.startswith("MemTotal")), "")
    return {
        "fecha_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sistema_contenedor": platform.platform(),
        "python": platform.python_version(),
        "cpus_visibles": os.cpu_count(),
        "memoria_visible_mb": round(int(mem.split()[1]) / 1024) if mem else None,
        "repeticiones": REPETICIONES,
    }


# ------------------------------------------------------------------ A) lista frente a diccionario
def medir_versiones() -> list[dict]:
    filas = []
    for n in (1_000, 10_000, 100_000):
        ids = [f"SINT-{i:07d}" for i in range(n)]              # identificadores SINTÉTICOS, solo en memoria
        busquedas = random.sample(ids, 200)                     # caso medio: ids que existen, al azar
        ausentes = [f"NOEXISTE-{i}" for i in range(200)]        # peor caso de la lista: no está -> la recorre entera

        tracemalloc.start()
        lista = [(i, 1_700_000_000_000) for i in ids]           # [(event_id, updated_ms), ...]
        mem_lista = tracemalloc.get_traced_memory()[0]
        tracemalloc.stop()
        tracemalloc.start()
        dic = {i: 1_700_000_000_000 for i in ids}               # {event_id: updated_ms}  (como version_publicada)
        mem_dic = tracemalloc.get_traced_memory()[0]
        tracemalloc.stop()

        def en_lista(claves):
            for c in claves:
                next((u for i, u in lista if i == c), None)     # búsqueda secuencial: O(N)
        def en_dic(claves):
            for c in claves:
                dic.get(c)                                      # tabla hash: O(1) de media

        filas.append({
            "n": n,
            "lista_medio_us": mediana_ms(lambda: en_lista(busquedas)) * 1000 / len(busquedas),
            "lista_peor_us": mediana_ms(lambda: en_lista(ausentes)) * 1000 / len(ausentes),
            "dic_medio_us": mediana_ms(lambda: en_dic(busquedas)) * 1000 / len(busquedas),
            "dic_peor_us": mediana_ms(lambda: en_dic(ausentes)) * 1000 / len(ausentes),
            "mem_lista_mb": mem_lista / 1e6,
            "mem_dic_mb": mem_dic / 1e6,
        })
        print(f"  A) n={n:>7}: hecho")
    return filas


# ------------------------------------------------------------------ B) STRtree frente a fuerza bruta
def medir_geografia(coords: list[tuple[float, float]]) -> list[dict]:
    rss0 = rss_mb()
    catalogo = Catalogo()                                        # carga 177 polígonos + construye el STRtree
    rss_catalogo = rss_mb() - rss0

    def bruto(lon, lat):
        p = Point(lon, lat)
        ids = sorted(catalogo.ids[i] for i, g in enumerate(catalogo.geoms) if g.covers(p))   # mismo criterio que covered_by
        return ids[0] if ids else None

    filas = []
    for n in (500, 2_000, 8_000):
        if len(coords) < n:                                      # no inventar: si no hay puntos suficientes, se dice
            raise SystemExit(f"Solo hay {len(coords)} coordenadas reales; hacen falta {n}. ¿Está cargado el histórico?")
        puntos = coords[:n]
        arbol_ms = mediana_ms(lambda: [catalogo.asignar(lon, lat) for lon, lat in puntos])
        bruto_ms = mediana_ms(lambda: [bruto(lon, lat) for lon, lat in puntos], repeticiones=3)
        iguales = sum(catalogo.asignar(lo, la) == bruto(lo, la) for lo, la in puntos)
        filas.append({"n": n, "strtree_ms": arbol_ms, "bruto_ms": bruto_ms, "coinciden": iguales,
                      "rss_catalogo_mb": rss_catalogo})
        print(f"  B) n={n:>7}: hecho ({iguales}/{n} coinciden)")
    return filas


# ------------------------------------------------------------------ C) agregación por ventanas (SQL real)
SQL_VENTANAS = """
EXPLAIN (ANALYZE, FORMAT JSON)
WITH horas AS (SELECT generate_series(date_trunc('hour', %(s)s::timestamptz AT TIME ZONE 'UTC'),
                                      date_trunc('hour', (%(e)s::timestamptz - interval '1 microsecond') AT TIME ZONE 'UTC'),
                                      interval '1 hour') AS h)
SELECT horas.h, COUNT(e.event_id)
FROM horas LEFT JOIN evento_actual e
  ON date_trunc('hour', e.event_time AT TIME ZONE 'UTC') = horas.h
 AND e.event_time >= %(s)s AND e.event_time < %(e)s AND e.source NOT LIKE 'prueba%%'
GROUP BY horas.h"""


async def plan_ms(conn, sql, params=None) -> float:
    cur = await conn.execute(sql, params)
    return (await cur.fetchone())[0][0]["Execution Time"]


async def mediana_sql(conn, sql, params=None) -> float:
    await plan_ms(conn, sql, params)                             # calentamiento (caché de PostgreSQL)
    return statistics.median([await plan_ms(conn, sql, params) for _ in range(REPETICIONES)])


async def medir_ventanas(conn) -> list[dict]:
    filas = []
    inicio = datetime(2025, 1, 1, tzinfo=timezone.utc)
    for etiqueta, fin in (("1 día", datetime(2025, 1, 2, tzinfo=timezone.utc)),
                          ("31 días", datetime(2025, 2, 1, tzinfo=timezone.utc)),
                          ("365 días", datetime(2026, 1, 1, tzinfo=timezone.utc))):
        cur = await conn.execute("SELECT COUNT(*) FROM evento_actual WHERE event_time >= %s AND event_time < %s",
                                 (inicio, fin))
        n = (await cur.fetchone())[0]
        ms = await mediana_sql(conn, SQL_VENTANAS, {"s": inicio, "e": fin})
        filas.append({"periodo": etiqueta, "eventos": n, "ventanas": int((fin - inicio).total_seconds() // 3600),
                      "ms": ms})
        print(f"  C) {etiqueta}: hecho")
    return filas


# ------------------------------------------------------------------ D) sin índice frente a con índice (SINTÉTICO)
async def medir_indices(conn) -> list[dict]:
    filas = []
    consulta_rango = ("EXPLAIN (ANALYZE, FORMAT JSON) SELECT COUNT(*) FROM bench.evento "
                      "WHERE event_time >= '2025-07-29' AND event_time < '2025-07-30'")
    consulta_id = "EXPLAIN (ANALYZE, FORMAT JSON) SELECT * FROM bench.evento WHERE event_id = 'SINT-0000077'"
    try:
        for n in (100_000, 1_000_000, 3_000_000):
            await conn.execute("DROP SCHEMA IF EXISTS bench CASCADE")
            await conn.execute("CREATE SCHEMA bench")
            await conn.execute("COMMENT ON SCHEMA bench IS 'DATOS SINTÉTICOS de la Fase 12 (mediciones). Se borra al terminar.'")
            await conn.execute("CREATE TABLE bench.evento (event_id TEXT, event_time TIMESTAMPTZ, mag DOUBLE PRECISION)")
            t0 = time.perf_counter()
            # Filas SINTÉTICAS: id «SINT-…», fecha al azar dentro de 2025, magnitud al azar. setseed -> reproducible.
            await conn.execute("SELECT setseed(0.42)")
            await conn.execute("""
                INSERT INTO bench.evento
                SELECT 'SINT-' || lpad(i::text, 7, '0'),
                       timestamptz '2025-01-01 00:00+00' + random() * interval '365 days',
                       round((random() * 7)::numeric, 1)
                FROM generate_series(1, %s) AS i""", (n,))
            carga_s = time.perf_counter() - t0
            await conn.execute("ANALYZE bench.evento")
            sin_rango = await mediana_sql(conn, consulta_rango)
            sin_id = await mediana_sql(conn, consulta_id)
            cur = await conn.execute("SELECT pg_relation_size('bench.evento')")
            tabla_b = (await cur.fetchone())[0]

            t0 = time.perf_counter()
            await conn.execute("CREATE INDEX ix_bench_time ON bench.evento (event_time)")
            await conn.execute("CREATE INDEX ix_bench_id ON bench.evento (event_id)")
            crear_idx_s = time.perf_counter() - t0
            await conn.execute("ANALYZE bench.evento")
            con_rango = await mediana_sql(conn, consulta_rango)
            con_id = await mediana_sql(conn, consulta_id)
            cur = await conn.execute("SELECT pg_relation_size('bench.ix_bench_time'), pg_relation_size('bench.ix_bench_id')")
            idx_time_b, idx_id_b = await cur.fetchone()
            filas.append({"n": n, "carga_s": carga_s, "tabla_mb": tabla_b / 1e6,
                          "rango_sin_ms": sin_rango, "rango_con_ms": con_rango,
                          "id_sin_ms": sin_id, "id_con_ms": con_id,
                          "crear_indices_s": crear_idx_s, "idx_time_mb": idx_time_b / 1e6, "idx_id_mb": idx_id_b / 1e6})
            print(f"  D) n={n:>9}: hecho")
    finally:
        await conn.execute("DROP SCHEMA IF EXISTS bench CASCADE")   # los datos sintéticos NO se quedan en la base
        print("  D) esquema bench borrado")
    return filas


# ------------------------------------------------------------------ informe
def tabla(cabeceras, filas) -> str:
    lineas = ["| " + " | ".join(cabeceras) + " |", "|" + "---|" * len(cabeceras)]
    lineas += ["| " + " | ".join(str(c) for c in f) + " |" for f in filas]
    return "\n".join(lineas)


def f(x, d=2):
    return f"{x:,.{d}f}".replace(",", " ")


async def main():
    resultado = {"equipo": equipo()}
    async with await psycopg.AsyncConnection.connect(conninfo("public"), autocommit=True) as conn:
        cur = await conn.execute("SHOW server_version")
        resultado["equipo"]["postgresql"] = (await cur.fetchone())[0]
        cur = await conn.execute("SELECT lon, lat FROM evento_actual WHERE source NOT LIKE 'prueba%' "
                                 "ORDER BY event_id LIMIT 8000")
        coords = await cur.fetchall()
        print(f"Equipo: {resultado['equipo']}")
        print("A) búsqueda de versiones…");  resultado["versiones"] = medir_versiones()
        print("B) integración geográfica…"); resultado["geografia"] = medir_geografia(coords)
        print("C) agregación por ventanas…"); resultado["ventanas"] = await medir_ventanas(conn)
        print("D) índices (sintético)…");    resultado["indices"] = await medir_indices(conn)

    SALIDA.mkdir(parents=True, exist_ok=True)
    archivo = SALIDA / f"mediciones-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
    archivo.write_text(json.dumps(resultado, indent=2, ensure_ascii=False))

    print("\n### A) Búsqueda de versiones (µs por búsqueda; memoria de la estructura)")
    print(tabla(["N ids", "Lista medio", "Lista peor", "Dicc. medio", "Dicc. peor", "Mem. lista (MB)", "Mem. dicc. (MB)"],
                [[f(r["n"], 0), f(r["lista_medio_us"]), f(r["lista_peor_us"]), f(r["dic_medio_us"], 3),
                  f(r["dic_peor_us"], 3), f(r["mem_lista_mb"]), f(r["mem_dic_mb"])] for r in resultado["versiones"]]))
    print("\n### B) Integración geográfica (ms para N puntos reales)")
    print(tabla(["N puntos", "STRtree (ms)", "Fuerza bruta (ms)", "Veces más rápido", "Coinciden", "RSS catálogo (MB)"],
                [[f(r["n"], 0), f(r["strtree_ms"]), f(r["bruto_ms"]), f(r["bruto_ms"] / r["strtree_ms"], 1),
                  f"{r['coinciden']}/{r['n']}", f(r["rss_catalogo_mb"], 1)] for r in resultado["geografia"]]))
    print("\n### C) Agregación por ventanas de 1 h (datos reales 2025)")
    print(tabla(["Periodo", "Eventos", "Ventanas", "Tiempo (ms)"],
                [[r["periodo"], f(r["eventos"], 0), f(r["ventanas"], 0), f(r["ms"])] for r in resultado["ventanas"]]))
    print("\n### D) Sin índice / con índice (tabla SINTÉTICA bench.evento, borrada al final)")
    print(tabla(["Filas", "Tabla (MB)", "Rango 1 día sin (ms)", "con (ms)", "Por id sin (ms)", "con (ms)",
                 "Crear índices (s)", "Índice fecha (MB)", "Índice id (MB)"],
                [[f(r["n"], 0), f(r["tabla_mb"], 1), f(r["rango_sin_ms"]), f(r["rango_con_ms"]), f(r["id_sin_ms"]),
                  f(r["id_con_ms"], 3), f(r["crear_indices_s"], 1), f(r["idx_time_mb"], 1), f(r["idx_id_mb"], 1)]
                 for r in resultado["indices"]]))
    print(f"\nGuardado en {archivo}")


if __name__ == "__main__":
    asyncio.run(main())
