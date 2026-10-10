from pathlib import Path
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
SILVER = RAIZ / "data" / "silver" / "telemetria_limpia.csv"

# Energía de cada intervalo: potencia (kW) × 5/60 h
INTERVALO_HORAS = 5 / 60


def construir_fact_diaria() -> pd.DataFrame:
    """Lee Silver y agrega la energía diaria por dispositivo."""
    df = pd.read_csv(SILVER, parse_dates=["ts"])
    df["fecha"] = df["ts"].dt.date

    # Energía del intervalo (kWh) y total diario
    df["energia_kwh"] = df["p_ac_kw"] * INTERVALO_HORAS

    agg = (
        df.groupby(["fecha", "dispositivo_id"], as_index=False)
          .agg(
              energia_kwh=("energia_kwh", "sum"),
              lecturas_validas=("ts", "count"),
          )
    )

    # Porcentaje de datos válidos del día (esperado: 288 lecturas = 24h/5min)
    LECTURAS_ESPERADAS = 288
    agg["pct_datos_validos"] = (
        100 * agg["lecturas_validas"] / LECTURAS_ESPERADAS
    ).round(2)

    # Claves del esquema estrella
    agg["fecha_key"] = agg["fecha"].apply(lambda f: int(f.strftime("%Y%m%d")))
    agg["dispositivo_key"] = agg["dispositivo_id"]
    agg["energia_kwh"] = agg["energia_kwh"].round(3)

    return agg[[
        "fecha_key", "dispositivo_key", "fecha",
        "energia_kwh", "pct_datos_validos",
    ]]