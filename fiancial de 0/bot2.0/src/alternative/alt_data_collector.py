"""
Alternative Data Collector
Recolecta datos alternativos de múltiples fuentes
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import time


class AlternativeDataCollector:
    """
    Recolector de datos alternativos
    
    Fuentes:
    - Google Trends (interés de búsqueda)
    - Twitter/X (sentimiento social)
    - Reddit (menciones y discusiones)
    """
    
    def __init__(
        self,
        google_trends_api_key: str = "",
        twitter_bearer_token: str = "",
        enable_google_trends: bool = True,
        enable_twitter: bool = False,
        enable_reddit: bool = True
    ):
        """
        Inicializa el recolector
        
        Args:
            google_trends_api_key: API key de Google Trends
            twitter_bearer_token: Bearer token de Twitter
            enable_google_trends: Activar Google Trends
            enable_twitter: Activar Twitter
            enable_reddit: Activar Reddit
        """
        self.google_trends_api_key = google_trends_api_key
        self.twitter_bearer_token = twitter_bearer_token
        
        self.enable_google_trends = enable_google_trends and bool(google_trends_api_key)
        self.enable_twitter = enable_twitter and bool(twitter_bearer_token)
        self.enable_reddit = enable_reddit
        
        print("📡 Alternative Data Collector inicializado:")
        print(f"   Google Trends: {'✓' if self.enable_google_trends else '✗'}")
        print(f"   Twitter: {'✓' if self.enable_twitter else '✗'}")
        print(f"   Reddit: {'✓' if self.enable_reddit else '✗'}")
    
    def get_google_trends(self, symbol: str, days: int = 7) -> Dict:
        """
        Obtiene interés de búsqueda de Google Trends
        
        Args:
            symbol: Símbolo del activo
            days: Días hacia atrás
        
        Returns:
            Dict con datos de tendencias
        """
        if not self.enable_google_trends:
            return {'interest': 50, 'trend': 'neutral', 'available': False}
        
        try:
            # Simulación (Google Trends no tiene API oficial gratuita)
            # En producción, usar pytrends o SerpAPI
            from pytrends.request import TrendReq
            
            pytrends = TrendReq(hl='es-AR', tz=360)
            
            # Buscar símbolo
            pytrends.build_payload([symbol], timeframe=f'now {days}-d')
            
            # Obtener datos
            data = pytrends.interest_over_time()
            
            if data.empty:
                return {'interest': 50, 'trend': 'neutral', 'available': False}
            
            # Calcular interés promedio
            interest = data[symbol].mean()
            
            # Detectar tendencia
            recent = data[symbol].tail(3).mean()
            older = data[symbol].head(3).mean()
            
            if recent > older * 1.2:
                trend = 'increasing'
            elif recent < older * 0.8:
                trend = 'decreasing'
            else:
                trend = 'stable'
            
            return {
                'interest': float(interest),
                'trend': trend,
                'recent_interest': float(recent),
                'available': True
            }
            
        except Exception as e:
            print(f"⚠ Error obteniendo Google Trends: {e}")
            return {'interest': 50, 'trend': 'neutral', 'available': False}
    
    def get_twitter_sentiment(self, symbol: str, count: int = 100) -> Dict:
        """
        Obtiene sentimiento de Twitter
        
        Args:
            symbol: Símbolo del activo
            count: Número de tweets a analizar
        
        Returns:
            Dict con sentimiento
        """
        if not self.enable_twitter:
            return {'sentiment': 0.0, 'volume': 0, 'available': False}
        
        try:
            # Buscar tweets
            url = "https://api.twitter.com/2/tweets/search/recent"
            headers = {"Authorization": f"Bearer {self.twitter_bearer_token}"}
            params = {
                "query": f"${symbol} OR {symbol}",
                "max_results": count,
                "tweet.fields": "created_at,public_metrics"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code != 200:
                return {'sentiment': 0.0, 'volume': 0, 'available': False}
            
            data = response.json()
            tweets = data.get('data', [])
            
            if not tweets:
                return {'sentiment': 0.0, 'volume': 0, 'available': False}
            
            # Análisis simple de sentimiento (en producción usar modelo NLP)
            positive_words = ['buy', 'bull', 'moon', 'up', 'gain', 'profit']
            negative_words = ['sell', 'bear', 'down', 'loss', 'crash', 'dump']
            
            sentiment_score = 0
            for tweet in tweets:
                text = tweet.get('text', '').lower()
                
                pos_count = sum(1 for word in positive_words if word in text)
                neg_count = sum(1 for word in negative_words if word in text)
                
                sentiment_score += (pos_count - neg_count)
            
            # Normalizar a -1 a 1
            normalized_sentiment = sentiment_score / len(tweets) if tweets else 0
            normalized_sentiment = max(-1, min(1, normalized_sentiment))
            
            return {
                'sentiment': normalized_sentiment,
                'volume': len(tweets),
                'available': True
            }
            
        except Exception as e:
            print(f"⚠ Error obteniendo Twitter sentiment: {e}")
            return {'sentiment': 0.0, 'volume': 0, 'available': False}
    
    def get_reddit_mentions(self, symbol: str, subreddits: List[str] = None) -> Dict:
        """
        Obtiene menciones de Reddit
        
        Args:
            symbol: Símbolo del activo
            subreddits: Lista de subreddits a buscar
        
        Returns:
            Dict con menciones
        """
        if not self.enable_reddit:
            return {'mentions': 0, 'sentiment': 0.0, 'available': False}
        
        if subreddits is None:
            subreddits = ['wallstreetbets', 'stocks', 'investing']
        
        try:
            # Usar API pública de Reddit (sin autenticación)
            mentions = 0
            sentiment_scores = []
            
            for subreddit in subreddits:
                url = f"https://www.reddit.com/r/{subreddit}/search.json"
                params = {
                    'q': symbol,
                    'restrict_sr': 'on',
                    'sort': 'new',
                    'limit': 25
                }
                headers = {'User-Agent': 'TradingBot/1.0'}
                
                response = requests.get(url, params=params, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    posts = data.get('data', {}).get('children', [])
                    
                    mentions += len(posts)
                    
                    # Análisis simple de sentimiento
                    for post in posts:
                        title = post.get('data', {}).get('title', '').lower()
                        score = post.get('data', {}).get('score', 0)
                        
                        # Sentimiento basado en upvotes
                        if score > 100:
                            sentiment_scores.append(1)
                        elif score < -10:
                            sentiment_scores.append(-1)
                        else:
                            sentiment_scores.append(0)
                
                # Rate limiting
                time.sleep(1)
            
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
            
            return {
                'mentions': mentions,
                'sentiment': avg_sentiment,
                'available': True
            }
            
        except Exception as e:
            print(f"⚠ Error obteniendo Reddit mentions: {e}")
            return {'mentions': 0, 'sentiment': 0.0, 'available': False}
    
    def collect_all(self, symbol: str) -> Dict:
        """
        Recolecta todos los datos alternativos
        
        Args:
            symbol: Símbolo del activo
        
        Returns:
            Dict con todos los datos
        """
        print(f"📡 Recolectando datos alternativos para {symbol}...")
        
        # Google Trends
        trends = self.get_google_trends(symbol)
        
        # Twitter
        twitter = self.get_twitter_sentiment(symbol)
        
        # Reddit
        reddit = self.get_reddit_mentions(symbol)
        
        # Calcular score agregado
        score = 0
        weight_sum = 0
        
        if trends['available']:
            # Normalizar interés (0-100 → -1 a 1)
            trend_score = (trends['interest'] - 50) / 50
            score += trend_score * 0.3
            weight_sum += 0.3
        
        if twitter['available']:
            score += twitter['sentiment'] * 0.4
            weight_sum += 0.4
        
        if reddit['available']:
            score += reddit['sentiment'] * 0.3
            weight_sum += 0.3
        
        # Normalizar score
        aggregated_score = score / weight_sum if weight_sum > 0 else 0
        
        # Clasificar
        if aggregated_score > 0.3:
            signal = 'POSITIVE'
        elif aggregated_score < -0.3:
            signal = 'NEGATIVE'
        else:
            signal = 'NEUTRAL'
        
        return {
            'symbol': symbol,
            'timestamp': datetime.now(),
            'google_trends': trends,
            'twitter': twitter,
            'reddit': reddit,
            'aggregated_score': aggregated_score,
            'signal': signal,
            'confidence': abs(aggregated_score)
        }
    
    def get_signal(self, symbol: str) -> Dict:
        """
        Obtiene señal de trading basada en datos alternativos
        
        Args:
            symbol: Símbolo del activo
        
        Returns:
            Dict con señal
        """
        data = self.collect_all(symbol)
        
        # Mapear a acción de trading
        if data['signal'] == 'POSITIVE' and data['confidence'] > 0.5:
            action = 'BUY'
        elif data['signal'] == 'NEGATIVE' and data['confidence'] > 0.5:
            action = 'SELL'
        else:
            action = 'HOLD'
        
        return {
            'action': action,
            'confidence': data['confidence'],
            'score': data['aggregated_score'],
            'reasoning': f"Alt Data: {data['signal']} (score: {data['aggregated_score']:.2f})"
        }
