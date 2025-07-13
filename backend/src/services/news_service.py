import requests
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from .api_validation_service import api_validator


class NewsService:
    """Service for integrating with news APIs"""

    def __init__(self):
        self.newsapi_key = os.getenv("NEWS_API_KEY")
        self.newsapi_base_url = "https://newsapi.org/v2"
        self.eodhd_api_key = os.getenv("EODHD_API_KEY")
        self.eodhd_base_url = "https://eodhistoricaldata.com/api"

    def search_news(self, query: str, days_back: int = 30, sources: Optional[str] = "") -> Dict:
        """Search for news articles about a brand"""
        if not self.newsapi_key:
            return {"success": False, "error": "NewsAPI key not configured. Cannot provide news data without real API access.", "articles": []}

        try:
            # Calculate date range
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days_back)

            def search_operation():
                return self._search_newsapi(query, from_date, to_date, sources)

            # Use validation service with retry logic
            return api_validator.execute_with_retry('newsapi', search_operation)

        except Exception as e:
            api_validator.log_api_usage('newsapi', 'search_news', False, None, str(e))
            return {"success": False, "error": f"News search failed: {str(e)}. Cannot provide news data without real API access.", "articles": []}

    def get_financial_news(self, symbol: str, days_back: int = 30) -> Dict:
        """Get financial news for a specific stock symbol"""
        if not self.eodhd_api_key:
            return {"success": False, "error": "EODHD API key not configured. Cannot provide financial news without real API access.", "articles": []}

        try:
            return self._get_eodhd_news(symbol, days_back)
        except Exception as e:
            return {"success": False, "error": f"Financial news search failed: {str(e)}. Cannot provide financial news without real API access.", "articles": []}

    def analyze_news_sentiment(self, articles: List[Dict]) -> Dict:
        """Analyze sentiment of news articles"""
        try:
            if not articles:
                return {"success": False, "error": "No articles provided for analysis"}

            # Mock sentiment analysis - in production, this would use LLM service
            positive_count = 0
            negative_count = 0
            neutral_count = 0

            sentiment_keywords = {
                "positive": [
                    "growth",
                    "success",
                    "profit",
                    "innovation",
                    "award",
                    "expansion",
                    "breakthrough",
                ],
                "negative": [
                    "loss",
                    "decline",
                    "scandal",
                    "lawsuit",
                    "bankruptcy",
                    "crisis",
                    "controversy",
                ],
            }

            for article in articles:
                content = (
                    article.get("title", "") + " " + article.get("description", "")
                ).lower()

                positive_score = sum(
                    1 for word in sentiment_keywords["positive"] if word in content
                )
                negative_score = sum(
                    1 for word in sentiment_keywords["negative"] if word in content
                )

                if positive_score > negative_score:
                    positive_count += 1
                elif negative_score > positive_score:
                    negative_count += 1
                else:
                    neutral_count += 1

            total_articles = len(articles)

            return {
                "success": True,
                "sentiment_distribution": {
                    "positive": round((positive_count / total_articles) * 100, 1),
                    "negative": round((negative_count / total_articles) * 100, 1),
                    "neutral": round((neutral_count / total_articles) * 100, 1),
                },
                "article_counts": {
                    "positive": positive_count,
                    "negative": negative_count,
                    "neutral": neutral_count,
                    "total": total_articles,
                },
                "overall_sentiment": self._determine_overall_sentiment(
                    positive_count, negative_count, neutral_count
                ),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_trending_topics(self, articles: List[Dict]) -> Dict:
        """Extract trending topics from news articles"""
        try:
            if not articles:
                return {"success": False, "error": "No articles provided for analysis"}

            # Simple keyword extraction - in production, this would use NLP
            word_count: Dict[str, int] = {}
            stop_words = {
                "the",
                "and",
                "or",
                "but",
                "in",
                "on",
                "at",
                "to",
                "for",
                "of",
                "with",
                "by",
                "is",
                "are",
                "was",
                "were",
                "be",
                "been",
                "being",
                "have",
                "has",
                "had",
                "do",
                "does",
                "did",
                "will",
                "would",
                "could",
                "should",
                "may",
                "might",
                "must",
                "can",
                "a",
                "an",
                "this",
                "that",
                "these",
                "those",
            }

            for article in articles:
                content = (
                    article.get("title", "") + " " + article.get("description", "")
                ).lower()
                words = content.split()

                for word in words:
                    # Clean word
                    word = "".join(c for c in word if c.isalnum())
                    if len(word) > 3 and word not in stop_words:
                        word_count[word] = word_count.get(word, 0) + 1

            # Get top trending topics
            trending = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:10]

            return {
                "success": True,
                "trending_topics": [
                    {"topic": topic, "mentions": count} for topic, count in trending
                ],
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _search_newsapi(
        self,
        query: str,
        from_date: datetime,
        to_date: datetime,
        sources: Optional[str] = None,
    ) -> Dict:
        """Search using NewsAPI"""
        headers = {"X-API-Key": self.newsapi_key}

        params = {
            "q": query,
            "from": from_date.strftime("%Y-%m-%d"),
            "to": to_date.strftime("%Y-%m-%d"),
            "sortBy": "relevancy",
            "language": "en",
            "pageSize": 100,
        }

        if sources:
            params["sources"] = sources

        response = requests.get(
            f"{self.newsapi_base_url}/everything",
            headers=headers,
            params=params,
            timeout=30,
        )

        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "total_results": data.get("totalResults", 0),
                "articles": data.get("articles", []),
            }
        else:
            raise Exception(f"NewsAPI error: {response.status_code} - {response.text}")

    def _get_eodhd_news(self, symbol: str, days_back: int) -> Dict:
        """Get financial news from EODHD"""
        params = {
            "api_token": self.eodhd_api_key,
            "s": symbol,
            "limit": 100,
            "from": (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d"),
        }

        response = requests.get(
            f"{self.eodhd_base_url}/news", params=params, timeout=30
        )

        if response.status_code == 200:
            articles = response.json()
            return {
                "success": True,
                "total_results": len(articles),
                "articles": articles,
            }
        else:
            raise Exception(
                f"EODHD API error: {response.status_code} - {response.text}"
            )

    def _determine_overall_sentiment(
        self, positive: int, negative: int, neutral: int
    ) -> str:
        """Determine overall sentiment based on counts"""
        total = positive + negative + neutral
        if total == 0:
            return "neutral"

        positive_pct = positive / total
        negative_pct = negative / total

        if positive_pct > 0.6:
            return "very positive"
        elif positive_pct > 0.4:
            return "positive"
        elif negative_pct > 0.6:
            return "very negative"
        elif negative_pct > 0.4:
            return "negative"
        else:
            return "neutral"


# Global instance
news_service = NewsService()
