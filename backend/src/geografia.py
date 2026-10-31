"""Integración geográfica (enunciado §4.3): ¿en qué país cae un terremoto?

Fuente: catálogo Natural Earth entregado por el profesor (frontend/public/datos/paises.geojson, 177 entidades),
montado en el contenedor en modo solo lectura. Puntos y polígonos están en WGS84 (lon/lat), el mismo sistema.

Reglas documentadas:
  - Punto en polígono con `covered_by` (punto cubierto por el polígono): un punto justo sobre la frontera cuenta como DENTRO.
  - Si cubren el punto VARIOS países (frontera compartida): gana el country_id menor alfabéticamente
    (regla determinista) y se cuenta en `multiples` para la memoria.
  - Si no lo cubre ninguno: None = «Sin país asignado» (mar, costa simplificada, territorio no incluido).
    NUNCA se asigna el país más cercano.
  - Geometrías no válidas del catálogo (USA y SDN: autointersección) se reparan EN MEMORIA con make_valid;
    el archivo original no se modifica.
  - NO se usa el texto de `place` (lo prohíbe el enunciado).
"""

import json
import os

from shapely import STRtree
from shapely.geometry import Point, shape
from shapely.validation import make_valid

RUTA_PAISES = os.environ.get("PAISES_GEOJSON", "/data/paises.geojson")


class Catalogo:
    def __init__(self, ruta: str = RUTA_PAISES):
        with open(ruta, encoding="utf-8") as f:
            datos = json.load(f)

        self.paises = []        # filas para la tabla `pais`
        self.ids = []           # country_id en el mismo orden que self.geoms
        self.geoms = []
        self.reparadas = []     # country_id cuya geometría hubo que reparar
        self.multiples = 0      # contador de puntos cubiertos por más de un país

        for feat in datos["features"]:
            p = feat["properties"]
            cid = p["ADM0_A3"]
            geom = shape(feat["geometry"])
            if not geom.is_valid:
                geom = make_valid(geom)
                self.reparadas.append(cid)
            self.ids.append(cid)
            self.geoms.append(geom)
            self.paises.append({
                "country_id": cid, "nombre_es": p.get("NAME_ES"), "admin": p.get("ADMIN"),
                "continente": p.get("CONTINENT"), "subregion": p.get("SUBREGION"),
            })

        # Comprobación de unicidad exigida por el enunciado antes de usar ADM0_A3 como clave
        if len(set(self.ids)) != len(self.ids):
            raise ValueError("ADM0_A3 no es único en el catálogo")

        # Índice espacial: en vez de comprobar los 177 polígonos (O(n)), el árbol descarta de golpe
        # los que están lejos usando sus rectángulos envolventes y devuelve solo unos pocos candidatos.
        self.arbol = STRtree(self.geoms)

    def asignar(self, lon: float, lat: float) -> str | None:
        """Devuelve el country_id del país que contiene el punto, o None si no hay ninguno."""
        punto = Point(lon, lat)                                     # ¡ojo! Point(x=lon, y=lat)
        # OJO con el sentido: query evalúa predicado(punto, polígono). "covered_by" = el punto está cubierto
        # por el polígono (dentro o en su borde). Con "covers" se preguntaría al revés y nunca daría True.
        candidatos = self.arbol.query(punto, predicate="covered_by")
        if len(candidatos) == 0:
            return None
        ids = sorted(self.ids[i] for i in candidatos)
        if len(ids) > 1:
            self.multiples += 1
        return ids[0]
