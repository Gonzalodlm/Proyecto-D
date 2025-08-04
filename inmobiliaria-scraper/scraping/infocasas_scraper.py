"""
Web scraper para infocasas.com.uy
Extrae datos de propiedades en venta y alquiler
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import sqlite3
import os
import sys

# Agregar el directorio padre al path para importar config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import *

class InfocasasScraper:
    def __init__(self):
        self.setup_driver()
        self.data = []
        
    def setup_driver(self):
        """Configura el driver de Selenium"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Ejecutar sin ventana
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(
            service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
    def extract_property_data(self, property_element):
        """Extrae datos de un elemento de propiedad"""
        try:
            # Precio
            price_element = property_element.find_element(By.CSS_SELECTOR, ".price")
            price = self.clean_price(price_element.text)
            
            # Detalles de la propiedad
            details = property_element.find_element(By.CSS_SELECTOR, ".property-details")
            
            # Metros cuadrados
            m2_match = re.search(r'(\d+)\s*m²', details.text)
            m2 = int(m2_match.group(1)) if m2_match else None
            
            # Dormitorios
            rooms_match = re.search(r'(\d+)\s*dorm', details.text)
            rooms = int(rooms_match.group(1)) if rooms_match else None
            
            # Baños
            baths_match = re.search(r'(\d+)\s*baño', details.text)
            baths = int(baths_match.group(1)) if baths_match else None
            
            # Barrio
            location_element = property_element.find_element(By.CSS_SELECTOR, ".location")
            neighborhood = self.clean_neighborhood(location_element.text)
            
            # URL de la propiedad
            link_element = property_element.find_element(By.CSS_SELECTOR, "a")
            property_url = link_element.get_attribute("href")
            
            return {
                'precio': price,
                'metros_cuadrados': m2,
                'dormitorios': rooms,
                'baños': baths,
                'barrio': neighborhood,
                'precio_por_m2': price / m2 if price and m2 else None,
                'url': property_url,
                'fecha_scraping': pd.Timestamp.now()
            }
            
        except Exception as e:
            print(f"Error extrayendo datos: {e}")
            return None
    
    def clean_price(self, price_text):
        """Limpia y convierte el precio a número"""
        # Remover símbolos y convertir a número
        price_clean = re.sub(r'[U$S,.\s]', '', price_text)
        try:
            return int(price_clean)
        except:
            return None
    
    def clean_neighborhood(self, location_text):
        """Extrae el barrio del texto de ubicación"""
        # Implementar lógica para extraer barrio específico
        for barrio in BARRIOS_MONTEVIDEO:
            if barrio.lower() in location_text.lower():
                return barrio
        return location_text.strip()
    
    def scrape_properties(self, operation_type="venta", max_pages=10):
        """Scrape propiedades por tipo de operación"""
        url = VENTA_URL if operation_type == "venta" else ALQUILER_URL
        
        for page in range(1, max_pages + 1):
            page_url = f"{url}?pagina={page}"
            print(f"Scrapeando página {page}: {page_url}")
            
            try:
                self.driver.get(page_url)
                time.sleep(DELAY_BETWEEN_REQUESTS)
                
                # Esperar a que carguen las propiedades
                WebDriverWait(self.driver, TIMEOUT).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".property-item"))
                )
                
                properties = self.driver.find_elements(By.CSS_SELECTOR, ".property-item")
                
                for prop in properties:
                    property_data = self.extract_property_data(prop)
                    if property_data:
                        property_data['tipo_operacion'] = operation_type
                        self.data.append(property_data)
                
                print(f"Página {page} completada. Total propiedades: {len(self.data)}")
                
            except Exception as e:
                print(f"Error en página {page}: {e}")
                continue
    
    def save_to_database(self):
        """Guarda los datos en SQLite"""
        df = pd.DataFrame(self.data)
        
        # Crear directorio data si no existe
        os.makedirs('data', exist_ok=True)
        
        # Conectar a la base de datos
        conn = sqlite3.connect(DATABASE_PATH)
        
        # Guardar datos
        df.to_sql('propiedades', conn, if_exists='append', index=False)
        
        conn.close()
        print(f"Datos guardados en {DATABASE_PATH}")
    
    def close(self):
        """Cierra el driver"""
        self.driver.quit()

if __name__ == "__main__":
    scraper = InfocasasScraper()
    
    try:
        # Scraper propiedades en venta
        print("Iniciando scraping de propiedades en venta...")
        scraper.scrape_properties("venta", MAX_PAGES_TO_SCRAPE)
        
        # Scraper propiedades en alquiler
        print("Iniciando scraping de propiedades en alquiler...")
        scraper.scrape_properties("alquiler", MAX_PAGES_TO_SCRAPE)
        
        # Guardar datos
        scraper.save_to_database()
        
    finally:
        scraper.close()