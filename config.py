"""
Configuración del scraper de proyectos de ley del Congreso del Perú
"""
import os
from datetime import datetime, timedelta

# =========================
# CONFIGURACIÓN GENERAL
# =========================
BASE_URL = "https://wb2server.congreso.gob.pe/spley-portal/#/expediente/search"
DATA_DIR = "data"
LOG_DIR = "logs"

# =========================
# CONFIGURACIÓN DEL NAVEGADOR
# =========================
CHROME_OPTIONS = [
    "--start-maximized",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-blink-features=AutomationControlled",
    "--disable-extensions",
    "--disable-plugins",
    "--disable-images",  # Para acelerar la carga
]

# =========================
# SELECTORES CSS/XPath
# =========================
SELECTORS = {
    "filtros_btn": '//button[.//i[contains(@class, "pi-filter")]]',
    "fecha_desde": '//input[@placeholder="Seleccionar desde"]',
    "fecha_hasta": '//input[@placeholder="Seleccionar hasta"]',
    "buscar_btn": '//button[.//i[contains(@class, "pi-filter")] and .//span[contains(text(), "Buscar")]]',
    "tabla_filas": "tbody.p-datatable-tbody > tr",
    "paginacion": '//button[contains(@class, "p-paginator-page")]',
    "siguiente_pagina": '//button[@class="p-paginator-next p-paginator-element p-link"]',
}

# =========================
# CONFIGURACIÓN DE SCRAPING
# =========================
WAIT_TIMEOUT = 15
PAGE_LOAD_DELAY = 3
SEARCH_DELAY = 5
MAX_RETRIES = 3
RETRY_DELAY = 2

# =========================
# CONFIGURACIÓN DE FECHAS
# =========================
DEFAULT_DATE_RANGE = 7  # días hacia atrás por defecto
DATE_FORMAT = "%d/%m/%Y"
CSV_DATE_FORMAT = "%Y-%m-%d"

# =========================
# CONFIGURACIÓN DE LOGGING
# =========================
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = os.path.join(LOG_DIR, f"scraper_{datetime.now().strftime('%Y%m%d')}.log")

# =========================
# CONFIGURACIÓN DE DATOS
# =========================
CSV_ENCODING = "utf-8-sig"
CSV_SEPARATOR = ","
INCLUDE_INDEX = False

# =========================
# CAMPOS A EXTRAER
# =========================
FIELDS = [
    "proyecto",
    "fecha",
    "titulo", 
    "estado",
    "proponente",
    "autores"
]

# =========================
# CONFIGURACIÓN DE ANÁLISIS
# =========================
ANALYSIS_DIR = "analysis"
VISUALIZATIONS_DIR = "visualizations"
REPORTS_DIR = "reports"

# Crear directorios si no existen
for directory in [DATA_DIR, LOG_DIR, ANALYSIS_DIR, VISUALIZATIONS_DIR, REPORTS_DIR]:
    os.makedirs(directory, exist_ok=True)
