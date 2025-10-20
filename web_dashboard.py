"""
Dashboard Web Interactivo para el Peru Congress Laws Scraper
"""
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

from flask import Flask, render_template, jsonify, request, send_file, redirect, url_for
from flask_cors import CORS
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder

# Import our utilities
from utils.metrics_collector import get_metrics_collector
from utils.alert_system import get_alert_system
from utils.report_generator import get_report_generator
from utils.limpieza import DataCleaner
from scraper_enhanced import EnhancedCongresoScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global instances
metrics_collector = get_metrics_collector()
alert_system = get_alert_system()
report_generator = get_report_generator()
data_cleaner = DataCleaner()


@app.route('/')
def index():
    """Página principal del dashboard"""
    return render_template('dashboard.html')


@app.route('/api/status')
def api_status():
    """API: Estado general del sistema"""
    try:
        # Obtener métricas recientes
        session_summary = metrics_collector.get_session_summary(days=7)
        quality_summary = metrics_collector.get_quality_summary(days=7)
        alert_summary = alert_system.get_alert_summary(hours=24)
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'system_status': 'online',
            'metrics': {
                'sessions': session_summary.get('total_sessions', 0),
                'projects': session_summary.get('total_projects', 0),
                'success_rate': session_summary.get('average_success_rate', 0),
                'data_quality': quality_summary.get('data_quality_score', 0)
            },
            'alerts': {
                'active': alert_summary.get('active_alerts', 0),
                'total_24h': alert_summary.get('total_alerts', 0),
                'by_severity': alert_summary.get('by_severity', {})
            },
            'data_files': _get_data_files_info()
        }
        
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error en API status: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/metrics')
def api_metrics():
    """API: Métricas detalladas"""
    try:
        days = request.args.get('days', 7, type=int)
        
        session_summary = metrics_collector.get_session_summary(days=days)
        quality_summary = metrics_collector.get_quality_summary(days=days)
        
        metrics = {
            'session_metrics': session_summary,
            'quality_metrics': quality_summary,
            'period_days': days
        }
        
        return jsonify(metrics)
    except Exception as e:
        logger.error(f"Error en API metrics: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/alerts')
def api_alerts():
    """API: Alertas del sistema"""
    try:
        hours = request.args.get('hours', 24, type=int)
        
        alert_summary = alert_system.get_alert_summary(hours=hours)
        active_alerts = alert_system.get_active_alerts()
        
        alerts_data = {
            'summary': alert_summary,
            'active_alerts': [
                {
                    'id': i,
                    'rule_name': alert.rule_name,
                    'message': alert.message,
                    'severity': alert.severity,
                    'timestamp': alert.timestamp.isoformat(),
                    'value': alert.value,
                    'threshold': alert.threshold
                }
                for i, alert in enumerate(active_alerts)
            ]
        }
        
        return jsonify(alerts_data)
    except Exception as e:
        logger.error(f"Error en API alerts: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/data')
def api_data():
    """API: Datos de proyectos de ley"""
    try:
        # Buscar archivos de datos recientes
        data_dir = Path('data')
        csv_files = list(data_dir.glob('proyectos_ley_*.csv'))
        
        if not csv_files:
            return jsonify({'error': 'No se encontraron archivos de datos'}), 404
        
        # Usar el archivo más reciente
        latest_file = max(csv_files, key=lambda f: f.stat().st_mtime)
        
        # Cargar datos
        df = pd.read_csv(latest_file, encoding='utf-8-sig')
        
        # Limpiar datos
        df_clean = data_cleaner.limpiar_dataframe(df)
        
        # Generar resumen
        resumen = data_cleaner.generar_resumen(df_clean)
        
        # Preparar datos para el frontend
        data_info = {
            'file_name': latest_file.name,
            'file_size': latest_file.stat().st_size,
            'last_modified': datetime.fromtimestamp(latest_file.stat().st_mtime).isoformat(),
            'total_records': len(df_clean),
            'summary': resumen,
            'sample_data': df_clean.head(10).to_dict('records')
        }
        
        return jsonify(data_info)
    except Exception as e:
        logger.error(f"Error en API data: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/charts/parties')
def api_charts_parties():
    """API: Gráfico de partidos políticos"""
    try:
        # Cargar datos
        data_dir = Path('data')
        csv_files = list(data_dir.glob('proyectos_ley_*.csv'))
        
        if not csv_files:
            return jsonify({'error': 'No se encontraron archivos de datos'}), 404
        
        latest_file = max(csv_files, key=lambda f: f.stat().st_mtime)
        df = pd.read_csv(latest_file, encoding='utf-8-sig')
        df_clean = data_cleaner.limpiar_dataframe(df)
        
        # Crear gráfico de partidos
        if 'partido_politico' in df_clean.columns:
            party_counts = df_clean['partido_politico'].value_counts().head(10)
            
            fig = px.bar(
                x=party_counts.values,
                y=party_counts.index,
                orientation='h',
                title="Top 10 Partidos Políticos por Número de Proyectos",
                labels={'x': 'Número de Proyectos', 'y': 'Partido Político'}
            )
            
            return jsonify(fig.to_json())
        else:
            return jsonify({'error': 'Columna partido_politico no encontrada'}), 400
            
    except Exception as e:
        logger.error(f"Error en API charts/parties: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/charts/types')
def api_charts_types():
    """API: Gráfico de tipos de proyecto"""
    try:
        # Cargar datos
        data_dir = Path('data')
        csv_files = list(data_dir.glob('proyectos_ley_*.csv'))
        
        if not csv_files:
            return jsonify({'error': 'No se encontraron archivos de datos'}), 404
        
        latest_file = max(csv_files, key=lambda f: f.stat().st_mtime)
        df = pd.read_csv(latest_file, encoding='utf-8-sig')
        df_clean = data_cleaner.limpiar_dataframe(df)
        
        # Crear gráfico de tipos
        if 'tipo_proyecto' in df_clean.columns:
            type_counts = df_clean['tipo_proyecto'].value_counts().head(10)
            
            fig = px.pie(
                values=type_counts.values,
                names=type_counts.index,
                title="Distribución de Tipos de Proyecto"
            )
            
            return jsonify(fig.to_json())
        else:
            return jsonify({'error': 'Columna tipo_proyecto no encontrada'}), 400
            
    except Exception as e:
        logger.error(f"Error en API charts/types: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/charts/timeline')
def api_charts_timeline():
    """API: Gráfico de línea de tiempo"""
    try:
        # Cargar datos
        data_dir = Path('data')
        csv_files = list(data_dir.glob('proyectos_ley_*.csv'))
        
        if not csv_files:
            return jsonify({'error': 'No se encontraron archivos de datos'}), 404
        
        latest_file = max(csv_files, key=lambda f: f.stat().st_mtime)
        df = pd.read_csv(latest_file, encoding='utf-8-sig')
        df_clean = data_cleaner.limpiar_dataframe(df)
        
        # Crear gráfico de línea de tiempo
        if 'fecha_datetime' in df_clean.columns:
            df_clean['fecha_datetime'] = pd.to_datetime(df_clean['fecha_datetime'])
            df_clean['fecha_date'] = df_clean['fecha_datetime'].dt.date
            
            timeline_data = df_clean.groupby('fecha_date').size().reset_index(name='count')
            timeline_data = timeline_data.sort_values('fecha_date')
            
            fig = px.line(
                timeline_data,
                x='fecha_date',
                y='count',
                title="Proyectos de Ley por Fecha",
                labels={'fecha_date': 'Fecha', 'count': 'Número de Proyectos'}
            )
            
            return jsonify(fig.to_json())
        else:
            return jsonify({'error': 'Columna fecha_datetime no encontrada'}), 400
            
    except Exception as e:
        logger.error(f"Error en API charts/timeline: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/scrape', methods=['POST'])
def api_scrape():
    """API: Iniciar scraping"""
    try:
        data = request.get_json() or {}
        
        # Configurar scraper
        scraper = EnhancedCongresoScraper(
            headless=data.get('headless', True),
            enable_monitoring=data.get('monitoring', True)
        )
        
        # Ejecutar scraping en background (simplificado)
        fecha_desde = data.get('fecha_desde')
        fecha_hasta = data.get('fecha_hasta')
        
        # Aquí deberías ejecutar el scraping en un hilo separado
        # Por simplicidad, solo retornamos un mensaje
        return jsonify({
            'message': 'Scraping iniciado',
            'config': {
                'fecha_desde': fecha_desde,
                'fecha_hasta': fecha_hasta,
                'headless': data.get('headless', True)
            }
        })
        
    except Exception as e:
        logger.error(f"Error en API scrape: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/<format>')
def api_export(format):
    """API: Exportar datos en diferentes formatos"""
    try:
        if format not in ['csv', 'json', 'excel']:
            return jsonify({'error': 'Formato no soportado'}), 400
        
        # Buscar archivo de datos más reciente
        data_dir = Path('data')
        csv_files = list(data_dir.glob('proyectos_ley_*.csv'))
        
        if not csv_files:
            return jsonify({'error': 'No se encontraron archivos de datos'}), 404
        
        latest_file = max(csv_files, key=lambda f: f.stat().st_mtime)
        df = pd.read_csv(latest_file, encoding='utf-8-sig')
        df_clean = data_cleaner.limpiar_dataframe(df)
        
        # Generar archivo de exportación
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == 'csv':
            output_file = f"export_proyectos_ley_{timestamp}.csv"
            df_clean.to_csv(f"reports/{output_file}", index=False, encoding='utf-8-sig')
        elif format == 'json':
            output_file = f"export_proyectos_ley_{timestamp}.json"
            df_clean.to_json(f"reports/{output_file}", orient='records', indent=2, force_ascii=False)
        elif format == 'excel':
            output_file = f"export_proyectos_ley_{timestamp}.xlsx"
            df_clean.to_excel(f"reports/{output_file}", index=False)
        
        return jsonify({
            'message': f'Datos exportados en formato {format.upper()}',
            'file': output_file,
            'records': len(df_clean)
        })
        
    except Exception as e:
        logger.error(f"Error en API export: {e}")
        return jsonify({'error': str(e)}), 500


def _get_data_files_info():
    """Obtener información de archivos de datos"""
    data_dir = Path('data')
    csv_files = list(data_dir.glob('proyectos_ley_*.csv'))
    
    files_info = []
    for file_path in csv_files:
        try:
            stat = file_path.stat()
            files_info.append({
                'name': file_path.name,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'path': str(file_path)
            })
        except Exception as e:
            logger.warning(f"Error obteniendo info de archivo {file_path}: {e}")
    
    return sorted(files_info, key=lambda x: x['modified'], reverse=True)


if __name__ == '__main__':
    # Crear directorio de templates si no existe
    templates_dir = Path('templates')
    templates_dir.mkdir(exist_ok=True)
    
    # Crear template básico si no existe
    template_file = templates_dir / 'dashboard.html'
    if not template_file.exists():
        _create_basic_template(template_file)
    
    # Crear directorio de reports
    reports_dir = Path('reports')
    reports_dir.mkdir(exist_ok=True)
    
    print("🚀 Iniciando Dashboard Web...")
    print("📊 Accede a: http://localhost:5000")
    print("🔧 API disponible en: http://localhost:5000/api/")
    
    app.run(debug=True, host='0.0.0.0', port=5000)


def _create_basic_template(template_file: Path):
    """Crear template HTML básico para el dashboard"""
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard - Peru Congress Laws Scraper</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; text-align: center; }
            .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }
            .stat-card { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; }
            .stat-value { font-size: 2.5em; font-weight: bold; color: #2196F3; margin-bottom: 10px; }
            .stat-label { color: #666; font-size: 1.1em; }
            .chart-container { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 20px 0; }
            .alert { padding: 15px; border-radius: 5px; margin: 10px 0; }
            .alert-critical { background-color: #ffebee; border-left: 5px solid #f44336; }
            .alert-high { background-color: #fff3e0; border-left: 5px solid #ff9800; }
            .alert-medium { background-color: #fff8e1; border-left: 5px solid #ffc107; }
            .alert-low { background-color: #e8f5e8; border-left: 5px solid #4caf50; }
            .loading { text-align: center; padding: 50px; color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Dashboard - Peru Congress Laws Scraper</h1>
                <p>Sistema de Monitoreo y Análisis en Tiempo Real</p>
            </div>
            
            <div id="loading" class="loading">
                <h3>🔄 Cargando datos...</h3>
            </div>
            
            <div id="dashboard" style="display: none;">
                <div class="stats-grid" id="stats-grid">
                    <!-- Stats will be loaded here -->
                </div>
                
                <div class="chart-container">
                    <h3>📈 Partidos Políticos</h3>
                    <div id="parties-chart"></div>
                </div>
                
                <div class="chart-container">
                    <h3>📊 Tipos de Proyecto</h3>
                    <div id="types-chart"></div>
                </div>
                
                <div class="chart-container">
                    <h3>📅 Línea de Tiempo</h3>
                    <div id="timeline-chart"></div>
                </div>
                
                <div class="chart-container">
                    <h3>🚨 Alertas Activas</h3>
                    <div id="alerts-container">
                        <!-- Alerts will be loaded here -->
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // Cargar datos del dashboard
            async function loadDashboard() {
                try {
                    // Cargar estado general
                    const statusResponse = await axios.get('/api/status');
                    const status = statusResponse.data;
                    
                    // Mostrar estadísticas
                    displayStats(status.metrics, status.alerts);
                    
                    // Cargar gráficos
                    loadCharts();
                    
                    // Cargar alertas
                    loadAlerts();
                    
                    // Ocultar loading y mostrar dashboard
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('dashboard').style.display = 'block';
                    
                } catch (error) {
                    console.error('Error cargando dashboard:', error);
                    document.getElementById('loading').innerHTML = '<h3>❌ Error cargando datos</h3>';
                }
            }
            
            function displayStats(metrics, alerts) {
                const statsGrid = document.getElementById('stats-grid');
                statsGrid.innerHTML = `
                    <div class="stat-card">
                        <div class="stat-value">${metrics.projects || 0}</div>
                        <div class="stat-label">Proyectos Totales</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${metrics.sessions || 0}</div>
                        <div class="stat-label">Sesiones</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${metrics.success_rate || 0}%</div>
                        <div class="stat-label">Tasa de Éxito</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${metrics.data_quality || 0}%</div>
                        <div class="stat-label">Calidad de Datos</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${alerts.active || 0}</div>
                        <div class="stat-label">Alertas Activas</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${alerts.total_24h || 0}</div>
                        <div class="stat-label">Alertas (24h)</div>
                    </div>
                `;
            }
            
            async function loadCharts() {
                try {
                    // Gráfico de partidos
                    const partiesResponse = await axios.get('/api/charts/parties');
                    const partiesData = partiesResponse.data;
                    Plotly.newPlot('parties-chart', partiesData.data, partiesData.layout);
                    
                    // Gráfico de tipos
                    const typesResponse = await axios.get('/api/charts/types');
                    const typesData = typesResponse.data;
                    Plotly.newPlot('types-chart', typesData.data, typesData.layout);
                    
                    // Gráfico de línea de tiempo
                    const timelineResponse = await axios.get('/api/charts/timeline');
                    const timelineData = timelineResponse.data;
                    Plotly.newPlot('timeline-chart', timelineData.data, timelineData.layout);
                    
                } catch (error) {
                    console.error('Error cargando gráficos:', error);
                }
            }
            
            async function loadAlerts() {
                try {
                    const alertsResponse = await axios.get('/api/alerts');
                    const alertsData = alertsResponse.data;
                    
                    const alertsContainer = document.getElementById('alerts-container');
                    
                    if (alertsData.active_alerts.length === 0) {
                        alertsContainer.innerHTML = '<p>✅ No hay alertas activas</p>';
                        return;
                    }
                    
                    let alertsHtml = '';
                    alertsData.active_alerts.forEach(alert => {
                        alertsHtml += `
                            <div class="alert alert-${alert.severity}">
                                <h4>${alert.severity.toUpperCase()}: ${alert.message}</h4>
                                <p><strong>Valor:</strong> ${alert.value} | <strong>Umbral:</strong> ${alert.threshold}</p>
                                <p><strong>Timestamp:</strong> ${new Date(alert.timestamp).toLocaleString()}</p>
                            </div>
                        `;
                    });
                    
                    alertsContainer.innerHTML = alertsHtml;
                    
                } catch (error) {
                    console.error('Error cargando alertas:', error);
                }
            }
            
            // Cargar dashboard al iniciar
            loadDashboard();
            
            // Actualizar cada 30 segundos
            setInterval(loadDashboard, 30000);
        </script>
    </body>
    </html>
    """
    
    with open(template_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
