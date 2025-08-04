"""
Configuración del proyecto de scraping inmobiliario
"""

# URLs base
BASE_URL = "https://infocasas.com.uy"
VENTA_URL = f"{BASE_URL}/venta/apartamento/montevideo"
ALQUILER_URL = f"{BASE_URL}/alquiler/apartamento/montevideo"

# Configuración de scraping
DELAY_BETWEEN_REQUESTS = 2  # segundos
MAX_PAGES_TO_SCRAPE = 50
TIMEOUT = 10

# Barrios de Montevideo a analizar
BARRIOS_MONTEVIDEO = [
    "Pocitos", "Punta Carretas", "Cordón", "Centro", "Ciudad Vieja",
    "Parque Rodó", "Buceo", "Malvín", "Carrasco", "Tres Cruces",
    "La Blanqueada", "Villa Biarritz", "Punta Gorda", "Palermo",
    "Barrio Sur", "Aguada", "Reducto", "Brazo Oriental", "Villa Dolores"
]

# Configuración de base de datos
DATABASE_PATH = "data/inmobiliaria.db"

# Configuración ML
TEST_SIZE = 0.2
RANDOM_STATE = 42

# Configuración de filtros de propiedades
MIN_PRICE = 50000  # USD
MAX_PRICE = 500000  # USD
MIN_M2 = 30
MAX_M2 = 200