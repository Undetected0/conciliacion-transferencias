import re
import unicodedata


def normalizar_columnas(df):
    df.columns = [str(c).replace("\n", " ").replace("\r", " ").strip() for c in df.columns]
    return df


def texto_normalizado(texto):
    texto = str(texto).strip().lower()
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("utf-8")
    texto = re.sub(r"\s+", " ", texto)
    return texto


def encontrar_columna(df, nombre):
    objetivo = texto_normalizado(nombre)
    for col in df.columns:
        if texto_normalizado(col) == objetivo:
            return col
    raise KeyError(f"No encontré la columna '{nombre}'. Columnas detectadas: {list(df.columns)}")


def normalizar_clave_serie(serie):
    return (
        serie.fillna("")
        .astype(str)
        .str.strip()
        .str.replace("'", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace(r"\.0$", "", regex=True)
    )


def formatear_segundos(segundos):
    segundos = max(0, int(segundos))
    minutos = segundos // 60
    resto = segundos % 60

    if minutos > 0:
        return f"{minutos} min {resto} s"
    return f"{resto} s"