"""
Test suite for the Peru Congress Laws Scraper
"""
import pytest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import os
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from scraper_enhanced import EnhancedCongresoScraper
from utils.data_validator import DataValidator, ValidationResult
from utils.limpieza import DataCleaner
from utils.logging_config import get_logger
from utils.performance_monitor import PerformanceMonitor, PerformanceProfiler


class TestDataValidator:
    """Test cases for DataValidator"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.validator = DataValidator()
    
    def test_validate_proyecto_valid(self):
        """Test valid project number validation"""
        result = self.validator.validate_proyecto("12345/2024-CR")
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert result.cleaned_data['proyecto'] == "12345/2024-CR"
    
    def test_validate_proyecto_invalid(self):
        """Test invalid project number validation"""
        result = self.validator.validate_proyecto("")
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert "requerido" in result.errors[0].lower()
    
    def test_validate_fecha_valid(self):
        """Test valid date validation"""
        result = self.validator.validate_fecha("15/06/2024")
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert result.cleaned_data['fecha'] == "15/06/2024"
    
    def test_validate_fecha_invalid(self):
        """Test invalid date validation"""
        result = self.validator.validate_fecha("32/13/2024")
        assert result.is_valid is False
        assert len(result.errors) > 0
    
    def test_validate_titulo_valid(self):
        """Test valid title validation"""
        result = self.validator.validate_titulo("Ley de Reforma Educativa")
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_titulo_short(self):
        """Test short title validation"""
        result = self.validator.validate_titulo("Ley")
        assert result.is_valid is True
        assert len(result.warnings) > 0
        assert "corto" in result.warnings[0].lower()
    
    def test_validate_estado_valid(self):
        """Test valid state validation"""
        result = self.validator.validate_estado("APROBADO")
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_autores_valid(self):
        """Test valid authors validation"""
        result = self.validator.validate_autores("Juan Pérez, María García")
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.cleaned_data['autores']) == 2
    
    def test_validate_autores_empty(self):
        """Test empty authors validation"""
        result = self.validator.validate_autores("")
        assert result.is_valid is True
        assert len(result.warnings) > 0
        assert result.cleaned_data['autores'] == []
    
    def test_validate_record_complete(self):
        """Test complete record validation"""
        record = {
            'proyecto': '12345/2024-CR',
            'fecha': '15/06/2024',
            'titulo': 'Ley de Reforma Educativa',
            'estado': 'APROBADO',
            'proponente': 'CONGRESO',
            'autores': 'Juan Pérez, María García'
        }
        
        result = self.validator.validate_record(record)
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_dataframe(self):
        """Test DataFrame validation"""
        data = {
            'proyecto': ['12345/2024-CR', '67890/2024-CR'],
            'fecha': ['15/06/2024', '20/06/2024'],
            'titulo': ['Ley de Reforma Educativa', 'Ley de Salud Pública'],
            'estado': ['APROBADO', 'ENVIADO'],
            'proponente': ['CONGRESO', 'CONGRESO'],
            'autores': ['Juan Pérez', 'María García']
        }
        
        df = pd.DataFrame(data)
        df_clean, report = self.validator.validate_dataframe(df)
        
        assert len(df_clean) == 2
        assert report['valid_records'] == 2
        assert report['invalid_records'] == 0


class TestDataCleaner:
    """Test cases for DataCleaner"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.cleaner = DataCleaner()
    
    def test_limpiar_fecha(self):
        """Test date cleaning"""
        # Test normal date
        result = self.cleaner.limpiar_fecha("15/06/2024")
        assert result == "15/06/2024"
        
        # Test date with prefix
        result = self.cleaner.limpiar_fecha("Fecha de Presentación15/06/2024")
        assert result == "15/06/2024"
        
        # Test invalid date
        result = self.cleaner.limpiar_fecha("invalid")
        assert result is None
    
    def test_limpiar_proyecto(self):
        """Test project cleaning"""
        # Test normal project
        result = self.cleaner.limpiar_proyecto("12345/2024-CR")
        assert result == "12345/2024-CR"
        
        # Test project with prefix
        result = self.cleaner.limpiar_proyecto("Proyecto de Ley 12345/2024-CR")
        assert result == "12345/2024-CR"
    
    def test_extraer_partido_politico(self):
        """Test political party extraction"""
        # Test known party
        result = self.cleaner.extraer_partido_politico("Juan Pérez - PERU LIBRE")
        assert result == "PERU LIBRE"
        
        # Test unknown party
        result = self.cleaner.extraer_partido_politico("Juan Pérez - Partido Desconocido")
        assert result == "DESCONOCIDO"
    
    def test_clasificar_tipo_proyecto(self):
        """Test project type classification"""
        # Test education project
        result = self.cleaner.clasificar_tipo_proyecto("Ley de Reforma Educativa")
        assert result == "EDUCACION"
        
        # Test health project
        result = self.cleaner.clasificar_tipo_proyecto("Ley de Salud Pública")
        assert result == "SALUD"
        
        # Test unknown project
        result = self.cleaner.clasificar_tipo_proyecto("Ley Misteriosa")
        assert result == "OTROS"
    
    def test_limpiar_dataframe(self):
        """Test DataFrame cleaning"""
        data = {
            'proyecto': ['Proyecto de Ley 12345/2024-CR'],
            'fecha': ['Fecha de Presentación15/06/2024'],
            'titulo': ['  Ley de Reforma Educativa  '],
            'estado': ['APROBADO'],
            'proponente': ['CONGRESO'],
            'autores': ['Juan Pérez - PERU LIBRE']
        }
        
        df = pd.DataFrame(data)
        df_clean = self.cleaner.limpiar_dataframe(df)
        
        assert len(df_clean) == 1
        assert 'proyecto_limpio' in df_clean.columns
        assert 'fecha_limpia' in df_clean.columns
        assert 'partido_politico' in df_clean.columns
        assert 'tipo_proyecto' in df_clean.columns


class TestPerformanceMonitor:
    """Test cases for PerformanceMonitor"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.monitor = PerformanceMonitor(monitoring_interval=0.1)
    
    def test_get_current_metrics(self):
        """Test getting current metrics"""
        metrics = self.monitor._get_current_metrics()
        
        assert isinstance(metrics.cpu_percent, float)
        assert isinstance(metrics.memory_percent, float)
        assert isinstance(metrics.memory_mb, float)
        assert isinstance(metrics.active_threads, int)
    
    def test_add_custom_metric(self):
        """Test adding custom metrics"""
        self.monitor.metrics_history = [self.monitor._get_current_metrics()]
        self.monitor.add_custom_metric("test_metric", "test_value")
        
        assert self.monitor.metrics_history[0].custom_metrics["test_metric"] == "test_value"
    
    def test_get_performance_summary(self):
        """Test getting performance summary"""
        # Add some mock metrics
        for i in range(5):
            metrics = self.monitor._get_current_metrics()
            metrics.cpu_percent = i * 10
            metrics.memory_percent = i * 5
            self.monitor.metrics_history.append(metrics)
        
        summary = self.monitor.get_performance_summary()
        
        assert 'cpu' in summary
        assert 'memory' in summary
        assert 'threads' in summary
        assert summary['cpu']['current'] == 40.0  # Last value


class TestEnhancedCongresoScraper:
    """Test cases for EnhancedCongresoScraper"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Mock the webdriver to avoid actual browser startup
        with patch('selenium.webdriver.Chrome'):
            self.scraper = EnhancedCongresoScraper(headless=True, enable_monitoring=False)
    
    def test_clean_proyecto(self):
        """Test project cleaning method"""
        result = self.scraper._clean_proyecto("Proyecto de Ley 12345/2024-CR")
        assert result == "12345/2024-CR"
        
        result = self.scraper._clean_proyecto("12345/2024-CR")
        assert result == "12345/2024-CR"
    
    def test_clean_fecha(self):
        """Test date cleaning method"""
        result = self.scraper._clean_fecha("Fecha de Presentación15/06/2024")
        assert result == "15/06/2024"
        
        result = self.scraper._clean_fecha("15/06/2024")
        assert result == "15/06/2024"
    
    def test_clean_titulo(self):
        """Test title cleaning method"""
        result = self.scraper._clean_titulo("  Ley de Reforma Educativa  ")
        assert result == "Ley de Reforma Educativa"
        
        result = self.scraper._clean_titulo("Ley   de   Reforma")
        assert result == "Ley de Reforma"
    
    def test_clean_estado(self):
        """Test state cleaning method"""
        result = self.scraper._clean_estado("Estado: APROBADO")
        assert result == "APROBADO"
        
        result = self.scraper._clean_estado("APROBADO")
        assert result == "APROBADO"
    
    def test_clean_proponente(self):
        """Test proponent cleaning method"""
        result = self.scraper._clean_proponente("Proponente: CONGRESO")
        assert result == "CONGRESO"
        
        result = self.scraper._clean_proponente("CONGRESO")
        assert result == "CONGRESO"
    
    def test_extract_text_safe(self):
        """Test safe text extraction"""
        from bs4 import BeautifulSoup
        
        html = '<td><span class="ellipsis">Test Title</span></td>'
        soup = BeautifulSoup(html, 'html.parser')
        element = soup.find('td')
        
        result = self.scraper._extract_text_safe(element)
        assert result == "Test Title"
    
    def test_extract_authors_safe(self):
        """Test safe authors extraction"""
        from bs4 import BeautifulSoup
        
        html = '<td><li>Author 1</li><li>Author 2</li></td>'
        soup = BeautifulSoup(html, 'html.parser')
        element = soup.find('td')
        
        result = self.scraper._extract_authors_safe(element)
        assert result == "Author 1, Author 2"
    
    def test_save_to_csv(self):
        """Test saving to CSV"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_data = [
                {
                    'proyecto': '12345/2024-CR',
                    'fecha': '15/06/2024',
                    'titulo': 'Test Law',
                    'estado': 'APROBADO',
                    'proponente': 'CONGRESO',
                    'autores': 'Test Author'
                }
            ]
            
            filename = os.path.join(temp_dir, 'test.csv')
            result_filename = self.scraper.save_to_csv(test_data, filename)
            
            assert os.path.exists(result_filename)
            
            # Read back and verify
            df = pd.read_csv(result_filename)
            assert len(df) == 1
            assert df.iloc[0]['proyecto'] == '12345/2024-CR'
    
    def test_get_statistics(self):
        """Test getting statistics"""
        self.scraper.stats['start_time'] = datetime.now()
        self.scraper.stats['end_time'] = datetime.now()
        self.scraper.stats['projects_found'] = 10
        
        stats = self.scraper.get_statistics()
        
        assert 'duration_seconds' in stats
        assert stats['projects_found'] == 10


class TestIntegration:
    """Integration tests"""
    
    def test_data_validation_integration(self):
        """Test integration between scraper and validator"""
        validator = DataValidator()
        cleaner = DataCleaner()
        
        # Simulate scraped data
        scraped_data = [
            {
                'proyecto': 'Proyecto de Ley 12345/2024-CR',
                'fecha': 'Fecha de Presentación15/06/2024',
                'titulo': '  Ley de Reforma Educativa  ',
                'estado': 'APROBADO',
                'proponente': 'CONGRESO',
                'autores': 'Juan Pérez - PERU LIBRE'
            }
        ]
        
        # Validate data
        df = pd.DataFrame(scraped_data)
        df_clean, validation_report = validator.validate_dataframe(df)
        
        # Clean data
        df_final = cleaner.limpiar_dataframe(df_clean)
        
        assert len(df_final) == 1
        assert 'partido_politico' in df_final.columns
        assert 'tipo_proyecto' in df_final.columns
        assert validation_report['valid_records'] == 1


# Fixtures for pytest
@pytest.fixture
def sample_data():
    """Sample data for testing"""
    return {
        'proyecto': ['12345/2024-CR', '67890/2024-CR'],
        'fecha': ['15/06/2024', '20/06/2024'],
        'titulo': ['Ley de Reforma Educativa', 'Ley de Salud Pública'],
        'estado': ['APROBADO', 'ENVIADO'],
        'proponente': ['CONGRESO', 'CONGRESO'],
        'autores': ['Juan Pérez - PERU LIBRE', 'María García - FUERZA POPULAR']
    }


@pytest.fixture
def validator():
    """DataValidator instance for testing"""
    return DataValidator()


@pytest.fixture
def cleaner():
    """DataCleaner instance for testing"""
    return DataCleaner()


# Parametrized tests
@pytest.mark.parametrize("fecha,expected", [
    ("15/06/2024", "15/06/2024"),
    ("Fecha de Presentación15/06/2024", "15/06/2024"),
    ("",L None),
    ("invalid", None)
])
def test_limpiar_fecha_parametrized(cleaner, fecha, expected):
    """Parametrized test for date cleaning"""
    result = cleaner.limpiar_fecha(fecha)
    assert result == expected


@pytest.mark.parametrize("proyecto,expected", [
    ("12345/2024-CR", "12345/2024-CR"),
    ("Proyecto de Ley 12345/2024-CR", "12345/2024-CR"),
    ("", None)
])
def test_limpiar_proyecto_parametrized(cleaner, proyecto, expected):
    """Parametrized test for project cleaning"""
    result = cleaner.limpiar_proyecto(proyecto)
    assert result == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
