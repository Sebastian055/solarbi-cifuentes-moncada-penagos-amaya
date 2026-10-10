"""
SolarBI · Carga del resumen diario a dwh.fact_energia_dia
==========================================================
Lee el CSV limpio (Silver), agrega por día en etl/gold.py y
carga el resultado en PostgreSQL mediante UPSERT.

"""
from etl.gold import construir_fact_diaria
from etl.load_postgres import get_conn, cargar_gold, contar


def main() -> None:
    # 1. Construir el resumen diario desde Silver
    print("Construyendo resumen diario (Silver -> Gold)...")
    fact = construir_fact_diaria()
    print(f"Días/dispositivos agregados: {len(fact)}")

    print("\nResumen a cargar:")
    print(fact.to_string(index=False))

    # 2. Conectar y cargar
    conn = get_conn()
    try:
        n = cargar_gold(conn, fact)
        total = contar(conn, "dwh.fact_energia_dia")

        print(f"\nFilas enviadas en esta ejecución: {n}")
        print(f"Total en dwh.fact_energia_dia   : {total}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()