"""
Advanced logging configuration for the Peru Congress Laws Scraper
"""
import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
import traceback


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Add color to level name
        if hasattr(record, 'levelname'):
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


class ScrapingLogger:
    """Enhanced logger for scraping operations"""
    
    def __init__(self, name: str = "congreso_scraper", 
                 log_dir: Optional[Path] = None,
                 level: str = "INFO"):
        self.name = name
        self.log_dir = log_dir or Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Setup handlers
        self._setup_console_handler()
        self._setup_file_handler()
        self._setup_error_handler()
    
    def _setup_console_handler(self):
        """Setup console handler with colors"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Use colored formatter for console
        formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def _setup_file_handler(self):
        """Setup rotating file handler"""
        log_file = self.log_dir / f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log"
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Use standard formatter for file
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def _setup_error_handler(self):
        """Setup separate error file handler"""
        error_file = self.log_dir / f"{self.name}_errors_{datetime.now().strftime('%Y%m%d')}.log"
        
        error_handler = logging.handlers.RotatingFileHandler(
            error_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s\n%(pathname)s:%(lineno)d\n',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)
    
    def get_logger(self):
        """Get the configured logger"""
        return self.logger
    
    def log_scraping_start(self, url: str, date_range: tuple):
        """Log scraping start with parameters"""
        self.logger.info("🚀 Iniciando scraping")
        self.logger.info(f"🌐 URL: {url}")
        self.logger.info(f"📅 Rango de fechas: {date_range[0]} - {date_range[1]}")
    
    def log_scraping_progress(self, page: int, total_pages: int, projects_found: int):
        """Log scraping progress"""
        self.logger.info(f"📄 Página {page}/{total_pages} - {projects_found} proyectos encontrados")
    
    def log_scraping_complete(self, total_projects: int, duration: float):
        """Log scraping completion"""
        self.logger.info(f"✅ Scraping completado")
        self.logger.info(f"📊 Total proyectos: {total_projects}")
        self.logger.info(f"⏱️ Duración: {duration:.2f} segundos")
    
    def log_error_with_traceback(self, error: Exception, context: str = ""):
        """Log error with full traceback"""
        self.logger.error(f"❌ Error en {context}: {str(error)}")
        self.logger.error(f"📋 Traceback:\n{traceback.format_exc()}")
    
    def log_performance_metrics(self, metrics: dict):
        """Log performance metrics"""
        self.logger.info("📈 Métricas de rendimiento:")
        for key, value in metrics.items():
            self.logger.info(f"   {key}: {value}")


def get_logger(name: str = "congreso_scraper", level: str = "INFO") -> logging.Logger:
    """Get a configured logger instance"""
    scraper_logger = ScrapingLogger(name, level=level)
    return scraper_logger.get_logger()


def log_function_call(func):
    """Decorator to log function calls"""
    def wrapper(*args, **kwargs):
        logger = get_logger()
        logger.debug(f"🔧 Llamando función: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"✅ Función {func.__name__} completada exitosamente")
            return result
        except Exception as e:
            logger.error(f"❌ Error en función {func.__name__}: {e}")
            raise
    return wrapper


def log_execution_time(func):
    """Decorator to log function execution time"""
    def wrapper(*args, **kwargs):
        import time
        logger = get_logger()
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"⏱️ {func.__name__} ejecutado en {execution_time:.2f} segundos")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ {func.__name__} falló después de {execution_time:.2f} segundos: {e}")
            raise
    return wrapper
