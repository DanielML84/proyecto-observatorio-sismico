"""Casos de PRUEBA CONTROLADOS (sintéticos, identificados con el prefijo 'PRUEBA-' y source='prueba-faq12').

Envía por Kafka:
  A) La secuencia de la FAQ 12 (E1 v1, E1 v1 repetido, E1 v2, E1 v1 tardío, E2)
     Esperado: 2 terremotos actuales (E1 mag 4.6, E2 mag 3.1) y 3 versiones.
  B) Casos de calidad del enunciado §11:
     - magnitud nula                  -> se guarda con mag NULL
     - latitud 145 (imposible)        -> cuarentena 'lat_fuera_de_rango'
     - explosión                      -> excluido 'type=explosion'
Los datos son INVENTADOS (enunciado §6: casos artificiales separados e identificados).
Uso:  docker compose run --rm productor-prueba python -m src.pruebas_faq12
"""

import asyncio
import json
import os
from datetime import datetime, timezone

from aiokafka import AIOKafkaProducer

from src.mensajes import construir_mensaje

BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC = os.environ.get("KAFKA_TOPIC", "terremotos.live")
SOURCE = "prueba-faq12"


def ms(hhmm: str) -> int:
    """'10:05' -> milisegundos Unix del 27/10/2026 a esa hora UTC."""
    h, m = map(int, hhmm.split(":"))
    return int(datetime(2026, 10, 27, h, m, tzinfo=timezone.utc).timestamp() * 1000)


def evento(eid, updated, mag, lat=40.4, lon=-3.7, depth=12, tipo="earthquake"):
    return {
        "type": "Feature", "id": eid,
        "properties": {"mag": mag, "magType": "ml", "place": "Caso de prueba sintético",
                       "time": ms("10:00"), "updated": ms(updated), "type": tipo, "status": "automatic"},
        "geometry": {"type": "Point", "coordinates": [lon, lat, depth]},
    }


CASOS = [
    ("FAQ12 #1 primera versión",          evento("PRUEBA-E1", "10:05", 4.2)),
    ("FAQ12 #2 repetición idéntica",      evento("PRUEBA-E1", "10:05", 4.2)),
    ("FAQ12 #3 revisión posterior",       evento("PRUEBA-E1", "10:09", 4.6)),
    ("FAQ12 #4 versión antigua tardía",   evento("PRUEBA-E1", "10:05", 4.2)),
    ("FAQ12 #5 otro terremoto",           evento("PRUEBA-E2", "10:12", 3.1)),
    ("Calidad: magnitud nula",            evento("PRUEBA-MAGNULA", "10:20", None)),
    ("Calidad: latitud 145",              evento("PRUEBA-LAT145", "10:21", 3.0, lat=145)),
    ("Calidad: explosión",                evento("PRUEBA-EXPLOSION", "10:22", 1.5, tipo="explosion")),
]


async def main():
    productor = AIOKafkaProducer(bootstrap_servers=BOOTSTRAP, acks="all")
    await productor.start()
    try:
        for descripcion, ev in CASOS:
            valor = json.dumps(construir_mensaje(ev, source=SOURCE), ensure_ascii=False).encode("utf-8")
            r = await productor.send_and_wait(TOPIC, value=valor, key=ev["id"].encode("utf-8"))
            print(f"[pruebas] {descripcion:34} id={ev['id']:17} -> p={r.partition} off={r.offset}")
    finally:
        await productor.stop()


if __name__ == "__main__":
    asyncio.run(main())
