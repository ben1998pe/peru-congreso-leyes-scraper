"""
Environment configuration management for the Peru Congress Laws Scraper
"""
import os
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    """Database configuration"""
    enabled: bool = False
    host: str = "localhost"
    port: int = 5432
    name: str = "congreso_leyes"
    user: str = "postgres"
    password: str = ""


@dataclass
class ScrapingConfig:
    """Scraping configuration"""
    max_pages: int = 50
    max_retries: int = 3
    retry_delay: float = 2.0
    page_load_timeout: int = 30
    element_wait_timeout: int = 15
    request_delay: float = 1.0
    concurrent_requests: int = 1
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_max_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    console_output: bool = True


class Environment:
    """Environment configuration manager"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.data_dir = self.project_root / "data"
        self.logs_dir = self.project_root / "logs"
        self.reports_dir = self.project_root / "reports"
        self.analysis_dir = self.project_root / "analysis"
        self.visualizations_dir = self.project_root / "visualizations"
        
        # Create directories if they don't exist
        for directory in [self.data_dir, self.logs_dir, self.reports_dir, 
                         self.analysis_dir, self.visualizations_dir]:
            directory.mkdir(exist_ok=True)
        
        # Load configuration
        self._load_config()
    
    def _load_config(self):
        """Load configuration from environment variables or defaults"""
        self.database = DatabaseConfig(
            enabled=os.getenv("DB_ENABLED", "false").lower() == "true",
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            name=os.getenv("DB_NAME", "congreso_leyes"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "")
        )
        
        self.scraping = ScrapingConfig(
            max_pages=int(os.getenv("MAX_PAGES", "50")),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            retry_delay=float(os.getenv("RETRY_DELAY", "2.0")),
            page_load_timeout=int(os.getenv("PAGE_LOAD_TIMEOUT", "30")),
            element_wait_timeout=int(os.getenv("ELEMENT_WAIT_TIMEOUT", "15")),
            request_delay=float(os.getenv("REQUEST_DELAY", "1.0")),
            concurrent_requests=int(os.getenv("CONCURRENT_REQUESTS", "1")),
            user_agent=os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        )
        
        self.logging = LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO"),
            format=os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            file_max_size=int(os.getenv("LOG_FILE_MAX_SIZE", str(10 * 1024 * 1024))),
            backup_count=int(os.getenv("LOG_BACKUP_COUNT", "5")),
            console_output=os.getenv("LOG_CONSOLE_OUTPUT", "true").lower() == "true"
        )
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get all configuration as a dictionary"""
        return {
            "project_root": str(self.project_root),
            "data_dir": str(self.data_dir),
            "logs_dir": str(self.logs_dir),
            "reports_dir": str(self.reports_dir),
            "analysis_dir": str(self.analysis_dir),
            "visualizations_dir": str(self.visualizations_dir),
            "database": self.database.__dict__,
            "scraping": self.scraping.__dict__,
            "logging": self.logging.__dict__
        }


# Global environment instance
env = Environment()
