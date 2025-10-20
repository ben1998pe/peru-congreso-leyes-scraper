"""
Generador de reportes automáticos para el Peru Congress Laws Scraper
"""
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from jinja2 import Template
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generador de reportes automáticos"""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Configurar matplotlib
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def generate_executive_summary(self, data: Dict[str, Any], 
                                 output_file: str = None) -> str:
        """Generar resumen ejecutivo"""
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"executive_summary_{timestamp}.html"
        
        template = Template("""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Resumen Ejecutivo - Proyectos de Ley del Perú</title>
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
                .header { text-align: center; border-bottom: 3px solid #2196F3; padding-bottom: 20px; margin-bottom: 30px; }
                .header h1 { color: #2196F3; margin: 0; font-size: 2.5em; }
                .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }
                .kpi-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 10px; text-align: center; }
                .kpi-value { font-size: 2.5em; font-weight: bold; margin-bottom: 10px; }
                .kpi-label { font-size: 1.1em; opacity: 0.9; }
                .section { margin: 40px 0; padding: 25px; background: #f8f9fa; border-radius: 8px; border-left: 5px solid #2196F3; }
                .section h2 { color: #2196F3; margin-top: 0; }
                table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
                th { background: #2196F3; color: white; }
                .chart-container { margin: 20px 0; text-align: center; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Resumen Ejecutivo</h1>
                    <p>Proyectos de Ley del Congreso del Perú</p>
                    <p>Generado el: {{ generated_at }}</p>
                </div>
                
                <div class="kpi-grid">
                    <div class="kpi-card">
                        <div class="kpi-value">{{ total_projects }}</div>
                        <div class="kpi-label">Total Proyectos</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-value">{{ total_parties }}</div>
                        <div class="kpi-label">Partidos Políticos</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-value">{{ avg_authors }}</div>
                        <div class="kpi-label">Promedio Autores</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-value">{{ data_quality_score }}%</div>
                        <div class="kpi-label">Calidad de Datos</div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>📈 Hallazgos Principales</h2>
                    <ul>
                        {% for finding in key_findings %}
                        <li>{{ finding }}</li>
                        {% endfor %}
                    </ul>
                </div>
                
                <div class="section">
                    <h2>🏛️ Top 5 Partidos Políticos</h2>
                    <table>
                        <thead>
                            <tr><th>Partido</th><th>Proyectos</th><th>% del Total</th></tr>
                        </thead>
                        <tbody>
                            {% for party, count in top_parties %}
                            <tr>
                                <td>{{ party }}</td>
                                <td>{{ count }}</td>
                                <td>{{ "%.1f"|format((count / total_projects) * 100) }}%</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                
                <div class="section">
                    <h2>📋 Top 5 Tipos de Proyecto</h2>
                    <table>
                        <thead>
                            <tr><th>Tipo</th><th>Proyectos</th><th>% del Total</th></tr>
                        </thead>
                        <tbody>
                            {% for ptype, count in top_types %}
                            <tr>
                                <td>{{ ptype }}</td>
                                <td>{{ count }}</td>
                                <td>{{ "%.1f"|format((count / total_projects) * 100) }}%</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                
                <div class="section">
                    <h2>📊 Recomendaciones</h2>
                    <ul>
                        {% for recommendation in recommendations %}
                        <li>{{ recommendation }}</li>
                        {% endfor %}
                    </ul>
                </div>
            </div>
        </body>
        </html>
        """)
        
        # Preparar datos para el template
        template_data = {
            'generated_at': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'total_projects': data.get('total_projects', 0),
            'total_parties': len(data.get('parties', {})),
            'avg_authors': data.get('avg_authors', 0),
            'data_quality_score': data.get('data_quality_score', 0),
            'key_findings': self._generate_key_findings(data),
            'top_parties': list(data.get('parties', {}).items())[:5],
            'top_types': list(data.get('project_types', {}).items())[:5],
            'recommendations': self._generate_recommendations(data)
        }
        
        # Generar HTML
        html_content = template.render(**template_data)
        
        # Guardar archivo
        output_path = self.output_dir / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"📊 Resumen ejecutivo generado: {output_path}")
        return str(output_path)
    
    def generate_analytics_report(self, df: pd.DataFrame, 
                                output_file: str = None) -> str:
        """Generar reporte de análisis detallado"""
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"analytics_report_{timestamp}.html"
        
        # Generar visualizaciones
        charts = self._generate_charts(df)
        
        template = Template("""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Reporte de Análisis - Proyectos de Ley</title>
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
                .header { text-align: center; border-bottom: 3px solid #2196F3; padding-bottom: 20px; margin-bottom: 30px; }
                .chart-section { margin: 40px 0; padding: 25px; background: #f8f9fa; border-radius: 8px; }
                .chart-container { margin: 20px 0; text-align: center; }
                .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
                .stat-card { background: #2196F3; color: white; padding: 20px; border-radius: 8px; text-align: center; }
                .stat-value { font-size: 2em; font-weight: bold; }
                .stat-label { font-size: 0.9em; opacity: 0.9; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Reporte de Análisis Detallado</h1>
                    <p>Proyectos de Ley del Congreso del Perú</p>
                    <p>Generado el: {{ generated_at }}</p>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">{{ total_projects }}</div>
                        <div class="stat-label">Total Proyectos</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{{ unique_parties }}</div>
                        <div class="stat-label">Partidos Únicos</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{{ unique_types }}</div>
                        <div class="stat-label">Tipos de Proyecto</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{{ date_range }}</div>
                        <div class="stat-label">Rango de Fechas</div>
                    </div>
                </div>
                
                {{ charts_html }}
            </div>
        </body>
        </html>
        """)
        
        # Preparar datos
        template_data = {
            'generated_at': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'total_projects': len(df),
            'unique_parties': df['partido_politico'].nunique() if 'partido_politico' in df.columns else 0,
            'unique_types': df['tipo_proyecto'].nunique() if 'tipo_proyecto' in df.columns else 0,
            'date_range': self._get_date_range(df),
            'charts_html': charts
        }
        
        # Generar HTML
        html_content = template.render(**template_data)
        
        # Guardar archivo
        output_path = self.output_dir / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"📊 Reporte de análisis generado: {output_path}")
        return str(output_path)
    
    def generate_metrics_report(self, metrics_data: Dict[str, Any], 
                              output_file: str = None) -> str:
        """Generar reporte de métricas de rendimiento"""
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"metrics_report_{timestamp}.html"
        
        template = Template("""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Reporte de Métricas - Scraper</title>
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
                .header { text-align: center; border-bottom: 3px solid #2196F3; padding-bottom: 20px; margin-bottom: 30px; }
                .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }
                .metric-card { background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 5px solid #2196F3; }
                .metric-title { font-weight: bold; color: #2196F3; margin-bottom: 10px; }
                .metric-value { font-size: 1.5em; color: #333; }
                .metric-description { font-size: 0.9em; color: #666; margin-top: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📈 Reporte de Métricas de Rendimiento</h1>
                    <p>Sistema de Scraping del Congreso del Perú</p>
                    <p>Generado el: {{ generated_at }}</p>
                </div>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-title">Sesiones Totales</div>
                        <div class="metric-value">{{ total_sessions }}</div>
                        <div class="metric-description">Últimos {{ period_days }} días</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Proyectos Extraídos</div>
                        <div class="metric-value">{{ total_projects }}</div>
                        <div class="metric-description">Total acumulado</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Tasa de Éxito</div>
                        <div class="metric-value">{{ success_rate }}%</div>
                        <div class="metric-description">Promedio de sesiones</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Velocidad Promedio</div>
                        <div class="metric-value">{{ projects_per_minute }}</div>
                        <div class="metric-description">Proyectos por minuto</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Duración Total</div>
                        <div class="metric-value">{{ total_duration_hours }}h</div>
                        <div class="metric-description">Tiempo de procesamiento</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Calidad de Datos</div>
                        <div class="metric-value">{{ data_quality_score }}%</div>
                        <div class="metric-description">Puntuación promedio</div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """)
        
        # Preparar datos
        template_data = {
            'generated_at': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'total_sessions': metrics_data.get('total_sessions', 0),
            'total_projects': metrics_data.get('total_projects', 0),
            'success_rate': metrics_data.get('average_success_rate', 0),
            'projects_per_minute': metrics_data.get('average_projects_per_minute', 0),
            'total_duration_hours': metrics_data.get('total_duration_hours', 0),
            'data_quality_score': metrics_data.get('data_quality_score', 0),
            'period_days': metrics_data.get('period_days', 7)
        }
        
        # Generar HTML
        html_content = template.render(**template_data)
        
        # Guardar archivo
        output_path = self.output_dir / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"📊 Reporte de métricas generado: {output_path}")
        return str(output_path)
    
    def _generate_key_findings(self, data: Dict[str, Any]) -> List[str]:
        """Generar hallazgos clave basados en los datos"""
        findings = []
        
        total_projects = data.get('total_projects', 0)
        if total_projects > 0:
            findings.append(f"Se analizaron {total_projects:,} proyectos de ley")
        
        parties = data.get('parties', {})
        if parties:
            top_party = max(parties.items(), key=lambda x: x[1])
            findings.append(f"El partido más activo es {top_party[0]} con {top_party[1]} proyectos")
        
        project_types = data.get('project_types', {})
        if project_types:
            top_type = max(project_types.items(), key=lambda x: x[1])
            findings.append(f"El tipo de proyecto más común es {top_type[0]} con {top_type[1]} casos")
        
        data_quality = data.get('data_quality_score', 0)
        if data_quality > 80:
            findings.append("La calidad de los datos es excelente (>80%)")
        elif data_quality > 60:
            findings.append("La calidad de los datos es buena (>60%)")
        else:
            findings.append("Se recomienda mejorar la calidad de los datos")
        
        return findings
    
    def _generate_recommendations(self, data: Dict[str, Any]) -> List[str]:
        """Generar recomendaciones basadas en los datos"""
        recommendations = []
        
        total_projects = data.get('total_projects', 0)
        if total_projects < 100:
            recommendations.append("Considerar aumentar la frecuencia de scraping para obtener más datos")
        
        data_quality = data.get('data_quality_score', 0)
        if data_quality < 70:
            recommendations.append("Implementar mejoras en la validación de datos")
        
        parties = data.get('parties', {})
        if parties and len(parties) > 10:
            recommendations.append("Analizar la distribución de proyectos entre partidos políticos")
        
        recommendations.append("Mantener monitoreo continuo del sistema de scraping")
        recommendations.append("Generar reportes periódicos para seguimiento de tendencias")
        
        return recommendations
    
    def _generate_charts(self, df: pd.DataFrame) -> str:
        """Generar gráficos para el reporte"""
        charts_html = ""
        
        try:
            # Gráfico de partidos políticos
            if 'partido_politico' in df.columns:
                party_counts = df['partido_politico'].value_counts().head(10)
                fig = px.bar(
                    x=party_counts.values,
                    y=party_counts.index,
                    orientation='h',
                    title="Top 10 Partidos Políticos por Número de Proyectos",
                    labels={'x': 'Número de Proyectos', 'y': 'Partido Político'}
                )
                fig.update_layout(height=400)
                charts_html += f'<div class="chart-section"><h3>Partidos Políticos</h3><div class="chart-container">{fig.to_html(include_plotlyjs="cdn")}</div></div>'
            
            # Gráfico de tipos de proyecto
            if 'tipo_proyecto' in df.columns:
                type_counts = df['tipo_proyecto'].value_counts().head(10)
                fig = px.pie(
                    values=type_counts.values,
                    names=type_counts.index,
                    title="Distribución de Tipos de Proyecto"
                )
                fig.update_layout(height=400)
                charts_html += f'<div class="chart-section"><h3>Tipos de Proyecto</h3><div class="chart-container">{fig.to_html(include_plotlyjs="cdn")}</div></div>'
            
        except Exception as e:
            logger.warning(f"Error generando gráficos: {e}")
            charts_html = "<p>No se pudieron generar gráficos</p>"
        
        return charts_html
    
    def _get_date_range(self, df: pd.DataFrame) -> str:
        """Obtener rango de fechas de los datos"""
        try:
            if 'fecha_datetime' in df.columns:
                dates = df['fecha_datetime'].dropna()
                if not dates.empty:
                    return f"{dates.min().strftime('%d/%m/%Y')} - {dates.max().strftime('%d/%m/%Y')}"
        except Exception:
            pass
        return "No disponible"


def get_report_generator() -> ReportGenerator:
    """Obtener instancia del generador de reportes"""
    return ReportGenerator()


# Funciones de conveniencia
def generate_executive_summary(data: Dict[str, Any], output_file: str = None) -> str:
    """Generar resumen ejecutivo"""
    generator = get_report_generator()
    return generator.generate_executive_summary(data, output_file)


def generate_analytics_report(df: pd.DataFrame, output_file: str = None) -> str:
    """Generar reporte de análisis"""
    generator = get_report_generator()
    return generator.generate_analytics_report(df, output_file)


def generate_metrics_report(metrics_data: Dict[str, Any], output_file: str = None) -> str:
    """Generar reporte de métricas"""
    generator = get_report_generator()
    return generator.generate_metrics_report(metrics_data, output_file)


if __name__ == "__main__":
    # Prueba del generador de reportes
    generator = ReportGenerator()
    
    # Datos de ejemplo
    sample_data = {
        'total_projects': 150,
        'parties': {'PERU LIBRE': 45, 'FUERZA POPULAR': 38, 'ACCION POPULAR': 25},
        'project_types': {'EDUCACION': 30, 'SALUD': 25, 'ECONOMIA': 20},
        'avg_authors': 2.3,
        'data_quality_score': 85.5
    }
    
    # Generar reportes
    exec_summary = generator.generate_executive_summary(sample_data)
    print(f"Resumen ejecutivo: {exec_summary}")
    
    # Crear DataFrame de ejemplo
    import pandas as pd
    sample_df = pd.DataFrame({
        'partido_politico': ['PERU LIBRE', 'FUERZA POPULAR', 'ACCION POPULAR'] * 50,
        'tipo_proyecto': ['EDUCACION', 'SALUD', 'ECONOMIA'] * 50,
        'fecha_datetime': pd.date_range('2024-01-01', periods=150, freq='D')
    })
    
    analytics_report = generator.generate_analytics_report(sample_df)
    print(f"Reporte de análisis: {analytics_report}")
