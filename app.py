import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página para usar todo el ancho de la pantalla
st.set_page_config(layout="wide", page_title="Sales Analytical Insights")

# --- 1. ESTILOS VISUALES (Barra lateral azul oscuro corporativo) ---
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background-color: #0b1d3a !important;
        }
        [data-testid="stSidebar"] * {
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- 2. CARGA Y PROCESAMIENTO DE DATOS ---
@st.cache_data
def cargar_datos():
    df = pd.read_excel("VentasRetail_ClaseMCP.xlsx")
    df.columns = df.columns.str.strip()
    
    # Convertir la columna Fecha al formato correcto y extraer el Año
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Año'] = df['Fecha'].dt.year
    
    # Crear las métricas financieras reales (usando DescuentoPct sin tilde)
    df['Ingresos_Totales'] = df['Cantidad'] * df['PrecioUnitario'] * (1 - df['DescuentoPct'])
    df['Costo_Total'] = df['Cantidad'] * df['CostoUnitario']
    df['Ganancia_Total'] = df['Ingresos_Totales'] - df['Costo_Total']
    
    return df

try:
    df = cargar_datos()

    # --- 3. BARRA LATERAL DE FILTROS INTELIGENTES ---
    with st.sidebar:
        st.title("Alison Corp LLC")
        st.subheader("Super Store")
        st.write("Sales Analytical Insights")
        st.markdown("---")
        
        # Filtros limpios usando tus columnas de Excel exactas (sin tildes)
        filtro_ano = st.selectbox("Selecciona el Año", sorted(df['Año'].unique(), reverse=True))
        
        opciones_cat = sorted(df['Categoria'].dropna().unique())
        filtro_categoria = st.multiselect("Categoría de Producto", options=opciones_cat, default=opciones_cat)
        
        opciones_sucursal = sorted(df['IdSucursal'].unique())
        filtro_sucursal = st.multiselect("ID Sucursal (Tienda)", options=opciones_sucursal, default=opciones_sucursal)

    # Aplicación de filtros al set de datos
    df_filtrado = df[
        (df['Año'] == filtro_ano) & 
        (df['Categoria'].isin(filtro_categoria)) & 
        (df['IdSucursal'].isin(filtro_sucursal))
    ]

    # --- 4. PANAL PRINCIPAL (EXECUTIVE OVERVIEW) ---
    st.title("Resumen Ejecutivo")
    st.caption(f"Análisis interactivo de rendimiento para el año comercial {filtro_ano}.")
    st.markdown("<br>", unsafe_allow_html=True)

    # Fila 1: Tarjetas de KPIs Financieros Reales
    col1, col2, col3 = st.columns(3)
    with col1:
        total_ventas = df_filtrado['Ingresos_Totales'].sum()
        st.metric(label="Ingresos Totales (Ventas)", value=f"${total_ventas:,.2f}")
    with col2:
        total_ganancia = df_filtrado['Ganancia_Total'].sum()
        st.metric(label="Ganancia Neta Total", value=f"${total_ganancia:,.2f}")
    with col3:
        total_unidades = df_filtrado['Cantidad'].sum()
        st.metric(label="Unidades Totales Vendidas", value=f"{int(total_unidades):,}")

    st.markdown("---")

    # Fila 2: Gráficos Estadísticos Dinámicos
    col_izq, col_der = st.columns(2)

    with col_izq:
        st.subheader("Ventas por Producto (Top Líderes)")
        df_prod = df_filtrado.groupby('Producto')['Ingresos_Totales'].sum().reset_index()
        df_prod = df_prod.sort_values(by='Ingresos_Totales', ascending=True).tail(10)
        
        fig_prod = px.bar(df_prod, x='Ingresos_Totales', y='Producto', orientation='h',
                           color='Ingresos_Totales', color_continuous_scale='Blues',
                           labels={'Ingresos_Totales': 'Ventas ($)', 'Producto': 'Producto'})
        fig_prod.update_layout(showlegend=False, height=350, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_prod, use_container_width=True)

    with col_der:
        st.subheader("Distribución de Ventas por Categoría")
        df_cat_graf = df_filtrado.groupby('Categoria')['Ingresos_Totales'].sum().reset_index()
        
        fig_cat = px.pie(df_cat_graf, values='Ingresos_Totales', names='Categoria', hole=0.5,
                         color_discrete_sequence=px.colors.sequential.Blues_r)
        fig_cat.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_cat, use_container_width=True)

    st.markdown("---")
    st.write("### Vista previa de registros detallados:")
    st.dataframe(df_filtrado[['IdVenta', 'Fecha', 'Producto', 'Categoria', 'Cantidad', 'Ingresos_Totales']], use_container_width=True)

except Exception as e:
    st.error(f"Ocurrió un inconveniente al procesar las columnas: {e}")
