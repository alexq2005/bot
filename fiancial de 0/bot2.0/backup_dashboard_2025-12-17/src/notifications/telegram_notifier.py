"""
Telegram Notifier
Sistema de notificaciones vía Telegram Bot
"""

import requests
from typing import Optional, Dict
from datetime import datetime


class TelegramNotifier:
    """Notificador vía Telegram"""
    
    def __init__(self, bot_token: str = "", chat_id: str = ""):
        """
        Inicializa el notificador de Telegram
        
        Args:
            bot_token: Token del bot de Telegram
            chat_id: ID del chat donde enviar mensajes
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.enabled = bool(bot_token and chat_id)
        
        if self.enabled:
            print("✓ Telegram Notifier activado")
        else:
            print("⚠ Telegram Notifier desactivado (falta configuración)")
    
    def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        Envía un mensaje a Telegram
        
        Args:
            message: Mensaje a enviar
            parse_mode: Modo de parseo (HTML o Markdown)
        
        Returns:
            bool: True si se envió exitosamente
        """
        if not self.enabled:
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode
            }
            
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Error enviando mensaje a Telegram: {e}")
            return False
    
    def notify_trade(self, trade_info: Dict) -> bool:
        """
        Notifica la ejecución de un trade
        
        Args:
            trade_info: Dict con información del trade
        
        Returns:
            bool: True si se envió exitosamente
        """
        action = trade_info.get('action', 'UNKNOWN')
        symbol = trade_info.get('symbol', 'N/A')
        quantity = trade_info.get('quantity', 0)
        price = trade_info.get('price', 0)
        total_value = trade_info.get('total_value', 0)
        
        # Emoji según acción
        emoji = "🟢" if action == "BUY" else "🔴" if action == "SELL" else "⚪"
        
        message = f"""
{emoji} <b>TRADE EJECUTADO</b>

<b>Acción:</b> {action}
<b>Símbolo:</b> {symbol}
<b>Cantidad:</b> {quantity}
<b>Precio:</b> ${price:,.2f}
<b>Valor Total:</b> ${total_value:,.2f}

<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        
        return self.send_message(message.strip())
    
    def notify_signal(self, signal_info: Dict) -> bool:
        """
        Notifica una señal de trading de alta confianza
        
        Args:
            signal_info: Dict con información de la señal
        
        Returns:
            bool: True si se envió exitosamente
        """
        signal = signal_info.get('signal', 'HOLD')
        symbol = signal_info.get('symbol', 'N/A')
        confidence = signal_info.get('confidence', 0) * 100
        reasoning = signal_info.get('reasoning', 'N/A')
        
        # Solo notificar señales de alta confianza
        if confidence < 70:
            return False
        
        emoji = "🚀" if signal == "BUY" else "⚠️" if signal == "SELL" else "ℹ️"
        
        message = f"""
{emoji} <b>SEÑAL DE ALTA CONFIANZA</b>

<b>Símbolo:</b> {symbol}
<b>Señal:</b> {signal}
<b>Confianza:</b> {confidence:.1f}%

<b>Razón:</b> {reasoning}

<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        
        return self.send_message(message.strip())
    
    def notify_risk_alert(self, alert_info: Dict) -> bool:
        """
        Notifica una alerta de riesgo
        
        Args:
            alert_info: Dict con información de la alerta
        
        Returns:
            bool: True si se envió exitosamente
        """
        alert_type = alert_info.get('type', 'UNKNOWN')
        message_text = alert_info.get('message', 'N/A')
        severity = alert_info.get('severity', 'INFO')
        
        # Emoji según severidad
        emoji_map = {
            'CRITICAL': '🚨',
            'WARNING': '⚠️',
            'INFO': 'ℹ️'
        }
        emoji = emoji_map.get(severity, 'ℹ️')
        
        message = f"""
{emoji} <b>ALERTA DE RIESGO</b>

<b>Tipo:</b> {alert_type}
<b>Severidad:</b> {severity}

{message_text}

<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        
        return self.send_message(message.strip())
    
    def notify_error(self, error_info: Dict) -> bool:
        """
        Notifica un error crítico del sistema
        
        Args:
            error_info: Dict con información del error
        
        Returns:
            bool: True si se envió exitosamente
        """
        error_type = error_info.get('type', 'UNKNOWN')
        error_message = error_info.get('message', 'N/A')
        component = error_info.get('component', 'N/A')
        
        message = f"""
🔥 <b>ERROR CRÍTICO</b>

<b>Componente:</b> {component}
<b>Tipo:</b> {error_type}

<b>Mensaje:</b>
{error_message}

<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        
        return self.send_message(message.strip())
    
    def notify_daily_summary(self, summary: Dict) -> bool:
        """
        Envía resumen diario de rendimiento
        
        Args:
            summary: Dict con métricas del día
        
        Returns:
            bool: True si se envió exitosamente
        """
        total_value = summary.get('total_value', 0)
        daily_pnl = summary.get('daily_pnl', 0)
        daily_pnl_pct = summary.get('daily_pnl_pct', 0)
        total_trades = summary.get('total_trades', 0)
        win_rate = summary.get('win_rate', 0)
        
        # Emoji según rendimiento
        emoji = "📈" if daily_pnl > 0 else "📉" if daily_pnl < 0 else "➡️"
        
        message = f"""
{emoji} <b>RESUMEN DIARIO</b>

<b>Valor del Portafolio:</b> ${total_value:,.2f}
<b>P&L del Día:</b> ${daily_pnl:,.2f} ({daily_pnl_pct:+.2f}%)

<b>Trades Ejecutados:</b> {total_trades}
<b>Win Rate:</b> {win_rate:.1f}%

<i>{datetime.now().strftime('%Y-%m-%d')}</i>
"""
        
        return self.send_message(message.strip())
    
    def notify_startup(self, config: Dict) -> bool:
        """
        Notifica el inicio del bot
        
        Args:
            config: Dict con configuración del bot
        
        Returns:
            bool: True si se envió exitosamente
        """
        mode = config.get('mode', 'UNKNOWN')
        symbols = config.get('symbols', [])
        
        message = f"""
🤖 <b>BOT INICIADO</b>

<b>Modo:</b> {mode}
<b>Símbolos:</b> {', '.join(symbols)}

<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        
        return self.send_message(message.strip())
    
    def notify_shutdown(self) -> bool:
        """
        Notifica el apagado del bot
        
        Returns:
            bool: True si se envió exitosamente
        """
        message = f"""
🛑 <b>BOT DETENIDO</b>

<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        
        return self.send_message(message.strip())
