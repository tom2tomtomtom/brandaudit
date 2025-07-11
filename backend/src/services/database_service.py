"""
Database Service for Brand Audit Tool
Handles database operations for Analysis, Brand, and Report entities
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from src.extensions import db
from src.models.user_model import Analysis, Brand, Report, User


class DatabaseService:
    """Service for database operations"""

    @staticmethod
    def create_analysis(brand_name: str, analysis_types: List[str] = None, user_id: str = None) -> Analysis:
        """Create a new analysis record"""
        
        # Generate unique ID
        analysis_id = f"analysis-{int(datetime.utcnow().timestamp())}"
        
        # Find or create brand
        brand = Brand.query.filter_by(name=brand_name).first()
        if not brand:
            brand = Brand(
                id=str(uuid.uuid4()),
                name=brand_name,
                created_at=datetime.utcnow()
            )
            db.session.add(brand)
            db.session.flush()  # Get the brand ID
        
        # Create analysis
        analysis = Analysis(
            id=analysis_id,
            user_id=user_id,
            brand_id=brand.id,
            brand_name=brand_name,
            analysis_types=analysis_types or [],
            status="started",
            created_at=datetime.utcnow()
        )
        
        db.session.add(analysis)
        db.session.commit()
        
        return analysis

    @staticmethod
    def get_analysis(analysis_id: str) -> Optional[Analysis]:
        """Get analysis by ID"""
        return Analysis.query.filter_by(id=analysis_id).first()

    @staticmethod
    def update_analysis_status(analysis_id: str, status: str, error_message: str = None, progress: int = None) -> bool:
        """Update analysis status"""
        analysis = Analysis.query.filter_by(id=analysis_id).first()
        if not analysis:
            return False
        
        analysis.update_status(status, error_message, progress)
        return True

    @staticmethod
    def update_analysis_results(analysis_id: str, results: Dict[str, Any]) -> bool:
        """Update analysis results"""
        analysis = Analysis.query.filter_by(id=analysis_id).first()
        if not analysis:
            return False
        
        analysis.update_results(results)
        return True

    @staticmethod
    def get_user_analyses(user_id: str, limit: int = 50) -> List[Analysis]:
        """Get analyses for a user"""
        return Analysis.query.filter_by(user_id=user_id).order_by(Analysis.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_recent_analyses(limit: int = 20) -> List[Analysis]:
        """Get recent analyses (for anonymous users)"""
        return Analysis.query.order_by(Analysis.created_at.desc()).limit(limit).all()

    @staticmethod
    def create_brand(name: str, website: str = None, industry: str = None, **kwargs) -> Brand:
        """Create a new brand record"""
        brand = Brand(
            id=str(uuid.uuid4()),
            name=name,
            website=website,
            industry=industry,
            **kwargs
        )
        
        db.session.add(brand)
        db.session.commit()
        
        return brand

    @staticmethod
    def get_brand(brand_id: str) -> Optional[Brand]:
        """Get brand by ID"""
        return Brand.query.filter_by(id=brand_id).first()

    @staticmethod
    def get_brand_by_name(name: str) -> Optional[Brand]:
        """Get brand by name"""
        return Brand.query.filter_by(name=name).first()

    @staticmethod
    def update_brand(brand_id: str, **kwargs) -> bool:
        """Update brand information"""
        brand = Brand.query.filter_by(id=brand_id).first()
        if not brand:
            return False
        
        for key, value in kwargs.items():
            if hasattr(brand, key):
                setattr(brand, key, value)
        
        brand.updated_at = datetime.utcnow()
        db.session.commit()
        return True

    @staticmethod
    def create_report(analysis_id: str, report_type: str, filename: str, file_path: str, 
                     title: str, user_id: str = None, **kwargs) -> Report:
        """Create a new report record"""
        report = Report(
            id=str(uuid.uuid4()),
            analysis_id=analysis_id,
            user_id=user_id,
            report_type=report_type,
            filename=filename,
            file_path=file_path,
            title=title,
            **kwargs
        )
        
        db.session.add(report)
        db.session.commit()
        
        return report

    @staticmethod
    def get_report(report_id: str) -> Optional[Report]:
        """Get report by ID"""
        return Report.query.filter_by(id=report_id).first()

    @staticmethod
    def get_analysis_reports(analysis_id: str) -> List[Report]:
        """Get all reports for an analysis"""
        return Report.query.filter_by(analysis_id=analysis_id).all()

    @staticmethod
    def update_report_status(report_id: str, status: str, error_message: str = None) -> bool:
        """Update report status"""
        report = Report.query.filter_by(id=report_id).first()
        if not report:
            return False
        
        report.update_status(status, error_message)
        return True

    @staticmethod
    def increment_report_download(report_id: str) -> bool:
        """Increment report download count"""
        report = Report.query.filter_by(id=report_id).first()
        if not report:
            return False
        
        report.increment_download()
        return True

    @staticmethod
    def cleanup_old_analyses(days: int = 30) -> int:
        """Clean up old analyses (for maintenance)"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        old_analyses = Analysis.query.filter(Analysis.created_at < cutoff_date).all()
        
        count = len(old_analyses)
        for analysis in old_analyses:
            db.session.delete(analysis)
        
        db.session.commit()
        return count

    @staticmethod
    def get_database_stats() -> Dict[str, int]:
        """Get database statistics"""
        return {
            "total_analyses": Analysis.query.count(),
            "total_brands": Brand.query.count(),
            "total_reports": Report.query.count(),
            "total_users": User.query.count(),
            "completed_analyses": Analysis.query.filter_by(status="completed").count(),
            "failed_analyses": Analysis.query.filter_by(status="failed").count(),
        }

    @staticmethod
    def search_brands(query: str, limit: int = 10) -> List[Brand]:
        """Search brands by name"""
        return Brand.query.filter(Brand.name.ilike(f"%{query}%")).limit(limit).all()

    @staticmethod
    def get_popular_brands(limit: int = 10) -> List[Dict[str, Any]]:
        """Get most analyzed brands"""
        from sqlalchemy import func
        
        results = db.session.query(
            Brand.id,
            Brand.name,
            func.count(Analysis.id).label('analysis_count')
        ).join(Analysis).group_by(Brand.id, Brand.name).order_by(
            func.count(Analysis.id).desc()
        ).limit(limit).all()
        
        return [
            {
                "brand_id": result.id,
                "brand_name": result.name,
                "analysis_count": result.analysis_count
            }
            for result in results
        ]
