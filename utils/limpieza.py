"""
Funciones de limpieza y procesamiento de datos para proyectos de ley
"""
import re
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class DataCleaner:
    """Clase para limpiar y procesar datos de proyectos de ley"""
    
    def __init__(self):
        self.partidos_politicos = {
            'FREPAP': ['Frente Popular Agrícola del Perú'],
            'PERU LIBRE': ['Perú Libre', 'Perú Libre - Partido Nacionalista'],
            'FUERZA POPULAR': ['Fuerza Popular', 'FP'],
            'ACCION POPULAR': ['Acción Popular', 'AP'],
            'ALIANZA PARA EL PROGRESO': ['Alianza para el Progreso', 'APP'],
            'PODEMOS PERU': ['Podemos Perú', 'Podemos'],
            'AVANZA PAIS': ['Avanza País', 'Avanza'],
            'RENOVACION POPULAR': ['Renovación Popular', 'RP'],
            'SOMOS PERU': ['Somos Perú', 'Somos'],
            'UNION POR EL PERU': ['Unión por el Perú', 'UPP'],
            'PARTIDO MORADO': ['Partido Morado', 'Morado'],
            'JUNTOS POR EL PERU': ['Juntos por el Perú', 'JPP'],
            'FRENTE AMPLIO': ['Frente Amplio', 'FA'],
            'CONFIEP': ['Confederación Nacional de Instituciones Empresariales Privadas'],
            'INDEPENDIENTE': ['Independiente', 'Independientes']
        }
    
    def limpiar_fecha(self, fecha_str: str) -> Optional[str]:
        """
        Limpia y normaliza el formato de fecha
        Convierte de 'Fecha de Presentación02/06/2025' a '02/06/2025'
        """
        try:
            if pd.isna(fecha_str) or not fecha_str:
                return None
            
            # Buscar patrón de fecha DD/MM/YYYY
            fecha_match = re.search(r'(\d{2}/\d{2}/\d{4})', str(fecha_str))
            if fecha_match:
                return fecha_match.group(1)
            
            # Si no encuentra patrón, intentar parsear directamente
            try:
                fecha_parsed = datetime.strptime(fecha_str, '%d/%m/%Y')
                return fecha_parsed.strftime('%d/%m/%Y')
            except:
                return None
                
        except Exception as e:
            logger.warning(f"Error limpiando fecha '{fecha_str}': {e}")
            return None
    
    def limpiar_proyecto(self, proyecto_str: str) -> Optional[str]:
        """
        Limpia el número de proyecto
        Convierte de 'Proyecto de Ley 11408/2024-CR' a '11408/2024-CR'
        """
        try:
            if pd.isna(proyecto_str) or not proyecto_str:
                return None
            
            # Buscar patrón de proyecto
            proyecto_match = re.search(r'(\d+/\d{4}-\w+)', str(proyecto_str))
            if proyecto_match:
                return proyecto_match.group(1)
            
            return str(proyecto_str).strip()
            
        except Exception as e:
            logger.warning(f"Error limpiando proyecto '{proyecto_str}': {e}")
            return None
    
    def limpiar_titulo(self, titulo_str: str) -> str:
        """Limpia y normaliza el título del proyecto"""
        try:
            if pd.isna(titulo_str) or not titulo_str:
                return ""
            
            # Limpiar espacios extra y caracteres especiales
            titulo = str(titulo_str).strip()
            titulo = re.sub(r'\s+', ' ', titulo)  # Múltiples espacios a uno
            titulo = re.sub(r'[^\w\s\.,;:()\-áéíóúñüÁÉÍÓÚÑÜ]', '', titulo)  # Caracteres especiales
            
            return titulo
            
        except Exception as e:
            logger.warning(f"Error limpiando título '{titulo_str}': {e}")
            return str(titulo_str) if titulo_str else ""
    
    def extraer_partido_politico(self, autores_str: str) -> Optional[str]:
        """
        Extrae el partido político de la lista de autores
        """
        try:
            if pd.isna(autores_str) or not autores_str:
                return None
            
            autores_upper = str(autores_str).upper()
            
            # Buscar partidos conocidos
            for partido, variantes in self.partidos_politicos.items():
                for variante in variantes:
                    if variante.upper() in autores_upper:
                        return partido
            
            # Si no encuentra partido específico, verificar si es independiente
            if 'INDEPENDIENTE' in autores_upper or 'INDEPENDIENTES' in autores_upper:
                return 'INDEPENDIENTE'
            
            return 'DESCONOCIDO'
            
        except Exception as e:
            logger.warning(f"Error extrayendo partido de '{autores_str}': {e}")
            return None
    
    def limpiar_autores(self, autores_str: str) -> List[str]:
        """
        Limpia y separa la lista de autores
        """
        try:
            if pd.isna(autores_str) or not autores_str:
                return []
            
            # Separar por comas y limpiar
            autores = [autor.strip() for autor in str(autores_str).split(',')]
            autores = [autor for autor in autores if autor]  # Eliminar vacíos
            
            # Limpiar cada autor
            autores_limpios = []
            for autor in autores:
                # Remover "ver más..." y similares
                autor_limpio = re.sub(r'\s+ver\s+más\.{3,}', '', autor, flags=re.IGNORECASE)
                autor_limpio = re.sub(r'\s+\.{3,}', '', autor_limpio)
                autor_limpio = autor_limpio.strip()
                
                if autor_limpio:
                    autores_limpios.append(autor_limpio)
            
            return autores_limpios
            
        except Exception as e:
            logger.warning(f"Error limpiando autores '{autores_str}': {e}")
            return []
    
    def clasificar_tipo_proyecto(self, titulo: str) -> str:
        """
        Clasifica el tipo de proyecto basado en palabras clave del título
        """
        try:
            if pd.isna(titulo) or not titulo:
                return 'DESCONOCIDO'
            
            titulo_upper = str(titulo).upper()
            
            # Categorías de proyectos
            categorias = {
                'EDUCACION': ['EDUCACIÓN', 'EDUCATIVO', 'UNIVERSIDAD', 'INSTITUTO', 'COLEGIO', 'ESCUELA', 'ESTUDIANTE'],
                'SALUD': ['SALUD', 'MÉDICO', 'HOSPITAL', 'MEDICINA', 'ENFERMO', 'PACIENTE', 'SANITARIO'],
                'TRABAJO': ['TRABAJO', 'TRABAJADOR', 'EMPLEO', 'LABORAL', 'SALARIO', 'SUELDO', 'RÉGIMEN LABORAL'],
                'ECONOMIA': ['ECONÓMICO', 'ECONOMÍA', 'FINANCIERO', 'PRESUPUESTO', 'INVERSIÓN', 'DESARROLLO ECONÓMICO'],
                'INFRAESTRUCTURA': ['CARRETERA', 'PUENTE', 'CONSTRUCCIÓN', 'OBRA', 'INFRAESTRUCTURA', 'RUTA'],
                'CULTURA': ['CULTURAL', 'PATRIMONIO', 'CULTURA', 'TRADICIÓN', 'FESTIVIDAD', 'ARTE'],
                'AMBIENTE': ['AMBIENTAL', 'MEDIO AMBIENTE', 'CONTAMINACIÓN', 'ECOLOGÍA', 'NATURALEZA'],
                'SEGURIDAD': ['SEGURIDAD', 'POLICÍA', 'DEFENSA', 'CRIMEN', 'DELITO', 'JUSTICIA'],
                'SOCIAL': ['SOCIAL', 'POBREZA', 'VULNERABLE', 'DISCAPACIDAD', 'ADULTO MAYOR', 'NIÑO'],
                'ADMINISTRATIVO': ['ADMINISTRATIVO', 'FUNCIONARIO', 'SERVIDOR PÚBLICO', 'RÉGIMEN', 'NOMBRAMIENTO']
            }
            
            for categoria, palabras in categorias.items():
                if any(palabra in titulo_upper for palabra in palabras):
                    return categoria
            
            return 'OTROS'
            
        except Exception as e:
            logger.warning(f"Error clasificando tipo de proyecto '{titulo}': {e}")
            return 'DESCONOCIDO'
    
    def extraer_region(self, titulo: str) -> Optional[str]:
        """
        Extrae la región mencionada en el título del proyecto
        """
        try:
            if pd.isna(titulo) or not titulo:
                return None
            
            titulo_upper = str(titulo).upper()
            
            # Regiones del Perú
            regiones = [
                'LIMA', 'AREQUIPA', 'CUSCO', 'LA LIBERTAD', 'PIURA', 'JUNÍN', 'CAJAMARCA',
                'LAMBAYEQUE', 'ANCASH', 'PUNO', 'HUÁNUCO', 'ICA', 'LORETO', 'SAN MARTÍN',
                'TACNA', 'UCAYALI', 'AYACUCHO', 'MOQUEGUA', 'PASCO', 'TUMBES', 'HUANCAVELICA',
                'APURÍMAC', 'MADRE DE DIOS', 'CALLAO'
            ]
            
            for region in regiones:
                if region in titulo_upper:
                    return region
            
            return None
            
        except Exception as e:
            logger.warning(f"Error extrayendo región de '{titulo}': {e}")
            return None
    
    def limpiar_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica todas las funciones de limpieza a un DataFrame
        """
        try:
            logger.info("🧹 Iniciando limpieza de datos...")
            
            # Crear copia para no modificar el original
            df_limpio = df.copy()
            
            # Limpiar fechas
            df_limpio['fecha_limpia'] = df_limpio['fecha'].apply(self.limpiar_fecha)
            
            # Limpiar proyectos
            df_limpio['proyecto_limpio'] = df_limpio['proyecto'].apply(self.limpiar_proyecto)
            
            # Limpiar títulos
            df_limpio['titulo_limpio'] = df_limpio['titulo'].apply(self.limpiar_titulo)
            
            # Extraer partido político
            df_limpio['partido_politico'] = df_limpio['autores'].apply(self.extraer_partido_politico)
            
            # Limpiar autores
            df_limpio['autores_limpios'] = df_limpio['autores'].apply(self.limpiar_autores)
            df_limpio['num_autores'] = df_limpio['autores_limpios'].apply(len)
            
            # Clasificar tipo de proyecto
            df_limpio['tipo_proyecto'] = df_limpio['titulo_limpio'].apply(self.clasificar_tipo_proyecto)
            
            # Extraer región
            df_limpio['region'] = df_limpio['titulo_limpio'].apply(self.extraer_region)
            
            # Convertir fecha a datetime
            df_limpio['fecha_datetime'] = pd.to_datetime(df_limpio['fecha_limpia'], 
                                                        format='%d/%m/%Y', errors='coerce')
            
            # Extraer año y mes
            df_limpio['año'] = df_limpio['fecha_datetime'].dt.year
            df_limpio['mes'] = df_limpio['fecha_datetime'].dt.month
            df_limpio['dia_semana'] = df_limpio['fecha_datetime'].dt.day_name()
            
            # Limpiar estado
            df_limpio['estado_limpio'] = df_limpio['estado'].str.strip().str.upper()
            
            logger.info(f"✅ Limpieza completada. Registros procesados: {len(df_limpio)}")
            
            return df_limpio
            
        except Exception as e:
            logger.error(f"❌ Error en limpieza de DataFrame: {e}")
            return df
    
    def generar_resumen(self, df: pd.DataFrame) -> Dict:
        """
        Genera un resumen estadístico de los datos limpios
        """
        try:
            resumen = {
                'total_proyectos': len(df),
                'fecha_inicio': df['fecha_datetime'].min(),
                'fecha_fin': df['fecha_datetime'].max(),
                'proyectos_por_partido': df['partido_politico'].value_counts().to_dict(),
                'proyectos_por_tipo': df['tipo_proyecto'].value_counts().to_dict(),
                'proyectos_por_region': df['region'].value_counts().to_dict(),
                'proyectos_por_estado': df['estado_limpio'].value_counts().to_dict(),
                'promedio_autores': df['num_autores'].mean(),
                'congresista_mas_activo': self._encontrar_congresista_mas_activo(df)
            }
            
            return resumen
            
        except Exception as e:
            logger.error(f"❌ Error generando resumen: {e}")
            return {}
    
    def _encontrar_congresista_mas_activo(self, df: pd.DataFrame) -> str:
        """Encuentra el congresista con más proyectos"""
        try:
            # Contar apariciones de cada autor
            todos_autores = []
            for autores_list in df['autores_limpios']:
                todos_autores.extend(autores_list)
            
            if not todos_autores:
                return "No disponible"
            
            conteo_autores = pd.Series(todos_autores).value_counts()
            return conteo_autores.index[0] if len(conteo_autores) > 0 else "No disponible"
            
        except Exception as e:
            logger.warning(f"Error encontrando congresista más activo: {e}")
            return "No disponible"

def limpiar_archivo_csv(archivo_entrada: str, archivo_salida: str = None) -> str:
    """
    Función de conveniencia para limpiar un archivo CSV
    """
    try:
        # Leer datos
        df = pd.read_csv(archivo_entrada, encoding='utf-8-sig')
        logger.info(f"📂 Archivo leído: {archivo_entrada}")
        
        # Limpiar datos
        cleaner = DataCleaner()
        df_limpio = cleaner.limpiar_dataframe(df)
        
        # Generar nombre de archivo de salida
        if archivo_salida is None:
            archivo_salida = archivo_entrada.replace('.csv', '_limpio.csv')
        
        # Guardar datos limpios
        df_limpio.to_csv(archivo_salida, index=False, encoding='utf-8-sig')
        logger.info(f"💾 Datos limpios guardados en: {archivo_salida}")
        
        # Generar resumen
        resumen = cleaner.generar_resumen(df_limpio)
        logger.info(f"📊 Resumen generado: {resumen['total_proyectos']} proyectos")
        
        return archivo_salida
        
    except Exception as e:
        logger.error(f"❌ Error limpiando archivo {archivo_entrada}: {e}")
        raise

if __name__ == "__main__":
    # Ejemplo de uso
    import sys
    
    if len(sys.argv) > 1:
        archivo_entrada = sys.argv[1]
        archivo_salida = sys.argv[2] if len(sys.argv) > 2 else None
        limpiar_archivo_csv(archivo_entrada, archivo_salida)
    else:
        print("Uso: python limpieza.py <archivo_entrada> [archivo_salida]")
