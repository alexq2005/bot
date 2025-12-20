"""
IOL Trading Bot - Automated trading bot with IOL Invertir Online integration.

This module provides an automated trading bot that:
- Generates trading signals using technical analysis
- Validates orders before execution
- Executes orders through IOL broker
- Manages risk with automatic stop loss/take profit
- Sends alerts via Telegram
"""

import logging
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import pandas as pd

from .iol_client import IOLBrokerClient
from ..analysis.technical_indicators import TechnicalIndicators
from ..validators.order_validator import OrderValidator
from ..alerts.alert_system import AlertSystem
from ..alerts.telegram_handler import TelegramHandler


class IOLTradingBot:
    """
    Automated trading bot with IOL broker integration.
    
    Features:
    - Technical analysis based signal generation
    - Order validation
    - Semi-automatic execution (with confirmation)
    - Risk management (stop loss/take profit)
    - Telegram notifications
    """
    
    def __init__(self, iol_client: IOLBrokerClient, 
                 auto_execute: bool = False,
                 telegram_enabled: bool = False):
        """
        Initialize trading bot.
        
        Args:
            iol_client: Authenticated IOL broker client
            auto_execute: If True, executes orders automatically without confirmation
            telegram_enabled: If True, sends alerts via Telegram
        """
        self.iol_client = iol_client
        self.auto_execute = auto_execute
        self.telegram_enabled = telegram_enabled
        
        self.technical_indicators = TechnicalIndicators()
        self.order_validator = OrderValidator()
        self.alert_system = AlertSystem()
        
        # Setup Telegram if enabled
        if telegram_enabled:
            telegram_handler = TelegramHandler()
            self.alert_system.add_handler(telegram_handler)
        
        self.logger = logging.getLogger(__name__)
        self.active_positions = {}
        self.pending_orders = {}
    
    def analyze_symbol(self, symbol: str, historical_data: pd.DataFrame) -> Dict:
        """
        Analyze a symbol using technical indicators.
        
        Args:
            symbol: Stock symbol to analyze
            historical_data: Historical price data (OHLCV)
        
        Returns:
            dict: Analysis results with signals and indicators
        """
        # Calculate all technical indicators
        df_with_indicators = self.technical_indicators.calculate_all_indicators(historical_data)
        
        # Get trading signals
        signals = self.technical_indicators.get_trading_signals(df_with_indicators)
        
        # Get latest indicator values
        latest_indicators = self.technical_indicators.get_latest_indicators(df_with_indicators)
        
        # Calculate stop loss and take profit
        sl, tp = self.technical_indicators.calculate_atr_stop_loss(
            df_with_indicators,
            risk_reward_ratio=1.5
        )
        
        return {
            'symbol': symbol,
            'signals': signals,
            'indicators': latest_indicators,
            'stop_loss': sl,
            'take_profit': tp,
            'recommendation': self._get_recommendation(signals)
        }
    
    def _get_recommendation(self, signals: Dict) -> str:
        """
        Get trading recommendation based on signals.
        
        Args:
            signals: Dict of trading signals
        
        Returns:
            str: 'COMPRA', 'VENTA', or 'NEUTRAL'
        """
        buy_count = sum(1 for s in signals.values() if s == 'COMPRA')
        sell_count = sum(1 for s in signals.values() if s == 'VENTA')
        
        if buy_count >= 3:
            return 'COMPRA'
        elif sell_count >= 3:
            return 'VENTA'
        else:
            return 'NEUTRAL'
    
    def execute_trade(self, symbol: str, signal: str, quantity: int,
                      stop_loss: Optional[float] = None,
                      take_profit: Optional[float] = None) -> Tuple[bool, str]:
        """
        Execute a trade based on analysis.
        
        Args:
            symbol: Stock symbol
            signal: Trading signal ('COMPRA' or 'VENTA')
            quantity: Number of shares
            stop_loss: Stop loss price
            take_profit: Take profit price
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Get account balance
            balance = self.iol_client.get_account_balance()
            available_balance = balance.get('saldo_disponible', 0)
            
            # Get current market price
            price_data = self.iol_client.get_market_price(symbol)
            if not price_data:
                return False, f"Could not get market price for {symbol}"
            
            current_price = price_data.get('ultimoPrecio')
            
            # Map signal to side
            side = 'buy' if signal == 'COMPRA' else 'sell'
            
            # Validate order
            order = {
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'price': current_price
            }
            
            is_valid, validation_results = self.order_validator.validate_order(
                order=order,
                account_balance=available_balance,
                current_positions=self.active_positions,
                last_price=current_price,
                daily_order_count=len(self.pending_orders)
            )
            
            if not is_valid:
                errors = [r['message'] for r in validation_results if r['level'] == 'ERROR']
                return False, f"Order validation failed: {'; '.join(errors)}"
            
            # Show confirmation if not auto-executing
            if not self.auto_execute:
                self.logger.info(f"Trade ready: {side} {quantity} {symbol} @ {current_price}")
                self.logger.info(f"Total cost: ${quantity * current_price:.2f}")
                if stop_loss:
                    self.logger.info(f"Stop Loss: ${stop_loss:.2f}")
                if take_profit:
                    self.logger.info(f"Take Profit: ${take_profit:.2f}")
                
                # In production, this would wait for manual confirmation
                # For now, we'll just log
                self.logger.warning("Auto-execute is OFF. Order not placed.")
                return False, "Manual confirmation required"
            
            # Execute order
            success, order_result = self.iol_client.place_order(
                symbol=symbol,
                side=side,
                quantity=quantity,
                order_type='market'
            )
            
            if success:
                order_id = order_result.get('numeroOrden')
                
                # Track position
                self.active_positions[symbol] = {
                    'quantity': quantity,
                    'entry_price': current_price,
                    'side': side,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'order_id': order_id
                }
                
                # Send alert
                self.alert_system.check_signal_alert(
                    signal=signal,
                    symbol=symbol,
                    confidence=0.85,
                    price=current_price,
                    quantity=quantity
                )
                
                message = f"Order executed: {side} {quantity} {symbol} @ ${current_price:.2f}"
                self.logger.info(message)
                return True, message
            else:
                return False, "Order execution failed"
        
        except Exception as e:
            error_msg = f"Error executing trade: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def monitor_positions(self):
        """
        Monitor active positions and manage stop loss/take profit.
        """
        for symbol, position in list(self.active_positions.items()):
            try:
                # Get current price
                price_data = self.iol_client.get_market_price(symbol)
                if not price_data:
                    continue
                
                current_price = price_data.get('ultimoPrecio')
                entry_price = position['entry_price']
                stop_loss = position.get('stop_loss')
                take_profit = position.get('take_profit')
                
                # Check stop loss
                if stop_loss and current_price <= stop_loss:
                    self.logger.warning(f"Stop loss triggered for {symbol}")
                    self._close_position(symbol, current_price, "Stop loss triggered")
                
                # Check take profit
                elif take_profit and current_price >= take_profit:
                    self.logger.info(f"Take profit triggered for {symbol}")
                    self._close_position(symbol, current_price, "Take profit reached")
                
            except Exception as e:
                self.logger.error(f"Error monitoring position {symbol}: {e}")
    
    def _close_position(self, symbol: str, price: float, reason: str):
        """
        Close an active position.
        
        Args:
            symbol: Stock symbol
            price: Current price
            reason: Reason for closing
        """
        position = self.active_positions.get(symbol)
        if not position:
            return
        
        try:
            # Determine opposite side
            close_side = 'sell' if position['side'] == 'buy' else 'buy'
            
            # Place closing order
            success, order_result = self.iol_client.place_order(
                symbol=symbol,
                side=close_side,
                quantity=position['quantity'],
                order_type='market'
            )
            
            if success:
                # Calculate P&L
                if position['side'] == 'buy':
                    pnl = (price - position['entry_price']) * position['quantity']
                else:
                    pnl = (position['entry_price'] - price) * position['quantity']
                
                message = f"Position closed: {symbol}. {reason}. P&L: ${pnl:.2f}"
                self.logger.info(message)
                
                # Send alert
                self.alert_system.check_custom_condition(
                    condition_met=True,
                    symbol=symbol,
                    message=message
                )
                
                # Remove from active positions
                del self.active_positions[symbol]
            
        except Exception as e:
            self.logger.error(f"Error closing position {symbol}: {e}")
    
    def get_portfolio_summary(self) -> Dict:
        """
        Get summary of current portfolio.
        
        Returns:
            dict: Portfolio summary with positions and P&L
        """
        try:
            balance = self.iol_client.get_account_balance()
            positions = self.iol_client.get_positions()
            
            total_value = balance.get('saldo_total', 0)
            available_cash = balance.get('saldo_disponible', 0)
            
            return {
                'total_value': total_value,
                'available_cash': available_cash,
                'positions': positions,
                'num_positions': len(positions)
            }
        
        except Exception as e:
            self.logger.error(f"Error getting portfolio summary: {e}")
            return {}
