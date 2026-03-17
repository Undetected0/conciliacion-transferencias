from io import BytesIO
import pandas as pd


def exportar_excel(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Resultado filtrado", index=False)
    buffer.seek(0)
    return buffer
