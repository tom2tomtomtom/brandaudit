"""
Campaign Analysis Service for Brand Audit Tool
Handles campaign discovery, creative asset collection, and advertising research
"""

import os
import json
import asyncio
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

# Import visual analysis service for creative asset processing
try:
    from .visual_analysis_service import VisualAnalysisService
    VISUAL_ANALYSIS_AVAILABLE = True
except ImportError:
    VISUAL_ANALYSIS_AVAILABLE = False
    logging.warning("Visual analysis service not available for campaign analysis")

# Import web scraping capabilities
try:
    from bs4 import BeautifulSoup
    import requests
    WEB_SCRAPING_AVAILABLE = True
except ImportError:
    WEB_SCRAPING_AVAILABLE = False
    logging.warning("Web scraping not available for campaign research")


class CampaignAnalysisService:
    """Service for campaign discovery and advertising research"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.openrouter_api_key = os.environ.get('OPENROUTER_API_KEY')
        self.news_api_key = os.environ.get('NEWS_API_KEY')
        self.visual_service = VisualAnalysisService() if VISUAL_ANALYSIS_AVAILABLE else None
        
    def get_capabilities(self) -> Dict[str, bool]:
        """Return available campaign analysis capabilities"""
        return {
            'campaign_discovery': bool(self.openrouter_api_key),
            'news_research': bool(self.news_api_key),
            'visual_analysis': VISUAL_ANALYSIS_AVAILABLE,
            'web_scraping': WEB_SCRAPING_AVAILABLE,
            'creative_asset_analysis': bool(self.visual_service)
        }
    
    async def analyze_brand_campaigns(self, brand_name: str, industry: str = None) -> Dict[str, Any]:
        """
        Main campaign analysis function
        Discovers campaigns, analyzes creative assets, and researches advertising
        """
        self.logger.info(f"Starting campaign analysis for {brand_name}")
        
        results = {
            'brand_name': brand_name,
            'industry': industry,
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'capabilities_used': self.get_capabilities(),
            'campaigns': [],
            'creative_assets': [],
            'advertising_research': {},
            'trade_press_coverage': [],
            'errors': []
        }
        
        # Step 1: Discover recent campaigns using news and AI
        if self.news_api_key or self.openrouter_api_key:
            try:
                campaigns = await self.discover_brand_campaigns(brand_name)
                results['campaigns'] = campaigns
                self.logger.info(f"Discovered {len(campaigns)} campaigns for {brand_name}")
            except Exception as e:
                error_msg = f"Campaign discovery failed: {str(e)}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
        else:
            results['errors'].append("API keys required for campaign discovery")
        
        # Step 2: Analyze creative assets for discovered campaigns
        if results['campaigns'] and self.visual_service:
            try:
                creative_assets = await self.analyze_campaign_creatives(results['campaigns'])
                results['creative_assets'] = creative_assets
                self.logger.info(f"Analyzed {len(creative_assets)} creative assets")
            except Exception as e:
                error_msg = f"Creative asset analysis failed: {str(e)}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
        
        # Step 3: Research trade press and industry coverage
        if self.news_api_key:
            try:
                trade_coverage = await self.research_trade_press_coverage(brand_name)
                results['trade_press_coverage'] = trade_coverage
                self.logger.info(f"Found {len(trade_coverage)} trade press articles")
            except Exception as e:
                error_msg = f"Trade press research failed: {str(e)}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
        
        # Step 4: Generate advertising insights using AI
        if self.openrouter_api_key and (results['campaigns'] or results['trade_press_coverage']):
            try:
                advertising_insights = await self.generate_advertising_insights(brand_name, results)
                results['advertising_research'] = advertising_insights
                self.logger.info(f"Generated advertising insights for {brand_name}")
            except Exception as e:
                error_msg = f"Advertising insights generation failed: {str(e)}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
        
        return results
    
    async def discover_brand_campaigns(self, brand_name: str) -> List[Dict[str, Any]]:
        """Discover recent brand campaigns using news API and AI analysis"""
        campaigns = []
        
        # Use News API to find campaign-related articles
        if self.news_api_key:
            try:
                news_campaigns = await self.find_campaigns_in_news(brand_name)
                campaigns.extend(news_campaigns)
            except Exception as e:
                self.logger.warning(f"News-based campaign discovery failed: {e}")
        
        # Use AI to identify known campaigns
        if self.openrouter_api_key:
            try:
                ai_campaigns = await self.identify_campaigns_with_ai(brand_name)
                campaigns.extend(ai_campaigns)
            except Exception as e:
                self.logger.warning(f"AI-based campaign discovery failed: {e}")
        
        # Remove duplicates and return top campaigns
        unique_campaigns = self.deduplicate_campaigns(campaigns)
        return unique_campaigns[:10]  # Limit to top 10 campaigns
    
    async def find_campaigns_in_news(self, brand_name: str) -> List[Dict[str, Any]]:
        """Find campaigns mentioned in news articles"""
        if not self.news_api_key:
            return []
        
        # Search for campaign-related keywords
        campaign_keywords = [
            f'"{brand_name}" campaign',
            f'"{brand_name}" advertising',
            f'"{brand_name}" marketing',
            f'"{brand_name}" commercial',
            f'"{brand_name}" launches'
        ]
        
        campaigns = []
        
        for keyword in campaign_keywords:
            try:
                # Calculate date range (last 12 months)
                end_date = datetime.now()
                start_date = end_date - timedelta(days=365)
                
                url = "https://newsapi.org/v2/everything"
                params = {
                    'q': keyword,
                    'from': start_date.strftime('%Y-%m-%d'),
                    'to': end_date.strftime('%Y-%m-%d'),
                    'sortBy': 'relevancy',
                    'pageSize': 10,
                    'apiKey': self.news_api_key
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('articles', [])
                    
                    for article in articles:
                        campaign = {
                            'title': article.get('title', ''),
                            'description': article.get('description', ''),
                            'url': article.get('url', ''),
                            'published_date': article.get('publishedAt', ''),
                            'source': article.get('source', {}).get('name', ''),
                            'discovery_method': 'news_api',
                            'search_keyword': keyword,
                            'campaign_type': self.classify_campaign_type(article.get('title', '') + ' ' + article.get('description', ''))
                        }
                        campaigns.append(campaign)
                
            except Exception as e:
                self.logger.warning(f"News search failed for keyword '{keyword}': {e}")
                continue
        
        return campaigns
    
    async def identify_campaigns_with_ai(self, brand_name: str) -> List[Dict[str, Any]]:
        """Use AI to identify known recent campaigns"""
        if not self.openrouter_api_key:
            return []
        
        prompt = f"""
        Identify recent marketing campaigns, advertising initiatives, and major launches by {brand_name} from the past 2 years.
        
        For each campaign, provide:
        1. Campaign name/title
        2. Brief description (2-3 sentences)
        3. Campaign type (product launch, brand awareness, seasonal, etc.)
        4. Approximate launch date (if known)
        5. Key messaging or theme
        6. Target audience
        7. Media channels used (TV, digital, social, print, etc.)
        
        Focus on:
        - Major advertising campaigns
        - Product launches with marketing campaigns
        - Seasonal or holiday campaigns
        - Brand repositioning efforts
        - Social responsibility campaigns
        
        Respond in JSON format:
        {{
            "campaigns": [
                {{
                    "name": "Campaign Name",
                    "description": "Brief description of the campaign",
                    "campaign_type": "product_launch|brand_awareness|seasonal|social_responsibility",
                    "launch_date": "2024-01-15",
                    "key_messaging": "Main theme or message",
                    "target_audience": "Primary target demographic",
                    "media_channels": ["TV", "Digital", "Social Media"],
                    "confidence_score": 0.9,
                    "discovery_method": "ai_analysis"
                }}
            ]
        }}
        """
        
        try:
            response = await self._call_openrouter_api(prompt)
            
            if response and 'campaigns' in response:
                return response['campaigns']
            else:
                self.logger.warning("Invalid response format from AI campaign identification")
                return []
                
        except Exception as e:
            self.logger.error(f"AI campaign identification failed: {e}")
            return []
    
    def classify_campaign_type(self, text: str) -> str:
        """Classify campaign type based on text content"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['launch', 'new', 'introducing', 'unveil']):
            return 'product_launch'
        elif any(word in text_lower for word in ['holiday', 'christmas', 'summer', 'seasonal']):
            return 'seasonal'
        elif any(word in text_lower for word in ['awareness', 'brand', 'identity', 'rebrand']):
            return 'brand_awareness'
        elif any(word in text_lower for word in ['social', 'responsibility', 'sustainability', 'cause']):
            return 'social_responsibility'
        else:
            return 'general_marketing'
    
    def deduplicate_campaigns(self, campaigns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate campaigns based on similarity"""
        if not campaigns:
            return []
        
        unique_campaigns = []
        seen_titles = set()
        
        for campaign in campaigns:
            title = campaign.get('title', campaign.get('name', '')).lower()
            
            # Simple deduplication based on title similarity
            is_duplicate = False
            for seen_title in seen_titles:
                if self.calculate_similarity(title, seen_title) > 0.7:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_campaigns.append(campaign)
                seen_titles.add(title)
        
        return unique_campaigns
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    async def analyze_campaign_creatives(self, campaigns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze creative assets from discovered campaigns"""
        if not self.visual_service:
            return []
        
        creative_assets = []
        
        for campaign in campaigns[:5]:  # Limit to first 5 campaigns
            try:
                # Try to find visual assets for the campaign
                campaign_url = campaign.get('url', '')
                if campaign_url:
                    # This would be enhanced with actual image extraction
                    # For now, we'll create placeholder analysis
                    asset_analysis = {
                        'campaign_name': campaign.get('title', campaign.get('name', 'Unknown')),
                        'campaign_url': campaign_url,
                        'analysis_timestamp': datetime.utcnow().isoformat(),
                        'visual_elements': {
                            'colors_detected': [],
                            'text_elements': [],
                            'image_style': 'unknown'
                        },
                        'analysis_method': 'placeholder'
                    }
                    creative_assets.append(asset_analysis)
                    
            except Exception as e:
                self.logger.warning(f"Creative analysis failed for campaign: {e}")
                continue
        
        return creative_assets
    
    async def research_trade_press_coverage(self, brand_name: str) -> List[Dict[str, Any]]:
        """Research trade press and industry coverage"""
        if not self.news_api_key:
            return []
        
        # Search for industry-specific coverage
        trade_keywords = [
            f'"{brand_name}" industry',
            f'"{brand_name}" market',
            f'"{brand_name}" business',
            f'"{brand_name}" strategy'
        ]
        
        trade_articles = []
        
        for keyword in trade_keywords:
            try:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=180)  # Last 6 months
                
                url = "https://newsapi.org/v2/everything"
                params = {
                    'q': keyword,
                    'from': start_date.strftime('%Y-%m-%d'),
                    'to': end_date.strftime('%Y-%m-%d'),
                    'sortBy': 'relevancy',
                    'pageSize': 5,
                    'apiKey': self.news_api_key
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('articles', [])
                    
                    for article in articles:
                        trade_article = {
                            'title': article.get('title', ''),
                            'description': article.get('description', ''),
                            'url': article.get('url', ''),
                            'published_date': article.get('publishedAt', ''),
                            'source': article.get('source', {}).get('name', ''),
                            'search_keyword': keyword,
                            'article_type': 'trade_press'
                        }
                        trade_articles.append(trade_article)
                
            except Exception as e:
                self.logger.warning(f"Trade press search failed for keyword '{keyword}': {e}")
                continue
        
        return trade_articles[:15]  # Limit to 15 articles
    
    async def generate_advertising_insights(self, brand_name: str, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate advertising insights using AI analysis"""
        if not self.openrouter_api_key:
            return {'error': 'OpenRouter API key required'}
        
        campaigns = campaign_data.get('campaigns', [])
        trade_coverage = campaign_data.get('trade_press_coverage', [])
        
        campaign_summary = json.dumps(campaigns[:5], indent=2)  # Limit data size
        coverage_summary = json.dumps(trade_coverage[:5], indent=2)
        
        prompt = f"""
        Analyze the advertising and campaign strategy for {brand_name} based on this data:
        
        Recent Campaigns:
        {campaign_summary}
        
        Trade Press Coverage:
        {coverage_summary}
        
        Provide insights on:
        1. Campaign strategy patterns and themes
        2. Media channel preferences and effectiveness
        3. Messaging consistency across campaigns
        4. Target audience analysis
        5. Campaign timing and seasonality
        6. Creative trends and visual identity
        7. Competitive positioning in campaigns
        8. Recommendations for future campaigns
        
        Respond in JSON format:
        {{
            "campaign_strategy_analysis": {{
                "dominant_themes": ["theme1", "theme2"],
                "preferred_channels": ["TV", "Digital", "Social"],
                "messaging_consistency": "high|medium|low",
                "target_audience_focus": "primary demographic"
            }},
            "creative_trends": {{
                "visual_style": "description",
                "color_preferences": ["color1", "color2"],
                "messaging_tone": "professional|casual|emotional"
            }},
            "campaign_effectiveness": {{
                "strengths": ["strength1", "strength2"],
                "opportunities": ["opportunity1", "opportunity2"],
                "recommendations": ["rec1", "rec2"]
            }}
        }}
        """
        
        try:
            response = await self._call_openrouter_api(prompt)
            return response if response else {'error': 'No response from AI analysis'}
        except Exception as e:
            return {'error': f'Advertising insights generation failed: {str(e)}'}
    
    async def _call_openrouter_api(self, prompt: str) -> Dict[str, Any]:
        """Call OpenRouter API for AI analysis"""
        if not self.openrouter_api_key:
            raise Exception("OpenRouter API key not configured")
        
        headers = {
            'Authorization': f'Bearer {self.openrouter_api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://brandaudit.app',
            'X-Title': 'AI Brand Audit Tool - Campaign Analysis'
        }
        
        data = {
            'model': 'anthropic/claude-3.5-sonnet',
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': 4000,
            'temperature': 0.7
        }
        
        try:
            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Try to parse as JSON
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    # If not JSON, return as text
                    return {'analysis': content}
            else:
                raise Exception(f"API call failed with status {response.status_code}: {response.text}")
                
        except Exception as e:
            self.logger.error(f"OpenRouter API call failed: {e}")
            raise
