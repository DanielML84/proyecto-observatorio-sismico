"""PASO 1 del histórico: descarga el año 2025 de la API FDSN de USGS y lo guarda en data/historico/.

Alcance (propuesta del enunciado §4.2): año 2025, ámbito mundial, magnitud >= 4, tipo earthquake.
Procedimiento:
  - Un intervalo por mes. Antes de descargar se llama a /count con los mismos parámetros.
  - Si un intervalo supera MAX_EVENTOS (20.000, límite del servicio), se PARTE EN DOS y se repite
    (nunca se trunca en silencio; la API además respondería HTTP 400).
  - Cada respuesta se guarda TAL CUAL en data/historico/<inicio>_<fin>.geojson.
  - Se escribe data/historico/manifest.json con URL, fecha de extracción y recuentos de cada consulta,
    y cada petición queda registrada en la tabla consulta_ingesta (fuente 'usgs-fdsn').
  - Reintentos con espera progresiva ante timeout/429/5xx.
Re-ejecutable: si el archivo de un intervalo ya existe, NO se vuelve a descargar (se reutiliza).
Uso:  docker compose run --rm productor python -m src.historico_descargar
"""

import asyncio
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from src import db

BASE = "https://earthquake.usgs.gov/fdsnws/event/1/"
DESTINO = Path("/data/historico")
MAX_EVENTOS = 20000
PARAMS_FIJOS = {"format": "geojson", "minmagnitude": "4", "eventtype": "earthquake", "orderby": "time-asc"}
ANIO = 2025


def iso(d: datetime) -> str:
    return d.strftime("%Y-%m-%dT%H:%M:%SZ")


def get_con_reintentos(url: str, intentos: int = 4, timeout: int = 60) -> tuple[int, bytes]:
    """GET con reintentos 2/4/8 s ante fallos temporales. Devuelve (status, cuerpo)."""
    for i in range(intentos):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "observatorio-sismico (proyecto educativo)"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            if not (e.code == 429 or e.code >= 500) or i == intentos - 1:
                raise
        except (urllib.error.URLError, TimeoutError, OSError):
            if i == intentos - 1:
                raise
        espera = 2 ** (i + 1)
        print(f"  reintento en {espera} s…")
        time.sleep(espera)
    raise RuntimeError("inalcanzable")


async def registrar(conn, url, status, ok, n, ms, error=None):
    await db.registrar_consulta(conn, "usgs-fdsn", url, status, ok, n, None, ms, error)


async def descargar_intervalo(conn, inicio: datetime, fin: datetime, manifiesto: list) -> None:
    params = {**PARAMS_FIJOS, "starttime": iso(inicio), "endtime": iso(fin)}
    qs = urllib.parse.urlencode(params)
    archivo = DESTINO / f"{inicio:%Y%m%dT%H%M%S}_{fin:%Y%m%dT%H%M%S}.geojson"

    # 1) ¿Cuántos eventos hay? (/count con los MISMOS parámetros)
    url_count = f"{BASE}count?{qs}"
    t0 = time.monotonic()
    status, cuerpo = await asyncio.to_thread(get_con_reintentos, url_count)
    n = json.loads(cuerpo)["count"]
    await registrar(conn, url_count, status, True, n, int((time.monotonic() - t0) * 1000))
    print(f"{iso(inicio)} -> {iso(fin)}: count = {n}")

    # 2) Si supera el máximo, partir el intervalo en dos mitades y repetir
    if n > MAX_EVENTOS:
        mitad = inicio + (fin - inicio) / 2
        print(f"  supera {MAX_EVENTOS}: se divide en dos")
        await descargar_intervalo(conn, inicio, mitad, manifiesto)
        await descargar_intervalo(conn, mitad, fin, manifiesto)
        return

    # 3) Descargar (o reutilizar si ya existe)
    url_query = f"{BASE}query?{qs}"
    if archivo.exists():
        datos = json.loads(archivo.read_bytes())
        print(f"  ya descargado: {archivo.name} ({len(datos['features'])} eventos) -> se reutiliza")
        extraido = datos["metadata"].get("generated")
    else:
        t0 = time.monotonic()
        status, cuerpo = await asyncio.to_thread(get_con_reintentos, url_query)
        datos = json.loads(cuerpo)
        archivo.write_bytes(cuerpo)                        # se guarda TAL CUAL llegó
        await registrar(conn, url_query, status, True, len(datos["features"]), int((time.monotonic() - t0) * 1000))
        extraido = datos["metadata"].get("generated")
        print(f"  descargado: {archivo.name} ({len(datos['features'])} eventos)")

    if len(datos["features"]) != n:
        print(f"  AVISO: count={n} pero la descarga trae {len(datos['features'])} (el catálogo puede haber cambiado entre peticiones)")
    manifiesto.append({
        "inicio": iso(inicio), "fin": iso(fin), "url": url_query, "archivo": archivo.name,
        "count_previo": n, "eventos_descargados": len(datos["features"]),
        "extraido_utc": datetime.fromtimestamp(extraido / 1000, tz=timezone.utc).isoformat() if extraido else None,
    })


async def main():
    DESTINO.mkdir(parents=True, exist_ok=True)
    conn = await db.conectar()
    manifiesto = []
    for mes in range(1, 13):
        inicio = datetime(ANIO, mes, 1, tzinfo=timezone.utc)
        fin = datetime(ANIO + (mes == 12), (mes % 12) + 1, 1, tzinfo=timezone.utc)
        await descargar_intervalo(conn, inicio, fin, manifiesto)
        await asyncio.sleep(1)                              # cortesía con el servicio público
    (DESTINO / "manifest.json").write_text(json.dumps(manifiesto, indent=2, ensure_ascii=False), encoding="utf-8")
    total = sum(m["eventos_descargados"] for m in manifiesto)
    print(f"\nHecho: {len(manifiesto)} archivos, {total} eventos en total (antes de deduplicar). Manifiesto: manifest.json")
    await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
