from utils import encontrar_columna, normalizar_clave_serie


def agregar_estado(df_revision, df_conglomerado):
    df_revision = df_revision.copy()
    df_conglomerado = df_conglomerado.copy()

    col_revision = encontrar_columna(df_revision, "Codigo Transferencia CCE")
    col_match = encontrar_columna(df_conglomerado, "Identificador de la Transaccion CCE Online")
    col_estado = encontrar_columna(df_conglomerado, "Estado")

    df_revision["_clave"] = normalizar_clave_serie(df_revision[col_revision])
    df_conglomerado["_clave"] = normalizar_clave_serie(df_conglomerado[col_match])

    mapa = (
        df_conglomerado[["_clave", col_estado]]
        .dropna(subset=["_clave"])
        .drop_duplicates("_clave")
        .set_index("_clave")[col_estado]
    )

    df_revision["ESTADO CCE"] = df_revision["_clave"].map(mapa).fillna("NO ENCONTRADO")

    debug_cruce = {
        "total_revision": int(len(df_revision)),
        "coincidencias_cruce": int((df_revision["ESTADO CCE"] != "NO ENCONTRADO").sum()),
        "sin_coincidencia": int((df_revision["ESTADO CCE"] == "NO ENCONTRADO").sum()),
        "col_revision_usada": col_revision,
        "col_conglomerado_usada": col_match,
        "col_estado_usada": col_estado,
        "ejemplos_revision": df_revision["_clave"].head(10).tolist(),
        "ejemplos_conglomerado": df_conglomerado["_clave"].head(10).tolist(),
    }

    df_revision.drop(columns="_clave", inplace=True, errors="ignore")
    return df_revision, debug_cruce


def aplicar_filtros(df):
    df = df.copy()

    col_banco = encontrar_columna(df, "Codigo Banco")
    col_tipo = encontrar_columna(df, "Tipo de transferencia")
    col_estado = encontrar_columna(df, "ESTADO CCE")

    f1 = df[col_banco].isna() | (df[col_banco].astype(str).str.strip() == "")
    f2 = df[col_tipo].fillna("").astype(str).str.strip() == "Transfer. Ordinaria"
    f3 = df[col_estado].fillna("").astype(str).str.strip() == "Aceptado"

    filtrado = df[f1 & f2 & f3].copy()

    debug_filtros = {
        "filas_antes_filtro": int(len(df)),
        "codigo_banco_vacio": int(f1.sum()),
        "tipo_transferencia_ordinaria": int(f2.sum()),
        "estado_cce_aceptado": int(f3.sum()),
        "resultado_final": int(len(filtrado)),
        "valores_tipo_transferencia": df[col_tipo].dropna().astype(str).str.strip().value_counts().head(10).to_dict(),
        "valores_estado_cce": df[col_estado].dropna().astype(str).str.strip().value_counts().head(10).to_dict(),
        "col_banco_usada": col_banco,
        "col_tipo_usada": col_tipo,
        "col_estado_usada": col_estado,
    }

    return filtrado, debug_filtros