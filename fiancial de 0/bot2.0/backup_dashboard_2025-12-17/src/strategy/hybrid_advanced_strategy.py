"""
Hybrid Advanced Strategy
Estrategia híbrida que integra TODAS las mejoras del sistema
"""

from typing import Dict, Optional
import numpy as np
import pandas as pd

# Importar todos los componentes
from ..ai.model_ensemble import ModelEnsemble
from ..ai.rl_agent import RLAgent
from ..ai.sac_agent import SACAgent
from ..ai.xgboost_model import XGBoostTradingModel
from ..ai.lstm_model import LSTMTradingModel
from ..ai.llm_reasoner import LLMReasoner
from ..analysis.signal_generator import SignalGenerator
from ..analysis.regime_detector import MarketRegimeDetector
from ..ai.sentiment_analyzer import SentimentAnalyzer
from ..alternative.alt_data_collector import AlternativeDataCollector


class HybridAdvancedStrategy:
    """
    Estrategia Híbrida Avanzada de 5 Capas
    
    Integra:
    1. Ensemble de 5 modelos ML
    2. Detección de régimen de mercado
    3. Datos alternativos (Google Trends, Twitter, Reddit)
    4. LLM Reasoning (GPT-4/Claude)
    5. Optimización continua
    """
    
    def __init__(
        self,
        enable_ensemble: bool = True,
        enable_regime_detection: bool = True,
        enable_alt_data: bool = True,
        enable_llm: bool = False,
        llm_api_key: str = "",
        google_trends_key: str = "",
        twitter_token: str = ""
    ):
        """
        Inicializa la estrategia híbrida avanzada
        
        Args:
            enable_ensemble: Activar ensemble de modelos
            enable_regime_detection: Activar detección de régimen
            enable_alt_data: Activar datos alternativos
            enable_llm: Activar LLM reasoning
            llm_api_key: API key para LLM
            google_trends_key: API key para Google Trends
            twitter_token: Token para Twitter
        """
        print("🚀 Inicializando Hybrid Advanced Strategy...")
        
        # Componentes base
        self.signal_generator = SignalGenerator()
        self.sentiment_analyzer = SentimentAnalyzer()
        
        # Ensemble de modelos ML
        self.enable_ensemble = enable_ensemble
        if enable_ensemble:
            self.ensemble = ModelEnsemble()
            self._setup_ensemble()
        
        # Detección de régimen
        self.enable_regime = enable_regime_detection
        if enable_regime_detection:
            self.regime_detector = MarketRegimeDetector()
        
        # Datos alternativos
        self.enable_alt_data = enable_alt_data
        if enable_alt_data:
            self.alt_data_collector = AlternativeDataCollector(
                google_trends_api_key=google_trends_key,
                twitter_bearer_token=twitter_token
            )
        
        # LLM Reasoning
        self.enable_llm = enable_llm
        if enable_llm and llm_api_key:
            self.llm_reasoner = LLMReasoner(api_key=llm_api_key)
        
        print("✓ Hybrid Advanced Strategy inicializada")
    
    def _setup_ensemble(self):
        """Configura el ensemble de modelos"""
        
        # Registrar modelos disponibles
        try:
            # PPO (ya existente)
            ppo_agent = RLAgent()
            self.ensemble.register_model('ppo', ppo_agent, initial_weight=0.25)
        except:
            print("⚠ PPO no disponible")
        
        try:
            # SAC
            sac_agent = SACAgent()
            self.ensemble.register_model('sac', sac_agent, initial_weight=0.25)
        except:
            print("⚠ SAC no disponible")
        
        try:
            # XGBoost
            xgb_model = XGBoostTradingModel()
            self.ensemble.register_model('xgboost', xgb_model, initial_weight=0.2)
        except:
            print("⚠ XGBoost no disponible")
        
        try:
            # LSTM
            lstm_model = LSTMTradingModel()
            self.ensemble.register_model('lstm', lstm_model, initial_weight=0.2)
        except:
            print("⚠ LSTM no disponible")
        
        # Ajustar pesos iniciales
        self.ensemble.adjust_weights(method='equal')
    
    def generate_signal(
        self,
        df: pd.DataFrame,
        symbol: str = "",
        news: list = None
    ) -> Dict:
        """
        Genera señal de trading usando el sistema híbrido completo
        
        Args:
            df: DataFrame con datos OHLCV
            symbol: Símbolo del activo
            news: Noticias recientes
        
        Returns:
            Dict con señal y detalles completos
        """
        # 1. ANÁLISIS TÉCNICO
        technical_signal = self.signal_generator.generate_signal(df)
        
        # 2. DETECCIÓN DE RÉGIMEN
        if self.enable_regime:
            regime_info = self.regime_detector.detect(df)
            regime_config = self.regime_detector.get_strategy_config(regime_info['regime'])
        else:
            regime_info = {'regime': 'sideways', 'confidence': 0.0}
            regime_config = {
                'risk_multiplier': 1.0,
                'weights': {
                    'technical': 0.3,
                    'rl': 0.3,
                    'sentiment': 0.2,
                    'alt_data': 0.2
                }
            }
        
        # 3. ENSEMBLE DE MODELOS ML
        if self.enable_ensemble:
            # Preparar estado para modelos
            state = self._prepare_state(df)
            ensemble_prediction = self.ensemble.predict(state)
        else:
            ensemble_prediction = {
                'action': 'HOLD',
                'confidence': 0.0,
                'votes': {}
            }
        
        # 4. ANÁLISIS DE SENTIMIENTO
        if news:
            sentiment_result = self.sentiment_analyzer.analyze_batch(news)
        else:
            sentiment_result = {'sentiment': 'neutral', 'score': 0.0, 'confidence': 0.0}
        
        # 5. DATOS ALTERNATIVOS
        if self.enable_alt_data and symbol:
            alt_data_signal = self.alt_data_collector.get_signal(symbol)
            alt_data_full = self.alt_data_collector.collect_all(symbol)
        else:
            alt_data_signal = {'action': 'HOLD', 'confidence': 0.0}
            alt_data_full = {}
        
        # 6. CONSENSO PONDERADO POR RÉGIMEN
        weights = regime_config['weights']
        
        final_signal = self._weighted_consensus(
            technical=technical_signal,
            ensemble=ensemble_prediction,
            sentiment=sentiment_result,
            alt_data=alt_data_signal,
            weights=weights
        )
        
        # 7. LLM REASONING (validación final)
        if self.enable_llm:
            market_data = {
                'price': df['close'].iloc[-1],
                'rsi': technical_signal['indicators'].get('rsi', 50),
                'macd': technical_signal['indicators'].get('macd', 0),
                'atr': technical_signal['indicators'].get('atr', 0)
            }
            
            signals = {
                'technical': technical_signal,
                'ensemble': ensemble_prediction,
                'sentiment': sentiment_result
            }
            
            llm_analysis = self.llm_reasoner.analyze_trading_decision(
                symbol=symbol,
                market_data=market_data,
                signals=signals,
                regime=regime_info,
                alt_data=alt_data_full
            )
            
            # LLM tiene veto/validación final
            if llm_analysis['available']:
                final_signal['action'] = llm_analysis['action']
                final_signal['confidence'] *= llm_analysis['confidence']
                final_signal['llm_reasoning'] = llm_analysis['reasoning']
        
        # Ajustar riesgo según régimen
        final_signal['risk_multiplier'] = regime_config['risk_multiplier']
        final_signal['regime'] = regime_info['regime']
        final_signal['regime_confidence'] = regime_info['confidence']
        
        return final_signal
    
    def _prepare_state(self, df: pd.DataFrame) -> np.ndarray:
        """Prepara estado para modelos ML"""
        
        latest = df.iloc[-1]
        
        # Calcular indicadores si no existen
        if 'rsi' not in df.columns:
            from ..analysis.technical_indicators import TechnicalIndicators
            df_with_indicators = TechnicalIndicators.calculate_all_indicators(df)
            latest = df_with_indicators.iloc[-1]
        
        state = np.array([
            latest.get('close', 0) / 10000,  # Normalizar precio
            latest.get('rsi', 50) / 100,
            latest.get('macd', 0) / 100,
            0.0,  # Sentimiento (placeholder)
            0.0,  # Posición actual (placeholder)
            1.0   # Cash disponible (placeholder)
        ])
        
        return state
    
    def _weighted_consensus(
        self,
        technical: Dict,
        ensemble: Dict,
        sentiment: Dict,
        alt_data: Dict,
        weights: Dict
    ) -> Dict:
        """Calcula consenso ponderado"""
        
        # Mapear señales a scores
        action_scores = {'BUY': 1, 'HOLD': 0, 'SELL': -1}
        
        # Technical
        tech_score = action_scores.get(technical['signal'], 0) * technical['confidence']
        
        # Ensemble
        ens_score = action_scores.get(ensemble['action'], 0) * ensemble['confidence']
        
        # Sentiment
        sent_map = {'positive': 1, 'neutral': 0, 'negative': -1}
        sent_score = sent_map.get(sentiment.get('sentiment', 'neutral'), 0) * sentiment.get('confidence', 0)
        
        # Alt Data
        alt_score = action_scores.get(alt_data['action'], 0) * alt_data['confidence']
        
        # Consenso ponderado
        weighted_score = (
            tech_score * weights['technical'] +
            ens_score * weights['rl'] +
            sent_score * weights['sentiment'] +
            alt_score * weights['alt_data']
        )
        
        # Mapear a acción
        if weighted_score > 0.3:
            action = 'BUY'
        elif weighted_score < -0.3:
            action = 'SELL'
        else:
            action = 'HOLD'
        
        confidence = abs(weighted_score)
        
        # Generar razonamiento
        reasoning_parts = []
        if weights['technical'] > 0:
            reasoning_parts.append(f"Técnico: {technical['signal']}")
        if weights['rl'] > 0:
            reasoning_parts.append(f"ML: {ensemble['action']}")
        if weights['sentiment'] > 0:
            reasoning_parts.append(f"Sentiment: {sentiment.get('sentiment', 'N/A')}")
        if weights['alt_data'] > 0:
            reasoning_parts.append(f"AltData: {alt_data['action']}")
        
        reasoning = " | ".join(reasoning_parts)
        
        return {
            'signal': action,
            'confidence': confidence,
            'strength': weighted_score,
            'reasoning': reasoning,
            'components': {
                'technical': technical,
                'ensemble': ensemble,
                'sentiment': sentiment,
                'alt_data': alt_data
            },
            'weights_used': weights
        }
