#!/usr/bin/env python3
"""
Script para ejecutar análisis completo de datos de proyectos de ley
"""
import sys
import os
from pathlib import Path
from datetime import datetime

# Agregar el directorio padre al path
sys.path.append(str(Path(__file__).parent.parent))

from utils.limpieza import DataCleaner
from utils.data_validator import DataValidator
import pandas as pd
import glob


def run_complete_analysis():
    """Ejecuta análisis completo de todos los datos disponibles"""
    
    print("🚀 Iniciando análisis completo de proyectos de ley")
    print("=" * 60)
    
    # 1. Cargar datos
    data_files = glob.glob("../data/proyectos_ley_*.csv")
    if not data_files:
        print("❌ No se encontraron archivos de datos")
        return False
    
    print(f"📁 Archivos encontrados: {len(data_files)}")
    
    # Cargar y combinar datos
    dataframes = []
    for file in data_files:
        try:
            df = pd.read_csv(file, encoding='utf-8-sig')
            df['archivo_origen'] = os.path.basename(file)
            dataframes.append(df)
            print(f"✅ Cargado: {file} ({len(df)} registros)")
        except Exception as e:
            print(f"❌ Error cargando {file}: {e}")
    
    if not dataframes:
        print("❌ No se pudieron cargar datos")
        return False
    
    df_raw = pd.concat(dataframes, ignore_index=True)
    print(f"\n📊 Total de registros: {len(df_raw)}")
    
    # 2. Validar datos
    print("\n🔍 Validando calidad de datos...")
    validator = DataValidator()
    df_validated, validation_report = validator.validate_dataframe(df_raw)
    
    print(f"✅ Validación completada:")
    print(f"   - Registros válidos: {validation_report['valid_records']}")
    print(f"   - Registros inválidos: {validation_report['invalid_records']}")
    print(f"   - Errores: {validation_report['total_errors']}")
    print(f"   - Advertencias: {validation_report['total_warnings']}")
    
    # 3. Limpiar datos
    print("\n🧹 Limpiando datos...")
    cleaner = DataCleaner()
    df_clean = cleaner.limpiar_dataframe(df_validated)
    
    print(f"✅ Limpieza completada: {len(df_clean)} registros")
    
    # 4. Generar resumen
    print("\n📊 Generando resumen estadístico...")
    resumen = cleaner.generar_resumen(df_clean)
    
    print(f"✅ Resumen generado:")
    print(f"   - Total proyectos: {resumen['total_projects']}")
    print(f"   - Período: {resumen['fecha_inicio']} - {resumen['fecha_fin']}")
    print(f"   - Promedio autores: {resumen['promedio_autores']:.1f}")
    print(f"   - Más activo: {resumen['congresista_mas_activo']}")
    
    # 5. Exportar resultados
    print("\n📤 Exportando resultados...")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Crear directorios
    Path("../analysis").mkdir(exist_ok=True)
    Path("../reports").mkdir(exist_ok=True)
    
    # Exportar datos limpios
    clean_file = f"../data/proyectos_ley_limpios_{timestamp}.csv"
    df_clean.to_csv(clean_file, index=False, encoding='utf-8-sig')
    print(f"✅ Datos limpios: {clean_file}")
    
    # Exportar resumen
    summary_file = f"../analysis/resumen_analisis_{timestamp}.json"
    import json
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(resumen, f, indent=2, default=str)
    print(f"✅ Resumen: {summary_file}")
    
    # Exportar estadísticas por partido
    if 'partido_politico' in df_clean.columns:
        party_stats = df_clean['partido_politico'].value_counts().reset_index()
        party_stats.columns = ['partido', 'proyectos']
        party_file = f"../analysis/estadisticas_partidos_{timestamp}.csv"
        party_stats.to_csv(party_file, index=False, encoding='utf-8-sig')
        print(f"✅ Estadísticas por partido: {party_file}")
    
    # Exportar estadísticas por tipo
    if 'tipo_proyecto' in df_clean.columns:
        type_stats = df_clean['tipo_proyecto'].value_counts().reset_index()
        type_stats.columns = ['tipo', 'proyectos']
        type_file = f"../analysis/estadisticas_tipos_{timestamp}.csv"
        type_stats.to_csv(type_file, index=False, encoding='utf-8-sig')
        print(f"✅ Estadísticas por tipo: {type_file}")
    
    # 6. Mostrar resumen final
    print("\n🎉 ANÁLISIS COMPLETADO EXITOSAMENTE")
    print("=" * 60)
    print(f"📊 Total proyectos analizados: {len(df_clean)}")
    print(f"🏛️ Partidos políticos: {len(resumen.get('proyectos_por_partido', {}))}")
    print(f"📋 Tipos de proyecto: {len(resumen.get('proyectos_por_tipo', {}))}")
    print(f"📅 Período: {resumen.get('fecha_inicio')} - {resumen.get('fecha_fin')}")
    print(f"👤 Congresista más activo: {resumen.get('congresista_mas_activo')}")
    
    print(f"\n📁 Archivos generados:")
    print(f"   - Datos limpios: {clean_file}")
    print(f"   - Resumen JSON: {summary_file}")
    if 'partido_politico' in df_clean.columns:
        print(f"   - Estadísticas partidos: {party_file}")
    if 'tipo_proyecto' in df_clean.columns:
        print(f"   - Estadísticas tipos: {type_file}")
    
    return True


def main():
    """Función principal"""
    try:
        success = run_complete_analysis()
        if success:
            print("\n✅ Análisis completado exitosamente")
            return 0
        else:
            print("\n❌ Error en el análisis")
            return 1
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
