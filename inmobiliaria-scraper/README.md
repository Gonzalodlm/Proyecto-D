# 🏡 Analizador de Inversiones Inmobiliarias

Aplicación Python para hacer web scraping de infocasas.com.uy y encontrar las mejores oportunidades de inversión inmobiliaria en Montevideo usando Machine Learning.

## 🎯 Características

- **Web Scraping**: Extrae datos de propiedades en venta y alquiler
- **Análisis de Mercado**: Calcula métricas por barrio (precio/m², ROI, etc.)
- **Machine Learning**: Predice valores y encuentra patrones
- **Optimización de Inversiones**: Encuentra las mejores oportunidades según tu presupuesto y tolerancia al riesgo

## 📁 Estructura del Proyecto

```
inmobiliaria-scraper/
├── scraping/
│   ├── infocasas_scraper.py    # Extrae datos de infocasas.com.uy
│   ├── data_processor.py       # Limpia y procesa datos
│   └── utils.py               # Funciones auxiliares
├── data/
│   ├── raw/                   # Datos crudos del scraping
│   ├── processed/             # Datos limpios y métricas
│   └── inmobiliaria.db        # Base de datos SQLite
├── machine_learning/
│   ├── investment_model.py    # Modelo de predicción ML
│   └── optimizer.py          # Optimizador de inversiones
├── analysis/
│   └── visualizations.py     # Gráficos y reportes
├── config/
│   └── settings.py           # Configuraciones
├── models/                   # Modelos ML entrenados
├── requirements.txt          # Dependencias
├── main.py                  # Aplicación principal
└── README.md               # Este archivo
```

## 🚀 Instalación

1. **Clonar el repositorio**:
```bash
git clone https://github.com/Gonzalodlm/Proyecto-D.git
cd inmobiliaria-scraper
```

2. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

3. **Instalar ChromeDriver**:
El scraper usa Selenium con Chrome. ChromeDriver se instala automáticamente.

## 📊 Uso

### 🌐 Interfaz Web (Recomendado):
```bash
streamlit run app.py
```
Abre tu navegador en `http://localhost:8501`

### 💻 Aplicación CLI:
```bash
python main.py
```

### Opciones del menú:

1. **Hacer scraping**: Extrae datos frescos de infocasas.com.uy
2. **Procesar datos**: Limpia y calcula métricas de mercado
3. **Entrenar modelo ML**: Crea modelo predictivo
4. **Buscar inversiones**: Encuentra oportunidades según tus criterios
5. **Análisis completo**: Ejecuta todo el pipeline
6. **Ver estadísticas**: Muestra resumen de datos

### Ejecución modular:

```bash
# Solo scraping
python scraping/infocasas_scraper.py

# Solo procesamiento
python scraping/data_processor.py

# Solo ML
python machine_learning/investment_model.py

# Solo optimización
python machine_learning/optimizer.py
```

## 🔧 Configuración

Editar `config/settings.py` para ajustar:

- Número máximo de páginas a scrapear
- Barrios a analizar
- Rangos de precios y tamaños
- Parámetros del modelo ML

## 📈 Métricas Calculadas

### Por Barrio:
- Precio promedio de venta y alquiler
- Precio por m² promedio
- ROI anual estimado
- Cantidad de propiedades disponibles

### Por Propiedad:
- Score de inversión (0-1)
- Precio por m²
- Ratio precio/dormitorios
- Potencial de revalorización

## 🤖 Algoritmo de Optimización

El algoritmo considera:

1. **ROI Anual**: (Alquiler mensual × 12) / Precio de venta
2. **Precio por m²**: Valor relativo en el mercado
3. **Tamaño**: Metros cuadrados de la propiedad
4. **Ubicación**: Barrio y sus características

### Perfiles de Riesgo:

- **Conservador**: Prioriza estabilidad y barrios consolidados
- **Balanceado**: Equilibra ROI y estabilidad
- **Agresivo**: Maximiza ROI potencial

## 📊 Datos Generados

### Archivos CSV en `data/processed/`:
- `propiedades_limpias.csv`: Todas las propiedades procesadas
- `metricas_venta_por_barrio.csv`: Estadísticas de venta por barrio
- `metricas_alquiler_por_barrio.csv`: Estadísticas de alquiler por barrio
- `roi_por_barrio.csv`: ROI calculado por barrio

### Base de Datos SQLite:
- `data/inmobiliaria.db`: Base de datos completa

## ⚠️ Consideraciones Legales

- Respeta los términos de servicio de infocasas.com.uy
- No hacer scraping excesivo (configurar delays)
- Solo para uso educativo y personal
- Los datos son aproximados, no constituyen asesoramiento financiero

## 🛠️ Dependencias Principales

- `requests`: Peticiones HTTP
- `beautifulsoup4`: Parsing HTML
- `selenium`: Automatización web
- `pandas`: Manipulación datos
- `scikit-learn`: Machine Learning
- `matplotlib/plotly`: Visualizaciones

## 🤝 Contribuir

1. Fork del proyecto
2. Crear rama feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit cambios (`git commit -am 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crear Pull Request

## 📝 Roadmap

- [ ] Agregar más sitios web (mercadolibre, gallito.com.uy)
- [ ] Implementar alertas por email
- [ ] Dashboard web con Flask/Django
- [ ] Análisis de tendencias temporales
- [ ] Integración con APIs de bancos para tasas

## 📞 Contacto

- GitHub: [@Gonzalodlm](https://github.com/Gonzalodlm)
- Email: gonzalodiaslopez3@gmail.com

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.