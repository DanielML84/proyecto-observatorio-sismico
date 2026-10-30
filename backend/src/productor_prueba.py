"""Productor de PRUEBA (Fase 3, FAQ paso 3): envía UN terremoto de ejemplo y termina.

No consulta USGS todavía. Usa un evento real copiado de la muestra del 28/10 (us7000ttlm)
para comprobar que el recorrido productor -> Kafka -> consumidor funciona con el contrato.

Variables de entorno (se definen en compose.yaml):
- KAFKA_BOOTSTRAP_SERVERS: dirección del broker dentro de Docker (kafka:9092)
- KAFKA_TOPIC: topic donde publicar (terremotos.live)
"""

import asyncio   # aiokafka es asíncrono: necesita un "bucle de eventos"
import json      # el mensaje viaja como texto JSON
import os        # para leer las variables de entorno

from aiokafka import AIOKafkaProducer

from src.mensajes import construir_mensaje

BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC = os.environ.get("KAFKA_TOPIC", "terremotos.live")

# Evento real (resumido) de la muestra del feed del 28/10/2026
EVENTO_EJEMPLO = {
    "type": "Feature",
    "properties": {
        "mag": 6, "place": "214 km NW of Port-Olry, Vanuatu",
        "time": 1793154105806, "updated": 1793162671840,
        "status": "reviewed", "magType": "mww", "type": "earthquake", "ids": ",us7000ttlm,",
    },
    "geometry": {"type": "Point", "coordinates": [165.446, -13.9312, 10]},
    "id": "us7000ttlm",
}


async def main():
    productor = AIOKafkaProducer(bootstrap_servers=BOOTSTRAP, acks="all")  # acks="all": esperar confirmación del broker
    await productor.start()          # conectar con Kafka
    try:
        mensaje = construir_mensaje(EVENTO_EJEMPLO, source="prueba-manual", mode="live")
        clave = EVENTO_EJEMPLO["id"].encode("utf-8")                  # clave = id del terremoto (contrato)
        valor = json.dumps(mensaje, ensure_ascii=False).encode("utf-8")  # valor = JSON en bytes

        # send_and_wait: envía y ESPERA a que Kafka confirme. Solo entonces lo damos por publicado (enunciado §5.5)
        resultado = await productor.send_and_wait(TOPIC, value=valor, key=clave)
        print(f"[productor] publicado id={EVENTO_EJEMPLO['id']} topic={resultado.topic} "
              f"particion={resultado.partition} offset={resultado.offset}")
    finally:
        await productor.stop()       # cerrar la conexión siempre, aunque haya error


if __name__ == "__main__":
    asyncio.run(main())
