"""
SolarBI · Punto de entrada único del flujo ETL
================================================
Ejecuta todo el pipeline Bronze → Silver → Gold → PostgreSQL
con un solo comando:

    python -m etl.run_etl

El flujo es idempotente: ejecutarlo varias veces deja el mismo
estado final en PostgreSQL (gracias a los UPSERT).
"""
from pathlib import Path
import pandas as pd

from etl.silver import (
    limpiar,
    imprimir_reporte,
    BRONZE,
    SILVER,
    RECHAZADOS,
)
from etl.gold import construir_fact_diaria
from etl.load_postgres import (
    get_conn,
    cargar_silver,
    cargar_gold,
    contar,
)

RAIZ = Path(__file__).resolve().parent.parent


def main() -> None:
    # ====================================================
    # 1. Bronze → Silver: limpieza y reglas de calidad
    # ====================================================
    print("=" * 60)
    print("SOLARBI · PIPELINE ETL")
    print("=" * 60)

    print("\n[1/4] Bronze → Silver (limpieza)")
    bronze = pd.read_csv(BRONZE)
    limpio, rechazado, resumen = limpiar(bronze)

    SILVER.parent.mkdir(parents=True, exist_ok=True)
    limpio.to_csv(SILVER, index=False)
    rechazado.to_csv(RECHAZADOS, index=False)
    imprimir_reporte(resumen)

    # ====================================================
    # 2. Silver → Gold: agregación diaria
    # ====================================================
    print("\n[2/4] Silver → Gold (agregación diaria)")
    fact = construir_fact_diaria()
    print(f"Días/dispositivos agregados: {len(fact)}")

    # ====================================================
    # 3. Carga a PostgreSQL: UPSERT idempotente
    # ====================================================
    print("\n[3/4] Carga a PostgreSQL (UPSERT)")
    conn = get_conn()
    try:
        n_silver = cargar_silver(conn, limpio)
        n_gold = cargar_gold(conn, fact)
        print(f"Filas enviadas a silver.lectura_5min : {n_silver}")
        print(f"Filas enviadas a dwh.fact_energia_dia: {n_gold}")

        # ====================================================
        # 4. Reporte final: conteos en PostgreSQL
        # ====================================================
        print("\n[4/4] Conteos finales en PostgreSQL")
        total_silver = contar(conn, "silver.lectura_5min")
        total_gold = contar(conn, "dwh.fact_energia_dia")
        print(f"silver.lectura_5min  : {total_silver} filas")
        print(f"dwh.fact_energia_dia : {total_gold} filas")

        print("\n" + "=" * 60)
        print("ETL COMPLETADO")
        print("=" * 60)
    finally:
        conn.close()


if __name__ == "__main__":
    main()