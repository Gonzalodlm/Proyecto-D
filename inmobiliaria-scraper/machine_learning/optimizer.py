"""
Optimizador de inversiones inmobiliarias
Encuentra las mejores oportunidades de inversión
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import sys
import os

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import *

class InvestmentOptimizer:
    def __init__(self):
        self.properties_df = None
        self.roi_df = None
        self.investment_scores = None
        
    def load_data(self):
        """Carga datos procesados"""
        try:
            self.properties_df = pd.read_csv('data/processed/propiedades_limpias.csv')
            self.roi_df = pd.read_csv('data/processed/roi_por_barrio.csv')
            print(f"Datos cargados: {len(self.properties_df)} propiedades")
            return True
        except FileNotFoundError:
            print("Error: Ejecute primero el procesador de datos")
            return False
    
    def calculate_investment_score(self, budget_min=50000, budget_max=300000, 
                                 risk_tolerance='medium'):
        """
        Calcula un score de inversión para cada propiedad
        
        Parámetros:
        - budget_min: Presupuesto mínimo
        - budget_max: Presupuesto máximo  
        - risk_tolerance: 'low', 'medium', 'high'
        """
        # Filtrar propiedades en venta dentro del presupuesto
        venta_props = self.properties_df[
            (self.properties_df['tipo_operacion'] == 'venta') &
            (self.properties_df['precio'] >= budget_min) &
            (self.properties_df['precio'] <= budget_max)
        ].copy()
        
        if len(venta_props) == 0:
            print("No hay propiedades en el rango de presupuesto especificado")
            return None
        
        # Agregar datos de ROI por barrio
        venta_props = venta_props.merge(
            self.roi_df[['barrio', 'roi_anual_porcentaje']], 
            on='barrio', 
            how='left'
        )
        
        # Rellenar ROI faltante con la mediana
        venta_props['roi_anual_porcentaje'] = venta_props['roi_anual_porcentaje'].fillna(
            venta_props['roi_anual_porcentaje'].median()
        )
        
        # Crear features para scoring
        scaler = MinMaxScaler()
        
        # Normalizar métricas (0-1, donde 1 es mejor)
        venta_props['score_roi'] = scaler.fit_transform(
            venta_props[['roi_anual_porcentaje']]
        ).flatten()
        
        venta_props['score_precio_m2'] = 1 - scaler.fit_transform(
            venta_props[['precio_por_m2']]
        ).flatten()  # Invertido: menor precio/m2 = mejor
        
        venta_props['score_tamaño'] = scaler.fit_transform(
            venta_props[['metros_cuadrados']]
        ).flatten()
        
        # Calcular score basado en tolerancia al riesgo
        if risk_tolerance == 'low':
            # Priorizar estabilidad y barrios consolidados
            weights = {'roi': 0.3, 'precio_m2': 0.4, 'tamaño': 0.3}
        elif risk_tolerance == 'medium':
            # Balance entre ROI y estabilidad
            weights = {'roi': 0.4, 'precio_m2': 0.3, 'tamaño': 0.3}
        else:  # high
            # Priorizar ROI alto
            weights = {'roi': 0.6, 'precio_m2': 0.2, 'tamaño': 0.2}
        
        venta_props['investment_score'] = (
            venta_props['score_roi'] * weights['roi'] +
            venta_props['score_precio_m2'] * weights['precio_m2'] +
            venta_props['score_tamaño'] * weights['tamaño']
        )
        
        # Ordenar por score
        venta_props = venta_props.sort_values('investment_score', ascending=False)
        
        self.investment_scores = venta_props
        return venta_props
    
    def get_top_opportunities(self, n=10):
        """Obtiene las mejores N oportunidades de inversión"""
        if self.investment_scores is None:
            print("Primero calcule los scores de inversión")
            return None
        
        top_props = self.investment_scores.head(n)[
            ['barrio', 'precio', 'metros_cuadrados', 'precio_por_m2', 
             'roi_anual_porcentaje', 'investment_score', 'dormitorios', 'baños']
        ].round(2)
        
        return top_props
    
    def analyze_by_neighborhood(self):
        """Analiza oportunidades por barrio"""
        if self.investment_scores is None:
            return None
        
        neighborhood_analysis = self.investment_scores.groupby('barrio').agg({
            'investment_score': ['mean', 'max', 'count'],
            'precio': ['mean', 'min', 'max'],
            'roi_anual_porcentaje': 'mean',
            'precio_por_m2': 'mean'
        }).round(2)
        
        neighborhood_analysis.columns = [
            'score_promedio', 'score_maximo', 'cantidad_propiedades',
            'precio_promedio', 'precio_minimo', 'precio_maximo',
            'roi_promedio', 'precio_m2_promedio'
        ]
        
        return neighborhood_analysis.sort_values('score_promedio', ascending=False)
    
    def get_investment_recommendation(self, budget_min, budget_max, 
                                    risk_tolerance='medium', location_preference=None):
        """
        Genera recomendación de inversión personalizada
        """
        print(f"=== ANÁLISIS DE INVERSIÓN ===")
        print(f"Presupuesto: USD {budget_min:,} - {budget_max:,}")
        print(f"Tolerancia al riesgo: {risk_tolerance}")
        if location_preference:
            print(f"Preferencia de ubicación: {location_preference}")
        print()
        
        # Calcular scores
        opportunities = self.calculate_investment_score(
            budget_min, budget_max, risk_tolerance
        )
        
        if opportunities is None:
            return None
        
        # Filtrar por ubicación si se especifica
        if location_preference:
            opportunities = opportunities[
                opportunities['barrio'].str.contains(location_preference, case=False, na=False)
            ]
        
        # Top oportunidades
        top_10 = self.get_top_opportunities(10)
        print("=== TOP 10 OPORTUNIDADES DE INVERSIÓN ===")
        print(top_10.to_string(index=False))
        print()
        
        # Análisis por barrio
        neighborhood_analysis = self.analyze_by_neighborhood()
        print("=== ANÁLISIS POR BARRIO (TOP 5) ===")
        print(neighborhood_analysis.head().to_string())
        print()
        
        # Recomendaciones específicas
        best_opportunity = top_10.iloc[0]
        print("=== MEJOR OPORTUNIDAD ===")
        print(f"Barrio: {best_opportunity['barrio']}")
        print(f"Precio: USD {best_opportunity['precio']:,.0f}")
        print(f"Tamaño: {best_opportunity['metros_cuadrados']:.0f} m²")
        print(f"ROI Anual Estimado: {best_opportunity['roi_anual_porcentaje']:.1f}%")
        print(f"Score de Inversión: {best_opportunity['investment_score']:.3f}")
        
        return {
            'top_opportunities': top_10,
            'neighborhood_analysis': neighborhood_analysis,
            'best_opportunity': best_opportunity
        }

if __name__ == "__main__":
    optimizer = InvestmentOptimizer()
    
    if optimizer.load_data():
        # Ejemplo de análisis
        results = optimizer.get_investment_recommendation(
            budget_min=80000,
            budget_max=200000,
            risk_tolerance='medium'
        )
    else:
        print("Ejecute primero el scraper y procesador de datos")