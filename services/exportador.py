from io import BytesIO
import pandas as pd


def exportar_excel(df_filtrado):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_filtrado.to_excel(writer, sheet_name="Resultado filtrado", index=False)
    buffer.seek(0)
    return buffer