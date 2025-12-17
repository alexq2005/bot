"""
Hybrid Strategy
Estrategia de consenso híbrido: Technical + RL + Sentiment
"""

import pandas as pd
from typing import Dict, Optional
from ..analysis.signal_generator import SignalGenerator
from ..ai.sentiment_analyzer import SentimentAnalyzer
from ..ai.news_aggregator import NewsAggregator


class HybridStrategy:
    """
    Estrategia híbrida de consenso
    
    Combina:
    1. Análisis Técnico (RSI, MACD, Bollinger Bands)
    2. Agente de Reinforcement Learning (PPO)
    3. Análisis de Sentimiento (FinBERT)
    
    Requiere alineación de múltiples fuentes para generar señal
    """
    
    def __init__(
        self,
        signal_generator: SignalGenerator,
        sentiment_analyzer: Optional[SentimentAnalyzer] = None,
        news_aggregator: Optional[NewsAggregator] = None,
        use_sentiment: bool = True,
        sentiment_threshold: float = 0.3,
        consensus_threshold: float = 0.6
    ):
        """
        Inicializa la estrategia híbrida
        
        Args:
            signal_generator: Generador de señales técnicas
            sentiment_analyzer: Analizador de sentimiento (opcional)
            news_aggregator: Agregador de noticias (opcional)
            use_sentiment: Usar análisis de sentimiento
            sentiment_threshold: Umbral de sentimiento para confirmación (0.3 = 30%)
            consensus_threshold: Umbral de consenso requerido (0.6 = 60%)
        """
        self.signal_generator = signal_generator
        self.sentiment_analyzer = sentiment_analyzer
        self.news_aggregator = news_aggregator
        self.use_sentiment = use_sentiment
        self.sentiment_threshold = sentiment_threshold
        self.consensus_threshold = consensus_threshold
    
    def get_sentiment_score(self, symbol: str) -> Dict:
        """
        Obtiene el score de sentimiento para un símbolo
        
        Args:
            symbol: Símbolo del activo
        
        Returns:
            Dict con: score, signal, confidence
        """
        if not self.use_sentiment or not self.sentiment_analyzer or not self.news_aggregator:
            return {
                "score": 0.0,
                "signal": "NEUTRAL",
                "confidence": 0.0,
                "news_count": 0
            }
        
        # Obtener noticias
        news = self.news_aggregator.get_all_news(symbol)
        
        if not news:
            return {
                "score": 0.0,
                "signal": "NEUTRAL",
                "confidence": 0.0,
                "news_count": 0
            }
        
        # Analizar sentimiento de los titulares
        headlines = [n['headline'] for n in news[:10]]  # Top 10 noticias
        sentiments = self.sentiment_analyzer.analyze_batch(headlines)
        
        # Agregar sentimientos
        avg_score = self.sentiment_analyzer.aggregate_sentiment(sentiments)
        avg_confidence = sum(s['confidence'] for s in sentiments) / len(sentiments)
        
        # Determinar señal
        if avg_score > self.sentiment_threshold:
            signal = "POSITIVE"
        elif avg_score < -self.sentiment_threshold:
            signal = "NEGATIVE"
        else:
            signal = "NEUTRAL"
        
        return {
            "score": avg_score,
            "signal": signal,
            "confidence": avg_confidence,
            "news_count": len(news)
        }
    
    def generate_decision(
        self,
        df: pd.DataFrame,
        symbol: str,
        rl_prediction: Optional[str] = None,
        custom_params: dict = None
    ) -> Dict:
        """
        Genera decisión de trading basada en consenso híbrido
        
        Args:
            df: DataFrame con datos históricos e indicadores
            symbol: Símbolo del activo
            rl_prediction: Predicción del agente RL ("BUY", "SELL", "HOLD")
            custom_params: Parámetros personalizados para indicadores
        
        Returns:
            Dict con: final_signal, confidence, components, reasoning
        """
        # 1. Señal Técnica (con parámetros personalizados si existen)
        technical_signal = self.signal_generator.generate_signal(df, custom_params)
        
        # 2. Señal de Sentimiento
        sentiment_data = self.get_sentiment_score(symbol)
        
        # 3. Señal de RL
        rl_signal = rl_prediction if rl_prediction else "HOLD"
        
        # Construir componentes
        components = {
            "technical": {
                "signal": technical_signal["signal"],
                "confidence": technical_signal["confidence"],
                "strength": technical_signal["strength"],
                "votes": technical_signal["votes"]
            },
            "sentiment": {
                "signal": sentiment_data["signal"],
                "score": sentiment_data["score"],
                "confidence": sentiment_data["confidence"],
                "news_count": sentiment_data["news_count"]
            },
            "rl": {
                "signal": rl_signal,
                "enabled": rl_prediction is not None
            }
        }
        
        # Sistema de votación
        votes = {"BUY": 0, "SELL": 0, "HOLD": 0}
        weights = {"BUY": 0, "SELL": 0, "HOLD": 0}
        
        # Voto técnico (peso: 1.0)
        votes[technical_signal["signal"]] += 1
        weights[technical_signal["signal"]] += technical_signal["confidence"]
        
        # Voto de RL (peso: 1.0)
        if rl_prediction:
            votes[rl_signal] += 1
            weights[rl_signal] += 0.8  # Confianza fija del RL
        
        # Voto de sentimiento (peso: 0.5 - menos peso que técnico y RL)
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
        else:
            final_signal = winning_signals[0]
            consensus_pct = votes[final_signal] / total_votes if total_votes > 0 else 0
        
        # Verificar umbral de consenso
        if consensus_pct < self.consensus_threshold and final_signal != "HOLD":
            final_signal = "HOLD"
            reasoning = f"Consenso insuficiente ({consensus_pct*100:.1f}% < {self.consensus_threshold*100:.1f}%)"
        else:
            reasoning = self._generate_reasoning(components, final_signal)
        
        # Calcular confianza final (promedio ponderado)
        final_confidence = weights[final_signal] / votes[final_signal] if votes[final_signal] > 0 else 0
        
        return {
            "signal": final_signal,
            "confidence": final_confidence,
            "consensus_pct": consensus_pct,
            "components": components,
            "reasoning": reasoning,
            "votes": votes
        }
    
    def _generate_reasoning(self, components: Dict, final_signal: str) -> str:
        """Genera explicación de la decisión"""
        reasons = []
        
        # Técnico
        tech = components["technical"]
        if tech["signal"] == final_signal:
            reasons.append(f"Técnico: {tech['signal']} (confianza {tech['confidence']*100:.0f}%)")
        
        # RL
        rl = components["rl"]
        if rl["enabled"] and rl["signal"] == final_signal:
            reasons.append(f"RL: {rl['signal']}")
        
        # Sentimiento
        sent = components["sentiment"]
        if sent["signal"] != "NEUTRAL":
            if (sent["signal"] == "POSITIVE" and final_signal == "BUY") or \
               (sent["signal"] == "NEGATIVE" and final_signal == "SELL"):
                reasons.append(f"Sentimiento: {sent['signal']} (score {sent['score']:.2f})")
        
        if not reasons:
            return "Señales mixtas - mantener posición"
        
        return " | ".join(reasons)
