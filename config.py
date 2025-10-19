"""
Enhanced configuration for the Peru Congress Laws Scraper
"""
import os
from datetime import datetime, timedelta
from pathlib import Path

# =========================
# CONFIGURACIÓN GENERAL
# =========================
BASE_URL = "https://wb2server.congreso.gob.pe/spley-portal/#/expediente/search"
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = PROJECT_ROOT / "logs"
ANALYSIS_DIR = PROJECT_ROOT / "analysis"
VISUALIZATIONS_DIR = PROJECT_ROOT / "visualizations"
REPORTS_DIR = PROJECT_ROOT / "reports"

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
    "--disable-javascript",  # Opcional: para mejorar rendimiento
    "--disable-gpu",
    "--disable-web-security",
    "--allow-running-insecure-content",
    "--memory-pressure-off",
    "--max_old_space_size=4096"
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
MAX_PAGES = 50
CONCURRENT_REQUESTS = 1
REQUEST_DELAY = 1.0

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
LOG_FILE = LOG_DIR / f"scraper_{datetime.now().strftime('%Y%m%d')}.log"
LOG_FILE_MAX_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

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
# CONFIGURACIÓN DE VALIDACIÓN
# =========================
VALIDATION_STRICT_MODE = False
VALIDATION_THRESHOLDS = {
    'min_title_length': 10,
    'max_title_length': 500,
    'min_authors': 1,
    'max_authors': 50,
    'date_range_years': 15  # Years back from current date
}

# =========================
# CONFIGURACIÓN DE PERFORMANCE
# =========================
PERFORMANCE_MONITORING = True
PERFORMANCE_INTERVAL = 1.0  # seconds
PERFORMANCE_THRESHOLDS = {
    'cpu_percent': 80.0,
    'memory_percent': 85.0,
    'memory_mb': 2048.0,
    'disk_io_read': 1000000,
    'disk_io_write': 1000000
}

# =========================
# CONFIGURACIÓN DE BASE DE DATOS
# =========================
DATABASE_CONFIG = {
    'enabled': False,
    'host': 'localhost',
    'port': 5432,
    'name': 'congreso_leyes',
    'user': 'postgres',
    'password': ''
}

# =========================
# CONFIGURACIÓN DE API
# =========================
API_CONFIG = {
    'enabled': False,
    'host': 'localhost',
    'port': 8000,
    'timeout': 30
}

# =========================
# CONFIGURACIÓN DE NOTIFICACIONES
# =========================
NOTIFICATION_CONFIG = {
    'enabled': False,
    'email': {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'username': '',
        'password': '',
        'to_emails': []
    },
    'slack': {
        'webhook_url': '',
        'channel': '#scraper-alerts'
    }
}

# Crear directorios si no existen
for directory in [DATA_DIR, LOG_DIR, ANALYSIS_DIR, VISUALIZATIONS_DIR, REPORTS_DIR]:
    directory.mkdir(exist_ok=True)
