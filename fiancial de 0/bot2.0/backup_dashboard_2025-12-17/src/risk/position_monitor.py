"""
Position Monitor
Servicio para monitorear posiciones activas y ejecutar cierres automáticos por SL/TP
"""

from typing import List, Dict
from datetime import datetime
from ..database.db_manager import db_manager
from ..database.models import ActivePosition, Trade
from ..risk.dynamic_risk_manager import DynamicRiskManager
from ..utils.logger import log


class PositionMonitor:
    """Monitor de posiciones activas con cierre automático por SL/TP"""
    
    def __init__(self, iol_client):
        """
        Args:
            iol_client: Cliente IOL para obtener precios y ejecutar cierres
        """
        self.client = iol_client
        self.risk_mgr = DynamicRiskManager(
            sl_atr_multiplier=2.0,
            tp_atr_multiplier=3.0,
            trailing_stop=True
        )
    
    def check_all_positions(self) -> Dict[str, int]:
        """
        Revisa todas las posiciones activas y ejecuta cierres si es necesario
        
        Returns:
            Dict con estadísticas: {'checked': N, 'closed_sl': N, 'closed_tp': N, 'updated': N}
        """
        stats = {
            'checked': 0,
            'closed_sl': 0,
            'closed_tp': 0,
            'updated': 0,
            'errors': 0
        }
        
        try:
            # Obtener posiciones activas
            with db_manager.get_session() as session:
                active_positions = session.query(ActivePosition).all()
                
                if not active_positions:
                    return stats
                
                log.info(f"🔍 Monitoreando {len(active_positions)} posiciones activas...")
                
                for pos in active_positions:
                    stats['checked'] += 1
                    
                    try:
                        # Obtener precio actual del mercado
                        current_price = self._get_current_price(pos.symbol)
                        
                        if current_price is None:
                            log.warning(f"⚠ No se pudo obtener precio para {pos.symbol}")
                            stats['errors'] += 1
                            continue
                        
                        # Actualizar precio en DB
                        pos.current_price = current_price
                        pos.current_pnl = (current_price - pos.entry_price) * pos.quantity
                        pos.current_pnl_pct = ((current_price - pos.entry_price) / pos.entry_price) * 100
                        
                        # Verificar si hay que cerrar
                        exit_decision = self.risk_mgr.should_exit(
                            current_price=current_price,
                            entry_price=pos.entry_price,
                            stop_loss=pos.stop_loss,
                            take_profit=pos.take_profit,
                            direction=pos.direction
                        )
                        
                        if exit_decision['exit']:
                            # CERRAR POSICIÓN
                            success = self._close_position(
                                pos, 
                                current_price, 
                                reason=exit_decision['reason']
                            )
                            
                            if success:
                                if exit_decision['reason'] == 'STOP_LOSS':
                                    stats['closed_sl'] += 1
                                    log.warning(f"🛑 Stop Loss ejecutado: {pos.symbol} @ ${current_price:,.2f}")
                                else:  # TAKE_PROFIT
                                    stats['closed_tp'] += 1
                                    log.info(f"🎯 Take Profit ejecutado: {pos.symbol} @ ${current_price:,.2f}")
                                
                                # Eliminar de posiciones activas
                                session.delete(pos)
                        else:
                            # Solo actualizar precio
                            stats['updated'] += 1
                            
                            # Trailing Stop (mover SL a favor si aplicable)
                            if pos.trailing_stop:
                                new_sl = self.risk_mgr.update_trailing_stop(
                                    entry_price=pos.entry_price,
                                    current_price=current_price,
                                    current_sl=pos.stop_loss,
                                    atr=pos.atr,
                                    direction=pos.direction
                                )
                                
                                if new_sl != pos.stop_loss:
                                    log.info(f"📈 Trailing Stop ajustado: {pos.symbol} SL ${pos.stop_loss:,.2f} → ${new_sl:,.2f}")
                                    pos.stop_loss = new_sl
                    
                    except Exception as e:
                        log.error(f"❌ Error monitoreando {pos.symbol}: {e}")
                        stats['errors'] += 1
                
                # Commit cambios
                session.commit()
        
        except Exception as e:
            log.error(f"❌ Error en check_all_positions: {e}")
            stats['errors'] += 1
        
        return stats
    
    def _get_current_price(self, symbol: str) -> float:
        """Obtiene el precio actual de un símbolo"""
        try:
            quote = self.client.get_last_price(symbol, market="bCBA")
            if quote and 'price' in quote:
                return float(quote['price'])
            return None
        except Exception as e:
            log.error(f"Error obteniendo precio de {symbol}: {e}")
            return None
    
    def _close_position(self, position: ActivePosition, exit_price: float, reason: str) -> bool:
        """
        Cierra una posición en el mercado y registra el resultado
        
        Args:
            position: Posición a cerrar
            exit_price: Precio de salida
            reason: 'STOP_LOSS' o 'TAKE_PROFIT'
        
        Returns:
            True si se cerró exitosamente
        """
        try:
            # Ejecutar venta en el mercado
            result = self.client.sell(position.symbol, position.quantity)
            
            if not result:
                log.error(f"❌ Falló venta de {position.symbol}")
                return False
            
            # Actualizar trade original como cerrado
            with db_manager.get_session() as session:
                if position.trade_id:
                    original_trade = session.query(Trade).filter_by(id=position.trade_id).first()
                    if original_trade:
                        original_trade.is_closed = True
                        original_trade.close_timestamp = datetime.now()
                        original_trade.pnl = position.current_pnl
                        original_trade.pnl_pct = position.current_pnl_pct
                
                # Registrar nuevo trade de VENTA
                close_trade = Trade(
                    symbol=position.symbol,
                    action="SELL",
                    quantity=position.quantity,
                    price=exit_price,
                    total_value=position.quantity * exit_price,
                    technical_signal=f"AUTO_CLOSE_{reason}",
                    mode=position.mode,
                    notes=f"Cierre automático por {reason}. P&L: ${position.current_pnl:,.2f} ({position.current_pnl_pct:+.2f}%)",
                    pnl=position.current_pnl,
                    pnl_pct=position.current_pnl_pct,
                    is_closed=True
                )
                session.add(close_trade)
                session.commit()
            
            log.info(f"✅ Posición {position.symbol} cerrada: PnL ${position.current_pnl:,.2f} ({position.current_pnl_pct:+.2f}%)")
            return True
            
        except Exception as e:
            log.error(f"❌ Error cerrando posición {position.symbol}: {e}")
            return False


def get_position_monitor(iol_client):
    """Factory function para crear PositionMonitor"""
    return PositionMonitor(iol_client)
