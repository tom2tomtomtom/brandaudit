"""
Social Media Analysis Service for Brand Audit Tool
Handles social media metrics, engagement analysis, and social sentiment
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

# Import web scraping for social media data
try:
    from bs4 import BeautifulSoup
    import requests
    WEB_SCRAPING_AVAILABLE = True
except ImportError:
    WEB_SCRAPING_AVAILABLE = False
    logging.warning("Web scraping not available for social media analysis")


class SocialMediaService:
    """Service for social media analysis and engagement metrics"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.openrouter_api_key = os.environ.get('OPENROUTER_API_KEY')
        
        # Social media API keys (if available)
        self.twitter_bearer_token = os.environ.get('TWITTER_BEARER_TOKEN')
        self.instagram_access_token = os.environ.get('INSTAGRAM_ACCESS_TOKEN')
        self.linkedin_access_token = os.environ.get('LINKEDIN_ACCESS_TOKEN')
        
    def get_capabilities(self) -> Dict[str, bool]:
        """Return available social media analysis capabilities"""
        return {
            'twitter_api': bool(self.twitter_bearer_token),
            'instagram_api': bool(self.instagram_access_token),
            'linkedin_api': bool(self.linkedin_access_token),
            'web_scraping': WEB_SCRAPING_AVAILABLE,
            'ai_analysis': bool(self.openrouter_api_key),
            'social_sentiment': bool(self.openrouter_api_key)
        }
    
    async def analyze_social_presence(self, brand_name: str, website_url: str = None) -> Dict[str, Any]:
        """
        Main social media analysis function
        Analyzes social media presence, engagement, and sentiment
        """
        self.logger.info(f"Starting social media analysis for {brand_name}")
        
        results = {
            'brand_name': brand_name,
            'website_url': website_url,
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'capabilities_used': self.get_capabilities(),
            'social_platforms': {},
            'engagement_metrics': {},
            'social_sentiment': {},
            'social_insights': {},
            'errors': []
        }
        
        # Step 1: Discover social media accounts
        if website_url and WEB_SCRAPING_AVAILABLE:
            try:
                social_accounts = await self.discover_social_accounts(website_url)
                results['social_platforms'] = social_accounts
                self.logger.info(f"Discovered {len(social_accounts)} social platforms for {brand_name}")
            except Exception as e:
                error_msg = f"Social account discovery failed: {str(e)}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
        
        # Step 2: Analyze engagement metrics (placeholder for API integration)
        try:
            engagement_metrics = await self.analyze_engagement_metrics(brand_name, results['social_platforms'])
            results['engagement_metrics'] = engagement_metrics
            self.logger.info(f"Analyzed engagement metrics for {brand_name}")
        except Exception as e:
            error_msg = f"Engagement analysis failed: {str(e)}"
            self.logger.error(error_msg)
            results['errors'].append(error_msg)
        
        # Step 3: Generate social insights using AI
        if self.openrouter_api_key and results['social_platforms']:
            try:
                social_insights = await self.generate_social_insights(brand_name, results)
                results['social_insights'] = social_insights
                self.logger.info(f"Generated social insights for {brand_name}")
            except Exception as e:
                error_msg = f"Social insights generation failed: {str(e)}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
        
        return results
    
    async def discover_social_accounts(self, website_url: str) -> Dict[str, Any]:
        """Discover social media accounts from website"""
        if not WEB_SCRAPING_AVAILABLE:
            return {}
        
        social_platforms = {
            'twitter': None,
            'instagram': None,
            'linkedin': None,
            'facebook': None,
            'youtube': None,
            'tiktok': None
        }
        
        try:
            response = requests.get(website_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for social media links
            social_patterns = {
                'twitter': ['twitter.com', 'x.com'],
                'instagram': ['instagram.com'],
                'linkedin': ['linkedin.com'],
                'facebook': ['facebook.com'],
                'youtube': ['youtube.com'],
                'tiktok': ['tiktok.com']
            }
            
            # Find all links
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href', '').lower()
                for platform, patterns in social_patterns.items():
                    for pattern in patterns:
                        if pattern in href and not social_platforms[platform]:
                            # Extract username/handle if possible
                            username = self.extract_social_username(href, platform)
                            social_platforms[platform] = {
                                'url': href if href.startswith('http') else f"https://{href}",
                                'username': username,
                                'discovered_method': 'website_scraping'
                            }
                            break
            
            # Remove None values
            social_platforms = {k: v for k, v in social_platforms.items() if v is not None}
            
            return social_platforms
            
        except Exception as e:
            self.logger.error(f"Social account discovery failed: {e}")
            return {}
    
    def extract_social_username(self, url: str, platform: str) -> str:
        """Extract username from social media URL"""
        try:
            # Remove protocol and www
            clean_url = url.replace('https://', '').replace('http://', '').replace('www.', '')
            
            if platform == 'twitter':
                # Extract from twitter.com/username or x.com/username
                if 'twitter.com/' in clean_url:
                    username = clean_url.split('twitter.com/')[-1].split('/')[0].split('?')[0]
                elif 'x.com/' in clean_url:
                    username = clean_url.split('x.com/')[-1].split('/')[0].split('?')[0]
                else:
                    return 'unknown'
                return f"@{username}" if username and not username.startswith('@') else username
            
            elif platform == 'instagram':
                if 'instagram.com/' in clean_url:
                    username = clean_url.split('instagram.com/')[-1].split('/')[0].split('?')[0]
                    return f"@{username}" if username and not username.startswith('@') else username
            
            elif platform == 'linkedin':
                if 'linkedin.com/company/' in clean_url:
                    username = clean_url.split('linkedin.com/company/')[-1].split('/')[0].split('?')[0]
                    return username
                elif 'linkedin.com/in/' in clean_url:
                    username = clean_url.split('linkedin.com/in/')[-1].split('/')[0].split('?')[0]
                    return username
            
            # For other platforms, try to extract the path
            parts = clean_url.split('/')
            if len(parts) > 1:
                return parts[1].split('?')[0]
            
            return 'unknown'
            
        except Exception:
            return 'unknown'
    
    async def analyze_engagement_metrics(self, brand_name: str, social_platforms: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze engagement metrics (placeholder for API integration)"""
        
        # This would integrate with actual social media APIs
        # For now, we'll create a structure for the metrics
        
        engagement_data = {
            'platforms_analyzed': len(social_platforms),
            'total_followers': 0,
            'engagement_rates': {},
            'content_performance': {},
            'analysis_method': 'placeholder'
        }
        
        # Placeholder metrics for each discovered platform
        for platform, account_info in social_platforms.items():
            engagement_data['engagement_rates'][platform] = {
                'followers': 'API_REQUIRED',
                'engagement_rate': 'API_REQUIRED',
                'posts_per_week': 'API_REQUIRED',
                'account_url': account_info.get('url', ''),
                'username': account_info.get('username', 'unknown')
            }
        
        return engagement_data
    
    async def generate_social_insights(self, brand_name: str, social_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate social media insights using AI"""
        if not self.openrouter_api_key:
            return {'error': 'OpenRouter API key required'}
        
        social_platforms = social_data.get('social_platforms', {})
        engagement_metrics = social_data.get('engagement_metrics', {})
        
        platforms_summary = json.dumps(social_platforms, indent=2)
        
        prompt = f"""
        Analyze the social media presence for {brand_name} based on this data:
        
        Social Platforms Discovered:
        {platforms_summary}
        
        Provide insights on:
        1. Social media platform strategy and presence
        2. Platform selection effectiveness for the brand
        3. Social media branding consistency
        4. Opportunities for social media growth
        5. Competitive social media positioning
        6. Content strategy recommendations
        7. Engagement optimization suggestions
        
        Respond in JSON format:
        {{
            "social_strategy_analysis": {{
                "platform_coverage": "comprehensive|moderate|limited",
                "platform_selection": ["platform1", "platform2"],
                "branding_consistency": "high|medium|low",
                "content_strategy": "description"
            }},
            "opportunities": {{
                "missing_platforms": ["platform1", "platform2"],
                "engagement_improvements": ["improvement1", "improvement2"],
                "content_recommendations": ["rec1", "rec2"]
            }},
            "competitive_positioning": {{
                "strengths": ["strength1", "strength2"],
                "weaknesses": ["weakness1", "weakness2"],
                "recommendations": ["rec1", "rec2"]
            }}
        }}
        """
        
        try:
            response = await self._call_openrouter_api(prompt)
            return response if response else {'error': 'No response from AI analysis'}
        except Exception as e:
            return {'error': f'Social insights generation failed: {str(e)}'}
    
    async def _call_openrouter_api(self, prompt: str) -> Dict[str, Any]:
        """Call OpenRouter API for AI analysis"""
        if not self.openrouter_api_key:
            raise Exception("OpenRouter API key not configured")
        
        headers = {
            'Authorization': f'Bearer {self.openrouter_api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://brandaudit.app',
            'X-Title': 'AI Brand Audit Tool - Social Media Analysis'
        }
        
        data = {
            'model': 'anthropic/claude-3.5-sonnet',
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': 3000,
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
