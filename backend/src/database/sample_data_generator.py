"""
Sample Data Generation System for Brand Audit Tool
Creates realistic sample data for testing and development purposes
"""

import os
import sys
import uuid
import random
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from flask import Flask

# Add the backend directory to the path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from src.extensions import db
from src.models.user_model import User, Analysis, Brand, Report, UploadedFile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SampleDataGenerator:
    """Comprehensive sample data generation system"""
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app or self.create_app()
        self.generated_data = {}
        
        # Sample data templates
        self.brand_templates = [
            {
                "name": "Apple",
                "website": "https://apple.com",
                "industry": "Technology",
                "description": "Technology company known for innovative consumer electronics and software",
                "primary_color": "#000000",
                "founded_year": 1976,
                "headquarters": "Cupertino, CA"
            },
            {
                "name": "Nike",
                "website": "https://nike.com",
                "industry": "Sportswear",
                "description": "Global leader in athletic footwear, apparel, and equipment",
                "primary_color": "#FF6900",
                "founded_year": 1964,
                "headquarters": "Beaverton, OR"
            },
            {
                "name": "Coca-Cola",
                "website": "https://coca-cola.com",
                "industry": "Beverages",
                "description": "World's largest beverage company and soft drink manufacturer",
                "primary_color": "#FF0000",
                "founded_year": 1886,
                "headquarters": "Atlanta, GA"
            },
            {
                "name": "Tesla",
                "website": "https://tesla.com",
                "industry": "Automotive",
                "description": "Electric vehicle and clean energy company",
                "primary_color": "#CC0000",
                "founded_year": 2003,
                "headquarters": "Austin, TX"
            },
            {
                "name": "Amazon",
                "website": "https://amazon.com",
                "industry": "E-commerce",
                "description": "Multinational technology company focusing on e-commerce and cloud computing",
                "primary_color": "#FF9900",
                "founded_year": 1994,
                "headquarters": "Seattle, WA"
            },
            {
                "name": "Google",
                "website": "https://google.com",
                "industry": "Technology",
                "description": "Multinational technology company specializing in Internet services",
                "primary_color": "#4285F4",
                "founded_year": 1998,
                "headquarters": "Mountain View, CA"
            },
            {
                "name": "Microsoft",
                "website": "https://microsoft.com",
                "industry": "Technology",
                "description": "Multinational technology corporation producing software and hardware",
                "primary_color": "#00BCF2",
                "founded_year": 1975,
                "headquarters": "Redmond, WA"
            },
            {
                "name": "McDonald's",
                "website": "https://mcdonalds.com",
                "industry": "Food Service",
                "description": "World's largest restaurant chain serving fast food",
                "primary_color": "#FFC72C",
                "founded_year": 1940,
                "headquarters": "Chicago, IL"
            },
            {
                "name": "Starbucks",
                "website": "https://starbucks.com",
                "industry": "Food & Beverage",
                "description": "American multinational chain of coffeehouses and roastery reserves",
                "primary_color": "#00704A",
                "founded_year": 1971,
                "headquarters": "Seattle, WA"
            },
            {
                "name": "Netflix",
                "website": "https://netflix.com",
                "industry": "Entertainment",
                "description": "Streaming entertainment service with TV series and films",
                "primary_color": "#E50914",
                "founded_year": 1997,
                "headquarters": "Los Gatos, CA"
            }
        ]
        
        self.user_templates = [
            {"name": "John Smith", "company": "Marketing Agency Pro", "role": "admin"},
            {"name": "Sarah Johnson", "company": "Brand Strategy Inc", "role": "user"},
            {"name": "Michael Brown", "company": "Creative Solutions LLC", "role": "user"},
            {"name": "Emily Davis", "company": "Digital Marketing Hub", "role": "user"},
            {"name": "David Wilson", "company": "Brand Consultants Co", "role": "user"},
            {"name": "Lisa Anderson", "company": "Strategic Branding", "role": "user"},
            {"name": "Robert Taylor", "company": "Marketing Insights", "role": "user"},
            {"name": "Jennifer Martinez", "company": "Brand Analytics", "role": "user"}
        ]
        
        self.analysis_types_options = [
            ["brand_positioning", "competitor_analysis"],
            ["market_research", "brand_positioning"],
            ["competitor_analysis", "market_research", "brand_positioning"],
            ["brand_positioning"],
            ["competitor_analysis"],
            ["market_research"],
            ["brand_positioning", "market_research"],
            ["competitor_analysis", "brand_positioning", "market_research"]
        ]
        
        self.status_options = ["completed", "processing", "failed", "started"]
        self.report_types = ["pdf", "powerpoint", "markdown"]
        self.file_types = ["logo", "screenshot", "typography", "color_palette", "marketing_material"]
    
    def create_app(self) -> Flask:
        """Create Flask app for data generation"""
        app = Flask(__name__)
        
        # Database configuration
        basedir = os.path.abspath(os.path.dirname(__file__))
        database_url = os.environ.get('DATABASE_URL') or f'sqlite:///{os.path.join(basedir, "app.db")}'
        
        app.config.update({
            'SQLALCHEMY_DATABASE_URI': database_url,
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-secret-key')
        })
        
        db.init_app(app)
        return app
    
    def generate_users(self, count: int = 8) -> List[User]:
        """Generate sample users"""
        users = []
        
        with self.app.app_context():
            for i, template in enumerate(self.user_templates[:count]):
                # Check if user already exists
                existing_user = User.query.filter_by(email=f"{template['name'].lower().replace(' ', '.')}@example.com").first()
                if existing_user:
                    users.append(existing_user)
                    continue
                
                user = User(
                    id=str(uuid.uuid4()),
                    email=f"{template['name'].lower().replace(' ', '.')}@example.com",
                    name=template['name'],
                    company=template['company'],
                    role=template['role'],
                    is_active=True,
                    is_verified=random.choice([True, False]),
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 365)),
                    last_login=datetime.utcnow() - timedelta(days=random.randint(0, 30)) if random.choice([True, False]) else None
                )
                user.set_password('password123')
                
                db.session.add(user)
                users.append(user)
            
            db.session.commit()
            logger.info(f"✅ Generated {len(users)} users")
            
        return users
    
    def generate_brands(self, count: int = 10) -> List[Brand]:
        """Generate sample brands"""
        brands = []
        
        with self.app.app_context():
            for template in self.brand_templates[:count]:
                # Check if brand already exists
                existing_brand = Brand.query.filter_by(name=template['name']).first()
                if existing_brand:
                    brands.append(existing_brand)
                    continue
                
                brand = Brand(
                    id=str(uuid.uuid4()),
                    name=template['name'],
                    website=template['website'],
                    industry=template['industry'],
                    description=template['description'],
                    primary_color=template['primary_color'],
                    founded_year=template['founded_year'],
                    headquarters=template['headquarters'],
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 180))
                )
                
                db.session.add(brand)
                brands.append(brand)
            
            db.session.commit()
            logger.info(f"✅ Generated {len(brands)} brands")
            
        return brands
    
    def generate_analyses(self, users: List[User], brands: List[Brand], count_per_brand: int = 2) -> List[Analysis]:
        """Generate sample analyses"""
        analyses = []
        
        with self.app.app_context():
            for brand in brands:
                for i in range(count_per_brand):
                    user = random.choice(users)
                    analysis_types = random.choice(self.analysis_types_options)
                    status = random.choice(self.status_options)
                    
                    # Generate realistic results based on analysis types
                    results = self._generate_analysis_results(brand, analysis_types)
                    
                    created_date = datetime.utcnow() - timedelta(days=random.randint(1, 90))
                    completed_date = created_date + timedelta(hours=random.randint(1, 48)) if status == "completed" else None
                    
                    analysis = Analysis(
                        id=f"analysis-{brand.name.lower().replace(' ', '-')}-{i+1}-{int(created_date.timestamp())}",
                        user_id=user.id,
                        brand_id=brand.id,
                        brand_name=brand.name,
                        analysis_types=analysis_types,
                        status=status,
                        progress=100 if status == "completed" else random.randint(10, 90) if status == "processing" else 0,
                        results=results if status == "completed" else None,
                        analysis_version="1.0",
                        data_sources=["web_scraping", "api_data", "social_media"] if status == "completed" else [],
                        processing_time_seconds=random.uniform(30.0, 120.0) if status == "completed" else None,
                        concurrent_processing_used=random.choice([True, False]),
                        cache_hit_rate=random.uniform(0.3, 0.9) if status == "completed" else None,
                        created_at=created_date,
                        completed_at=completed_date,
                        error_message="Sample error message" if status == "failed" else None
                    )
                    
                    db.session.add(analysis)
                    analyses.append(analysis)
            
            db.session.commit()
            logger.info(f"✅ Generated {len(analyses)} analyses")
            
        return analyses

    def _generate_analysis_results(self, brand: Brand, analysis_types: List[str]) -> Dict[str, Any]:
        """Generate realistic analysis results based on brand and analysis types"""
        results = {}

        if "brand_positioning" in analysis_types:
            results["brand_positioning"] = {
                "strength": random.choice(["Very Strong", "Strong", "Moderate", "Weak"]),
                "market_position": random.choice(["Leader", "Challenger", "Follower", "Niche"]),
                "brand_value": random.choice(["Premium", "Mass Market", "Value", "Luxury"]),
                "differentiation": random.choice(["High", "Medium", "Low"]),
                "brand_equity_score": random.randint(60, 95),
                "key_attributes": random.sample([
                    "Innovation", "Quality", "Reliability", "Trust", "Style",
                    "Performance", "Value", "Sustainability", "Heritage", "Convenience"
                ], k=random.randint(3, 6))
            }

        if "competitor_analysis" in analysis_types:
            competitors = self._get_competitors_for_industry(brand.industry)
            results["competitor_analysis"] = {
                "main_competitors": random.sample(competitors, k=min(3, len(competitors))),
                "competitive_advantage": random.choice([
                    "Innovation", "Brand Recognition", "Price", "Quality",
                    "Distribution", "Customer Service", "Technology"
                ]),
                "market_share_estimate": f"{random.randint(5, 35)}%",
                "competitive_threats": random.sample([
                    "New entrants", "Price competition", "Technology disruption",
                    "Changing consumer preferences", "Regulatory changes"
                ], k=random.randint(2, 4)),
                "opportunities": random.sample([
                    "Market expansion", "Product innovation", "Digital transformation",
                    "Sustainability focus", "Partnership opportunities"
                ], k=random.randint(2, 3))
            }

        if "market_research" in analysis_types:
            results["market_research"] = {
                "market_size": random.choice(["Large", "Medium", "Small", "Niche"]),
                "growth_rate": f"{random.randint(1, 15)}%",
                "target_demographic": self._get_target_demographic(brand.industry),
                "market_trends": random.sample([
                    "Digital transformation", "Sustainability focus", "Personalization",
                    "Mobile-first approach", "Social commerce", "AI integration",
                    "Health consciousness", "Remote work impact"
                ], k=random.randint(3, 5)),
                "consumer_sentiment": random.choice(["Very Positive", "Positive", "Neutral", "Negative"]),
                "price_sensitivity": random.choice(["Low", "Medium", "High"]),
                "brand_awareness": f"{random.randint(40, 95)}%"
            }

        return results

    def _get_competitors_for_industry(self, industry: str) -> List[str]:
        """Get realistic competitors based on industry"""
        competitor_map = {
            "Technology": ["Apple", "Google", "Microsoft", "Samsung", "Amazon", "Meta", "IBM"],
            "Sportswear": ["Nike", "Adidas", "Puma", "Under Armour", "Reebok", "New Balance"],
            "Beverages": ["Coca-Cola", "Pepsi", "Dr Pepper", "Monster", "Red Bull", "Nestlé"],
            "Automotive": ["Tesla", "Toyota", "Ford", "GM", "BMW", "Mercedes", "Volkswagen"],
            "E-commerce": ["Amazon", "eBay", "Alibaba", "Shopify", "Walmart", "Target"],
            "Food Service": ["McDonald's", "Burger King", "KFC", "Subway", "Taco Bell", "Pizza Hut"],
            "Food & Beverage": ["Starbucks", "Dunkin'", "Costa Coffee", "Tim Hortons", "Peet's"],
            "Entertainment": ["Netflix", "Disney+", "Amazon Prime", "Hulu", "HBO Max", "Apple TV+"]
        }
        return competitor_map.get(industry, ["Competitor A", "Competitor B", "Competitor C"])

    def _get_target_demographic(self, industry: str) -> str:
        """Get realistic target demographic based on industry"""
        demographic_map = {
            "Technology": "Tech-savvy consumers aged 25-45",
            "Sportswear": "Athletes and fitness enthusiasts aged 18-40",
            "Beverages": "General consumers aged 16-65",
            "Automotive": "Environmentally conscious consumers aged 30-55",
            "E-commerce": "Online shoppers aged 20-50",
            "Food Service": "Families and young adults aged 18-45",
            "Food & Beverage": "Coffee enthusiasts aged 25-50",
            "Entertainment": "Streaming content consumers aged 18-55"
        }
        return demographic_map.get(industry, "General consumers aged 18-65")

    def generate_reports(self, analyses: List[Analysis]) -> List[Report]:
        """Generate sample reports for analyses"""
        reports = []

        with self.app.app_context():
            for analysis in analyses:
                if analysis.status == "completed" and random.choice([True, False, True]):  # 66% chance
                    report_type = random.choice(self.report_types)

                    report = Report(
                        id=str(uuid.uuid4()),
                        analysis_id=analysis.id,
                        user_id=analysis.user_id,
                        report_type=report_type,
                        filename=f"{analysis.brand_name.lower().replace(' ', '_')}_report.{report_type}",
                        file_path=f"/reports/{analysis.brand_name.lower().replace(' ', '_')}_report.{report_type}",
                        file_size=random.randint(1024, 10240),  # 1KB to 10KB
                        title=f"{analysis.brand_name} Brand Audit Report",
                        description=f"Comprehensive brand audit report for {analysis.brand_name}",
                        pages_count=random.randint(15, 50),
                        status="completed",
                        download_count=random.randint(0, 25),
                        last_downloaded=datetime.utcnow() - timedelta(days=random.randint(0, 30)) if random.choice([True, False]) else None,
                        created_at=analysis.completed_at + timedelta(minutes=random.randint(5, 60)) if analysis.completed_at else datetime.utcnow()
                    )

                    db.session.add(report)
                    reports.append(report)

            db.session.commit()
            logger.info(f"✅ Generated {len(reports)} reports")

        return reports

    def generate_uploaded_files(self, users: List[User], analyses: List[Analysis], count_per_analysis: int = 2) -> List[UploadedFile]:
        """Generate sample uploaded files"""
        uploaded_files = []

        with self.app.app_context():
            for analysis in analyses:
                if random.choice([True, False, True]):  # 66% chance of having files
                    for i in range(random.randint(1, count_per_analysis)):
                        file_type = random.choice(self.file_types)
                        file_extension = self._get_file_extension(file_type)

                        uploaded_file = UploadedFile(
                            id=str(uuid.uuid4()),
                            user_id=analysis.user_id,
                            analysis_id=analysis.id,
                            filename=f"{analysis.brand_name.lower().replace(' ', '_')}_{file_type}_{i+1}.{file_extension}",
                            original_filename=f"original_{file_type}_{i+1}.{file_extension}",
                            file_path=f"/uploads/{analysis.brand_name.lower().replace(' ', '_')}_{file_type}_{i+1}.{file_extension}",
                            file_size=random.randint(512, 5120),  # 512B to 5KB
                            mime_type=self._get_mime_type(file_extension),
                            file_type=file_type,
                            created_at=analysis.created_at + timedelta(minutes=random.randint(1, 30))
                        )

                        db.session.add(uploaded_file)
                        uploaded_files.append(uploaded_file)

            db.session.commit()
            logger.info(f"✅ Generated {len(uploaded_files)} uploaded files")

        return uploaded_files

    def _get_file_extension(self, file_type: str) -> str:
        """Get appropriate file extension for file type"""
        extension_map = {
            "logo": random.choice(["png", "svg", "jpg"]),
            "screenshot": random.choice(["png", "jpg"]),
            "typography": random.choice(["ttf", "otf", "woff"]),
            "color_palette": random.choice(["png", "pdf"]),
            "marketing_material": random.choice(["pdf", "png", "jpg"])
        }
        return extension_map.get(file_type, "png")

    def _get_mime_type(self, extension: str) -> str:
        """Get MIME type for file extension"""
        mime_map = {
            "png": "image/png",
            "jpg": "image/jpeg",
            "svg": "image/svg+xml",
            "pdf": "application/pdf",
            "ttf": "font/ttf",
            "otf": "font/otf",
            "woff": "font/woff"
        }
        return mime_map.get(extension, "application/octet-stream")

    def generate_comprehensive_sample_data(self,
                                         user_count: int = 8,
                                         brand_count: int = 10,
                                         analyses_per_brand: int = 2,
                                         files_per_analysis: int = 2) -> Dict[str, Any]:
        """Generate comprehensive sample data for the entire system"""
        logger.info("🎲 Starting comprehensive sample data generation...")

        results = {
            'success': True,
            'generated_counts': {},
            'errors': [],
            'timestamp': datetime.utcnow().isoformat()
        }

        try:
            with self.app.app_context():
                # Ensure tables exist
                db.create_all()

                # Generate data in dependency order
                logger.info("   Generating users...")
                users = self.generate_users(user_count)
                results['generated_counts']['users'] = len(users)

                logger.info("   Generating brands...")
                brands = self.generate_brands(brand_count)
                results['generated_counts']['brands'] = len(brands)

                logger.info("   Generating analyses...")
                analyses = self.generate_analyses(users, brands, analyses_per_brand)
                results['generated_counts']['analyses'] = len(analyses)

                logger.info("   Generating reports...")
                reports = self.generate_reports(analyses)
                results['generated_counts']['reports'] = len(reports)

                logger.info("   Generating uploaded files...")
                uploaded_files = self.generate_uploaded_files(users, analyses, files_per_analysis)
                results['generated_counts']['uploaded_files'] = len(uploaded_files)

                # Store generated data for reference
                self.generated_data = {
                    'users': users,
                    'brands': brands,
                    'analyses': analyses,
                    'reports': reports,
                    'uploaded_files': uploaded_files
                }

                logger.info("✅ Comprehensive sample data generation completed successfully!")

        except Exception as e:
            logger.error(f"❌ Sample data generation failed: {e}")
            results['success'] = False
            results['errors'].append(str(e))

        return results

    def clear_all_data(self) -> bool:
        """Clear all existing data (use with caution!)"""
        try:
            with self.app.app_context():
                logger.info("🗑️ Clearing all existing data...")

                # Delete in reverse dependency order
                UploadedFile.query.delete()
                Report.query.delete()
                Analysis.query.delete()
                Brand.query.delete()
                User.query.delete()

                db.session.commit()
                logger.info("✅ All data cleared successfully")
                return True

        except Exception as e:
            logger.error(f"❌ Data clearing failed: {e}")
            db.session.rollback()
            return False

    def get_generation_summary(self) -> Dict[str, Any]:
        """Get summary of generated data"""
        with self.app.app_context():
            return {
                'users': User.query.count(),
                'brands': Brand.query.count(),
                'analyses': Analysis.query.count(),
                'reports': Report.query.count(),
                'uploaded_files': UploadedFile.query.count(),
                'completed_analyses': Analysis.query.filter_by(status='completed').count(),
                'failed_analyses': Analysis.query.filter_by(status='failed').count(),
                'processing_analyses': Analysis.query.filter_by(status='processing').count()
            }


def generate_sample_data(clear_existing: bool = False,
                        user_count: int = 8,
                        brand_count: int = 10,
                        analyses_per_brand: int = 2,
                        files_per_analysis: int = 2):
    """Generate sample data (standalone function)"""
    print("🎲 Brand Audit Tool - Sample Data Generation")
    print("=" * 50)

    generator = SampleDataGenerator()

    # Clear existing data if requested
    if clear_existing:
        print("🗑️ Clearing existing data...")
        if generator.clear_all_data():
            print("   ✅ Existing data cleared")
        else:
            print("   ❌ Failed to clear existing data")
            return False

    # Generate comprehensive sample data
    results = generator.generate_comprehensive_sample_data(
        user_count=user_count,
        brand_count=brand_count,
        analyses_per_brand=analyses_per_brand,
        files_per_analysis=files_per_analysis
    )

    # Print results
    print(f"\n📊 Generation Results:")
    print(f"   Success: {'✅' if results['success'] else '❌'}")

    if results['success']:
        counts = results['generated_counts']
        print(f"   Generated:")
        print(f"     - Users: {counts.get('users', 0)}")
        print(f"     - Brands: {counts.get('brands', 0)}")
        print(f"     - Analyses: {counts.get('analyses', 0)}")
        print(f"     - Reports: {counts.get('reports', 0)}")
        print(f"     - Uploaded Files: {counts.get('uploaded_files', 0)}")

        # Show summary
        summary = generator.get_generation_summary()
        print(f"\n📈 Database Summary:")
        print(f"     - Total Users: {summary['users']}")
        print(f"     - Total Brands: {summary['brands']}")
        print(f"     - Total Analyses: {summary['analyses']}")
        print(f"       • Completed: {summary['completed_analyses']}")
        print(f"       • Processing: {summary['processing_analyses']}")
        print(f"       • Failed: {summary['failed_analyses']}")
        print(f"     - Total Reports: {summary['reports']}")
        print(f"     - Total Files: {summary['uploaded_files']}")

    if results['errors']:
        print(f"\n⚠️ Errors encountered:")
        for error in results['errors']:
            print(f"   - {error}")

    print("\n" + "=" * 50)
    if results['success']:
        print("🎉 Sample data generation completed successfully!")
        print("\n💡 Next steps:")
        print("   1. Test the application with the generated data")
        print("   2. Verify all relationships are working correctly")
        print("   3. Use the data for development and testing")
    else:
        print("⚠️ Sample data generation failed. Please review the errors above.")

    return results['success']


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Generate sample data for Brand Audit Tool')
    parser.add_argument('--clear', action='store_true', help='Clear existing data before generating')
    parser.add_argument('--users', type=int, default=8, help='Number of users to generate')
    parser.add_argument('--brands', type=int, default=10, help='Number of brands to generate')
    parser.add_argument('--analyses-per-brand', type=int, default=2, help='Number of analyses per brand')
    parser.add_argument('--files-per-analysis', type=int, default=2, help='Number of files per analysis')

    args = parser.parse_args()

    success = generate_sample_data(
        clear_existing=args.clear,
        user_count=args.users,
        brand_count=args.brands,
        analyses_per_brand=args.analyses_per_brand,
        files_per_analysis=args.files_per_analysis
    )

    sys.exit(0 if success else 1)
