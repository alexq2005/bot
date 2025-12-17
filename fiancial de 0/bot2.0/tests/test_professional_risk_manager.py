"""
Tests for Professional Risk Manager
Pruebas críticas para el componente más importante del sistema
"""

import pytest
from datetime import datetime
from src.risk.professional_risk_manager import ProfessionalRiskManager
from src.domain.signal import Signal


class TestProfessionalRiskManager:
    """Tests para ProfessionalRiskManager"""
    
    def test_initialization(self):
        """Test inicialización correcta"""
        rm = ProfessionalRiskManager(
            initial_equity=100000.0,
            risk_per_trade=0.01,
            max_drawdown=0.15
        )
        
        assert rm.equity == 100000.0
        assert rm.peak_equity == 100000.0
        assert rm.trading_enabled
        assert rm.current_drawdown() == 0.0
    
    def test_approve_valid_signal(self):
        """Test aprobación de señal válida"""
        rm = ProfessionalRiskManager(initial_equity=100000.0)
        
        signal = Signal(
            symbol="GGAL",
            side="BUY",
            entry=100.0,
            stop_loss=95.0,  # 5% stop
            take_profit=110.0,
            confidence=0.8,
            timestamp=datetime.now()
        )
        
        decision = rm.evaluate(signal, current_exposure=0.0)
        
        assert decision.approved
        assert decision.size > 0
        assert decision.risk_amount == 1000.0  # 1% of 100k
    
    def test_reject_on_max_drawdown(self):
        """Test rechazo cuando se alcanza max drawdown"""
        rm = ProfessionalRiskManager(
            initial_equity=100000.0,
            max_drawdown=0.15
        )
        
        # Simular pérdida del 16%
        rm.update_equity(84000.0)
        
        signal = Signal(
            symbol="GGAL",
            side="BUY",
            entry=100.0,
            stop_loss=95.0,
            take_profit=110.0,
            confidence=0.8,
            timestamp=datetime.now()
        )
        
        decision = rm.evaluate(signal)
        
        assert not decision.approved
        assert "drawdown" in decision.reason.lower()
        assert not rm.trading_enabled  # Kill switch activado
    
    def test_reject_on_exposure_limit(self):
        """Test rechazo cuando se excede límite de exposición"""
        rm = ProfessionalRiskManager(
            initial_equity=100000.0,
            max_exposure=0.30  # 30% máximo
        )
        
        signal = Signal(
            symbol="GGAL",
            side="BUY",
            entry=100.0,
            stop_loss=95.0,
            take_profit=110.0,
            confidence=0.8,
            timestamp=datetime.now()
        )
        
        # Ya tenemos 35k de exposición (35%)
        decision = rm.evaluate(signal, current_exposure=35000.0)
        
        assert not decision.approved
        assert "exposure" in decision.reason.lower()
    
    def test_reject_tiny_stop_distance(self):
        """Test rechazo de señal con stop distance muy pequeño que genera posición excesiva"""
        rm = ProfessionalRiskManager(initial_equity=100000.0)
        
        # Crear señal con stop muy cercano al entry
        # Stop distance = 0.01 resulta en position size = 1000 / 0.01 = 100,000 acciones
        # Exposure = 100,000 * 100 = 10,000,000 (excede límite de 30% = 30,000)
        signal = Signal(
            symbol="GGAL",
            side="BUY",
            entry=100.0,
            stop_loss=99.99,  # Stop distance = 0.01 (muy pequeño)
            take_profit=110.0,
            confidence=0.8,
            timestamp=datetime.now()
        )
        
        decision = rm.evaluate(signal)
        
        # El risk manager debe RECHAZAR esto por exceso de exposición
        # Esto es CORRECTO - protege contra posiciones demasiado grandes
        assert not decision.approved
        assert "exposure" in decision.reason.lower() or "limit" in decision.reason.lower()
    
    def test_position_sizing_calculation(self):
        """Test cálculo correcto de tamaño de posición"""
        rm = ProfessionalRiskManager(
            initial_equity=100000.0,
            risk_per_trade=0.01  # 1%
        )
        
        signal = Signal(
            symbol="GGAL",
            side="BUY",
            entry=100.0,
            stop_loss=95.0,  # 5 puntos de stop
            take_profit=110.0,
            confidence=0.8,
            timestamp=datetime.now()
        )
        
        decision = rm.evaluate(signal)
        
        # Risk amount = 100k * 0.01 = 1000
        # Stop distance = 5
        # Position size = 1000 / 5 = 200 acciones
        assert decision.size == 200.0
        assert decision.risk_amount == 1000.0
    
    def test_dynamic_risk_adjustment_after_losses(self):
        """Test ajuste dinámico de riesgo tras pérdidas"""
        rm = ProfessionalRiskManager(
            initial_equity=100000.0,
            risk_per_trade=0.01
        )
        
        initial_risk = rm.risk_per_trade
        
        # Registrar 3 pérdidas consecutivas
        rm.record_trade_result(-500)
        rm.record_trade_result(-500)
        rm.record_trade_result(-500)
        
        # El riesgo debe haberse reducido
        assert rm.risk_per_trade < initial_risk
        assert rm.consecutive_losses == 3
    
    def test_dynamic_risk_adjustment_after_wins(self):
        """Test ajuste dinámico de riesgo tras ganancias"""
        rm = ProfessionalRiskManager(
            initial_equity=100000.0,
            risk_per_trade=0.01
        )
        
        initial_risk = rm.risk_per_trade
        
        # Registrar ganancias
        rm.record_trade_result(500)
        rm.record_trade_result(500)
        
        # El riesgo debe haberse incrementado (pero sin exceder el máximo)
        assert rm.risk_per_trade >= initial_risk
        assert rm.consecutive_losses == 0
    
    def test_kill_switch_manual(self):
        """Test kill switch manual"""
        rm = ProfessionalRiskManager(initial_equity=100000.0)
        
        assert rm.trading_enabled
        
        rm.disable_trading()
        assert not rm.trading_enabled
        
        rm.enable_trading()
        assert rm.trading_enabled
    
    def test_get_stats(self):
        """Test obtención de estadísticas"""
        rm = ProfessionalRiskManager(initial_equity=100000.0)
        
        rm.record_trade_result(500)
        rm.record_trade_result(-300)
        
        stats = rm.get_stats()
        
        assert stats["total_trades"] == 2
        assert stats["winning_trades"] == 1
        assert stats["losing_trades"] == 1
        assert stats["win_rate"] == 50.0
    
    def test_equity_tracking(self):
        """Test tracking de equity"""
        rm = ProfessionalRiskManager(initial_equity=100000.0)
        
        rm.update_equity(105000.0)
        rm.update_equity(103000.0)
        
        assert rm.equity == 103000.0
        assert rm.peak_equity == 105000.0
        assert len(rm.equity_history) == 3  # Initial + 2 updates


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
