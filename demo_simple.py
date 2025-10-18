"""
Demo simple sin emojis para evitar problemas de codificación
"""
import pandas as pd
from utils.limpieza import DataCleaner
from datetime import datetime

def demo_simple():
    print("=" * 60)
    print("DEMO DE ANALISIS - DATOS DEL CONGRESO DEL PERU")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    # Cargar datos existentes
    print("\n1. CARGANDO DATOS EXISTENTES...")
    print("-" * 30)
    
    try:
        # Cargar datos del 17 de octubre
        df_raw = pd.read_csv('data/proyectos_ley_2025-10-17.csv', encoding='utf-8-sig')
        print(f"[OK] Datos cargados: {len(df_raw)} registros del 17/10/2025")
        
        # Mostrar estructura
        print(f"[INFO] Columnas disponibles: {list(df_raw.columns)}")
        print(f"[INFO] Primeros 3 proyectos:")
        for i, (_, row) in enumerate(df_raw.head(3).iterrows(), 1):
            print(f"   {i}. {row['proyecto']} - {row['titulo'][:50]}...")
        
    except Exception as e:
        print(f"[ERROR] Error cargando datos: {e}")
        return
    
    # Aplicar limpieza
    print("\n2. APLICANDO LIMPIEZA DE DATOS...")
    print("-" * 30)
    
    try:
        cleaner = DataCleaner()
        df_clean = cleaner.limpiar_dataframe(df_raw)
        print(f"[OK] Limpieza completada: {len(df_clean)} registros")
        
        # Mostrar nuevas columnas
        nuevas_columnas = [col for col in df_clean.columns if col not in df_raw.columns]
        print(f"[INFO] Nuevas columnas agregadas: {len(nuevas_columnas)}")
        for col in nuevas_columnas:
            print(f"   - {col}")
        
    except Exception as e:
        print(f"[ERROR] Error en limpieza: {e}")
        return
    
    # Análisis estadístico
    print("\n3. ANALISIS ESTADISTICO...")
    print("-" * 30)
    
    try:
        resumen = cleaner.generar_resumen(df_clean)
        
        print("[RESUMEN] GENERAL:")
        print(f"   - Total proyectos: {resumen['total_proyectos']}")
        print(f"   - Fecha: {resumen['fecha_inicio'].strftime('%d/%m/%Y')}")
        print(f"   - Promedio autores: {resumen['promedio_autores']:.1f}")
        print(f"   - Congresista mas activo: {resumen['congresista_mas_activo']}")
        
        # Análisis por tipo
        print(f"\n[TIPOS] DE PROYECTOS:")
        for tipo, count in resumen['proyectos_por_tipo'].items():
            porcentaje = (count / resumen['total_proyectos']) * 100
            print(f"   - {tipo}: {count} proyectos ({porcentaje:.1f}%)")
        
        # Análisis por región
        if resumen['proyectos_por_region']:
            print(f"\n[REGIONES] MENCIONADAS:")
            for region, count in resumen['proyectos_por_region'].items():
                print(f"   - {region}: {count} proyectos")
        
        # Análisis de autores
        print(f"\n[AUTORES] ANALISIS:")
        print(f"   - Promedio de autores por proyecto: {resumen['promedio_autores']:.1f}")
        
        # Contar proyectos con múltiples autores
        proyectos_multiples = df_clean[df_clean['num_autores'] > 1]
        print(f"   - Proyectos con multiples autores: {len(proyectos_multiples)} ({len(proyectos_multiples)/len(df_clean)*100:.1f}%)")
        
    except Exception as e:
        print(f"[ERROR] Error en analisis: {e}")
    
    # Ejemplos detallados
    print("\n4. EJEMPLOS DETALLADOS...")
    print("-" * 30)
    
    try:
        print("[EJEMPLOS] Primeros 3 proyectos con datos enriquecidos:")
        for i, (_, row) in enumerate(df_clean.head(3).iterrows(), 1):
            print(f"\n   {i}. PROYECTO: {row['proyecto_limpio']}")
            print(f"      TITULO: {row['titulo_limpio'][:60]}...")
            print(f"      TIPO: {row['tipo_proyecto']}")
            print(f"      REGION: {row['region'] if pd.notna(row['region']) else 'No especificada'}")
            print(f"      AUTORES: {len(row['autores_limpios'])} congresistas")
            print(f"      PARTIDO: {row['partido_politico']}")
            print(f"      FECHA: {row['fecha_limpia']} ({row['dia_semana']})")
    
    except Exception as e:
        print(f"[ERROR] Error mostrando ejemplos: {e}")
    
    # Análisis de calidad
    print("\n5. ANALISIS DE CALIDAD...")
    print("-" * 30)
    
    try:
        print("[CALIDAD] Completitud de datos:")
        campos_importantes = ['proyecto_limpio', 'fecha_limpia', 'titulo_limpio', 'partido_politico', 'tipo_proyecto']
        for campo in campos_importantes:
            if campo in df_clean.columns:
                completitud = (1 - df_clean[campo].isnull().sum() / len(df_clean)) * 100
                print(f"   - {campo}: {completitud:.1f}%")
        
        # Detectar duplicados
        duplicados = df_clean.duplicated(subset=['proyecto_limpio'], keep=False)
        if duplicados.any():
            print(f"\n[WARNING] Duplicados detectados: {duplicados.sum()}")
        else:
            print(f"\n[OK] No se detectaron duplicados")
        
        # Estadísticas de autores
        print(f"\n[AUTORES] Estadisticas:")
        print(f"   - Maximo autores en un proyecto: {df_clean['num_autores'].max()}")
        print(f"   - Minimo autores en un proyecto: {df_clean['num_autores'].min()}")
        print(f"   - Proyectos con 1 autor: {len(df_clean[df_clean['num_autores'] == 1])}")
        print(f"   - Proyectos con 2+ autores: {len(df_clean[df_clean['num_autores'] > 1])}")
    
    except Exception as e:
        print(f"[ERROR] Error en analisis de calidad: {e}")
    
    # Resumen final
    print("\n" + "=" * 60)
    print("RESUMEN FINAL DEL DEMO")
    print("=" * 60)
    print(f"[OK] Datos procesados: {len(df_clean)} proyectos")
    print(f"[OK] Tipos identificados: {len(resumen['proyectos_por_tipo'])}")
    print(f"[OK] Regiones detectadas: {len(resumen['proyectos_por_region'])}")
    print(f"[OK] Promedio de autores: {resumen['promedio_autores']:.1f}")
    print(f"[OK] Congresista mas activo: {resumen['congresista_mas_activo']}")
    print(f"[OK] Demo de analisis completado exitosamente!")
    print("=" * 60)

if __name__ == "__main__":
    demo_simple()
