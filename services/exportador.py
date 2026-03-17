from io import BytesIO
import pandas as pd

MAX_ROWS = 1_048_576 - 1  # máximo de Excel menos la fila de encabezado


def exportar_excel(df, sheet_name="Resultado filtrado"):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        if len(df) <= MAX_ROWS:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        else:
            for i, start in enumerate(range(0, len(df), MAX_ROWS)):
                df.iloc[start:start + MAX_ROWS].to_excel(
                    writer, sheet_name=f"{sheet_name[:28]}_{i+1}", index=False
                )
    buffer.seek(0)
    return buffer
