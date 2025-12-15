import requests
import logging
from typing import List, Dict
from datetime import datetime, timedelta
from .config import settings

logger = logging.getLogger(__name__)

class NewsService:
    """
    Aggregates financial news from multiple providers.
    Designed to be resilient: if one API fails, it tries the next.
    """

    def __init__(self):
        self.seen_titles = set()

    def get_news(self, query: str = "Argentina Economy") -> List[Dict]:
        """
        Fetches news from available sources.
        Returns a list of dicts: {'title': str, 'source': str, 'published_at': str}
        """
        news_items = []

        # 1. Try NewsAPI (General Global)
        if settings.NEWS_API_KEY:
            news_items.extend(self._fetch_newsapi(query))

        # 2. Try Finnhub (Financial Specific)
        if settings.FINNHUB_API_KEY and len(news_items) < 5:
            news_items.extend(self._fetch_finnhub(query))

        # 3. Try Alpha Vantage (Sentiment/News)
        if settings.ALPHA_VANTAGE_API_KEY and len(news_items) < 5:
            news_items.extend(self._fetch_alphavantage(query))

        # Deduplicate
        unique_news = []
        for item in news_items:
            if item['title'] not in self.seen_titles:
                unique_news.append(item)
                self.seen_titles.add(item['title'])

        logger.info(f"📰 Fetched {len(unique_news)} new articles for '{query}'")
        return unique_news

    def _fetch_newsapi(self, query: str) -> List[Dict]:
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": query,
                "apiKey": settings.NEWS_API_KEY,
                "language": "en", # Better for NLP models
                "sortBy": "publishedAt",
                "pageSize": 5
            }
            resp = requests.get(url, params=params, timeout=5)
            if resp.status_code == 200:
                articles = resp.json().get("articles", [])
                return [{"title": a["title"], "source": "NewsAPI", "published_at": a["publishedAt"]} for a in articles]
        except Exception as e:
            logger.error(f"NewsAPI failed: {e}")
        return []

    def _fetch_finnhub(self, query: str) -> List[Dict]:
        try:
            # Finnhub general news or company news
            url = "https://finnhub.io/api/v1/news"
            params = {
                "category": "general",
                "token": settings.FINNHUB_API_KEY
            }
            resp = requests.get(url, params=params, timeout=5)
            if resp.status_code == 200:
                articles = resp.json()[:5]
                return [{"title": a["headline"], "source": "Finnhub", "published_at": str(datetime.now())} for a in articles]
        except Exception as e:
            logger.error(f"Finnhub failed: {e}")
        return []

    def _fetch_alphavantage(self, query: str) -> List[Dict]:
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "NEWS_SENTIMENT",
                "tickers": query if query.isupper() and len(query) < 5 else "", # Use ticker if query looks like one
                "topics": "economy_macro" if not query.isupper() else "",
                "apikey": settings.ALPHA_VANTAGE_API_KEY,
                "limit": 5
            }
            resp = requests.get(url, params=params, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                feed = data.get("feed", [])
                return [{"title": a["title"], "source": "AlphaVantage", "published_at": a["time_published"]} for a in feed]
        except Exception as e:
            logger.error(f"AlphaVantage failed: {e}")
        return []
