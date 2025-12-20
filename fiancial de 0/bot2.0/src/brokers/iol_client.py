"""
IOL Broker Client - Integration with IOL Invertir Online API.

This module provides a client to interact with the IOL broker API for
real-time market data, account information, and order execution.
"""

import os
import requests
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json


class IOLBrokerClient:
    """
    Client for IOL Invertir Online broker API.
    
    Provides methods to:
    - Authenticate with IOL API
    - Get real-time market data
    - Query account balance and positions
    - Execute buy/sell orders
    - Get order history
    """
    
    BASE_URL = "https://api.invertironline.com"
    
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize IOL Broker Client.
        
        Args:
            username: IOL username (if None, reads from env var IOL_USERNAME)
            password: IOL password (if None, reads from env var IOL_PASSWORD)
        """
        self.username = username or os.getenv('IOL_USERNAME')
        self.password = password or os.getenv('IOL_PASSWORD')
        self.access_token = None
        self.refresh_token = None
        self.logger = logging.getLogger(__name__)
        
        if not self.username or not self.password:
            raise ValueError("IOL credentials not provided. Set IOL_USERNAME and IOL_PASSWORD environment variables.")
    
    def authenticate(self) -> bool:
        """
        Authenticate with IOL API and obtain access token.
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            url = f"{self.BASE_URL}/token"
            data = {
                'username': self.username,
                'password': self.password,
                'grant_type': 'password'
            }
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            self.refresh_token = token_data.get('refresh_token')
            
            self.logger.info("Successfully authenticated with IOL API")
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Authentication failed: {e}")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authorization token."""
        if not self.access_token:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def get_account_balance(self) -> Dict:
        """
        Get account balance and available funds.
        
        Returns:
            dict: Account balance information
                - saldo_disponible: Available balance
                - saldo_total: Total balance
                - moneda: Currency
        """
        try:
            url = f"{self.BASE_URL}/api/v2/estadocuenta/balance"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            
            balance_data = response.json()
            self.logger.info(f"Retrieved account balance: {balance_data}")
            return balance_data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get account balance: {e}")
            return {}
    
    def get_positions(self) -> List[Dict]:
        """
        Get current portfolio positions.
        
        Returns:
            list: List of positions with symbol, quantity, price, etc.
        """
        try:
            url = f"{self.BASE_URL}/api/v2/portafolio/argentina"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            
            positions = response.json().get('activos', [])
            self.logger.info(f"Retrieved {len(positions)} positions")
            return positions
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get positions: {e}")
            return []
    
    def get_market_price(self, symbol: str, market: str = 'bCBA') -> Optional[Dict]:
        """
        Get real-time market price for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'GGAL', 'YPFD')
            market: Market identifier (default: 'bCBA' for BCBA)
        
        Returns:
            dict: Price information
                - ultimoPrecio: Last price
                - variacion: Price change
                - apertura: Opening price
                - maximo: High price
                - minimo: Low price
                - volumen: Volume
        """
        try:
            url = f"{self.BASE_URL}/api/v2/Cotizaciones/{symbol}/{market}/precios"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            
            price_data = response.json()
            self.logger.info(f"Retrieved price for {symbol}: {price_data.get('ultimoPrecio')}")
            return price_data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get price for {symbol}: {e}")
            return None
    
    def place_order(self, symbol: str, side: str, quantity: int, 
                   price: Optional[float] = None, order_type: str = 'market') -> Tuple[bool, Optional[Dict]]:
        """
        Place a buy or sell order.
        
        Args:
            symbol: Stock symbol (e.g., 'GGAL')
            side: 'buy' or 'sell'
            quantity: Number of shares
            price: Limit price (only for limit orders)
            order_type: 'market' or 'limit'
        
        Returns:
            tuple: (success: bool, order_data: dict or None)
        """
        try:
            url = f"{self.BASE_URL}/api/v2/operar/Comprar"
            
            # Map side to IOL format
            if side.lower() == 'sell':
                url = f"{self.BASE_URL}/api/v2/operar/Vender"
            
            # Prepare order data
            order_data = {
                'mercado': 'bCBA',
                'simbolo': symbol,
                'cantidad': quantity,
                'precio': price if order_type == 'limit' else None,
                'plazo': 't2',  # Settlement period
                'validez': datetime.now().strftime('%Y-%m-%d')
            }
            
            # Remove None values
            order_data = {k: v for k, v in order_data.items() if v is not None}
            
            self.logger.info(f"Placing {side} order: {symbol} x {quantity}")
            
            response = requests.post(url, headers=self._get_headers(), json=order_data)
            response.raise_for_status()
            
            result = response.json()
            self.logger.info(f"Order placed successfully: {result}")
            
            return True, result
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to place order: {e}")
            return False, None
    
    def get_order_status(self, order_id: str) -> Optional[Dict]:
        """
        Get status of a specific order.
        
        Args:
            order_id: Order identifier
        
        Returns:
            dict: Order status information
        """
        try:
            url = f"{self.BASE_URL}/api/v2/operaciones/{order_id}"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            
            order_status = response.json()
            self.logger.info(f"Order {order_id} status: {order_status.get('estado')}")
            return order_status
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get order status: {e}")
            return None
    
    def get_order_history(self, days: int = 30) -> List[Dict]:
        """
        Get order history for the last N days.
        
        Args:
            days: Number of days to look back (default: 30)
        
        Returns:
            list: List of historical orders
        """
        try:
            url = f"{self.BASE_URL}/api/v2/operaciones"
            params = {
                'dias': days
            }
            
            response = requests.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            
            orders = response.json()
            self.logger.info(f"Retrieved {len(orders)} historical orders")
            return orders
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get order history: {e}")
            return []
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel a pending order.
        
        Args:
            order_id: Order identifier to cancel
        
        Returns:
            bool: True if cancellation successful
        """
        try:
            url = f"{self.BASE_URL}/api/v2/operaciones/{order_id}"
            response = requests.delete(url, headers=self._get_headers())
            response.raise_for_status()
            
            self.logger.info(f"Order {order_id} cancelled successfully")
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to cancel order {order_id}: {e}")
            return False
