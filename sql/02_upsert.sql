    -- ============================================================
-- SolarBI · Consultas UPSERT (referencia)
-- Ejecutadas desde etl/load_postgres.py con psycopg2
-- ============================================================

-- Silver: UPSERT de lecturas limpias de 5 minutos
-- Clave de conflicto: (ts, dispositivo_id)
INSERT INTO silver.lectura_5min
    (ts, dispositivo_id, p_ac_kw, irradiancia_wm2, temp_modulo_c)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT (ts, dispositivo_id) DO UPDATE SET
    p_ac_kw         = EXCLUDED.p_ac_kw,
    irradiancia_wm2 = EXCLUDED.irradiancia_wm2,
    temp_modulo_c   = EXCLUDED.temp_modulo_c;

-- Gold: UPSERT del resumen diario
-- Clave de conflicto: (fecha_key, dispositivo_key)
INSERT INTO dwh.fact_energia_dia
    (fecha_key, dispositivo_key, fecha, energia_kwh, pct_datos_validos)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT (fecha_key, dispositivo_key) DO UPDATE SET
    fecha             = EXCLUDED.fecha,
    energia_kwh       = EXCLUDED.energia_kwh,
    pct_datos_validos = EXCLUDED.pct_datos_validos,
    actualizado_en    = NOW();