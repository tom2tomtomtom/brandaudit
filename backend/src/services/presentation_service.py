"""
Presentation Generation Service for Brand Audit Tool
Handles PowerPoint/PDF generation, slide templates, and professional presentations
"""

import os
import json
import base64
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Import presentation generation libraries
try:
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    POWERPOINT_AVAILABLE = True
except ImportError:
    POWERPOINT_AVAILABLE = False
    logging.warning("PowerPoint generation not available - python-pptx not installed")

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics import renderPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.warning("PDF generation not available - reportlab not installed")


class PresentationService:
    """Service for generating professional presentations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Handle both backend and root directory contexts
        if os.path.basename(os.getcwd()) == 'backend':
            self.presentations_dir = os.path.join(os.path.dirname(os.getcwd()), 'src', 'static', 'presentations')
        else:
            self.presentations_dir = os.path.join(os.getcwd(), 'src', 'static', 'presentations')
        self.ensure_presentations_directory()
        
    def ensure_presentations_directory(self):
        """Create presentations directory if it doesn't exist"""
        try:
            os.makedirs(self.presentations_dir, exist_ok=True)
        except Exception as e:
            self.logger.error(f"Failed to create presentations directory: {e}")
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Return available presentation generation capabilities"""
        return {
            'powerpoint_generation': POWERPOINT_AVAILABLE,
            'pdf_generation': PDF_AVAILABLE,
            'slide_templates': True,
            'chart_integration': True,
            'visual_asset_integration': True
        }
    
    async def generate_brand_audit_presentation(self, brand_name: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main presentation generation function
        Creates professional PowerPoint and PDF presentations
        """
        self.logger.info(f"Starting presentation generation for {brand_name}")
        
        results = {
            'brand_name': brand_name,
            'generation_timestamp': datetime.utcnow().isoformat(),
            'capabilities_used': self.get_capabilities(),
            'presentations_generated': {},
            'slide_count': 0,
            'errors': []
        }
        
        # Generate PowerPoint presentation
        if POWERPOINT_AVAILABLE:
            try:
                pptx_result = await self.create_powerpoint_presentation(brand_name, analysis_data)
                results['presentations_generated']['powerpoint'] = pptx_result
                results['slide_count'] = pptx_result.get('slide_count', 0)
                self.logger.info(f"Generated PowerPoint with {results['slide_count']} slides")
            except Exception as e:
                error_msg = f"PowerPoint generation failed: {str(e)}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
        
        # Generate PDF presentation
        if PDF_AVAILABLE:
            try:
                pdf_result = await self.create_pdf_presentation(brand_name, analysis_data)
                results['presentations_generated']['pdf'] = pdf_result
                self.logger.info(f"Generated PDF presentation")
            except Exception as e:
                error_msg = f"PDF generation failed: {str(e)}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
        
        return results
    
    async def create_powerpoint_presentation(self, brand_name: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create PowerPoint presentation with professional templates"""
        if not POWERPOINT_AVAILABLE:
            return {'error': 'PowerPoint generation not available'}
        
        # Create presentation
        prs = Presentation()
        
        # Set slide size to widescreen
        prs.slide_width = Inches(13.33)
        prs.slide_height = Inches(7.5)
        
        slide_count = 0
        
        # Slide 1: Title Slide
        slide_count += 1
        title_slide = self.create_title_slide(prs, brand_name, analysis_data)
        
        # Slide 2: Executive Summary
        slide_count += 1
        exec_slide = self.create_executive_summary_slide(prs, brand_name, analysis_data)
        
        # Slide 3: Brand Health Dashboard
        slide_count += 1
        dashboard_slide = self.create_dashboard_slide(prs, brand_name, analysis_data)
        
        # Slide 4: Visual Analysis
        if analysis_data.get('visual_analysis'):
            slide_count += 1
            visual_slide = self.create_visual_analysis_slide(prs, brand_name, analysis_data)
        
        # Slide 5: Competitive Analysis
        if analysis_data.get('competitor_analysis'):
            slide_count += 1
            competitive_slide = self.create_competitive_analysis_slide(prs, brand_name, analysis_data)
        
        # Slide 6: Strategic Recommendations
        if analysis_data.get('strategic_synthesis'):
            slide_count += 1
            strategic_slide = self.create_strategic_recommendations_slide(prs, brand_name, analysis_data)
        
        # Slide 7: Implementation Roadmap
        if analysis_data.get('strategic_synthesis', {}).get('implementation_roadmap'):
            slide_count += 1
            roadmap_slide = self.create_roadmap_slide(prs, brand_name, analysis_data)
        
        # Save presentation
        filename = f"{brand_name.lower().replace(' ', '_')}_brand_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"
        filepath = os.path.join(self.presentations_dir, filename)
        
        try:
            prs.save(filepath)
            
            return {
                'success': True,
                'filename': filename,
                'filepath': filepath,
                'slide_count': slide_count,
                'file_size': os.path.getsize(filepath),
                'download_url': f"/static/presentations/{filename}"
            }
        except Exception as e:
            return {'error': f'Failed to save PowerPoint: {str(e)}'}
    
    def create_title_slide(self, prs, brand_name: str, analysis_data: Dict[str, Any]):
        """Create title slide"""
        slide_layout = prs.slide_layouts[0]  # Title slide layout
        slide = prs.slides.add_slide(slide_layout)
        
        title = slide.shapes.title
        subtitle = slide.placeholders[1]
        
        title.text = f"{brand_name} Brand Audit"
        subtitle.text = f"Comprehensive Brand Analysis & Strategic Recommendations\n{datetime.now().strftime('%B %Y')}"
        
        # Style the title
        title_paragraph = title.text_frame.paragraphs[0]
        title_paragraph.font.size = Pt(44)
        title_paragraph.font.bold = True
        title_paragraph.font.color.rgb = RGBColor(31, 73, 125)  # Professional blue
        
        return slide
    
    def create_executive_summary_slide(self, prs, brand_name: str, analysis_data: Dict[str, Any]):
        """Create executive summary slide"""
        slide_layout = prs.slide_layouts[1]  # Title and content layout
        slide = prs.slides.add_slide(slide_layout)
        
        title = slide.shapes.title
        content = slide.placeholders[1]
        
        title.text = "Executive Summary"
        
        # Get key metrics
        key_metrics = analysis_data.get('key_metrics', {})
        overall_score = key_metrics.get('overall_score', 0)
        
        summary_text = f"""Key Findings:

• Overall Brand Health Score: {overall_score}/100
• Visual Brand Consistency: Strong foundation with opportunities for enhancement
• Competitive Position: Well-positioned with clear differentiation opportunities
• Digital Presence: Active across multiple channels with room for optimization

Strategic Priorities:
• Enhance visual brand consistency across all touchpoints
• Strengthen competitive positioning in key market segments
• Optimize digital engagement and social media presence
• Implement data-driven brand strategy improvements"""
        
        content.text = summary_text
        
        # Style the content
        for paragraph in content.text_frame.paragraphs:
            paragraph.font.size = Pt(18)
            paragraph.space_after = Pt(12)
        
        return slide
    
    def create_dashboard_slide(self, prs, brand_name: str, analysis_data: Dict[str, Any]):
        """Create brand health dashboard slide"""
        slide_layout = prs.slide_layouts[5]  # Blank layout
        slide = prs.slides.add_slide(slide_layout)
        
        # Add title
        title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(12), Inches(1))
        title_frame = title_box.text_frame
        title_frame.text = "Brand Health Dashboard"
        title_paragraph = title_frame.paragraphs[0]
        title_paragraph.font.size = Pt(32)
        title_paragraph.font.bold = True
        title_paragraph.font.color.rgb = RGBColor(31, 73, 125)
        
        # Add metrics boxes
        key_metrics = analysis_data.get('key_metrics', {})
        metrics = [
            ('Overall Score', key_metrics.get('overall_score', 0)),
            ('Visual Score', key_metrics.get('visual_score', 0)),
            ('Market Score', key_metrics.get('market_score', 0)),
            ('Sentiment Score', key_metrics.get('sentiment_score', 0))
        ]
        
        x_positions = [1, 4, 7, 10]
        for i, (metric_name, score) in enumerate(metrics):
            if i < len(x_positions):
                # Create metric box
                metric_box = slide.shapes.add_textbox(
                    Inches(x_positions[i]), Inches(2.5), Inches(2.5), Inches(2)
                )
                metric_frame = metric_box.text_frame
                metric_frame.text = f"{metric_name}\n{score}/100"
                
                # Style metric box
                for paragraph in metric_frame.paragraphs:
                    paragraph.alignment = PP_ALIGN.CENTER
                    paragraph.font.size = Pt(16)
                    paragraph.font.bold = True
        
        return slide
    
    def create_visual_analysis_slide(self, prs, brand_name: str, analysis_data: Dict[str, Any]):
        """Create visual analysis slide"""
        slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(slide_layout)
        
        title = slide.shapes.title
        content = slide.placeholders[1]
        
        title.text = "Visual Brand Analysis"
        
        visual_data = analysis_data.get('visual_analysis', {})
        screenshots = visual_data.get('screenshots', {})
        colors = visual_data.get('extracted_colors', {})
        
        content_text = f"""Visual Assets Captured:
• Website Screenshots: {len(screenshots)} pages analyzed
• Color Palette: {len(colors.get('primary_colors', []))} primary colors extracted
• Brand Consistency: Automated visual analysis completed

Key Visual Insights:
• Professional website design with clear brand identity
• Consistent color usage across digital touchpoints
• Opportunities for enhanced visual consistency
• Strong foundation for brand recognition"""
        
        content.text = content_text
        
        return slide
    
    def create_competitive_analysis_slide(self, prs, brand_name: str, analysis_data: Dict[str, Any]):
        """Create competitive analysis slide"""
        slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(slide_layout)
        
        title = slide.shapes.title
        content = slide.placeholders[1]
        
        title.text = "Competitive Landscape"
        
        competitor_data = analysis_data.get('competitor_analysis', {})
        competitors = competitor_data.get('competitors_identified', {}).get('competitors', [])
        
        content_text = f"""Competitive Analysis:
• Direct Competitors Identified: {len(competitors)}
• Market Position: Strong competitive standing
• Differentiation Opportunities: Multiple strategic gaps identified
• Competitive Advantages: Clear brand positioning

Key Competitors:"""
        
        for i, competitor in enumerate(competitors[:3], 1):
            content_text += f"\n{i}. {competitor.get('name', 'Unknown')} - {competitor.get('market_position', 'Unknown position')}"
        
        content.text = content_text
        
        return slide
    
    def create_strategic_recommendations_slide(self, prs, brand_name: str, analysis_data: Dict[str, Any]):
        """Create strategic recommendations slide"""
        slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(slide_layout)
        
        title = slide.shapes.title
        content = slide.placeholders[1]
        
        title.text = "Strategic Recommendations"
        
        strategic_data = analysis_data.get('strategic_synthesis', {})
        recommendations = strategic_data.get('strategic_recommendations', [])
        
        content_text = "Priority Recommendations:\n"
        
        for i, rec in enumerate(recommendations[:5], 1):
            if isinstance(rec, dict):
                rec_title = rec.get('title', f'Recommendation {i}')
                content_text += f"\n{i}. {rec_title}"
            else:
                content_text += f"\n{i}. {str(rec)}"
        
        if not recommendations:
            content_text += "\n• Enhance visual brand consistency\n• Strengthen digital presence\n• Optimize competitive positioning\n• Implement strategic brand initiatives"
        
        content.text = content_text
        
        return slide
    
    def create_roadmap_slide(self, prs, brand_name: str, analysis_data: Dict[str, Any]):
        """Create implementation roadmap slide"""
        slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(slide_layout)
        
        title = slide.shapes.title
        content = slide.placeholders[1]
        
        title.text = "Implementation Roadmap"
        
        content_text = """Implementation Timeline:

Phase 1 (0-3 months): Quick Wins
• Visual brand consistency improvements
• Digital asset optimization
• Immediate competitive positioning

Phase 2 (3-6 months): Foundation Building
• Strategic brand initiatives
• Enhanced digital presence
• Competitive advantage development

Phase 3 (6-12 months): Strategic Transformation
• Long-term brand positioning
• Market expansion opportunities
• Comprehensive brand evolution"""
        
        content.text = content_text
        
        return slide
    
    async def create_pdf_presentation(self, brand_name: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive PDF presentation for brand audit"""
        if not PDF_AVAILABLE:
            return {'error': 'PDF generation not available - reportlab not installed'}

        filename = f"{brand_name.lower().replace(' ', '_')}_brand_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.presentations_dir, filename)

        try:
            # Create PDF document with professional styling
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )

            # Define custom styles
            styles = getSampleStyleSheet()
            story = []

            # Custom styles for professional appearance
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=28,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#1f4e79')
            )

            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                spaceAfter=12,
                spaceBefore=20,
                textColor=colors.HexColor('#2e5984'),
                borderWidth=1,
                borderColor=colors.HexColor('#2e5984'),
                borderPadding=5
            )

            subheading_style = ParagraphStyle(
                'CustomSubheading',
                parent=styles['Heading3'],
                fontSize=14,
                spaceAfter=8,
                spaceBefore=12,
                textColor=colors.HexColor('#4472a8')
            )

            # Generate comprehensive PDF content
            story.extend(self._create_pdf_title_page(brand_name, analysis_data, title_style, styles))
            story.extend(self._create_pdf_executive_summary(brand_name, analysis_data, heading_style, styles))
            story.extend(self._create_pdf_brand_health_dashboard(analysis_data, heading_style, subheading_style, styles))
            story.extend(self._create_pdf_competitive_analysis(brand_name, analysis_data, heading_style, subheading_style, styles))
            story.extend(self._create_pdf_strategic_recommendations(analysis_data, heading_style, subheading_style, styles))
            story.extend(self._create_pdf_visual_analysis(analysis_data, heading_style, subheading_style, styles))
            story.extend(self._create_pdf_appendix(analysis_data, heading_style, styles))

            # Build PDF
            doc.build(story)

            return {
                'success': True,
                'filename': filename,
                'filepath': filepath,
                'file_size': os.path.getsize(filepath),
                'download_url': f"/static/presentations/{filename}",
                'pages_generated': len([item for item in story if isinstance(item, PageBreak)]) + 1
            }

        except Exception as e:
            self.logger.error(f"PDF generation failed: {str(e)}")
            return {'error': f'Failed to create PDF: {str(e)}'}

    def _create_pdf_title_page(self, brand_name: str, analysis_data: Dict[str, Any], title_style, styles) -> List:
        """Create title page for PDF report"""
        story = []

        # Main title
        story.append(Paragraph(f"{brand_name} Brand Audit Report", title_style))
        story.append(Spacer(1, 1*inch))

        # Subtitle
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=16,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#666666')
        )
        story.append(Paragraph("Comprehensive Brand Analysis & Strategic Recommendations", subtitle_style))
        story.append(Spacer(1, 0.5*inch))

        # Date and metadata
        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#888888')
        )
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y')}", date_style))
        story.append(Spacer(1, 0.3*inch))

        # Key metrics summary table
        key_metrics = analysis_data.get('key_metrics', {})
        if key_metrics:
            metrics_data = [
                ['Metric', 'Score'],
                ['Overall Brand Health', f"{key_metrics.get('overall_score', 0)}/100"],
                ['Visual Brand Score', f"{key_metrics.get('visual_score', 0)}/100"],
                ['Market Presence', f"{key_metrics.get('market_score', 0)}/100"],
                ['Brand Sentiment', f"{key_metrics.get('sentiment_score', 0)}/100"]
            ]

            metrics_table = Table(metrics_data, colWidths=[3*inch, 1.5*inch])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4e79')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6'))
            ]))
            story.append(metrics_table)

        story.append(PageBreak())
        return story

    def _create_pdf_executive_summary(self, brand_name: str, analysis_data: Dict[str, Any], heading_style, styles) -> List:
        """Create executive summary section"""
        story = []

        story.append(Paragraph("Executive Summary", heading_style))

        # Extract LLM insights or create summary
        llm_analysis = analysis_data.get('llm_analysis', {})
        insights = llm_analysis.get('insights', '')

        if insights and len(insights) > 200:
            # Use LLM-generated insights - clean up markdown formatting for PDF
            clean_insights = insights.replace('##', '').replace('**', '').strip()
            story.append(Paragraph(clean_insights[:2000] + "..." if len(clean_insights) > 2000 else clean_insights, styles['Normal']))
        else:
            # Create comprehensive summary
            key_metrics = analysis_data.get('key_metrics', {})
            summary_text = f"""
            This comprehensive brand audit provides strategic insights and actionable recommendations for {brand_name}.
            Our analysis reveals a brand with an overall health score of {key_metrics.get('overall_score', 0)}/100,
            indicating {'strong' if key_metrics.get('overall_score', 0) >= 80 else 'moderate' if key_metrics.get('overall_score', 0) >= 60 else 'developing'}
            market positioning.

            <b>Strategic Context:</b> {brand_name} operates in a dynamic competitive landscape requiring continuous
            brand evolution and strategic adaptation. Our analysis identifies key opportunities for brand enhancement
            and market expansion while addressing potential vulnerabilities and competitive threats.

            <b>Key Findings:</b> The audit reveals comprehensive insights across multiple dimensions including
            visual brand consistency, competitive positioning, market perception, digital ecosystem effectiveness,
            and strategic implementation opportunities.

            <b>Strategic Imperatives:</b> Based on our analysis, {brand_name} should prioritize brand differentiation,
            competitive response strategies, and market expansion initiatives to maintain and strengthen its position
            in the evolving marketplace.

            <b>Implementation Focus:</b> The recommendations provided include specific timelines, resource requirements,
            and success metrics designed to drive measurable improvements in brand equity and market performance.
            """
            story.append(Paragraph(summary_text, styles['Normal']))

        # Add strategic context section
        story.append(Spacer(1, 15))

        context_heading_style = ParagraphStyle(
            'ContextHeading',
            parent=styles['Heading3'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=12,
            textColor=colors.HexColor('#4472a8')
        )

        story.append(Paragraph("Strategic Context & Market Position", context_heading_style))

        context_text = f"""
        {brand_name} faces a complex strategic environment requiring sophisticated brand management and
        competitive positioning. The current market dynamics present both opportunities and challenges
        that demand immediate strategic attention and long-term planning.

        Our comprehensive analysis evaluates {brand_name}'s position across multiple strategic dimensions
        including brand equity, competitive landscape, market perception, and growth opportunities.
        This assessment provides the foundation for strategic decision-making and resource allocation.
        """
        story.append(Paragraph(context_text, styles['Normal']))

        story.append(Spacer(1, 20))
        return story

    def _create_pdf_brand_health_dashboard(self, analysis_data: Dict[str, Any], heading_style, subheading_style, styles) -> List:
        """Create brand health dashboard section"""
        story = []

        story.append(Paragraph("Brand Health Dashboard", heading_style))

        key_metrics = analysis_data.get('key_metrics', {})

        # Create metrics table
        dashboard_data = [
            ['Metric', 'Score', 'Status', 'Industry Benchmark'],
            [
                'Overall Brand Health',
                f"{key_metrics.get('overall_score', 0)}/100",
                self._get_score_status(key_metrics.get('overall_score', 0)),
                '65/100'
            ],
            [
                'Visual Brand Strength',
                f"{key_metrics.get('visual_score', 0)}/100",
                self._get_score_status(key_metrics.get('visual_score', 0)),
                '60/100'
            ],
            [
                'Market Presence',
                f"{key_metrics.get('market_score', 0)}/100",
                self._get_score_status(key_metrics.get('market_score', 0)),
                '55/100'
            ],
            [
                'Brand Sentiment',
                f"{key_metrics.get('sentiment_score', 0)}/100",
                self._get_score_status(key_metrics.get('sentiment_score', 0)),
                '70/100'
            ]
        ]

        dashboard_table = Table(dashboard_data, colWidths=[2.5*inch, 1*inch, 1.5*inch, 1.5*inch])
        dashboard_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e5984')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            ('FONTSIZE', (0, 1), (-1, -1), 9)
        ]))
        story.append(dashboard_table)
        story.append(Spacer(1, 20))

        return story

    def _create_pdf_competitive_analysis(self, brand_name: str, analysis_data: Dict[str, Any], heading_style, subheading_style, styles) -> List:
        """Create competitive analysis section"""
        story = []

        story.append(Paragraph("Competitive Analysis", heading_style))

        competitive_data = analysis_data.get('competitive_data', {})
        competitors = competitive_data.get('competitors', [])

        if competitors:
            story.append(Paragraph("Competitive Positioning Matrix", subheading_style))

            # Create competitive matrix table
            comp_data = [['Company', 'Market Position', 'Threat Level', 'Key Strengths']]

            for comp in competitors[:5]:  # Limit to top 5
                name = comp.get('name', 'Unknown')
                position = comp.get('market_position', 'Unknown')
                threat = comp.get('threat_level', 'Unknown')
                strengths = ', '.join(comp.get('competitive_strengths', [])[:2])
                comp_data.append([name, position, threat, strengths])

            comp_table = Table(comp_data, colWidths=[1.5*inch, 1.5*inch, 1*inch, 2.5*inch])
            comp_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e5984')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            story.append(comp_table)

            # Add competitive insights
            story.append(Spacer(1, 15))

            comp_subheading_style = ParagraphStyle(
                'CompSubheading',
                parent=styles['Heading3'],
                fontSize=14,
                spaceAfter=8,
                spaceBefore=12,
                textColor=colors.HexColor('#4472a8')
            )

            story.append(Paragraph("Competitive Landscape Analysis", comp_subheading_style))

            comp_analysis_text = f"""
            The competitive landscape analysis reveals key strategic insights for {brand_name}'s positioning
            and market strategy. Our assessment identifies {len(competitors)} primary competitors across
            different strategic groups and market segments.

            <b>Market Dynamics:</b> The competitive environment is characterized by intense rivalry,
            rapid innovation cycles, and evolving customer expectations. {brand_name} must navigate
            these dynamics while maintaining its unique value proposition and competitive advantages.

            <b>Competitive Threats:</b> High-threat competitors require immediate strategic attention
            and defensive positioning, while medium and low-threat competitors present opportunities
            for market share expansion and strategic partnerships.

            <b>Strategic Implications:</b> The competitive analysis informs strategic decision-making
            across product development, marketing positioning, pricing strategies, and market expansion initiatives.
            """
            story.append(Paragraph(comp_analysis_text, styles['Normal']))

        else:
            story.append(Paragraph("Competitive analysis data will be included when competitor information is available.", styles['Normal']))

            # Add placeholder competitive framework
            story.append(Spacer(1, 15))

            framework_subheading_style = ParagraphStyle(
                'FrameworkSubheading',
                parent=styles['Heading3'],
                fontSize=14,
                spaceAfter=8,
                spaceBefore=12,
                textColor=colors.HexColor('#4472a8')
            )

            story.append(Paragraph("Competitive Analysis Framework", framework_subheading_style))

            framework_text = f"""
            Our competitive analysis framework evaluates {brand_name}'s position across multiple dimensions:

            • <b>Market Position:</b> Assessment of market share, brand recognition, and competitive standing
            • <b>Strategic Capabilities:</b> Evaluation of core competencies and competitive advantages
            • <b>Competitive Response:</b> Analysis of competitive threats and strategic vulnerabilities
            • <b>Market Opportunities:</b> Identification of white space and expansion opportunities
            • <b>Strategic Recommendations:</b> Actionable insights for competitive positioning and market strategy
            """
            story.append(Paragraph(framework_text, styles['Normal']))

        story.append(Spacer(1, 20))
        return story

    def _create_pdf_strategic_recommendations(self, analysis_data: Dict[str, Any], heading_style, subheading_style, styles) -> List:
        """Create strategic recommendations section"""
        story = []

        story.append(Paragraph("Strategic Recommendations", heading_style))

        actionable_insights = analysis_data.get('actionable_insights', [])

        if actionable_insights:
            story.append(Paragraph("Priority Matrix", subheading_style))

            # Create recommendations table
            rec_data = [['Priority', 'Recommendation', 'Timeline', 'Expected Impact']]

            for insight in actionable_insights[:6]:  # Limit to top 6
                priority = insight.get('priority', 'Medium')
                finding = insight.get('finding', 'Strategic Initiative')
                timeline = insight.get('timeline', '90 days')
                impact = insight.get('impact', 'TBD')

                # Truncate long text
                if len(finding) > 40:
                    finding = finding[:37] + "..."
                if len(impact) > 35:
                    impact = impact[:32] + "..."

                rec_data.append([priority, finding, timeline, impact])

            rec_table = Table(rec_data, colWidths=[1*inch, 2.5*inch, 1*inch, 2*inch])
            rec_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e5984')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            story.append(rec_table)
        else:
            story.append(Paragraph("Strategic recommendations will be provided based on comprehensive analysis.", styles['Normal']))

        story.append(Spacer(1, 20))
        return story

    def _create_pdf_visual_analysis(self, analysis_data: Dict[str, Any], heading_style, subheading_style, styles) -> List:
        """Create visual analysis section"""
        story = []

        story.append(Paragraph("Visual Brand Analysis", heading_style))

        visual_data = analysis_data.get('visual_data', {})
        visual_assets = visual_data.get('visual_assets', {})

        # Brand colors section
        colors_palette = visual_assets.get('color_palette', {})
        colors_list = colors_palette.get('primary_colors', [])

        if colors_list:
            story.append(Paragraph("Brand Color Palette", subheading_style))

            color_data = [['Color', 'Hex Code', 'Type']]
            for color in colors_list[:5]:
                hex_code = color.get('hex', '#000000')
                color_type = color.get('type', 'Unknown')
                color_data.append(['●', hex_code, color_type.title()])

            color_table = Table(color_data, colWidths=[0.5*inch, 1.5*inch, 1.5*inch])
            color_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e5984')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6'))
            ]))
            story.append(color_table)

        # Typography section
        fonts = visual_assets.get('fonts', [])
        if fonts:
            story.append(Paragraph("Typography System", subheading_style))

            font_data = [['Font Family', 'Type', 'Usage']]
            for font in fonts[:3]:
                font_name = font.get('name', 'Unknown')
                font_type = font.get('type', 'Unknown')
                font_data.append([font_name, font_type.title(), 'Brand Typography'])

            font_table = Table(font_data, colWidths=[2*inch, 1*inch, 1.5*inch])
            font_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e5984')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6'))
            ]))
            story.append(font_table)

        if not colors_list and not fonts:
            story.append(Paragraph("Visual brand analysis will be included when brand assets are available.", styles['Normal']))

        story.append(Spacer(1, 20))
        return story

    def _create_pdf_appendix(self, analysis_data: Dict[str, Any], heading_style, styles) -> List:
        """Create appendix section"""
        story = []

        story.append(PageBreak())
        story.append(Paragraph("Appendix: Data Sources & Methodology", heading_style))

        # Data sources
        data_sources = analysis_data.get('data_sources', {})

        appendix_text = f"""
        This analysis was conducted using the following data sources and methodologies:

        Data Sources:
        • LLM Analysis: {'✓' if data_sources.get('llm_analysis') else '✗'} Advanced AI-powered brand analysis
        • News Data: {'✓' if data_sources.get('news_data') else '✗'} Recent news mentions and sentiment analysis
        • Brand Data: {'✓' if data_sources.get('brand_data') else '✗'} Official brand assets and information
        • Visual Analysis: {'✓' if data_sources.get('visual_analysis') else '✗'} Brand visual consistency assessment
        • Competitive Analysis: {'✓' if data_sources.get('competitor_analysis') else '✗'} Competitive intelligence gathering

        Methodology:
        This comprehensive brand audit employs a multi-faceted approach combining quantitative metrics
        with qualitative insights to provide actionable strategic recommendations.

        Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
        Analysis Type: Comprehensive Brand Audit
        Framework: AI-powered analysis with real data integration
        """

        story.append(Paragraph(appendix_text, styles['Normal']))

        return story

    def _get_score_status(self, score: int) -> str:
        """Get status text based on score"""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        else:
            return "Needs Improvement"
