"""
Script de automatización para ejecutar el scraper diariamente
"""
import os
import sys
import subprocess
import schedule
import time
from datetime import datetime, timedelta
from scraper_mejorado import CongresoScraper
from utils.limpieza import DataCleaner
import pandas as pd

def ejecutar_scraping():
    """Ejecuta el scraping y procesa los datos"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Iniciando scraping automático...")
    
    try:
        # Configurar fechas (últimos 7 días)
        fecha_hasta = datetime.now()
        fecha_desde = fecha_hasta - timedelta(days=7)
        
        fecha_desde_str = fecha_desde.strftime('%d/%m/%Y')
        fecha_hasta_str = fecha_hasta.strftime('%d/%m/%Y')
        
        print(f"Período: {fecha_desde_str} - {fecha_hasta_str}")
        
        # Ejecutar scraping
        scraper = CongresoScraper(headless=True)
        proyectos = scraper.scrape(fecha_desde_str, fecha_hasta_str)
        scraper.close()
        
        if proyectos:
            print(f"✅ Scraping exitoso: {len(proyectos)} proyectos")
            
            # Procesar y limpiar datos
            df_raw = pd.DataFrame(proyectos)
            cleaner = DataCleaner()
            df_clean = cleaner.limpiar_dataframe(df_raw)
            
            # Guardar datos
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            archivo_limpio = f"data/proyectos_ley_limpios_{timestamp}.csv"
            df_clean.to_csv(archivo_limpio, index=False, encoding='utf-8-sig')
            
            print(f"💾 Datos guardados en: {archivo_limpio}")
            
            # Generar resumen
            resumen = cleaner.generar_resumen(df_clean)
            print(f"📊 Resumen: {resumen['total_proyectos']} proyectos, {resumen['promedio_autores']:.1f} autores promedio")
            
            return True
        else:
            print("❌ No se encontraron proyectos")
            return False
            
    except Exception as e:
        print(f"❌ Error en scraping: {e}")
        return False

def commit_y_push():
    """Hace commit y push de los cambios"""
    try:
        print("📤 Subiendo cambios al repositorio...")
        
        # Agregar archivos de datos
        subprocess.run(["git", "add", "data/"], check=True)
        
        # Commit
        fecha = datetime.now().strftime('%d/%m/%Y')
        mensaje = f"🤖 Auto-update: Datos del {fecha}"
        subprocess.run(["git", "commit", "-m", mensaje], check=True)
        
        # Push
        subprocess.run(["git", "push"], check=True)
        
        print("✅ Cambios subidos exitosamente")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en git: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def tarea_diaria():
    """Tarea que se ejecuta diariamente"""
    print(f"\n{'='*60}")
    print(f"🚀 TAREA DIARIA - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*60}")
    
    # Ejecutar scraping
    if ejecutar_scraping():
        # Si hay datos nuevos, hacer commit
        commit_y_push()
    else:
        print("ℹ️ No hay datos nuevos para subir")
    
    print(f"{'='*60}\n")

def main():
    """Función principal"""
    print("🤖 Iniciando automatizador del scraper...")
    print("Presiona Ctrl+C para detener")
    
    # Programar tarea diaria a las 6:00 AM
    schedule.every().day.at("06:00").do(tarea_diaria)
    
    # Ejecutar inmediatamente para prueba
    print("🧪 Ejecutando prueba inicial...")
    tarea_diaria()
    
    # Mantener el script corriendo
    while True:
        schedule.run_pending()
        time.sleep(60)  # Verificar cada minuto

if __name__ == "__main__":
    main()
