"""
Fallback Service for Brand Audit Application

This service provides intelligent fallback strategies when primary APIs fail,
ensuring the application continues to function with alternative data sources
and graceful degradation.
"""

import logging
import requests
import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor

from src.utils.logging_config import get_logger
from src.services.error_management_service import error_manager, ErrorContext


class FallbackPriority(Enum):
    """Priority levels for fallback strategies"""
    HIGH = 1
    MEDIUM = 2
    LOW = 3


@dataclass
class FallbackResult:
    """Result from a fallback operation"""
    success: bool
    data: Any
    source: str
    quality_score: float  # 0.0 to 1.0, where 1.0 is equivalent to primary source
    limitations: List[str]
    execution_time: float
    fallback_used: bool = True


class FallbackService:
    """Service for managing fallback strategies"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.fallback_cache = {}
        self.cache_ttl = 3600  # 1 hour
        
    async def get_brand_data_with_fallback(self, company_name: str, website: Optional[str] = None) -> FallbackResult:
        """Get brand data with fallback strategies"""
        context = ErrorContext(
            operation="brand_data_fallback",
            additional_context={"company_name": company_name, "website": website}
        )
        
        # Try fallback strategies in order of priority
        strategies = [
            (FallbackPriority.HIGH, self._wikipedia_brand_fallback),
            (FallbackPriority.MEDIUM, self._web_scraping_fallback),
            (FallbackPriority.LOW, self._cached_brand_fallback)
        ]
        
        for priority, strategy in strategies:
            try:
                self.logger.info(f"Attempting {strategy.__name__} for {company_name}")
                result = await self._execute_fallback_strategy(strategy, company_name, website)
                
                if result.success:
                    self.logger.info(f"Fallback strategy {strategy.__name__} succeeded")
                    return result
                    
            except Exception as e:
                self.logger.warning(f"Fallback strategy {strategy.__name__} failed: {str(e)}")
                continue
        
        # All fallback strategies failed
        return FallbackResult(
            success=False,
            data=None,
            source="none",
            quality_score=0.0,
            limitations=["All fallback strategies failed"],
            execution_time=0.0
        )
    
    async def get_news_data_with_fallback(self, company_name: str, days_back: int = 30) -> FallbackResult:
        """Get news data with fallback strategies"""
        strategies = [
            (FallbackPriority.HIGH, self._rss_news_fallback),
            (FallbackPriority.MEDIUM, self._google_news_fallback),
            (FallbackPriority.LOW, self._cached_news_fallback)
        ]
        
        for priority, strategy in strategies:
            try:
                self.logger.info(f"Attempting {strategy.__name__} for {company_name}")
                result = await self._execute_fallback_strategy(strategy, company_name, days_back)
                
                if result.success:
                    self.logger.info(f"News fallback strategy {strategy.__name__} succeeded")
                    return result
                    
            except Exception as e:
                self.logger.warning(f"News fallback strategy {strategy.__name__} failed: {str(e)}")
                continue
        
        return FallbackResult(
            success=False,
            data={"articles": [], "total_results": 0},
            source="none",
            quality_score=0.0,
            limitations=["No news data available"],
            execution_time=0.0
        )
    
    async def get_ai_analysis_with_fallback(self, context: str, company_name: str) -> FallbackResult:
        """Get AI analysis with fallback strategies"""
        strategies = [
            (FallbackPriority.HIGH, self._template_analysis_fallback),
            (FallbackPriority.MEDIUM, self._rule_based_analysis_fallback),
            (FallbackPriority.LOW, self._cached_analysis_fallback)
        ]
        
        for priority, strategy in strategies:
            try:
                self.logger.info(f"Attempting {strategy.__name__} for {company_name}")
                result = await self._execute_fallback_strategy(strategy, context, company_name)
                
                if result.success:
                    self.logger.info(f"AI analysis fallback strategy {strategy.__name__} succeeded")
                    return result
                    
            except Exception as e:
                self.logger.warning(f"AI analysis fallback strategy {strategy.__name__} failed: {str(e)}")
                continue
        
        return FallbackResult(
            success=False,
            data=None,
            source="none",
            quality_score=0.0,
            limitations=["AI analysis unavailable"],
            execution_time=0.0
        )
    
    async def _execute_fallback_strategy(self, strategy: Callable, *args, **kwargs) -> FallbackResult:
        """Execute a fallback strategy with timeout and error handling"""
        start_time = time.time()
        
        try:
            # Execute strategy with timeout
            result = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    self.executor, strategy, *args, **kwargs
                ),
                timeout=30.0
            )
            
            execution_time = time.time() - start_time
            result.execution_time = execution_time
            
            return result
            
        except asyncio.TimeoutError:
            return FallbackResult(
                success=False,
                data=None,
                source=strategy.__name__,
                quality_score=0.0,
                limitations=["Strategy timed out"],
                execution_time=time.time() - start_time
            )
        except Exception as e:
            return FallbackResult(
                success=False,
                data=None,
                source=strategy.__name__,
                quality_score=0.0,
                limitations=[f"Strategy failed: {str(e)}"],
                execution_time=time.time() - start_time
            )
    
    def _wikipedia_brand_fallback(self, company_name: str, website: Optional[str] = None) -> FallbackResult:
        """Fallback to Wikipedia for brand information"""
        try:
            import wikipedia
            
            # Search for the company
            search_results = wikipedia.search(company_name, results=3)
            if not search_results:
                return FallbackResult(
                    success=False,
                    data=None,
                    source="wikipedia",
                    quality_score=0.0,
                    limitations=["No Wikipedia results found"],
                    execution_time=0.0
                )
            
            # Get the page content
            page = wikipedia.page(search_results[0])
            
            # Extract relevant information
            data = {
                "name": company_name,
                "description": page.summary[:500] if page.summary else "",
                "url": page.url,
                "founded": self._extract_founded_date(page.content),
                "industry": self._extract_industry(page.content),
                "headquarters": self._extract_headquarters(page.content),
                "source": "wikipedia",
                "confidence": 0.7
            }
            
            return FallbackResult(
                success=True,
                data=data,
                source="wikipedia",
                quality_score=0.7,
                limitations=["Limited to publicly available Wikipedia information"],
                execution_time=0.0
            )
            
        except Exception as e:
            return FallbackResult(
                success=False,
                data=None,
                source="wikipedia",
                quality_score=0.0,
                limitations=[f"Wikipedia fallback failed: {str(e)}"],
                execution_time=0.0
            )
    
    def _web_scraping_fallback(self, company_name: str, website: Optional[str] = None) -> FallbackResult:
        """Fallback to web scraping for brand information"""
        if not website:
            return FallbackResult(
                success=False,
                data=None,
                source="web_scraping",
                quality_score=0.0,
                limitations=["No website provided for scraping"],
                execution_time=0.0
            )
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(website, headers=headers, timeout=10)
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic information
            title = soup.find('title')
            description = soup.find('meta', attrs={'name': 'description'})
            keywords = soup.find('meta', attrs={'name': 'keywords'})
            
            data = {
                "name": company_name,
                "title": title.text.strip() if title else "",
                "description": description.get('content', '') if description else "",
                "keywords": keywords.get('content', '').split(',') if keywords else [],
                "url": website,
                "source": "web_scraping",
                "confidence": 0.5
            }
            
            return FallbackResult(
                success=True,
                data=data,
                source="web_scraping",
                quality_score=0.5,
                limitations=["Limited to basic website metadata", "May not reflect current information"],
                execution_time=0.0
            )
            
        except Exception as e:
            return FallbackResult(
                success=False,
                data=None,
                source="web_scraping",
                quality_score=0.0,
                limitations=[f"Web scraping failed: {str(e)}"],
                execution_time=0.0
            )
    
    def _cached_brand_fallback(self, company_name: str, website: Optional[str] = None) -> FallbackResult:
        """Fallback to cached brand information"""
        cache_key = f"brand_{company_name.lower().replace(' ', '_')}"
        
        if cache_key in self.fallback_cache:
            cached_data = self.fallback_cache[cache_key]
            if datetime.utcnow() - cached_data['timestamp'] < timedelta(seconds=self.cache_ttl):
                return FallbackResult(
                    success=True,
                    data=cached_data['data'],
                    source="cache",
                    quality_score=0.3,
                    limitations=["Using cached data", "May be outdated"],
                    execution_time=0.0
                )
        
        return FallbackResult(
            success=False,
            data=None,
            source="cache",
            quality_score=0.0,
            limitations=["No cached data available"],
            execution_time=0.0
        )
    
    def _rss_news_fallback(self, company_name: str, days_back: int = 30) -> FallbackResult:
        """Fallback to RSS feeds for news data"""
        try:
            import feedparser
            
            # Google News RSS feed
            rss_url = f"https://news.google.com/rss/search?q={company_name}&hl=en-US&gl=US&ceid=US:en"
            
            feed = feedparser.parse(rss_url)
            articles = []
            
            for entry in feed.entries[:10]:  # Limit to 10 articles
                articles.append({
                    "title": entry.title,
                    "description": entry.summary if hasattr(entry, 'summary') else "",
                    "url": entry.link,
                    "published": entry.published if hasattr(entry, 'published') else "",
                    "source": "Google News RSS"
                })
            
            data = {
                "articles": articles,
                "total_results": len(articles),
                "source": "rss_feeds"
            }
            
            return FallbackResult(
                success=True,
                data=data,
                source="rss_feeds",
                quality_score=0.6,
                limitations=["Limited article details", "May include unrelated news"],
                execution_time=0.0
            )
            
        except Exception as e:
            return FallbackResult(
                success=False,
                data={"articles": [], "total_results": 0},
                source="rss_feeds",
                quality_score=0.0,
                limitations=[f"RSS feed fallback failed: {str(e)}"],
                execution_time=0.0
            )
    
    def _google_news_fallback(self, company_name: str, days_back: int = 30) -> FallbackResult:
        """Fallback to Google News search (simplified)"""
        # This would implement a more sophisticated Google News search
        # For now, return a basic structure
        return FallbackResult(
            success=False,
            data={"articles": [], "total_results": 0},
            source="google_news",
            quality_score=0.0,
            limitations=["Google News fallback not implemented"],
            execution_time=0.0
        )
    
    def _cached_news_fallback(self, company_name: str, days_back: int = 30) -> FallbackResult:
        """Fallback to cached news data"""
        cache_key = f"news_{company_name.lower().replace(' ', '_')}"
        
        if cache_key in self.fallback_cache:
            cached_data = self.fallback_cache[cache_key]
            if datetime.utcnow() - cached_data['timestamp'] < timedelta(seconds=self.cache_ttl):
                return FallbackResult(
                    success=True,
                    data=cached_data['data'],
                    source="cache",
                    quality_score=0.3,
                    limitations=["Using cached news data", "May be outdated"],
                    execution_time=0.0
                )
        
        return FallbackResult(
            success=False,
            data={"articles": [], "total_results": 0},
            source="cache",
            quality_score=0.0,
            limitations=["No cached news data available"],
            execution_time=0.0
        )
    
    # Helper methods for data extraction
    def _extract_founded_date(self, content: str) -> Optional[str]:
        """Extract founding date from content"""
        import re
        patterns = [
            r'founded in (\d{4})',
            r'established in (\d{4})',
            r'founded (\d{4})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_industry(self, content: str) -> Optional[str]:
        """Extract industry from content"""
        # Simple keyword matching - could be enhanced with NLP
        industries = [
            'technology', 'software', 'hardware', 'automotive', 'finance',
            'healthcare', 'retail', 'manufacturing', 'energy', 'telecommunications'
        ]
        
        content_lower = content.lower()
        for industry in industries:
            if industry in content_lower:
                return industry.title()
        
        return None
    
    def _extract_headquarters(self, content: str) -> Optional[str]:
        """Extract headquarters location from content"""
        import re
        patterns = [
            r'headquartered in ([^.]+)',
            r'headquarters in ([^.]+)',
            r'based in ([^.]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None


    def _template_analysis_fallback(self, context: str, company_name: str) -> FallbackResult:
        """Fallback to template-based analysis"""
        try:
            # Generate template-based analysis
            analysis = {
                "brand_perception": {
                    "summary": f"Brand analysis for {company_name} is currently limited due to service unavailability.",
                    "strengths": [
                        "Established market presence",
                        "Brand recognition in target market"
                    ],
                    "opportunities": [
                        "Digital transformation initiatives",
                        "Customer engagement optimization",
                        "Market expansion potential"
                    ],
                    "recommendations": [
                        "Monitor brand performance metrics regularly",
                        "Engage with customer feedback actively",
                        "Maintain consistent brand messaging across channels"
                    ]
                },
                "competitive_analysis": {
                    "summary": "Competitive analysis requires full API access for comprehensive insights.",
                    "market_position": "Analysis pending - requires real-time data",
                    "key_differentiators": [
                        "Unique value proposition development needed",
                        "Market positioning analysis required"
                    ]
                },
                "limitations": [
                    "Analysis based on general business principles",
                    "Specific market data unavailable",
                    "Real-time competitive intelligence limited"
                ],
                "confidence_score": 0.4,
                "source": "template_analysis"
            }

            return FallbackResult(
                success=True,
                data=analysis,
                source="template_analysis",
                quality_score=0.4,
                limitations=[
                    "Generic analysis based on templates",
                    "No real-time market data",
                    "Limited competitive intelligence"
                ],
                execution_time=0.0
            )

        except Exception as e:
            return FallbackResult(
                success=False,
                data=None,
                source="template_analysis",
                quality_score=0.0,
                limitations=[f"Template analysis failed: {str(e)}"],
                execution_time=0.0
            )

    def _rule_based_analysis_fallback(self, context: str, company_name: str) -> FallbackResult:
        """Fallback to rule-based analysis"""
        try:
            # Simple rule-based analysis
            analysis = {
                "brand_health": {
                    "status": "monitoring_required",
                    "message": "Brand health assessment requires comprehensive data analysis",
                    "key_metrics": [
                        "Brand awareness tracking",
                        "Customer satisfaction monitoring",
                        "Market share analysis",
                        "Digital presence evaluation"
                    ]
                },
                "strategic_recommendations": [
                    "Implement comprehensive brand monitoring system",
                    "Establish key performance indicators (KPIs)",
                    "Develop customer feedback collection mechanisms",
                    "Create competitive analysis framework"
                ],
                "next_steps": [
                    "Restore full API connectivity for detailed analysis",
                    "Gather additional brand performance data",
                    "Schedule comprehensive brand audit when services are available"
                ],
                "confidence_score": 0.3,
                "source": "rule_based_analysis"
            }

            return FallbackResult(
                success=True,
                data=analysis,
                source="rule_based_analysis",
                quality_score=0.3,
                limitations=[
                    "Basic rule-based recommendations",
                    "No AI-powered insights",
                    "Limited personalization"
                ],
                execution_time=0.0
            )

        except Exception as e:
            return FallbackResult(
                success=False,
                data=None,
                source="rule_based_analysis",
                quality_score=0.0,
                limitations=[f"Rule-based analysis failed: {str(e)}"],
                execution_time=0.0
            )

    def _cached_analysis_fallback(self, context: str, company_name: str) -> FallbackResult:
        """Fallback to cached analysis results"""
        cache_key = f"analysis_{company_name.lower().replace(' ', '_')}"

        if cache_key in self.fallback_cache:
            cached_data = self.fallback_cache[cache_key]
            if datetime.utcnow() - cached_data['timestamp'] < timedelta(seconds=self.cache_ttl):
                return FallbackResult(
                    success=True,
                    data=cached_data['data'],
                    source="cache",
                    quality_score=0.5,
                    limitations=["Using cached analysis", "May not reflect current market conditions"],
                    execution_time=0.0
                )

        return FallbackResult(
            success=False,
            data=None,
            source="cache",
            quality_score=0.0,
            limitations=["No cached analysis available"],
            execution_time=0.0
        )

    def cache_result(self, cache_key: str, data: Any):
        """Cache a result for future fallback use"""
        self.fallback_cache[cache_key] = {
            'data': data,
            'timestamp': datetime.utcnow()
        }

        # Clean up old cache entries
        self._cleanup_cache()

    def _cleanup_cache(self):
        """Clean up expired cache entries"""
        current_time = datetime.utcnow()
        expired_keys = []

        for key, cached_data in self.fallback_cache.items():
            if current_time - cached_data['timestamp'] > timedelta(seconds=self.cache_ttl):
                expired_keys.append(key)

        for key in expired_keys:
            del self.fallback_cache[key]

    def get_fallback_quality_report(self) -> Dict[str, Any]:
        """Get a report on fallback usage and quality"""
        return {
            "cache_size": len(self.fallback_cache),
            "cache_ttl_hours": self.cache_ttl / 3600,
            "available_strategies": {
                "brand_data": ["wikipedia", "web_scraping", "cache"],
                "news_data": ["rss_feeds", "google_news", "cache"],
                "ai_analysis": ["template_analysis", "rule_based_analysis", "cache"]
            },
            "quality_scores": {
                "wikipedia": 0.7,
                "web_scraping": 0.5,
                "rss_feeds": 0.6,
                "template_analysis": 0.4,
                "rule_based_analysis": 0.3,
                "cache": 0.3
            }
        }


# Global instance
fallback_service = FallbackService()
