"""Consumidor (versión mínima, Fase 3): lee mensajes de Kafka y los muestra en el log.

En fases siguientes añadirá validación, cuarentena, país y escritura en PostgreSQL.
Desde ya confirma el offset A MANO y DESPUÉS de procesar cada mensaje (FAQ 13):
si el proceso cae antes de confirmar, Kafka le volverá a entregar ese mensaje (al menos una vez).

Variables de entorno:
- KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC
- KAFKA_GROUP_ID: nombre del grupo de consumo; Kafka guarda el offset por grupo
"""

import asyncio
import json
import os

from aiokafka import AIOKafkaConsumer

BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC = os.environ.get("KAFKA_TOPIC", "terremotos.live")
GROUP_ID = os.environ.get("KAFKA_GROUP_ID", "consumidor-observatorio")


def procesar(clave: str, mensaje: dict) -> None:
    """Por ahora solo muestra lo más importante del mensaje."""
    ev = mensaje["event"]
    p = ev["properties"]
    print(f"[consumidor] clave={clave} mode={mensaje['mode']} source={mensaje['source']} "
          f"mag={p.get('mag')} type={p.get('type')} updated={p.get('updated')} "
          f"ingested_at={mensaje['ingested_at']} lugar={p.get('place')!r}")


async def main():
    consumidor = AIOKafkaConsumer(
        TOPIC,
        bootstrap_servers=BOOTSTRAP,
        group_id=GROUP_ID,
        enable_auto_commit=False,      # NO confirmar automáticamente: lo hacemos nosotros tras procesar
        auto_offset_reset="earliest",  # si el grupo es nuevo, empezar desde el principio del topic
    )
    await consumidor.start()
    print(f"[consumidor] escuchando topic={TOPIC} grupo={GROUP_ID}")
    try:
        async for registro in consumidor:  # espera mensajes indefinidamente
            clave = registro.key.decode("utf-8") if registro.key else None
            mensaje = json.loads(registro.value.decode("utf-8"))
            print(f"[consumidor] recibido particion={registro.partition} offset={registro.offset}")
            procesar(clave, mensaje)
            await consumidor.commit()      # confirmar el offset SOLO después de procesar
    finally:
        await consumidor.stop()


if __name__ == "__main__":
    asyncio.run(main())
