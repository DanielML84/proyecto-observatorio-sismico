"""PRODUCTOR DE REPRODUCCIÓN (Fase 11 · enunciado §11 · guía §2.9).

Qué hace: reproduce por Kafka, ACELERADA y en orden de fecha, una selección del histórico 2025 ya descargado,
para poder demostrar el flujo completo sin esperar a que ocurran terremotos nuevos.

Selección (por defecto): la secuencia del terremoto M8,8 de Kamchatka (us6000qw60, 29/07/2025 23:24:52 UTC),
desde 1 h ANTES hasta 2 h DESPUÉS del principal -> 96 eventos reales de data/historico/ (Conclusión 1 de la memoria).

Reglas:
  - Topic SEPARADO: terremotos.replay (lo lee el servicio consumidor-replay, que escribe en el esquema "replay").
  - mode="replay" y replayed_at = hora real de envío. Las FECHAS ORIGINALES no se tocan (FAQ: «no cambies las fechas»).
  - Un evento cada REPLAY_INTERVALO_S segundos (2 s por defecto -> ~3 min).
  - Al final, CASOS CONTROLADOS sobre un evento de la selección (el primero), para la prueba de idempotencia:
      a) DUPLICADO: el mismo evento, misma versión            -> esperado: ignorado (version_repetida)
      b) REVISIÓN:  updated + 1 h y magnitud + 0,1 (SINTÉTICA) -> esperado: actualizado
      c) ANTIGUA:   otra vez la versión original              -> esperado: ignorado, NO sustituye a la revisión
                    (el log dirá «version_repetida» porque esa versión ya estaba en evento_version; lo importante
                     es que evento_actual conserva la revisión, que es más reciente)
    La revisión es inventada a propósito y va marcada con source='replay-caso-controlado' (nunca se presenta como USGS).

Uso (con el sistema levantado):
    docker compose run --rm productor-replay
Repetir desde cero (vacía SOLO el esquema replay, el live no se toca):
    docker compose exec postgres psql -U observatorio -d observatorio -c "TRUNCATE replay.evento_actual, replay.evento_version, replay.cuarentena"
"""

import asyncio
import copy
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from aiokafka import AIOKafkaProducer

from src.mensajes import ahora_utc_iso, construir_mensaje

BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC = os.environ.get("KAFKA_TOPIC", "terremotos.replay")
ORIGEN = Path(os.environ.get("HISTORICO_DIR", "/data/historico"))
INTERVALO_S = float(os.environ.get("REPLAY_INTERVALO_S", "2"))
EVENTO_CENTRAL = os.environ.get("REPLAY_EVENTO", "us6000qw60")   # M8,8 Kamchatka
HORAS_ANTES = float(os.environ.get("REPLAY_HORAS_ANTES", "1"))
HORAS_DESPUES = float(os.environ.get("REPLAY_HORAS_DESPUES", "2"))
FUENTE = "usgs-fdsn"                        # los 96 eventos son reales, del catálogo FDSN
FUENTE_SINTETICA = "replay-caso-controlado" # solo la revisión inventada


def cargar_seleccion() -> list[dict]:
    """Lee el histórico, deduplica por id (quedándose el mayor updated) y recorta la ventana alrededor del evento central."""
    por_id: dict[str, dict] = {}
    for archivo in sorted(ORIGEN.glob("*.geojson")):
        for ev in json.loads(archivo.read_bytes())["features"]:
            previo = por_id.get(ev["id"])
            if previo is None or ev["properties"]["updated"] > previo["properties"]["updated"]:
                por_id[ev["id"]] = ev
    if EVENTO_CENTRAL not in por_id:
        raise SystemExit(f"No encuentro {EVENTO_CENTRAL} en {ORIGEN}. ¿Está descargado el histórico (Fase 7)?")
    t0 = por_id[EVENTO_CENTRAL]["properties"]["time"]
    desde, hasta = t0 - HORAS_ANTES * 3_600_000, t0 + HORAS_DESPUES * 3_600_000
    seleccion = [e for e in por_id.values() if desde <= e["properties"]["time"] < hasta]
    seleccion.sort(key=lambda e: (e["properties"]["time"], e["id"]))       # ORDENADA por fecha original
    return seleccion


def utc(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


async def enviar(productor, evento: dict, source: str, etiqueta: str) -> None:
    """Publica UN evento con mode='replay' y espera la confirmación de Kafka (acks=all)."""
    mensaje = construir_mensaje(evento, source=source, mode="replay", replayed_at=ahora_utc_iso())
    await productor.send_and_wait(TOPIC, value=json.dumps(mensaje, ensure_ascii=False).encode(),
                                  key=evento["id"].encode())   # clave = id -> mismo id, misma partición, orden garantizado
    p = evento["properties"]
    print(f"[replay] {etiqueta:<22} {evento['id']:<12} M{p['mag']}  original={utc(p['time'])}  updated={p['updated']}")


async def main():
    seleccion = cargar_seleccion()
    print(f"[replay] selección: {len(seleccion)} eventos, de {utc(seleccion[0]['properties']['time'])} "
          f"a {utc(seleccion[-1]['properties']['time'])} · 1 cada {INTERVALO_S} s -> topic {TOPIC}")
    productor = AIOKafkaProducer(bootstrap_servers=BOOTSTRAP, acks="all")
    await productor.start()
    try:
        for i, ev in enumerate(seleccion, 1):
            await enviar(productor, ev, FUENTE, f"{i}/{len(seleccion)}")
            await asyncio.sleep(INTERVALO_S)

        # ---- Casos controlados (sobre el primer evento: llega a la base antes que ninguno)
        base = seleccion[0]
        await enviar(productor, base, FUENTE, "caso a) duplicado")
        await asyncio.sleep(INTERVALO_S)

        revision = copy.deepcopy(base)
        revision["properties"]["updated"] += 3_600_000                     # versión POSTERIOR (+1 h)
        if revision["properties"]["mag"] is not None:
            revision["properties"]["mag"] = round(revision["properties"]["mag"] + 0.1, 2)
        await enviar(productor, revision, FUENTE_SINTETICA, "caso b) revisión")
        await asyncio.sleep(INTERVALO_S)

        await enviar(productor, base, FUENTE, "caso c) versión antigua")
        print(f"[replay] terminado: {len(seleccion)} eventos + 3 casos controlados. "
              f"Esperado en replay.evento_actual: {len(seleccion)} filas; el evento {base['id']} con la revisión.")
    finally:
        await productor.stop()


if __name__ == "__main__":
    asyncio.run(main())
