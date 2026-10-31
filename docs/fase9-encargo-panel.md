# Encargo · Fase 9 · Panel Angular

> Para Claude Code. Antes de empezar, lee `CLAUDE.md` y `docs/prompt-principal.md`.

## Objetivo
Convertir el mapa de demostración del profesor (`frontend/`, Angular 20.3 + ngx-leaflet + Leaflet 1.9.4) en el
**panel del observatorio**, que consume **nuestra API** (nunca USGS directamente; enunciado §8 y FAQ 25).

## Requisitos (enunciado §8; contrato `docs/material-profesor/CONTRATO-API.md`)
1. **Mapa interactivo**: fondo, fronteras, círculos y ficha del terremoto. Tamaño según la magnitud, color según la profundidad,
   **leyenda** y tratamiento visible de los nulos (magnitud ND, «Sin país asignado»). *Ya existe en `app.component.ts`;
   reutilizarlo y ampliarlo, no reescribirlo desde cero.*
2. **Recuentos por país o subregión** y **ventanas fijas de 1 h UTC** (por tiempo del evento), con «Sin país asignado».
3. **Distribuciones de magnitud y de profundidad**, indicando los registros sin valor.
4. **Comparación histórica**: recuento reciente frente a la media de 2025 con los mismos filtros; mostrar también la
   mediana/p10/p90 y el % de días (`dias_2025`) y la **nota** (periodo posiblemente incompleto, Kamchatka, no es una predicción).
   Si `variacion_pct` es null → mostrar «ND».
5. **Filtros** de fecha (inicio/fin), magnitud mínima y país (lista de `por_pais`, incluido «Sin país asignado» =
   `SIN_PAIS`), aplicados **a la vez** al mapa, la tabla y los gráficos (las dos llamadas a la API con los mismos parámetros).
6. **Estado del sistema**: último acceso correcto a la API (hora local del navegador), `generated`, `last_ingestion`,
   periodo consultado, aviso si `datos_desactualizados` (de `/api/salud`) o si la API no responde.
   **No presentar datos antiguos como recién obtenidos**: si falla, se conserva la última lectura marcada como antigua.
7. **Tabla consultable** de eventos (alternativa accesible al mapa y al color): fecha UTC, magnitud (ND), profundidad,
   país, lugar; ordenable o al menos ordenada por fecha.
8. Si `metadata.truncated` es true → avisarlo (no calcular estadísticas sobre la muestra truncada; las estadísticas ya vienen de la API).
9. Refresco cada 60 s (ya implementado, `refreshMs` en `public/config.json`); sin peticiones solapadas.

## La API (ya funcionando; ver `backend/src/api.py` o http://localhost:8000/docs)
- `GET /api/eventos?start&end&min_mag&country_id&limit&offset` → FeatureCollection; `metadata`: generated,
  last_ingestion, mode, count, total, truncated, next_offset, periodo, filtros. `properties`: mag, magType, place,
  time (ms), updated (ms), status, country_id, country_name, subregion. Coordenadas [lon, lat, prof].
- `GET /api/estadisticas?start&end&min_mag&country_id` → total, sin_valor{magnitud,profundidad,pais}, por_pais[],
  por_subregion[], por_hora_utc[{hora,n}], distribucion_magnitud{tramo,tramos[{desde,hasta,n}],sin_valor},
  distribucion_profundidad{clases[{clase,n}],sin_valor}, comparacion_historica{…, dias_2025{mediana,p10,p90,pct_…}, nota}.
- `GET /api/salud` → api, base_datos, generated, last_ingestion, segundos_desde_ultima_ingesta, datos_desactualizados.
- Fechas `start`/`end` en ISO 8601 UTC (start inclusivo, end exclusivo). Por defecto, últimas 24 h.
- CORS ya permite `http://localhost:4200` y la cabecera `ngrok-skip-browser-warning`.

## Restricciones y decisiones
- **Gráficos sin dependencias nuevas** si es razonable (barras con HTML/CSS o SVG). Si se añade una librería, fijar la
  versión, actualizar `package-lock.json` y justificarlo en la memoria.
- Mantener las versiones del `package.json` del profesor (Angular 20.3, ngx-leaflet 20, Leaflet 1.9.4).
- Desarrollo: `frontend/public/config.json` en `"mode": "api"` con `"apiUrl": "http://localhost:8000"`. (En la Fase 10 se
  cambiará a la URL HTTPS de ngrok.) El modo `demo` debe seguir funcionando.
- Separar en componentes pequeños si ayuda a explicarlo (filtros, estado, mapa, tabla, gráficos), con un servicio que hable con la API.
- Accesibilidad básica: textos, no solo color; etiquetas en los filtros.
- Verificar con `npm run build` (sin errores) y en el navegador; guardar capturas en `docs/evidencias/fase9-*.png`
  (pedirle a Daniel que las haga si hace falta).

## Orden sugerido (un bloque cada vez, explicado y con commit al final de cada uno)
1. Configuración en modo api + servicio de API + estado del sistema (salud, avisos).
2. Filtros conectados al mapa (las mismas consultas).
3. Tabla de eventos.
4. Estadísticas: recuentos por país/subregión, ventanas horarias, distribuciones.
5. Comparación histórica.
6. Revisión final: modo demo sigue funcionando, `npm run build` limpio, capturas, documentación.
