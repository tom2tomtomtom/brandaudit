"""
Competitor Analysis Service for Brand Audit Tool
Handles competitor identification, analysis, and visual comparison
"""

import os
import json
import asyncio
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Import visual analysis service
try:
    from .visual_analysis_service import VisualAnalysisService
    VISUAL_ANALYSIS_AVAILABLE = True
except ImportError:
    VISUAL_ANALYSIS_AVAILABLE = False
    logging.warning("Visual analysis service not available for competitor analysis")

# Import web scraping capabilities
try:
    from bs4 import BeautifulSoup
    import requests
    WEB_SCRAPING_AVAILABLE = True
except ImportError:
    WEB_SCRAPING_AVAILABLE = False
    logging.warning("Web scraping not available for competitor research")


class CompetitorAnalysisService:
    """Service for competitor identification and analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.openrouter_api_key = os.environ.get('OPENROUTER_API_KEY')
        self.visual_service = VisualAnalysisService() if VISUAL_ANALYSIS_AVAILABLE else None
        
    def get_capabilities(self) -> Dict[str, bool]:
        """Return available competitor analysis capabilities"""
        return {
            'competitor_identification': bool(self.openrouter_api_key),
            'visual_analysis': VISUAL_ANALYSIS_AVAILABLE,
            'web_scraping': WEB_SCRAPING_AVAILABLE,
            'llm_analysis': bool(self.openrouter_api_key)
        }
    
    async def analyze_competitors(self, brand_name: str, industry: str = None) -> Dict[str, Any]:
        """
        Main competitor analysis function
        Identifies competitors and performs comprehensive analysis
        """
        self.logger.info(f"Starting competitor analysis for {brand_name}")
        
        results = {
            'brand_name': brand_name,
            'industry': industry,
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'capabilities_used': self.get_capabilities(),
            'competitors': [],
            'competitive_analysis': {},
            'errors': []
        }
        
        # Step 1: Identify competitors using AI
        if self.openrouter_api_key:
            try:
                competitors = await self.identify_competitors_with_ai(brand_name, industry)
                results['competitors'] = competitors
                self.logger.info(f"Identified {len(competitors)} competitors for {brand_name}")
            except Exception as e:
                error_msg = f"Competitor identification failed: {str(e)}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
        else:
            results['errors'].append("OpenRouter API key required for competitor identification")
        
        # Step 2: Analyze each competitor
        if results['competitors']:
            competitor_analyses = []
            for competitor in results['competitors'][:5]:  # Limit to top 5
                try:
                    analysis = await self.analyze_single_competitor(competitor)
                    competitor_analyses.append(analysis)
                    self.logger.info(f"Analyzed competitor: {competitor.get('name', 'Unknown')}")
                except Exception as e:
                    error_msg = f"Analysis failed for competitor {competitor.get('name', 'Unknown')}: {str(e)}"
                    self.logger.error(error_msg)
                    results['errors'].append(error_msg)
            
            results['competitor_analyses'] = competitor_analyses
        
        # Step 3: Generate competitive positioning analysis
        if results['competitors'] and self.openrouter_api_key:
            try:
                positioning = await self.generate_competitive_positioning(brand_name, results['competitors'])
                results['competitive_analysis'] = positioning
                self.logger.info(f"Generated competitive positioning analysis for {brand_name}")
            except Exception as e:
                error_msg = f"Competitive positioning analysis failed: {str(e)}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
        
        return results
    
    async def identify_competitors_with_ai(self, brand_name: str, industry: str = None) -> List[Dict[str, Any]]:
        """Use AI to identify direct competitors"""
        if not self.openrouter_api_key:
            return []
        
        industry_context = f" in the {industry} industry" if industry else ""
        
        prompt = f"""
        You are a senior strategy consultant conducting comprehensive competitive intelligence for {brand_name}{industry_context}.
        Identify 5-7 direct competitors and provide detailed strategic analysis suitable for C-suite decision making.

        IMPORTANT: Provide comprehensive, detailed responses with minimum 2000 characters total. Each competitor analysis should be substantial and strategic.

        For each competitor, provide comprehensive intelligence:

        **COMPETITOR IDENTIFICATION & PROFILING**
        1. Company name and primary website
        2. Strategic positioning and value proposition
        3. Market position (Market Leader/Strong Challenger/Follower/Niche Player)
        4. Estimated market share and revenue scale
        5. Geographic presence and market focus

        **COMPETITIVE STRENGTHS & VULNERABILITIES**
        6. Top 3 competitive strengths vs {brand_name}
        7. Top 3 competitive vulnerabilities vs {brand_name}
        8. Unique differentiators and competitive moats
        9. Strategic initiatives and recent moves
        10. Financial performance indicators

        **STRATEGIC THREAT ASSESSMENT**
        11. Threat level to {brand_name} (High/Medium/Low)
        12. Areas of direct competition overlap
        13. Competitive response capabilities
        14. Innovation and R&D capabilities
        15. Strategic partnerships and alliances

        Focus on competitors that pose the greatest strategic threat or opportunity for {brand_name}.
        Include both traditional competitors and emerging disruptors.

        Respond in JSON format:
        {{
            "competitors": [
                {{
                    "name": "Company Name",
                    "website": "https://example.com",
                    "strategic_positioning": "Brief strategic positioning statement",
                    "market_position": "Market Leader|Strong Challenger|Follower|Niche Player",
                    "estimated_market_share": "X% or $X billion",
                    "geographic_focus": "Global|Regional|Local markets",
                    "competitive_strengths": ["Strength 1", "Strength 2", "Strength 3"],
                    "competitive_vulnerabilities": ["Vulnerability 1", "Vulnerability 2", "Vulnerability 3"],
                    "unique_differentiators": "Key differentiating factors",
                    "recent_strategic_moves": "Recent initiatives or strategic changes",
                    "threat_level": "High|Medium|Low",
                    "competition_overlap": "Areas of direct competition",
                    "confidence_score": 0.9
                }}
            ]
        }}
        """
        
        try:
            response = await self._call_openrouter_api(prompt)
            
            # Parse JSON response
            if response and 'competitors' in response:
                return response['competitors']
            else:
                self.logger.warning("Invalid response format from competitor identification")
                return []
                
        except Exception as e:
            self.logger.error(f"AI competitor identification failed: {e}")
            return []
    
    async def analyze_single_competitor(self, competitor: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single competitor comprehensively with smart fallbacks"""
        competitor_name = competitor.get('name', 'Unknown')
        website_url = competitor.get('website', '')

        analysis = {
            'competitor_info': competitor,
            'visual_analysis': {},
            'web_analysis': {},
            'fallback_analysis': {},
            'data_sources_used': [],
            'analysis_timestamp': datetime.utcnow().isoformat()
        }

        # Strategy 1: Try website analysis (fast timeout)
        website_success = False
        if website_url and self.visual_service:
            try:
                visual_results = await self.visual_service.analyze_brand_visuals(competitor_name, website_url)
                analysis['visual_analysis'] = visual_results
                analysis['data_sources_used'].append('website_visual')
                website_success = True
                self.logger.info(f"✅ Website visual analysis completed for {competitor_name}")
            except Exception as e:
                self.logger.warning(f"⚠️ Website visual analysis failed for {competitor_name}: {e}")

        if website_url and WEB_SCRAPING_AVAILABLE and not website_success:
            try:
                web_analysis = await self.analyze_competitor_website(website_url)
                analysis['web_analysis'] = web_analysis
                analysis['data_sources_used'].append('website_content')
                website_success = True
                self.logger.info(f"✅ Website content analysis completed for {competitor_name}")
            except Exception as e:
                self.logger.warning(f"⚠️ Website content analysis failed for {competitor_name}: {e}")

        # Strategy 2: Wikipedia fallback
        if not website_success:
            try:
                wikipedia_data = await self.get_wikipedia_info(competitor_name)
                if wikipedia_data:
                    analysis['fallback_analysis']['wikipedia'] = wikipedia_data
                    analysis['data_sources_used'].append('wikipedia')
                    self.logger.info(f"✅ Wikipedia fallback successful for {competitor_name}")
            except Exception as e:
                self.logger.warning(f"⚠️ Wikipedia fallback failed for {competitor_name}: {e}")

        # Strategy 3: LLM knowledge fallback (always try this for rich data)
        try:
            llm_analysis = await self.get_llm_competitor_analysis(competitor_name)
            if llm_analysis:
                analysis['fallback_analysis']['llm_knowledge'] = llm_analysis
                analysis['data_sources_used'].append('llm_knowledge')
                self.logger.info(f"✅ LLM knowledge analysis completed for {competitor_name}")
        except Exception as e:
            self.logger.warning(f"⚠️ LLM analysis failed for {competitor_name}: {e}")

        # Ensure we always have some data
        if not analysis['data_sources_used']:
            analysis['fallback_analysis']['basic_info'] = {
                'name': competitor_name,
                'website': website_url,
                'note': 'Limited data available - all sources failed'
            }
            analysis['data_sources_used'].append('basic_info')

        return analysis
    
    async def analyze_competitor_website(self, website_url: str) -> Dict[str, Any]:
        """Analyze competitor website content"""
        if not WEB_SCRAPING_AVAILABLE:
            return {'error': 'Web scraping not available'}
        
        try:
            response = requests.get(website_url, timeout=5, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract key information
            analysis = {
                'title': soup.title.string if soup.title else '',
                'meta_description': '',
                'headings': [],
                'key_messages': [],
                'navigation_items': [],
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
            # Meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                analysis['meta_description'] = meta_desc.get('content', '')
            
            # Headings
            for tag in ['h1', 'h2', 'h3']:
                headings = soup.find_all(tag)
                for heading in headings[:5]:  # Limit to first 5 of each type
                    text = heading.get_text().strip()
                    if text:
                        analysis['headings'].append({
                            'level': tag,
                            'text': text
                        })
            
            # Navigation items
            nav_elements = soup.find_all(['nav', 'ul', 'ol'])
            for nav in nav_elements[:3]:  # Limit to first 3 navigation elements
                links = nav.find_all('a')
                for link in links[:10]:  # Limit to 10 links per nav
                    link_text = link.get_text().strip()
                    if link_text and len(link_text) < 50:  # Reasonable link text length
                        analysis['navigation_items'].append(link_text)
            
            return analysis
            
        except Exception as e:
            return {'error': f'Website analysis failed: {str(e)}'}
    
    async def generate_competitive_positioning(self, brand_name: str, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate competitive positioning analysis using AI"""
        if not self.openrouter_api_key:
            return {'error': 'OpenRouter API key required'}
        
        competitor_names = [comp.get('name', 'Unknown') for comp in competitors]
        competitor_info = json.dumps(competitors, indent=2)
        
        prompt = f"""
        You are a senior partner at McKinsey & Company conducting a comprehensive competitive landscape analysis for {brand_name}.
        Create a strategic competitive intelligence report suitable for C-suite decision making and board presentations.

        COMPETITOR DATA:
        {competitor_info}

        Provide a comprehensive competitive analysis structured as follows:

        ## COMPETITIVE LANDSCAPE OVERVIEW
        - Industry structure and competitive dynamics
        - Market concentration and fragmentation analysis
        - Competitive intensity assessment (Porter's Five Forces perspective)
        - Barriers to entry and competitive moats

        ## STRATEGIC GROUP ANALYSIS
        - Primary strategic groups in the market
        - {brand_name}'s strategic group positioning
        - Mobility barriers between groups
        - Strategic group evolution trends

        ## COMPETITIVE POSITIONING MATRIX
        Multi-dimensional positioning analysis on key strategic dimensions:
        - Innovation Leadership vs Market Execution
        - Premium Positioning vs Value Positioning
        - Global Reach vs Local Focus
        - Digital Transformation vs Traditional Operations
        - Customer Experience vs Operational Efficiency

        ## COMPETITOR STRATEGIC PROFILES
        For each major competitor, provide:
        - Strategic intent and business model
        - Competitive advantages and core competencies
        - Strategic vulnerabilities and blind spots
        - Recent strategic moves and future direction
        - Financial performance and investment capacity
        - Threat level assessment to {brand_name}

        ## COMPETITIVE DYNAMICS ANALYSIS
        - Head-to-head competitive battles
        - Competitive response patterns
        - Market share dynamics and trends
        - Pricing strategies and competitive pricing
        - Innovation cycles and R&D competition

        ## MARKET OPPORTUNITIES & WHITE SPACES
        - Underserved market segments
        - Emerging customer needs
        - Technology disruption opportunities
        - Geographic expansion opportunities
        - Partnership and acquisition targets

        ## STRATEGIC RECOMMENDATIONS FOR {brand_name}
        Provide 7-10 strategic recommendations with:
        - Strategic rationale and competitive logic
        - Implementation priority (High/Medium/Low)
        - Expected competitive impact
        - Resource requirements and timeline
        - Success metrics and KPIs
        - Risk mitigation strategies

        CRITICAL OUTPUT REQUIREMENTS:
        - Respond in MARKDOWN format (NOT JSON) with detailed strategic insights
        - Minimum 2500 characters total content
        - Use professional consulting language and frameworks
        - Include specific data points and strategic analysis

        EXAMPLE OUTPUT FORMAT:
        {{
            "competitive_landscape": {{
                "industry_structure": "Detailed industry structure analysis",
                "competitive_intensity": "High|Medium|Low with rationale",
                "market_concentration": "Concentrated|Fragmented with analysis",
                "barriers_to_entry": ["Barrier 1", "Barrier 2", "Barrier 3"]
            }},
            "strategic_groups": {{
                "primary_groups": [
                    {{
                        "group_name": "Premium Leaders",
                        "members": ["Brand1", "Brand2"],
                        "characteristics": "Key characteristics",
                        "competitive_dynamics": "Internal competition patterns"
                    }}
                ],
                "{brand_name.lower()}_positioning": "Strategic group and positioning analysis"
            }},
            "positioning_matrix": {{
                "dimensions": ["innovation_leadership", "market_execution", "premium_positioning", "global_reach", "digital_transformation"],
                "brand_positions": {{
                    "{brand_name}": {{"innovation_leadership": 0.8, "market_execution": 0.9, "premium_positioning": 0.9, "global_reach": 0.8, "digital_transformation": 0.7}},
                    "competitor_scores": "Detailed competitor positioning scores"
                }},
                "strategic_implications": "Key insights from positioning analysis"
            }},
            "competitor_profiles": [
                {{
                    "name": "Competitor Name",
                    "strategic_intent": "Strategic direction and business model",
                    "competitive_advantages": ["Advantage 1", "Advantage 2", "Advantage 3"],
                    "strategic_vulnerabilities": ["Vulnerability 1", "Vulnerability 2"],
                    "recent_moves": "Recent strategic initiatives",
                    "threat_level": "High|Medium|Low",
                    "competitive_response_capability": "Assessment of response speed and effectiveness"
                }}
            ],
            "market_opportunities": {{
                "underserved_segments": ["Segment 1", "Segment 2"],
                "emerging_needs": ["Need 1", "Need 2"],
                "white_spaces": ["Opportunity 1", "Opportunity 2"],
                "disruption_potential": "Areas ripe for disruption"
            }},
            "strategic_recommendations": [
                {{
                    "recommendation": "Strategic recommendation title",
                    "rationale": "Detailed strategic rationale and competitive logic",
                    "priority": "High|Medium|Low",
                    "competitive_impact": "Expected impact on competitive position",
                    "implementation_timeline": "Specific timeline",
                    "resource_requirements": "Investment and resource needs",
                    "success_metrics": ["KPI 1", "KPI 2"],
                    "risk_factors": ["Risk 1", "Risk 2"]
                }}
            ]
        }}
        """
        
        try:
            response = await self._call_openrouter_api(prompt)
            return response if response else {'error': 'No response from AI analysis'}
        except Exception as e:
            return {'error': f'Competitive positioning analysis failed: {str(e)}'}
    
    async def _call_openrouter_api(self, prompt: str) -> Dict[str, Any]:
        """Call OpenRouter API for AI analysis"""
        if not self.openrouter_api_key:
            raise Exception("OpenRouter API key not configured")
        
        headers = {
            'Authorization': f'Bearer {self.openrouter_api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://brandaudit.app',
            'X-Title': 'AI Brand Audit Tool - Competitor Analysis'
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

    async def get_wikipedia_info(self, competitor_name: str) -> Dict[str, Any]:
        """Get competitor info from Wikipedia as fallback"""
        try:
            # Simple Wikipedia API call
            search_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{competitor_name.replace(' ', '_')}"
            response = requests.get(search_url, timeout=5)

            if response.status_code == 200:
                data = response.json()
                return {
                    'title': data.get('title', ''),
                    'description': data.get('extract', ''),
                    'url': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                    'source': 'wikipedia'
                }
            else:
                # Try search if direct lookup fails
                search_api = f"https://en.wikipedia.org/api/rest_v1/page/summary/{competitor_name.replace(' ', '%20')}"
                response = requests.get(search_api, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    return {
                        'title': data.get('title', ''),
                        'description': data.get('extract', ''),
                        'url': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                        'source': 'wikipedia'
                    }
        except Exception as e:
            self.logger.warning(f"Wikipedia lookup failed for {competitor_name}: {e}")

        return None

    async def get_llm_competitor_analysis(self, competitor_name: str) -> Dict[str, Any]:
        """Get comprehensive competitor analysis using LLM knowledge"""
        if not self.openrouter_api_key:
            return None

        try:
            prompt = f"""Provide a comprehensive analysis of {competitor_name} as a competitor. Include:

1. COMPANY OVERVIEW:
   - Industry and market position
   - Founded year and headquarters
   - Key products/services
   - Target market and customer base

2. BUSINESS MODEL:
   - Revenue streams
   - Pricing strategy
   - Distribution channels
   - Key partnerships

3. BRAND POSITIONING:
   - Brand values and messaging
   - Unique selling propositions
   - Brand personality and tone
   - Visual identity characteristics

4. COMPETITIVE STRENGTHS:
   - Market advantages
   - Technology/innovation edge
   - Customer loyalty factors
   - Operational excellence areas

5. POTENTIAL WEAKNESSES:
   - Market vulnerabilities
   - Customer pain points
   - Competitive gaps
   - Areas for improvement

6. RECENT DEVELOPMENTS:
   - New product launches
   - Strategic initiatives
   - Market expansion
   - Notable campaigns or partnerships

Provide specific, factual information based on your knowledge. If certain details are unknown, indicate that clearly."""

            headers = {
                'Authorization': f'Bearer {self.openrouter_api_key}',
                'Content-Type': 'application/json'
            }

            data = {
                'model': 'openai/gpt-4-turbo',
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are a business intelligence analyst providing factual competitor analysis. Be specific and accurate.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': 2000,
                'temperature': 0.3
            }

            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                analysis_text = result['choices'][0]['message']['content']

                return {
                    'analysis': analysis_text,
                    'source': 'llm_knowledge',
                    'model': 'gpt-4-turbo',
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                self.logger.error(f"LLM analysis failed: {response.status_code}")

        except Exception as e:
            self.logger.error(f"LLM competitor analysis failed for {competitor_name}: {e}")

        return None
