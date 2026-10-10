
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
BRONZE = RAIZ / "data" / "bronze" / "telemetria.csv"
SILVER = RAIZ / "data" / "silver" / "telemetria_limpia.csv"
RECHAZADOS = RAIZ / "data" / "silver" / "telemetria_rechazada.csv"

COLUMNAS_MEDIDA = ["p_ac_kw", "irradiancia_wm2", "temp_modulo_c"]

# Rango físico válido (mínimo, máximo) por variable. Inversor de 5 kWp.
RANGOS = {
    "p_ac_kw": (0.0, 5.0),            # no puede ser negativa ni superar la capacidad
    "irradiancia_wm2": (0.0, 1500.0),  # W/m²
    "temp_modulo_c": (-10.0, 100.0),   # °C
}


def limpiar(bronze: pd.DataFrame):
    """Aplica las reglas de calidad. Devuelve (limpio, rechazado, resumen)."""
    df = bronze.copy()
    df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
    df["motivo"] = None

    # Regla 1 · Duplicados: misma lectura (ts + dispositivo) repetida. Se conserva la primera.
    duplicada = df.duplicated(subset=["ts", "dispositivo_id"], keep="first")
    df.loc[duplicada, "motivo"] = "duplicado"

    # Regla 2 · Datos faltantes: fecha o alguna medida vacía.
    faltante = df[["ts"] + COLUMNAS_MEDIDA].isna().any(axis=1) & df["motivo"].isna()
    df.loc[faltante, "motivo"] = "dato_faltante"

    # Regla 3 · Rango físico válido.
    fuera = pd.Series(False, index=df.index)
    for columna, (minimo, maximo) in RANGOS.items():
        fuera |= (df[columna] < minimo) | (df[columna] > maximo)
    fuera &= df["motivo"].isna()
    df.loc[fuera, "motivo"] = "fuera_de_rango"

    valido = df["motivo"].isna()
    limpio = df.loc[valido].drop(columns="motivo")
    rechazado = df.loc[~valido]

    leidas = len(df)
    resumen = {
        "filas_leidas": leidas,
        "rechazadas_duplicado": int((df["motivo"] == "duplicado").sum()),
        "rechazadas_dato_faltante": int((df["motivo"] == "dato_faltante").sum()),
        "rechazadas_fuera_de_rango": int((df["motivo"] == "fuera_de_rango").sum()),
        "filas_validas": int(valido.sum()),
        "pct_datos_validos": round(100 * valido.sum() / leidas, 2) if leidas else 0.0,
    }
    return limpio, rechazado, resumen


def imprimir_reporte(resumen: dict) -> None:
    print("=== Reporte de calidad (Bronze -> Silver) ===")
    print(f"Filas leídas:                    {resumen['filas_leidas']}")
    print(f"Rechazadas por duplicado:        {resumen['rechazadas_duplicado']}")
    print(f"Rechazadas por dato faltante:    {resumen['rechazadas_dato_faltante']}")
    print(f"Rechazadas por fuera de rango:   {resumen['rechazadas_fuera_de_rango']}")
    print(f"Filas válidas:                   {resumen['filas_validas']}")
    print(f"Porcentaje de datos válidos:     {resumen['pct_datos_validos']} %")


def main() -> None:
    bronze = pd.read_csv(BRONZE)
    limpio, rechazado, resumen = limpiar(bronze)

    SILVER.parent.mkdir(parents=True, exist_ok=True)
    limpio.to_csv(SILVER, index=False)
    rechazado.to_csv(RECHAZADOS, index=False)

    imprimir_reporte(resumen)


if __name__ == "__main__":
    main()