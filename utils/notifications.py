"""
Sistema de notificaciones para el Peru Congress Laws Scraper
"""
import smtplib
import json
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class NotificationManager:
    """Gestor de notificaciones para el scraper"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = self._load_config(config_file)
        self.enabled = self.config.get('enabled', False)
    
    def _load_config(self, config_file: Optional[str] = None) -> Dict:
        """Cargar configuración de notificaciones"""
        if config_file is None:
            config_file = Path(__file__).parent.parent / "config" / "notifications.json"
        
        default_config = {
            'enabled': False,
            'email': {
                'enabled': False,
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': '',
                'password': '',
                'to_emails': []
            },
            'slack': {
                'enabled': False,
                'webhook_url': '',
                'channel': '#scraper-alerts'
            },
            'telegram': {
                'enabled': False,
                'bot_token': '',
                'chat_id': ''
            }
        }
        
        try:
            if Path(config_file).exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                        elif isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                if sub_key not in config[key]:
                                    config[key][sub_key] = sub_value
                    return config
            else:
                # Create default config file
                Path(config_file).parent.mkdir(exist_ok=True)
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2)
                return default_config
        except Exception as e:
            logger.warning(f"Error loading notification config: {e}")
            return default_config
    
    def send_email(self, subject: str, message: str, to_emails: Optional[List[str]] = None) -> bool:
        """Enviar notificación por email"""
        if not self.enabled or not self.config['email']['enabled']:
            return False
        
        try:
            email_config = self.config['email']
            to_emails = to_emails or email_config['to_emails']
            
            if not to_emails:
                logger.warning("No email recipients configured")
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = email_config['username']
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = f"[Peru Congress Scraper] {subject}"
            
            # Add timestamp and project info
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            full_message = f"""
Peru Congress Laws Scraper - Notificación

Fecha: {timestamp}
Asunto: {subject}

{message}

---
Este es un mensaje automático del sistema de scraping del Congreso del Perú.
            """
            
            msg.attach(MIMEText(full_message, 'plain', 'utf-8'))
            
            # Send email
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['username'], email_config['password'])
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email notification sent to {len(to_emails)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
            return False
    
    def send_slack(self, message: str, channel: Optional[str] = None) -> bool:
        """Enviar notificación a Slack"""
        if not self.enabled or not self.config['slack']['enabled']:
            return False
        
        try:
            slack_config = self.config['slack']
            channel = channel or slack_config['channel']
            
            payload = {
                'channel': channel,
                'text': f"🇵🇪 *Peru Congress Scraper*\n{message}",
                'username': 'Congress Scraper Bot',
                'icon_emoji': ':robot_face:'
            }
            
            response = requests.post(slack_config['webhook_url'], json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info("Slack notification sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")
            return False
    
    def send_telegram(self, message: str, chat_id: Optional[str] = None) -> bool:
        """Enviar notificación a Telegram"""
        if not self.enabled or not self.config['telegram']['enabled']:
            return False
        
        try:
            telegram_config = self.config['telegram']
            chat_id = chat_id or telegram_config['chat_id']
            
            bot_token = telegram_config['bot_token']
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            
            payload = {
                'chat_id': chat_id,
                'text': f"🇵🇪 Peru Congress Scraper\n\n{message}",
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info("Telegram notification sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error sending Telegram notification: {e}")
            return False
    
    def notify_scraping_start(self, date_range: tuple) -> None:
        """Notificar inicio de scraping"""
        message = f"""
🚀 *Scraping iniciado*
📅 Período: {date_range[0]} - {date_range[1]}
⏰ Hora: {datetime.now().strftime('%H:%M:%S')}
        """
        self._send_all_notifications("Scraping Iniciado", message)
    
    def notify_scraping_complete(self, projects_found: int, duration: float, errors: int = 0) -> None:
        """Notificar finalización de scraping"""
        status = "✅ Exitoso" if errors == 0 else f"⚠️ Completado con {errors} errores"
        
        message = f"""
{status}
📊 Proyectos encontrados: {projects_found}
⏱️ Duración: {duration:.2f} segundos
📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}
        """
        self._send_all_notifications("Scraping Completado", message)
    
    def notify_scraping_error(self, error_message: str) -> None:
        """Notificar error en scraping"""
        message = f"""
❌ *Error en scraping*
🔍 Detalle: {error_message}
⏰ Hora: {datetime.now().strftime('%H:%M:%S')}
        """
        self._send_all_notifications("Error en Scraping", message)
    
    def notify_analysis_complete(self, total_projects: int, analysis_type: str) -> None:
        """Notificar finalización de análisis"""
        message = f"""
📊 *Análisis completado*
📈 Tipo: {analysis_type}
📋 Proyectos analizados: {total_projects}
📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}
        """
        self._send_all_notifications("Análisis Completado", message)
    
    def notify_health_check(self, is_healthy: bool, issues: List[str]) -> None:
        """Notificar resultado de verificación de salud"""
        status = "✅ Proyecto saludable" if is_healthy else "❌ Problemas encontrados"
        
        message = f"""
🏥 *Verificación de salud*
{status}
        """
        
        if issues:
            message += "\n🔍 Problemas:\n"
            for issue in issues[:5]:  # Mostrar máximo 5 problemas
                message += f"• {issue}\n"
            if len(issues) > 5:
                message += f"• ... y {len(issues) - 5} más"
        
        self._send_all_notifications("Health Check", message)
    
    def _send_all_notifications(self, subject: str, message: str) -> None:
        """Enviar notificación por todos los canales habilitados"""
        if not self.enabled:
            return
        
        # Email
        if self.config['email']['enabled']:
            self.send_email(subject, message)
        
        # Slack
        if self.config['slack']['enabled']:
            self.send_slack(message)
        
        # Telegram
        if self.config['telegram']['enabled']:
            self.send_telegram(message)
    
    def test_notifications(self) -> Dict[str, bool]:
        """Probar todas las notificaciones configuradas"""
        test_message = f"""
🧪 *Prueba de notificaciones*
✅ Sistema funcionando correctamente
📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        """
        
        results = {}
        
        if self.config['email']['enabled']:
            results['email'] = self.send_email("Prueba de Notificación", test_message)
        
        if self.config['slack']['enabled']:
            results['slack'] = self.send_slack(test_message)
        
        if self.config['telegram']['enabled']:
            results['telegram'] = self.send_telegram(test_message)
        
        return results


def get_notification_manager() -> NotificationManager:
    """Obtener instancia del gestor de notificaciones"""
    return NotificationManager()


# Funciones de conveniencia
def notify_scraping_start(date_range: tuple):
    """Función de conveniencia para notificar inicio de scraping"""
    manager = get_notification_manager()
    manager.notify_scraping_start(date_range)


def notify_scraping_complete(projects_found: int, duration: float, errors: int = 0):
    """Función de conveniencia para notificar finalización de scraping"""
    manager = get_notification_manager()
    manager.notify_scraping_complete(projects_found, duration, errors)


def notify_scraping_error(error_message: str):
    """Función de conveniencia para notificar error en scraping"""
    manager = get_notification_manager()
    manager.notify_scraping_error(error_message)


if __name__ == "__main__":
    # Prueba del sistema de notificaciones
    manager = NotificationManager()
    
    if manager.enabled:
        print("🧪 Probando sistema de notificaciones...")
        results = manager.test_notifications()
        
        print("📊 Resultados:")
        for channel, success in results.items():
            status = "✅" if success else "❌"
            print(f"   {status} {channel}")
    else:
        print("⚠️ Sistema de notificaciones deshabilitado")
        print("💡 Habilite las notificaciones en config/notifications.json")
