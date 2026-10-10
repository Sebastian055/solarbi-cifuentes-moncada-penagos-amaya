"""
SolarBI · Carga de lecturas limpias a silver.lectura_5min
==========================================================
Lee el CSV limpio (Silver) y lo carga en PostgreSQL mediante UPSERT.

Uso:
    python etl/load_silver.py
"""
import pandas as pd

from etl.load_postgres import get_conn, cargar_silver, contar, SILVER_CSV


def main() -> None:
    # 1. Leer el CSV limpio
    print("Leyendo CSV limpio...")
    df = pd.read_csv(SILVER_CSV, parse_dates=["ts"])
    print(f"Filas en el CSV: {len(df)}")

    # 2. Conectar y cargar
    conn = get_conn()
    try:
        n = cargar_silver(conn, df)
        total = contar(conn, "silver.lectura_5min")

        print(f"\nFilas enviadas en esta ejecución: {n}")
        print(f"Total en silver.lectura_5min    : {total}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()