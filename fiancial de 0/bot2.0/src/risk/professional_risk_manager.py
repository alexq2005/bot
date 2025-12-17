"""
Professional Risk Manager
Risk manager de nivel profesional con control de drawdown, exposure y kill switch
"""

from typing import Optional, Dict
from datetime import datetime

from ..domain.signal import Signal
from ..domain.decision import OrderDecision


class ProfessionalRiskManager:
    """
    Risk Manager profesional con:
    - Riesgo por trade basado en stop distance
    - Control de drawdown global
    - Límite de exposición total
    - Kill switch automático
    - Ajuste dinámico de riesgo
    
    Este es el componente MÁS IMPORTANTE del sistema.
    Sin un risk manager robusto, ningún bot sobrevive en producción.
    """
    
    def __init__(
        self,
        initial_equity: float,
        risk_per_trade: float = 0.01,  # 1% por trade
        max_drawdown: float = 0.15,     # 15% drawdown máximo
        max_exposure: float = 0.30,     # 30% exposición máxima
        min_risk_per_trade: float = 0.005,  # 0.5% mínimo
        max_risk_per_trade: float = 0.02    # 2% máximo
    ):
        """
        Inicializa el Risk Manager
        
        Args:
            initial_equity: Capital inicial
            risk_per_trade: Porcentaje de capital a arriesgar por trade (0.01 = 1%)
            max_drawdown: Drawdown máximo permitido antes de kill switch (0.15 = 15%)
            max_exposure: Exposición máxima total permitida (0.30 = 30%)
            min_risk_per_trade: Riesgo mínimo por trade (para ajuste dinámico)
            max_risk_per_trade: Riesgo máximo por trade (para ajuste dinámico)
        """
        # Equity tracking
        self.initial_equity = initial_equity
        self.equity = initial_equity
        self.peak_equity = initial_equity
        
        # Risk parameters
        self.risk_per_trade = risk_per_trade
        self.max_drawdown = max_drawdown
        self.max_exposure = max_exposure
        self.min_risk_per_trade = min_risk_per_trade
        self.max_risk_per_trade = max_risk_per_trade
        
        # State
        self.trading_enabled = True
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.consecutive_losses = 0
        
        # Tracking
        self.equity_history = [initial_equity]
        self.decisions_log = []
    
    def update_equity(self, equity: float):
        """
        Actualiza el equity actual y el peak equity
        
        Args:
            equity: Nuevo valor del equity
        """
        self.equity = equity
        self.peak_equity = max(self.peak_equity, equity)
        self.equity_history.append(equity)
        
        # Check if we need to disable trading due to drawdown
        if self.current_drawdown() > self.max_drawdown:
            self.trading_enabled = False
    
    def current_drawdown(self) -> float:
        """
        Calcula el drawdown actual desde el peak
        
        Returns:
            Drawdown como porcentaje (0.15 = 15%)
        """
        if self.peak_equity == 0:
            return 0.0
        return (self.peak_equity - self.equity) / self.peak_equity
    
    def evaluate(
        self,
        signal: Signal,
        current_exposure: float = 0.0
    ) -> OrderDecision:
        """
        Evalúa una señal y decide si aprobarla o rechazarla
        
        Este es el método CRÍTICO del sistema. Aquí se decide:
        1. Si operamos o no
        2. Cuánto arriesgamos
        3. Qué tamaño de posición tomamos
        
        Args:
            signal: Señal de trading a evaluar
            current_exposure: Exposición actual del portfolio (valor total de posiciones abiertas)
        
        Returns:
            OrderDecision con la decisión de aprobar/rechazar y el tamaño
        """
        # 1. Check if trading is enabled
        if not self.trading_enabled:
            return OrderDecision(
                approved=False,
                symbol=signal.symbol,
                side=signal.side,
                size=0.0,
                reason="Trading disabled - Max drawdown reached",
                risk_amount=0.0
            )
        
        # 2. Check drawdown limit
        current_dd = self.current_drawdown()
        if current_dd > self.max_drawdown:
            self.trading_enabled = False
            return OrderDecision(
                approved=False,
                symbol=signal.symbol,
                side=signal.side,
                size=0.0,
                reason=f"Max drawdown exceeded: {current_dd:.2%} > {self.max_drawdown:.2%}",
                risk_amount=0.0
            )
        
        # 3. Calculate risk amount
        risk_amount = self.equity * self.risk_per_trade
        
        # 4. Calculate stop distance
        stop_distance = signal.stop_distance
        
        if stop_distance <= 0:
            return OrderDecision(
                approved=False,
                symbol=signal.symbol,
                side=signal.side,
                size=0.0,
                reason=f"Invalid stop loss: distance = {stop_distance}",
                risk_amount=0.0
            )
        
        # 5. Calculate position size based on risk
        # Position Size = Risk Amount / Stop Distance
        position_size = risk_amount / stop_distance
        
        # 6. Calculate exposure of this position
        position_exposure = position_size * signal.entry
        
        # 7. Check exposure limit
        total_exposure = current_exposure + position_exposure
        max_allowed_exposure = self.equity * self.max_exposure
        
        if total_exposure > max_allowed_exposure:
            return OrderDecision(
                approved=False,
                symbol=signal.symbol,
                side=signal.side,
                size=0.0,
                reason=f"Exposure limit: {total_exposure:,.2f} > {max_allowed_exposure:,.2f}",
                risk_amount=0.0
            )
        
        # 8. Check minimum position size (avoid dust trades)
        min_position_value = 1000  # Mínimo $1000 por posición
        if position_exposure < min_position_value:
            return OrderDecision(
                approved=False,
                symbol=signal.symbol,
                side=signal.side,
                size=0.0,
                reason=f"Position too small: ${position_exposure:,.2f} < ${min_position_value:,.2f}",
                risk_amount=0.0
            )
        
        # 9. APPROVED - Log decision
        decision = OrderDecision(
            approved=True,
            symbol=signal.symbol,
            side=signal.side,
            size=position_size,
            reason="Approved",
            risk_amount=risk_amount,
            entry_price=signal.entry,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit
        )
        
        self.decisions_log.append({
            "timestamp": datetime.now(),
            "signal": signal.to_dict(),
            "decision": decision.to_dict(),
            "equity": self.equity,
            "drawdown": current_dd,
            "exposure": total_exposure
        })
        
        return decision
    
    def record_trade_result(self, profit: float):
        """
        Registra el resultado de un trade y ajusta el riesgo dinámicamente
        
        Args:
            profit: Ganancia/pérdida del trade
        """
        self.total_trades += 1
        
        if profit > 0:
            self.winning_trades += 1
            self.consecutive_losses = 0
            # Aumentar riesgo gradualmente tras wins
            self.risk_per_trade = min(
                self.risk_per_trade * 1.05,
                self.max_risk_per_trade
            )
        else:
            self.losing_trades += 1
            self.consecutive_losses += 1
            # Reducir riesgo tras losses
            if self.consecutive_losses >= 3:
                self.risk_per_trade = max(
                    self.risk_per_trade * 0.8,
                    self.min_risk_per_trade
                )
    
    def enable_trading(self):
        """Habilita el trading (usar con precaución)"""
        self.trading_enabled = True
    
    def disable_trading(self):
        """Deshabilita el trading (kill switch manual)"""
        self.trading_enabled = False
    
    def get_stats(self) -> Dict:
        """
        Retorna estadísticas del risk manager
        
        Returns:
            Diccionario con estadísticas
        """
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0.0
        
        return {
            "equity": self.equity,
            "initial_equity": self.initial_equity,
            "peak_equity": self.peak_equity,
            "current_drawdown": self.current_drawdown(),
            "max_drawdown_limit": self.max_drawdown,
            "trading_enabled": self.trading_enabled,
            "risk_per_trade": self.risk_per_trade,
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": win_rate,
            "consecutive_losses": self.consecutive_losses
        }
    
    def __str__(self) -> str:
        """Representación en string del risk manager"""
        stats = self.get_stats()
        return (
            f"ProfessionalRiskManager("
            f"equity=${stats['equity']:,.2f}, "
            f"dd={stats['current_drawdown']:.2%}, "
            f"risk={stats['risk_per_trade']:.2%}, "
            f"enabled={stats['trading_enabled']})"
        )
