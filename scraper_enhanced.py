"""
Enhanced scraper for Peru Congress Laws with advanced error handling, 
performance monitoring, and data validation
"""
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, WebDriverException,
    ElementClickInterceptedException, StaleElementReferenceException
)
from bs4 import BeautifulSoup
from tqdm import tqdm
import requests
from urllib.parse import urljoin, urlparse

# Import our enhanced utilities
from utils.logging_config import get_logger, log_execution_time, PerformanceProfiler
from utils.data_validator import DataValidator
from utils.performance_monitor import PerformanceMonitor
from utils.notifications import get_notification_manager
from config.environment import env


class EnhancedCongresoScraper:
    """Enhanced scraper with advanced error handling and monitoring"""
    
    def __init__(self, headless: bool = True, enable_monitoring: bool = True):
        self.headless = headless
        self.enable_monitoring = enable_monitoring
        
        # Setup logging
        self.logger = get_logger("enhanced_scraper")
        
        # Initialize components
        self.driver = None
        self.wait = None
        self.validator = DataValidator()
        self.performance_monitor = PerformanceMonitor() if enable_monitoring else None
        self.notification_manager = get_notification_manager()
        
        # Configuration
        self.base_url = "https://wb2server.congreso.gob.pe/spley-portal/#/expediente/search"
        self.max_retries = env.scraping.max_retries
        self.retry_delay = env.scraping.retry_delay
        self.request_delay = env.scraping.request_delay
        
        # Statistics
        self.stats = {
            'pages_scraped': 0,
            'projects_found': 0,
            'errors_encountered': 0,
            'retries_performed': 0,
            'start_time': None,
            'end_time': None
        }
        
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver with enhanced configuration"""
        try:
            options = Options()
            
            # Basic options
            options.add_argument("--start-maximized")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-images")
            options.add_argument("--disable-javascript")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-web-security")
            options.add_argument("--allow-running-insecure-content")
            
            # User agent
            options.add_argument(f"--user-agent={env.scraping.user_agent}")
            
            # Performance options
            options.add_argument("--memory-pressure-off")
            options.add_argument("--max_old_space_size=4096")
            
            if self.headless:
                options.add_argument("--headless")
            
            # Setup service
            service = Service(ChromeDriverManager().install())
            
            # Create driver
            self.driver = webdriver.Chrome(service=service, options=options)
            self.wait = WebDriverWait(self.driver, env.scraping.element_wait_timeout)
            
            # Set timeouts
            self.driver.set_page_load_timeout(env.scraping.page_load_timeout)
            self.driver.implicitly_wait(10)
            
            self.logger.info("✅ Enhanced Chrome driver configured successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Error setting up driver: {e}")
            raise
    
    def _safe_navigate(self, url: str, max_retries: int = None) -> bool:
        """Safely navigate to URL with retries"""
        max_retries = max_retries or self.max_retries
        
        for attempt in range(max_retries):
            try:
                self.driver.get(url)
                time.sleep(self.request_delay)
                return True
                
            except TimeoutException:
                self.logger.warning(f"⏰ Timeout navigating to {url} (attempt {attempt + 1})")
                if attempt < max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    
            except WebDriverException as e:
                self.logger.warning(f"🌐 WebDriver error navigating to {url} (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    
            except Exception as e:
                self.logger.error(f"❌ Unexpected error navigating to {url}: {e}")
                break
        
        return False
    
    def _safe_find_element(self, by: By, value: str, timeout: int = None) -> Optional[Any]:
        """Safely find element with error handling"""
        try:
            timeout = timeout or env.scraping.element_wait_timeout
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            self.logger.warning(f"⏰ Element not found: {value}")
            return None
        except Exception as e:
            self.logger.warning(f"🔍 Error finding element {value}: {e}")
            return None
    
    def _safe_click(self, element) -> bool:
        """Safely click element with retries"""
        for attempt in range(self.max_retries):
            try:
                # Scroll element into view
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(0.5)
                
                # Try clicking
                element.click()
                return True
                
            except ElementClickInterceptedException:
                self.logger.warning(f"🖱️ Click intercepted (attempt {attempt + 1})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except StaleElementReferenceException:
                self.logger.warning(f"🔄 Stale element reference (attempt {attempt + 1})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except Exception as e:
                self.logger.warning(f"🖱️ Error clicking element: {e}")
                break
        
        return False
    
    def _safe_input(self, element, text: str) -> bool:
        """Safely input text into element"""
        try:
            element.clear()
            time.sleep(0.2)
            element.send_keys(text)
            time.sleep(0.2)
            return True
        except Exception as e:
            self.logger.warning(f"⌨️ Error inputting text: {e}")
            return False
    
    def _check_connection(self) -> bool:
        """Check internet connection"""
        try:
            response = requests.get("https://www.google.com", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _wait_for_page_load(self, timeout: int = 30):
        """Wait for page to fully load"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            time.sleep(2)  # Additional buffer
        except TimeoutException:
            self.logger.warning("⏰ Page load timeout")
    
    @log_execution_time
    def scrape(self, fecha_desde: Optional[str] = None, 
               fecha_hasta: Optional[str] = None) -> List[Dict]:
        """Main scraping method with enhanced error handling"""
        
        self.stats['start_time'] = datetime.now()
        
        # Start performance monitoring
        if self.performance_monitor:
            self.performance_monitor.start_monitoring()
        
        try:
            # Check connection
            if not self._check_connection():
                self.logger.error("❌ No internet connection")
                return []
            
            # Setup dates
            if fecha_desde is None:
                fecha_desde = datetime.now().strftime("%d/%m/%Y")
            if fecha_hasta is None:
                fecha_hasta = datetime.now().strftime("%d/%m/%Y")
            
            self.logger.info(f"🚀 Starting enhanced scraping: {fecha_desde} - {fecha_hasta}")
            
            # Notificar inicio de scraping
            self.notification_manager.notify_scraping_start((fecha_desde, fecha_hasta))
            
            # Navigate to page
            if not self._safe_navigate(self.base_url):
                self.notification_manager.notify_scraping_error("Error navegando a la página")
                return []
            
            self._wait_for_page_load()
            
            # Open filters
            if not self._open_advanced_filters():
                return []
            
            # Set date range
            if not self._set_date_range(fecha_desde, fecha_hasta):
                return []
            
            # Execute search
            if not self._execute_search():
                return []
            
            # Scrape all pages
            proyectos = self._scrape_all_pages()
            
            # Validate data
            if proyectos:
                proyectos = self._validate_scraped_data(proyectos)
            
            self.stats['end_time'] = datetime.now()
            self.stats['projects_found'] = len(proyectos)
            
            # Notificar finalización de scraping
            duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
            self.notification_manager.notify_scraping_complete(
                len(proyectos), duration, self.stats['errors_encountered']
            )
            
            self.logger.info(f"✅ Scraping completed: {len(proyectos)} projects found")
            
            return proyectos
            
        except Exception as e:
            self.logger.error(f"❌ Critical error in scraping: {e}")
            self.stats['errors_encountered'] += 1
            self.notification_manager.notify_scraping_error(str(e))
            return []
        
        finally:
            if self.performance_monitor:
                self.performance_monitor.stop_monitoring()
    
    def _open_advanced_filters(self) -> bool:
        """Open advanced filters with error handling"""
        try:
            # Try multiple selectors for the filters button
            selectors = [
                '//button[.//i[contains(@class, "pi-filter")]]',
                '//button[contains(@class, "p-button") and contains(text(), "Filtros")]',
                '//button[@aria-label="Filtros"]'
            ]
            
            for selector in selectors:
                element = self._safe_find_element(By.XPATH, selector)
                if element and self._safe_click(element):
                    time.sleep(2)
                    self.logger.info("✅ Advanced filters opened")
                    return True
            
            self.logger.error("❌ Could not open advanced filters")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error opening filters: {e}")
            return False
    
    def _set_date_range(self, fecha_desde: str, fecha_hasta: str) -> bool:
        """Set date range with error handling"""
        try:
            # Try multiple selectors for date inputs
            date_selectors = {
                'desde': [
                    '//input[@placeholder="Seleccionar desde"]',
                    '//input[contains(@id, "desde")]',
                    '//input[contains(@name, "desde")]'
                ],
                'hasta': [
                    '//input[@placeholder="Seleccionar hasta"]',
                    '//input[contains(@id, "hasta")]',
                    '//input[contains(@name, "hasta")]'
                ]
            }
            
            # Set fecha desde
            for selector in date_selectors['desde']:
                element = self._safe_find_element(By.XPATH, selector)
                if element and self._safe_input(element, fecha_desde):
                    break
            else:
                self.logger.error("❌ Could not set fecha desde")
                return False
            
            # Set fecha hasta
            for selector in date_selectors['hasta']:
                element = self._safe_find_element(By.XPATH, selector)
                if element and self._safe_input(element, fecha_hasta):
                    break
            else:
                self.logger.error("❌ Could not set fecha hasta")
                return False
            
            time.sleep(2)
            self.logger.info(f"✅ Date range set: {fecha_desde} - {fecha_hasta}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error setting date range: {e}")
            return False
    
    def _execute_search(self) -> bool:
        """Execute search with error handling"""
        try:
            # Try multiple selectors for search button
            search_selectors = [
                '//button[.//i[contains(@class, "pi-filter")] and .//span[contains(text(), "Buscar")]]',
                '//button[contains(@class, "p-button") and contains(text(), "Buscar")]',
                '//button[@type="submit"]'
            ]
            
            for selector in search_selectors:
                element = self._safe_find_element(By.XPATH, selector)
                if element and self._safe_click(element):
                    time.sleep(env.scraping.request_delay * 2)
                    self.logger.info("✅ Search executed")
                    return True
            
            self.logger.error("❌ Could not execute search")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error executing search: {e}")
            return False
    
    def _scrape_all_pages(self) -> List[Dict]:
        """Scrape all pages with enhanced error handling"""
        all_proyectos = []
        page_num = 1
        max_pages = env.scraping.max_pages
        
        with PerformanceProfiler("scrape_all_pages"):
            while page_num <= max_pages:
                self.logger.info(f"📄 Processing page {page_num}")
                
                try:
                    # Scrape current page
                    proyectos_pagina = self._scrape_current_page()
                    
                    if not proyectos_pagina:
                        self.logger.warning(f"⚠️ No projects found on page {page_num}")
                        break
                    
                    all_proyectos.extend(proyectos_pagina)
                    self.stats['pages_scraped'] += 1
                    
                    # Check for next page
                    if not self._has_next_page():
                        self.logger.info("📄 No more pages available")
                        break
                    
                    # Go to next page
                    if not self._go_to_next_page():
                        self.logger.warning("⚠️ Could not navigate to next page")
                        break
                    
                    page_num += 1
                    
                    # Add delay between pages
                    time.sleep(self.request_delay + random.uniform(0.5, 1.5))
                    
                except Exception as e:
                    self.logger.error(f"❌ Error processing page {page_num}: {e}")
                    self.stats['errors_encountered'] += 1
                    break
        
        return all_proyectos
    
    def _scrape_current_page(self) -> List[Dict]:
        """Scrape current page with enhanced parsing"""
        try:
            # Wait for table to load
            table_selector = "tbody.p-datatable-tbody > tr"
            elements = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, table_selector))
            )
            
            if not elements:
                return []
            
            # Parse HTML
            html = self.driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            rows = soup.select(table_selector)
            
            proyectos = []
            for row in rows:
                try:
                    proyecto_data = self._extract_project_data(row)
                    if proyecto_data:
                        proyectos.append(proyecto_data)
                except Exception as e:
                    self.logger.warning(f"⚠️ Error extracting project data: {e}")
                    continue
            
            self.logger.info(f"📊 Extracted {len(proyectos)} projects from current page")
            return proyectos
            
        except TimeoutException:
            self.logger.warning("⏰ Timeout waiting for table data")
            return []
        except Exception as e:
            self.logger.error(f"❌ Error scraping current page: {e}")
            return []
    
    def _extract_project_data(self, row) -> Optional[Dict]:
        """Extract project data with enhanced parsing"""
        try:
            columns = row.find_all("td")
            if len(columns) < 6:
                return None
            
            # Extract data with better error handling
            proyecto = self._extract_text_safe(columns[0])
            fecha = self._extract_text_safe(columns[1])
            titulo = self._extract_text_safe(columns[2])
            estado = self._extract_text_safe(columns[3])
            proponente = self._extract_text_safe(columns[4])
            autores = self._extract_authors_safe(columns[5])
            
            # Clean and validate data
            proyecto_clean = self._clean_proyecto(proyecto)
            fecha_clean = self._clean_fecha(fecha)
            titulo_clean = self._clean_titulo(titulo)
            estado_clean = self._clean_estado(estado)
            proponente_clean = self._clean_proponente(proponente)
            
            return {
                "proyecto": proyecto_clean,
                "fecha": fecha_clean,
                "titulo": titulo_clean,
                "estado": estado_clean,
                "proponente": proponente_clean,
                "autores": autores
            }
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error extracting project data: {e}")
            return None
    
    def _extract_text_safe(self, element) -> str:
        """Safely extract text from element"""
        try:
            if not element:
                return ""
            
            # Try to get text from span with ellipsis class
            span = element.find("span", class_="ellipsis")
            if span:
                return span.get_text(strip=True)
            
            return element.get_text(strip=True)
        except:
            return ""
    
    def _extract_authors_safe(self, element) -> str:
        """Safely extract authors from element"""
        try:
            if not element:
                return ""
            
            # Try to find list items
            li_elements = element.find_all("li")
            if li_elements:
                autores = [li.get_text(strip=True) for li in li_elements]
                return ", ".join(autores)
            
            return element.get_text(strip=True)
        except:
            return ""
    
    def _clean_proyecto(self, proyecto: str) -> str:
        """Clean project number"""
        import re
        if not proyecto:
            return ""
        
        # Extract project number pattern
        match = re.search(r'(\d+/\d{4}-\w+)', proyecto)
        return match.group(1) if match else proyecto.strip()
    
    def _clean_fecha(self, fecha: str) -> str:
        """Clean date"""
        import re
        if not fecha:
            return ""
        
        # Extract date pattern
        match = re.search(r'(\d{2}/\d{2}/\d{4})', fecha)
        return match.group(1) if match else fecha.strip()
    
    def _clean_titulo(self, titulo: str) -> str:
        """Clean title"""
        if not titulo:
            return ""
        
        # Remove extra whitespace
        import re
        return re.sub(r'\s+', ' ', titulo.strip())
    
    def _clean_estado(self, estado: str) -> str:
        """Clean state"""
        if not estado:
            return ""
        
        import re
        match = re.search(r'([A-ZÁÉÍÓÚÑ\s]+)', estado)
        return match.group(1).strip() if match else estado.strip()
    
    def _clean_proponente(self, proponente: str) -> str:
        """Clean proponent"""
        if not proponente:
            return ""
        
        import re
        match = re.search(r'([A-ZÁÉÍÓÚÑ\s]+)', proponente)
        return match.group(1).strip() if match else proponente.strip()
    
    def _has_next_page(self) -> bool:
        """Check if there's a next page"""
        try:
            next_btn = self.driver.find_element(
                By.XPATH, 
                '//button[@class="p-paginator-next p-paginator-element p-link"]'
            )
            return next_btn.is_enabled() and next_btn.get_attribute("aria-disabled") != "true"
        except NoSuchElementException:
            return False
        except Exception as e:
            self.logger.warning(f"⚠️ Error checking next page: {e}")
            return False
    
    def _go_to_next_page(self) -> bool:
        """Go to next page"""
        try:
            next_btn = self.driver.find_element(
                By.XPATH, 
                '//button[@class="p-paginator-next p-paginator-element p-link"]'
            )
            
            if self._safe_click(next_btn):
                time.sleep(env.scraping.request_delay)
                self.logger.info("➡️ Navigated to next page")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error navigating to next page: {e}")
            return False
    
    def _validate_scraped_data(self, proyectos: List[Dict]) -> List[Dict]:
        """Validate scraped data"""
        self.logger.info(f"🔍 Validating {len(proyectos)} projects")
        
        try:
            df = pd.DataFrame(proyectos)
            df_clean, validation_report = self.validator.validate_dataframe(df)
            
            # Log validation results
            self.logger.info(self.validator.get_validation_summary(validation_report))
            
            return df_clean.to_dict('records')
            
        except Exception as e:
            self.logger.error(f"❌ Error validating data: {e}")
            return proyectos
    
    def save_to_csv(self, proyectos: List[Dict], filename: Optional[str] = None) -> str:
        """Save data to CSV with enhanced error handling"""
        try:
            if not proyectos:
                raise ValueError("No projects to save")
            
            df = pd.DataFrame(proyectos)
            
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"data/proyectos_ley_enhanced_{timestamp}.csv"
            
            # Ensure directory exists
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            
            # Save with proper encoding
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            
            self.logger.info(f"💾 Data saved to: {filename}")
            self.logger.info(f"📊 Records saved: {len(df)}")
            
            return filename
            
        except Exception as e:
            self.logger.error(f"❌ Error saving CSV: {e}")
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get scraping statistics"""
        duration = None
        if self.stats['start_time'] and self.stats['end_time']:
            duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        
        stats = self.stats.copy()
        stats['duration_seconds'] = duration
        
        if self.performance_monitor:
            stats['performance_summary'] = self.performance_monitor.get_performance_summary()
        
        return stats
    
    def close(self):
        """Close driver and cleanup"""
        try:
            if self.driver:
                self.driver.quit()
                self.logger.info("👋 Driver closed")
            
            if self.performance_monitor:
                self.performance_monitor.stop_monitoring()
                
        except Exception as e:
            self.logger.error(f"❌ Error closing driver: {e}")


def main():
    """Main function for testing"""
    scraper = EnhancedCongresoScraper(headless=True, enable_monitoring=True)
    
    try:
        # Test scraping
        proyectos = scraper.scrape()
        
        if proyectos:
            filename = scraper.save_to_csv(proyectos)
            print(f"✅ Scraping completed: {len(proyectos)} projects saved to {filename}")
            
            # Print statistics
            stats = scraper.get_statistics()
            print(f"📊 Statistics: {stats}")
        else:
            print("❌ No projects found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
