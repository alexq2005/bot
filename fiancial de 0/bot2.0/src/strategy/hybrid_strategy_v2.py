"""
Hybrid Strategy - Migrated to BaseStrategy
Estrategia híbrida que combina análisis técnico, RL y sentimiento

MIGRADO A NUEVA ARQUITECTURA:
- Hereda de BaseStrategy
- Retorna Signal en lugar de dict
- Usa objetos de dominio
"""

import pandas as pd
from typing import Optional
from datetime import datetime

from .base import BaseStrategy
from ..domain.signal import Signal
from ..analysis.signal_generator import SignalGenerator
from ..ai.sentiment_analyzer import SentimentAnalyzer
from ..ai.news_aggregator import NewsAggregator


class HybridStrategyV2(BaseStrategy):
    """
    Estrategia híbrida de consenso (v2.0 - Migrada)
    
    Combina:
    1. Análisis Técnico (RSI, MACD, Bollinger Bands)
    2. Agente de Reinforcement Learning (PPO)
    3. Análisis de Sentimiento (FinBERT)
    
    Usa sistema de votación ponderada para consenso.
    """
    
    def __init__(
        self,
        signal_generator: SignalGenerator,
        sentiment_analyzer: Optional[SentimentAnalyzer] = None,
        news_aggregator: Optional[NewsAggregator] = None,
        use_sentiment: bool = True,
        sentiment_threshold: float = 0.3,
        consensus_threshold: float = 0.6,
        default_stop_pct: float = 0.03,  # 3% stop loss
        default_target_pct: float = 0.06  # 6% take profit
    ):
        """
        Inicializa la estrategia híbrida
        
        Args:
            signal_generator: Generador de señales técnicas
            sentiment_analyzer: Analizador de sentimiento (opcional)
            news_aggregator: Agregador de noticias (opcional)
            use_sentiment: Si usar análisis de sentimiento
            sentiment_threshold: Umbral para considerar sentimiento
            consensus_threshold: Umbral mínimo de consenso (0.6 = 60%)
            default_stop_pct: Porcentaje de stop loss por defecto
            default_target_pct: Porcentaje de take profit por defecto
        """
        super().__init__(name="Hybrid Strategy V2")
        
        self.signal_generator = signal_generator
        self.sentiment_analyzer = sentiment_analyzer
        self.news_aggregator = news_aggregator
        self.use_sentiment = use_sentiment
        self.sentiment_threshold = sentiment_threshold
        self.consensus_threshold = consensus_threshold
        self.default_stop_pct = default_stop_pct
        self.default_target_pct = default_target_pct
    
    def generate_signal(self, market_data: pd.DataFrame) -> Optional[Signal]:
        """
        Genera señal de trading basada en consenso híbrido
        
        Args:
            market_data: DataFrame con datos OHLCV e indicadores
        
        Returns:
            Signal si hay consenso, None si no hay señal clara
        """
        # Validar datos
        if not self.validate_market_data(market_data):
            return None
        
        if len(market_data) < 2:
            return None
        
        # Obtener símbolo y precio actual
        current = market_data.iloc[-1]
        symbol = current.get('symbol', 'UNKNOWN')
        price = current['close']
        
        # 1. Señal Técnica
        technical_signal = self.signal_generator.generate_signal(market_data)
        
        # 2. Señal de Sentimiento
        sentiment_data = self._get_sentiment_score(symbol)
        
        # 3. Sistema de votación
        decision = self._calculate_consensus(
            technical_signal,
            sentiment_data,
            rl_prediction=None  # Por ahora sin RL
        )
        
        # Si no hay consenso o es HOLD, no generar señal
        if decision['signal'] == 'HOLD':
            return None
        
        # Verificar umbral de consenso
        if decision['consensus_pct'] < self.consensus_threshold:
            return None
        
        # Calcular stop loss y take profit
        if decision['signal'] == 'BUY':
            stop_loss = price * (1 - self.default_stop_pct)
            take_profit = price * (1 + self.default_target_pct)
        else:  # SELL
            stop_loss = price * (1 + self.default_stop_pct)
            take_profit = price * (1 - self.default_target_pct)
        
        # Crear Signal
        signal = Signal(
            symbol=symbol,
            side=decision['signal'],
            entry=price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            confidence=decision['confidence'],
            timestamp=datetime.now(),
            strategy_name=self.name
        )
        
        return signal
    
    def _get_sentiment_score(self, symbol: str) -> dict:
        """
        Obtiene el score de sentimiento para un símbolo
        
        Args:
            symbol: Símbolo del activo
        
        Returns:
            Dict con: score, signal, confidence, news_count
        """
        if not self.use_sentiment or not self.sentiment_analyzer:
            return {
                'score': 0.0,
                'signal': 'NEUTRAL',
                'confidence': 0.0,
                'news_count': 0
            }
        
        try:
            # Obtener noticias
            if self.news_aggregator:
                news = self.news_aggregator.get_news(symbol, max_results=10)
            else:
                news = []
            
            if not news:
                return {
                    'score': 0.0,
                    'signal': 'NEUTRAL',
                    'confidence': 0.0,
                    'news_count': 0
                }
            
            # Analizar sentimiento
            sentiments = []
            for article in news:
                text = f"{article.get('title', '')} {article.get('description', '')}"
                sentiment = self.sentiment_analyzer.analyze(text)
                sentiments.append(sentiment['score'])
            
            # Calcular score promedio
            avg_score = sum(sentiments) / len(sentiments) if sentiments else 0.0
            
            # Determinar señal
            if avg_score > self.sentiment_threshold:
                signal = 'POSITIVE'
                confidence = min(abs(avg_score), 1.0)
            elif avg_score < -self.sentiment_threshold:
                signal = 'NEGATIVE'
                confidence = min(abs(avg_score), 1.0)
            else:
                signal = 'NEUTRAL'
                confidence = 0.3
            
            return {
                'score': avg_score,
                'signal': signal,
                'confidence': confidence,
                'news_count': len(news)
            }
            
        except Exception as e:
            print(f"Error obteniendo sentimiento para {symbol}: {e}")
            return {
                'score': 0.0,
                'signal': 'NEUTRAL',
                'confidence': 0.0,
                'news_count': 0
            }
    
    def _calculate_consensus(
        self,
        technical_signal: dict,
        sentiment_data: dict,
        rl_prediction: Optional[str] = None
    ) -> dict:
        """
        Calcula consenso entre componentes
        
        Args:
            technical_signal: Señal técnica
            sentiment_data: Datos de sentimiento
            rl_prediction: Predicción RL (opcional)
        
        Returns:
            Dict con signal, confidence, consensus_pct
        """
        # Sistema de votación
        votes = {"BUY": 0, "SELL": 0, "HOLD": 0}
        weights = {"BUY": 0, "SELL": 0, "HOLD": 0}
        
        # Voto técnico (peso: 1.0)
        tech_signal = technical_signal.get("signal", "HOLD")
        votes[tech_signal] += 1
        weights[tech_signal] += technical_signal.get("confidence", 0.5)
        
        # Voto de RL (peso: 1.0)
        if rl_prediction:
            votes[rl_prediction] += 1
            weights[rl_prediction] += 0.8
        
        # Voto de sentimiento (peso: 0.5)
        if self.use_sentiment:
            if sentiment_data["signal"] == "POSITIVE":
                votes["BUY"] += 0.5
                weights["BUY"] += sentiment_data["confidence"] * 0.5
            elif sentiment_data["signal"] == "NEGATIVE":
                votes["SELL"] += 0.5
                weights["SELL"] += sentiment_data["confidence"] * 0.5
            else:
                votes["HOLD"] += 0.5
                weights["HOLD"] += 0.3
        
        # Calcular total de votos
        total_votes = sum(votes.values())
        
        # Determinar señal ganadora
        max_votes = max(votes.values())
        winning_signals = [sig for sig, v in votes.items() if v == max_votes]
        
        # Si hay empate, usar HOLD
        if len(winning_signals) > 1:
            final_signal = "HOLD"
            consensus_pct = 0.0
            final_confidence = 0.0
        else:
            final_signal = winning_signals[0]
            consensus_pct = votes[final_signal] / total_votes if total_votes > 0 else 0
            final_confidence = weights[final_signal] / votes[final_signal] if votes[final_signal] > 0 else 0
        
        return {
            'signal': final_signal,
            'confidence': final_confidence,
            'consensus_pct': consensus_pct,
            'votes': votes
        }
    
    def get_required_indicators(self) -> list:
        """
        Retorna indicadores requeridos
        
        Returns:
            Lista de indicadores necesarios
        """
        return [
            'rsi_14',
            'macd',
            'macd_signal',
            'bb_upper',
            'bb_middle',
            'bb_lower',
            'sma_50',
            'sma_200',
            'volume'
        ]
