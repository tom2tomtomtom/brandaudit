import requests
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from .api_validation_service import api_validator

try:
    from .intelligent_cache_service import intelligent_cache
    CACHING_AVAILABLE = True
except ImportError:
    CACHING_AVAILABLE = False


class LLMService:
    """Service for integrating with various LLM APIs"""

    def __init__(self):
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.openrouter_base_url = "https://openrouter.ai/api/v1"
        self.default_model = "anthropic/claude-3-haiku"

    async def analyze_brand_sentiment(self, text_content: str, brand_name: str) -> Dict:
        """Analyze brand sentiment from text content with caching"""

        # Check cache first
        if CACHING_AVAILABLE:
            cache_key = f"sentiment_analysis:{hash(text_content + brand_name)}"
            cached_result = await intelligent_cache.get(cache_key, 'llm_response')
            if cached_result:
                return cached_result

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
            result = {
                "success": True,
                "analysis": response,
                "processed_at": datetime.utcnow().isoformat(),
                "cached": False
            }

            # Cache the result
            if CACHING_AVAILABLE:
                await intelligent_cache.set(cache_key, result, 'llm_response')

            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "processed_at": datetime.utcnow().isoformat(),
            }

    def analyze_competitive_landscape(
        self, brand_name: str, competitor_data: List[Dict]
    ) -> Dict:
        """Generate BCG-level competitive intelligence analysis"""
        competitors_text = "\n".join(
            [
                f"- {comp.get('name', 'Unknown')}: {comp.get('description', 'No description')}"
                for comp in competitor_data
            ]
        )

        prompt = f"""
        You are a senior consultant at Boston Consulting Group conducting a comprehensive competitive intelligence analysis for {brand_name}.
        Create a strategic competitive analysis that would be suitable for executive decision-making and competitive strategy development.

        TARGET BRAND: {brand_name}

        KNOWN COMPETITORS:
        {competitors_text}

        Provide a comprehensive competitive intelligence analysis structured as follows:

        ## COMPETITIVE LANDSCAPE OVERVIEW
        - Industry structure and competitive dynamics
        - Market segmentation and strategic groups
        - Competitive intensity and rivalry assessment
        - Barriers to entry and competitive moats

        ## COMPETITOR STRATEGIC PROFILES
        For each major competitor, provide:
        - Strategic positioning and value proposition
        - Competitive strengths and vulnerabilities
        - Market share and financial performance
        - Strategic initiatives and future direction
        - Threat level assessment to {brand_name}

        ## COMPETITIVE POSITIONING MATRIX
        Create a strategic positioning analysis covering:
        - Price vs Quality positioning
        - Innovation vs Tradition positioning
        - Premium vs Mass market positioning
        - Digital vs Traditional channel focus

        ## MARKET SHARE & DYNAMICS
        - Current market share distribution
        - Growth trajectory analysis by competitor
        - Market share trends and shifts
        - Emerging competitive threats

        ## COMPETITIVE ADVANTAGES ANALYSIS
        For {brand_name} specifically:
        - Unique competitive advantages vs each competitor
        - Competitive disadvantages and vulnerabilities
        - White space opportunities in the market
        - Differentiation potential and strategies

        ## STRATEGIC IMPLICATIONS & RECOMMENDATIONS
        Provide 5-7 strategic recommendations for {brand_name}:
        - Competitive response strategies
        - Market positioning adjustments
        - Differentiation opportunities
        - Competitive intelligence priorities
        - Strategic partnership considerations

        Format as structured markdown with clear strategic insights. Focus on actionable competitive intelligence that can drive strategic decision-making.
        """

        try:
            response = self._call_llm(prompt, max_tokens=1500)
            return {
                "success": True,
                "analysis": response,
                "processed_at": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "processed_at": datetime.utcnow().isoformat(),
            }

    def generate_brand_insights(self, brand_data: Dict) -> Dict:
        """Generate McKinsey-level comprehensive brand strategic analysis"""
        brand_name = brand_data.get("name", "Unknown Brand")

        prompt = f"""
        You are a senior partner at McKinsey & Company conducting a comprehensive brand audit for {brand_name}.
        Create a consulting-grade strategic analysis that would be suitable for C-suite presentation and help brand agencies win business.

        BRAND DATA:
        - Name: {brand_data.get("name", "Unknown")}
        - Industry: {brand_data.get("industry", "Unknown")}
        - Description: {brand_data.get("description", "No description")}
        - Founded: {brand_data.get("founded", "Unknown")}
        - Website: {brand_data.get("website", "Unknown")}
        - News Articles: {len(brand_data.get("news_articles", []))} articles analyzed
        - Social Mentions: {brand_data.get("social_mentions", 0)} mentions tracked

        Provide a comprehensive analysis structured as follows:

        ## EXECUTIVE SUMMARY
        Write 4-5 comprehensive paragraphs (minimum 1500 characters) of strategic insights covering:

        **Strategic Context & Market Position** (300-400 characters): Provide detailed analysis of {brand_name}'s current market position, brand equity valuation, competitive landscape dynamics, and strategic challenges. Include specific metrics, market share data, and competitive positioning insights.

        **Critical Strategic Findings** (300-400 characters): Detail the most significant discoveries from the brand audit with material business implications. Focus on findings that require immediate executive attention, represent significant opportunities or risks, and impact competitive positioning.

        **Competitive Dynamics & Threats** (300-400 characters): Analyze key competitive threats, emerging market disruptors, competitive response patterns, and strategic vulnerabilities. Include assessment of competitive advantages and areas where {brand_name} faces strategic pressure.

        **Strategic Imperatives & Priorities** (300-400 characters): Outline the top 3-4 strategic priorities for the next 12-18 months with expected business impact, resource requirements, and implementation timelines. Focus on initiatives that will drive measurable improvements in brand equity and market position.

        **Executive Recommendations** (200-300 characters): Provide clear, actionable recommendations for C-suite decision making with priority levels, expected ROI, and success metrics.

        ## BRAND POSITIONING ANALYSIS
        - Market positioning vs key competitors with strategic implications
        - Brand equity drivers and value proposition assessment
        - Customer perception and loyalty analysis with quantitative insights
        - Brand architecture and portfolio strategy evaluation

        ## COMPETITIVE INTELLIGENCE
        Provide comprehensive competitive analysis (minimum 1200 characters):

        **Competitive Landscape Overview**: Detailed industry structure analysis, competitive intensity assessment, market concentration dynamics, and strategic group mapping. Include Porter's Five Forces analysis and competitive moats assessment.

        **Key Competitor Strategic Profiles**: For each of the top 4-5 competitors, provide:
        - Strategic positioning and business model analysis
        - Competitive strengths and core competencies
        - Strategic vulnerabilities and blind spots
        - Recent strategic moves and future direction
        - Financial performance and investment capacity
        - Threat level assessment to {brand_name}

        **Competitive Positioning Matrix**: Multi-dimensional analysis positioning {brand_name} vs competitors on:
        - Innovation Leadership vs Market Execution
        - Premium Positioning vs Value Positioning
        - Global Reach vs Local Focus
        - Digital Transformation vs Traditional Operations

        **Market Share & Dynamics**: Historical and projected market share analysis, growth trajectory assessment, competitive response patterns, and emerging competitive threats.

        **Strategic Implications**: Specific recommendations for {brand_name} based on competitive analysis including defensive strategies, offensive opportunities, and white space identification.

        ## MARKET PERFORMANCE & DYNAMICS
        Provide comprehensive market analysis (minimum 800 characters):
        - **Industry Trends**: Detailed analysis of industry trends and market dynamics affecting {brand_name} performance with specific data and projections
        - **Growth Opportunities**: Quantified market expansion potential with addressable market size and growth rates
        - **Customer Behavior**: Analysis of customer behavior shifts and emerging market segments with demographic and psychographic insights
        - **Digital Transformation**: Impact assessment of digital transformation on brand positioning and competitive landscape
        - **Market Disruption**: Identification of potential disruptors and emerging competitive threats

        ## BRAND EQUITY ASSESSMENT
        Provide detailed brand equity analysis (minimum 700 characters):
        - **Brand Valuation**: Quantitative brand strength metrics and equity valuation with industry benchmarking
        - **Customer Loyalty**: Comprehensive customer loyalty and retention analysis with specific metrics and trends
        - **Brand Awareness**: Brand awareness and consideration metrics across key demographics and markets
        - **Cultural Relevance**: Assessment of cultural relevance and social impact with reputation analysis
        - **Brand Architecture**: Evaluation of brand portfolio strategy and sub-brand relationships

        ## DIGITAL ECOSYSTEM ANALYSIS
        Provide comprehensive digital analysis (minimum 600 characters):
        - **Digital Presence**: Effectiveness analysis across all digital touchpoints with performance metrics
        - **Social Media Strategy**: Social media strategy and engagement analysis with platform-specific insights
        - **Content Strategy**: Content strategy and thought leadership positioning assessment
        - **Customer Experience**: Digital customer experience and conversion optimization analysis
        - **Technology Integration**: Assessment of technology integration and digital innovation capabilities

        ## STRATEGIC RECOMMENDATIONS
        Provide 7-10 comprehensive strategic recommendations (minimum 1000 characters) with detailed analysis:

        For each recommendation, include:
        **Strategic Rationale**: Detailed explanation of why this recommendation is critical for {brand_name}'s success
        **Expected Business Impact**: Quantified impact on brand equity, market share, revenue, or competitive position
        **Implementation Timeline**: Specific phases (30/60/90/120 days) with key milestones
        **Resource Requirements**: Investment levels, team requirements, and capability needs
        **Success Metrics**: Specific KPIs and measurement frameworks
        **Risk Assessment**: Potential risks and mitigation strategies
        **Priority Level**: High/Medium/Low with justification
        **Competitive Implications**: How this impacts competitive positioning

        Structure as:
        ### 1. [Recommendation Title] (Priority: High/Medium/Low)
        **Strategic Rationale**: [Detailed explanation]
        **Expected Impact**: [Quantified business impact]
        **Implementation**: [Phase-by-phase timeline]
        **Resources**: [Investment and team requirements]
        **Success Metrics**: [Specific KPIs]
        **Risks & Mitigation**: [Risk assessment]

        ## IMPLEMENTATION ROADMAP
        Provide detailed implementation roadmap (minimum 800 characters) with specific timelines and deliverables:

        **Phase 1: Foundation & Quick Wins (0-3 months)**
        - Specific initiatives and deliverables
        - Resource allocation and team assignments
        - Key milestones and success criteria
        - Expected outcomes and impact metrics

        **Phase 2: Core Strategic Implementation (3-6 months)**
        - Major strategic initiatives and programs
        - Cross-functional coordination requirements
        - Investment and resource scaling
        - Performance monitoring and adjustment protocols

        **Phase 3: Optimization & Expansion (6-12 months)**
        - Advanced capabilities and market expansion
        - Competitive response and market adaptation
        - Long-term sustainability and growth
        - Strategic review and evolution planning

        **Success Metrics & Governance**
        - KPI tracking and measurement frameworks
        - Executive review cycles and accountability
        - Course correction protocols and triggers
        - ROI measurement and business impact assessment

        CRITICAL OUTPUT REQUIREMENTS:
        - Format as structured markdown with clear headers (NOT JSON)
        - Minimum 3000 characters total content
        - Each section must be substantial with detailed analysis
        - Use professional consulting language and frameworks
        - Include specific metrics, data points, and strategic insights
        - Ensure consulting-grade depth throughout
        - This analysis should be comprehensive enough to help brand agencies win business and guide C-suite decision making

        EXAMPLE OUTPUT FORMAT:
        ## EXECUTIVE SUMMARY
        [4-5 detailed paragraphs with specific insights...]

        ## BRAND POSITIONING ANALYSIS
        [Comprehensive analysis with data and frameworks...]

        [Continue with all sections in markdown format]
        """

        try:
            response = self._call_llm(prompt, max_tokens=4000)
            return {
                "success": True,
                "insights": response,
                "processed_at": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "processed_at": datetime.utcnow().isoformat(),
            }

    def generate_executive_summary(self, analysis_data: Dict) -> Dict:
        """Generate C-suite ready executive summary with strategic depth"""
        brand_name = analysis_data.get("brand_name", "the brand")

        prompt = f"""
        You are preparing an executive summary for the CEO and board of directors regarding {brand_name}'s brand audit.
        This summary will be used for strategic decision-making and must be of the highest professional quality.

        CRITICAL REQUIREMENT: Generate a comprehensive executive summary with minimum 2000 characters. This must be substantial enough for C-suite presentation and board review.

        ANALYSIS DATA:
        {json.dumps(analysis_data, indent=2)}

        Create a comprehensive executive summary with the following structure:

        ## EXECUTIVE SUMMARY

        Write 2-3 substantive paragraphs (not bullet points) covering:

        **Strategic Context & Position**: Current market position, key competitive dynamics, and strategic challenges facing {brand_name}. Include specific insights about market share, competitive threats, and positioning relative to key competitors.

        **Critical Findings & Implications**: Most important discoveries from the brand audit with their strategic implications. Focus on findings that require immediate executive attention or represent significant opportunities/risks.

        **Strategic Imperatives**: Top 3-4 strategic priorities for the next 12-18 months with expected impact on business performance and competitive position.

        ## KEY STRATEGIC FINDINGS
        - [Finding 1]: Specific insight with business impact
        - [Finding 2]: Specific insight with business impact
        - [Finding 3]: Specific insight with business impact
        - [Finding 4]: Specific insight with business impact
        - [Finding 5]: Specific insight with business impact

        ## PRIORITY RECOMMENDATIONS
        1. **[Recommendation Title]** (Priority: High/Medium/Low)
           - Strategic rationale and expected impact
           - Implementation timeline: [specific timeframe]
           - Investment required: [estimate]
           - Success metrics: [specific KPIs]

        2. **[Recommendation Title]** (Priority: High/Medium/Low)
           - Strategic rationale and expected impact
           - Implementation timeline: [specific timeframe]
           - Investment required: [estimate]
           - Success metrics: [specific KPIs]

        [Continue for 5-7 recommendations]

        ## OVERALL BRAND HEALTH ASSESSMENT
        - Overall Brand Health Score: [X]/100
        - Competitive Position: [Strong/Moderate/Weak] vs key competitors
        - Market Trajectory: [Improving/Stable/Declining]
        - Strategic Risk Level: [Low/Medium/High]

        ## IMMEDIATE NEXT STEPS (30-60-90 Days)
        - 30 Days: [Specific actions]
        - 60 Days: [Specific actions]
        - 90 Days: [Specific actions]

        CRITICAL OUTPUT REQUIREMENTS:
        - Format as structured markdown (NOT JSON)
        - Minimum 2500 characters total content
        - Use professional consulting language suitable for board presentations
        - Include specific metrics, insights, and strategic recommendations
        - Focus on business impact and competitive implications

        EXAMPLE OUTPUT FORMAT:
        ## EXECUTIVE SUMMARY
        [4-5 detailed paragraphs...]

        ## KEY STRATEGIC FINDINGS
        [Detailed bullet points with analysis...]

        [Continue with all sections in markdown format]
        """

        try:
            response = self._call_llm(prompt, max_tokens=1500)
            return {
                "success": True,
                "summary": response,
                "generated_at": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "generated_at": datetime.utcnow().isoformat(),
            }

    def analyze_visual_brand_consistency(self, visual_assets: List[Dict]) -> Dict:
        """Analyze visual brand consistency from uploaded assets"""
        assets_description = "\n".join(
            [
                f"- {asset.get('type', 'unknown')}: {asset.get('filename', 'unknown')} "
                f"({asset.get('size', 'unknown')} bytes)"
                for asset in visual_assets
            ]
        )

        prompt = f"""
        You are a senior brand strategist conducting a comprehensive visual brand analysis.
        Create a professional assessment suitable for brand management and creative agency presentations.

        VISUAL ASSETS ANALYZED:
        {assets_description}

        Provide a comprehensive visual brand analysis structured as follows:

        ## VISUAL BRAND CONSISTENCY ANALYSIS

        **Overall Visual Consistency Score**: [X]/100
        - Rationale for score based on cross-platform consistency
        - Key consistency strengths and weaknesses identified
        - Benchmark comparison vs industry standards

        ## BRAND IDENTITY SYSTEM ASSESSMENT

        **Logo Usage & Application**:
        - Logo consistency across different applications
        - Proper usage vs violations of brand guidelines
        - Logo scalability and readability assessment
        - Recommendations for logo optimization

        **Color Palette Analysis**:
        - Primary and secondary color consistency
        - Color application across different media
        - Color psychology and brand alignment
        - Accessibility and contrast considerations

        **Typography System**:
        - Font consistency and hierarchy
        - Readability across different applications
        - Brand personality alignment through typography
        - Typography system recommendations

        ## VISUAL BRAND GUIDELINES COMPLIANCE

        **Brand Standards Adherence**:
        - Compliance with established brand guidelines
        - Deviations and inconsistencies identified
        - Impact of inconsistencies on brand perception
        - Guidelines enforcement recommendations

        ## STRATEGIC VISUAL RECOMMENDATIONS

        Provide 5-7 prioritized recommendations:
        1. **[Recommendation]**: Strategic rationale and implementation approach
        2. **[Recommendation]**: Strategic rationale and implementation approach
        [Continue for all recommendations]

        ## VISUAL BRAND PERFORMANCE METRICS
        - Brand Recognition Score: [X]/100
        - Visual Differentiation Score: [X]/100
        - Cross-Platform Consistency: [X]/100
        - Professional Execution Quality: [X]/100

        Note: This analysis is based on available asset metadata. For complete visual analysis,
        computer vision and design analysis tools would provide additional insights.

        Format as structured markdown with professional insights suitable for brand strategy presentations.
        """

        try:
            response = self._call_llm(prompt, max_tokens=1000)
            return {
                "success": True,
                "analysis": response,
                "processed_at": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "processed_at": datetime.utcnow().isoformat(),
            }

    def _call_llm(
        self, prompt: str, max_tokens: int = 1000, model: Optional[str] = None
    ) -> str:
        """Make API call to LLM service with validation and retry logic"""
        if not self.openrouter_api_key:
            raise Exception("OpenRouter API key not configured. Cannot proceed without real API access.")

        def make_llm_request():
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://brand-audit-tool.com",
                "X-Title": "Brand Audit Tool",
            }

            data = {
                "model": model or self.default_model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.7,
            }

            response = requests.post(
                f"{self.openrouter_base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=60,
            )

            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                raise Exception(f"LLM API error: {response.status_code} - {response.text}")

        # Use validation service with retry logic
        try:
            return api_validator.execute_with_retry('openrouter', make_llm_request)
        except Exception as e:
            # Log the failure and re-raise - no fake data fallback
            api_validator.log_api_usage('openrouter', 'chat_completion', False, None, str(e))
            raise Exception(f"LLM service unavailable: {str(e)}. Cannot provide analysis without real API access.")


# Global instance
llm_service = LLMService()
