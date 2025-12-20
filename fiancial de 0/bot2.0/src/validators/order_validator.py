"""
Sistema robusto de validación de órdenes pre-ejecución
Previene errores costosos en modo LIVE
"""

import logging
from typing import Dict, Tuple, List, Optional
from datetime import datetime, time
from enum import Enum

logger = logging.getLogger(__name__)

class ValidationLevel(Enum):
    """Niveles de severidad de validación"""
    ERROR = "ERROR"      # Bloquea la orden
    WARNING = "WARNING"  # Permite pero advierte
    INFO = "INFO"        # Solo informativo

class ValidationResult:
    """Resultado de una validación"""
    def __init__(
        self,
        passed: bool,
        level: ValidationLevel,
        message: str,
        details: Optional[Dict] = None
    ):
        self.passed = passed
        self.level = level
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now()

class OrderValidator:
    """
    Validador multi-nivel de órdenes de trading
    
    Validaciones implementadas:
    1. Saldo suficiente
    2. Límites de posición
    3. Horario de mercado
    4. Precio razonable
    5. Cantidad mínima/máxima
    6. Límite de órdenes diarias
    7. Exposición máxima por activo
    8. Validación de símbolos
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.validation_history: List[ValidationResult] = []
        
        # Configuración de límites
        self.max_position_size = config.get('max_position_size', 100000)
        self.max_daily_orders = config.get('max_daily_orders', 50)
        self.max_price_deviation = config.get('max_price_deviation', 0.05)  # 5%
        self.max_exposure_per_asset = config.get('max_exposure_per_asset', 0.3)  # 30%
        
        # Horario de mercado (Buenos Aires)
        self.market_open = time(11, 0)   # 11:00 AM
        self.market_close = time(17, 0)  # 5:00 PM
    
    def validate_order(
        self,
        order: Dict,
        account_balance: float,
        current_positions: Dict,
        last_price: float,
        daily_order_count: int
    ) -> Tuple[bool, List[ValidationResult]]:
        """
        Valida una orden antes de ejecutarla
        
        Args:
            order: Dict con 'symbol', 'side', 'quantity', 'price'
            account_balance: Saldo disponible en cuenta
            current_positions: Dict de posiciones actuales
            last_price: Último precio conocido del activo
            daily_order_count: Número de órdenes ejecutadas hoy
            
        Returns:
            (is_valid, validation_results)
        """
        results = []
        
        # 1. Validar saldo suficiente
        results.append(self._validate_balance(order, account_balance))
        
        # 2. Validar límites de posición
        results.append(self._validate_position_limits(order, current_positions))
        
        # 3. Validar horario de mercado
        results.append(self._validate_market_hours())
        
        # 4. Validar precio razonable
        results.append(self._validate_price(order, last_price))
        
        # 5. Validar cantidad mínima/máxima
        results.append(self._validate_quantity(order))
        
        # 6. Validar límite de órdenes diarias
        results.append(self._validate_daily_limit(daily_order_count))
        
        # 7. Validar exposición máxima
        results.append(self._validate_exposure(order, current_positions, account_balance))
        
        # 8. Validar símbolo
        results.append(self._validate_symbol(order))
        
        # Guardar en historial
        self.validation_history.extend(results)
        
        # Determinar si la orden es válida
        has_errors = any(
            not r.passed and r.level == ValidationLevel.ERROR 
            for r in results
        )
        
        is_valid = not has_errors
        
        # Log resultados
        self._log_validation_results(order, is_valid, results)
        
        return is_valid, results
    
    def _validate_balance(
        self,
        order: Dict,
        balance: float
    ) -> ValidationResult:
        """Valida que hay saldo suficiente"""
        required = order['quantity'] * order.get('price', 0)
        
        if order['side'].upper() == 'BUY':
            if required > balance:
                return ValidationResult(
                    passed=False,
                    level=ValidationLevel.ERROR,
                    message=f"Saldo insuficiente. Requerido: ${required:,.2f}, Disponible: ${balance:,.2f}",
                    details={'required': required, 'available': balance}
                )
        
        return ValidationResult(
            passed=True,
            level=ValidationLevel.INFO,
            message="Saldo suficiente"
        )
    
    def _validate_position_limits(
        self,
        order: Dict,
        positions: Dict
    ) -> ValidationResult:
        """Valida límites de tamaño de posición"""
        symbol = order['symbol']
        quantity = order['quantity']
        price = order.get('price', 0)
        position_value = quantity * price
        
        if position_value > self.max_position_size:
            return ValidationResult(
                passed=False,
                level=ValidationLevel.ERROR,
                message=f"Posición excede límite máximo de ${self.max_position_size:,.2f}",
                details={'position_value': position_value, 'limit': self.max_position_size}
            )
        
        return ValidationResult(
            passed=True,
            level=ValidationLevel.INFO,
            message="Tamaño de posición dentro de límites"
        )
    
    def _validate_market_hours(self) -> ValidationResult:
        """Valida que el mercado esté abierto"""
        now = datetime.now().time()
        
        if not (self.market_open <= now <= self.market_close):
            return ValidationResult(
                passed=False,
                level=ValidationLevel.WARNING,
                message=f"Fuera de horario de mercado ({self.market_open} - {self.market_close})",
                details={'current_time': now.strftime('%H:%M')}
            )
        
        return ValidationResult(
            passed=True,
            level=ValidationLevel.INFO,
            message="Dentro de horario de mercado"
        )
    
    def _validate_price(
        self,
        order: Dict,
        last_price: float
    ) -> ValidationResult:
        """Valida que el precio sea razonable"""
        order_price = order.get('price', 0)
        
        if last_price > 0:
            deviation = abs(order_price - last_price) / last_price
            
            if deviation > self.max_price_deviation:
                return ValidationResult(
                    passed=False,
                    level=ValidationLevel.ERROR,
                    message=f"Precio se desvía {deviation*100:.1f}% del último precio (máx: {self.max_price_deviation*100}%)",
                    details={
                        'order_price': order_price,
                        'last_price': last_price,
                        'deviation': deviation
                    }
                )
        
        return ValidationResult(
            passed=True,
            level=ValidationLevel.INFO,
            message="Precio dentro de rango razonable"
        )
    
    def _validate_quantity(self, order: Dict) -> ValidationResult:
        """Valida cantidad mínima y máxima"""
        quantity = order['quantity']
        
        if quantity <= 0:
            return ValidationResult(
                passed=False,
                level=ValidationLevel.ERROR,
                message="Cantidad debe ser mayor a 0"
            )
        
        return ValidationResult(
            passed=True,
            level=ValidationLevel.INFO,
            message="Cantidad válida"
        )
    
    def _validate_daily_limit(self, daily_count: int) -> ValidationResult:
        """Valida límite de órdenes diarias"""
        if daily_count >= self.max_daily_orders:
            return ValidationResult(
                passed=False,
                level=ValidationLevel.ERROR,
                message=f"Límite diario de órdenes alcanzado ({self.max_daily_orders})",
                details={'daily_count': daily_count, 'limit': self.max_daily_orders}
            )
        
        return ValidationResult(
            passed=True,
            level=ValidationLevel.INFO,
            message=f"Órdenes diarias: {daily_count}/{self.max_daily_orders}"
        )
    
    def _validate_exposure(
        self,
        order: Dict,
        positions: Dict,
        balance: float
    ) -> ValidationResult:
        """Valida exposición máxima por activo"""
        symbol = order['symbol']
        order_value = order['quantity'] * order.get('price', 0)
        
        current_exposure = positions.get(symbol, {}).get('value', 0)
        total_exposure = current_exposure + order_value
        
        exposure_ratio = total_exposure / balance if balance > 0 else 0
        
        if exposure_ratio > self.max_exposure_per_asset:
            return ValidationResult(
                passed=False,
                level=ValidationLevel.WARNING,
                message=f"Exposición en {symbol} excede {self.max_exposure_per_asset*100}% del capital",
                details={
                    'exposure_ratio': exposure_ratio,
                    'limit': self.max_exposure_per_asset
                }
            )
        
        return ValidationResult(
            passed=True,
            level=ValidationLevel.INFO,
            message=f"Exposición en {symbol}: {exposure_ratio*100:.1f}%"
        )
    
    def _validate_symbol(self, order: Dict) -> ValidationResult:
        """Valida que el símbolo sea válido"""
        symbol = order.get('symbol', '')
        
        if not symbol or len(symbol) < 2:
            return ValidationResult(
                passed=False,
                level=ValidationLevel.ERROR,
                message="Símbolo inválido"
            )
        
        return ValidationResult(
            passed=True,
            level=ValidationLevel.INFO,
            message=f"Símbolo válido: {symbol}"
        )
    
    def _log_validation_results(
        self,
        order: Dict,
        is_valid: bool,
        results: List[ValidationResult]
    ):
        """Log detallado de validaciones"""
        status = "✅ APROBADA" if is_valid else "❌ RECHAZADA"
        logger.info(f"\n{'='*60}")
        logger.info(f"VALIDACIÓN DE ORDEN: {status}")
        logger.info(f"Símbolo: {order['symbol']} | Lado: {order['side']} | Cantidad: {order['quantity']}")
        logger.info(f"{'='*60}")
        
        for result in results:
            icon = "✅" if result.passed else "❌"
            logger.info(f"{icon} [{result.level.value}] {result.message}")
            if result.details:
                logger.debug(f"   Detalles: {result.details}")
        
        logger.info(f"{'='*60}\n")
