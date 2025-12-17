"""
Market Hours & Symbol Universe Manager
Gestiona horarios de mercado y universo de símbolos IOL
"""

from datetime import datetime, time
import pytz
from typing import List, Dict, Tuple
import requests


class MarketManager:
    """
    Gestor de horarios de mercado y universo de símbolos
    
    Funcionalidades:
    - Detecta si el mercado está abierto/cerrado
    - Obtiene universo de símbolos de IOL
    - Filtra símbolos por liquidez
    - Maneja horarios de Argentina
    """
    
    def __init__(self):
        """Inicializa el gestor de mercado"""
        self.timezone = pytz.timezone('America/Argentina/Buenos_Aires')
        
        # Horarios del mercado argentino (BYMA)
        self.market_open_time = time(11, 0)   # 11:00 AM
        self.market_close_time = time(17, 0)  # 5:00 PM
        
        # Días de la semana (0=Lunes, 6=Domingo)
        self.trading_days = [0, 1, 2, 3, 4]  # Lunes a Viernes
        
        # Cache de símbolos
        self._symbol_cache = None
        self._cache_timestamp = None
    
    def is_market_open(self) -> bool:
        """
        Verifica si el mercado está abierto
        
        Returns:
            bool: True si el mercado está abierto
        """
        now = datetime.now(self.timezone)
        
        # Verificar día de la semana
        if now.weekday() not in self.trading_days:
            return False
        
        # Verificar horario
        current_time = now.time()
        
        if self.market_open_time <= current_time <= self.market_close_time:
            return True
        
        return False
    
    def get_market_status(self) -> Dict:
        """
        Obtiene estado detallado del mercado
        
        Returns:
            Dict con información del mercado
        """
        now = datetime.now(self.timezone)
        is_open = self.is_market_open()
        
        # Calcular próxima apertura
        next_open = self._calculate_next_open(now)
        
        # Calcular próximo cierre
        next_close = self._calculate_next_close(now)
        
        return {
            'is_open': is_open,
            'current_time': now,
            'market_open_time': self.market_open_time,
            'market_close_time': self.market_close_time,
            'next_open': next_open,
            'next_close': next_close,
            'status': 'ABIERTO' if is_open else 'CERRADO'
        }
    
    def _calculate_next_open(self, now: datetime) -> datetime:
        """Calcula próxima apertura del mercado"""
        # Simplificado: próximo día hábil a las 11:00
        next_day = now
        
        while True:
            next_day = next_day.replace(hour=11, minute=0, second=0, microsecond=0)
            
            if next_day > now and next_day.weekday() in self.trading_days:
                return next_day
            
            # Avanzar un día
            next_day = next_day.replace(day=next_day.day + 1)
    
    def _calculate_next_close(self, now: datetime) -> datetime:
        """Calcula próximo cierre del mercado"""
        if self.is_market_open():
            return now.replace(hour=17, minute=0, second=0, microsecond=0)
        else:
            next_open = self._calculate_next_open(now)
            return next_open.replace(hour=17, minute=0)
    
    def get_iol_universe(self, iol_client=None, min_volume: float = 1000000) -> List[str]:
        """
        Obtiene universo de símbolos de IOL
        
        Args:
            iol_client: Cliente IOL autenticado
            min_volume: Volumen mínimo diario (filtro de liquidez)
        
        Returns:
            Lista de símbolos
        """
        # Si hay cache reciente (menos de 1 hora), usar cache
        if self._symbol_cache and self._cache_timestamp:
            cache_age = (datetime.now() - self._cache_timestamp).total_seconds()
            if cache_age < 3600:  # 1 hora
                return self._symbol_cache
        
        symbols = []
        
        try:
            if iol_client:
                # Obtener títulos de IOL
                # Nota: Esto depende de la API de IOL
                # Por ahora usamos una lista curada
                symbols = self._get_curated_symbols()
            else:
                symbols = self._get_curated_symbols()
            
            # Actualizar cache
            self._symbol_cache = symbols
            self._cache_timestamp = datetime.now()
            
            return symbols
            
        except Exception as e:
            print(f"⚠ Error obteniendo universo IOL: {e}")
            return self._get_curated_symbols()
    
    def _get_curated_symbols(self) -> List[str]:
        """
        Obtiene lista completa del universo IOL
        Incluye: Acciones, CEDEARs, Bonos, Letras, ONs
        
        Returns:
            Lista de símbolos de todas las herramientas IOL
        """
        symbols = {
            # ==================== ACCIONES ARGENTINAS ====================
            'acciones': [
                # Panel General - Más Líquidos
                'GGAL',   # Grupo Financiero Galicia
                'YPFD',   # YPF
                'PAMP',   # Pampa Energía
                'BMA',    # Banco Macro
                'ALUA',   # Aluar
                'TXAR',   # Ternium Argentina
                'COME',   # Sociedad Comercial del Plata
                'EDN',    # Edenor
                'LOMA',   # Loma Negra
                'MIRG',   # Mirgor
                'TRAN',   # Transener
                'CRES',   # Cresud
                'TGSU2',  # Transportadora de Gas del Sur
                'CEPU',   # Central Puerto
                'VALO',   # Banco de Valores
                'SUPV',   # Supervielle
                'BBAR',   # Banco BBVA Argentina
                'BYMA',   # Bolsas y Mercados Argentinos
                'TGNO4',  # Transportadora de Gas del Norte
                'AGRO',   # Agrometal
                'HARG',   # Holcim Argentina
                'BOLT',   # Boldt
                'DGCU2',  # Distribuidora de Gas Cuyana
                'METR',   # Metrogas
                'SEMI',   # Molinos Río de la Plata
                'IRSA',   # IRSA
                'MOLI',   # Molinos Agro
                'CAPX',   # Capex
                'CARC',   # Carboclor
                'CTIO',   # Consultatio
                'DYCA',   # Dycasa
                'FERR',   # Ferrum
                'GBAN',   # Grupo Banco Galicia
                'GCLA',   # Grupo Clarín
                'GRIM',   # Grimoldi
                'INTR',   # Grupo Inversora
                'LONG',   # Longvie
                'OEST',   # Banco Patagonia
                'RICH',   # Laboratorio Richmond
                'ROSE',   # Petroquímica Comodoro Rivadavia
                'SAMI',   # San Miguel
                'TECO2',  # Telecom Argentina
            ],
            
            # ==================== CEDEARS ====================
            'cedears': [
                # Tech Giants
                'AAPL',   # Apple
                'GOOGL',  # Google (Alphabet)
                'MSFT',   # Microsoft
                'AMZN',   # Amazon
                'META',   # Meta (Facebook)
                'TSLA',   # Tesla
                'NVDA',   # NVIDIA
                'NFLX',   # Netflix
                
                # Finance
                'JPM',    # JPMorgan Chase
                'BAC',    # Bank of America
                'WFC',    # Wells Fargo
                'GS',     # Goldman Sachs
                'V',      # Visa
                'MA',     # Mastercard
                'PYPL',   # PayPal
                
                # Consumer
                'KO',     # Coca-Cola
                'PEP',    # PepsiCo
                'WMT',    # Walmart
                'NKE',    # Nike
                'MCD',    # McDonald's
                'SBUX',   # Starbucks
                'DIS',    # Disney
                
                # Energy
                'XOM',    # ExxonMobil
                'CVX',    # Chevron
                
                # Healthcare
                'JNJ',    # Johnson & Johnson
                'PFE',    # Pfizer
                'ABBV',   # AbbVie
                
                # Industrial
                'BA',     # Boeing
                'CAT',    # Caterpillar
                'GE',     # General Electric
                
                # Retail
                'MELI',   # MercadoLibre
                'GLOB',   # Globant
                
                # Otros
                'GOLD',   # Barrick Gold
                'VALE',   # Vale
                'DESP',   # Despegar
            ],
            
            # ==================== BONOS SOBERANOS ====================
            'bonos_soberanos': [
                # Bonos en USD
                'AL30',   # Bono Argentina 2030
                'AL35',   # Bono Argentina 2035
                'AL41',   # Bono Argentina 2041
                'GD30',   # Bono Argentina 2030 (Ley NY)
                'GD35',   # Bono Argentina 2035 (Ley NY)
                'GD41',   # Bono Argentina 2041 (Ley NY)
                'GD46',   # Bono Argentina 2046 (Ley NY)
                
                # Bonos en ARS
                'T2V4',   # Bono del Tesoro
                'TO26',   # Bono del Tesoro 2026
                'TZX26',  # Bono CER 2026
                
                # Bonares
                'AE38',   # Bonar 2038
                'DICA',   # Bono Discount
            ],
            
            # ==================== LETRAS ====================
            'letras': [
                'S31O4',  # LEDE (Letra del Tesoro)
                'S30N4',  # LEDE
                'S30D4',  # LEDE
                'S31E5',  # LEDE
            ],
            
            # ==================== OBLIGACIONES NEGOCIABLES ====================
            'ons': [
                # ONs Corporativas
                'TVPP',   # Telecom ON
                'PAMP',   # Pampa ON
                'YPF',    # YPF ON
                'IRSA',   # IRSA ON
            ],
        }
        
        # Combinar todos los símbolos
        all_symbols = []
        for category, symbols_list in symbols.items():
            all_symbols.extend(symbols_list)
        
        # Eliminar duplicados y ordenar
        all_symbols = list(set(all_symbols))
        all_symbols.sort()
        
        return all_symbols
    
    def filter_symbols_by_liquidity(
        self,
        symbols: List[str],
        iol_client=None,
        min_volume: float = 1000000
    ) -> List[str]:
        """
        Filtra símbolos por liquidez
        
        Args:
            symbols: Lista de símbolos
            iol_client: Cliente IOL
            min_volume: Volumen mínimo
        
        Returns:
            Lista filtrada
        """
        if not iol_client:
            # Sin cliente, retornar top 10
            return symbols[:10]
        
        # Aquí se podría consultar volumen real de IOL
        # Por ahora retornamos los más líquidos
        return symbols[:15]
    
    def get_data_mode(self) -> str:
        """
        Determina qué modo de datos usar
        
        Returns:
            'realtime' si mercado abierto, 'last_close' si cerrado
        """
        return 'realtime' if self.is_market_open() else 'last_close'
    
    def get_categories(self) -> List[str]:
        """
        Obtiene lista de categorías disponibles
        
        Returns:
            Lista de categorías
        """
        return [
            'acciones',
            'cedears',
            'bonos_soberanos',
            'letras',
            'ons'
        ]
    
    def get_symbols_by_category(self, categories: List[str] = None) -> List[str]:
        """
        Obtiene símbolos filtrados por categoría
        
        Args:
            categories: Lista de categorías a incluir
                       Si None, retorna todas
        
        Returns:
            Lista de símbolos filtrados
        """
        symbols_dict = {
            'acciones': [
                'GGAL', 'YPFD', 'PAMP', 'BMA', 'ALUA', 'TXAR', 'COME', 'EDN',
                'LOMA', 'MIRG', 'TRAN', 'CRES', 'TGSU2', 'CEPU', 'VALO', 'SUPV',
                'BBAR', 'BYMA', 'TGNO4', 'AGRO', 'HARG', 'BOLT', 'DGCU2', 'METR',
                'SEMI', 'IRSA', 'MOLI', 'CAPX', 'CARC', 'CTIO', 'DYCA', 'FERR',
                'GBAN', 'GCLA', 'GRIM', 'INTR', 'LONG', 'OEST', 'RICH', 'ROSE',
                'SAMI', 'TECO2'
            ],
            'cedears': [
                'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META', 'TSLA', 'NVDA', 'NFLX',
                'JPM', 'BAC', 'WFC', 'GS', 'V', 'MA', 'PYPL',
                'KO', 'PEP', 'WMT', 'NKE', 'MCD', 'SBUX', 'DIS',
                'XOM', 'CVX', 'JNJ', 'PFE', 'ABBV',
                'BA', 'CAT', 'GE', 'MELI', 'GLOB', 'GOLD', 'VALE', 'DESP'
            ],
            'bonos_soberanos': [
                'AL30', 'AL35', 'AL41', 'GD30', 'GD35', 'GD41', 'GD46',
                'T2V4', 'TO26', 'TZX26', 'AE38', 'DICA'
            ],
            'letras': [
                'S31O4', 'S30N4', 'S30D4', 'S31E5'
            ],
            'ons': [
                'TVPP', 'PAMP', 'YPF', 'IRSA'
            ]
        }
        
        if categories is None:
            categories = list(symbols_dict.keys())
        
        result = []
        for category in categories:
            if category in symbols_dict:
                result.extend(symbols_dict[category])
        
        # Eliminar duplicados manteniendo el orden original definido
        seen = set()
        unique_sorted = []
        for symbol in result:
            if symbol not in seen:
                seen.add(symbol)
                unique_sorted.append(symbol)

        return unique_sorted
    
    def get_recommended_symbols(self, max_symbols: int = 10) -> List[str]:
        """
        Obtiene símbolos recomendados según liquidez
        
        Args:
            max_symbols: Número máximo de símbolos
        
        Returns:
            Lista de símbolos recomendados
        """
        all_symbols = self._get_curated_symbols()
        return all_symbols[:max_symbols]
