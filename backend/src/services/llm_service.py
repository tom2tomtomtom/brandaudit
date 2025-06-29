import requests
import json
import os
from typing import Dict, List, Optional
from datetime import datetime

class LLMService:
    """Service for integrating with various LLM APIs"""
    
    def __init__(self):
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.openrouter_base_url = 'https://openrouter.ai/api/v1'
        self.default_model = 'anthropic/claude-3-haiku'
        
    def analyze_brand_sentiment(self, text_content: str, brand_name: str) -> Dict:
        """Analyze brand sentiment from text content"""
        prompt = f"""
        Analyze the sentiment and brand perception for "{brand_name}" in the following text content.
        
        Text content:
        {text_content}
        
        Please provide:
        1. Overall sentiment (positive, negative, neutral)
        2. Sentiment score (0-100)
        3. Key themes and topics mentioned
        4. Brand perception indicators
        5. Specific quotes that support the sentiment analysis
        
        Return the analysis in JSON format.
        """
        
        try:
            response = self._call_llm(prompt, max_tokens=1000)
            return {
                'success': True,
                'analysis': response,
                'processed_at': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processed_at': datetime.utcnow().isoformat()
            }
    
    def analyze_competitive_landscape(self, brand_name: str, competitor_data: List[Dict]) -> Dict:
        """Analyze competitive landscape and positioning"""
        competitors_text = "\n".join([
            f"- {comp.get('name', 'Unknown')}: {comp.get('description', 'No description')}"
            for comp in competitor_data
        ])
        
        prompt = f"""
        Analyze the competitive landscape for "{brand_name}" given the following competitor information:
        
        Competitors:
        {competitors_text}
        
        Please provide:
        1. Market positioning analysis
        2. Competitive advantages and disadvantages
        3. Market share estimation
        4. Differentiation opportunities
        5. Strategic recommendations
        
        Return the analysis in JSON format.
        """
        
        try:
            response = self._call_llm(prompt, max_tokens=1500)
            return {
                'success': True,
                'analysis': response,
                'processed_at': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processed_at': datetime.utcnow().isoformat()
            }
    
    def generate_brand_insights(self, brand_data: Dict) -> Dict:
        """Generate comprehensive brand insights"""
        prompt = f"""
        Generate comprehensive brand insights for the following brand data:
        
        Brand Information:
        - Name: {brand_data.get('name', 'Unknown')}
        - Industry: {brand_data.get('industry', 'Unknown')}
        - Description: {brand_data.get('description', 'No description')}
        - Founded: {brand_data.get('founded', 'Unknown')}
        - Website: {brand_data.get('website', 'Unknown')}
        
        News Mentions: {len(brand_data.get('news_articles', []))} articles
        Social Media Mentions: {brand_data.get('social_mentions', 0)} mentions
        
        Please provide:
        1. Brand strength assessment
        2. Market presence evaluation
        3. Brand perception summary
        4. Growth opportunities
        5. Risk factors
        6. Strategic recommendations
        
        Return the insights in JSON format with specific scores and actionable recommendations.
        """
        
        try:
            response = self._call_llm(prompt, max_tokens=2000)
            return {
                'success': True,
                'insights': response,
                'processed_at': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processed_at': datetime.utcnow().isoformat()
            }
    
    def generate_executive_summary(self, analysis_data: Dict) -> Dict:
        """Generate executive summary from analysis data"""
        prompt = f"""
        Create an executive summary for a brand audit based on the following analysis data:
        
        Analysis Data:
        {json.dumps(analysis_data, indent=2)}
        
        Please provide:
        1. Executive summary (2-3 paragraphs)
        2. Key findings (bullet points)
        3. Critical recommendations (prioritized)
        4. Overall brand health score (0-100)
        5. Next steps
        
        The summary should be professional, concise, and actionable for C-level executives.
        Return in JSON format.
        """
        
        try:
            response = self._call_llm(prompt, max_tokens=1500)
            return {
                'success': True,
                'summary': response,
                'generated_at': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'generated_at': datetime.utcnow().isoformat()
            }
    
    def analyze_visual_brand_consistency(self, visual_assets: List[Dict]) -> Dict:
        """Analyze visual brand consistency from uploaded assets"""
        assets_description = "\n".join([
            f"- {asset.get('type', 'unknown')}: {asset.get('filename', 'unknown')} "
            f"({asset.get('size', 'unknown')} bytes)"
            for asset in visual_assets
        ])
        
        prompt = f"""
        Analyze visual brand consistency based on the following uploaded assets:
        
        Visual Assets:
        {assets_description}
        
        Please provide:
        1. Visual consistency score (0-100)
        2. Brand guideline compliance assessment
        3. Color palette analysis
        4. Typography consistency
        5. Logo usage evaluation
        6. Recommendations for improvement
        
        Note: This is based on file metadata. For actual visual analysis, 
        computer vision models would be needed.
        
        Return the analysis in JSON format.
        """
        
        try:
            response = self._call_llm(prompt, max_tokens=1000)
            return {
                'success': True,
                'analysis': response,
                'processed_at': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processed_at': datetime.utcnow().isoformat()
            }
    
    def _call_llm(self, prompt: str, max_tokens: int = 1000, model: str = None) -> str:
        """Make API call to LLM service"""
        if not self.openrouter_api_key:
            # Return mock response if no API key is configured
            return self._get_mock_response(prompt)
        
        headers = {
            'Authorization': f'Bearer {self.openrouter_api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://brand-audit-tool.com',
            'X-Title': 'Brand Audit Tool'
        }
        
        data = {
            'model': model or self.default_model,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': max_tokens,
            'temperature': 0.7
        }
        
        response = requests.post(
            f'{self.openrouter_base_url}/chat/completions',
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            raise Exception(f"LLM API error: {response.status_code} - {response.text}")
    
    def _get_mock_response(self, prompt: str) -> str:
        """Return mock response when API key is not configured"""
        if "sentiment" in prompt.lower():
            return json.dumps({
                "overall_sentiment": "positive",
                "sentiment_score": 78,
                "key_themes": ["innovation", "customer satisfaction", "market leadership"],
                "brand_perception": "strong and positive",
                "supporting_quotes": ["Leading innovation in the industry", "Excellent customer service"]
            })
        elif "competitive" in prompt.lower():
            return json.dumps({
                "market_position": "strong leader",
                "competitive_advantages": ["innovation", "brand recognition", "customer loyalty"],
                "market_share_estimate": "25-30%",
                "differentiation_opportunities": ["emerging markets", "new product categories"],
                "recommendations": ["maintain innovation leadership", "expand market presence"]
            })
        elif "insights" in prompt.lower():
            return json.dumps({
                "brand_strength_score": 82,
                "market_presence": "strong",
                "brand_perception": "positive",
                "growth_opportunities": ["digital transformation", "international expansion"],
                "risk_factors": ["increased competition", "market saturation"],
                "recommendations": ["invest in digital capabilities", "strengthen customer relationships"]
            })
        elif "executive" in prompt.lower():
            return json.dumps({
                "executive_summary": "The brand demonstrates strong market presence with positive sentiment and consistent visual identity. Key opportunities exist in digital transformation and market expansion.",
                "key_findings": ["Strong brand recognition", "Positive customer sentiment", "Consistent visual identity"],
                "recommendations": ["Invest in digital capabilities", "Expand market presence", "Strengthen customer engagement"],
                "brand_health_score": 78,
                "next_steps": ["Develop digital strategy", "Conduct market research", "Implement brand guidelines"]
            })
        elif "visual" in prompt.lower():
            return json.dumps({
                "visual_consistency_score": 85,
                "brand_compliance": "good",
                "color_palette": "consistent primary colors",
                "typography": "consistent font usage",
                "logo_usage": "proper implementation",
                "recommendations": ["standardize color codes", "create style guide", "ensure consistent application"]
            })
        else:
            return json.dumps({
                "analysis": "Mock analysis response",
                "score": 75,
                "recommendations": ["Continue current strategy", "Monitor market trends"]
            })

# Global instance
llm_service = LLMService()

