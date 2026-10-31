"""Script de UNA VEZ: asigna el país a los terremotos guardados ANTES de que existiera la Fase 6.

Recorre evento_actual y recalcula country_id con la misma regla que el consumidor (src/geografia.py).
Es idempotente: ejecutarlo de nuevo da el mismo resultado.
Uso:  docker compose run --rm consumidor python -m src.rellenar_paises
"""

import asyncio

from src import db
from src.geografia import Catalogo


async def main():
    conn = await db.conectar()
    catalogo = Catalogo()
    await db.cargar_paises(conn, catalogo.paises)
    cur = await conn.execute("SELECT event_id, lon, lat FROM evento_actual")
    filas = await cur.fetchall()
    con_pais = 0
    async with conn.transaction():
        for event_id, lon, lat in filas:
            cid = catalogo.asignar(lon, lat)
            con_pais += cid is not None
            await conn.execute("UPDATE evento_actual SET country_id = %s WHERE event_id = %s", (cid, event_id))
    print(f"[rellenar_paises] eventos={len(filas)} con_pais={con_pais} sin_pais={len(filas) - con_pais} "
          f"coincidencias_multiples={catalogo.multiples}")
    await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
