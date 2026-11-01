-- =====================================================================================
-- ANÁLISIS DE CALIDAD sobre los datos guardados (enunciado §6 · guía §2.4)
-- Uso (PowerShell, desde la carpeta del proyecto):
--   Get-Content analisis/calidad.sql | docker compose exec -T postgres psql -U observatorio -d observatorio
-- Solo LEE (SELECT): no cambia nada. Está fuera de sql/ a propósito: lo de sql/ se ejecuta al crear la base.
-- Los datos SINTÉTICOS (source 'prueba%', ids 'PRUEBA-%') se cuentan aparte y se excluyen del resto.
-- Esquema public (datos actuales). La reproducción (esquema replay) no entra.
-- =====================================================================================
\pset footer off

\echo '=== 0. DENOMINADORES: qué conjunto se mide =============================================='
SELECT source,
       COUNT(*)                           AS terremotos_actuales,
       MIN(event_time)::date              AS desde,
       MAX(event_time)::date              AS hasta
FROM evento_actual GROUP BY source ORDER BY 2 DESC;
SELECT (SELECT COUNT(*) FROM evento_version)                          AS versiones_guardadas,
       (SELECT COUNT(*) FROM evento_version WHERE source LIKE 'prueba%') AS versiones_sinteticas,
       (SELECT COUNT(*) FROM cuarentena)                              AS mensajes_en_cuarentena,
       (SELECT COUNT(*) FROM cuarentena WHERE event_id LIKE 'PRUEBA-%') AS cuarentena_sintetica;

\echo '=== 1. COMPLETITUD: % de terremotos (reales) con el campo informado ======================'
SELECT source, COUNT(*) AS n,
       ROUND(100.0 * COUNT(mag)        / COUNT(*), 2) AS pct_mag,
       ROUND(100.0 * COUNT(mag_type)   / COUNT(*), 2) AS pct_mag_type,
       ROUND(100.0 * COUNT(depth_km)   / COUNT(*), 2) AS pct_depth,
       ROUND(100.0 * COUNT(place)      / COUNT(*), 2) AS pct_place,
       ROUND(100.0 * COUNT(status)     / COUNT(*), 2) AS pct_status,
       ROUND(100.0 * COUNT(country_id) / COUNT(*), 2) AS pct_pais
FROM evento_actual WHERE source NOT LIKE 'prueba%' GROUP BY source ORDER BY n DESC;

\echo '=== 2. UNICIDAD ==========================================================================='
\echo '--- 2a. Estado actual: filas frente a ids distintos (deben coincidir)'
SELECT COUNT(*) AS filas, COUNT(DISTINCT event_id) AS ids_distintos FROM evento_actual;
\echo '--- 2b. Historial: versiones (id, updated) repetidas (debe ser 0)'
SELECT COUNT(*) AS versiones_repetidas FROM (
  SELECT event_id, updated_ms FROM evento_version GROUP BY 1, 2 HAVING COUNT(*) > 1) t;
\echo '--- 2c. Cuántas versiones distintas se han visto de cada terremoto (reales)'
SELECT n_versiones, COUNT(*) AS terremotos FROM (
  SELECT event_id, COUNT(*) AS n_versiones FROM evento_version WHERE source NOT LIKE 'prueba%' GROUP BY 1) t
GROUP BY 1 ORDER BY 1;

\echo '=== 3. VALIDEZ (terremotos reales) ========================================================'
SELECT COUNT(*) FILTER (WHERE lat NOT BETWEEN -90 AND 90 OR lon NOT BETWEEN -180 AND 180) AS coord_fuera_rango,
       MIN(mag) AS mag_min, MAX(mag) AS mag_max,
       COUNT(*) FILTER (WHERE mag < 0)        AS mag_negativa,
       MIN(depth_km) AS prof_min, MAX(depth_km) AS prof_max,
       COUNT(*) FILTER (WHERE depth_km < 0)   AS prof_negativa,
       COUNT(*) FILTER (WHERE depth_km > 700) AS prof_mayor_700
FROM evento_actual WHERE source NOT LIKE 'prueba%';
\echo '--- 3b. Mensajes rechazados por regla (reales y sintéticos por separado)'
SELECT CASE WHEN event_id LIKE 'PRUEBA-%' THEN 'sintético' ELSE 'real' END AS origen,
       tipo, motivo, COUNT(*) AS mensajes
FROM cuarentena GROUP BY 1, 2, 3 ORDER BY 1, 4 DESC;

\echo '=== 4. CONSISTENCIA ======================================================================='
\echo '--- 4a. Claves: país inexistente / día que no corresponde a event_time (deben ser 0)'
SELECT COUNT(*) FILTER (WHERE country_id IS NOT NULL AND country_id NOT IN (SELECT country_id FROM pais)) AS pais_inexistente,
       COUNT(*) FILTER (WHERE fecha_id <> (event_time AT TIME ZONE 'UTC')::date)                       AS dia_incoherente,
       COUNT(*) FILTER (WHERE updated_at < event_time)                                                 AS actualizado_antes_de_ocurrir
FROM evento_actual;
\echo '--- 4b. Secuencia de revisiones: el estado actual tiene la versión MÁS RECIENTE del historial (debe ser 0)'
SELECT COUNT(*) AS actual_no_es_la_ultima FROM evento_actual a
JOIN (SELECT event_id, MAX(updated_ms) AS ultima FROM evento_version GROUP BY 1) v USING (event_id)
WHERE a.updated_ms <> v.ultima;
\echo '--- 4c. Unidades/escalas de magnitud (reales)'
SELECT COALESCE(mag_type, '(nulo)') AS mag_type, COUNT(*) FROM evento_actual
WHERE source NOT LIKE 'prueba%' GROUP BY 1 ORDER BY 2 DESC LIMIT 12;

\echo '=== 5. ACTUALIDAD (solo feed en vivo) ====================================================='
\echo '--- 5a. Retrasos en minutos: ocurrencia -> última actualización USGS -> nuestra ingesta'
SELECT COUNT(*) AS terremotos,
       ROUND((percentile_cont(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM updated_at - event_time)) / 60)::numeric, 1)  AS mediana_min_ocurrencia_a_updated,
       ROUND((percentile_cont(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM ingested_at - event_time)) / 60)::numeric, 1) AS mediana_min_ocurrencia_a_ingesta,
       ROUND((percentile_cont(0.9) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM ingested_at - event_time)) / 60)::numeric, 1) AS p90_min_ocurrencia_a_ingesta,
       ROUND((percentile_cont(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM processed_at - ingested_at)))::numeric, 2)  AS mediana_s_ingesta_a_guardado
FROM evento_actual WHERE source = 'usgs-feed-all_day';
\echo '--- 5b. Consultas al feed: correctas, fallidas y huecos de más de 5 min entre consultas correctas'
SELECT COUNT(*) FILTER (WHERE ok) AS correctas, COUNT(*) FILTER (WHERE NOT ok) AS fallidas,
       MIN(solicitada_at) AS primera, MAX(solicitada_at) AS ultima
FROM consulta_ingesta WHERE fuente = 'usgs-feed-all_day';
SELECT anterior, solicitada_at AS siguiente, ROUND(EXTRACT(EPOCH FROM solicitada_at - anterior) / 3600, 2) AS horas_sin_consultar
FROM (SELECT solicitada_at, LAG(solicitada_at) OVER (ORDER BY solicitada_at) AS anterior
      FROM consulta_ingesta WHERE fuente = 'usgs-feed-all_day' AND ok) t
WHERE solicitada_at - anterior > interval '5 minutes' ORDER BY anterior;

\echo '=== 6. TRANSFORMACIONES: cuántos registros afecta cada una (terremotos reales) ============='
SELECT COUNT(*)                                   AS fechas_ms_a_utc,
       COUNT(country_id)                          AS con_pais_asignado,
       COUNT(*) - COUNT(country_id)               AS sin_pais_asignado,
       COUNT(*) FILTER (WHERE country_id IN ('USA', 'SDN')) AS en_geometrias_reparadas
FROM evento_actual WHERE source NOT LIKE 'prueba%';
