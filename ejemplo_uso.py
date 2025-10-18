"""
Ejemplo de uso del scraper mejorado de proyectos de ley del Congreso del Perú
"""
from datetime import datetime, timedelta
from scraper_mejorado import CongresoScraper
from utils.limpieza import DataCleaner, limpiar_archivo_csv
import pandas as pd

def ejemplo_basico():
    """Ejemplo básico de uso del scraper"""
    print("🚀 EJEMPLO BÁSICO - SCRAPING DE ÚLTIMOS 7 DÍAS")
    print("=" * 60)
    
    # Crear scraper
    scraper = CongresoScraper(headless=False)
    
    try:
        # Scraping de últimos 7 días
        proyectos = scraper.scrape()
        
        if proyectos:
            print(f"✅ Scraping completado: {len(proyectos)} proyectos encontrados")
            
            # Guardar datos
            archivo = scraper.save_to_csv(proyectos)
            print(f"💾 Datos guardados en: {archivo}")
            
            # Mostrar resumen
            df = pd.DataFrame(proyectos)
            print(f"\n📊 RESUMEN:")
            print(f"   - Total proyectos: {len(df)}")
            print(f"   - Fechas: {df['fecha'].min()} - {df['fecha'].max()}")
            print(f"   - Estados únicos: {df['estado'].nunique()}")
            
        else:
            print("❌ No se encontraron proyectos")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        scraper.close()

def ejemplo_fechas_personalizadas():
    """Ejemplo con fechas personalizadas"""
    print("\n🗓️ EJEMPLO CON FECHAS PERSONALIZADAS")
    print("=" * 60)
    
    # Definir rango de fechas específico
    fecha_desde = "01/06/2025"
    fecha_hasta = "05/06/2025"
    
    scraper = CongresoScraper(headless=False)
    
    try:
        proyectos = scraper.scrape(fecha_desde, fecha_hasta)
        
        if proyectos:
            print(f"✅ Scraping completado: {len(proyectos)} proyectos")
            archivo = scraper.save_to_csv(proyectos)
            print(f"💾 Datos guardados en: {archivo}")
        else:
            print("❌ No se encontraron proyectos en el rango especificado")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        scraper.close()

def ejemplo_limpieza_datos():
    """Ejemplo de limpieza de datos"""
    print("\n🧹 EJEMPLO DE LIMPIEZA DE DATOS")
    print("=" * 60)
    
    # Buscar archivos CSV existentes
    import glob
    archivos = glob.glob("data/proyectos_ley_*.csv")
    
    if archivos:
        archivo_entrada = archivos[0]  # Usar el primer archivo encontrado
        print(f"📂 Limpiando archivo: {archivo_entrada}")
        
        try:
            # Limpiar datos
            archivo_salida = limpiar_archivo_csv(archivo_entrada)
            print(f"✅ Limpieza completada: {archivo_salida}")
            
            # Cargar y mostrar datos limpios
            df_limpio = pd.read_csv(archivo_salida, encoding='utf-8-sig')
            print(f"\n📊 DATOS LIMPIOS:")
            print(f"   - Registros: {len(df_limpio)}")
            print(f"   - Columnas: {list(df_limpio.columns)}")
            
            # Mostrar estadísticas básicas
            if 'partido_politico' in df_limpio.columns:
                print(f"\n🏛️ PROYECTOS POR PARTIDO:")
                for partido, count in df_limpio['partido_politico'].value_counts().head(5).items():
                    print(f"   {partido}: {count}")
            
            if 'tipo_proyecto' in df_limpio.columns:
                print(f"\n📋 PROYECTOS POR TIPO:")
                for tipo, count in df_limpio['tipo_proyecto'].value_counts().head(5).items():
                    print(f"   {tipo}: {count}")
                    
        except Exception as e:
            print(f"❌ Error en limpieza: {e}")
    else:
        print("❌ No se encontraron archivos CSV para limpiar")

def ejemplo_analisis_completo():
    """Ejemplo de análisis completo"""
    print("\n📊 EJEMPLO DE ANÁLISIS COMPLETO")
    print("=" * 60)
    
    # Buscar archivos CSV
    import glob
    archivos = glob.glob("data/proyectos_ley_*.csv")
    
    if not archivos:
        print("❌ No se encontraron archivos CSV. Ejecute primero el scraping.")
        return
    
    try:
        # Cargar datos
        dataframes = []
        for archivo in archivos:
            df = pd.read_csv(archivo, encoding='utf-8-sig')
            dataframes.append(df)
        
        df_raw = pd.concat(dataframes, ignore_index=True)
        print(f"📂 Datos cargados: {len(df_raw)} registros")
        
        # Limpiar datos
        cleaner = DataCleaner()
        df_clean = cleaner.limpiar_dataframe(df_raw)
        print(f"🧹 Datos limpios: {len(df_clean)} registros")
        
        # Generar resumen
        resumen = cleaner.generar_resumen(df_clean)
        
        print(f"\n📊 RESUMEN EJECUTIVO:")
        print(f"   📈 Total proyectos: {resumen['total_proyectos']}")
        print(f"   📅 Período: {resumen['fecha_inicio'].strftime('%d/%m/%Y')} - {resumen['fecha_fin'].strftime('%d/%m/%Y')}")
        print(f"   👥 Promedio autores: {resumen['promedio_autores']:.1f}")
        print(f"   🏆 Más activo: {resumen['congresista_mas_activo']}")
        
        # Top partidos
        print(f"\n🏛️ TOP 5 PARTIDOS:")
        for i, (partido, count) in enumerate(list(resumen['proyectos_por_partido'].items())[:5], 1):
            print(f"   {i}. {partido}: {count} proyectos")
        
        # Top tipos
        print(f"\n📋 TOP 5 TIPOS DE PROYECTOS:")
        for i, (tipo, count) in enumerate(list(resumen['proyectos_por_tipo'].items())[:5], 1):
            print(f"   {i}. {tipo}: {count} proyectos")
        
        # Guardar análisis
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archivo_analisis = f"data/analisis_completo_{timestamp}.csv"
        df_clean.to_csv(archivo_analisis, index=False, encoding='utf-8-sig')
        print(f"\n💾 Análisis guardado en: {archivo_analisis}")
        
    except Exception as e:
        print(f"❌ Error en análisis: {e}")

def main():
    """Función principal con menú de opciones"""
    print("🇵🇪 SCRAPER DE PROYECTOS DE LEY - CONGRESO DEL PERÚ")
    print("=" * 60)
    print("Seleccione una opción:")
    print("1. Scraping básico (últimos 7 días)")
    print("2. Scraping con fechas personalizadas")
    print("3. Limpiar datos existentes")
    print("4. Análisis completo")
    print("5. Ejecutar todos los ejemplos")
    print("0. Salir")
    
    while True:
        try:
            opcion = input("\nIngrese su opción (0-5): ").strip()
            
            if opcion == "0":
                print("👋 ¡Hasta luego!")
                break
            elif opcion == "1":
                ejemplo_basico()
            elif opcion == "2":
                ejemplo_fechas_personalizadas()
            elif opcion == "3":
                ejemplo_limpieza_datos()
            elif opcion == "4":
                ejemplo_analisis_completo()
            elif opcion == "5":
                ejemplo_basico()
                ejemplo_fechas_personalizadas()
                ejemplo_limpieza_datos()
                ejemplo_analisis_completo()
            else:
                print("❌ Opción inválida. Intente nuevamente.")
                
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
