"""
Strategic Synthesis Service for Brand Audit Tool
Handles competitive positioning, gap analysis, and strategic recommendations
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging


class StrategicSynthesisService:
    """Service for strategic analysis and synthesis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.openrouter_api_key = os.environ.get('OPENROUTER_API_KEY')
        
    def get_capabilities(self) -> Dict[str, bool]:
        """Return available strategic synthesis capabilities"""
        return {
            'competitive_positioning': bool(self.openrouter_api_key),
            'gap_analysis': bool(self.openrouter_api_key),
            'strategic_recommendations': bool(self.openrouter_api_key),
            'opportunity_mapping': bool(self.openrouter_api_key)
        }
    
    async def generate_strategic_synthesis(self, brand_name: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main strategic synthesis function
        Generates competitive positioning, gap analysis, and strategic recommendations
        """
        self.logger.info(f"Starting strategic synthesis for {brand_name}")
        
        results = {
            'brand_name': brand_name,
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'capabilities_used': self.get_capabilities(),
            'competitive_positioning_matrix': {},
            'brand_gap_analysis': {},
            'strategic_opportunities': {},
            'implementation_roadmap': {},
            'strategic_recommendations': [],
            'errors': []
        }
        
        # Step 1: Generate competitive positioning matrix
        if self.openrouter_api_key:
            try:
                positioning_matrix = await self.create_positioning_matrix(brand_name, analysis_data)
                results['competitive_positioning_matrix'] = positioning_matrix
                self.logger.info(f"Generated positioning matrix for {brand_name}")
            except Exception as e:
                error_msg = f"Positioning matrix generation failed: {str(e)}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
        
        # Step 2: Conduct brand gap analysis
        if self.openrouter_api_key:
            try:
                gap_analysis = await self.analyze_brand_gaps(brand_name, analysis_data)
                results['brand_gap_analysis'] = gap_analysis
                self.logger.info(f"Completed gap analysis for {brand_name}")
            except Exception as e:
                error_msg = f"Gap analysis failed: {str(e)}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
        
        # Step 3: Map strategic opportunities
        if self.openrouter_api_key:
            try:
                opportunities = await self.map_strategic_opportunities(brand_name, analysis_data)
                results['strategic_opportunities'] = opportunities
                self.logger.info(f"Mapped strategic opportunities for {brand_name}")
            except Exception as e:
                error_msg = f"Opportunity mapping failed: {str(e)}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
        
        # Step 4: Generate implementation roadmap
        if self.openrouter_api_key and results['strategic_opportunities']:
            try:
                roadmap = await self.create_implementation_roadmap(brand_name, results)
                results['implementation_roadmap'] = roadmap
                self.logger.info(f"Created implementation roadmap for {brand_name}")
            except Exception as e:
                error_msg = f"Roadmap generation failed: {str(e)}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
        
        # Step 5: Synthesize strategic recommendations
        if self.openrouter_api_key:
            try:
                recommendations = await self.synthesize_recommendations(brand_name, results)
                results['strategic_recommendations'] = recommendations
                self.logger.info(f"Synthesized strategic recommendations for {brand_name}")
            except Exception as e:
                error_msg = f"Recommendation synthesis failed: {str(e)}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
        
        return results
    
    async def create_positioning_matrix(self, brand_name: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create competitive positioning matrix"""
        if not self.openrouter_api_key:
            return {'error': 'OpenRouter API key required'}
        
        # Extract relevant data
        competitors = analysis_data.get('competitor_analysis', {}).get('competitors_identified', {}).get('competitors', [])
        visual_data = analysis_data.get('visual_analysis', {})
        brand_scores = analysis_data.get('key_metrics', {})
        
        competitors_summary = json.dumps(competitors[:5], indent=2)
        visual_summary = json.dumps({
            'color_consistency': visual_data.get('visual_scores', {}).get('color_consistency', 0),
            'visual_quality': visual_data.get('visual_scores', {}).get('overall_visual_score', 0)
        }, indent=2)
        
        prompt = f"""
        Create a comprehensive competitive positioning matrix for {brand_name} based on this analysis:
        
        Brand Scores: {brand_scores}
        Visual Analysis: {visual_summary}
        Competitors: {competitors_summary}
        
        Generate a positioning matrix with these dimensions:
        1. Innovation vs Tradition (0-100 scale)
        2. Premium vs Value (0-100 scale)
        3. Global vs Local (0-100 scale)
        4. Digital vs Physical (0-100 scale)
        
        For each brand (target + competitors), provide:
        - Position on each dimension (0-100)
        - Quadrant classification
        - Competitive advantages
        - Market positioning summary
        
        Also include:
        - Market gaps and white spaces
        - Positioning recommendations
        - Competitive threats and opportunities
        
        Respond in JSON format:
        {{
            "positioning_matrix": {{
                "dimensions": ["innovation_tradition", "premium_value", "global_local", "digital_physical"],
                "brand_positions": {{
                    "{brand_name}": {{
                        "innovation_tradition": 75,
                        "premium_value": 85,
                        "global_local": 90,
                        "digital_physical": 80,
                        "quadrant": "Premium Innovator",
                        "competitive_advantages": ["advantage1", "advantage2"]
                    }}
                }},
                "market_gaps": [
                    {{"gap": "Affordable Innovation", "opportunity_score": 85}},
                    {{"gap": "Local Premium", "opportunity_score": 70}}
                ],
                "positioning_insights": {{
                    "current_position": "description",
                    "competitive_threats": ["threat1", "threat2"],
                    "positioning_opportunities": ["opp1", "opp2"],
                    "recommended_moves": ["move1", "move2"]
                }}
            }}
        }}
        """
        
        try:
            response = await self._call_openrouter_api(prompt)
            return response if response else {'error': 'No response from positioning analysis'}
        except Exception as e:
            return {'error': f'Positioning matrix generation failed: {str(e)}'}
    
    async def analyze_brand_gaps(self, brand_name: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze brand gaps and weaknesses"""
        if not self.openrouter_api_key:
            return {'error': 'OpenRouter API key required'}
        
        # Extract comprehensive data for gap analysis
        visual_scores = analysis_data.get('visual_analysis', {}).get('visual_scores', {})
        competitor_data = analysis_data.get('competitor_analysis', {})
        campaign_data = analysis_data.get('campaign_analysis', {})
        brand_scores = analysis_data.get('key_metrics', {})
        
        analysis_summary = json.dumps({
            'brand_scores': brand_scores,
            'visual_scores': visual_scores,
            'competitor_count': len(competitor_data.get('competitors_identified', {}).get('competitors', [])),
            'campaign_count': len(campaign_data.get('campaigns_discovered', {}).get('campaigns', []))
        }, indent=2)
        
        prompt = f"""
        Conduct a comprehensive brand gap analysis for {brand_name} based on this data:
        
        Analysis Data: {analysis_summary}
        
        Identify gaps in these areas:
        1. Visual Brand Identity (consistency, quality, recognition)
        2. Digital Presence (website, social media, online engagement)
        3. Competitive Positioning (differentiation, market position)
        4. Marketing & Communications (campaigns, messaging, reach)
        5. Brand Experience (customer touchpoints, consistency)
        
        For each gap area, provide:
        - Current state assessment (0-100)
        - Industry benchmark (0-100)
        - Gap size (benchmark - current)
        - Impact level (high/medium/low)
        - Effort to close (high/medium/low)
        - Priority score (1-10)
        
        Respond in JSON format:
        {{
            "gap_analysis": {{
                "visual_identity": {{
                    "current_state": 75,
                    "industry_benchmark": 85,
                    "gap_size": 10,
                    "impact_level": "high",
                    "effort_to_close": "medium",
                    "priority_score": 8,
                    "specific_gaps": ["gap1", "gap2"],
                    "improvement_actions": ["action1", "action2"]
                }},
                "digital_presence": {{...}},
                "competitive_positioning": {{...}},
                "marketing_communications": {{...}},
                "brand_experience": {{...}}
            }},
            "overall_assessment": {{
                "total_gaps_identified": 5,
                "high_priority_gaps": 2,
                "quick_wins": ["win1", "win2"],
                "strategic_initiatives": ["initiative1", "initiative2"]
            }}
        }}
        """
        
        try:
            response = await self._call_openrouter_api(prompt)
            return response if response else {'error': 'No response from gap analysis'}
        except Exception as e:
            return {'error': f'Gap analysis failed: {str(e)}'}
    
    async def map_strategic_opportunities(self, brand_name: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map strategic opportunities with impact/feasibility analysis"""
        if not self.openrouter_api_key:
            return {'error': 'OpenRouter API key required'}
        
        prompt = f"""
        Map strategic opportunities for {brand_name} based on the comprehensive brand audit data.
        
        Create an opportunity matrix with:
        1. Impact potential (1-10 scale)
        2. Implementation feasibility (1-10 scale)
        3. Time to value (short/medium/long term)
        4. Resource requirements (low/medium/high)
        
        Categories of opportunities:
        - Brand Positioning Opportunities
        - Digital Transformation Opportunities
        - Market Expansion Opportunities
        - Product/Service Innovation Opportunities
        - Partnership & Collaboration Opportunities
        
        For each opportunity, provide:
        - Description and rationale
        - Impact score (1-10)
        - Feasibility score (1-10)
        - Time horizon (3-6 months, 6-12 months, 12+ months)
        - Success metrics
        - Key risks
        
        Respond in JSON format:
        {{
            "opportunity_matrix": {{
                "high_impact_high_feasibility": [
                    {{
                        "opportunity": "Enhance Visual Brand Consistency",
                        "description": "Standardize visual elements across all touchpoints",
                        "impact_score": 8,
                        "feasibility_score": 9,
                        "time_horizon": "3-6 months",
                        "success_metrics": ["metric1", "metric2"],
                        "key_risks": ["risk1", "risk2"]
                    }}
                ],
                "high_impact_low_feasibility": [...],
                "low_impact_high_feasibility": [...],
                "low_impact_low_feasibility": [...]
            }},
            "prioritized_opportunities": [
                {{
                    "rank": 1,
                    "opportunity": "opportunity name",
                    "priority_score": 85,
                    "rationale": "why this is top priority"
                }}
            ]
        }}
        """
        
        try:
            response = await self._call_openrouter_api(prompt)
            return response if response else {'error': 'No response from opportunity mapping'}
        except Exception as e:
            return {'error': f'Opportunity mapping failed: {str(e)}'}
    
    async def create_implementation_roadmap(self, brand_name: str, synthesis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create implementation roadmap with timelines and milestones"""
        if not self.openrouter_api_key:
            return {'error': 'OpenRouter API key required'}
        
        opportunities = synthesis_data.get('strategic_opportunities', {})
        gaps = synthesis_data.get('brand_gap_analysis', {})
        
        prompt = f"""
        Create a detailed implementation roadmap for {brand_name} based on the strategic analysis.
        
        Organize initiatives into phases:
        - Phase 1: Quick Wins (0-3 months)
        - Phase 2: Foundation Building (3-6 months)
        - Phase 3: Strategic Initiatives (6-12 months)
        - Phase 4: Long-term Transformation (12+ months)
        
        For each phase, include:
        - Key initiatives and projects
        - Success metrics and KPIs
        - Resource requirements
        - Dependencies and prerequisites
        - Risk mitigation strategies
        
        Respond in JSON format:
        {{
            "implementation_roadmap": {{
                "phase_1_quick_wins": {{
                    "duration": "0-3 months",
                    "initiatives": [
                        {{
                            "name": "Visual Brand Audit",
                            "description": "Standardize visual elements",
                            "success_metrics": ["metric1", "metric2"],
                            "resources_needed": ["resource1", "resource2"],
                            "dependencies": ["dep1", "dep2"]
                        }}
                    ],
                    "expected_impact": "description"
                }},
                "phase_2_foundation": {{...}},
                "phase_3_strategic": {{...}},
                "phase_4_transformation": {{...}}
            }},
            "success_framework": {{
                "key_metrics": ["metric1", "metric2"],
                "measurement_frequency": "monthly",
                "review_checkpoints": ["3 months", "6 months", "12 months"]
            }}
        }}
        """
        
        try:
            response = await self._call_openrouter_api(prompt)
            return response if response else {'error': 'No response from roadmap generation'}
        except Exception as e:
            return {'error': f'Roadmap generation failed: {str(e)}'}
    
    async def synthesize_recommendations(self, brand_name: str, synthesis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Synthesize final strategic recommendations"""
        if not self.openrouter_api_key:
            return [{'error': 'OpenRouter API key required'}]
        
        prompt = f"""
        Synthesize the top 5 strategic recommendations for {brand_name} based on the complete analysis.
        
        Each recommendation should be:
        - Specific and actionable
        - Based on data insights
        - Prioritized by impact
        - Include implementation guidance
        
        Respond in JSON format:
        {{
            "strategic_recommendations": [
                {{
                    "rank": 1,
                    "title": "Enhance Visual Brand Consistency",
                    "description": "Detailed description of the recommendation",
                    "rationale": "Why this is important based on analysis",
                    "impact_level": "high",
                    "effort_required": "medium",
                    "time_horizon": "3-6 months",
                    "success_metrics": ["metric1", "metric2"],
                    "implementation_steps": ["step1", "step2", "step3"],
                    "expected_outcomes": ["outcome1", "outcome2"]
                }}
            ]
        }}
        """
        
        try:
            response = await self._call_openrouter_api(prompt)
            return response.get('strategic_recommendations', []) if response else []
        except Exception as e:
            return [{'error': f'Recommendation synthesis failed: {str(e)}'}]
    
    async def _call_openrouter_api(self, prompt: str) -> Dict[str, Any]:
        """Call OpenRouter API for AI analysis"""
        if not self.openrouter_api_key:
            raise Exception("OpenRouter API key not configured")
        
        headers = {
            'Authorization': f'Bearer {self.openrouter_api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://brandaudit.app',
            'X-Title': 'AI Brand Audit Tool - Strategic Synthesis'
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
