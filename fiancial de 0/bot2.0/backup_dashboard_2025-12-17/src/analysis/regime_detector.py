"""
Market Regime Detector
Detecta el régimen actual del mercado usando Hidden Markov Models
"""

import numpy as np
import pandas as pd
from typing import Dict, Literal
from hmmlearn import hmm
from sklearn.preprocessing import StandardScaler


RegimeType = Literal["bull_trend", "bear_trend", "sideways", "high_volatility"]


class MarketRegimeDetector:
    """
    Detector de régimen de mercado
    
    Regímenes detectados:
    - bull_trend: Tendencia alcista sostenida
    - bear_trend: Tendencia bajista sostenida
    - sideways: Mercado lateral (rango)
    - high_volatility: Alta volatilidad sin tendencia clara
    """
    
    def __init__(self, n_regimes: int = 4):
        """
        Inicializa el detector
        
        Args:
            n_regimes: Número de regímenes a detectar
        """
        self.n_regimes = n_regimes
        self.model = hmm.GaussianHMM(
            n_components=n_regimes,
            covariance_type="full",
            n_iter=100,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Mapeo de estados a regímenes
        self.regime_map = {}
    
    def extract_features(self, df: pd.DataFrame) -> np.ndarray:
        """
        Extrae features para detección de régimen
        
        Args:
            df: DataFrame con datos OHLCV
        
        Returns:
            Array de features
        """
        features = []
        
        # 1. Retornos
        returns = df['close'].pct_change().fillna(0)
        features.append(returns)
        
        # 2. Volatilidad (rolling std de retornos)
        volatility = returns.rolling(window=20).std().fillna(0)
        features.append(volatility)
        
        # 3. Tendencia (SMA 50 - SMA 200)
        sma_50 = df['close'].rolling(window=50).mean()
        sma_200 = df['close'].rolling(window=200).mean()
        trend = ((sma_50 - sma_200) / sma_200).fillna(0)
        features.append(trend)
        
        # 4. Momentum (ROC 14 días)
        roc = df['close'].pct_change(periods=14).fillna(0)
        features.append(roc)
        
        # 5. Volumen relativo
        vol_avg = df['volume'].rolling(window=20).mean()
        vol_ratio = (df['volume'] / vol_avg).fillna(1)
        features.append(vol_ratio)
        
        # Combinar features
        feature_matrix = np.column_stack(features)
        
        return feature_matrix
    
    def train(self, df: pd.DataFrame):
        """
        Entrena el modelo HMM
        
        Args:
            df: DataFrame con datos históricos
        """
        print("🎓 Entrenando detector de régimen...")
        
        # Extraer features
        features = self.extract_features(df)
        
        # Normalizar
        features_scaled = self.scaler.fit_transform(features)
        
        # Entrenar HMM
        self.model.fit(features_scaled)
        
        # Identificar regímenes basándose en características
        self._identify_regimes(df, features_scaled)
        
        self.is_trained = True
        print("✓ Detector de régimen entrenado")
    
    def _identify_regimes(self, df: pd.DataFrame, features: np.ndarray):
        """
        Identifica qué estado HMM corresponde a qué régimen
        
        Args:
            df: DataFrame original
            features: Features normalizadas
        """
        # Predecir estados
        states = self.model.predict(features)
        
        # Calcular características promedio por estado
        state_characteristics = {}
        
        for state in range(self.n_regimes):
            mask = states == state
            
            if mask.sum() > 0:
                # Retorno promedio
                returns = df['close'].pct_change()[mask]
                avg_return = returns.mean()
                
                # Volatilidad promedio
                volatility = returns.std()
                
                # Tendencia (SMA 50 vs 200)
                sma_50 = df['close'].rolling(50).mean()[mask]
                sma_200 = df['close'].rolling(200).mean()[mask]
                trend = ((sma_50 - sma_200) / sma_200).mean()
                
                state_characteristics[state] = {
                    'return': avg_return,
                    'volatility': volatility,
                    'trend': trend
                }
        
        # Clasificar estados en regímenes
        for state, chars in state_characteristics.items():
            if chars['volatility'] > 0.03:  # Alta volatilidad
                self.regime_map[state] = 'high_volatility'
            elif chars['trend'] > 0.05:  # Tendencia alcista fuerte
                self.regime_map[state] = 'bull_trend'
            elif chars['trend'] < -0.05:  # Tendencia bajista fuerte
                self.regime_map[state] = 'bear_trend'
            else:  # Lateral
                self.regime_map[state] = 'sideways'
    
    def detect(self, df: pd.DataFrame) -> Dict:
        """
        Detecta el régimen actual del mercado
        
        Args:
            df: DataFrame con datos recientes
        
        Returns:
            Dict con régimen y detalles
        """
        if not self.is_trained:
            return {
                'regime': 'sideways',
                'confidence': 0.0,
                'state': -1,
                'description': 'Detector no entrenado'
            }
        
        # Extraer features
        features = self.extract_features(df)
        
        # Normalizar
        features_scaled = self.scaler.transform(features)
        
        # Predecir estado
        state = self.model.predict(features_scaled)[-1]
        
        # Obtener probabilidades
        log_prob, posteriors = self.model.score_samples(features_scaled)
        confidence = posteriors[-1, state]
        
        # Mapear a régimen
        regime = self.regime_map.get(state, 'sideways')
        
        # Descripción
        descriptions = {
            'bull_trend': '📈 Tendencia Alcista - Mercado en alza sostenida',
            'bear_trend': '📉 Tendencia Bajista - Mercado en caída sostenida',
            'sideways': '↔️ Lateral - Mercado en rango sin tendencia clara',
            'high_volatility': '⚡ Alta Volatilidad - Movimientos bruscos e impredecibles'
        }
        
        return {
            'regime': regime,
            'confidence': float(confidence),
            'state': int(state),
            'description': descriptions.get(regime, 'Desconocido')
        }
    
    def get_strategy_config(self, regime: RegimeType) -> Dict:
        """
        Obtiene configuración de estrategia según régimen
        
        Args:
            regime: Tipo de régimen
        
        Returns:
            Dict con configuración
        """
        configs = {
            'bull_trend': {
                'risk_multiplier': 1.3,
                'strategy': 'trend_following',
                'weights': {
                    'technical': 0.2,
                    'rl': 0.4,
                    'sentiment': 0.3,
                    'alt_data': 0.1
                },
                'description': 'Agresivo - Seguir tendencia alcista'
            },
            'bear_trend': {
                'risk_multiplier': 0.6,
                'strategy': 'defensive',
                'weights': {
                    'technical': 0.5,
                    'rl': 0.2,
                    'sentiment': 0.2,
                    'alt_data': 0.1
                },
                'description': 'Defensivo - Proteger capital'
            },
            'sideways': {
                'risk_multiplier': 1.0,
                'strategy': 'mean_reversion',
                'weights': {
                    'technical': 0.4,
                    'rl': 0.3,
                    'sentiment': 0.2,
                    'alt_data': 0.1
                },
                'description': 'Mean Reversion - Operar en rangos'
            },
            'high_volatility': {
                'risk_multiplier': 0.7,
                'strategy': 'conservative',
                'weights': {
                    'technical': 0.5,
                    'rl': 0.2,
                    'sentiment': 0.2,
                    'alt_data': 0.1
                },
                'description': 'Conservador - Reducir exposición'
            }
        }
        
        return configs.get(regime, configs['sideways'])
    
    def get_regime_summary(self, df: pd.DataFrame) -> str:
        """
        Genera resumen del régimen actual
        
        Args:
            df: DataFrame con datos
        
        Returns:
            str: Resumen en lenguaje natural
        """
        detection = self.detect(df)
        config = self.get_strategy_config(detection['regime'])
        
        summary = f"""
🎯 RÉGIMEN DE MERCADO DETECTADO

{detection['description']}
Confianza: {detection['confidence']:.1%}

ESTRATEGIA RECOMENDADA:
- Tipo: {config['strategy']}
- Multiplicador de Riesgo: {config['risk_multiplier']:.1f}x
- {config['description']}

PESOS DEL ENSEMBLE:
- Técnico: {config['weights']['technical']:.0%}
- RL: {config['weights']['rl']:.0%}
- Sentimiento: {config['weights']['sentiment']:.0%}
- Datos Alt: {config['weights']['alt_data']:.0%}
"""
        
        return summary.strip()
