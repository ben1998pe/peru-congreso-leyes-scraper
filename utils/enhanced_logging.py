"""
Sistema de logging mejorado para el Peru Congress Laws Scraper
"""
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import json
import sys
import traceback
from functools import wraps


class ColoredFormatter(logging.Formatter):
    """Formateador de logs con colores para consola"""
    
    # Códigos de color ANSI
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Verde
        'WARNING': '\033[33m',    # Amarillo
        'ERROR': '\033[31m',      # Rojo
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Agregar color al nivel de log
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


class JSONFormatter(logging.Formatter):
    """Formateador JSON para logs estructurados"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Agregar información de excepción si existe
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Agregar campos extra si existen
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry, ensure_ascii=False, indent=2)


class EnhancedLogger:
    """Logger mejorado con funcionalidades avanzadas"""
    
    def __init__(self, name: str, log_dir: str = "logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Evitar duplicar handlers
        if self.logger.handlers:
            return
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Configurar handlers de logging"""
        
        # Handler para consola con colores
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = ColoredFormatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # Handler para archivo con rotación
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(module)s:%(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Handler para archivo JSON (logs estructurados)
        json_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / f"{self.name}_structured_{datetime.now().strftime('%Y%m%d')}.json",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        json_handler.setLevel(logging.INFO)
        json_formatter = JSONFormatter()
        json_handler.setFormatter(json_formatter)
        self.logger.addHandler(json_handler)
    
    def log_with_context(self, level: int, message: str, **context):
        """Log con contexto adicional"""
        extra_fields = {'context': context} if context else {}
        self.logger.log(level, message, extra={'extra_fields': extra_fields})
    
    def log_performance(self, operation: str, duration: float, **metrics):
        """Log específico para métricas de rendimiento"""
        context = {
            'operation': operation,
            'duration_seconds': duration,
            'metrics': metrics
        }
        self.log_with_context(logging.INFO, f"Performance: {operation} completed in {duration:.2f}s", **context)
    
    def log_data_quality(self, total_records: int, valid_records: int, **quality_metrics):
        """Log específico para calidad de datos"""
        quality_score = (valid_records / total_records * 100) if total_records > 0 else 0
        context = {
            'total_records': total_records,
            'valid_records': valid_records,
            'quality_score': quality_score,
            'quality_metrics': quality_metrics
        }
        self.log_with_context(
            logging.INFO, 
            f"Data Quality: {valid_records}/{total_records} records valid ({quality_score:.1f}%)",
            **context
        )
    
    def log_scraping_session(self, session_id: str, **session_data):
        """Log específico para sesiones de scraping"""
        context = {
            'session_id': session_id,
            'session_data': session_data
        }
        self.log_with_context(logging.INFO, f"Scraping session {session_id} started", **context)
    
    def log_error_with_context(self, error: Exception, operation: str, **context):
        """Log de error con contexto detallado"""
        error_context = {
            'operation': operation,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context
        }
        self.log_with_context(logging.ERROR, f"Error in {operation}: {error}", **error_context)
    
    def get_logger(self):
        """Obtener el logger estándar"""
        return self.logger


def log_execution_time(operation_name: str = None):
    """Decorator para loggear tiempo de ejecución"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = EnhancedLogger(func.__module__)
            start_time = datetime.now()
            
            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                logger.log_performance(operation_name or func.__name__, duration)
                return result
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                logger.log_error_with_context(e, operation_name or func.__name__)
                raise
        return wrapper
    return decorator


def get_enhanced_logger(name: str) -> EnhancedLogger:
    """Obtener instancia del logger mejorado"""
    return EnhancedLogger(name)


# Funciones de conveniencia
def setup_logging(name: str = "scraper") -> EnhancedLogger:
    """Configurar logging mejorado"""
    return EnhancedLogger(name)


def log_scraping_progress(current: int, total: int, operation: str = "scraping"):
    """Log de progreso de scraping"""
    logger = get_enhanced_logger("scraper")
    progress = (current / total * 100) if total > 0 else 0
    logger.log_with_context(
        logging.INFO,
        f"Progress: {current}/{total} ({progress:.1f}%) - {operation}",
        current=current,
        total=total,
        progress_percent=progress,
        operation=operation
    )


if __name__ == "__main__":
    # Prueba del sistema de logging mejorado
    logger = setup_logging("test")
    
    # Log básico
    logger.get_logger().info("Test de logging básico")
    
    # Log con contexto
    logger.log_with_context(logging.INFO, "Test con contexto", user_id=123, action="test")
    
    # Log de rendimiento
    logger.log_performance("test_operation", 1.23, records_processed=100)
    
    # Log de calidad de datos
    logger.log_data_quality(100, 95, duplicates=2, missing=3)
    
    # Log de sesión
    logger.log_scraping_session("test_session_123", pages_scraped=5, projects_found=50)
    
    print("✅ Test de logging completado")
