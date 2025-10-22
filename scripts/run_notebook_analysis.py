#!/usr/bin/env python3
"""
Script para ejecutar automáticamente el análisis del notebook
"""
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def run_notebook_analysis():
    """Ejecutar el análisis del notebook automáticamente"""
    
    print("🚀 Iniciando análisis automático del notebook...")
    
    # Verificar que el notebook existe
    notebook_path = Path("notebooks/analisis.ipynb")
    if not notebook_path.exists():
        print("❌ No se encontró el notebook de análisis")
        return False
    
    # Verificar que hay datos para analizar
    data_dir = Path("data")
    csv_files = list(data_dir.glob("proyectos_ley_*.csv"))
    
    if not csv_files:
        print("⚠️ No se encontraron archivos de datos. Ejecutando scraping primero...")
        
        # Intentar ejecutar scraping
        try:
            result = subprocess.run([sys.executable, "cli.py", "scrape", "--headless"], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                print(f"❌ Error en scraping: {result.stderr}")
                return False
            print("✅ Scraping completado")
        except subprocess.TimeoutExpired:
            print("⏰ Timeout en scraping")
            return False
        except Exception as e:
            print(f"❌ Error ejecutando scraping: {e}")
            return False
    
    # Ejecutar el notebook
    try:
        print("📊 Ejecutando análisis del notebook...")
        
        # Usar nbconvert para ejecutar el notebook
        cmd = [
            sys.executable, "-m", "jupyter", "nbconvert", 
            "--to", "notebook", 
            "--execute", 
            "--inplace",
            str(notebook_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print("✅ Análisis del notebook completado exitosamente")
            
            # Generar reporte HTML
            print("📄 Generando reporte HTML...")
            html_cmd = [
                sys.executable, "-m", "jupyter", "nbconvert",
                "--to", "html",
                "--output", f"analisis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                str(notebook_path)
            ]
            
            subprocess.run(html_cmd, capture_output=True, text=True)
            print("✅ Reporte HTML generado")
            
            return True
        else:
            print(f"❌ Error ejecutando notebook: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout ejecutando notebook")
        return False
    except Exception as e:
        print(f"❌ Error ejecutando notebook: {e}")
        return False

def main():
    """Función principal"""
    print("=" * 60)
    print("📊 ANALIZADOR AUTOMÁTICO DE PROYECTOS DE LEY")
    print("=" * 60)
    
    success = run_notebook_analysis()
    
    if success:
        print("\n🎉 Análisis completado exitosamente!")
        print("📁 Revisa los archivos generados en:")
        print("   - notebooks/analisis.ipynb (notebook ejecutado)")
        print("   - reports/ (reportes generados)")
        print("   - exports/ (datos exportados)")
    else:
        print("\n❌ Error en el análisis")
        sys.exit(1)

if __name__ == "__main__":
    main()
