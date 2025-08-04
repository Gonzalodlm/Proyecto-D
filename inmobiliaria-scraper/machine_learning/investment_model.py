"""
Modelo de Machine Learning para optimización de inversiones inmobiliarias
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
import joblib
import sys
import os

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import *

class InvestmentModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = None
        self.target_column = 'precio_por_m2'
        
    def load_processed_data(self):
        """Carga datos procesados"""
        try:
            self.df = pd.read_csv('data/processed/propiedades_limpias.csv')
            print(f"Datos cargados: {len(self.df)} registros")
            return True
        except FileNotFoundError:
            print("Error: Primero debe ejecutar el procesador de datos")
            return False
    
    def prepare_features(self):
        """Prepara características para el modelo"""
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
        ml_df['ratio_baño_dormitorios'] = ml_df['baños'] / ml_df['dormitorios']
        
        # Seleccionar features relevantes
        feature_columns = [
            'metros_cuadrados', 'dormitorios', 'baños',
            'ratio_precio_dormitorios', 'ratio_m2_dormitorios', 'ratio_baño_dormitorios'
        ]
        
        # Agregar columnas dummy de barrios y operaciones
        barrio_cols = [col for col in ml_df.columns if col.startswith('barrio_')]
        operacion_cols = [col for col in ml_df.columns if col.startswith('operacion_')]
        
        self.feature_columns = feature_columns + barrio_cols + operacion_cols
        
        return ml_df
    
    def train_model(self):
        """Entrena el modelo de machine learning"""
        print("Preparando datos para entrenamiento...")
        ml_df = self.prepare_features()
        
        # Separar features y target
        X = ml_df[self.feature_columns]
        y = ml_df[self.target_column]
        
        # División train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
        )
        
        # Escalar features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Entrenar múltiples modelos
        models = {
            'RandomForest': RandomForestRegressor(n_estimators=100, random_state=RANDOM_STATE),
            'GradientBoosting': GradientBoostingRegressor(random_state=RANDOM_STATE),
            'LinearRegression': LinearRegression()
        }
        
        best_model = None
        best_score = float('-inf')
        
        print("Entrenando modelos...")
        for name, model in models.items():
            if name == 'LinearRegression':
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
            
            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            
            print(f"{name}:")
            print(f"  R² Score: {r2:.4f}")
            print(f"  MAE: {mae:.2f}")
            print(f"  RMSE: {rmse:.2f}")
            print()
            
            if r2 > best_score:
                best_score = r2
                best_model = model
                self.model = model
                self.best_model_name = name
        
        print(f"Mejor modelo: {self.best_model_name} (R² = {best_score:.4f})")
        
        # Guardar modelo
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.model, 'models/investment_model.pkl')
        joblib.dump(self.scaler, 'models/scaler.pkl')
        joblib.dump(self.feature_columns, 'models/feature_columns.pkl')
        
        return best_score
    
    def predict_property_value(self, property_data):
        """Predice el valor de una propiedad"""
        if self.model is None:
            self.load_model()
        
        # Convertir a DataFrame
        df = pd.DataFrame([property_data])
        
        # Aplicar el mismo procesamiento
        # (Este método necesitaría el mismo preprocesamiento que en train)
        
        if self.best_model_name == 'LinearRegression':
            prediction = self.model.predict(self.scaler.transform(df[self.feature_columns]))
        else:
            prediction = self.model.predict(df[self.feature_columns])
        
        return prediction[0]
    
    def load_model(self):
        """Carga modelo entrenado"""
        try:
            self.model = joblib.load('models/investment_model.pkl')
            self.scaler = joblib.load('models/scaler.pkl')
            self.feature_columns = joblib.load('models/feature_columns.pkl')
            print("Modelo cargado exitosamente")
            return True
        except FileNotFoundError:
            print("Error: No se encontró modelo entrenado")
            return False
    
    def analyze_feature_importance(self):
        """Analiza importancia de características"""
        if hasattr(self.model, 'feature_importances_'):
            importance_df = pd.DataFrame({
                'feature': self.feature_columns,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            print("=== IMPORTANCIA DE CARACTERÍSTICAS ===")
            print(importance_df.head(10).to_string(index=False))
            
            return importance_df
        else:
            print("El modelo no soporta análisis de importancia")
            return None

if __name__ == "__main__":
    model = InvestmentModel()
    
    if model.load_processed_data():
        score = model.train_model()
        model.analyze_feature_importance()
    else:
        print("Ejecute primero el scraper y el procesador de datos")