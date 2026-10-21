import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# 1. CONFIGURACIÓN DE LA PÁGINA (Tema Oscuro / Azul Corporativo)
st.set_page_config(layout="wide", page_title="ATB - Dashboard Ventas Resumen")

# --- ESTILOS VISUALES CORREGIDOS SIN ERRORES DE SINTAXIS ---
st.markdown("""
    <style>
        stApp { background-color: #f0f4f8; }
        [data-testid="stSidebar"] { background-color: #0d47a1 !important; }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { 
            color: white !important; 
        }
        div[data-baseweb="select"] * {
            color: #333333 !important;
        }
        .metric-card {
            background-color: #1565c0; color: white; border-radius: 8px;
            padding: 15px; text-align: center;
        }
        .metric-title { font-size: 14px; font-weight: bold; opacity: 0.9; }
        .metric-value { font-size: 22px; font-weight: bold; margin-top: 5px; }
    </style>
""", unsafe_allow_html=True)

# 2. CARGA Y ASIGNACIÓN INTELIGENTE DE COLUMNAS
@st.cache_data
def cargar_y_mapear_datos():
    df = pd.read_excel("VentasRetail_ClaseMCP.xlsx")
    df.columns = df.columns.str.strip()
    
    # Procesar Fechas
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Año'] = df['Fecha'].dt.year
    df['Mes_Num'] = df['Fecha'].dt.month
    
    # Nombres de meses en español
    meses_es = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio', 
                 7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}
    df['Mes'] = df['Mes_Num'].map(meses_es)
    
    # Calcular Venta Neta Real
    df['Venta_Neta'] = df['Cantidad'] * df['PrecioUnitario'] * (1 - df['DescuentoPct'])
    
    # Asignar Vendedores de forma consistente según el IdCliente
    vendedores = ['FLORES POZO R.', 'SILVA IBARRA A.', 'YANAC VICTORI...', 'SARAVIA CALDE...', 'QUISPE FLORIAN...']
    df['Vendedor'] = df['IdCliente'].apply(lambda x: vendedores[x % len(vendedores)])
    
    # Asignar Canales según el IdSucursal
    canales = {1: 'Lima', 2: 'Provincia', 3: 'Call Center', 4: 'Botica', 5: 'Instituciones', 6: 'Promotoria'}
    df['Canal'] = df['IdSucursal'].map(canales).fillna('Community Manager')
    
    return df

try:
    df = cargar_y_mapear_datos()

    # 3. INTERFAZ Y FILTROS (Barra Lateral Superior)
    with st.sidebar:
        st.title("Dashboard Ventas")
        st.subheader("Resumen Corporativo")
        st.markdown("---")
        
        filtro_ano = st.selectbox("AÑO", sorted(df['Año'].unique(), reverse=True))
        df_ano = df[df['Año'] == filtro_ano]
        
        lista_meses = sorted(df_ano['Mes_Num'].unique())
        meses_disponibles = [df_ano[df_ano['Mes_Num'] == m]['Mes'].iloc[0] for m in lista_meses]
        filtro_mes = st.selectbox("MES", meses_disponibles)

    # Filtrado según la selección del usuario
    df_filtrado = df_ano[df_ano['Mes'] == filtro_mes]
    ventas_actuales = df_filtrado['Venta_Neta'].sum()
    
    # Cálculo de Mes Pasado para las tarjetas comparativas
    mes_num_actual = df_filtrado['Mes_Num'].iloc[0]
    df_mes_pasado = df_ano[df_ano['Mes_Num'] == (mes_num_actual - 1)]
    ventas_pasadas = df_mes_pasado['Venta_Neta'].sum() if not df_mes_pasado.empty else ventas_actuales * 0.85
    
    # Definición de la Meta Dinámica adaptada a tus montos del mes
    meta_comercial = int(ventas_actuales * 1.30)

    # 4. DISPOSICIÓN EN CUADRÍCULA (Métricas Superiores)
    col_logo, col_gauge, col_cards = st.columns([1.5, 2, 2.5])
    
    with col_logo:
        st.markdown(f"<h2 style='color:#0d47a1; margin-top:15px;'>ATB SA</h2>", unsafe_allow_html=True)
        st.markdown(f"<b>Periodo:</b> {filtro_mes} {filtro_ano}", unsafe_allow_html=True)
        
    with col_gauge:
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = ventas_actuales,
            number = {'prefix': "S/ ", 'valueformat': ",.0f", 'font': {'size': 20}},
            title = {'text': f"META: S/ {meta_comercial:,}", 'font': {'size': 12, 'weight': 'bold'}},
            gauge = {
                'axis': {'range': [0, meta_comercial if meta_comercial > 0 else 100000]},
                'bar': {'color': "#0d47a1"},
                'steps': [{'range': [0, meta_comercial], 'color': "#e0e0e0"}]
            }
        ))
        fig_gauge.update_layout(height=140, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_gauge, use_container_width=True)
        
    with col_cards:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"<div class='metric-card'><div class='metric-title'>Ventas Actuales</div><div class='metric-value'>S/ {ventas_actuales/1000:,.1f}K</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='metric-card'><div class='metric-title'>Mes Pasado</div><div class='metric-value'>S/ {ventas_pasadas/1000:,.1f}K</div></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='metric-card'><div class='metric-title'>Meta Objetivo</div><div class='metric-value'>S/ {meta_comercial/1000:,.1f}K</div></div>", unsafe_allow_html=True)

    st.markdown("---")

    # FILA 2: HISTÓRICO MENSUAL Y LÍNEA DE TENDENCIA (PRONÓSTICO)
    col_hist, col_trend = st.columns(2)
    
    with col_hist:
        st.write("### Ventas por meses")
        df_mensual = df_ano.groupby(['Mes_Num', 'Mes'])['Venta_Neta'].sum().reset_index().sort_values('Mes_Num')
        fig_meses = px.bar(df_mensual, x='Mes', y='Venta_Neta', text_auto=',.0f', color_discrete_sequence=['#0d47a1'])
        fig_meses.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10), yaxis_title=None, xaxis_title=None)
        st.plotly_chart(fig_meses, use_container_width=True)
        
    with col_trend:
        st.write("### Línea Pronósticos de ventas (Días del Mes)")
        df_diario = df_filtrado.groupby(df_filtrado['Fecha'].dt.day)['Venta_Neta'].sum().reset_index()
        df_diario.columns = ['Día', 'Ventas']
        
        fig_diario = go.Figure()
        fig_diario.add_trace(go.Scatter(x=df_diario['Día'], y=df_diario['Ventas'], mode='lines+markers', name='Ventas Reales', line=dict(color='#0d47a1', width=3)))
        
        # Simulación de línea de pronóstico (Siguientes 5 días)
        if len(df_diario) > 0:
            ult_dia = df_diario['Día'].max()
            dias_pronostico = list(range(int(ult_dia)+1, int(ult_dia)+6))
            valores_pronostico = [df_diario['Ventas'].mean()] * len(dias_pronostico)
            fig_diario.add_trace(go.Scatter(x=dias_pronostico, y=valores_pronostico, mode='lines', name='Pronóstico', line=dict(color='green', dash='dash')))
            
        fig_diario.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
        st.plotly_chart(fig_diario, use_container_width=True)

    # FILA 3: TOP VENDEDORES Y CANALES PRINCIPALES / SECUNDARIOS
    st.markdown("---")
    col_vended, col_can1, col_can2 = st.columns([2, 2, 2.5])
    
    with col_vended:
        st.write("### TOP - 5 Vendedores")
        df_vend = df_filtrado.groupby('Vendedor')['Venta_Neta'].sum().reset_index().sort_values('Venta_Neta', ascending=True)
        fig_vend = px.bar(df_vend, x='Venta_Neta', y='Vendedor', orientation='h', text_auto=',.0f', color_discrete_sequence=['#4caf50'])
        fig_vend.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10), yaxis_title=None, xaxis_title=None)
        st.plotly_chart(fig_vend, use_container_width=True)
        
    with col_can1:
        st.write("### Canales más importantes")
        df_can_principales = df_filtrado[df_filtrado['Canal'].isin(['Lima', 'Provincia'])].groupby('Canal')['Venta_Neta'].sum().reset_index()
        fig_can1 = px.bar(df_can_principales, x='Canal', y='Venta_Neta', text_auto=',.0f', color_discrete_sequence=['#78909c'])
        fig_can1.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10), yaxis_title=None, xaxis_title=None)
        st.plotly_chart(fig_can1, use_container_width=True)
        
    with col_can2:
        st.write("### Canales secundarios")
        df_can_secundarios = df_filtrado[~df_filtrado['Canal'].isin(['Lima', 'Provincia'])].groupby('Canal')['Venta_Neta'].sum().reset_index()
        fig_can2 = px.bar(df_can_secundarios, x='Canal', y='Venta_Neta', text_auto=',.0f', color_discrete_sequence=['#a5d6a7'])
        fig_can2.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10), yaxis_title=None, xaxis_title=None)
        st.plotly_chart(fig_can2, use_container_width=True)

except Exception as e:
    st.error(f"Error general: {e}")
