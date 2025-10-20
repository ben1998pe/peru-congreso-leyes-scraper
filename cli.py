"""
Command Line Interface for Peru Congress Laws Scraper
"""
import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json
import logging

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from scraper_enhanced import EnhancedCongresoScraper
from utils.data_validator import DataValidator
from utils.limpieza import DataCleaner, limpiar_archivo_csv
from utils.logging_config import get_logger
from utils.performance_monitor import PerformanceMonitor
from utils.notifications import get_notification_manager
from utils.metrics_collector import get_metrics_collector
from utils.report_generator import get_report_generator
from config.environment import env


class ScraperCLI:
    """Command Line Interface for the scraper"""
    
    def __init__(self):
        self.logger = get_logger("cli")
        self.setup_argparser()
    
    def setup_argparser(self):
        """Setup argument parser"""
        self.parser = argparse.ArgumentParser(
            description="Peru Congress Laws Scraper - Enhanced Version",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Basic scraping (last 7 days)
  python cli.py scrape
  
  # Scraping with custom date range
  python cli.py scrape --fecha-desde "01/01/2024" --fecha-hasta "31/01/2024"
  
  # Scraping with monitoring
  python cli.py scrape --monitor --output "data/my_data.csv"
  
  # Clean existing data
  python cli.py clean --input "data/raw_data.csv" --output "data/clean_data.csv"
  
  # Validate data
  python cli.py validate --input "data/data.csv"
  
  # Run analysis
  python cli.py analyze --input "data/data.csv"
            """
        )
        
        # Subcommands
        subparsers = self.parser.add_subparsers(dest='command', help='Available commands')
        
        # Scraping command
        scrape_parser = subparsers.add_parser('scrape', help='Scrape law projects')
        scrape_parser.add_argument('--fecha-desde', type=str, help='Start date (DD/MM/YYYY)')
        scrape_parser.add_argument('--fecha-hasta', type=str, help='End date (DD/MM/YYYY)')
        scrape_parser.add_argument('--output', '-o', type=str, help='Output CSV file')
        scrape_parser.add_argument('--headless', action='store_true', default=True, help='Run in headless mode')
        scrape_parser.add_argument('--monitor', action='store_true', help='Enable performance monitoring')
        scrape_parser.add_argument('--max-pages', type=int, default=50, help='Maximum pages to scrape')
        scrape_parser.add_argument('--retries', type=int, default=3, help='Maximum retries')
        
        # Clean command
        clean_parser = subparsers.add_parser('clean', help='Clean and process data')
        clean_parser.add_argument('--input', '-i', type=str, required=True, help='Input CSV file')
        clean_parser.add_argument('--output', '-o', type=str, help='Output CSV file')
        clean_parser.add_argument('--show-stats', action='store_true', help='Show cleaning statistics')
        
        # Validate command
        validate_parser = subparsers.add_parser('validate', help='Validate data quality')
        validate_parser.add_argument('--input', '-i', type=str, required=True, help='Input CSV file')
        validate_parser.add_argument('--output', '-o', type=str, help='Output validation report')
        validate_parser.add_argument('--strict', action='store_true', help='Strict validation mode')
        
        # Analyze command
        analyze_parser = subparsers.add_parser('analyze', help='Analyze scraped data')
        analyze_parser.add_argument('--input', '-i', type=str, required=True, help='Input CSV file')
        analyze_parser.add_argument('--output', '-o', type=str, help='Output analysis directory')
        analyze_parser.add_argument('--format', choices=['csv', 'json', 'html'], default='csv', help='Output format')
        
        # Monitor command
        monitor_parser = subparsers.add_parser('monitor', help='Monitor system performance')
        monitor_parser.add_argument('--duration', type=int, default=60, help='Monitoring duration in seconds')
        monitor_parser.add_argument('--output', '-o', type=str, help='Output metrics file')
        
        # Config command
        config_parser = subparsers.add_parser('config', help='Show configuration')
        config_parser.add_argument('--format', choices=['json', 'yaml'], default='json', help='Output format')
        
        # Dashboard command
        dashboard_parser = subparsers.add_parser('dashboard', help='Generate dashboard')
        dashboard_parser.add_argument('--output', '-o', type=str, help='Output HTML file')
        dashboard_parser.add_argument('--console', action='store_true', help='Show dashboard in console')
        
        # Notifications command
        notify_parser = subparsers.add_parser('notify', help='Manage notifications')
        notify_parser.add_argument('--test', action='store_true', help='Test notifications')
        notify_parser.add_argument('--enable', action='store_true', help='Enable notifications')
        notify_parser.add_argument('--disable', action='store_true', help='Disable notifications')
        
        # Metrics command
        metrics_parser = subparsers.add_parser('metrics', help='View and manage metrics')
        metrics_parser.add_argument('--summary', action='store_true', help='Show metrics summary')
        metrics_parser.add_argument('--export', type=str, help='Export metrics report')
        metrics_parser.add_argument('--days', type=int, default=7, help='Number of days to analyze')
        
        # Reports command
        reports_parser = subparsers.add_parser('reports', help='Generate reports')
        reports_parser.add_argument('--type', choices=['executive', 'analytics', 'metrics'], required=True, help='Report type')
        reports_parser.add_argument('--input', '-i', type=str, help='Input data file')
        reports_parser.add_argument('--output', '-o', type=str, help='Output report file')
    
    def run(self, args=None):
        """Run the CLI"""
        if args is None:
            args = sys.argv[1:]
        
        parsed_args = self.parser.parse_args(args)
        
        if not parsed_args.command:
            self.parser.print_help()
            return 1
        
        try:
            if parsed_args.command == 'scrape':
                return self.handle_scrape(parsed_args)
            elif parsed_args.command == 'clean':
                return self.handle_clean(parsed_args)
            elif parsed_args.command == 'validate':
                return self.handle_validate(parsed_args)
            elif parsed_args.command == 'analyze':
                return self.handle_analyze(parsed_args)
            elif parsed_args.command == 'monitor':
                return self.handle_monitor(parsed_args)
            elif parsed_args.command == 'config':
                return self.handle_config(parsed_args)
            elif parsed_args.command == 'dashboard':
                return self.handle_dashboard(parsed_args)
            elif parsed_args.command == 'notify':
                return self.handle_notifications(parsed_args)
            elif parsed_args.command == 'metrics':
                return self.handle_metrics(parsed_args)
            elif parsed_args.command == 'reports':
                return self.handle_reports(parsed_args)
            else:
                self.logger.error(f"Unknown command: {parsed_args.command}")
                return 1
                
        except KeyboardInterrupt:
            self.logger.info("Operation cancelled by user")
            return 1
        except Exception as e:
            self.logger.error(f"Error executing command: {e}")
            return 1
    
    def handle_scrape(self, args):
        """Handle scraping command"""
        self.logger.info("🚀 Starting scraping operation")
        
        # Setup dates
        fecha_desde = args.fecha_desde
        fecha_hasta = args.fecha_hasta
        
        if not fecha_desde:
            fecha_desde = (datetime.now() - timedelta(days=7)).strftime("%d/%m/%Y")
        if not fecha_hasta:
            fecha_hasta = datetime.now().strftime("%d/%m/%Y")
        
        # Create scraper
        scraper = EnhancedCongresoScraper(
            headless=args.headless,
            enable_monitoring=args.monitor
        )
        
        try:
            # Execute scraping
            proyectos = scraper.scrape(fecha_desde, fecha_hasta)
            
            if not proyectos:
                self.logger.warning("No projects found")
                return 1
            
            # Save data
            output_file = args.output
            if not output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"data/proyectos_ley_{timestamp}.csv"
            
            filename = scraper.save_to_csv(proyectos, output_file)
            
            # Show statistics
            stats = scraper.get_statistics()
            self.logger.info(f"✅ Scraping completed successfully")
            self.logger.info(f"📊 Projects found: {stats['projects_found']}")
            self.logger.info(f"📄 Pages scraped: {stats['pages_scraped']}")
            self.logger.info(f"⏱️ Duration: {stats.get('duration_seconds', 0):.2f} seconds")
            self.logger.info(f"💾 Data saved to: {filename}")
            
            return 0
            
        finally:
            scraper.close()
    
    def handle_clean(self, args):
        """Handle data cleaning command"""
        self.logger.info("🧹 Starting data cleaning operation")
        
        input_file = args.input
        if not Path(input_file).exists():
            self.logger.error(f"Input file not found: {input_file}")
            return 1
        
        try:
            # Clean data
            output_file = args.output or input_file.replace('.csv', '_clean.csv')
            clean_file = limpiar_archivo_csv(input_file, output_file)
            
            self.logger.info(f"✅ Data cleaning completed")
            self.logger.info(f"💾 Clean data saved to: {clean_file}")
            
            if args.show_stats:
                # Load and show statistics
                import pandas as pd
                df = pd.read_csv(clean_file)
                self.logger.info(f"📊 Clean records: {len(df)}")
                if 'partido_politico' in df.columns:
                    self.logger.info(f"🏛️ Parties: {df['partido_politico'].nunique()}")
                if 'tipo_proyecto' in df.columns:
                    self.logger.info(f"📋 Project types: {df['tipo_proyecto'].nunique()}")
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Error cleaning data: {e}")
            return 1
    
    def handle_validate(self, args):
        """Handle data validation command"""
        self.logger.info("🔍 Starting data validation operation")
        
        input_file = args.input
        if not Path(input_file).exists():
            self.logger.error(f"Input file not found: {input_file}")
            return 1
        
        try:
            import pandas as pd
            validator = DataValidator()
            
            # Load data
            df = pd.read_csv(input_file)
            self.logger.info(f"📂 Loaded {len(df)} records for validation")
            
            # Validate data
            df_clean, validation_report = validator.validate_dataframe(df)
            
            # Show validation summary
            summary = validator.get_validation_summary(validation_report)
            self.logger.info(f"\n{summary}")
            
            # Save validation report
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(validation_report, f, indent=2, default=str)
                self.logger.info(f"📋 Validation report saved to: {args.output}")
            
            # Save cleaned data if there are differences
            if len(df_clean) != len(df):
                clean_file = input_file.replace('.csv', '_validated.csv')
                df_clean.to_csv(clean_file, index=False, encoding='utf-8-sig')
                self.logger.info(f"💾 Validated data saved to: {clean_file}")
            
            return 0 if validation_report['invalid_records'] == 0 else 1
            
        except Exception as e:
            self.logger.error(f"Error validating data: {e}")
            return 1
    
    def handle_analyze(self, args):
        """Handle data analysis command"""
        self.logger.info("📊 Starting data analysis operation")
        
        input_file = args.input
        if not Path(input_file).exists():
            self.logger.error(f"Input file not found: {input_file}")
            return 1
        
        try:
            import pandas as pd
            from utils.limpieza import DataCleaner
            
            # Load and clean data
            df = pd.read_csv(input_file)
            cleaner = DataCleaner()
            df_clean = cleaner.limpiar_dataframe(df)
            
            # Generate analysis
            resumen = cleaner.generar_resumen(df_clean)
            
            # Show analysis
            self.logger.info("📊 ANALYSIS RESULTS")
            self.logger.info("=" * 50)
            self.logger.info(f"Total projects: {resumen['total_projects']}")
            self.logger.info(f"Date range: {resumen['fecha_inicio']} - {resumen['fecha_fin']}")
            self.logger.info(f"Average authors: {resumen['promedio_autores']:.1f}")
            self.logger.info(f"Most active congressperson: {resumen['congresista_mas_activo']}")
            
            # Top parties
            self.logger.info("\n🏛️ TOP PARTIES:")
            for i, (partido, count) in enumerate(list(resumen['proyectos_por_partido'].items())[:5], 1):
                self.logger.info(f"  {i}. {partido}: {count} projects")
            
            # Top project types
            self.logger.info("\n📋 TOP PROJECT TYPES:")
            for i, (tipo, count) in enumerate(list(resumen['proyectos_por_tipo'].items())[:5], 1):
                self.logger.info(f"  {i}. {tipo}: {count} projects")
            
            # Save analysis
            if args.output:
                output_dir = Path(args.output)
                output_dir.mkdir(parents=True, exist_ok=True)
                
                if args.format == 'json':
                    with open(output_dir / 'analysis.json', 'w', encoding='utf-8') as f:
                        json.dump(resumen, f, indent=2, default=str)
                elif args.format == 'csv':
                    # Save summary as CSV
                    summary_df = pd.DataFrame([resumen])
                    summary_df.to_csv(output_dir / 'analysis_summary.csv', index=False)
                elif args.format == 'html':
                    # Generate HTML report
                    self._generate_html_report(resumen, output_dir / 'analysis_report.html')
                
                self.logger.info(f"📊 Analysis saved to: {output_dir}")
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Error analyzing data: {e}")
            return 1
    
    def handle_monitor(self, args):
        """Handle performance monitoring command"""
        self.logger.info("📈 Starting performance monitoring")
        
        monitor = PerformanceMonitor()
        monitor.start_monitoring()
        
        try:
            import time
            self.logger.info(f"Monitoring for {args.duration} seconds...")
            time.sleep(args.duration)
            
            # Get summary
            summary = monitor.get_performance_summary()
            
            self.logger.info("📊 PERFORMANCE SUMMARY")
            self.logger.info("=" * 40)
            self.logger.info(f"CPU - Current: {summary['cpu']['current']:.1f}%, Average: {summary['cpu']['average']:.1f}%")
            self.logger.info(f"Memory - Current: {summary['memory']['current_mb']:.1f}MB, Average: {summary['memory']['average_mb']:.1f}MB")
            self.logger.info(f"Threads - Current: {summary['threads']['current']}, Max: {summary['threads']['max']}")
            
            # Export metrics
            if args.output:
                monitor.export_metrics(Path(args.output))
                self.logger.info(f"📊 Metrics exported to: {args.output}")
            
            return 0
            
        finally:
            monitor.stop_monitoring()
    
    def handle_config(self, args):
        """Handle configuration command"""
        config_dict = env.get_config_dict()
        
        if args.format == 'json':
            print(json.dumps(config_dict, indent=2, default=str))
        elif args.format == 'yaml':
            import yaml
            print(yaml.dump(config_dict, default_flow_style=False))
        
        return 0
    
    def handle_dashboard(self, args):
        """Handle dashboard command"""
        from dashboard import ScraperDashboard
        
        self.logger.info("📊 Generando dashboard...")
        
        dashboard = ScraperDashboard()
        
        if args.console:
            dashboard.print_dashboard()
        else:
            html_file = dashboard.generate_dashboard_html(args.output)
            self.logger.info(f"✅ Dashboard HTML generado: {html_file}")
        
        return 0
    
    def handle_notifications(self, args):
        """Handle notifications command"""
        notification_manager = get_notification_manager()
        
        if args.test:
            self.logger.info("🧪 Probando notificaciones...")
            results = notification_manager.test_notifications()
            
            self.logger.info("📊 Resultados de prueba:")
            for channel, success in results.items():
                status = "✅" if success else "❌"
                self.logger.info(f"   {status} {channel}")
            
            return 0 if all(results.values()) else 1
        
        elif args.enable:
            self.logger.info("🔔 Habilitando notificaciones...")
            # Aquí podrías agregar lógica para habilitar notificaciones
            self.logger.info("💡 Configure las notificaciones en config/notifications.json")
            return 0
        
        elif args.disable:
            self.logger.info("🔕 Deshabilitando notificaciones...")
            # Aquí podrías agregar lógica para deshabilitar notificaciones
            self.logger.info("💡 Modifique config/notifications.json para deshabilitar")
            return 0
        
        else:
            # Mostrar estado de notificaciones
            status = "habilitadas" if notification_manager.enabled else "deshabilitadas"
            self.logger.info(f"📧 Estado de notificaciones: {status}")
            
            if notification_manager.enabled:
                channels = []
                if notification_manager.config['email']['enabled']:
                    channels.append("Email")
                if notification_manager.config['slack']['enabled']:
                    channels.append("Slack")
                if notification_manager.config['telegram']['enabled']:
                    channels.append("Telegram")
                
                if channels:
                    self.logger.info(f"📱 Canales activos: {', '.join(channels)}")
                else:
                    self.logger.info("⚠️ No hay canales configurados")
            
            return 0
    
    def handle_metrics(self, args):
        """Handle metrics command"""
        metrics_collector = get_metrics_collector()
        
        if args.summary:
            self.logger.info("📊 Generando resumen de métricas...")
            summary = metrics_collector.get_session_summary(args.days)
            quality_summary = metrics_collector.get_quality_summary(args.days)
            
            self.logger.info("📈 RESUMEN DE SESIONES:")
            self.logger.info(f"   Período: {summary.get('period_days', 0)} días")
            self.logger.info(f"   Sesiones totales: {summary.get('total_sessions', 0)}")
            self.logger.info(f"   Proyectos extraídos: {summary.get('total_projects', 0)}")
            self.logger.info(f"   Tasa de éxito promedio: {summary.get('average_success_rate', 0)}%")
            self.logger.info(f"   Velocidad promedio: {summary.get('average_projects_per_minute', 0)} proyectos/min")
            
            self.logger.info("\n📊 RESUMEN DE CALIDAD:")
            self.logger.info(f"   Registros totales: {quality_summary.get('total_records', 0)}")
            self.logger.info(f"   Registros válidos: {quality_summary.get('valid_records', 0)}")
            self.logger.info(f"   Completitud promedio: {quality_summary.get('average_completeness', 0)}%")
            self.logger.info(f"   Precisión promedio: {quality_summary.get('average_accuracy', 0)}%")
            self.logger.info(f"   Puntuación de calidad: {quality_summary.get('data_quality_score', 0)}%")
            
            return 0
        
        elif args.export:
            self.logger.info(f"📤 Exportando reporte de métricas...")
            report_file = metrics_collector.export_metrics_report(args.export)
            self.logger.info(f"✅ Reporte exportado: {report_file}")
            return 0
        
        else:
            self.logger.info("📊 Comandos de métricas disponibles:")
            self.logger.info("   --summary    Mostrar resumen de métricas")
            self.logger.info("   --export     Exportar reporte de métricas")
            self.logger.info("   --days       Número de días a analizar (default: 7)")
            return 0
    
    def handle_reports(self, args):
        """Handle reports command"""
        report_generator = get_report_generator()
        
        if args.type == 'executive':
            self.logger.info("📊 Generando resumen ejecutivo...")
            
            # Cargar datos si se proporciona archivo
            if args.input:
                try:
                    df = pd.read_csv(args.input, encoding='utf-8-sig')
                    from utils.limpieza import DataCleaner
                    cleaner = DataCleaner()
                    df_clean = cleaner.limpiar_dataframe(df)
                    resumen = cleaner.generar_resumen(df_clean)
                except Exception as e:
                    self.logger.error(f"Error cargando datos: {e}")
                    return 1
            else:
                # Usar datos de ejemplo
                resumen = {
                    'total_projects': 0,
                    'parties': {},
                    'project_types': {},
                    'avg_authors': 0,
                    'data_quality_score': 0
                }
            
            report_file = report_generator.generate_executive_summary(resumen, args.output)
            self.logger.info(f"✅ Resumen ejecutivo generado: {report_file}")
            return 0
        
        elif args.type == 'analytics':
            self.logger.info("📊 Generando reporte de análisis...")
            
            if not args.input:
                self.logger.error("Se requiere archivo de entrada para reporte de análisis")
                return 1
            
            try:
                df = pd.read_csv(args.input, encoding='utf-8-sig')
                report_file = report_generator.generate_analytics_report(df, args.output)
                self.logger.info(f"✅ Reporte de análisis generado: {report_file}")
                return 0
            except Exception as e:
                self.logger.error(f"Error generando reporte de análisis: {e}")
                return 1
        
        elif args.type == 'metrics':
            self.logger.info("📊 Generando reporte de métricas...")
            
            metrics_collector = get_metrics_collector()
            session_summary = metrics_collector.get_session_summary()
            quality_summary = metrics_collector.get_quality_summary()
            
            # Combinar métricas
            metrics_data = {**session_summary, **quality_summary}
            
            report_file = report_generator.generate_metrics_report(metrics_data, args.output)
            self.logger.info(f"✅ Reporte de métricas generado: {report_file}")
            return 0
        
        return 0
    
    def _generate_html_report(self, resumen, output_file):
        """Generate HTML analysis report"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Peru Congress Laws Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #333; }}
                h2 {{ color: #666; }}
                .summary {{ background-color: #f5f5f5; padding: 20px; border-radius: 5px; }}
                .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .stat {{ text-align: center; }}
                .stat-value {{ font-size: 24px; font-weight: bold; color: #2196F3; }}
                .stat-label {{ color: #666; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>📊 Peru Congress Laws Analysis Report</h1>
            <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <div class="summary">
                <h2>📈 Summary</h2>
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value">{resumen['total_projects']}</div>
                        <div class="stat-label">Total Projects</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{resumen['promedio_autores']:.1f}</div>
                        <div class="stat-label">Avg Authors</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{resumen['fecha_inicio'].strftime('%d/%m/%Y') if resumen['fecha_inicio'] else 'N/A'}</div>
                        <div class="stat-label">Start Date</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{resumen['fecha_fin'].strftime('%d/%m/%Y') if resumen['fecha_fin'] else 'N/A'}</div>
                        <div class="stat-label">End Date</div>
                    </div>
                </div>
            </div>
            
            <h2>🏛️ Projects by Party</h2>
            <table>
                <tr><th>Party</th><th>Projects</th></tr>
        """
        
        for partido, count in list(resumen['proyectos_por_partido'].items())[:10]:
            html_content += f"<tr><td>{partido}</td><td>{count}</td></tr>"
        
        html_content += """
            </table>
            
            <h2>📋 Projects by Type</h2>
            <table>
                <tr><th>Type</th><th>Projects</th></tr>
        """
        
        for tipo, count in list(resumen['proyectos_por_tipo'].items())[:10]:
            html_content += f"<tr><td>{tipo}</td><td>{count}</td></tr>"
        
        html_content += """
            </table>
            
            <h2>👤 Most Active Congressperson</h2>
            <p><strong>{}</strong></p>
        """.format(resumen['congresista_mas_activo'])
        
        html_content += """
        </body>
        </html>
        """
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)


def main():
    """Main CLI entry point"""
    cli = ScraperCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
