"""
Sistema de alertas inteligentes para el Peru Congress Laws Scraper
"""
import json
import smtplib
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import logging
from dataclasses import dataclass, asdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class AlertRule:
    """Regla de alerta configurable"""
    name: str
    condition: str  # 'gt', 'lt', 'eq', 'contains', 'missing'
    threshold: float
    field: str
    message: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    enabled: bool = True
    cooldown_minutes: int = 60  # Tiempo entre alertas del mismo tipo


@dataclass
class Alert:
    """Alerta generada"""
    rule_name: str
    message: str
    severity: str
    timestamp: datetime
    value: Any
    threshold: Any
    resolved: bool = False


class AlertSystem:
    """Sistema de alertas inteligentes"""
    
    def __init__(self, config_file: str = "config/alerts.json"):
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(exist_ok=True)
        
        self.rules: List[AlertRule] = []
        self.alerts: List[Alert] = []
        self.alert_history: List[Alert] = []
        
        # Configuración de notificaciones
        self.email_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'username': '',
            'password': '',
            'from_email': '',
            'to_emails': []
        }
        
        self.webhook_config = {
            'slack_webhook': '',
            'discord_webhook': '',
            'teams_webhook': ''
        }
        
        self.load_config()
        self.setup_default_rules()
    
    def load_config(self):
        """Cargar configuración desde archivo"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Cargar reglas
                if 'rules' in config:
                    self.rules = [AlertRule(**rule) for rule in config['rules']]
                
                # Cargar configuración de email
                if 'email' in config:
                    self.email_config.update(config['email'])
                
                # Cargar configuración de webhooks
                if 'webhooks' in config:
                    self.webhook_config.update(config['webhooks'])
                
                logger.info(f"✅ Configuración de alertas cargada desde {self.config_file}")
            except Exception as e:
                logger.warning(f"Error cargando configuración de alertas: {e}")
    
    def save_config(self):
        """Guardar configuración en archivo"""
        config = {
            'rules': [asdict(rule) for rule in self.rules],
            'email': self.email_config,
            'webhooks': self.webhook_config,
            'last_updated': datetime.now().isoformat()
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, default=str)
            logger.info(f"✅ Configuración de alertas guardada en {self.config_file}")
        except Exception as e:
            logger.error(f"Error guardando configuración de alertas: {e}")
    
    def setup_default_rules(self):
        """Configurar reglas de alerta por defecto"""
        if not self.rules:
            default_rules = [
                AlertRule(
                    name="high_error_rate",
                    condition="gt",
                    threshold=10.0,
                    field="error_rate",
                    message="Tasa de errores alta detectada",
                    severity="high",
                    cooldown_minutes=30
                ),
                AlertRule(
                    name="low_success_rate",
                    condition="lt",
                    threshold=80.0,
                    field="success_rate",
                    message="Tasa de éxito baja detectada",
                    severity="medium",
                    cooldown_minutes=60
                ),
                AlertRule(
                    name="high_memory_usage",
                    condition="gt",
                    threshold=1000.0,
                    field="memory_usage_mb",
                    message="Uso de memoria alto detectado",
                    severity="medium",
                    cooldown_minutes=15
                ),
                AlertRule(
                    name="slow_processing",
                    condition="gt",
                    threshold=300.0,
                    field="processing_time_seconds",
                    message="Tiempo de procesamiento lento detectado",
                    severity="low",
                    cooldown_minutes=120
                ),
                AlertRule(
                    name="no_data_found",
                    condition="eq",
                    threshold=0,
                    field="projects_found",
                    message="No se encontraron proyectos de ley",
                    severity="critical",
                    cooldown_minutes=60
                ),
                AlertRule(
                    name="data_quality_low",
                    condition="lt",
                    threshold=70.0,
                    field="data_quality_score",
                    message="Calidad de datos baja detectada",
                    severity="high",
                    cooldown_minutes=45
                )
            ]
            
            self.rules = default_rules
            self.save_config()
            logger.info("✅ Reglas de alerta por defecto configuradas")
    
    def add_rule(self, rule: AlertRule):
        """Agregar nueva regla de alerta"""
        self.rules.append(rule)
        self.save_config()
        logger.info(f"✅ Regla de alerta agregada: {rule.name}")
    
    def remove_rule(self, rule_name: str):
        """Eliminar regla de alerta"""
        self.rules = [rule for rule in self.rules if rule.name != rule_name]
        self.save_config()
        logger.info(f"✅ Regla de alerta eliminada: {rule_name}")
    
    def check_alerts(self, data: Dict[str, Any]) -> List[Alert]:
        """Verificar reglas de alerta contra los datos"""
        new_alerts = []
        current_time = datetime.now()
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            # Verificar cooldown
            if self._is_in_cooldown(rule.name, current_time):
                continue
            
            # Obtener valor del campo
            value = self._get_field_value(data, rule.field)
            if value is None:
                continue
            
            # Evaluar condición
            if self._evaluate_condition(value, rule.condition, rule.threshold):
                alert = Alert(
                    rule_name=rule.name,
                    message=rule.message,
                    severity=rule.severity,
                    timestamp=current_time,
                    value=value,
                    threshold=rule.threshold
                )
                
                new_alerts.append(alert)
                self.alerts.append(alert)
                self.alert_history.append(alert)
                
                logger.warning(f"🚨 ALERTA {rule.severity.upper()}: {rule.message} (Valor: {value}, Umbral: {rule.threshold})")
        
        return new_alerts
    
    def _is_in_cooldown(self, rule_name: str, current_time: datetime) -> bool:
        """Verificar si la regla está en período de cooldown"""
        rule = next((r for r in self.rules if r.name == rule_name), None)
        if not rule:
            return False
        
        # Buscar última alerta de esta regla
        last_alert = None
        for alert in reversed(self.alert_history):
            if alert.rule_name == rule_name and not alert.resolved:
                last_alert = alert
                break
        
        if not last_alert:
            return False
        
        cooldown_end = last_alert.timestamp + timedelta(minutes=rule.cooldown_minutes)
        return current_time < cooldown_end
    
    def _get_field_value(self, data: Dict[str, Any], field: str) -> Any:
        """Obtener valor del campo usando notación de puntos"""
        try:
            keys = field.split('.')
            value = data
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return None
    
    def _evaluate_condition(self, value: Any, condition: str, threshold: Any) -> bool:
        """Evaluar condición de la regla"""
        try:
            if condition == 'gt':
                return float(value) > float(threshold)
            elif condition == 'lt':
                return float(value) < float(threshold)
            elif condition == 'eq':
                return value == threshold
            elif condition == 'contains':
                return str(threshold).lower() in str(value).lower()
            elif condition == 'missing':
                return value is None or value == ''
            else:
                return False
        except (ValueError, TypeError):
            return False
    
    def send_notifications(self, alerts: List[Alert]):
        """Enviar notificaciones para las alertas"""
        if not alerts:
            return
        
        # Agrupar alertas por severidad
        critical_alerts = [a for a in alerts if a.severity == 'critical']
        high_alerts = [a for a in alerts if a.severity == 'high']
        other_alerts = [a for a in alerts if a.severity in ['medium', 'low']]
        
        # Enviar notificaciones por email
        if self.email_config.get('username') and self.email_config.get('to_emails'):
            self._send_email_alert(alerts)
        
        # Enviar notificaciones por webhook
        if self.webhook_config.get('slack_webhook'):
            self._send_slack_alert(alerts)
        
        if self.webhook_config.get('discord_webhook'):
            self._send_discord_alert(alerts)
    
    def _send_email_alert(self, alerts: List[Alert]):
        """Enviar alerta por email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from_email']
            msg['To'] = ', '.join(self.email_config['to_emails'])
            msg['Subject'] = f"🚨 Alertas del Sistema de Scraping - {len(alerts)} alertas"
            
            # Crear contenido del email
            body = self._create_email_body(alerts)
            msg.attach(MIMEText(body, 'html'))
            
            # Enviar email
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])
            server.send_message(msg)
            server.quit()
            
            logger.info("✅ Alerta enviada por email")
        except Exception as e:
            logger.error(f"Error enviando email: {e}")
    
    def _send_slack_alert(self, alerts: List[Alert]):
        """Enviar alerta a Slack"""
        try:
            webhook_url = self.webhook_config['slack_webhook']
            
            # Crear mensaje para Slack
            message = {
                "text": f"🚨 *Alertas del Sistema de Scraping*",
                "attachments": []
            }
            
            for alert in alerts:
                color = self._get_severity_color(alert.severity)
                attachment = {
                    "color": color,
                    "title": f"{alert.severity.upper()}: {alert.message}",
                    "fields": [
                        {"title": "Valor", "value": str(alert.value), "short": True},
                        {"title": "Umbral", "value": str(alert.threshold), "short": True},
                        {"title": "Timestamp", "value": alert.timestamp.strftime('%Y-%m-%d %H:%M:%S'), "short": False}
                    ]
                }
                message["attachments"].append(attachment)
            
            response = requests.post(webhook_url, json=message)
            response.raise_for_status()
            
            logger.info("✅ Alerta enviada a Slack")
        except Exception as e:
            logger.error(f"Error enviando a Slack: {e}")
    
    def _send_discord_alert(self, alerts: List[Alert]):
        """Enviar alerta a Discord"""
        try:
            webhook_url = self.webhook_config['discord_webhook']
            
            # Crear mensaje para Discord
            message = {
                "content": f"🚨 **Alertas del Sistema de Scraping** - {len(alerts)} alertas",
                "embeds": []
            }
            
            for alert in alerts:
                color = self._get_severity_color_hex(alert.severity)
                embed = {
                    "title": f"{alert.severity.upper()}: {alert.message}",
                    "color": color,
                    "fields": [
                        {"name": "Valor", "value": str(alert.value), "inline": True},
                        {"name": "Umbral", "value": str(alert.threshold), "inline": True},
                        {"name": "Timestamp", "value": alert.timestamp.strftime('%Y-%m-%d %H:%M:%S'), "inline": False}
                    ]
                }
                message["embeds"].append(embed)
            
            response = requests.post(webhook_url, json=message)
            response.raise_for_status()
            
            logger.info("✅ Alerta enviada a Discord")
        except Exception as e:
            logger.error(f"Error enviando a Discord: {e}")
    
    def _create_email_body(self, alerts: List[Alert]) -> str:
        """Crear contenido HTML para el email"""
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .alert { margin: 10px 0; padding: 15px; border-radius: 5px; }
                .critical { background-color: #ffebee; border-left: 5px solid #f44336; }
                .high { background-color: #fff3e0; border-left: 5px solid #ff9800; }
                .medium { background-color: #fff8e1; border-left: 5px solid #ffc107; }
                .low { background-color: #e8f5e8; border-left: 5px solid #4caf50; }
                .header { background-color: #2196f3; color: white; padding: 20px; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🚨 Alertas del Sistema de Scraping</h2>
                <p>Se detectaron {count} alertas en el sistema</p>
            </div>
        """.format(count=len(alerts))
        
        for alert in alerts:
            html += f"""
            <div class="alert {alert.severity}">
                <h3>{alert.severity.upper()}: {alert.message}</h3>
                <p><strong>Valor:</strong> {alert.value}</p>
                <p><strong>Umbral:</strong> {alert.threshold}</p>
                <p><strong>Timestamp:</strong> {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    def _get_severity_color(self, severity: str) -> str:
        """Obtener color para Slack basado en severidad"""
        colors = {
            'critical': 'danger',
            'high': 'warning',
            'medium': 'warning',
            'low': 'good'
        }
        return colors.get(severity, 'good')
    
    def _get_severity_color_hex(self, severity: str) -> int:
        """Obtener color hexadecimal para Discord basado en severidad"""
        colors = {
            'critical': 0xff0000,  # Rojo
            'high': 0xff8c00,      # Naranja
            'medium': 0xffd700,    # Amarillo
            'low': 0x00ff00        # Verde
        }
        return colors.get(severity, 0x00ff00)
    
    def get_active_alerts(self) -> List[Alert]:
        """Obtener alertas activas (no resueltas)"""
        return [alert for alert in self.alerts if not alert.resolved]
    
    def resolve_alert(self, alert_id: int):
        """Marcar alerta como resuelta"""
        if 0 <= alert_id < len(self.alerts):
            self.alerts[alert_id].resolved = True
            logger.info(f"✅ Alerta resuelta: {self.alerts[alert_id].message}")
    
    def get_alert_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Obtener resumen de alertas de las últimas N horas"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_alerts = [
            alert for alert in self.alert_history
            if alert.timestamp >= cutoff_time
        ]
        
        summary = {
            'total_alerts': len(recent_alerts),
            'by_severity': {},
            'by_rule': {},
            'active_alerts': len(self.get_active_alerts()),
            'period_hours': hours
        }
        
        # Agrupar por severidad
        for alert in recent_alerts:
            severity = alert.severity
            summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1
        
        # Agrupar por regla
        for alert in recent_alerts:
            rule_name = alert.rule_name
            summary['by_rule'][rule_name] = summary['by_rule'].get(rule_name, 0) + 1
        
        return summary
    
    def export_alerts(self, output_file: str = None) -> str:
        """Exportar alertas a archivo"""
        if output_file is None:
            output_file = f"alerts_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            'exported_at': datetime.now().isoformat(),
            'rules': [asdict(rule) for rule in self.rules],
            'alerts': [asdict(alert) for alert in self.alert_history],
            'summary': self.get_alert_summary()
        }
        
        output_path = Path("reports") / output_file
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        logger.info(f"✅ Alertas exportadas a {output_path}")
        return str(output_path)


def get_alert_system() -> AlertSystem:
    """Obtener instancia del sistema de alertas"""
    return AlertSystem()


# Funciones de conveniencia
def check_scraping_alerts(scraping_data: Dict[str, Any]) -> List[Alert]:
    """Verificar alertas para datos de scraping"""
    alert_system = get_alert_system()
    alerts = alert_system.check_alerts(scraping_data)
    
    if alerts:
        alert_system.send_notifications(alerts)
    
    return alerts


def setup_alert_rules():
    """Configurar reglas de alerta por defecto"""
    alert_system = get_alert_system()
    alert_system.setup_default_rules()
    return alert_system


if __name__ == "__main__":
    # Prueba del sistema de alertas
    alert_system = AlertSystem()
    
    # Datos de ejemplo
    test_data = {
        'error_rate': 15.5,
        'success_rate': 75.0,
        'memory_usage_mb': 1200.0,
        'processing_time_seconds': 450.0,
        'projects_found': 0,
        'data_quality_score': 65.0
    }
    
    # Verificar alertas
    alerts = alert_system.check_alerts(test_data)
    print(f"Alertas generadas: {len(alerts)}")
    
    for alert in alerts:
        print(f"- {alert.severity.upper()}: {alert.message}")
    
    # Mostrar resumen
    summary = alert_system.get_alert_summary()
    print(f"Resumen: {summary}")
