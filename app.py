import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(page_title="Sismógrafo Macroeconómico", layout="wide", initial_sidebar_state="expanded")

st.title("Sismógrafo Macroeconómico - Modelo SVAR(11)")
st.markdown("Plataforma interactiva para evaluar la transmisión de política monetaria en Colombia y visualizar la 'Sábana Macroeconómica' en 3D.")

# Panel Lateral (Sidebar) para ingreso de datos
st.sidebar.header("Parámetros de Entrada")
st.sidebar.markdown("Ingresa los datos para proyectar:")

tasa_input = st.sidebar.slider("Tasa BanRep (%)", min_value=2.0, max_value=16.0, value=12.25, step=0.25)
ise_input = st.sidebar.number_input("ISE Observado (Producción)", min_value=100.0, max_value=160.0, value=132.49, step=0.1)
ipc_input = st.sidebar.number_input("IPC Observado (Precios)", min_value=100.0, max_value=200.0, value=161.88, step=0.1)

# Botón de ejecución
if st.sidebar.button("Ejecutar Sismógrafo 3D", type="primary"):
    
    st.subheader("1. Diagnóstico Estructural del Estado Actual")
    
    # Ecuación de la variedad cuadrática (La Sábana) deducida en la investigación
    ipc_eq = (112.4512 
              - 2.1840 * tasa_input 
              + 0.3125 * ise_input 
              + 0.2415 * (tasa_input**2) 
              + 0.0018 * (ise_input**2) 
              - 0.0084 * (tasa_input * ise_input))
    
    # Cálculo de la Tensión Estructural (Brecha Vertical)
    brecha = ipc_input - ipc_eq
    
    # Tarjetas de Métricas
    col1, col2, col3 = st.columns(3)
    col1.metric("Tasa de Intervención", f"{tasa_input}%")
    col2.metric("IPC de Equilibrio (Sábana)", f"{ipc_eq:.2f}")
    col3.metric("Tensión Estructural (Drop-line)", f"{brecha:.2f} pts")
    
    if brecha > 5:
        st.error("⚠️ La economía se encuentra bajo Tensión Estructural severa por Canal de Costos.")
    elif brecha > 0:
        st.warning("⚠️ Ligera tensión de costos. La inflación supera el nivel de reposo.")
    else:
        st.success("✅ La economía opera de forma balanceada sobre la Sábana Macroeconómica.")

    st.divider()

    st.subheader("2. Topología Tridimensional: La Sábana Macroeconómica")
    
    # Crear la malla de datos para renderizar la superficie
    tasa_range = np.linspace(2, 16, 50)
    ise_range = np.linspace(120, 150, 50)
    TASA, ISE = np.meshgrid(tasa_range, ise_range)
    
    # Calcular el eje Z (IPC) para cada punto de la malla
    IPC_SURF = (112.4512 
              - 2.1840 * TASA 
              + 0.3125 * ISE 
              + 0.2415 * (TASA**2) 
              + 0.0018 * (ISE**2) 
              - 0.0084 * (TASA * ISE))
    
    fig = go.Figure()
    
    # 1. Agregar la Sábana de Equilibrio
    fig.add_trace(go.Surface(
        z=IPC_SURF, x=TASA, y=ISE,
        colorscale='Viridis',
        opacity=0.75,
        name='Sábana de Equilibrio',
        showscale=False
    ))
    
    # 2. Agregar el punto real actual ingresado por el usuario
    fig.add_trace(go.Scatter3d(
        x=[tasa_input], y=[ise_input], z=[ipc_input],
        mode='markers+text',
        marker=dict(size=8, color='red', symbol='circle'),
        text=["Estado Actual"],
        textposition="top center",
        name="Condición Actual"
    ))
    
    # 3. Agregar la línea de tensión (Drop-line)
    fig.add_trace(go.Scatter3d(
        x=[tasa_input, tasa_input], y=[ise_input, ise_input], z=[ipc_eq, ipc_input],
        mode='lines',
        line=dict(color='red', width=6, dash='dash'),
        name="Línea de Tensión"
    ))
    
    # 4. Agregar el Punto Neutral Estructural del Modelo (5.50%)
    fig.add_trace(go.Scatter3d(
        x=[5.50], y=[141.20], z=[164.80],
        mode='markers+text',
        marker=dict(size=10, color='blue', symbol='diamond'),
        text=["Tasa Neutral (5.50%)"],
        textposition="bottom center",
        name="Equilibrio Óptimo"
    ))

    # Formatear la escena 3D
    fig.update_layout(
        scene=dict(
            xaxis_title='Tasa BanRep (%)',
            yaxis_title='ISE (Producción)',
            zaxis_title='IPC (Nivel de Precios)',
            camera=dict(eye=dict(x=1.8, y=-1.8, z=0.5))
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        height=700
    )
    
    # Mostrar el gráfico interactivo en Streamlit
    st.plotly_chart(fig, use_container_width=True)
    
else:
    st.info("👈 Ajusta los parámetros en el panel lateral y haz clic en 'Ejecutar Sismógrafo 3D' para generar el modelo.")
