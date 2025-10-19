#!/usr/bin/env python3
"""
Script de verificación de salud del proyecto Peru Congress Laws Scraper
"""
import sys
import os
from pathlib import Path
from datetime import datetime

# Agregar el directorio padre al path
sys.path.append(str(Path(__file__).parent.parent))

def check_project_health():
    """Verifica la salud general del proyecto"""
    
    print("🏥 Verificación de Salud del Proyecto")
    print("=" * 50)
    
    issues = []
    warnings = []
    
    # 1. Verificar estructura de directorios
    print("📁 Verificando estructura de directorios...")
    required_dirs = [
        "data", "logs", "analysis", "reports", "visualizations",
        "utils", "tests", "scripts", "config"
    ]
    
    for dir_name in required_dirs:
        dir_path = Path(f"../{dir_name}")
        if dir_path.exists():
            print(f"   ✅ {dir_name}/")
        else:
            print(f"   ❌ {dir_name}/ (faltante)")
            issues.append(f"Directorio faltante: {dir_name}")
    
    # 2. Verificar archivos principales
    print("\n📄 Verificando archivos principales...")
    required_files = [
        "scraper_enhanced.py", "cli.py", "config.py", "requirements.txt",
        "README.md", "setup.py", "Makefile"
    ]
    
    for file_name in required_files:
        file_path = Path(f"../{file_name}")
        if file_path.exists():
            print(f"   ✅ {file_name}")
        else:
            print(f"   ❌ {file_name} (faltante)")
            issues.append(f"Archivo faltante: {file_name}")
    
    # 3. Verificar utilidades
    print("\n🔧 Verificando utilidades...")
    utils_files = [
        "utils/limpieza.py", "utils/data_validator.py", 
        "utils/logging_config.py", "utils/performance_monitor.py"
    ]
    
    for file_name in utils_files:
        file_path = Path(f"../{file_name}")
        if file_path.exists():
            print(f"   ✅ {file_name}")
        else:
            print(f"   ❌ {file_name} (faltante)")
            issues.append(f"Utilidad faltante: {file_name}")
    
    # 4. Verificar datos
    print("\n📊 Verificando datos...")
    data_files = list(Path("../data").glob("proyectos_ley_*.csv"))
    if data_files:
        print(f"   ✅ {len(data_files)} archivos de datos encontrados")
        for file in data_files[:3]:  # Mostrar solo los primeros 3
            print(f"      - {file.name}")
        if len(data_files) > 3:
            print(f"      ... y {len(data_files) - 3} más")
    else:
        print("   ⚠️ No se encontraron archivos de datos")
        warnings.append("No hay datos para analizar")
    
    # 5. Verificar logs
    print("\n📝 Verificando logs...")
    log_files = list(Path("../logs").glob("*.log"))
    if log_files:
        print(f"   ✅ {len(log_files)} archivos de log encontrados")
        latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
        print(f"      - Último log: {latest_log.name}")
    else:
        print("   ⚠️ No se encontraron archivos de log")
        warnings.append("No hay logs disponibles")
    
    # 6. Verificar dependencias
    print("\n📦 Verificando dependencias...")
    try:
        import pandas
        import selenium
        import plotly
        import requests
        print("   ✅ Dependencias principales disponibles")
    except ImportError as e:
        print(f"   ❌ Dependencia faltante: {e}")
        issues.append(f"Dependencia faltante: {e}")
    
    # 7. Verificar configuración
    print("\n⚙️ Verificando configuración...")
    try:
        import config
        print("   ✅ Configuración cargada correctamente")
    except Exception as e:
        print(f"   ❌ Error en configuración: {e}")
        issues.append(f"Error en configuración: {e}")
    
    # 8. Resumen de salud
    print("\n🏥 RESUMEN DE SALUD")
    print("=" * 50)
    
    if not issues:
        print("✅ PROYECTO SALUDABLE")
        print("   No se encontraron problemas críticos")
    else:
        print("❌ PROBLEMAS ENCONTRADOS:")
        for issue in issues:
            print(f"   - {issue}")
    
    if warnings:
        print("\n⚠️ ADVERTENCIAS:")
        for warning in warnings:
            print(f"   - {warning}")
    
    # 9. Recomendaciones
    print("\n💡 RECOMENDACIONES:")
    if not data_files:
        print("   - Ejecutar scraping para obtener datos")
    if not log_files:
        print("   - Ejecutar el scraper para generar logs")
    if issues:
        print("   - Resolver los problemas críticos antes de continuar")
    else:
        print("   - El proyecto está listo para usar")
        print("   - Ejecutar 'make test' para verificar funcionalidad")
    
    print(f"\n📅 Verificación completada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return len(issues) == 0


def main():
    """Función principal"""
    try:
        success = check_project_health()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ Error durante la verificación: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
