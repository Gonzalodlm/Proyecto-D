"""
Aplicación principal de análisis de inversiones inmobiliarias
"""

import sys
import os
from datetime import datetime

# Importar módulos del proyecto
from scraping.infocasas_scraper import InfocasasScraper
from scraping.data_processor import DataProcessor
from machine_learning.investment_model import InvestmentModel
from machine_learning.optimizer import InvestmentOptimizer

def print_menu():
    """Muestra el menú principal"""
    print("\n" + "="*50)
    print("  ANALIZADOR DE INVERSIONES INMOBILIARIAS")
    print("="*50)
    print("1. Hacer scraping de propiedades")
    print("2. Procesar y limpiar datos")
    print("3. Entrenar modelo de ML")
    print("4. Buscar oportunidades de inversión")
    print("5. Análisis completo (1-4)")
    print("6. Ver estadísticas generales")
    print("0. Salir")
    print("="*50)

def run_scraping():
    """Ejecuta el scraping de propiedades"""
    print("\n🔍 Iniciando scraping de infocasas.com.uy...")
    
    scraper = InfocasasScraper()
    try:
        # Scraper propiedades en venta
        print("📊 Scrapeando propiedades en venta...")
        scraper.scrape_properties("venta", 20)  # Reducido para pruebas
        
        # Scraper propiedades en alquiler
        print("🏠 Scrapeando propiedades en alquiler...")
        scraper.scrape_properties("alquiler", 20)
        
        # Guardar datos
        scraper.save_to_database()
        print("✅ Scraping completado exitosamente")
        
    except Exception as e:
        print(f"❌ Error durante el scraping: {e}")
    finally:
        scraper.close()

def run_data_processing():
    """Procesa y limpia los datos"""
    print("\n🧹 Procesando y limpiando datos...")
    
    try:
        processor = DataProcessor()
        processor.load_data()
        processor.clean_data()
        roi_analysis = processor.save_processed_data()
        
        print("✅ Procesamiento completado")
        print("\n📈 TOP 5 BARRIOS POR ROI:")
        print(roi_analysis.head()[['barrio', 'roi_anual_porcentaje']].to_string(index=False))
        
    except Exception as e:
        print(f"❌ Error durante el procesamiento: {e}")

def run_ml_training():
    """Entrena el modelo de machine learning"""
    print("\n🤖 Entrenando modelo de Machine Learning...")
    
    try:
        model = InvestmentModel()
        if model.load_processed_data():
            score = model.train_model()
            model.analyze_feature_importance()
            print(f"✅ Modelo entrenado exitosamente (R² = {score:.4f})")
        else:
            print("❌ No se encontraron datos procesados")
            
    except Exception as e:
        print(f"❌ Error durante el entrenamiento: {e}")

def run_investment_analysis():
    """Ejecuta análisis de oportunidades de inversión"""
    print("\n💰 Analizando oportunidades de inversión...")
    
    try:
        optimizer = InvestmentOptimizer()
        if not optimizer.load_data():
            print("❌ No se encontraron datos procesados")
            return
        
        # Solicitar parámetros al usuario
        print("\nConfiguración de búsqueda:")
        budget_min = int(input("Presupuesto mínimo (USD): ") or "80000")
        budget_max = int(input("Presupuesto máximo (USD): ") or "200000")
        
        print("\nTolerancia al riesgo:")
        print("1. Baja (conservador)")
        print("2. Media (balanceado)")
        print("3. Alta (agresivo)")
        risk_choice = input("Seleccione (1-3): ") or "2"
        
        risk_map = {"1": "low", "2": "medium", "3": "high"}
        risk_tolerance = risk_map.get(risk_choice, "medium")
        
        location = input("Barrio preferido (opcional): ") or None
        
        # Ejecutar análisis
        results = optimizer.get_investment_recommendation(
            budget_min, budget_max, risk_tolerance, location
        )
        
        if results:
            print("✅ Análisis completado")
        
    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")

def run_complete_analysis():
    """Ejecuta el análisis completo"""
    print("\n🚀 Ejecutando análisis completo...")
    print("Esto puede tomar varios minutos...")
    
    run_scraping()
    run_data_processing()
    run_ml_training()
    run_investment_analysis()
    
    print("\n✅ Análisis completo finalizado")

def show_statistics():
    """Muestra estadísticas generales"""
    print("\n📊 Estadísticas generales...")
    
    try:
        # Cargar datos si existen
        import pandas as pd
        import sqlite3
        from config.settings import DATABASE_PATH
        
        if os.path.exists(DATABASE_PATH):
            conn = sqlite3.connect(DATABASE_PATH)
            df = pd.read_sql_query("SELECT * FROM propiedades", conn)
            conn.close()
            
            print(f"Total propiedades en base de datos: {len(df)}")
            print(f"Propiedades en venta: {len(df[df['tipo_operacion'] == 'venta'])}")
            print(f"Propiedades en alquiler: {len(df[df['tipo_operacion'] == 'alquiler'])}")
            print(f"Barrios únicos: {df['barrio'].nunique()}")
            print(f"Rango de precios: USD {df['precio'].min():,.0f} - {df['precio'].max():,.0f}")
            print(f"Última actualización: {df['fecha_scraping'].max()}")
        else:
            print("No hay datos disponibles. Ejecute primero el scraping.")
            
    except Exception as e:
        print(f"❌ Error mostrando estadísticas: {e}")

def main():
    """Función principal"""
    print("🏡 Bienvenido al Analizador de Inversiones Inmobiliarias")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    while True:
        print_menu()
        choice = input("\nSeleccione una opción: ")
        
        if choice == "1":
            run_scraping()
        elif choice == "2":
            run_data_processing()
        elif choice == "3":
            run_ml_training()
        elif choice == "4":
            run_investment_analysis()
        elif choice == "5":
            run_complete_analysis()
        elif choice == "6":
            show_statistics()
        elif choice == "0":
            print("👋 ¡Gracias por usar el analizador!")
            break
        else:
            print("❌ Opción no válida")
        
        input("\nPresione Enter para continuar...")

if __name__ == "__main__":
    main()