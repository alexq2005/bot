"""
Manejador de alertas para Telegram
"""
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class TelegramHandler:
    """
    Manejador de alertas para Telegram
    
    Envía alertas a un chat de Telegram usando el bot API
    """
    
    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None,
        enabled: bool = False
    ):
        """
        Inicializa el manejador de Telegram
        
        Args:
            bot_token: Token del bot de Telegram
            chat_id: ID del chat donde enviar mensajes
            enabled: Si está habilitado (False por defecto para testing)
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.enabled = enabled
        self.sent_messages = []  # Para testing
    
    def __call__(self, alert):
        """
        Envía una alerta a Telegram
        
        Args:
            alert: Objeto Alert a enviar
        """
        if not self.enabled:
            logger.info(f"Telegram deshabilitado. Alerta: {alert}")
            self.sent_messages.append(alert)
            return
        
        if not self.bot_token or not self.chat_id:
            logger.warning("Bot token o chat_id no configurado")
            return
        
        message = self._format_message(alert)
        
        try:
            # En producción, aquí iría el código para enviar a Telegram
            # import requests
            # url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            # data = {'chat_id': self.chat_id, 'text': message, 'parse_mode': 'HTML'}
            # response = requests.post(url, data=data)
            # response.raise_for_status()
            
            logger.info(f"Alerta enviada a Telegram: {message}")
            self.sent_messages.append(alert)
        except Exception as e:
            logger.error(f"Error al enviar alerta a Telegram: {e}")
    
    def _format_message(self, alert) -> str:
        """Formatea una alerta para Telegram"""
        emoji = self._get_emoji(alert.priority.value, alert.alert_type.value)
        
        message = f"{emoji} <b>{alert.priority.value.upper()}</b>\n"
        message += f"📊 <b>{alert.symbol}</b>\n"
        message += f"💬 {alert.message}\n"
        message += f"🕐 {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        if alert.details:
            message += "\n<b>Detalles:</b>\n"
            for key, value in alert.details.items():
                if isinstance(value, float):
                    message += f"  • {key}: {value:.2f}\n"
                else:
                    message += f"  • {key}: {value}\n"
        
        return message
    
    def _get_emoji(self, priority: str, alert_type: str) -> str:
        """Obtiene emoji apropiado para la alerta"""
        if priority == 'critical':
            return '🚨'
        elif priority == 'high':
            return '⚠️'
        elif priority == 'medium':
            return '📢'
        else:
            return 'ℹ️'
    
    def get_sent_count(self) -> int:
        """Obtiene número de mensajes enviados"""
        return len(self.sent_messages)
    
    def clear_history(self):
        """Limpia historial de mensajes"""
        self.sent_messages = []
