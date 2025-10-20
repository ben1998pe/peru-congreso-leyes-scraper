"""
Sistema de exportación de datos en múltiples formatos para el Peru Congress Laws Scraper
"""
import json
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import logging
import zipfile
import io
import base64

logger = logging.getLogger(__name__)


class DataExporter:
    """Sistema de exportación de datos en múltiples formatos"""
    
    def __init__(self, output_dir: str = "exports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Configuración de formatos soportados
        self.supported_formats = {
            'csv': self._export_csv,
            'excel': self._export_excel,
            'json': self._export_json,
            'xml': self._export_xml,
            'html': self._export_html,
            'sql': self._export_sql,
            'parquet': self._export_parquet,
            'zip': self._export_zip
        }
    
    def export_data(self, df: pd.DataFrame, format: str, 
                   filename: str = None, **kwargs) -> str:
        """Exportar datos en el formato especificado"""
        
        if format not in self.supported_formats:
            raise ValueError(f"Formato no soportado: {format}. Formatos disponibles: {list(self.supported_formats.keys())}")
        
        # Generar nombre de archivo si no se proporciona
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"proyectos_ley_export_{timestamp}.{format}"
        
        # Asegurar que el archivo tenga la extensión correcta
        if not filename.endswith(f'.{format}'):
            filename = f"{filename}.{format}"
        
        # Exportar datos
        output_path = self.output_dir / filename
        export_func = self.supported_formats[format]
        
        try:
            result_path = export_func(df, output_path, **kwargs)
            logger.info(f"✅ Datos exportados exitosamente: {result_path}")
            return str(result_path)
        except Exception as e:
            logger.error(f"❌ Error exportando datos en formato {format}: {e}")
            raise
    
    def export_multiple_formats(self, df: pd.DataFrame, 
                               formats: List[str], 
                               base_filename: str = None) -> Dict[str, str]:
        """Exportar datos en múltiples formatos simultáneamente"""
        
        if base_filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_filename = f"proyectos_ley_export_{timestamp}"
        
        results = {}
        
        for format in formats:
            try:
                filename = f"{base_filename}.{format}"
                output_path = self.export_data(df, format, filename)
                results[format] = output_path
            except Exception as e:
                logger.warning(f"Error exportando en formato {format}: {e}")
                results[format] = f"Error: {str(e)}"
        
        return results
    
    def _export_csv(self, df: pd.DataFrame, output_path: Path, **kwargs) -> Path:
        """Exportar a CSV"""
        encoding = kwargs.get('encoding', 'utf-8-sig')
        separator = kwargs.get('separator', ',')
        index = kwargs.get('index', False)
        
        df.to_csv(output_path, encoding=encoding, sep=separator, index=index)
        return output_path
    
    def _export_excel(self, df: pd.DataFrame, output_path: Path, **kwargs) -> Path:
        """Exportar a Excel"""
        sheet_name = kwargs.get('sheet_name', 'Proyectos_Ley')
        index = kwargs.get('index', False)
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=index)
            
            # Agregar hoja de resumen si se solicita
            if kwargs.get('include_summary', True):
                summary_df = self._create_summary_sheet(df)
                summary_df.to_excel(writer, sheet_name='Resumen', index=False)
        
        return output_path
    
    def _export_json(self, df: pd.DataFrame, output_path: Path, **kwargs) -> Path:
        """Exportar a JSON"""
        orient = kwargs.get('orient', 'records')
        indent = kwargs.get('indent', 2)
        force_ascii = kwargs.get('force_ascii', False)
        
        df.to_json(output_path, orient=orient, indent=indent, force_ascii=force_ascii)
        return output_path
    
    def _export_xml(self, df: pd.DataFrame, output_path: Path, **kwargs) -> Path:
        """Exportar a XML"""
        root_name = kwargs.get('root_name', 'proyectos_ley')
        row_name = kwargs.get('row_name', 'proyecto')
        
        # Convertir DataFrame a XML
        xml_content = f'<?xml version="1.0" encoding="UTF-8"?>\n'
        xml_content += f'<{root_name}>\n'
        
        for _, row in df.iterrows():
            xml_content += f'  <{row_name}>\n'
            for col, value in row.items():
                if pd.notna(value):
                    # Limpiar nombre de columna para XML
                    clean_col = str(col).replace(' ', '_').replace('-', '_')
                    xml_content += f'    <{clean_col}>{value}</{clean_col}>\n'
            xml_content += f'  </{row_name}>\n'
        
        xml_content += f'</{root_name}>\n'
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        return output_path
    
    def _export_html(self, df: pd.DataFrame, output_path: Path, **kwargs) -> Path:
        """Exportar a HTML con tabla estilizada"""
        title = kwargs.get('title', 'Proyectos de Ley del Congreso del Perú')
        include_style = kwargs.get('include_style', True)
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
        """
        
        if include_style:
            html_content += """
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background-color: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
                .header { text-align: center; border-bottom: 3px solid #2196F3; padding-bottom: 20px; margin-bottom: 30px; }
                .header h1 { color: #2196F3; margin: 0; }
                .summary { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px; }
                table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
                th { background: #2196F3; color: white; font-weight: bold; }
                tr:nth-child(even) { background-color: #f9f9f9; }
                tr:hover { background-color: #f5f5f5; }
                .footer { text-align: center; margin-top: 30px; color: #666; font-size: 0.9em; }
            </style>
            """
        
        html_content += """
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Proyectos de Ley del Congreso del Perú</h1>
                    <p>Exportado el: """ + datetime.now().strftime('%d/%m/%Y %H:%M:%S') + """</p>
                </div>
        """
        
        # Agregar resumen si se solicita
        if kwargs.get('include_summary', True):
            summary_df = self._create_summary_sheet(df)
            html_content += """
                <div class="summary">
                    <h3>📈 Resumen de Datos</h3>
                    <p><strong>Total de registros:</strong> """ + str(len(df)) + """</p>
            """
            
            if 'partido_politico' in df.columns:
                top_party = df['partido_politico'].value_counts().head(1)
                if not top_party.empty:
                    html_content += f"<p><strong>Partido más activo:</strong> {top_party.index[0]} ({top_party.iloc[0]} proyectos)</p>"
            
            html_content += """
                </div>
            """
        
        # Agregar tabla de datos
        html_content += f"""
                <h3>📋 Datos Detallados</h3>
                {df.to_html(classes='table', table_id='data-table', escape=False, index=False)}
                
                <div class="footer">
                    <p>Generado por Peru Congress Laws Scraper</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def _export_sql(self, df: pd.DataFrame, output_path: Path, **kwargs) -> Path:
        """Exportar a SQL (INSERT statements)"""
        table_name = kwargs.get('table_name', 'proyectos_ley')
        
        sql_content = f"-- Script SQL generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        sql_content += f"-- Tabla: {table_name}\n\n"
        
        # Crear tabla si se solicita
        if kwargs.get('create_table', True):
            sql_content += f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
            
            for col in df.columns:
                # Determinar tipo de columna
                if df[col].dtype == 'object':
                    col_type = 'TEXT'
                elif df[col].dtype in ['int64', 'int32']:
                    col_type = 'INTEGER'
                elif df[col].dtype in ['float64', 'float32']:
                    col_type = 'REAL'
                elif df[col].dtype == 'bool':
                    col_type = 'BOOLEAN'
                else:
                    col_type = 'TEXT'
                
                sql_content += f"    {col} {col_type},\n"
            
            sql_content = sql_content.rstrip(',\n') + "\n);\n\n"
        
        # Generar INSERT statements
        for _, row in df.iterrows():
            values = []
            for value in row:
                if pd.isna(value):
                    values.append('NULL')
                elif isinstance(value, str):
                    # Escapar comillas simples
                    escaped_value = value.replace("'", "''")
                    values.append(f"'{escaped_value}'")
                else:
                    values.append(str(value))
            
            sql_content += f"INSERT INTO {table_name} VALUES ({', '.join(values)});\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(sql_content)
        
        return output_path
    
    def _export_parquet(self, df: pd.DataFrame, output_path: Path, **kwargs) -> Path:
        """Exportar a Parquet"""
        compression = kwargs.get('compression', 'snappy')
        index = kwargs.get('index', False)
        
        df.to_parquet(output_path, compression=compression, index=index)
        return output_path
    
    def _export_zip(self, df: pd.DataFrame, output_path: Path, **kwargs) -> Path:
        """Exportar múltiples formatos en un archivo ZIP"""
        formats = kwargs.get('formats', ['csv', 'excel', 'json'])
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for format in formats:
                try:
                    # Crear archivo temporal
                    temp_filename = f"proyectos_ley.{format}"
                    temp_path = self.output_dir / temp_filename
                    
                    # Exportar en formato específico
                    export_func = self.supported_formats[format]
                    export_func(df, temp_path, **kwargs)
                    
                    # Agregar al ZIP
                    zipf.write(temp_path, temp_filename)
                    
                    # Eliminar archivo temporal
                    temp_path.unlink()
                    
                except Exception as e:
                    logger.warning(f"Error agregando formato {format} al ZIP: {e}")
        
        return output_path
    
    def _create_summary_sheet(self, df: pd.DataFrame) -> pd.DataFrame:
        """Crear hoja de resumen para Excel"""
        summary_data = []
        
        # Estadísticas básicas
        summary_data.append(['Total de registros', len(df)])
        summary_data.append(['Columnas', len(df.columns)])
        summary_data.append(['Registros únicos', len(df.drop_duplicates())])
        
        # Estadísticas por columna
        for col in df.columns:
            if df[col].dtype == 'object':
                unique_count = df[col].nunique()
                null_count = df[col].isnull().sum()
                summary_data.append([f'{col} (únicos)', unique_count])
                summary_data.append([f'{col} (nulos)', null_count])
            elif df[col].dtype in ['int64', 'float64']:
                summary_data.append([f'{col} (promedio)', df[col].mean()])
                summary_data.append([f'{col} (mínimo)', df[col].min()])
                summary_data.append([f'{col} (máximo)', df[col].max()])
        
        return pd.DataFrame(summary_data, columns=['Métrica', 'Valor'])
    
    def get_export_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Obtener información sobre las opciones de exportación"""
        return {
            'supported_formats': list(self.supported_formats.keys()),
            'data_info': {
                'rows': len(df),
                'columns': len(df.columns),
                'memory_usage': df.memory_usage(deep=True).sum(),
                'dtypes': df.dtypes.to_dict()
            },
            'recommended_formats': self._get_recommended_formats(df)
        }
    
    def _get_recommended_formats(self, df: pd.DataFrame) -> List[str]:
        """Obtener formatos recomendados basados en el tamaño de los datos"""
        row_count = len(df)
        
        if row_count < 1000:
            return ['csv', 'excel', 'json', 'html']
        elif row_count < 10000:
            return ['csv', 'excel', 'parquet', 'json']
        else:
            return ['parquet', 'csv', 'zip']


def get_data_exporter() -> DataExporter:
    """Obtener instancia del exportador de datos"""
    return DataExporter()


# Funciones de conveniencia
def export_to_csv(df: pd.DataFrame, filename: str = None, **kwargs) -> str:
    """Exportar DataFrame a CSV"""
    exporter = get_data_exporter()
    return exporter.export_data(df, 'csv', filename, **kwargs)


def export_to_excel(df: pd.DataFrame, filename: str = None, **kwargs) -> str:
    """Exportar DataFrame a Excel"""
    exporter = get_data_exporter()
    return exporter.export_data(df, 'excel', filename, **kwargs)


def export_to_json(df: pd.DataFrame, filename: str = None, **kwargs) -> str:
    """Exportar DataFrame a JSON"""
    exporter = get_data_exporter()
    return exporter.export_data(df, 'json', filename, **kwargs)


def export_multiple_formats(df: pd.DataFrame, formats: List[str], 
                           base_filename: str = None) -> Dict[str, str]:
    """Exportar DataFrame en múltiples formatos"""
    exporter = get_data_exporter()
    return exporter.export_multiple_formats(df, formats, base_filename)


if __name__ == "__main__":
    # Prueba del sistema de exportación
    exporter = DataExporter()
    
    # Crear DataFrame de ejemplo
    sample_data = {
        'proyecto': ['123/2024-CR', '456/2024-CR', '789/2024-CR'],
        'fecha': ['01/01/2024', '02/01/2024', '03/01/2024'],
        'titulo': ['Proyecto 1', 'Proyecto 2', 'Proyecto 3'],
        'partido_politico': ['PERU LIBRE', 'FUERZA POPULAR', 'ACCION POPULAR'],
        'tipo_proyecto': ['EDUCACION', 'SALUD', 'ECONOMIA']
    }
    
    df = pd.DataFrame(sample_data)
    
    # Exportar en diferentes formatos
    print("📤 Probando exportación en múltiples formatos...")
    
    formats_to_test = ['csv', 'excel', 'json', 'html', 'xml']
    results = exporter.export_multiple_formats(df, formats_to_test)
    
    for format, result in results.items():
        print(f"✅ {format.upper()}: {result}")
    
    # Mostrar información de exportación
    info = exporter.get_export_info(df)
    print(f"\n📊 Información de exportación:")
    print(f"   Formatos soportados: {info['supported_formats']}")
    print(f"   Registros: {info['data_info']['rows']}")
    print(f"   Columnas: {info['data_info']['columns']}")
    print(f"   Formatos recomendados: {info['recommended_formats']}")
