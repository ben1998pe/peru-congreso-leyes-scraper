# 📜 Scraper de Proyectos de Ley - Congreso del Perú 🇵🇪

Este proyecto extrae, limpia y analiza datos de los proyectos de ley presentados en el Congreso del Perú desde su plataforma oficial: [https://wb2server.congreso.gob.pe/spley-portal/#/expediente/search](https://wb2server.congreso.gob.pe/spley-portal/#/expediente/search)

## 🚀 Características Principales

- **Web Scraping Avanzado**: Extracción automática con Selenium y BeautifulSoup
- **Limpieza de Datos**: Normalización y enriquecimiento de información
- **Análisis Exploratorio**: Visualizaciones interactivas con Plotly
- **Configuración Flexible**: Rango de fechas personalizable y paginación automática
- **Logging Completo**: Monitoreo y debugging detallado
- **Exportación Múltiple**: CSV, análisis y reportes automáticos

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
├── 📄 scraper.py              # Scraper original (básico)
├── 📄 scraper_mejorado.py     # Scraper mejorado con todas las funcionalidades
├── 📄 config.py               # Configuración centralizada
├── 📄 ejemplo_uso.py          # Ejemplos de uso y menú interactivo
├── 📄 requirements.txt        # Dependencias del proyecto
├── 📁 data/                   # Datos extraídos (CSV)
│   ├── proyectos_ley_*.csv
│   └── proyectos_ley_limpios_*.csv
├── 📁 notebooks/              # Análisis exploratorio
│   └── analisis.ipynb
├── 📁 utils/                  # Funciones auxiliares
│   └── limpieza.py
├── 📁 analysis/               # Reportes y análisis
├── 📁 visualizations/         # Gráficos exportados
├── 📁 logs/                   # Archivos de log
└── 📄 chromedriver.exe        # Driver de Chrome
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
