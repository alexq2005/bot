"""
News Aggregator
Agrega noticias de múltiples fuentes (NewsData, Finnhub, Alpha Vantage)
"""

import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta


class NewsAggregator:
    """Agregador de noticias financieras de múltiples fuentes"""
    
    def __init__(
        self,
        newsdata_api_key: str = "",
        finnhub_api_key: str = "",
        alphavantage_api_key: str = "",
        news_api_key: str = "",
        gnews_api_key: str = ""
    ):
        """
        Inicializa el agregador de noticias
        
        Args:
            newsdata_api_key: API key de NewsData.io
            finnhub_api_key: API key de Finnhub
            alphavantage_api_key: API key de Alpha Vantage
            news_api_key: API key de NewsAPI.org
            gnews_api_key: API key de GNews.io
        """
        self.newsdata_api_key = newsdata_api_key
        self.finnhub_api_key = finnhub_api_key
        self.alphavantage_api_key = alphavantage_api_key
        self.news_api_key = news_api_key
        self.gnews_api_key = gnews_api_key
    
    def get_newsdata_news(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Obtiene noticias de NewsData.io
        
        Args:
            query: Término de búsqueda (ej: "GGAL", "Galicia")
            max_results: Máximo número de resultados
        
        Returns:
            Lista de noticias
        """
        if not self.newsdata_api_key:
            return []
        
        try:
            url = "https://newsdata.io/api/1/news"
            params = {
                "apikey": self.newsdata_api_key,
                "q": query,
                "language": "es",
                "category": "business",
                "size": max_results
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            # Normalizar formato
            news = []
            for item in results:
                news.append({
                    "headline": item.get("title", ""),
                    "source": "NewsData",
                    "url": item.get("link", ""),
                    "published_at": item.get("pubDate", ""),
                    "description": item.get("description", "")
                })
            
            return news
            
        except Exception as e:
            print(f"⚠ Error obteniendo noticias de NewsData: {e}")
            return []
    
    def get_finnhub_news(self, symbol: str, max_results: int = 10) -> List[Dict]:
        """
        Obtiene noticias de Finnhub
        
        Args:
            symbol: Símbolo del activo
            max_results: Máximo número de resultados
        
        Returns:
            Lista de noticias
        """
        if not self.finnhub_api_key:
            return []
        
        try:
            # Finnhub usa formato de fechas YYYY-MM-DD
            to_date = datetime.now()
            from_date = to_date - timedelta(days=7)
            
            url = "https://finnhub.io/api/v1/company-news"
            params = {
                "symbol": symbol,
                "from": from_date.strftime("%Y-%m-%d"),
                "to": to_date.strftime("%Y-%m-%d"),
                "token": self.finnhub_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Normalizar formato
            news = []
            for item in data[:max_results]:
                news.append({
                    "headline": item.get("headline", ""),
                    "source": "Finnhub",
                    "url": item.get("url", ""),
                    "published_at": datetime.fromtimestamp(item.get("datetime", 0)).isoformat(),
                    "description": item.get("summary", "")
                })
            
            return news
            
        except Exception as e:
            print(f"⚠ Error obteniendo noticias de Finnhub: {e}")
            return []
    
    def get_alphavantage_news(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Obtiene noticias de Alpha Vantage
        
        Args:
            query: Término de búsqueda
            max_results: Máximo número de resultados
        
        Returns:
            Lista de noticias
        """
        if not self.alphavantage_api_key:
            return []
        
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "NEWS_SENTIMENT",
                "tickers": query,
                "apikey": self.alphavantage_api_key,
                "limit": max_results
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            feed = data.get("feed", [])
            
            # Normalizar formato
            news = []
            for item in feed:
                news.append({
                    "headline": item.get("title", ""),
                    "source": "AlphaVantage",
                    "url": item.get("url", ""),
                    "published_at": item.get("time_published", ""),
                    "description": item.get("summary", "")
                })
            
            return news
            
        except Exception as e:
            print(f"⚠ Error obteniendo noticias de Alpha Vantage: {e}")
            return []

    def get_newsapi_news(self, query: str, max_results: int = 10) -> List[Dict]:
        """Obtiene noticias de NewsAPI.org"""
        if not self.news_api_key: return []
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": query,
                "apiKey": self.news_api_key,
                "language": "es",
                "sortBy": "publishedAt",
                "pageSize": max_results
            }
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            articles = data.get("articles", [])
            news = []
            for item in articles:
                news.append({
                    "headline": item.get("title", ""),
                    "source": item.get("source", {}).get("name", "NewsAPI"),
                    "url": item.get("url", ""),
                    "published_at": item.get("publishedAt", ""),
                    "description": item.get("description", "")
                })
            return news
        except Exception as e:
            print(f"⚠ Error NewsAPI: {e}")
            return []

    def get_gnews_news(self, query: str, max_results: int = 10) -> List[Dict]:
        """Obtiene noticias de GNews.io"""
        if not self.gnews_api_key: return []
        try:
            url = "https://gnews.io/api/v4/search"
            params = {
                "q": query,
                "token": self.gnews_api_key,
                "lang": "es",
                "max": max_results,
                "sortby": "publishedAt"
            }
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            articles = data.get("articles", [])
            news = []
            for item in articles:
                news.append({
                    "headline": item.get("title", ""),
                    "source": item.get("source", {}).get("name", "GNews"),
                    "url": item.get("url", ""),
                    "published_at": item.get("publishedAt", ""),
                    "description": item.get("description", "")
                })
            return news
        except Exception as e:
            print(f"⚠ Error GNews: {e}")
            return []
    
    def get_all_news(self, symbol: str, query: str = None, max_per_source: int = 5) -> List[Dict]:
        """
        Obtiene noticias de todas las fuentes disponibles
        
        Args:
            symbol: Símbolo del activo (para Finnhub)
            query: Término de búsqueda (para NewsData y AlphaVantage)
            max_per_source: Máximo de noticias por fuente
        
        Returns:
            Lista combinada de noticias
        """
        all_news = []
        
        # Si no se proporciona query, usar el símbolo
        if not query:
            query = symbol
        
        # Obtener de todas las fuentes
        all_news.extend(self.get_newsdata_news(query, max_per_source))
        all_news.extend(self.get_finnhub_news(symbol, max_per_source))
        all_news.extend(self.get_alphavantage_news(query, max_per_source))
        all_news.extend(self.get_newsapi_news(query, max_per_source))
        all_news.extend(self.get_gnews_news(query, max_per_source))
        
        # Deduplicar por titular
        seen_headlines = set()
        unique_news = []
        
        for news_item in all_news:
            headline = news_item['headline'].lower().strip()
            if headline and headline not in seen_headlines:
                seen_headlines.add(headline)
                unique_news.append(news_item)
        
        # Ordenar por fecha (más recientes primero)
        unique_news.sort(
            key=lambda x: x.get('published_at', ''),
            reverse=True
        )
        
        return unique_news
    
    def get_mock_news(self, symbol: str) -> List[Dict]:
        """
        Genera noticias mock para testing
        
        Args:
            symbol: Símbolo del activo
        
        Returns:
            Lista de noticias simuladas
        """
        import random
        
        templates = [
            f"{symbol} registra fuerte alza en la jornada bursátil",
            f"Analistas recomiendan comprar acciones de {symbol}",
            f"{symbol} presenta resultados trimestrales por encima de expectativas",
            f"Caída en el precio de {symbol} genera preocupación",
            f"{symbol} anuncia nuevos proyectos de expansión",
            f"Volatilidad en {symbol} tras anuncio económico"
        ]
        
        news = []
        for i, template in enumerate(random.sample(templates, min(5, len(templates)))):
            news.append({
                "headline": template,
                "source": "Mock",
                "url": f"https://example.com/news/{i}",
                "published_at": (datetime.now() - timedelta(hours=i)).isoformat(),
                "description": f"Noticia simulada sobre {symbol}"
            })
        
        return news
