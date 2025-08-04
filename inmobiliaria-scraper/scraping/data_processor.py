"""
Procesador de datos inmobiliarios
Limpia y prepara los datos para análisis y ML
"""

import pandas as pd
import numpy as np
import sqlite3
import sys
import os

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import *

class DataProcessor:
    def __init__(self):
        self.df = None
        
    def load_data(self):
        """Carga datos desde la base de datos"""
        conn = sqlite3.connect(DATABASE_PATH)
        self.df = pd.read_sql_query("SELECT * FROM propiedades", conn)
        conn.close()
        print(f"Cargados {len(self.df)} registros")
        
    def clean_data(self):
        """Limpia y procesa los datos"""
        print("Iniciando limpieza de datos...")
        
        # Remover registros con datos faltantes críticos
        initial_count = len(self.df)
        self.df = self.df.dropna(subset=['precio', 'metros_cuadrados', 'barrio'])
        print(f"Removidos {initial_count - len(self.df)} registros con datos faltantes")
        
        # Filtrar por rangos válidos
        self.df = self.df[
            (self.df['precio'] >= MIN_PRICE) & 
            (self.df['precio'] <= MAX_PRICE) &
            (self.df['metros_cuadrados'] >= MIN_M2) &
            (self.df['metros_cuadrados'] <= MAX_M2)
        ]
        
        # Calcular precio por m2 si no existe
        self.df['precio_por_m2'] = self.df['precio'] / self.df['metros_cuadrados']
        
        # Normalizar nombres de barrios
        self.df['barrio'] = self.df['barrio'].str.strip().str.title()
        
        # Crear variables categóricas
        self.df['categoria_precio'] = pd.cut(
            self.df['precio'], 
            bins=[0, 100000, 200000, 300000, float('inf')],
            labels=['Económica', 'Media', 'Alta', 'Premium']
        )
        
        self.df['categoria_tamaño'] = pd.cut(
            self.df['metros_cuadrados'],
            bins=[0, 50, 80, 120, float('inf')],
            labels=['Pequeña', 'Mediana', 'Grande', 'Extra Grande']
        )
        
        print(f"Datos limpios: {len(self.df)} registros")
        
    def calculate_market_metrics(self):
        """Calcula métricas del mercado por barrio"""
        # Métricas por barrio para venta
        venta_metrics = self.df[self.df['tipo_operacion'] == 'venta'].groupby('barrio').agg({
            'precio': ['mean', 'median', 'std', 'count'],
            'precio_por_m2': ['mean', 'median', 'std'],
            'metros_cuadrados': ['mean', 'median']
        }).round(2)
        
        # Métricas por barrio para alquiler
        alquiler_metrics = self.df[self.df['tipo_operacion'] == 'alquiler'].groupby('barrio').agg({
            'precio': ['mean', 'median', 'std', 'count'],
            'precio_por_m2': ['mean', 'median', 'std'],
            'metros_cuadrados': ['mean', 'median']
        }).round(2)
        
        return venta_metrics, alquiler_metrics
    
    def calculate_roi_potential(self):
        """Calcula potencial de ROI por barrio"""
        # Obtener precios promedio de venta y alquiler por barrio
        venta_avg = self.df[self.df['tipo_operacion'] == 'venta'].groupby('barrio')['precio'].mean()
        alquiler_avg = self.df[self.df['tipo_operacion'] == 'alquiler'].groupby('barrio')['precio'].mean()
        
        # Calcular ROI anual (alquiler mensual * 12 / precio de venta)
        roi_data = []
        for barrio in venta_avg.index:
            if barrio in alquiler_avg.index:
                precio_venta = venta_avg[barrio]
                precio_alquiler_mensual = alquiler_avg[barrio]
                roi_anual = (precio_alquiler_mensual * 12 / precio_venta) * 100
                
                roi_data.append({
                    'barrio': barrio,
                    'precio_venta_promedio': precio_venta,
                    'precio_alquiler_mensual_promedio': precio_alquiler_mensual,
                    'roi_anual_porcentaje': roi_anual
                })
        
        roi_df = pd.DataFrame(roi_data).sort_values('roi_anual_porcentaje', ascending=False)
        return roi_df
    
    def prepare_ml_features(self):
        """Prepara features para machine learning"""
        # Crear DataFrame para ML
        ml_df = self.df.copy()
        
        # Encoding de variables categóricas
        ml_df = pd.get_dummies(ml_df, columns=['barrio', 'tipo_operacion'], prefix=['barrio', 'operacion'])
        
        # Rellenar valores faltantes
        ml_df['dormitorios'] = ml_df['dormitorios'].fillna(ml_df['dormitorios'].median())
        ml_df['baños'] = ml_df['baños'].fillna(ml_df['baños'].median())
        
        # Crear features adicionales
        ml_df['ratio_precio_dormitorios'] = ml_df['precio'] / ml_df['dormitorios']
        ml_df['ratio_m2_dormitorios'] = ml_df['metros_cuadrados'] / ml_df['dormitorios']
        
        return ml_df
    
    def save_processed_data(self):
        """Guarda datos procesados"""
        # Crear directorio si no existe
        os.makedirs('data/processed', exist_ok=True)
        
        # Guardar CSV
        self.df.to_csv('data/processed/propiedades_limpias.csv', index=False)
        
        # Calcular y guardar métricas
        venta_metrics, alquiler_metrics = self.calculate_market_metrics()
        venta_metrics.to_csv('data/processed/metricas_venta_por_barrio.csv')
        alquiler_metrics.to_csv('data/processed/metricas_alquiler_por_barrio.csv')
        
        # Calcular y guardar ROI
        roi_df = self.calculate_roi_potential()
        roi_df.to_csv('data/processed/roi_por_barrio.csv', index=False)
        
        print("Datos procesados guardados en data/processed/")
        
        return roi_df

if __name__ == "__main__":
    processor = DataProcessor()
    processor.load_data()
    processor.clean_data()
    roi_analysis = processor.save_processed_data()
    
    print("\n=== TOP 10 BARRIOS POR ROI ===")
    print(roi_analysis.head(10)[['barrio', 'roi_anual_porcentaje']].to_string(index=False))