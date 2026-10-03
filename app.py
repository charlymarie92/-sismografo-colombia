import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(page_title="Sismógrafo Macroeconómico - SVAR(11)", layout="wide", initial_sidebar_state="expanded")

st.title("Sismógrafo Macroeconómico - Modelo SVAR(11)")
st.markdown("Plataforma interactiva para evaluar la transmisión de política monetaria en Colombia y visualizar la 'Sábana Macroeconómica' en 3D con 4 variables.")

# Panel Lateral (Sidebar) para ingreso de datos o carga de CSV
st.sidebar.header("Parámetros de Entrada")

# Componente para cargar archivos CSV
uploaded_file = st.sidebar.file_uploader("Cargar archivo histórico CSV (Opcional)", type=["csv"])

tasa_default, ise_default, ipc_default, trm_default = 12.25, 132.49, 161.88, 4100.0

if uploaded_file is not None:
    try:
        df_user = pd.read_csv(uploaded_file)
        st.sidebar.success("¡CSV cargado correctamente!")
        if 'tasa' in df_user.columns: tasa_default = float(df_user['tasa'].iloc[-1])
        if 'ise' in df_user.columns: ise_default = float(df_user['ise'].iloc[-1])
        if 'ipc' in df_user.columns: ipc_default = float(df_user['ipc'].iloc[-1])
        if 'trm' in df_user.columns: trm_default = float(df_user['trm'].iloc[-1])
    except Exception as e:
        st.sidebar.error(f"Error al leer el CSV: {e}")

st.sidebar.markdown("---")
st.sidebar.markdown("Ajusta las 4 variables del modelo:")
tasa_input = st.sidebar.slider("Tasa BanRep (%)", min_value=2.0, max_value=16.0, value=float(tasa_default), step=0.25)
ise_input = st.sidebar.number_input("ISE Observado (Producción)", min_value=100.0, max_value=160.0, value=float(ise_default), step=0.1)
ipc_input = st.sidebar.number_input("IPC Observado (Precios)", min_value=100.0, max_value=200.0, value=float(ipc_default), step=0.1)
trm_input = st.sidebar.number_input("TRM Observada ($)", min_value=3000.0, max_value=6000.0, value=float(trm_default), step=10.0)

# Botón de ejecución
if st.sidebar.button("Ejecutar Sismógrafo 3D", type="primary"):
    st.subheader("1. Diagnóstico Estructural del Estado Actual (4 Variables)")
    
    trm_factor = trm_input / 4100.0
    
    ipc_eq = (112.4512 
              - 2.1840 * tasa_input 
              + 0.3125 * ise_input 
              + 1.2000 * (trm_factor - 1.0) * 10
              + 0.2415 * (tasa_input**2) 
              + 0.0018 * (ise_input**2) 
              - 0.0084 * tasa_input * ise_input)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tasa BanRep", f"{tasa_input:.2f}%")
    col2.metric("ISE", f"{ise_input:.2f}")
    col3.metric("IPC", f"{ipc_input:.2f}")
    col4.metric("TRM", f"${trm_input:,.0f}")

    st.markdown(f"**IPC Estimado por el Modelo (con choque TRM):** `{ipc_eq:.2f}`")

    # Visualización 3D mejorada para móviles
    st.subheader("2. Sábana Macroeconómica 3D")
    st.markdown("Ejes: **X** = Tasa BanRep | **Y** = ISE | **Z** = IPC | **Color** = Dinámica cruzada ajustada por TRM.")

    tasa_grid = np.linspace(2, 16, 30)
    ise_grid = np.linspace(100, 160, 30)
    TASA, ISE = np.meshgrid(tasa_grid, ise_grid)
    
    IPC_SURF = (112.4512 
                - 2.1840 * TASA 
                + 0.3125 * ISE 
                + 1.2000 * (trm_factor - 1.0) * 10
                + 0.2415 * (TASA**2) 
                + 0.0018 * (ISE**2) 
                - 0.0084 * TASA * ISE)

    # Matriz de color variada en la cuadrícula y escalada por el nivel de la TRM
    TRM_COLOR = (TASA * 0.5 + ISE * 0.5) * (trm_input / 4100.0)

    fig = go.Figure(data=[
        go.Surface(
            z=IPC_SURF, 
            x=TASA, 
            y=ISE, 
            surfacecolor=TRM_COLOR,
            colorscale='Viridis',
            colorbar=dict(title="Intensidad TRM")
        )
    ])

    # Punto del estado actual
    fig.add_trace(go.Scatter3d(
        x=[tasa_input],
        y=[ise_input],
        z=[ipc_eq],
        mode='markers+text',
        marker=dict(size=10, color='red', symbol='diamond'),
        text=["Estado Actual"],
        textposition="top center",
        name="Estado Actual"
    ))

    # Optimización de diseño para evitar compresión en pantallas de celular
    fig.update_layout(
        autosize=True,
        height=580,
        margin=dict(l=5, r=5, b=5, t=25),
        scene=dict(
            xaxis_title='Tasa BanRep (%)',
            yaxis_title='ISE (Producción)',
            zaxis_title='IPC (Precios)',
            camera=dict(
                eye=dict(x=1.6, y=1.6, z=1.3)
            )
        )
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("👈 Ingresa los parámetros o carga un archivo CSV en el panel lateral y presiona **'Ejecutar Sismógrafo 3D'**.")
