"""CONTRASTE feed en vivo frente a catálogo FDSN (Conclusión 3 · dimensiones de Actualidad y Exactitud).

Pregunta: el 31/10/2026 el feed nos dio 25 terremotos M>=4 en las 24 h anteriores. ¿Estaba completo, o USGS añadió
o cambió eventos después? Se compara, terremoto a terremoto, para el MISMO periodo y los MISMOS filtros:
  A) lo que tenemos ahora en evento_actual con source='usgs-feed-all_day' (incluye las revisiones posteriores del feed)
  B) lo que devuelve HOY la API FDSN (catálogo de USGS)

Emparejamiento: por id. FDSN da en `ids` todos los identificadores asociados a un evento (",us7000abcd,ak2026xyz,"):
si USGS cambió el id preferido, se empareja igual.
Solo lee: no escribe terremotos. Registra la consulta en consulta_ingesta (fuente 'usgs-fdsn-contraste').

Uso:  docker compose run --rm productor python -m src.contrastar_fdsn
      (periodo por defecto: 2026-10-30T09:28:00Z -> 2026-10-31T09:28:00Z, M>=4; cambiable con CONTRASTE_INICIO/FIN/MAG)
"""

import asyncio
import json
import os
import time
import urllib.parse
from datetime import datetime, timezone

from src import db
from src.historico_descargar import BASE, get_con_reintentos

INICIO = os.environ.get("CONTRASTE_INICIO", "2026-10-30T09:28:00")
FIN = os.environ.get("CONTRASTE_FIN", "2026-10-31T09:28:00")
MAG = float(os.environ.get("CONTRASTE_MAG", "4"))


def utc(texto: str) -> datetime:
    return datetime.fromisoformat(texto).replace(tzinfo=timezone.utc)


def hora(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%m-%d %H:%M:%S")


async def main():
    inicio, fin = utc(INICIO), utc(FIN)
    conn = await db.conectar()

    # ---- B) catálogo FDSN hoy (endtime es INCLUSIVO en FDSN: el extremo se filtra después en Python)
    qs = urllib.parse.urlencode({"format": "geojson", "starttime": INICIO, "endtime": FIN, "minmagnitude": MAG,
                                 "eventtype": "earthquake", "orderby": "time-asc"})
    url = f"{BASE}query?{qs}"
    t0 = time.perf_counter()
    status, cuerpo = await asyncio.to_thread(get_con_reintentos, url)
    duracion = int((time.perf_counter() - t0) * 1000)
    fdsn = [f for f in json.loads(cuerpo)["features"]
            if f["properties"]["time"] < fin.timestamp() * 1000]           # fin EXCLUSIVO, como nuestra API
    await db.registrar_consulta(conn, "usgs-fdsn-contraste", url, status, True, len(fdsn), None, duracion, None)

    # ---- A) nuestra base: lo que llegó por el feed, en su versión actual
    cur = await conn.execute(
        "SELECT event_id, mag, event_time, updated_ms, status FROM evento_actual "
        "WHERE source = 'usgs-feed-all_day' AND event_time >= %s AND event_time < %s", (inicio, fin))
    nuestros_todos = {r[0]: r for r in await cur.fetchall()}             # todas las magnitudes (para buscar cambios)
    nuestros = {k: v for k, v in nuestros_todos.items() if v[1] is not None and v[1] >= MAG}
    await conn.close()

    # ---- emparejar por cualquiera de los ids asociados
    emparejados, solo_fdsn = [], []
    vistos = set()
    for f in fdsn:
        ids = [i for i in f["properties"].get("ids", "").split(",") if i] or [f["id"]]
        nuestro = next((nuestros_todos[i] for i in ids if i in nuestros_todos), None)
        if nuestro:
            emparejados.append((f, nuestro)); vistos.add(nuestro[0])
        else:
            solo_fdsn.append(f)
    solo_nuestros = [v for k, v in nuestros.items() if k not in vistos]

    print(f"Periodo [{INICIO}Z, {FIN}Z) · earthquake · M >= {MAG} · consulta FDSN {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC")
    print(f"  Nuestra base (feed, versión actual), M >= {MAG}: {len(nuestros)}")
    print(f"  Catálogo FDSN hoy, M >= {MAG}:                   {len(fdsn)}")
    print(f"  En los dos: {len(emparejados)} · solo en FDSN: {len(solo_fdsn)} · solo en nuestra base: {len(solo_nuestros)}")

    cambios = [(f, n) for f, n in emparejados if n[1] is None or abs(f["properties"]["mag"] - n[1]) >= 0.05]
    print(f"\nEmparejados con magnitud distinta (catálogo frente a nuestra base): {len(cambios)}")
    for f, n in cambios:
        print(f"  {f['id']:<14} {hora(f['properties']['time'])}  nuestra {n[1]} -> FDSN {f['properties']['mag']}  "
              f"({f['properties'].get('place')})")

    print(f"\nSolo en FDSN ({len(solo_fdsn)}): no llegaron por el feed, o llegaron con M < {MAG}, o con otro id")
    for f in solo_fdsn:
        p = f["properties"]
        print(f"  {f['id']:<14} {hora(p['time'])}  M{p['mag']} {p.get('magType')}  status={p.get('status')}  "
              f"updated={hora(p['updated'])}  ({p.get('place')})")

    print(f"\nSolo en nuestra base ({len(solo_nuestros)}): el catálogo hoy no los tiene con M >= {MAG}")
    for n in solo_nuestros:
        print(f"  {n[0]:<14} {n[2].astimezone(timezone.utc):%m-%d %H:%M:%S}  M{n[1]}  status={n[4]}")


if __name__ == "__main__":
    asyncio.run(main())
