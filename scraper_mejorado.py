"""
Scraper mejorado para proyectos de ley del Congreso del Perú
Incluye manejo de fechas, paginación, logging y mejor parsing
"""
import logging
import re
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
from tqdm import tqdm
import config

# =========================
# CONFIGURACIÓN DE LOGGING
# =========================
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CongresoScraper:
    """Clase principal para el scraping de proyectos de ley"""
    
    def __init__(self, headless: bool = False):
        self.driver = None
        self.wait = None
        self.headless = headless
        self.setup_driver()
    
    def setup_driver(self):
        """Configura el driver de Chrome"""
        try:
            options = Options()
            for option in config.CHROME_OPTIONS:
                options.add_argument(option)
            
            if self.headless:
                options.add_argument("--headless")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.wait = WebDriverWait(self.driver, config.WAIT_TIMEOUT)
            logger.info("✅ Driver de Chrome configurado correctamente")
        except Exception as e:
            logger.error(f"❌ Error configurando driver: {e}")
            raise
    
    def navigate_to_page(self) -> bool:
        """Navega a la página del Congreso"""
        try:
            logger.info(f"🌐 Navegando a: {config.BASE_URL}")
            self.driver.get(config.BASE_URL)
            time.sleep(config.PAGE_LOAD_DELAY)
            logger.info("✅ Página cargada correctamente")
            return True
        except Exception as e:
            logger.error(f"❌ Error navegando a la página: {e}")
            return False
    
    def open_advanced_filters(self) -> bool:
        """Abre los filtros avanzados"""
        try:
            btn_filtros = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, config.SELECTORS["filtros_btn"])
            ))
            btn_filtros.click()
            logger.info("✅ Filtros avanzados abiertos")
            time.sleep(2)
            return True
        except TimeoutException:
            logger.error("❌ Timeout esperando botón de filtros")
            return False
        except Exception as e:
            logger.error(f"❌ Error abriendo filtros: {e}")
            return False
    
    def set_date_range(self, fecha_desde: str, fecha_hasta: str) -> bool:
        """Establece el rango de fechas"""
        try:
            # Fecha desde
            input_desde = self.wait.until(EC.presence_of_element_located(
                (By.XPATH, config.SELECTORS["fecha_desde"])
            ))
            input_desde.clear()
            input_desde.send_keys(fecha_desde)
            
            # Fecha hasta
            input_hasta = self.wait.until(EC.presence_of_element_located(
                (By.XPATH, config.SELECTORS["fecha_hasta"])
            ))
            input_hasta.clear()
            input_hasta.send_keys(fecha_hasta)
            
            logger.info(f"✅ Fechas establecidas: {fecha_desde} - {fecha_hasta}")
            time.sleep(2)
            return True
        except Exception as e:
            logger.error(f"❌ Error estableciendo fechas: {e}")
            return False
    
    def search_projects(self) -> bool:
        """Ejecuta la búsqueda de proyectos"""
        try:
            btn_buscar = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, config.SELECTORS["buscar_btn"])
            ))
            btn_buscar.click()
            logger.info("✅ Búsqueda ejecutada")
            time.sleep(config.SEARCH_DELAY)
            return True
        except Exception as e:
            logger.error(f"❌ Error ejecutando búsqueda: {e}")
            return False
    
    def extract_project_data(self, row) -> Optional[Dict]:
        """Extrae datos de una fila de proyecto"""
        try:
            columns = row.find_all("td")
            if len(columns) < 6:
                return None
            
            # Proyecto
            proyecto_text = columns[0].text.strip()
            proyecto_match = re.search(r'Proyecto de Ley (\d+/\d+-\w+)', proyecto_text)
            proyecto = proyecto_match.group(1) if proyecto_match else proyecto_text
            
            # Fecha
            fecha_text = columns[1].text.strip()
            fecha_match = re.search(r'(\d{2}/\d{2}/\d{4})', fecha_text)
            fecha = fecha_match.group(1) if fecha_match else fecha_text
            
            # Título
            titulo_elem = columns[2].find("span", class_="ellipsis")
            titulo = titulo_elem.text.strip() if titulo_elem else columns[2].text.strip()
            
            # Estado
            estado_text = columns[3].text.strip()
            estado_match = re.search(r'([A-ZÁÉÍÓÚÑ\s]+)', estado_text)
            estado = estado_match.group(1).strip() if estado_match else estado_text
            
            # Proponente
            proponente_text = columns[4].text.strip()
            proponente_match = re.search(r'([A-ZÁÉÍÓÚÑ\s]+)', proponente_text)
            proponente = proponente_match.group(1).strip() if proponente_match else proponente_text
            
            # Autores
            autores_elem = columns[5].find_all("li")
            autores = [a.text.strip() for a in autores_elem]
            autores_str = ", ".join(autores)
            
            return {
                "proyecto": proyecto,
                "fecha": fecha,
                "titulo": titulo,
                "estado": estado,
                "proponente": proponente,
                "autores": autores_str
            }
        except Exception as e:
            logger.warning(f"⚠️ Error extrayendo datos de fila: {e}")
            return None
    
    def scrape_current_page(self) -> List[Dict]:
        """Scraping de la página actual"""
        try:
            html = self.driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            rows = soup.select(config.SELECTORS["tabla_filas"])
            
            proyectos = []
            for row in rows:
                proyecto_data = self.extract_project_data(row)
                if proyecto_data:
                    proyectos.append(proyecto_data)
            
            logger.info(f"📊 Extraídos {len(proyectos)} proyectos de la página actual")
            return proyectos
        except Exception as e:
            logger.error(f"❌ Error scraping página actual: {e}")
            return []
    
    def has_next_page(self) -> bool:
        """Verifica si hay página siguiente"""
        try:
            next_btn = self.driver.find_element(By.XPATH, config.SELECTORS["siguiente_pagina"])
            return next_btn.is_enabled() and not next_btn.get_attribute("aria-disabled") == "true"
        except NoSuchElementException:
            return False
        except Exception as e:
            logger.warning(f"⚠️ Error verificando página siguiente: {e}")
            return False
    
    def go_to_next_page(self) -> bool:
        """Va a la página siguiente"""
        try:
            next_btn = self.driver.find_element(By.XPATH, config.SELECTORS["siguiente_pagina"])
            next_btn.click()
            time.sleep(config.SEARCH_DELAY)
            logger.info("➡️ Navegando a página siguiente")
            return True
        except Exception as e:
            logger.error(f"❌ Error navegando a página siguiente: {e}")
            return False
    
    def scrape_all_pages(self) -> List[Dict]:
        """Scraping de todas las páginas"""
        all_proyectos = []
        page_num = 1
        
        while True:
            logger.info(f"📄 Procesando página {page_num}")
            proyectos_pagina = self.scrape_current_page()
            all_proyectos.extend(proyectos_pagina)
            
            if not self.has_next_page():
                break
            
            if not self.go_to_next_page():
                break
            
            page_num += 1
        
        logger.info(f"✅ Scraping completado. Total: {len(all_proyectos)} proyectos")
        return all_proyectos
    
    def save_to_csv(self, proyectos: List[Dict], filename: Optional[str] = None) -> str:
        """Guarda los datos en CSV"""
        try:
            df = pd.DataFrame(proyectos)
            
            if filename is None:
                fecha_archivo = datetime.now().strftime(config.CSV_DATE_FORMAT)
                filename = f"{config.DATA_DIR}/proyectos_ley_{fecha_archivo}.csv"
            
            df.to_csv(filename, index=config.INCLUDE_INDEX, 
                     encoding=config.CSV_ENCODING, sep=config.CSV_SEPARATOR)
            
            logger.info(f"💾 Datos guardados en: {filename}")
            logger.info(f"📊 Total de registros: {len(df)}")
            return filename
        except Exception as e:
            logger.error(f"❌ Error guardando CSV: {e}")
            raise
    
    def scrape(self, fecha_desde: Optional[str] = None, 
               fecha_hasta: Optional[str] = None) -> List[Dict]:
        """Método principal de scraping"""
        try:
            # Configurar fechas
            if fecha_desde is None:
                fecha_desde = datetime.now().strftime(config.DATE_FORMAT)
            if fecha_hasta is None:
                fecha_hasta = datetime.now().strftime(config.DATE_FORMAT)
            
            logger.info(f"🚀 Iniciando scraping: {fecha_desde} - {fecha_hasta}")
            
            # Navegar y configurar
            if not self.navigate_to_page():
                return []
            
            if not self.open_advanced_filters():
                return []
            
            if not self.set_date_range(fecha_desde, fecha_hasta):
                return []
            
            if not self.search_projects():
                return []
            
            # Scraping
            proyectos = self.scrape_all_pages()
            
            return proyectos
            
        except Exception as e:
            logger.error(f"❌ Error en scraping: {e}")
            return []
        finally:
            self.close()
    
    def close(self):
        """Cierra el driver"""
        if self.driver:
            self.driver.quit()
            logger.info("👋 Driver cerrado")

def main():
    """Función principal"""
    # Configurar fechas (últimos 7 días por defecto)
    fecha_hasta = datetime.now()
    fecha_desde = fecha_hasta - timedelta(days=config.DEFAULT_DATE_RANGE)
    
    fecha_desde_str = fecha_desde.strftime(config.DATE_FORMAT)
    fecha_hasta_str = fecha_hasta.strftime(config.DATE_FORMAT)
    
    # Crear scraper
    scraper = CongresoScraper(headless=False)
    
    try:
        # Ejecutar scraping
        proyectos = scraper.scrape(fecha_desde_str, fecha_hasta_str)
        
        if proyectos:
            # Guardar datos
            filename = scraper.save_to_csv(proyectos)
            
            # Mostrar resumen
            df = pd.DataFrame(proyectos)
            print(f"\n📊 RESUMEN DEL SCRAPING")
            print(f"📅 Período: {fecha_desde_str} - {fecha_hasta_str}")
            print(f"📄 Total proyectos: {len(proyectos)}")
            print(f"💾 Archivo: {filename}")
            print(f"\n🔍 PRIMEROS 5 PROYECTOS:")
            print(df.head().to_string(index=False))
        else:
            print("❌ No se encontraron proyectos")
            
    except Exception as e:
        logger.error(f"❌ Error en main: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
