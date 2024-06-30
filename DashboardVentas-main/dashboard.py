import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Flavio Cesar",
    page_icon="🐈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Función para cargar una animación Lottie desde una URL
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# URL de animación Lottie
lottie_url = "https://lottie.host/109cf722-8f3f-4791-a294-6d6d9e5060a3/JPxyoYkgSa.json"
lottie_json = load_lottieurl(lottie_url)

# Cargar datos
file_path = '/workspaces/Dashboard1/DashboardVentas-main/ventas.xlsx'
data = pd.read_excel(file_path)

# Transformar datos
data['Date'] = pd.to_datetime(data['Date'])
data['YearMonth'] = data['Date'].dt.to_period('M').astype(str)
data['Quarter'] = data['Date'].dt.to_period('Q')

# Eliminar valores nulos en las columnas usadas para los filtros
data.dropna(subset=['Date', 'Pais', 'IdCliente', 'Descripcion'], inplace=True)

# Título del Dashboard
st.title('🔱 Dashboard de Ventas 🔱')
st.markdown('### Resumen de ventas y rendimiento 📊')

# Mostrar la animación Lottie si se cargó correctamente
if lottie_json:
    st_lottie(lottie_json, speed=1, width=1200, height=200, key="dashboard")

# Filtros en la barra lateral con expanders
with st.sidebar:
    st.title('🕒 Filtros')
    with st.expander("📅 Filtro por Fechas"):
        start_date = st.date_input('Fecha de inicio', data['Date'].min())
        end_date = st.date_input('Fecha de fin', data['Date'].max())
    with st.expander("🌍 Filtro por País"):
        country_filter = st.selectbox('Selecciona País', ['Todos'] + list(data['Pais'].unique()))
    with st.expander("👥 Filtro por Cliente"):
        customer_filter = st.selectbox('Selecciona Cliente', ['Todos'] + list(data['IdCliente'].unique()))
    with st.expander("🛍️ Filtro por Producto"):
        product_filter = st.selectbox('Selecciona Producto', ['Todos'] + list(data['Descripcion'].unique()))

# Aplicar filtros
filtered_data = data[
    (data['Date'] >= pd.to_datetime(start_date)) &
    (data['Date'] <= pd.to_datetime(end_date))
]

if country_filter != 'Todos':
    filtered_data = filtered_data[filtered_data['Pais'] == country_filter]
if customer_filter != 'Todos':
    filtered_data = filtered_data[filtered_data['IdCliente'] == customer_filter]
if product_filter != 'Todos':
    filtered_data = filtered_data[filtered_data['Descripcion'] == product_filter]

# KPIs principales
total_sales = filtered_data['Total'].sum()
total_quantity = filtered_data['Cantidad'].sum()
num_customers = filtered_data['IdCliente'].nunique()
quarterly_sales = filtered_data.groupby('Quarter')['Total'].sum()

# Primera fila de KPIs
st.markdown("## 🔑 KPIs Principales")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric('Ventas Totales', f'${total_sales:,.2f}', delta="Mejora respecto al mes anterior", delta_color="inverse")

with col2:
    st.metric('Cantidad de Ventas', f'{total_quantity:,.0f}')

with col3:
    st.metric('Número de Clientes', f'{num_customers}')

with col4:
    st.metric('Ventas Trimestrales', f'${quarterly_sales.sum():,.2f}')

# Segunda fila de gráficos
st.markdown("## 📈 Gráficos de Ventas")
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader('📅 Ventas Totales por Mes')
    monthly_sales = filtered_data.groupby('YearMonth')['Total'].sum().reset_index()
    fig = px.bar(monthly_sales, x='YearMonth', y='Total', title="Ventas Totales por Mes",
                 labels={'YearMonth':'Mes', 'Total':'Ventas Totales'}, color='Total', color_continuous_scale='Blues')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader('🌍 Ventas por País')
    country_sales = filtered_data.groupby('Pais')['Total'].sum().reset_index()
    fig = px.pie(country_sales, values='Total', names='Pais', title="Ventas por País", hole=.3,
                 color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig, use_container_width=True)

# Tercera fila de gráficos
col3, col4 = st.columns([2, 1])

with col3:
    st.subheader('🛍️ Ventas por Producto')
    product_sales = filtered_data.groupby('Descripcion')['Cantidad'].sum().reset_index()
    fig = px.bar(product_sales, x='Descripcion', y='Cantidad', title="Ventas por Producto",
                 labels={'Descripcion':'Producto', 'Cantidad':'Cantidad Vendida'}, color='Cantidad', color_continuous_scale='Viridis')
    fig.update_layout(xaxis={'categoryorder':'total descending'})
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.subheader('📊 Ventas Trimestrales')
    fig = go.Figure(data=[go.Scatter(x=quarterly_sales.index.to_timestamp(), y=quarterly_sales.values, mode='lines+markers', line=dict(color='firebrick'))])
    fig.update_layout(title='Ventas Trimestrales',
                      xaxis_title='Trimestre',
                      yaxis_title='Ventas Totales',
                      template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

# Fila adicional de gráficos
st.markdown("## 🔍 Análisis Detallado")
col5, col6 = st.columns(2)

with col5:
    st.subheader('📈 Tendencia de Ventas')
    trend_sales = filtered_data.resample('M', on='Date')['Total'].sum().reset_index()
    fig = px.line(trend_sales, x='Date', y='Total', title="Tendencia de Ventas Mensuales",
                  labels={'Date':'Fecha', 'Total':'Ventas Totales'}, markers=True)
    fig.update_traces(line=dict(color='magenta', width=4), marker=dict(size=10))
    st.plotly_chart(fig, use_container_width=True)

with col6:
    st.subheader('🧮 Distribución de Ventas')
    fig = px.histogram(filtered_data, x='Total', nbins=30, title="Distribución de Ventas",
                       labels={'Total':'Ventas'}, color='Total')
    fig.update_layout(bargap=0.2)
    st.plotly_chart(fig, use_container_width=True)

# Análisis de ventas por cliente
st.markdown("## 👥 Análisis por Cliente")
col7, col8 = st.columns([1, 1])

with col7:
    st.subheader('Top 10 Clientes por Ventas')
    top_clients = filtered_data.groupby('IdCliente')['Total'].sum().nlargest(10).reset_index()
    fig = px.bar(top_clients, x='IdCliente', y='Total', title="Top 10 Clientes por Ventas",
                 labels={'IdCliente':'Cliente', 'Total':'Ventas Totales'}, color='Total', color_continuous_scale='Turbo')
    st.plotly_chart(fig, use_container_width=True)

with col8:
    st.subheader('Ventas por Cliente')
    client_sales = filtered_data.groupby('IdCliente')['Total'].sum().reset_index()
    fig = px.pie(client_sales, values='Total', names='IdCliente', title="Distribución de Ventas por Cliente", hole=.3,
                 color_discrete_sequence=px.colors.sequential.Teal)
    st.plotly_chart(fig, use_container_width=True)


# Mostrar la animación Lottie si se cargó correctamente al final
if lottie_json:
    st_lottie(lottie_json, speed=1, width=1200, height=200, key="dashboard_end")

# Footer con Copyright
st.markdown("""
<hr style="border:2px solid gray"> </hr>
<center>
<p style="font-size:12px; color:gray;">&copy; 2024 Flavio Cesar Flores - UPDS</p>
</center>
""", unsafe_allow_html=True)
