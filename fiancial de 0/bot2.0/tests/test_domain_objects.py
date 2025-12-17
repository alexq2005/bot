"""
Tests for Domain Objects
Pruebas unitarias para Signal, OrderDecision y Order
"""

import pytest
from datetime import datetime
from src.domain.signal import Signal
from src.domain.decision import OrderDecision
from src.domain.order import Order, OrderStatus


class TestSignal:
    """Tests para Signal domain object"""
    
    def test_valid_buy_signal(self):
        """Test creación de señal BUY válida"""
        signal = Signal(
            symbol="GGAL",
            side="BUY",
            entry=100.0,
            stop_loss=95.0,
            take_profit=110.0,
            confidence=0.8,
            timestamp=datetime.now(),
            strategy_name="TestStrategy"
        )
        
        assert signal.symbol == "GGAL"
        assert signal.side == "BUY"
        assert signal.stop_distance == 5.0
        assert signal.profit_distance == 10.0
        assert signal.risk_reward_ratio == 2.0
    
    def test_valid_sell_signal(self):
        """Test creación de señal SELL válida"""
        signal = Signal(
            symbol="YPFD",
            side="SELL",
            entry=100.0,
            stop_loss=105.0,
            take_profit=90.0,
            confidence=0.7,
            timestamp=datetime.now()
        )
        
        assert signal.symbol == "YPFD"
        assert signal.side == "SELL"
        assert signal.stop_distance == 5.0
        assert signal.profit_distance == 10.0
    
    def test_invalid_confidence(self):
        """Test que confidence debe estar entre 0 y 1"""
        with pytest.raises(ValueError, match="Confidence debe estar entre"):
            Signal(
                symbol="GGAL",
                side="BUY",
                entry=100.0,
                stop_loss=95.0,
                take_profit=110.0,
                confidence=1.5,  # Inválido
                timestamp=datetime.now()
            )
    
    def test_invalid_buy_stop_loss(self):
        """Test que stop_loss debe ser < entry para BUY"""
        with pytest.raises(ValueError, match="stop_loss debe ser < entry"):
            Signal(
                symbol="GGAL",
                side="BUY",
                entry=100.0,
                stop_loss=105.0,  # Inválido para BUY
                take_profit=110.0,
                confidence=0.8,
                timestamp=datetime.now()
            )
    
    def test_invalid_sell_stop_loss(self):
        """Test que stop_loss debe ser > entry para SELL"""
        with pytest.raises(ValueError, match="stop_loss debe ser > entry"):
            Signal(
                symbol="GGAL",
                side="SELL",
                entry=100.0,
                stop_loss=95.0,  # Inválido para SELL
                take_profit=90.0,
                confidence=0.8,
                timestamp=datetime.now()
            )
    
    def test_signal_to_dict(self):
        """Test serialización a dict"""
        signal = Signal(
            symbol="GGAL",
            side="BUY",
            entry=100.0,
            stop_loss=95.0,
            take_profit=110.0,
            confidence=0.8,
            timestamp=datetime.now()
        )
        
        data = signal.to_dict()
        assert data["symbol"] == "GGAL"
        assert data["side"] == "BUY"
        assert data["risk_reward_ratio"] == 2.0


class TestOrderDecision:
    """Tests para OrderDecision domain object"""
    
    def test_approved_decision(self):
        """Test decisión aprobada"""
        decision = OrderDecision(
            approved=True,
            symbol="GGAL",
            side="BUY",
            size=100.0,
            reason="Approved",
            risk_amount=1000.0
        )
        
        assert decision.is_approved
        assert not decision.is_rejected
        assert decision.size == 100.0
    
    def test_rejected_decision(self):
        """Test decisión rechazada"""
        decision = OrderDecision(
            approved=False,
            symbol="GGAL",
            side="BUY",
            size=0.0,
            reason="Max drawdown reached",
            risk_amount=0.0
        )
        
        assert decision.is_rejected
        assert not decision.is_approved
        assert decision.size == 0.0
    
    def test_approved_with_zero_size_fails(self):
        """Test que decisión aprobada con size=0 falla"""
        with pytest.raises(ValueError, match="Decisión aprobada debe tener size > 0"):
            OrderDecision(
                approved=True,
                symbol="GGAL",
                side="BUY",
                size=0.0,  # Inválido
                reason="Approved"
            )
    
    def test_rejected_with_nonzero_size_fails(self):
        """Test que decisión rechazada con size>0 falla"""
        with pytest.raises(ValueError, match="Decisión rechazada debe tener size = 0"):
            OrderDecision(
                approved=False,
                symbol="GGAL",
                side="BUY",
                size=100.0,  # Inválido
                reason="Rejected"
            )


class TestOrder:
    """Tests para Order domain object"""
    
    def test_create_order(self):
        """Test creación de orden"""
        order = Order(
            id="ORD-001",
            symbol="GGAL",
            side="BUY",
            size=100.0,
            entry_price=100.0,
            timestamp=datetime.now()
        )
        
        assert order.id == "ORD-001"
        assert order.is_pending
        assert not order.is_filled
        assert order.fill_percentage == 0.0
    
    def test_update_fill(self):
        """Test actualización de ejecución"""
        order = Order(
            id="ORD-001",
            symbol="GGAL",
            side="BUY",
            size=100.0,
            entry_price=100.0,
            timestamp=datetime.now()
        )
        
        order.update_fill(filled_size=100.0, filled_price=100.5, commission=10.0)
        
        assert order.is_filled
        assert order.filled_size == 100.0
        assert order.filled_price == 100.5
        assert order.commission == 10.0
        assert order.fill_percentage == 100.0
    
    def test_partial_fill(self):
        """Test ejecución parcial"""
        order = Order(
            id="ORD-001",
            symbol="GGAL",
            side="BUY",
            size=100.0,
            entry_price=100.0,
            timestamp=datetime.now()
        )
        
        order.update_fill(filled_size=50.0, filled_price=100.5, commission=5.0)
        
        assert order.status == OrderStatus.PARTIALLY_FILLED
        assert order.fill_percentage == 50.0
    
    def test_cancel_order(self):
        """Test cancelación de orden"""
        order = Order(
            id="ORD-001",
            symbol="GGAL",
            side="BUY",
            size=100.0,
            entry_price=100.0,
            timestamp=datetime.now()
        )
        
        order.cancel()
        
        assert order.status == OrderStatus.CANCELLED
        assert not order.is_active


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
