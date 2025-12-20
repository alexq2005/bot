"""
Brokers integration package for automated trading.

This package provides integration with broker APIs for real-time trading.
"""

from .iol_client import IOLBrokerClient
from .iol_trading_bot import IOLTradingBot

__all__ = ['IOLBrokerClient', 'IOLTradingBot']
