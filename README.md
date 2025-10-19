# 📜 Scraper de Proyectos de Ley - Congreso del Perú 🇵🇪

[![CI/CD](https://github.com/ben1998pe/peru-congreso-leyes-scraper/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/ben1998pe/peru-congreso-leyes-scraper/actions)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Este proyecto extrae, limpia y analiza datos de los proyectos de ley presentados en el Congreso del Perú desde su plataforma oficial: [https://wb2server.congreso.gob.pe/spley-portal/#/expediente/search](https://wb2server.congreso.gob.pe/spley-portal/#/expediente/search)

## 🚀 Características Principales

### ✨ Versión 2.0 - Mejorada
- **🚀 Scraping Avanzado**: Extracción automática con Selenium y BeautifulSoup con manejo robusto de errores
- **🔍 Validación de Datos**: Sistema completo de validación y limpieza de datos
- **📊 Monitoreo de Rendimiento**: Seguimiento en tiempo real del rendimiento del sistema
- **🛠️ CLI Completa**: Interfaz de línea de comandos para todas las operaciones
- **🧪 Suite de Pruebas**: Cobertura completa de pruebas unitarias e integración
- **📈 Análisis Avanzado**: Visualizaciones interactivas y reportes detallados
- **🔧 Configuración Flexible**: Sistema de configuración centralizado y personalizable
- **📝 Logging Mejorado**: Sistema de logging avanzado con rotación de archivos
- **🚀 CI/CD**: Pipeline automatizado de integración y despliegue continuo

## 🛠 Tecnologías Utilizadas

### Core
- **Python 3.8+**
- **Selenium 4.15+** - Automatización del navegador
- **BeautifulSoup 4.12+** - Parsing de HTML
- **pandas 2.1+** - Manipulación de datos
- **ChromeDriver** - Control del navegador Chrome

### Análisis y Visualización
- **matplotlib 3.8+** - Gráficos estáticos
- **seaborn 0.13+** - Visualizaciones estadísticas
- **plotly 5.17+** - Gráficos interactivos
- **jupyter** - Notebooks de análisis

### Utilidades
- **numpy 1.25+** - Cálculos numéricos
- **openpyxl 3.1+** - Exportación a Excel
- **tqdm 4.66+** - Barras de progreso

## 📁 Estructura del Proyecto

```
peru-congreso-leyes-scraper/
├── 📄 scraper.py                    # Scraper original (básico)
├── 📄 scraper_mejorado.py           # Scraper mejorado (v1.0)
├── 📄 scraper_enhanced.py           # Scraper mejorado v2.0 con validación y monitoreo
├── 📄 cli.py                        # Interfaz de línea de comandos
├── 📄 config.py                     # Configuración centralizada
├── 📄 ejemplo_uso.py                # Ejemplos de uso y menú interactivo
├── 📄 requirements.txt              # Dependencias del proyecto
├── 📄 setup.py                      # Script de instalación
├── 📄 Makefile                      # Comandos de automatización
├── 📁 config/                       # Configuración avanzada
│   └── environment.py               # Gestión de configuración por entorno
├── 📁 utils/                        # Utilidades mejoradas
│   ├── limpieza.py                  # Limpieza de datos
│   ├── logging_config.py            # Configuración de logging
│   ├── data_validator.py            # Validación de datos
│   └── performance_monitor.py       # Monitoreo de rendimiento
├── 📁 tests/                        # Suite de pruebas
│   └── test_scraper.py              # Pruebas unitarias e integración
├── 📁 .github/                      # Configuración de GitHub
│   └── workflows/
│       └── ci.yml                   # Pipeline de CI/CD
├── 📁 data/                         # Datos extraídos (CSV)
│   ├── proyectos_ley_*.csv
│   └── proyectos_ley_limpios_*.csv
├── 📁 notebooks/                    # Análisis exploratorio
│   └── analisis.ipynb
├── 📁 analysis/                     # Reportes y análisis
├── 📁 visualizations/               # Gráficos exportados
├── 📁 logs/                         # Archivos de log
└── 📄 chromedriver.exe              # Driver de Chrome
```

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com/ben1998pe/peru-congreso-leyes-scraper.git
cd peru-congreso-leyes-scraper
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar ChromeDriver
- Descargar ChromeDriver compatible con tu versión de Chrome
- Colocar `chromedriver.exe` en la raíz del proyecto
- O usar `webdriver-manager` para descarga automática

### 4. Ejecutar ejemplo básico
```bash
python ejemplo_uso.py
```

### 5. Usar la CLI mejorada (Recomendado)
```bash
# Scraping básico
python cli.py scrape

# Scraping con fechas personalizadas
python cli.py scrape --fecha-desde "01/01/2024" --fecha-hasta "31/01/2024"

# Ver todas las opciones
python cli.py --help
```

### 6. Usar Makefile para automatización
```bash
# Ver todas las opciones disponibles
make help

# Configuración completa del entorno de desarrollo
make dev-setup

# Ejecutar scraping
make scrape

# Ejecutar pruebas
make test
```

### 7. Configuración de entorno (Opcional)
```bash
# Copiar archivo de configuración de ejemplo
cp environment.example .env

# Editar configuración según necesidades
# nano .env
```

## 📖 Guía de Uso

### Uso Básico

```python
from scraper_mejorado import CongresoScraper

# Crear scraper
scraper = CongresoScraper(headless=False)

# Scraping de últimos 7 días
proyectos = scraper.scrape()

# Guardar datos
archivo = scraper.save_to_csv(proyectos)
print(f"Datos guardados en: {archivo}")

# Cerrar scraper
scraper.close()
```

### Uso Avanzado con Fechas Personalizadas

```python
from datetime import datetime, timedelta

# Definir rango de fechas
fecha_desde = "01/06/2025"
fecha_hasta = "15/06/2025"

scraper = CongresoScraper(headless=True)  # Modo headless
proyectos = scraper.scrape(fecha_desde, fecha_hasta)
```

### Limpieza y Análisis de Datos

```python
from utils.limpieza import DataCleaner, limpiar_archivo_csv

# Limpiar archivo existente
archivo_limpio = limpiar_archivo_csv("data/proyectos_ley_2025-06-05.csv")

# Análisis completo
cleaner = DataCleaner()
df_limpio = cleaner.limpiar_dataframe(df_raw)
resumen = cleaner.generar_resumen(df_limpio)
```

## 🆕 Nuevas Funcionalidades v2.0

### 🚀 Scraper Mejorado (`scraper_enhanced.py`)
- **Manejo Robusto de Errores**: Sistema avanzado de reintentos y recuperación de errores
- **Validación de Datos**: Validación automática de todos los datos extraídos
- **Monitoreo de Rendimiento**: Seguimiento en tiempo real del rendimiento del sistema
- **Logging Avanzado**: Sistema de logging con rotación de archivos y colores
- **Múltiples Selectores**: Fallbacks automáticos para elementos de la página web

### 🛠️ CLI Completa (`cli.py`)
```bash
# Comandos disponibles
python cli.py scrape          # Scraping con opciones avanzadas
python cli.py clean           # Limpieza de datos
python cli.py validate        # Validación de calidad de datos
python cli.py analyze         # Análisis completo de datos
python cli.py monitor         # Monitoreo de rendimiento
python cli.py config          # Ver configuración actual
```

### 🔍 Sistema de Validación (`utils/data_validator.py`)
- **Validación de Campos**: Verificación automática de formato y contenido
- **Detección de Anomalías**: Identificación de datos inconsistentes
- **Reportes de Validación**: Informes detallados de calidad de datos
- **Modo Estricto**: Validación más estricta para datos críticos

### 📊 Monitoreo de Rendimiento (`utils/performance_monitor.py`)
- **Métricas del Sistema**: CPU, memoria, disco, red
- **Alertas Automáticas**: Notificaciones cuando se exceden umbrales
- **Exportación de Datos**: Exportación de métricas a JSON
- **Profiling de Código**: Medición de tiempo de ejecución de funciones

### 🧪 Suite de Pruebas (`tests/`)
- **Pruebas Unitarias**: Cobertura completa de todas las funciones
- **Pruebas de Integración**: Verificación de flujos completos
- **Pruebas Parametrizadas**: Múltiples casos de prueba con datos variados
- **Mocks y Fixtures**: Simulación de dependencias externas

### 🔧 Automatización (`Makefile`)
```bash
make dev-setup         # Configuración completa del entorno
make test              # Ejecutar todas las pruebas
make quality           # Verificaciones de calidad de código
make pipeline          # Pipeline completo de datos
make analyze-complete  # Análisis completo automatizado
make health-check      # Verificación de salud del proyecto
```

### 📊 Scripts de Análisis (`scripts/`)
- **`run_analysis.py`**: Análisis completo automatizado con exportación de resultados
- **`health_check.py`**: Verificación de salud del proyecto y estructura

### 📓 Notebook Mejorado (`notebooks/analisis.ipynb`)
- **Validación automática**: Verificación de calidad de datos integrada
- **Exportación avanzada**: Generación automática de reportes HTML y JSON
- **Análisis interactivo**: Visualizaciones mejoradas con Plotly
- **Reportes automáticos**: Generación de reportes HTML profesionales

## 📊 Funcionalidades del Scraper Mejorado

### ✨ Características Principales

1. **Manejo de Fechas Flexible**
   - Rango de fechas personalizable
   - Fechas por defecto (últimos 7 días)
   - Validación de formato de fechas

2. **Paginación Automática**
   - Detección automática de páginas múltiples
   - Navegación secuencial entre páginas
   - Manejo de timeouts y errores

3. **Limpieza de Datos Avanzada**
   - Normalización de fechas y proyectos
   - Extracción de partidos políticos
   - Clasificación automática de tipos de proyectos
   - Detección de regiones geográficas
   - Análisis de colaboraciones entre congresistas

4. **Sistema de Logging**
   - Logs detallados de todas las operaciones
   - Rotación automática de archivos de log
   - Niveles de logging configurables

5. **Configuración Centralizada**
   - Parámetros en archivo `config.py`
   - Selectores CSS/XPath configurables
   - Timeouts y delays ajustables

### 🔍 Datos Extraídos

- **Proyecto**: Número y código del proyecto de ley
- **Fecha**: Fecha de presentación (normalizada)
- **Título**: Título completo del proyecto
- **Estado**: Estado procesal actual
- **Proponente**: Entidad proponente
- **Autores**: Lista de congresistas autores
- **Partido Político**: Extraído automáticamente
- **Tipo de Proyecto**: Clasificado automáticamente
- **Región**: Región mencionada en el proyecto
- **Metadatos**: Año, mes, día de la semana, etc.

## 📈 Análisis y Visualizaciones

### Notebook de Análisis (`notebooks/analisis.ipynb`)

1. **Carga y Limpieza de Datos**
2. **Análisis Descriptivo**
3. **Análisis Temporal**
4. **Análisis por Partido Político**
5. **Análisis por Tipo de Proyecto**
6. **Análisis de Autores y Colaboraciones**
7. **Visualizaciones Interactivas**

### Tipos de Visualizaciones

- **Gráficos de Barras**: Proyectos por partido/región/tipo
- **Gráficos de Torta**: Distribución de tipos de proyectos
- **Timeline**: Evolución temporal de proyectos
- **Heatmaps**: Actividad por congresista
- **Word Clouds**: Temas más frecuentes

## ⚙️ Configuración Avanzada

### Archivo `config.py`

```python
# Configuración del navegador
CHROME_OPTIONS = [
    "--start-maximized",
    "--no-sandbox",
    "--disable-dev-shm-usage"
]

# Timeouts y delays
WAIT_TIMEOUT = 15
PAGE_LOAD_DELAY = 3
SEARCH_DELAY = 5

# Rango de fechas por defecto
DEFAULT_DATE_RANGE = 7  # días hacia atrás

# Configuración de logging
LOG_LEVEL = "INFO"
LOG_FILE = "logs/scraper_20250605.log"
```

## 🐛 Solución de Problemas

### Errores Comunes

1. **ChromeDriver no encontrado**
   ```bash
   # Descargar ChromeDriver compatible
   # O usar webdriver-manager
   pip install webdriver-manager
   ```

2. **Timeout en elementos**
   - Aumentar `WAIT_TIMEOUT` en `config.py`
   - Verificar conectividad a internet
   - Verificar que el sitio web esté disponible

3. **Datos mal formateados**
   - Ejecutar limpieza de datos con `utils/limpieza.py`
   - Verificar logs para errores de parsing

4. **Memoria insuficiente**
   - Usar modo headless: `CongresoScraper(headless=True)`
   - Procesar datos en lotes más pequeños

### Logs y Debugging

Los logs se guardan en `logs/scraper_YYYYMMDD.log` con información detallada:
- Navegación entre páginas
- Elementos encontrados/no encontrados
- Errores de parsing
- Estadísticas de extracción

## 📊 Ejemplos de Análisis

### Estadísticas Básicas
```python
# Total de proyectos por partido
df_clean['partido_politico'].value_counts()

# Proyectos por tipo
df_clean['tipo_proyecto'].value_counts()

# Congresista más activo
todos_autores = []
for autores in df_clean['autores_limpios']:
    todos_autores.extend(autores)
pd.Series(todos_autores).value_counts().head(1)
```

### Análisis Temporal
```python
# Proyectos por mes
df_clean.groupby([df_clean['fecha_datetime'].dt.year, 
                 df_clean['fecha_datetime'].dt.month]).size()

# Proyectos por día de la semana
df_clean['dia_semana'].value_counts()
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## ✍️ Autor

**Benjamin Oscco Arias**
- GitHub: [@ben1998pe](https://github.com/ben1998pe)
- LinkedIn: [Benjamin Oscco](https://linkedin.com/in/benjamin-oscco)

## 🙏 Agradecimientos

- Al Congreso del Perú por proporcionar acceso público a los datos
- A la comunidad de Python por las excelentes librerías utilizadas
- A todos los contribuidores del proyecto

---

**⚠️ Nota Legal**: Este proyecto es solo para fines educativos y de investigación. Respete los términos de uso del sitio web del Congreso del Perú.
