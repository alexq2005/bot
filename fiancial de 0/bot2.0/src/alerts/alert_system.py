"""
Sistema de Alertas Inteligentes
Detecta condiciones de mercado y envía notificaciones
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Callable
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AlertType(Enum):
    """Tipos de alertas"""
    DIVERGENCE = "divergence"
    BREAKOUT = "breakout"
    PATTERN = "pattern"
    SIGNAL = "signal"
    CUSTOM = "custom"


class AlertPriority(Enum):
    """Prioridad de alertas"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Alert:
    """Representa una alerta individual"""
    
    def __init__(
        self,
        alert_type: AlertType,
        priority: AlertPriority,
        symbol: str,
        message: str,
        details: Optional[Dict] = None
    ):
        self.alert_type = alert_type
        self.priority = priority
        self.symbol = symbol
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now()
        self.sent = False
    
    def to_dict(self) -> Dict:
        """Convierte alerta a diccionario"""
        return {
            'type': self.alert_type.value,
            'priority': self.priority.value,
            'symbol': self.symbol,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp.isoformat(),
            'sent': self.sent
        }
    
    def __repr__(self):
        return f"Alert({self.priority.value.upper()}, {self.symbol}, {self.message})"


class AlertSystem:
    """
    Sistema de alertas inteligentes
    
    Detecta:
    - Divergencias RSI/MACD
    - Breakouts de niveles clave
    - Patrones de velas
    - Señales de trading
    """
    
    def __init__(self):
        self.alerts: List[Alert] = []
        self.alert_handlers: List[Callable] = []
    
    def add_handler(self, handler: Callable):
        """Agrega un manejador de alertas (ej: Telegram, Email)"""
        self.alert_handlers.append(handler)
    
    def _trigger_alert(self, alert: Alert):
        """Dispara una alerta a todos los manejadores"""
        self.alerts.append(alert)
        
        for handler in self.alert_handlers:
            try:
                handler(alert)
                alert.sent = True
            except Exception as e:
                logger.error(f"Error al enviar alerta: {e}")
    
    def check_rsi_divergence(
        self,
        df: pd.DataFrame,
        rsi_column: str = 'rsi',
        lookback: int = 20
    ) -> Optional[Alert]:
        """
        Detecta divergencias RSI
        
        Divergencia alcista: Precio hace mínimos más bajos, RSI hace mínimos más altos
        Divergencia bajista: Precio hace máximos más altos, RSI hace máximos más bajos
        """
        if len(df) < lookback:
            return None
        
        recent_data = df.tail(lookback).copy()
        
        # Encontrar mínimos y máximos locales
        price_lows = recent_data['close'].iloc[:-1] < recent_data['close'].iloc[1:].values
        price_lows = price_lows & (recent_data['close'].iloc[:-1].values < recent_data['close'].shift(1).iloc[:-1].values)
        
        if rsi_column in recent_data.columns:
            rsi = recent_data[rsi_column]
            
            # Divergencia alcista (bullish)
            last_price_low_idx = None
            prev_price_low_idx = None
            
            for i in range(len(recent_data) - 2, 0, -1):
                if (recent_data['close'].iloc[i] < recent_data['close'].iloc[i-1] and 
                    recent_data['close'].iloc[i] < recent_data['close'].iloc[i+1]):
                    if last_price_low_idx is None:
                        last_price_low_idx = i
                    elif prev_price_low_idx is None:
                        prev_price_low_idx = i
                        break
            
            if last_price_low_idx and prev_price_low_idx:
                price_low_1 = recent_data['close'].iloc[prev_price_low_idx]
                price_low_2 = recent_data['close'].iloc[last_price_low_idx]
                rsi_low_1 = rsi.iloc[prev_price_low_idx]
                rsi_low_2 = rsi.iloc[last_price_low_idx]
                
                # Divergencia alcista: precio baja, RSI sube
                if price_low_2 < price_low_1 and rsi_low_2 > rsi_low_1:
                    alert = Alert(
                        alert_type=AlertType.DIVERGENCE,
                        priority=AlertPriority.HIGH,
                        symbol=df.get('symbol', ['UNKNOWN'])[0] if 'symbol' in df.columns else 'UNKNOWN',
                        message="Divergencia alcista detectada (RSI)",
                        details={
                            'price_low_1': float(price_low_1),
                            'price_low_2': float(price_low_2),
                            'rsi_low_1': float(rsi_low_1),
                            'rsi_low_2': float(rsi_low_2)
                        }
                    )
                    self._trigger_alert(alert)
                    return alert
        
        return None
    
    def check_bollinger_breakout(
        self,
        df: pd.DataFrame,
        bb_upper: str = 'bb_upper',
        bb_lower: str = 'bb_lower'
    ) -> Optional[Alert]:
        """Detecta breakouts de Bandas de Bollinger"""
        if len(df) < 2:
            return None
        
        current = df.iloc[-1]
        previous = df.iloc[-2]
        
        symbol = current.get('symbol', 'UNKNOWN')
        
        # Breakout alcista (precio cruza banda superior)
        if (bb_upper in df.columns and 
            previous['close'] <= previous[bb_upper] and 
            current['close'] > current[bb_upper]):
            
            alert = Alert(
                alert_type=AlertType.BREAKOUT,
                priority=AlertPriority.MEDIUM,
                symbol=symbol,
                message="Breakout alcista - Precio sobre banda superior",
                details={
                    'price': float(current['close']),
                    'bb_upper': float(current[bb_upper]),
                    'breakout_percent': float((current['close'] - current[bb_upper]) / current[bb_upper] * 100)
                }
            )
            self._trigger_alert(alert)
            return alert
        
        # Breakout bajista (precio cruza banda inferior)
        if (bb_lower in df.columns and 
            previous['close'] >= previous[bb_lower] and 
            current['close'] < current[bb_lower]):
            
            alert = Alert(
                alert_type=AlertType.BREAKOUT,
                priority=AlertPriority.MEDIUM,
                symbol=symbol,
                message="Breakout bajista - Precio bajo banda inferior",
                details={
                    'price': float(current['close']),
                    'bb_lower': float(current[bb_lower]),
                    'breakout_percent': float((current[bb_lower] - current['close']) / current[bb_lower] * 100)
                }
            )
            self._trigger_alert(alert)
            return alert
        
        return None
    
    def check_pattern_alert(
        self,
        pattern_name: str,
        pattern_detected: bool,
        symbol: str,
        is_bullish: bool
    ) -> Optional[Alert]:
        """Crea alerta para patrones de velas"""
        if not pattern_detected:
            return None
        
        sentiment = "alcista" if is_bullish else "bajista"
        priority = AlertPriority.HIGH if is_bullish else AlertPriority.MEDIUM
        
        alert = Alert(
            alert_type=AlertType.PATTERN,
            priority=priority,
            symbol=symbol,
            message=f"Patrón {pattern_name} {sentiment} detectado",
            details={
                'pattern': pattern_name,
                'sentiment': sentiment
            }
        )
        self._trigger_alert(alert)
        return alert
    
    def check_signal_alert(
        self,
        signal: str,
        symbol: str,
        confidence: float = 1.0,
        indicators: Optional[Dict] = None
    ) -> Optional[Alert]:
        """Crea alerta para señales de trading"""
        if signal == 'NEUTRAL':
            return None
        
        priority = AlertPriority.HIGH if confidence > 0.7 else AlertPriority.MEDIUM
        
        alert = Alert(
            alert_type=AlertType.SIGNAL,
            priority=priority,
            symbol=symbol,
            message=f"Señal de {signal}",
            details={
                'signal': signal,
                'confidence': confidence,
                'indicators': indicators or {}
            }
        )
        self._trigger_alert(alert)
        return alert
    
    def check_custom_condition(
        self,
        condition_met: bool,
        symbol: str,
        message: str,
        priority: AlertPriority = AlertPriority.MEDIUM,
        details: Optional[Dict] = None
    ) -> Optional[Alert]:
        """Permite crear alertas personalizadas"""
        if not condition_met:
            return None
        
        alert = Alert(
            alert_type=AlertType.CUSTOM,
            priority=priority,
            symbol=symbol,
            message=message,
            details=details or {}
        )
        self._trigger_alert(alert)
        return alert
    
    def get_alerts(
        self,
        alert_type: Optional[AlertType] = None,
        priority: Optional[AlertPriority] = None,
        sent: Optional[bool] = None
    ) -> List[Alert]:
        """Obtiene alertas filtradas"""
        filtered = self.alerts
        
        if alert_type:
            filtered = [a for a in filtered if a.alert_type == alert_type]
        
        if priority:
            filtered = [a for a in filtered if a.priority == priority]
        
        if sent is not None:
            filtered = [a for a in filtered if a.sent == sent]
        
        return filtered
    
    def clear_alerts(self):
        """Limpia todas las alertas"""
        self.alerts = []
    
    def get_summary(self) -> Dict:
        """Obtiene resumen de alertas"""
        total = len(self.alerts)
        by_type = {}
        by_priority = {}
        sent_count = sum(1 for a in self.alerts if a.sent)
        
        for alert in self.alerts:
            by_type[alert.alert_type.value] = by_type.get(alert.alert_type.value, 0) + 1
            by_priority[alert.priority.value] = by_priority.get(alert.priority.value, 0) + 1
        
        return {
            'total_alerts': total,
            'sent': sent_count,
            'pending': total - sent_count,
            'by_type': by_type,
            'by_priority': by_priority
        }
