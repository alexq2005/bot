import pandas_ta as ta
import logging
from typing import Dict, List
import pandas as pd

logger = logging.getLogger(__name__)

class RiskManager:
    """
    Institutional Grade Risk Management.
    Uses Volatility (ATR) to size positions and set dynamic stops.
    """

    def __init__(self, account_size: float = 100000.0, risk_per_trade: float = 0.02):
        self.account_size = account_size
        self.risk_per_trade = risk_per_trade # 2% risk per trade

    def calculate_position_size(self, symbol: str, price: float, atr: float, current_portfolio_value: float = 0.0) -> int:
        """
        Calculate position size based on volatility and portfolio constraints.
        Formula: (Account * Risk%) / (2 * ATR)

        Constraints:
        - Max 20% of account in one asset.
        - Ensure enough cash is available (implied).
        """
        if atr <= 0 or price <= 0:
            return 1 # Fallback

        risk_amount = self.account_size * self.risk_per_trade
        stop_distance = 2 * atr

        # Quantity = Risk $ / Risk per Share
        if stop_distance == 0:
            quantity = 1
        else:
            quantity = int(risk_amount / stop_distance)

        # Cap 1: Max 20% allocation per asset
        max_allocation = self.account_size * 0.20
        max_qty_by_alloc = int(max_allocation / price)

        quantity = min(quantity, max_qty_by_alloc)

        logger.info(f"⚖️ Risk Calc for {symbol}: ATR={atr:.2f} -> Qty={quantity} (Max Alloc Cap: {max_qty_by_alloc})")
        return max(1, quantity)

    def calculate_atr(self, data: List[Dict], period: int = 14) -> float:
        """Calculates the Average True Range (Volatilidad)"""
        if not data:
            return 0.0

        df = pd.DataFrame(data)
        if len(df) < period + 1:
            return 0.0

        df.ta.atr(length=period, append=True)
        return df.iloc[-1][f'ATR_{period}']
