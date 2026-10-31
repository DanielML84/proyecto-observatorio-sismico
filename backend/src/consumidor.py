"""Consumidor: lee terremotos.live, VALIDA, y GUARDA en PostgreSQL de forma idempotente.

Orden por cada mensaje (FAQ 13):
  1. Leer y validar (src/validacion.py)
  2. Guardar en PostgreSQL dentro de una transacción (src/db.py), o en cuarentena si no es válido
  3. Confirmar la transacción
  4. Confirmar el offset en Kafka  <- SOLO después de guardar
Si el proceso cae entre 3 y 4, Kafka reenvía el mensaje; la base lo absorbe sin duplicar (idempotencia).
Si la base de datos falla, NO se confirma el offset: el proceso termina con error, Docker lo reinicia
(restart: unless-stopped) y el mensaje se vuelve a procesar ("al menos una vez").
"""

import asyncio
import json
import os

from aiokafka import AIOKafkaConsumer

from src import db
from src.validacion import Rechazo, validar

BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC = os.environ.get("KAFKA_TOPIC", "terremotos.live")
GROUP_ID = os.environ.get("KAFKA_GROUP_ID", "consumidor-observatorio")


async def procesar(conn, registro) -> str:
    """Procesa UN registro de Kafka y devuelve un texto con el resultado (para el log)."""
    texto = registro.value.decode("utf-8", errors="replace")
    donde = (registro.topic, registro.partition, registro.offset)

    try:
        mensaje = json.loads(texto)
    except json.JSONDecodeError:
        await db.guardar_cuarentena(conn, "invalido", "json_invalido", None, *donde, texto)
        return "cuarentena: json_invalido"

    resultado = validar(mensaje)
    if isinstance(resultado, Rechazo):
        await db.guardar_cuarentena(conn, resultado.tipo, resultado.motivo, resultado.event_id, *donde, texto)
        return f"{'excluido' if resultado.tipo == 'excluido' else 'cuarentena'}: {resultado.motivo}"

    return await db.guardar_evento(conn, resultado.campos, mensaje["event"])


async def main():
    conn = await db.conectar()
    print("[consumidor] conectado a PostgreSQL")
    consumidor = AIOKafkaConsumer(
        TOPIC,
        bootstrap_servers=BOOTSTRAP,
        group_id=GROUP_ID,
        enable_auto_commit=False,      # el offset lo confirmamos nosotros, DESPUÉS de guardar
        auto_offset_reset="earliest",  # grupo nuevo -> empezar desde el principio del topic
    )
    await consumidor.start()
    print(f"[consumidor] escuchando topic={TOPIC} grupo={GROUP_ID}")
    try:
        async for registro in consumidor:
            clave = registro.key.decode("utf-8") if registro.key else None
            resultado = await procesar(conn, registro)       # si falla la BD, lanza excepción y NO se confirma
            await consumidor.commit()                        # confirmar offset SOLO tras guardar
            print(f"[consumidor] p={registro.partition} off={registro.offset} clave={clave} -> {resultado}")
    finally:
        await consumidor.stop()
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
