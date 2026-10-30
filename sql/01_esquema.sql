-- =====================================================================================
-- Observatorio de actividad sísmica · Esquema de la base de datos (nivel FÍSICO)
-- PostgreSQL ejecuta este archivo automáticamente la PRIMERA vez que arranca con el
-- volumen vacío (carpeta /docker-entrypoint-initdb.d). Si el volumen ya tiene datos, NO se vuelve a ejecutar.
-- Convenciones: fechas en UTC (TIMESTAMPTZ); "_ms" = milisegundos Unix tal como los da USGS.
-- =====================================================================================

-- -------------------------------------------------------------------------------------
-- DIMENSIÓN PAÍS · una fila = una entidad del catálogo Natural Earth (177)
-- Se carga desde frontend/public/datos/paises.geojson (Fase 6).
-- -------------------------------------------------------------------------------------
CREATE TABLE pais (
    country_id  TEXT PRIMARY KEY,      -- ADM0_A3 (único en el catálogo; NO siempre es un código ISO oficial)
    nombre_es   TEXT,                  -- NAME_ES
    admin       TEXT,                  -- ADMIN (nombre en inglés)
    continente  TEXT,                  -- CONTINENT
    subregion   TEXT                   -- SUBREGION
);

-- -------------------------------------------------------------------------------------
-- DIMENSIÓN FECHA · una fila = un día UTC
-- Se rellena aquí mismo con todos los días de 2024 a 2027 (cubre el histórico de 2025 y el periodo actual).
-- -------------------------------------------------------------------------------------
CREATE TABLE fecha (
    fecha_id    DATE PRIMARY KEY,      -- el día (UTC)
    anio        SMALLINT NOT NULL,
    mes         SMALLINT NOT NULL,     -- 1..12
    dia         SMALLINT NOT NULL,     -- 1..31
    dia_semana  SMALLINT NOT NULL      -- 1 = lunes … 7 = domingo (ISO)
);

INSERT INTO fecha (fecha_id, anio, mes, dia, dia_semana)
SELECT d::date,
       EXTRACT(YEAR   FROM d),
       EXTRACT(MONTH  FROM d),
       EXTRACT(DAY    FROM d),
       EXTRACT(ISODOW FROM d)
FROM generate_series('2024-01-01'::date, '2027-12-31'::date, interval '1 day') AS d;

-- -------------------------------------------------------------------------------------
-- HECHO · EVENTO ACTUAL · una fila = UN TERREMOTO con su versión más reciente
-- Es la tabla que consultan el mapa, los recuentos y las estadísticas.
-- -------------------------------------------------------------------------------------
CREATE TABLE evento_actual (
    event_id     TEXT PRIMARY KEY,                 -- id de USGS. PRIMARY KEY = único -> imposible tener 2 filas del mismo terremoto
    updated_ms   BIGINT NOT NULL,                  -- versión vigente (properties.updated, ms Unix). Se compara para aceptar o no una revisión
    event_time   TIMESTAMPTZ NOT NULL,             -- cuándo OCURRIÓ (properties.time convertido a UTC)
    updated_at   TIMESTAMPTZ NOT NULL,             -- updated_ms convertido a fecha UTC (para leerlo)
    fecha_id     DATE NOT NULL REFERENCES fecha(fecha_id),        -- día UTC de event_time (dimensión fecha)
    mag          DOUBLE PRECISION,                 -- magnitud; NULL = desconocida (NO es 0)
    mag_type     TEXT,                             -- escala de la magnitud (ml, mb, mww...)
    depth_km     DOUBLE PRECISION,                 -- profundidad en km; NULL = desconocida; puede ser negativa
    lon          DOUBLE PRECISION NOT NULL,        -- longitud  [-180, 180]
    lat          DOUBLE PRECISION NOT NULL,        -- latitud   [-90, 90]
    place        TEXT,                             -- descripción de USGS (NO se usa para asignar país)
    status       TEXT,                             -- automatic / reviewed
    country_id   TEXT REFERENCES pais(country_id), -- NULL = «Sin país asignado» (mar, costa simplificada...)
    source       TEXT NOT NULL,                    -- de dónde llegó (contrato del mensaje)
    ingested_at  TIMESTAMPTZ NOT NULL,             -- cuándo lo descargó el productor (hora de proceso)
    processed_at TIMESTAMPTZ NOT NULL DEFAULT now(),  -- cuándo lo escribió el consumidor
    CONSTRAINT ck_lat CHECK (lat BETWEEN -90 AND 90),
    CONSTRAINT ck_lon CHECK (lon BETWEEN -180 AND 180)
);

-- Índices: se justifican por las consultas de la API (y se medirán con/sin en la Fase 12)
CREATE INDEX ix_evento_actual_time    ON evento_actual (event_time);   -- filtros por intervalo y ventanas horarias
CREATE INDEX ix_evento_actual_country ON evento_actual (country_id);   -- recuentos y filtro por país

-- -------------------------------------------------------------------------------------
-- HISTORIAL · EVENTO VERSIÓN · una fila = UNA VERSIÓN observada (event_id, updated)
-- Conserva el original de cada versión. La clave compuesta impide guardar la misma versión dos veces.
-- -------------------------------------------------------------------------------------
CREATE TABLE evento_version (
    event_id     TEXT   NOT NULL,
    updated_ms   BIGINT NOT NULL,
    mag          DOUBLE PRECISION,                 -- copia de los valores de esa versión, para comparar cambios
    depth_km     DOUBLE PRECISION,
    lon          DOUBLE PRECISION,
    lat          DOUBLE PRECISION,
    event_time   TIMESTAMPTZ,
    status       TEXT,
    source       TEXT NOT NULL,
    ingested_at  TIMESTAMPTZ NOT NULL,
    received_at  TIMESTAMPTZ NOT NULL DEFAULT now(),  -- cuándo la recibió el consumidor
    raw          JSONB NOT NULL,                   -- el Feature ORIGINAL de USGS, sin modificar
    PRIMARY KEY (event_id, updated_ms)
);

-- -------------------------------------------------------------------------------------
-- CUARENTENA · una fila = un mensaje que no entra en el conjunto válido, con su motivo
--   tipo = 'invalido'  -> no se puede tratar (coordenadas imposibles, JSON roto, falta el id...)
--   tipo = 'excluido'  -> válido pero fuera del alcance (type != earthquake)
-- -------------------------------------------------------------------------------------
CREATE TABLE cuarentena (
    id              BIGSERIAL PRIMARY KEY,
    tipo            TEXT NOT NULL CHECK (tipo IN ('invalido', 'excluido')),
    motivo          TEXT NOT NULL,                 -- p. ej. 'lat_fuera_de_rango', 'type=explosion'
    event_id        TEXT,                          -- puede faltar si el mensaje está roto
    kafka_topic     TEXT NOT NULL,                 -- referencia al mensaje original en Kafka
    kafka_partition INTEGER NOT NULL,
    kafka_offset    BIGINT NOT NULL,
    raw             TEXT NOT NULL,                 -- el mensaje tal cual (TEXT: puede no ser JSON válido)
    received_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_cuarentena_mensaje UNIQUE (kafka_topic, kafka_partition, kafka_offset)  -- reprocesar no duplica
);

-- -------------------------------------------------------------------------------------
-- ESTADO DEL PRODUCTOR · una fila = la última versión PUBLICADA de cada evento
-- Es la "memoria" del productor (FAQ 10): sobrevive a reinicios, a diferencia de un diccionario en RAM.
-- -------------------------------------------------------------------------------------
CREATE TABLE version_publicada (
    event_id      TEXT PRIMARY KEY,
    updated_ms    BIGINT NOT NULL,
    published_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- -------------------------------------------------------------------------------------
-- REGISTRO DE CONSULTAS · una fila = una petición del productor a USGS
-- Sirve para: procedencia (enunciado §5.2), errores (§5.6) y «última ingesta correcta» del panel (§8.6).
-- -------------------------------------------------------------------------------------
CREATE TABLE consulta_ingesta (
    id             BIGSERIAL PRIMARY KEY,
    fuente         TEXT NOT NULL,                  -- 'usgs-feed-all_day', 'usgs-fdsn'...
    url            TEXT NOT NULL,
    solicitada_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    http_status    INTEGER,                        -- NULL si ni siquiera hubo respuesta (timeout)
    ok             BOOLEAN NOT NULL,
    n_eventos      INTEGER,                        -- cuántos traía la respuesta
    n_publicados   INTEGER,                        -- cuántos eran nuevos o revisiones y se enviaron a Kafka
    duracion_ms    INTEGER,
    error          TEXT
);
CREATE INDEX ix_consulta_ok_fecha ON consulta_ingesta (ok, solicitada_at DESC);  -- «última consulta correcta»
