"""PASO 2 del histórico: lee los archivos de data/historico/, DEDUPLICA y los publica por Kafka.

- Deduplicación: los límites temporales de la API son inclusivos en los dos extremos, así que un evento en el
  instante exacto de cambio de mes aparece en dos archivos. Se agrupa por id y se queda la versión con mayor `updated`.
- Se publica en terremotos.live con source='usgs-fdsn' (contrato v1). El MISMO consumidor aplica las mismas reglas
  de calidad, el país y la idempotencia que a los datos en vivo (FAQ 21: decisión documentada).
- Re-ejecutable: publicar otra vez no duplica nada (el consumidor es idempotente).
Uso:  docker compose run --rm productor python -m src.historico_cargar
"""

import asyncio
import json
import os
from pathlib import Path

from aiokafka import AIOKafkaProducer

from src.mensajes import construir_mensaje

BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC = os.environ.get("KAFKA_TOPIC", "terremotos.live")
ORIGEN = Path("/data/historico")


async def main():
    archivos = sorted(ORIGEN.glob("*.geojson"))
    if not archivos:
        raise SystemExit("No hay archivos en data/historico. Ejecuta antes src.historico_descargar")

    por_id: dict[str, dict] = {}
    leidos = repetidos = 0
    for a in archivos:
        for ev in json.loads(a.read_bytes())["features"]:
            leidos += 1
            previo = por_id.get(ev["id"])
            if previo is not None:
                repetidos += 1
                if ev["properties"]["updated"] <= previo["properties"]["updated"]:
                    continue
            por_id[ev["id"]] = ev
    print(f"Archivos: {len(archivos)} | eventos leídos: {leidos} | repetidos entre archivos: {repetidos} "
          f"| únicos: {len(por_id)}")

    productor = AIOKafkaProducer(bootstrap_servers=BOOTSTRAP, acks="all", linger_ms=20)  # linger: agrupa envíos -> más rápido
    await productor.start()
    try:
        enviados = 0
        pendientes = []
        for ev in por_id.values():
            valor = json.dumps(construir_mensaje(ev, source="usgs-fdsn", mode="live"), ensure_ascii=False).encode()
            pendientes.append(await productor.send(TOPIC, value=valor, key=ev["id"].encode()))  # envío sin esperar uno a uno
            if len(pendientes) >= 500:
                await asyncio.gather(*pendientes)             # esperar la confirmación de Kafka del bloque
                enviados += len(pendientes); pendientes = []
                print(f"  publicados {enviados}/{len(por_id)}")
        await asyncio.gather(*pendientes)
        enviados += len(pendientes)
        print(f"Publicados {enviados} eventos históricos en {TOPIC}")
    finally:
        await productor.stop()


if __name__ == "__main__":
    asyncio.run(main())
