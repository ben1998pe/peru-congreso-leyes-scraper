"""
Data validation utilities for the Peru Congress Laws Scraper
"""
import re
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import logging
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of data validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    cleaned_data: Optional[Dict[str, Any]] = None


class DataValidator:
    """Data validation class for scraped law projects"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Regex patterns for validation
        self.patterns = {
            'proyecto': r'^\d+/\d{4}-[A-Z]{2}$',
            'fecha': r'^\d{2}/\d{2}/\d{4}$',
            'estado': r'^[A-ZÁÉÍÓÚÑ\s]+$',
            'proponente': r'^[A-ZÁÉÍÓÚÑ\s]+$'
        }
        
        # Valid states
        self.valid_states = {
            'ENVIADO', 'RECIBIDO', 'DERIVADO', 'OBSERVADO', 'APROBADO',
            'RECHAZADO', 'ARCHIVADO', 'RETIRADO', 'PRESENTADO', 'PUBLICADO'
        }
        
        # Valid proponents
        self.valid_proponents = {
            'CONGRESO', 'CONGRESISTA', 'CONGRESISTAS', 'PRESIDENTE',
            'COMISION', 'MESA DIRECTIVA', 'GRUPO PARLAMENTARIO'
        }
    
    def validate_proyecto(self, proyecto: str) -> ValidationResult:
        """Validate project number format"""
        errors = []
        warnings = []
        
        if not proyecto or pd.isna(proyecto):
            errors.append("Número de proyecto es requerido")
            return ValidationResult(False, errors, warnings)
        
        proyecto_str = str(proyecto).strip()
        
        if not re.match(self.patterns['proyecto'], proyecto_str):
            warnings.append(f"Formato de proyecto inusual: {proyecto_str}")
        
        return ValidationResult(True, errors, warnings, {'proyecto': proyecto_str})
    
    def validate_fecha(self, fecha: str) -> ValidationResult:
        """Validate date format and content"""
        errors = []
        warnings = []
        
        if not fecha or pd.isna(fecha):
            errors.append("Fecha es requerida")
            return ValidationResult(False, errors, warnings)
        
        fecha_str = str(fecha).strip()
        
        # Check format
        if not re.match(self.patterns['fecha'], fecha_str):
            errors.append(f"Formato de fecha inválido: {fecha_str}")
            return ValidationResult(False, errors, warnings)
        
        # Check if date is valid
        try:
            parsed_date = datetime.strptime(fecha_str, '%d/%m/%Y')
            if parsed_date.year < 2000 or parsed_date.year > 2030:
                warnings.append(f"Año inusual: {parsed_date.year}")
        except ValueError:
            errors.append(f"Fecha inválida: {fecha_str}")
            return ValidationResult(False, errors, warnings)
        
        return ValidationResult(True, errors, warnings, {'fecha': fecha_str})
    
    def validate_titulo(self, titulo: str) -> ValidationResult:
        """Validate project title"""
        errors = []
        warnings = []
        
        if not titulo or pd.isna(titulo):
            errors.append("Título es requerido")
            return ValidationResult(False, errors, warnings)
        
        titulo_str = str(titulo).strip()
        
        if len(titulo_str) < 10:
            warnings.append("Título muy corto")
        elif len(titulo_str) > 500:
            warnings.append("Título muy largo")
        
        # Check for suspicious content
        if titulo_str.lower() in ['test', 'prueba', 'ejemplo']:
            warnings.append("Título parece ser de prueba")
        
        return ValidationResult(True, errors, warnings, {'titulo': titulo_str})
    
    def validate_estado(self, estado: str) -> ValidationResult:
        """Validate project state"""
        errors = []
        warnings = []
        
        if not estado or pd.isna(estado):
            errors.append("Estado es requerido")
            return ValidationResult(False, errors, warnings)
        
        estado_str = str(estado).strip().upper()
        
        if not re.match(self.patterns['estado'], estado_str):
            warnings.append(f"Estado con caracteres inusuales: {estado_str}")
        
        if estado_str not in self.valid_states:
            warnings.append(f"Estado no reconocido: {estado_str}")
        
        return ValidationResult(True, errors, warnings, {'estado': estado_str})
    
    def validate_proponente(self, proponente: str) -> ValidationResult:
        """Validate proponent"""
        errors = []
        warnings = []
        
        if not proponente or pd.isna(proponente):
            errors.append("Proponente es requerido")
            return ValidationResult(False, errors, warnings)
        
        proponente_str = str(proponente).strip().upper()
        
        if not re.match(self.patterns['proponente'], proponente_str):
            warnings.append(f"Proponente con caracteres inusuales: {proponente_str}")
        
        # Check if it's a known proponent type
        is_known = any(known in proponente_str for known in self.valid_proponents)
        if not is_known:
            warnings.append(f"Tipo de proponente no reconocido: {proponente_str}")
        
        return ValidationResult(True, errors, warnings, {'proponente': proponente_str})
    
    def validate_autores(self, autores: str) -> ValidationResult:
        """Validate authors list"""
        errors = []
        warnings = []
        
        if not autores or pd.isna(autores):
            warnings.append("Lista de autores vacía")
            return ValidationResult(True, errors, warnings, {'autores': []})
        
        autores_str = str(autores).strip()
        
        if len(autores_str) < 3:
            warnings.append("Lista de autores muy corta")
        
        # Check for suspicious patterns
        if 'test' in autores_str.lower() or 'prueba' in autores_str.lower():
            warnings.append("Lista de autores parece ser de prueba")
        
        # Split and validate individual authors
        autores_list = [autor.strip() for autor in autores_str.split(',')]
        autores_clean = []
        
        for autor in autores_list:
            if autor and len(autor) > 2:
                autores_clean.append(autor)
            else:
                warnings.append(f"Autor inválido o muy corto: '{autor}'")
        
        if not autores_clean:
            errors.append("No se encontraron autores válidos")
            return ValidationResult(False, errors, warnings)
        
        return ValidationResult(True, errors, warnings, {'autores': autores_clean})
    
    def validate_record(self, record: Dict[str, Any]) -> ValidationResult:
        """Validate a complete record"""
        errors = []
        warnings = []
        cleaned_data = {}
        
        # Validate each field
        fields_to_validate = [
            ('proyecto', self.validate_proyecto),
            ('fecha', self.validate_fecha),
            ('titulo', self.validate_titulo),
            ('estado', self.validate_estado),
            ('proponente', self.validate_proponente),
            ('autores', self.validate_autores)
        ]
        
        for field_name, validator_func in fields_to_validate:
            field_value = record.get(field_name, '')
            result = validator_func(field_value)
            
            if not result.is_valid:
                errors.extend([f"{field_name}: {error}" for error in result.errors])
            
            warnings.extend([f"{field_name}: {warning}" for warning in result.warnings])
            
            if result.cleaned_data:
                cleaned_data.update(result.cleaned_data)
        
        # Additional cross-field validations
        self._validate_cross_fields(record, errors, warnings, cleaned_data)
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings, cleaned_data)
    
    def _validate_cross_fields(self, record: Dict[str, Any], 
                              errors: List[str], warnings: List[str], 
                              cleaned_data: Dict[str, Any]):
        """Validate relationships between fields"""
        
        # Check date consistency
        fecha = record.get('fecha', '')
        if fecha:
            try:
                parsed_date = datetime.strptime(fecha, '%d/%m/%Y')
                current_date = datetime.now()
                
                # Check if date is too far in the future
                if parsed_date > current_date:
                    warnings.append("Fecha en el futuro")
                
                # Check if date is too old
                if parsed_date.year < 2010:
                    warnings.append("Fecha muy antigua")
                    
            except ValueError:
                pass  # Already handled in fecha validation
        
        # Check title-content consistency
        titulo = record.get('titulo', '').lower()
        estado = record.get('estado', '').lower()
        
        if 'archivado' in estado and 'nuevo' in titulo:
            warnings.append("Proyecto archivado pero título sugiere que es nuevo")
    
    def validate_dataframe(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Validate entire DataFrame and return cleaned data with validation report"""
        self.logger.info(f"🔍 Validando DataFrame con {len(df)} registros")
        
        valid_records = []
        validation_report = {
            'total_records': len(df),
            'valid_records': 0,
            'invalid_records': 0,
            'total_errors': 0,
            'total_warnings': 0,
            'field_errors': {},
            'field_warnings': {}
        }
        
        for idx, record in df.iterrows():
            result = self.validate_record(record.to_dict())
            
            if result.is_valid:
                valid_records.append(result.cleaned_data)
                validation_report['valid_records'] += 1
            else:
                validation_report['invalid_records'] += 1
                self.logger.warning(f"Registro {idx} inválido: {', '.join(result.errors)}")
            
            validation_report['total_errors'] += len(result.errors)
            validation_report['total_warnings'] += len(result.warnings)
            
            # Track field-specific issues
            for error in result.errors:
                field = error.split(':')[0]
                validation_report['field_errors'][field] = validation_report['field_errors'].get(field, 0) + 1
            
            for warning in result.warnings:
                field = warning.split(':')[0]
                validation_report['field_warnings'][field] = validation_report['field_warnings'].get(field, 0) + 1
        
        cleaned_df = pd.DataFrame(valid_records)
        
        self.logger.info(f"✅ Validación completada: {validation_report['valid_records']}/{validation_report['total_records']} registros válidos")
        
        return cleaned_df, validation_report
    
    def get_validation_summary(self, validation_report: Dict[str, Any]) -> str:
        """Get a formatted validation summary"""
        summary = []
        summary.append("📊 RESUMEN DE VALIDACIÓN")
        summary.append("=" * 40)
        summary.append(f"Total registros: {validation_report['total_records']}")
        summary.append(f"Registros válidos: {validation_report['valid_records']}")
        summary.append(f"Registros inválidos: {validation_report['invalid_records']}")
        summary.append(f"Total errores: {validation_report['total_errors']}")
        summary.append(f"Total advertencias: {validation_report['total_warnings']}")
        
        if validation_report['field_errors']:
            summary.append("\n🔴 Errores por campo:")
            for field, count in validation_report['field_errors'].items():
                summary.append(f"   {field}: {count}")
        
        if validation_report['field_warnings']:
            summary.append("\n🟡 Advertencias por campo:")
            for field, count in validation_report['field_warnings'].items():
                summary.append(f"   {field}: {count}")
        
        return "\n".join(summary)
