# 📜 Scraper de Proyectos de Ley - Congreso del Perú 🇵🇪

[![CI/CD](https://github.com/ben1998pe/peru-congreso-leyes-scraper/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/ben1998pe/peru-congreso-leyes-scraper/actions)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Este proyecto extrae, limpia y analiza datos de los proyectos de ley presentados en el Congreso del Perú desde su plataforma oficial: [https://wb2server.congreso.gob.pe/spley-portal/#/expediente/search](https://wb2server.congreso.gob.pe/spley-portal/#/expediente/search)

## 🚀 Características Principales

### ✨ Versión 2.0 - Mejorada
- **🚀 Scraping Avanzado**: Extracción automática con Selenium y BeautifulSoup con manejo robusto de errores.
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

### 8. Configurar notificaciones (Opcional)
```bash
# Editar configuración de notificaciones
nano config/notifications.json

# Probar notificaciones
python cli.py notify --test
```

### 9. Usar el dashboard
```bash
# Ver dashboard en consola
make dashboard

# Generar dashboard HTML
make dashboard-html
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
- **Sistema de Métricas**: Recolección automática de métricas de rendimiento y calidad

### 📊 Sistema de Métricas y Reportes
- **Recolección Automática**: Métricas de sesiones, rendimiento y calidad de datos
- **Análisis de Tendencias**: Seguimiento de patrones de uso y rendimiento
- **Reportes Ejecutivos**: Generación automática de resúmenes para stakeholders
- **Dashboard de Métricas**: Visualización en tiempo real del estado del sistema
- **Exportación Avanzada**: Reportes en JSON, HTML y CSV para análisis externos

### 🚨 Sistema de Alertas Inteligentes
- **Umbrales Configurables**: Alertas personalizables por tipo de métrica
- **Múltiples Canales**: Notificaciones por email, Slack, Discord y Teams
- **Cooldown Inteligente**: Prevención de spam de alertas
- **Severidad Graduada**: Alertas críticas, altas, medias y bajas
- **Resolución Manual**: Sistema para marcar alertas como resueltas

### 🌐 Dashboard Web Interactivo
- **Monitoreo en Tiempo Real**: Estado del sistema actualizado automáticamente
- **API REST Completa**: Endpoints para todas las funcionalidades
- **Visualizaciones Interactivas**: Gráficos con Plotly para análisis dinámico
- **Responsive Design**: Accesible desde cualquier dispositivo
- **Exportación Directa**: Descarga de datos en múltiples formatos

### 📤 Exportación Multi-Formato
- **Formatos Soportados**: CSV, Excel, JSON, HTML, XML, SQL, Parquet, ZIP
- **Exportación Múltiple**: Varios formatos simultáneamente
- **Optimización Automática**: Recomendaciones de formato según el tamaño de datos
- **Hojas de Resumen**: Información estadística incluida en Excel
- **Compresión ZIP**: Múltiples archivos empaquetados

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
make metrics-summary   # Mostrar resumen de métricas
make metrics-export    # Exportar reporte de métricas
make report-executive  # Generar resumen ejecutivo
make report-analytics  # Generar reporte de análisis
make report-metrics    # Generar reporte de métricas
make alerts-list       # Listar alertas activas
make alerts-summary    # Mostrar resumen de alertas
make alerts-export     # Exportar alertas a archivo
make export-csv        # Exportar datos a CSV
make export-multiple   # Exportar datos en múltiples formatos
make dashboard         # Mostrar dashboard en consola
make dashboard-html    # Generar dashboard HTML
make dashboard-web     # Iniciar dashboard web
make notify-test       # Probar sistema de notificaciones
```

### 📊 Scripts de Análisis (`scripts/`)
- **`run_analysis.py`**: Análisis completo automatizado con exportación de resultados
- **`health_check.py`**: Verificación de salud del proyecto y estructura

### 📈 Sistema de Métricas y Reportes (`utils/`)
- **`metrics_collector.py`**: Recolección avanzada de métricas de rendimiento y calidad
- **`report_generator.py`**: Generación automática de reportes ejecutivos y analíticos
- **`alert_system.py`**: Sistema de alertas inteligentes con umbrales configurables
- **`data_exporter.py`**: Exportación de datos en múltiples formatos (CSV, Excel, JSON, HTML, XML, SQL, Parquet)

### 🌐 Dashboard Web Interactivo
- **`web_dashboard.py`**: Dashboard web con Flask para monitoreo en tiempo real
- **API REST**: Endpoints para métricas, alertas, datos y gráficos
- **Visualizaciones**: Gráficos interactivos con Plotly
- **Monitoreo**: Estado del sistema, alertas activas y métricas en tiempo real

### 📓 Notebook Mejorado (`notebooks/analisis.ipynb`)
- **Validación automática**: Verificación de calidad de datos integrada
- **Exportación avanzada**: Generación automática de reportes HTML y JSON
- **Análisis interactivo**: Visualizaciones mejoradas con Plotly
- **Reportes automáticos**: Generación de reportes HTML profesionales

### 🔔 Sistema de Notificaciones (`utils/notifications.py`)
- **Múltiples canales**: Email, Slack, Telegram
- **Notificaciones automáticas**: Inicio, finalización y errores de scraping
- **Configuración flexible**: JSON configuración para diferentes canales
- **Pruebas integradas**: Sistema de testing de notificaciones

### 📊 Dashboard de Monitoreo (`dashboard.py`)
- **Estado en tiempo real**: Monitoreo del estado del proyecto
- **Métricas visuales**: Estadísticas de datos y rendimiento
- **Dashboard HTML**: Interfaz web interactiva con auto-actualización
- **Logs en vivo**: Visualización de logs recientes con colores

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

## 🆕 Funcionalidades Avanzadas v3.0

### 🚨 Sistema de Alertas Inteligentes

El sistema de alertas permite monitorear el rendimiento del scraper y recibir notificaciones automáticas cuando se detectan problemas.

```bash
# Gestionar alertas
python cli.py alerts --list           # Listar alertas activas
python cli.py alerts --summary        # Mostrar resumen de alertas
python cli.py alerts --resolve 0      # Resolver alerta por ID
python cli.py alerts --export alerts.json  # Exportar alertas

# Comandos Makefile
make alerts-list                       # Listar alertas activas
make alerts-summary                    # Mostrar resumen de alertas
make alerts-export                     # Exportar alertas a archivo
```

**Características:**
- Umbrales configurables por tipo de métrica
- Notificaciones por email, Slack, Discord y Teams
- Sistema de cooldown para evitar spam
- Alertas graduadas por severidad (crítica, alta, media, baja)

### 📤 Exportación Multi-Formato

Exporta tus datos en múltiples formatos para diferentes necesidades de análisis.

```bash
# Exportar en formato único
python cli.py export --input data/proyectos_ley_2024-01-15.csv --format excel
python cli.py export --input data/proyectos_ley_2024-01-15.csv --format json
python cli.py export --input data/proyectos_ley_2024-01-15.csv --format html

# Exportar en múltiples formatos
python cli.py export --input data/proyectos_ley_2024-01-15.csv --multiple --formats csv excel json html

# Comandos Makefile
make export-csv                        # Exportar a CSV
make export-multiple                   # Exportar en múltiples formatos
```

**Formatos soportados:**
- **CSV**: Para análisis en Excel o herramientas de datos
- **Excel**: Con hojas de resumen y formato profesional
- **JSON**: Para integración con APIs y aplicaciones web
- **HTML**: Reportes web con visualizaciones
- **XML**: Para sistemas legacy y intercambio de datos
- **SQL**: Scripts de inserción para bases de datos
- **Parquet**: Formato optimizado para big data
- **ZIP**: Múltiples formatos empaquetados

### 🌐 Dashboard Web Interactivo

Dashboard web completo para monitoreo en tiempo real del sistema.

```bash
# Iniciar dashboard web
python cli.py dashboard --port 5000 --host 0.0.0.0

# Comando Makefile
make dashboard-web                     # Iniciar dashboard web en puerto 5000

# Acceder al dashboard
# http://localhost:5000 - Dashboard principal
# http://localhost:5000/api/status - API de estado
# http://localhost:5000/api/metrics - API de métricas
# http://localhost:5000/api/alerts - API de alertas
```

**Características:**
- Monitoreo en tiempo real del estado del sistema
- Gráficos interactivos con Plotly
- API REST completa para integración
- Responsive design para móviles y tablets
- Exportación directa de datos desde la interfaz

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## ✍️ Autor(es)

**Benjamin Oscco Arias**
- GitHub: [@ben1998pe](https://github.com/ben1998pe)
- LinkedIn: [Benjamin Oscco](https://linkedin.com/in/benjamin-oscco)

## 🙏 Agradecimientos

- Al Congreso del Perú por proporcionar acceso público a los datos
- A la comunidad de Python por las excelentes librerías utilizadas
- A todos los contribuidores del proyecto

---

**⚠️ Nota Legal**: Este proyecto es solo para fines educativos y de investigación. Respete los términos de uso del sitio web del Congreso del Perú.
