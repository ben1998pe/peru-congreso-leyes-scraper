#!/usr/bin/env python3
"""
Dashboard simple para monitorear el estado del Peru Congress Laws Scraper
"""
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import json
import pandas as pd
import glob

# Agregar el directorio padre al path
sys.path.append(str(Path(__file__).parent))

from utils.limpieza import DataCleaner
from utils.data_validator import DataValidator
from utils.notifications import get_notification_manager


class ScraperDashboard:
    """Dashboard para monitorear el estado del scraper"""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.logs_dir = Path("logs")
        self.analysis_dir = Path("analysis")
        self.reports_dir = Path("reports")
        
    def get_project_status(self) -> dict:
        """Obtener estado general del proyecto"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'data_files': 0,
            'log_files': 0,
            'analysis_files': 0,
            'latest_data': None,
            'latest_log': None,
            'total_projects': 0,
            'last_scraping': None,
            'health_status': 'unknown'
        }
        
        # Contar archivos de datos
        data_files = list(self.data_dir.glob("proyectos_ley_*.csv"))
        status['data_files'] = len(data_files)
        
        if data_files:
            latest_data = max(data_files, key=lambda x: x.stat().st_mtime)
            status['latest_data'] = {
                'file': latest_data.name,
                'size': latest_data.stat().st_size,
                'modified': datetime.fromtimestamp(latest_data.stat().st_mtime).isoformat()
            }
            
            # Contar proyectos en el archivo más reciente
            try:
                df = pd.read_csv(latest_data, encoding='utf-8-sig')
                status['total_projects'] = len(df)
                status['last_scraping'] = status['latest_data']['modified']
            except Exception as e:
                status['error'] = f"Error reading data file: {e}"
        
        # Contar archivos de log
        log_files = list(self.logs_dir.glob("*.log"))
        status['log_files'] = len(log_files)
        
        if log_files:
            latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
            status['latest_log'] = {
                'file': latest_log.name,
                'size': latest_log.stat().st_size,
                'modified': datetime.fromtimestamp(latest_log.stat().st_mtime).isoformat()
            }
        
        # Contar archivos de análisis
        analysis_files = list(self.analysis_dir.glob("*.json")) + list(self.analysis_dir.glob("*.csv"))
        status['analysis_files'] = len(analysis_files)
        
        # Determinar estado de salud
        if status['data_files'] > 0 and status['log_files'] > 0:
            # Verificar si el último scraping fue reciente (últimas 24 horas)
            if status['last_scraping']:
                last_scraping = datetime.fromisoformat(status['last_scraping'])
                hours_ago = (datetime.now() - last_scraping).total_seconds() / 3600
                if hours_ago < 24:
                    status['health_status'] = 'healthy'
                elif hours_ago < 168:  # 1 semana
                    status['health_status'] = 'warning'
                else:
                    status['health_status'] = 'stale'
            else:
                status['health_status'] = 'unknown'
        else:
            status['health_status'] = 'no_data'
        
        return status
    
    def get_data_summary(self) -> dict:
        """Obtener resumen de los datos disponibles"""
        summary = {
            'total_files': 0,
            'total_projects': 0,
            'date_range': None,
            'parties': [],
            'project_types': [],
            'latest_analysis': None
        }
        
        # Analizar archivos de datos
        data_files = list(self.data_dir.glob("proyectos_ley_*.csv"))
        summary['total_files'] = len(data_files)
        
        if data_files:
            # Combinar todos los datos
            all_data = []
            for file in data_files:
                try:
                    df = pd.read_csv(file, encoding='utf-8-sig')
                    all_data.append(df)
                except Exception as e:
                    continue
            
            if all_data:
                combined_df = pd.concat(all_data, ignore_index=True)
                summary['total_projects'] = len(combined_df)
                
                # Limpiar datos para análisis
                cleaner = DataCleaner()
                df_clean = cleaner.limpiar_dataframe(combined_df)
                
                # Obtener partidos políticos
                if 'partido_politico' in df_clean.columns:
                    parties = df_clean['partido_politico'].value_counts().head(10).to_dict()
                    summary['parties'] = parties
                
                # Obtener tipos de proyecto
                if 'tipo_proyecto' in df_clean.columns:
                    types = df_clean['tipo_proyecto'].value_counts().head(10).to_dict()
                    summary['project_types'] = types
                
                # Obtener rango de fechas
                if 'fecha_datetime' in df_clean.columns:
                    dates = df_clean['fecha_datetime'].dropna()
                    if not dates.empty:
                        summary['date_range'] = {
                            'start': dates.min().isoformat(),
                            'end': dates.max().isoformat()
                        }
        
        # Verificar último análisis
        analysis_files = list(self.analysis_dir.glob("resumen_analisis_*.json"))
        if analysis_files:
            latest_analysis = max(analysis_files, key=lambda x: x.stat().st_mtime)
            summary['latest_analysis'] = {
                'file': latest_analysis.name,
                'modified': datetime.fromtimestamp(latest_analysis.stat().st_mtime).isoformat()
            }
        
        return summary
    
    def get_recent_logs(self, lines: int = 20) -> list:
        """Obtener logs recientes"""
        log_files = list(self.logs_dir.glob("*.log"))
        if not log_files:
            return []
        
        latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
        
        try:
            with open(latest_log, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                return [line.strip() for line in all_lines[-lines:]]
        except Exception as e:
            return [f"Error reading log file: {e}"]
    
    def generate_dashboard_html(self, output_file: str = None) -> str:
        """Generar dashboard HTML"""
        if output_file is None:
            output_file = f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        # Obtener datos
        status = self.get_project_status()
        summary = self.get_data_summary()
        recent_logs = self.get_recent_logs()
        
        # Generar HTML
        html_content = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Peru Congress Laws Scraper - Dashboard</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                    color: #333;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border-radius: 10px;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 2.5em;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    opacity: 0.9;
                }}
                .dashboard-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .card {{
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .card h2 {{
                    margin-top: 0;
                    color: #2196F3;
                    border-bottom: 2px solid #2196F3;
                    padding-bottom: 10px;
                }}
                .status-indicator {{
                    display: inline-block;
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    margin-right: 8px;
                }}
                .status-healthy {{ background-color: #4CAF50; }}
                .status-warning {{ background-color: #FF9800; }}
                .status-stale {{ background-color: #F44336; }}
                .status-unknown {{ background-color: #9E9E9E; }}
                .status-no-data {{ background-color: #607D8B; }}
                .metric {{
                    display: flex;
                    justify-content: space-between;
                    margin: 10px 0;
                    padding: 8px 0;
                    border-bottom: 1px solid #eee;
                }}
                .metric:last-child {{
                    border-bottom: none;
                }}
                .metric-label {{
                    font-weight: 500;
                }}
                .metric-value {{
                    color: #2196F3;
                    font-weight: bold;
                }}
                .logs-container {{
                    background: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 5px;
                    padding: 15px;
                    max-height: 300px;
                    overflow-y: auto;
                    font-family: 'Courier New', monospace;
                    font-size: 0.9em;
                }}
                .log-entry {{
                    margin: 2px 0;
                    padding: 2px 0;
                }}
                .log-error {{ color: #dc3545; }}
                .log-warning {{ color: #fd7e14; }}
                .log-info {{ color: #17a2b8; }}
                .log-success {{ color: #28a745; }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding: 20px;
                    background: #f8f9fa;
                    border-radius: 10px;
                    color: #666;
                }}
                .refresh-btn {{
                    background: #2196F3;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 1em;
                    margin: 10px 0;
                }}
                .refresh-btn:hover {{
                    background: #1976D2;
                }}
            </style>
            <script>
                function refreshDashboard() {{
                    location.reload();
                }}
                
                // Auto-refresh cada 5 minutos
                setInterval(refreshDashboard, 300000);
            </script>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🇵🇪 Peru Congress Laws Scraper</h1>
                    <p>Dashboard de Monitoreo</p>
                    <p>Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                    <button class="refresh-btn" onclick="refreshDashboard()">🔄 Actualizar</button>
                </div>
                
                <div class="dashboard-grid">
                    <!-- Estado del Proyecto -->
                    <div class="card">
                        <h2>📊 Estado del Proyecto</h2>
                        <div class="metric">
                            <span class="metric-label">Estado de Salud:</span>
                            <span class="metric-value">
                                <span class="status-indicator status-{status['health_status']}"></span>
                                {status['health_status'].upper()}
                            </span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Archivos de Datos:</span>
                            <span class="metric-value">{status['data_files']}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Archivos de Log:</span>
                            <span class="metric-value">{status['log_files']}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Archivos de Análisis:</span>
                            <span class="metric-value">{status['analysis_files']}</span>
                        </div>
                        {f'''
                        <div class="metric">
                            <span class="metric-label">Último Scraping:</span>
                            <span class="metric-value">{status['last_scraping'][:16] if status['last_scraping'] else 'N/A'}</span>
                        </div>
                        ''' if status['last_scraping'] else ''}
                    </div>
                    
                    <!-- Resumen de Datos -->
                    <div class="card">
                        <h2>📈 Resumen de Datos</h2>
                        <div class="metric">
                            <span class="metric-label">Total Proyectos:</span>
                            <span class="metric-value">{summary['total_projects']:,}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Archivos Procesados:</span>
                            <span class="metric-value">{summary['total_files']}</span>
                        </div>
                        {f'''
                        <div class="metric">
                            <span class="metric-label">Rango de Fechas:</span>
                            <span class="metric-value">{summary['date_range']['start'][:10] if summary['date_range'] else 'N/A'}</span>
                        </div>
                        ''' if summary['date_range'] else ''}
                        {f'''
                        <div class="metric">
                            <span class="metric-label">Último Análisis:</span>
                            <span class="metric-value">{summary['latest_analysis']['modified'][:16] if summary['latest_analysis'] else 'N/A'}</span>
                        </div>
                        ''' if summary['latest_analysis'] else ''}
                    </div>
                    
                    <!-- Top Partidos -->
                    <div class="card">
                        <h2>🏛️ Top Partidos Políticos</h2>
                        {''.join([f'''
                        <div class="metric">
                            <span class="metric-label">{party}:</span>
                            <span class="metric-value">{count}</span>
                        </div>
                        ''' for party, count in list(summary['parties'].items())[:5]]) if summary['parties'] else '<p>No hay datos disponibles</p>'}
                    </div>
                    
                    <!-- Top Tipos de Proyecto -->
                    <div class="card">
                        <h2>📋 Top Tipos de Proyecto</h2>
                        {''.join([f'''
                        <div class="metric">
                            <span class="metric-label">{ptype}:</span>
                            <span class="metric-value">{count}</span>
                        </div>
                        ''' for ptype, count in list(summary['project_types'].items())[:5]]) if summary['project_types'] else '<p>No hay datos disponibles</p>'}
                    </div>
                </div>
                
                <!-- Logs Recientes -->
                <div class="card">
                    <h2>📝 Logs Recientes</h2>
                    <div class="logs-container">
                        {''.join([f'''
                        <div class="log-entry log-{self._get_log_level(line)}">{line}</div>
                        ''' for line in recent_logs]) if recent_logs else '<p>No hay logs disponibles</p>'}
                    </div>
                </div>
                
                <div class="footer">
                    <p>Dashboard generado automáticamente por Peru Congress Laws Scraper v2.0</p>
                    <p>Auto-actualización cada 5 minutos</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Guardar archivo
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_file
    
    def _get_log_level(self, line: str) -> str:
        """Determinar el nivel de log basado en el contenido de la línea"""
        if 'ERROR' in line or '❌' in line:
            return 'error'
        elif 'WARNING' in line or '⚠️' in line:
            return 'warning'
        elif 'INFO' in line or '✅' in line or '📊' in line:
            return 'info'
        elif 'SUCCESS' in line or '🎉' in line:
            return 'success'
        else:
            return 'info'
    
    def print_dashboard(self) -> None:
        """Imprimir dashboard en consola"""
        status = self.get_project_status()
        summary = self.get_data_summary()
        
        print("🇵🇪 PERU CONGRESS LAWS SCRAPER - DASHBOARD")
        print("=" * 60)
        print(f"📅 Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print()
        
        # Estado del proyecto
        print("📊 ESTADO DEL PROYECTO:")
        print(f"   Estado de salud: {status['health_status'].upper()}")
        print(f"   Archivos de datos: {status['data_files']}")
        print(f"   Archivos de log: {status['log_files']}")
        print(f"   Archivos de análisis: {status['analysis_files']}")
        if status['last_scraping']:
            print(f"   Último scraping: {status['last_scraping'][:16]}")
        print()
        
        # Resumen de datos
        print("📈 RESUMEN DE DATOS:")
        print(f"   Total proyectos: {summary['total_projects']:,}")
        print(f"   Archivos procesados: {summary['total_files']}")
        if summary['date_range']:
            print(f"   Rango de fechas: {summary['date_range']['start'][:10]} - {summary['date_range']['end'][:10]}")
        print()
        
        # Top partidos
        if summary['parties']:
            print("🏛️ TOP PARTIDOS POLÍTICOS:")
            for party, count in list(summary['parties'].items())[:5]:
                print(f"   {party}: {count}")
            print()
        
        # Top tipos de proyecto
        if summary['project_types']:
            print("📋 TOP TIPOS DE PROYECTO:")
            for ptype, count in list(summary['project_types'].items())[:5]:
                print(f"   {ptype}: {count}")
            print()
        
        print("=" * 60)


def main():
    """Función principal"""
    dashboard = ScraperDashboard()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--html':
        # Generar dashboard HTML
        html_file = dashboard.generate_dashboard_html()
        print(f"✅ Dashboard HTML generado: {html_file}")
    else:
        # Mostrar dashboard en consola
        dashboard.print_dashboard()


if __name__ == "__main__":
    main()
