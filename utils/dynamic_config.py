"""
Sistema de configuración dinámica para el Peru Congress Laws Scraper
"""
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
from datetime import datetime
import logging
from dataclasses import dataclass, asdict
import os


@dataclass
class ScrapingConfig:
    """Configuración de scraping"""
    max_retries: int = 3
    retry_delay: float = 2.0
    page_load_timeout: int = 30
    implicit_wait: int = 10
    headless: bool = True
    window_size: tuple = (1920, 1080)
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


@dataclass
class DataConfig:
    """Configuración de datos"""
    output_format: str = "csv"
    encoding: str = "utf-8-sig"
    include_metadata: bool = True
    validate_data: bool = True
    clean_data: bool = True
    backup_original: bool = True


@dataclass
class AlertConfig:
    """Configuración de alertas"""
    enabled: bool = True
    email_enabled: bool = False
    slack_enabled: bool = False
    discord_enabled: bool = False
    error_threshold: float = 10.0
    success_threshold: float = 80.0
    memory_threshold: float = 1000.0


@dataclass
class PerformanceConfig:
    """Configuración de rendimiento"""
    monitor_enabled: bool = True
    memory_limit_mb: int = 2048
    cpu_limit_percent: float = 80.0
    log_performance: bool = True
    profile_memory: bool = False


class DynamicConfigManager:
    """Gestor de configuración dinámica"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self.config_file = self.config_dir / "dynamic_config.json"
        self.env_file = self.config_dir / ".env"
        
        # Configuraciones por defecto
        self.scraping = ScrapingConfig()
        self.data = DataConfig()
        self.alerts = AlertConfig()
        self.performance = PerformanceConfig()
        
        # Cargar configuración existente
        self.load_config()
        
        # Cargar variables de entorno
        self.load_env_vars()
    
    def load_config(self):
        """Cargar configuración desde archivo"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Actualizar configuraciones
                if 'scraping' in config_data:
                    self.scraping = ScrapingConfig(**config_data['scraping'])
                
                if 'data' in config_data:
                    self.data = DataConfig(**config_data['data'])
                
                if 'alerts' in config_data:
                    self.alerts = AlertConfig(**config_data['alerts'])
                
                if 'performance' in config_data:
                    self.performance = PerformanceConfig(**config_data['performance'])
                
                logging.info(f"✅ Configuración cargada desde {self.config_file}")
                
            except Exception as e:
                logging.warning(f"Error cargando configuración: {e}")
                self.save_config()  # Crear archivo con valores por defecto
    
    def load_env_vars(self):
        """Cargar variables de entorno"""
        # Variables de scraping
        if os.getenv('SCRAPING_MAX_RETRIES'):
            self.scraping.max_retries = int(os.getenv('SCRAPING_MAX_RETRIES'))
        
        if os.getenv('SCRAPING_HEADLESS'):
            self.scraping.headless = os.getenv('SCRAPING_HEADLESS').lower() == 'true'
        
        if os.getenv('SCRAPING_TIMEOUT'):
            self.scraping.page_load_timeout = int(os.getenv('SCRAPING_TIMEOUT'))
        
        # Variables de datos
        if os.getenv('DATA_OUTPUT_FORMAT'):
            self.data.output_format = os.getenv('DATA_OUTPUT_FORMAT')
        
        if os.getenv('DATA_VALIDATE'):
            self.data.validate_data = os.getenv('DATA_VALIDATE').lower() == 'true'
        
        # Variables de alertas
        if os.getenv('ALERTS_ENABLED'):
            self.alerts.enabled = os.getenv('ALERTS_ENABLED').lower() == 'true'
        
        if os.getenv('ALERTS_EMAIL_ENABLED'):
            self.alerts.email_enabled = os.getenv('ALERTS_EMAIL_ENABLED').lower() == 'true'
        
        # Variables de rendimiento
        if os.getenv('PERFORMANCE_MONITOR'):
            self.performance.monitor_enabled = os.getenv('PERFORMANCE_MONITOR').lower() == 'true'
        
        if os.getenv('PERFORMANCE_MEMORY_LIMIT'):
            self.performance.memory_limit_mb = int(os.getenv('PERFORMANCE_MEMORY_LIMIT'))
    
    def save_config(self):
        """Guardar configuración actual"""
        config_data = {
            'scraping': asdict(self.scraping),
            'data': asdict(self.data),
            'alerts': asdict(self.alerts),
            'performance': asdict(self.performance),
            'last_updated': datetime.now().isoformat(),
            'version': '1.0.0'
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            logging.info(f"✅ Configuración guardada en {self.config_file}")
            
        except Exception as e:
            logging.error(f"Error guardando configuración: {e}")
    
    def update_scraping_config(self, **kwargs):
        """Actualizar configuración de scraping"""
        for key, value in kwargs.items():
            if hasattr(self.scraping, key):
                setattr(self.scraping, key, value)
        
        self.save_config()
        logging.info(f"✅ Configuración de scraping actualizada: {kwargs}")
    
    def update_data_config(self, **kwargs):
        """Actualizar configuración de datos"""
        for key, value in kwargs.items():
            if hasattr(self.data, key):
                setattr(self.data, key, value)
        
        self.save_config()
        logging.info(f"✅ Configuración de datos actualizada: {kwargs}")
    
    def update_alert_config(self, **kwargs):
        """Actualizar configuración de alertas"""
        for key, value in kwargs.items():
            if hasattr(self.alerts, key):
                setattr(self.alerts, key, value)
        
        self.save_config()
        logging.info(f"✅ Configuración de alertas actualizada: {kwargs}")
    
    def update_performance_config(self, **kwargs):
        """Actualizar configuración de rendimiento"""
        for key, value in kwargs.items():
            if hasattr(self.performance, key):
                setattr(self.performance, key, value)
        
        self.save_config()
        logging.info(f"✅ Configuración de rendimiento actualizada: {kwargs}")
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Obtener resumen de la configuración actual"""
        return {
            'scraping': asdict(self.scraping),
            'data': asdict(self.data),
            'alerts': asdict(self.alerts),
            'performance': asdict(self.performance),
            'config_file': str(self.config_file),
            'last_updated': datetime.now().isoformat()
        }
    
    def export_config(self, output_file: str = None) -> str:
        """Exportar configuración a archivo"""
        if output_file is None:
            output_file = f"config_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output_path = self.config_dir / output_file
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.get_config_summary(), f, indent=2, ensure_ascii=False)
        
        logging.info(f"✅ Configuración exportada a {output_path}")
        return str(output_path)
    
    def import_config(self, config_file: str) -> bool:
        """Importar configuración desde archivo"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Actualizar configuraciones
            if 'scraping' in config_data:
                self.scraping = ScrapingConfig(**config_data['scraping'])
            
            if 'data' in config_data:
                self.data = DataConfig(**config_data['data'])
            
            if 'alerts' in config_data:
                self.alerts = AlertConfig(**config_data['alerts'])
            
            if 'performance' in config_data:
                self.performance = PerformanceConfig(**config_data['performance'])
            
            self.save_config()
            logging.info(f"✅ Configuración importada desde {config_file}")
            return True
            
        except Exception as e:
            logging.error(f"Error importando configuración: {e}")
            return False
    
    def reset_to_defaults(self):
        """Resetear configuración a valores por defecto"""
        self.scraping = ScrapingConfig()
        self.data = DataConfig()
        self.alerts = AlertConfig()
        self.performance = PerformanceConfig()
        
        self.save_config()
        logging.info("✅ Configuración reseteada a valores por defecto")
    
    def create_env_template(self):
        """Crear archivo .env de ejemplo"""
        env_template = """# Configuración del Peru Congress Laws Scraper
# Copia este archivo como .env y ajusta los valores según necesites

# Configuración de Scraping
SCRAPING_MAX_RETRIES=3
SCRAPING_HEADLESS=true
SCRAPING_TIMEOUT=30

# Configuración de Datos
DATA_OUTPUT_FORMAT=csv
DATA_VALIDATE=true
DATA_CLEAN=true

# Configuración de Alertas
ALERTS_ENABLED=true
ALERTS_EMAIL_ENABLED=false
ALERTS_SLACK_ENABLED=false

# Configuración de Rendimiento
PERFORMANCE_MONITOR=true
PERFORMANCE_MEMORY_LIMIT=2048
PERFORMANCE_CPU_LIMIT=80.0

# Configuración de Notificaciones (opcional)
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR/DISCORD/WEBHOOK
"""
        
        env_file = self.config_dir / "env.template"
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_template)
        
        logging.info(f"✅ Template de variables de entorno creado: {env_file}")


def get_config_manager() -> DynamicConfigManager:
    """Obtener instancia del gestor de configuración"""
    return DynamicConfigManager()


# Funciones de conveniencia
def get_scraping_config() -> ScrapingConfig:
    """Obtener configuración de scraping"""
    manager = get_config_manager()
    return manager.scraping


def get_data_config() -> DataConfig:
    """Obtener configuración de datos"""
    manager = get_config_manager()
    return manager.data


def get_alert_config() -> AlertConfig:
    """Obtener configuración de alertas"""
    manager = get_config_manager()
    return manager.alerts


def get_performance_config() -> PerformanceConfig:
    """Obtener configuración de rendimiento"""
    manager = get_config_manager()
    return manager.performance


if __name__ == "__main__":
    # Prueba del sistema de configuración dinámica
    config_manager = DynamicConfigManager()
    
    # Mostrar configuración actual
    print("📋 Configuración actual:")
    summary = config_manager.get_config_summary()
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    
    # Actualizar configuración de scraping
    config_manager.update_scraping_config(max_retries=5, headless=False)
    
    # Crear template de variables de entorno
    config_manager.create_env_template()
    
    # Exportar configuración
    export_file = config_manager.export_config()
    print(f"✅ Configuración exportada a: {export_file}")
    
    print("✅ Test de configuración dinámica completado")
