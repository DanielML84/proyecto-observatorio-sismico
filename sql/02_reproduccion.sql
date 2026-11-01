-- =====================================================================================
-- 02 · REPRODUCCIÓN HISTÓRICA AISLADA (enunciado §11, guía §2.9, FAQ «reproducción»)
-- =====================================================================================
-- Aislamiento: un ESQUEMA aparte ("replay") con las MISMAS tablas de hechos que el live.
--   * public.*  -> datos actuales (live + histórico 2025)
--   * replay.*  -> SOLO lo que llega por el topic terremotos.replay
-- Las dimensiones (pais, fecha) son compartidas: son catálogos, no datos de actualidad.
--
-- Se ejecuta SOLO en un volumen vacío (docker-entrypoint-initdb.d, después de 01_esquema.sql).
-- En una base que ya existe, aplicarlo a mano (es idempotente, se puede repetir):
--   docker compose exec -T postgres psql -U observatorio -d observatorio < sql/02_reproduccion.sql
-- =====================================================================================

-- 1) Hora de reproducción. En el live queda NULL; en replay guarda cuándo se reprodujo
--    (el tiempo ORIGINAL del terremoto sigue en event_time, sin tocar).
ALTER TABLE public.evento_actual  ADD COLUMN IF NOT EXISTS replayed_at TIMESTAMPTZ;
ALTER TABLE public.evento_version ADD COLUMN IF NOT EXISTS replayed_at TIMESTAMPTZ;

-- 2) Esquema separado
CREATE SCHEMA IF NOT EXISTS replay;

-- 3) Copias de la estructura. LIKE ... INCLUDING ALL copia columnas, tipos, NOT NULL, CHECK, valores por defecto,
--    clave primaria, UNIQUE e índices. NO copia las claves foráneas: se añaden debajo.
CREATE TABLE IF NOT EXISTS replay.evento_actual  (LIKE public.evento_actual  INCLUDING ALL);
CREATE TABLE IF NOT EXISTS replay.evento_version (LIKE public.evento_version INCLUDING ALL);
CREATE TABLE IF NOT EXISTS replay.cuarentena     (LIKE public.cuarentena     INCLUDING ALL);
-- Nota: replay.cuarentena.id usa por defecto la MISMA secuencia que public.cuarentena (lo copia LIKE).
-- Es inofensivo: solo genera números únicos.

-- 4) Claves foráneas hacia las dimensiones compartidas (solo si no existen ya)
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'replay_evento_actual_fecha_fk') THEN
    ALTER TABLE replay.evento_actual ADD CONSTRAINT replay_evento_actual_fecha_fk
      FOREIGN KEY (fecha_id) REFERENCES public.fecha (fecha_id);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'replay_evento_actual_pais_fk') THEN
    ALTER TABLE replay.evento_actual ADD CONSTRAINT replay_evento_actual_pais_fk
      FOREIGN KEY (country_id) REFERENCES public.pais (country_id);
  END IF;
END $$;
