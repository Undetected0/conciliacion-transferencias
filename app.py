import time
import streamlit as st

from services.lectores import consolidar_conglomerado, consolidar_revision
from services.conciliacion import agregar_estado, aplicar_filtros
from services.exportador import exportar_excel
from utils import formatear_segundos

st.set_page_config(
    page_title="Conciliación de transferencias",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2rem;
        max-width: 1180px;
    }
    h1 {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        margin-bottom: 0.3rem !important;
    }
    .stButton button, .stDownloadButton button {
        border-radius: 12px !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("Procesar documentos para conciliación de transferencias emitidas (RECIBIDAS)")
st.caption("Carga archivos del conglomerado y archivos de revisión para generar el resultado filtrado.")

if "detener_proceso" not in st.session_state:
    st.session_state.detener_proceso = False

if "procesando" not in st.session_state:
    st.session_state.procesando = False


def verificar_cancelacion():
    if st.session_state.get("detener_proceso", False):
        st.session_state.procesando = False
        st.warning("Procesamiento detenido por el usuario.")
        st.stop()


def update_progress(bar, msg_box, eta_box, step, total, mensaje, inicio):
    progreso = min(step / total, 1.0)
    bar.progress(progreso)

    transcurrido = time.time() - inicio
    if step > 0:
        tiempo_por_paso = transcurrido / step
        restantes = max(total - step, 0)
        estimado_restante = tiempo_por_paso * restantes
    else:
        estimado_restante = 0

    msg_box.info(f"⏳ {mensaje}")
    eta_box.caption(f"Tiempo estimado restante: {formatear_segundos(estimado_restante)}")


st.subheader("1) Subir archivos del conglomerado")
files_conglomerado = st.file_uploader(
    "Selecciona archivos del conglomerado",
    accept_multiple_files=True,
    type=["xlsx", "xls"]
)

if files_conglomerado:
    st.success(f"Archivos cargados: {len(files_conglomerado)}")
    with st.expander("Ver archivos cargados del conglomerado"):
        for f in files_conglomerado:
            st.write(f.name)

st.subheader("2) Subir archivo(s) de transacciones a revisar")
files_revision = st.file_uploader(
    "Selecciona archivo(s) de revisión",
    accept_multiple_files=True,
    type=["xlsx", "xls"]
)

if files_revision:
    st.success(f"Archivos de revisión cargados: {len(files_revision)}")
    with st.expander("Ver archivos cargados de revisión"):
        for f in files_revision:
            st.write(f.name)

mostrar_debug = st.toggle("Mostrar panel de debug", value=False)

if not st.session_state.procesando:
    if st.button("▶ Procesar conciliación", type="primary", use_container_width=True):
        st.session_state.procesando = True
        st.session_state.detener_proceso = False
        st.rerun()
else:
    if st.button("⛔ Detener procesamiento", use_container_width=True):
        st.session_state.detener_proceso = True
        st.session_state.procesando = False
        st.warning("Se solicitó detener el procesamiento.")
        st.rerun()


if st.session_state.procesando:
    if not files_conglomerado:
        st.session_state.procesando = False
        st.warning("Sube archivos del conglomerado.")
        st.stop()

    if not files_revision:
        st.session_state.procesando = False
        st.warning("Sube archivo(s) de revisión.")
        st.stop()

    try:
        inicio = time.time()

        progress = st.progress(0)
        status = st.empty()
        eta_box = st.empty()

        total_steps = len(files_conglomerado) + len(files_revision) + 5
        step = 0

        verificar_cancelacion()
        step += 1
        update_progress(progress, status, eta_box, step, total_steps, "Leyendo archivos del conglomerado", inicio)
        df_cong, logs_cong = consolidar_conglomerado(files_conglomerado)

        if df_cong is None or df_cong.empty:
            st.session_state.procesando = False
            progress.empty()
            status.empty()
            eta_box.empty()
            st.error("No se pudo generar el conglomerado.")
            st.stop()

        verificar_cancelacion()
        step += 1
        update_progress(progress, status, eta_box, step, total_steps, "Leyendo archivos de revisión", inicio)
        df_rev, logs_rev = consolidar_revision(files_revision)

        if df_rev is None or df_rev.empty:
            st.session_state.procesando = False
            progress.empty()
            status.empty()
            eta_box.empty()
            st.error("No se pudo generar la base de revisión.")
            st.stop()

        verificar_cancelacion()
        step += 1
        update_progress(progress, status, eta_box, step, total_steps, "Cruzando información", inicio)
        df_completo, debug_cruce = agregar_estado(df_rev, df_cong)

        verificar_cancelacion()
        step += 1
        update_progress(progress, status, eta_box, step, total_steps, "Aplicando filtros", inicio)
        df_filtrado, debug_filtros = aplicar_filtros(df_completo)

        verificar_cancelacion()
        step += 1
        update_progress(progress, status, eta_box, step, total_steps, "Generando archivo final", inicio)
        excel = exportar_excel(df_filtrado)

        progress.empty()
        eta_box.empty()
        status.success("✅ Proceso completado correctamente.")
        st.session_state.procesando = False

        c1, c2 = st.columns(2)
        with c1:
            st.metric("Filas totales revisión", len(df_completo))
        with c2:
            st.metric("Filas resultado filtrado", len(df_filtrado))

        st.markdown("### Vista previa del resultado filtrado")
        st.dataframe(df_filtrado.head(50), use_container_width=True)

        st.download_button(
            "Descargar resultado filtrado",
            excel,
            "resultado_filtrado_conciliacion.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

        if mostrar_debug:
            with st.expander("Debug del cruce", expanded=False):
                st.write(debug_cruce)

            with st.expander("Debug de filtros", expanded=False):
                st.write(debug_filtros)

            with st.expander("Logs técnicos", expanded=False):
                for log in logs_cong + logs_rev:
                    st.write(log)

    except Exception as e:
        st.session_state.procesando = False
        st.error(f"Ocurrió un error: {e}")