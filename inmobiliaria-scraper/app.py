"""
Interfaz Streamlit para el Analizador de Inversiones Inmobiliarias
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import os
import sys
from datetime import datetime
import time

# Configuración de página
st.set_page_config(
    page_title="🏡 Analizador Inmobiliario",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Importar módulos del proyecto
from scraping.infocasas_scraper import InfocasasScraper
from scraping.data_processor import DataProcessor
from machine_learning.investment_model import InvestmentModel
from machine_learning.optimizer import InvestmentOptimizer
from config.settings import *

# CSS personalizado
st.markdown("""
<style>
.main-header {
    font-size: 3rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.metric-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 5px solid #1f77b4;
}
.success-box {
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    border-radius: 0.5rem;
    padding: 1rem;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">🏡 Analizador de Inversiones Inmobiliarias</h1>', unsafe_allow_html=True)
    st.markdown("**Encuentra las mejores oportunidades de inversión en Montevideo**")
    
    # Sidebar para navegación
    st.sidebar.title("🔧 Panel de Control")
    
    # Verificar si hay datos
    data_exists = check_data_exists()
    
    if not data_exists:
        st.sidebar.warning("⚠️ No hay datos disponibles")
        st.sidebar.info("Ejecuta el scraping primero")
    
    # Menú principal
    page = st.sidebar.selectbox(
        "Selecciona una opción:",
        ["🏠 Dashboard Principal", "🔍 Hacer Scraping", "📊 Análisis de Mercado", 
         "💰 Buscar Inversiones", "🤖 Modelo ML", "📈 Estadísticas"]
    )
    
    # Enrutamiento de páginas
    if page == "🏠 Dashboard Principal":
        show_dashboard()
    elif page == "🔍 Hacer Scraping":
        show_scraping_page()
    elif page == "📊 Análisis de Mercado":
        show_market_analysis()
    elif page == "💰 Buscar Inversiones":
        show_investment_finder()
    elif page == "🤖 Modelo ML":
        show_ml_page()
    elif page == "📈 Estadísticas":
        show_statistics()

def check_data_exists():
    """Verifica si existen datos en la base de datos"""
    try:
        if os.path.exists(DATABASE_PATH):
            conn = sqlite3.connect(DATABASE_PATH)
            df = pd.read_sql_query("SELECT COUNT(*) as count FROM propiedades", conn)
            conn.close()
            return df['count'].iloc[0] > 0
        return False
    except:
        return False

def load_data():
    """Carga datos desde la base de datos"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        df = pd.read_sql_query("SELECT * FROM propiedades", conn)
        conn.close()
        return df
    except:
        return None

def show_dashboard():
    """Muestra el dashboard principal"""
    st.header("📋 Dashboard Principal")
    
    if not check_data_exists():
        st.warning("⚠️ No hay datos disponibles. Ve a 'Hacer Scraping' para obtener datos.")
        return
    
    df = load_data()
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Propiedades", len(df))
    
    with col2:
        venta_count = len(df[df['tipo_operacion'] == 'venta'])
        st.metric("🏪 En Venta", venta_count)
    
    with col3:
        alquiler_count = len(df[df['tipo_operacion'] == 'alquiler'])
        st.metric("🏠 En Alquiler", alquiler_count)
    
    with col4:
        barrios_count = df['barrio'].nunique()
        st.metric("🗺️ Barrios", barrios_count)
    
    st.divider()
    
    # Gráficos principales
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Propiedades por Barrio")
        barrio_counts = df['barrio'].value_counts().head(10)
        fig = px.bar(x=barrio_counts.values, y=barrio_counts.index, orientation='h')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💰 Distribución de Precios")
        fig = px.histogram(df, x='precio', nbins=30, title="Distribución de Precios")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Mapa de calor de precios por barrio
    st.subheader("🗺️ Precio Promedio por Barrio")
    precio_por_barrio = df.groupby(['barrio', 'tipo_operacion'])['precio'].mean().reset_index()
    
    fig = px.bar(precio_por_barrio, x='barrio', y='precio', color='tipo_operacion',
                 title="Precio Promedio por Barrio y Tipo de Operación")
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

def show_scraping_page():
    """Página para ejecutar scraping"""
    st.header("🔍 Scraping de Propiedades")
    st.write("Extrae datos frescos de infocasas.com.uy")
    
    # Configuración de scraping
    col1, col2 = st.columns(2)
    
    with col1:
        max_pages = st.slider("Máximo páginas a scrapear", 1, 50, 10)
        include_venta = st.checkbox("Incluir propiedades en venta", True)
        include_alquiler = st.checkbox("Incluir propiedades en alquiler", True)
    
    with col2:
        st.info("""
        **Tiempo estimado:**
        - 1-5 páginas: 2-5 minutos
        - 6-20 páginas: 5-15 minutos
        - 21+ páginas: 15+ minutos
        """)
    
    if st.button("🚀 Iniciar Scraping", type="primary"):
        if not include_venta and not include_alquiler:
            st.error("Selecciona al menos un tipo de operación")
            return
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            scraper = InfocasasScraper()
            total_steps = (include_venta + include_alquiler) * max_pages + 1
            current_step = 0
            
            if include_venta:
                status_text.text("🏪 Scrapeando propiedades en venta...")
                scraper.scrape_properties("venta", max_pages)
                current_step += max_pages
                progress_bar.progress(current_step / total_steps)
            
            if include_alquiler:
                status_text.text("🏠 Scrapeando propiedades en alquiler...")
                scraper.scrape_properties("alquiler", max_pages)
                current_step += max_pages
                progress_bar.progress(current_step / total_steps)
            
            status_text.text("💾 Guardando datos...")
            scraper.save_to_database()
            progress_bar.progress(1.0)
            
            scraper.close()
            
            st.success(f"✅ Scraping completado! Se obtuvieron {len(scraper.data)} propiedades")
            st.balloons()
            
        except Exception as e:
            st.error(f"❌ Error durante el scraping: {str(e)}")

def show_market_analysis():
    """Análisis de mercado"""
    st.header("📊 Análisis de Mercado")
    
    if not check_data_exists():
        st.warning("⚠️ No hay datos disponibles.")
        return
    
    # Procesar datos
    if st.button("🔄 Actualizar Análisis"):
        with st.spinner("Procesando datos..."):
            processor = DataProcessor()
            processor.load_data()
            processor.clean_data()
            roi_df = processor.save_processed_data()
        st.success("✅ Análisis actualizado")
    
    # Cargar datos procesados si existen
    try:
        roi_df = pd.read_csv('data/processed/roi_por_barrio.csv')
        
        st.subheader("🏆 TOP 10 Barrios por ROI")
        
        # Gráfico de ROI
        top_roi = roi_df.head(10)
        fig = px.bar(top_roi, x='barrio', y='roi_anual_porcentaje',
                     title="ROI Anual por Barrio (%)")
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabla detallada
        st.subheader("📋 Detalles por Barrio")
        st.dataframe(roi_df.round(2), use_container_width=True)
        
    except FileNotFoundError:
        st.info("Ejecuta el procesamiento de datos primero")

def show_investment_finder():
    """Buscador de inversiones"""
    st.header("💰 Buscador de Inversiones")
    
    if not check_data_exists():
        st.warning("⚠️ No hay datos disponibles.")
        return
    
    # Configuración de búsqueda
    st.subheader("⚙️ Configuración de Búsqueda")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        budget_min = st.number_input("Presupuesto Mínimo (USD)", 50000, 1000000, 80000, 10000)
        budget_max = st.number_input("Presupuesto Máximo (USD)", budget_min, 1000000, 200000, 10000)
    
    with col2:
        risk_tolerance = st.selectbox(
            "Tolerancia al Riesgo",
            ["low", "medium", "high"],
            index=1,
            format_func=lambda x: {"low": "🛡️ Conservador", "medium": "⚖️ Balanceado", "high": "🚀 Agresivo"}[x]
        )
    
    with col3:
        location_pref = st.selectbox("Barrio Preferido (Opcional)", ["Todos"] + BARRIOS_MONTEVIDEO)
        location = None if location_pref == "Todos" else location_pref
    
    if st.button("🔍 Buscar Oportunidades", type="primary"):
        with st.spinner("Analizando oportunidades..."):
            try:
                optimizer = InvestmentOptimizer()
                if optimizer.load_data():
                    results = optimizer.get_investment_recommendation(
                        budget_min, budget_max, risk_tolerance, location
                    )
                    
                    if results:
                        st.success("✅ Análisis completado")
                        
                        # Mejor oportunidad
                        st.subheader("🥇 Mejor Oportunidad")
                        best = results['best_opportunity']
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("📍 Barrio", best['barrio'])
                        with col2:
                            st.metric("💰 Precio", f"USD {best['precio']:,.0f}")
                        with col3:
                            st.metric("📐 Tamaño", f"{best['metros_cuadrados']:.0f} m²")
                        with col4:
                            st.metric("📈 ROI Anual", f"{best['roi_anual_porcentaje']:.1f}%")
                        
                        # Top 10 oportunidades
                        st.subheader("🏆 Top 10 Oportunidades")
                        st.dataframe(results['top_opportunities'], use_container_width=True)
                        
                        # Análisis por barrio
                        st.subheader("🗺️ Análisis por Barrio")
                        st.dataframe(results['neighborhood_analysis'].head(), use_container_width=True)
                    
                else:
                    st.error("Error cargando datos")
                    
            except Exception as e:
                st.error(f"Error en el análisis: {str(e)}")

def show_ml_page():
    """Página del modelo ML"""
    st.header("🤖 Modelo de Machine Learning")
    
    if not check_data_exists():
        st.warning("⚠️ No hay datos disponibles.")
        return
    
    st.write("Entrena y evalúa el modelo predictivo de precios")
    
    if st.button("🚀 Entrenar Modelo", type="primary"):
        with st.spinner("Entrenando modelo..."):
            try:
                model = InvestmentModel()
                if model.load_processed_data():
                    score = model.train_model()
                    importance_df = model.analyze_feature_importance()
                    
                    st.success(f"✅ Modelo entrenado exitosamente (R² = {score:.4f})")
                    
                    if importance_df is not None:
                        st.subheader("📊 Importancia de Características")
                        fig = px.bar(importance_df.head(10), x='importance', y='feature', orientation='h')
                        st.plotly_chart(fig, use_container_width=True)
                        
                else:
                    st.error("Error cargando datos procesados")
                    
            except Exception as e:
                st.error(f"Error entrenando modelo: {str(e)}")

def show_statistics():
    """Estadísticas generales"""
    st.header("📈 Estadísticas Generales")
    
    if not check_data_exists():
        st.warning("⚠️ No hay datos disponibles.")
        return
    
    df = load_data()
    
    # Estadísticas básicas
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Resumen General")
        st.write(f"**Total propiedades:** {len(df):,}")
        st.write(f"**Propiedades en venta:** {len(df[df['tipo_operacion'] == 'venta']):,}")
        st.write(f"**Propiedades en alquiler:** {len(df[df['tipo_operacion'] == 'alquiler']):,}")
        st.write(f"**Barrios únicos:** {df['barrio'].nunique()}")
        st.write(f"**Rango de precios:** USD {df['precio'].min():,.0f} - {df['precio'].max():,.0f}")
    
    with col2:
        st.subheader("💰 Estadísticas de Precios")
        st.write(f"**Precio promedio:** USD {df['precio'].mean():,.0f}")
        st.write(f"**Precio mediano:** USD {df['precio'].median():,.0f}")
        st.write(f"**Precio/m² promedio:** USD {df['precio_por_m2'].mean():,.0f}")
        st.write(f"**Tamaño promedio:** {df['metros_cuadrados'].mean():.0f} m²")
    
    # Distribuciones
    st.subheader("📊 Distribuciones")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.box(df, y='precio', color='tipo_operacion', title="Distribución de Precios")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.scatter(df, x='metros_cuadrados', y='precio', color='tipo_operacion',
                        title="Relación Tamaño vs Precio")
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()