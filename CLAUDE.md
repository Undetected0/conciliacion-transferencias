# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Ejecutar la app

```bash
pip install -r requirements.txt
streamlit run app.py
```

La app corre en `http://localhost:8501`.

## Arquitectura

App Streamlit que concilia transferencias inmediatas bancarias entre dos fuentes de datos Excel:
- **Archivos conglomerado**: Datos maestros CCE (cámara de compensación) con identificadores de transacción y sus estados
- **Archivos revisión**: Transacciones a conciliar contra el conglomerado

**Responsabilidad de cada módulo:**
- `app.py` — Orquestación de UI, session state, seguimiento de progreso, subida y descarga de archivos
- `services/lectores.py` — Lectura y consolidación de archivos Excel en DataFrames
- `services/conciliacion.py` — Matching de transacciones revisión con conglomerado por código CCE, y aplicación de filtros de negocio
- `services/exportador.py` — Exportación de resultados filtrados a Excel (BytesIO)
- `utils.py` — Normalización de nombres de columna, buscador fuzzy de columnas, normalización de texto (sin tildes, case insensitive)
- `config.py` — Nombres de hojas Excel y números de fila de encabezado

**Flujo de datos:**
1. El usuario sube archivos conglomerado + revisión en Excel
2. `consolidar_conglomerado()` / `consolidar_revision()` → DataFrames únicos
3. Filtrado opcional por tipo de cuenta (Ohpay vs ahorros, por prefijo)
4. `agregar_estado()` — normaliza y hace match de "Codigo Transferencia CCE" ↔ "Identificador de la Transaccion CCE Online", agrega columna "ESTADO CCE"
5. `aplicar_filtros()` — conserva filas donde: "Codigo Banco" vacío AND tipo = "Transfer. Ordinaria" AND estado = "Aceptado"
6. `exportar_excel()` → descarga ZIP con resultados filtrados + conglomerado consolidado

## Convenciones clave

- La lógica de negocio va en `services/`; la lógica de UI va en `app.py`
- Para acceder a columnas usar `encontrar_columna()` (insensible a tildes y mayúsculas) — nunca usar strings hardcodeados directamente
- El matching de claves usa `normalizar_clave_serie()` que elimina comillas, espacios y `.0` al final
- Los criterios de filtrado están hardcodeados en `services/conciliacion.py:aplicar_filtros()` — cambios ahí afectan toda la salida de conciliación
- Las filas de encabezado Excel se configuran en `config.py` (conglomerado: fila 6, revisión: fila 1)
- Evitar refactorizaciones innecesarias; preferir cambios pequeños e incrementales
- Optimizar para archivos grandes (100k+ filas): usar operaciones vectorizadas de pandas, evitar iteración por filas
