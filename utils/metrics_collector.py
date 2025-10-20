"""
Sistema de recolección de métricas avanzadas para el Peru Congress Laws Scraper
"""
import json
import time
import psutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd
import logging
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class ScrapingMetrics:
    """Métricas de scraping"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    projects_found: int = 0
    pages_scraped: int = 0
    errors_encountered: int = 0
    retries_performed: int = 0
    duration_seconds: float = 0.0
    success_rate: float = 0.0
    projects_per_minute: float = 0.0
    memory_peak_mb: float = 0.0
    cpu_peak_percent: float = 0.0


@dataclass
class DataQualityMetrics:
    """Métricas de calidad de datos"""
    total_records: int = 0
    valid_records: int = 0
    invalid_records: int = 0
    validation_errors: int = 0
    validation_warnings: int = 0
    data_completeness: float = 0.0
    data_accuracy: float = 0.0
    duplicate_records: int = 0
    missing_fields: Dict[str, int] = None


class MetricsCollector:
    """Recolector de métricas avanzadas"""
    
    def __init__(self, metrics_dir: str = "metrics"):
        self.metrics_dir = Path(metrics_dir)
        self.metrics_dir.mkdir(exist_ok=True)
        
        self.current_session = None
        self.session_metrics = []
        self.quality_metrics = []
        
    def start_session(self, session_id: str = None) -> str:
        """Iniciar nueva sesión de métricas"""
        if session_id is None:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_session = ScrapingMetrics(
            session_id=session_id,
            start_time=datetime.now()
        )
        
        logger.info(f"📊 Iniciando sesión de métricas: {session_id}")
        return session_id
    
    def end_session(self, projects_found: int = 0, pages_scraped: int = 0, 
                   errors: int = 0, retries: int = 0) -> ScrapingMetrics:
        """Finalizar sesión de métricas"""
        if not self.current_session:
            logger.warning("No hay sesión activa para finalizar")
            return None
        
        self.current_session.end_time = datetime.now()
        self.current_session.projects_found = projects_found
        self.current_session.pages_scraped = pages_scraped
        self.current_session.errors_encountered = errors
        self.current_session.retries_performed = retries
        
        # Calcular métricas derivadas
        self._calculate_derived_metrics()
        
        # Guardar métricas
        self.session_metrics.append(self.current_session)
        self._save_session_metrics()
        
        logger.info(f"📊 Sesión finalizada: {self.current_session.session_id}")
        logger.info(f"   Proyectos: {projects_found}, Páginas: {pages_scraped}")
        logger.info(f"   Duración: {self.current_session.duration_seconds:.2f}s")
        logger.info(f"   Tasa de éxito: {self.current_session.success_rate:.1f}%")
        
        return self.current_session
    
    def _calculate_derived_metrics(self):
        """Calcular métricas derivadas"""
        if not self.current_session or not self.current_session.end_time:
            return
        
        # Duración
        self.current_session.duration_seconds = (
            self.current_session.end_time - self.current_session.start_time
        ).total_seconds()
        
        # Tasa de éxito
        total_operations = self.current_session.pages_scraped + self.current_session.errors_encountered
        if total_operations > 0:
            self.current_session.success_rate = (
                (total_operations - self.current_session.errors_encountered) / total_operations
            ) * 100
        
        # Proyectos por minuto
        if self.current_session.duration_seconds > 0:
            self.current_session.projects_per_minute = (
                self.current_session.projects_found / (self.current_session.duration_seconds / 60)
            )
        
        # Métricas del sistema
        try:
            process = psutil.Process()
            self.current_session.memory_peak_mb = process.memory_info().rss / 1024 / 1024
            self.current_session.cpu_peak_percent = process.cpu_percent()
        except Exception as e:
            logger.warning(f"Error obteniendo métricas del sistema: {e}")
    
    def record_data_quality(self, df: pd.DataFrame, validation_report: Dict = None) -> DataQualityMetrics:
        """Registrar métricas de calidad de datos"""
        metrics = DataQualityMetrics()
        
        # Métricas básicas
        metrics.total_records = len(df)
        
        if validation_report:
            metrics.valid_records = validation_report.get('valid_records', 0)
            metrics.invalid_records = validation_report.get('invalid_records', 0)
            metrics.validation_errors = validation_report.get('total_errors', 0)
            metrics.validation_warnings = validation_report.get('total_warnings', 0)
        else:
            # Calcular métricas básicas sin reporte de validación
            metrics.valid_records = len(df)
            metrics.invalid_records = 0
        
        # Completitud de datos
        if metrics.total_records > 0:
            metrics.data_completeness = (metrics.valid_records / metrics.total_records) * 100
        
        # Precisión de datos (simplificada)
        if metrics.total_records > 0:
            metrics.data_accuracy = max(0, 100 - (metrics.validation_errors / metrics.total_records) * 100)
        
        # Duplicados
        if not df.empty:
            metrics.duplicate_records = df.duplicated().sum()
        
        # Campos faltantes
        metrics.missing_fields = {}
        for column in df.columns:
            missing_count = df[column].isna().sum()
            if missing_count > 0:
                metrics.missing_fields[column] = int(missing_count)
        
        # Guardar métricas
        self.quality_metrics.append(metrics)
        self._save_quality_metrics()
        
        logger.info(f"📊 Métricas de calidad registradas:")
        logger.info(f"   Registros: {metrics.total_records} (válidos: {metrics.valid_records})")
        logger.info(f"   Completitud: {metrics.data_completeness:.1f}%")
        logger.info(f"   Precisión: {metrics.data_accuracy:.1f}%")
        
        return metrics
    
    def get_session_summary(self, days: int = 7) -> Dict[str, Any]:
        """Obtener resumen de sesiones de los últimos N días"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_sessions = [
            session for session in self.session_metrics
            if session.start_time >= cutoff_date
        ]
        
        if not recent_sessions:
            return {"message": "No hay sesiones recientes"}
        
        # Calcular estadísticas
        total_projects = sum(s.projects_found for s in recent_sessions)
        total_pages = sum(s.pages_scraped for s in recent_sessions)
        total_errors = sum(s.errors_encountered for s in recent_sessions)
        total_duration = sum(s.duration_seconds for s in recent_sessions)
        
        avg_success_rate = sum(s.success_rate for s in recent_sessions) / len(recent_sessions)
        avg_projects_per_minute = sum(s.projects_per_minute for s in recent_sessions) / len(recent_sessions)
        
        return {
            "period_days": days,
            "total_sessions": len(recent_sessions),
            "total_projects": total_projects,
            "total_pages": total_pages,
            "total_errors": total_errors,
            "total_duration_hours": total_duration / 3600,
            "average_success_rate": round(avg_success_rate, 2),
            "average_projects_per_minute": round(avg_projects_per_minute, 2),
            "sessions": [
                {
                    "session_id": s.session_id,
                    "start_time": s.start_time.isoformat(),
                    "duration_seconds": s.duration_seconds,
                    "projects_found": s.projects_found,
                    "success_rate": s.success_rate
                }
                for s in recent_sessions[-10:]  # Últimas 10 sesiones
            ]
        }
    
    def get_quality_summary(self, days: int = 7) -> Dict[str, Any]:
        """Obtener resumen de calidad de datos"""
        if not self.quality_metrics:
            return {"message": "No hay métricas de calidad disponibles"}
        
        # Calcular estadísticas agregadas
        total_records = sum(m.total_records for m in self.quality_metrics)
        total_valid = sum(m.valid_records for m in self.quality_metrics)
        total_invalid = sum(m.invalid_records for m in self.quality_metrics)
        total_errors = sum(m.validation_errors for m in self.quality_metrics)
        total_warnings = sum(m.validation_warnings for m in self.quality_metrics)
        
        avg_completeness = sum(m.data_completeness for m in self.quality_metrics) / len(self.quality_metrics)
        avg_accuracy = sum(m.data_accuracy for m in self.quality_metrics) / len(self.quality_metrics)
        
        return {
            "total_records": total_records,
            "valid_records": total_valid,
            "invalid_records": total_invalid,
            "validation_errors": total_errors,
            "validation_warnings": total_warnings,
            "average_completeness": round(avg_completeness, 2),
            "average_accuracy": round(avg_accuracy, 2),
            "data_quality_score": round((avg_completeness + avg_accuracy) / 2, 2)
        }
    
    def _save_session_metrics(self):
        """Guardar métricas de sesión"""
        if not self.current_session:
            return
        
        file_path = self.metrics_dir / f"session_metrics_{datetime.now().strftime('%Y%m%d')}.json"
        
        # Cargar métricas existentes
        existing_metrics = []
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing_metrics = json.load(f)
            except Exception as e:
                logger.warning(f"Error cargando métricas existentes: {e}")
        
        # Agregar nueva métrica
        existing_metrics.append(asdict(self.current_session))
        
        # Guardar
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_metrics, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error guardando métricas de sesión: {e}")
    
    def _save_quality_metrics(self):
        """Guardar métricas de calidad"""
        if not self.quality_metrics:
            return
        
        file_path = self.metrics_dir / f"quality_metrics_{datetime.now().strftime('%Y%m%d')}.json"
        
        # Cargar métricas existentes
        existing_metrics = []
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing_metrics = json.load(f)
            except Exception as e:
                logger.warning(f"Error cargando métricas de calidad existentes: {e}")
        
        # Agregar nuevas métricas
        for metric in self.quality_metrics:
            existing_metrics.append(asdict(metric))
        
        # Guardar
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_metrics, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error guardando métricas de calidad: {e}")
    
    def export_metrics_report(self, output_file: str = None) -> str:
        """Exportar reporte completo de métricas"""
        if output_file is None:
            output_file = f"metrics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "session_summary": self.get_session_summary(),
            "quality_summary": self.get_quality_summary(),
            "system_info": {
                "python_version": f"{psutil.sys.version_info.major}.{psutil.sys.version_info.minor}",
                "platform": psutil.sys.platform,
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2)
            }
        }
        
        output_path = self.metrics_dir / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"📊 Reporte de métricas exportado: {output_path}")
        return str(output_path)


def get_metrics_collector() -> MetricsCollector:
    """Obtener instancia del recolector de métricas"""
    return MetricsCollector()


# Funciones de conveniencia
def start_metrics_session(session_id: str = None) -> str:
    """Iniciar sesión de métricas"""
    collector = get_metrics_collector()
    return collector.start_session(session_id)


def end_metrics_session(projects_found: int = 0, pages_scraped: int = 0, 
                       errors: int = 0, retries: int = 0) -> ScrapingMetrics:
    """Finalizar sesión de métricas"""
    collector = get_metrics_collector()
    return collector.end_session(projects_found, pages_scraped, errors, retries)


def record_data_quality(df: pd.DataFrame, validation_report: Dict = None) -> DataQualityMetrics:
    """Registrar métricas de calidad de datos"""
    collector = get_metrics_collector()
    return collector.record_data_quality(df, validation_report)


if __name__ == "__main__":
    # Prueba del sistema de métricas
    collector = MetricsCollector()
    
    # Simular sesión de scraping
    session_id = collector.start_session()
    time.sleep(2)  # Simular trabajo
    metrics = collector.end_session(projects_found=100, pages_scraped=5, errors=1, retries=2)
    
    # Simular métricas de calidad
    import pandas as pd
    test_df = pd.DataFrame({
        'proyecto': ['123/2024-CR', '456/2024-CR'],
        'fecha': ['01/01/2024', '02/01/2024'],
        'titulo': ['Test 1', 'Test 2']
    })
    
    quality_metrics = collector.record_data_quality(test_df)
    
    # Generar reporte
    report_file = collector.export_metrics_report()
    print(f"Reporte generado: {report_file}")
    
    # Mostrar resumen
    summary = collector.get_session_summary()
    print(f"Resumen de sesiones: {summary}")
