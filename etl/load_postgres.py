"""
SolarBI · Módulo de carga a PostgreSQL
=======================================
Carga idempotente de los datos limpios (Silver) y del resumen
diario (Gold) usando UPSERT (INSERT ... ON CONFLICT ... DO UPDATE).

Las credenciales se leen desde el archivo .env (no versionado).
"""
import os
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Cargar variables de entorno (.env en la raíz del proyecto)
load_dotenv()

RAIZ = Path(__file__).resolve().parent.parent
SILVER_CSV = RAIZ / "data" / "silver" / "telemetria_limpia.csv"


# ------------------------------------------------------------
# Conexión
# ------------------------------------------------------------
def get_conn():
    """Devuelve una conexión nueva a PostgreSQL usando el .env."""
    return psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "solarbi"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD"),
    )


# ------------------------------------------------------------
# Carga Silver
# ------------------------------------------------------------
def cargar_silver(conn, df: pd.DataFrame) -> int:
    """
    Carga las lecturas limpias de 5 minutos en silver.lectura_5min.

    Usa UPSERT sobre la PK (ts, dispositivo_id): si la lectura ya
    existe se actualiza, si no se inserta. Idempotente.

    Returns:
        Número de filas enviadas.
    """
    sql = """
        INSERT INTO silver.lectura_5min
            (ts, dispositivo_id, p_ac_kw, irradiancia_wm2, temp_modulo_c)
        VALUES %s
        ON CONFLICT (ts, dispositivo_id) DO UPDATE SET
            p_ac_kw         = EXCLUDED.p_ac_kw,
            irradiancia_wm2 = EXCLUDED.irradiancia_wm2,
            temp_modulo_c   = EXCLUDED.temp_modulo_c;
    """
    filas = list(df.itertuples(index=False, name=None))
    with conn.cursor() as cur:
        execute_values(cur, sql, filas)
    conn.commit()
    return len(filas)


# ------------------------------------------------------------
# Carga Gold
# ------------------------------------------------------------
def cargar_gold(conn, df: pd.DataFrame) -> int:
    """
    Carga el resumen diario en dwh.fact_energia_dia.

    Usa UPSERT sobre la PK (fecha_key, dispositivo_key). Idempotente.

    Returns:
        Número de filas enviadas.
    """
    sql = """
        INSERT INTO dwh.fact_energia_dia
            (fecha_key, dispositivo_key, fecha, energia_kwh, pct_datos_validos)
        VALUES %s
        ON CONFLICT (fecha_key, dispositivo_key) DO UPDATE SET
            fecha             = EXCLUDED.fecha,
            energia_kwh       = EXCLUDED.energia_kwh,
            pct_datos_validos = EXCLUDED.pct_datos_validos,
            actualizado_en    = NOW();
    """
    filas = list(df.itertuples(index=False, name=None))
    with conn.cursor() as cur:
        execute_values(cur, sql, filas)
    conn.commit()
    return len(filas)


# ------------------------------------------------------------
# Utilidad
# ------------------------------------------------------------
def contar(conn, tabla: str) -> int:
    """Devuelve el número de filas de una tabla."""
    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) FROM {tabla};")
        return cur.fetchone()[0]