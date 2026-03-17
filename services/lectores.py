from io import BytesIO

import openpyxl
import pandas as pd

from config import HOJAS_OBJETIVO, HEADER_ROW_CONGLOMERADO, HEADER_ROW_REVISION
from utils import normalizar_columnas, encontrar_columna


def _abrir_excel(file):
    file_bytes = file.getvalue()
    try:
        return pd.ExcelFile(BytesIO(file_bytes), engine="openpyxl")
    except Exception as e:
        if "visible" not in str(e).lower():
            raise
        wb = openpyxl.load_workbook(BytesIO(file_bytes), data_only=True, keep_links=False)
        for sheet in wb.worksheets:
            sheet.sheet_state = "visible"
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return pd.ExcelFile(buffer, engine="openpyxl")


def leer_archivo_conglomerado(file):
    dfs = []
    logs = []

    xls = _abrir_excel(file)
    logs.append(f"Procesando conglomerado: {file.name}")

    for hoja in HOJAS_OBJETIVO:
        if hoja in xls.sheet_names:
            df = pd.read_excel(
                xls,
                sheet_name=hoja,
                header=HEADER_ROW_CONGLOMERADO,
                dtype=str,
                engine="openpyxl"
            )
            df = df.dropna(how="all")
            df = normalizar_columnas(df)

            col_match = encontrar_columna(df, "Identificador de la Transaccion CCE Online")
            col_estado = encontrar_columna(df, "Estado")
            df = df[[col_match, col_estado]].copy()

            dfs.append(df)
            logs.append(f"{file.name} | {hoja}: {len(df)} filas")
        else:
            logs.append(f"{file.name} | {hoja}: hoja no encontrada")

    return dfs, logs


def consolidar_conglomerado(files):
    all_dfs = []
    logs = []

    for f in files:
        dfs, logs_arch = leer_archivo_conglomerado(f)
        all_dfs.extend(dfs)
        logs.extend(logs_arch)

    if not all_dfs:
        return None, logs

    df = pd.concat(all_dfs, ignore_index=True)
    df = df.dropna(how="all")
    return df, logs


def leer_revision(file):
    xls = _abrir_excel(file)
    df = pd.read_excel(
        xls,
        sheet_name=xls.sheet_names[0],
        header=HEADER_ROW_REVISION,
        dtype=str,
        engine="openpyxl"
    )
    df = df.dropna(how="all")
    df = normalizar_columnas(df)
    return df


def consolidar_revision(files):
    dfs = []
    logs = []

    for f in files:
        df = leer_revision(f)
        df["archivo_revision_origen"] = f.name
        dfs.append(df)
        logs.append(f"{f.name}: {len(df)} filas")

    if not dfs:
        return None, logs

    df = pd.concat(dfs, ignore_index=True)
    df = df.dropna(how="all")
    return df, logs