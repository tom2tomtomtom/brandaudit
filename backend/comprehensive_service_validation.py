#!/usr/bin/env python3
"""
Comprehensive Service Validation Script for Flask Brand Audit App
Tests all service imports, initialization, database connectivity, API services,
Playwright capabilities, and presentation generation functionality.
"""

import os
import sys
import json
import time
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ValidationStatus(Enum):
    PASS = "✅ PASS"
    FAIL = "❌ FAIL"
    WARNING = "⚠️ WARNING"
    SKIP = "⏭️ SKIP"

@dataclass
class ValidationResult:
    service_name: str
    status: ValidationStatus
    message: str
    details: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = None

class ServiceValidator:
    """Comprehensive service validation system"""
    
    def __init__(self):
        self.results: List[ValidationResult] = []
        self.start_time = datetime.now()
        
    def add_result(self, service_name: str, status: ValidationStatus, message: str, 
                   details: Optional[Dict[str, Any]] = None, execution_time: Optional[float] = None):
        """Add validation result"""
        self.results.append(ValidationResult(
            service_name=service_name,
            status=status,
            message=message,
            details=details,
            execution_time=execution_time
        ))
    
    def validate_service_imports(self) -> None:
        """Test all service imports and initialization"""
        print("\n🔍 TESTING SERVICE IMPORTS AND INITIALIZATION")
        print("=" * 60)
        
        # Core services to test
        services_to_test = [
            ('database_service', 'src.services.database_service', 'DatabaseService'),
            ('api_validation_service', 'src.services.api_validation_service', 'api_validator'),
            ('presentation_service', 'src.services.presentation_service', 'PresentationService'),
            ('visual_analysis_service', 'src.services.visual_analysis_service', 'VisualAnalysisService'),
            ('llm_service', 'src.services.llm_service', 'LLMService'),
            ('news_service', 'src.services.news_service', 'NewsService'),
            ('brand_data_service', 'src.services.brand_data_service', 'BrandDataService'),
            ('campaign_analysis_service', 'src.services.campaign_analysis_service', 'CampaignAnalysisService'),
            ('competitor_analysis_service', 'src.services.competitor_analysis_service', 'CompetitorAnalysisService'),
            ('strategic_synthesis_service', 'src.services.strategic_synthesis_service', 'StrategicSynthesisService'),
            ('async_analysis_service', 'src.services.async_analysis_service', 'AsyncAnalysisService'),
            ('websocket_service', 'src.services.websocket_service', 'WebSocketService'),
            ('health_service', 'src.services.health_service', 'HealthService'),
            ('monitoring_service', 'src.services.monitoring_service', 'MonitoringService'),
            ('error_management_service', 'src.services.error_management_service', 'ErrorManagementService'),
            ('intelligent_cache_service', 'src.services.intelligent_cache_service', 'IntelligentCacheService'),
            ('image_optimization_service', 'src.services.image_optimization_service', 'ImageOptimizationService'),
            ('database_optimization_service', 'src.services.database_optimization_service', 'DatabaseOptimizationService'),
            ('enhanced_retry_service', 'src.services.enhanced_retry_service', 'EnhancedRetryService'),
            ('fallback_service', 'src.services.fallback_service', 'FallbackService'),
            ('social_media_service', 'src.services.social_media_service', 'SocialMediaService'),
            ('report_generation_service', 'src.services.report_generation_service', 'ReportGenerationService'),
            ('analysis_service', 'src.services.analysis_service', None),  # Celery task module
        ]
        
        for service_name, module_path, class_name in services_to_test:
            start_time = time.time()
            try:
                # Import the module
                module = __import__(module_path, fromlist=[class_name] if class_name else [''])
                
                if class_name and hasattr(module, class_name):
                    # Try to instantiate the class if it exists
                    service_class = getattr(module, class_name)
                    if class_name in ['api_validator']:
                        # These are already instantiated
                        instance = service_class
                    else:
                        # Try to instantiate
                        instance = service_class()
                    
                    execution_time = time.time() - start_time
                    self.add_result(
                        service_name, 
                        ValidationStatus.PASS, 
                        f"Successfully imported and initialized {class_name}",
                        {"module": module_path, "class": class_name},
                        execution_time
                    )
                else:
                    execution_time = time.time() - start_time
                    self.add_result(
                        service_name, 
                        ValidationStatus.PASS, 
                        f"Successfully imported module {module_path}",
                        {"module": module_path},
                        execution_time
                    )
                    
            except ImportError as e:
                execution_time = time.time() - start_time
                self.add_result(
                    service_name, 
                    ValidationStatus.FAIL, 
                    f"Import failed: {str(e)}",
                    {"error": str(e), "module": module_path},
                    execution_time
                )
            except Exception as e:
                execution_time = time.time() - start_time
                self.add_result(
                    service_name, 
                    ValidationStatus.WARNING, 
                    f"Import succeeded but initialization failed: {str(e)}",
                    {"error": str(e), "module": module_path},
                    execution_time
                )
    
    def validate_database_connectivity(self) -> None:
        """Test database connection and model creation"""
        print("\n🗄️ TESTING DATABASE CONNECTIVITY")
        print("=" * 60)
        
        start_time = time.time()
        try:
            # Test Flask app creation and database initialization
            from flask import Flask
            from src.extensions import db
            from src.models.user_model import User, Analysis, Brand, Report
            
            # Create test app
            app = Flask(__name__)
            basedir = os.path.abspath(os.path.dirname(__file__))
            app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "test_validation.db")}'
            app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
            app.config['SECRET_KEY'] = 'test-secret-key'
            
            # Initialize database
            db.init_app(app)
            
            with app.app_context():
                # Create tables
                db.create_all()
                
                # Test database service
                from src.services.database_service import DatabaseService
                
                # Test basic operations
                stats = DatabaseService.get_database_stats()
                
                execution_time = time.time() - start_time
                self.add_result(
                    "database_connectivity", 
                    ValidationStatus.PASS, 
                    "Database connection and model creation successful",
                    {
                        "database_stats": stats,
                        "models_tested": ["User", "Analysis", "Brand", "Report"]
                    },
                    execution_time
                )
                
                # Clean up test database
                os.remove(os.path.join(basedir, "test_validation.db"))
                
        except Exception as e:
            execution_time = time.time() - start_time
            self.add_result(
                "database_connectivity", 
                ValidationStatus.FAIL, 
                f"Database connectivity test failed: {str(e)}",
                {"error": str(e)},
                execution_time
            )
    
    def validate_api_services(self) -> None:
        """Test API service connectivity"""
        print("\n🌐 TESTING API SERVICE CONNECTIVITY")
        print("=" * 60)
        
        start_time = time.time()
        try:
            from src.services.api_validation_service import api_validator
            
            # Test all configured APIs
            api_results = api_validator.validate_all_apis(force_check=True)
            
            execution_time = time.time() - start_time
            
            # Check individual API statuses
            healthy_apis = []
            unhealthy_apis = []
            
            for api_name, health_info in api_results.items():
                if health_info.status.value in ['healthy', 'degraded']:
                    healthy_apis.append(api_name)
                else:
                    unhealthy_apis.append(api_name)
            
            if len(healthy_apis) > 0:
                status = ValidationStatus.PASS if len(unhealthy_apis) == 0 else ValidationStatus.WARNING
                message = f"API validation completed. Healthy: {len(healthy_apis)}, Unhealthy: {len(unhealthy_apis)}"
            else:
                status = ValidationStatus.FAIL
                message = "All API services are unhealthy"
            
            self.add_result(
                "api_services", 
                status, 
                message,
                {
                    "healthy_apis": healthy_apis,
                    "unhealthy_apis": unhealthy_apis,
                    "detailed_results": {api: health.status.value for api, health in api_results.items()}
                },
                execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.add_result(
                "api_services",
                ValidationStatus.FAIL,
                f"API service validation failed: {str(e)}",
                {"error": str(e)},
                execution_time
            )

    def validate_playwright_capabilities(self) -> None:
        """Test Playwright and visual analysis capabilities"""
        print("\n🎭 TESTING PLAYWRIGHT AND VISUAL ANALYSIS")
        print("=" * 60)

        start_time = time.time()
        try:
            # Test Playwright installation
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                # Test browser launch
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                # Test basic navigation
                page.goto("https://example.com")
                title = page.title()

                browser.close()

                # Test visual analysis service
                from src.services.visual_analysis_service import VisualAnalysisService
                visual_service = VisualAnalysisService()

                # Test service capabilities
                capabilities = visual_service.get_capabilities()

                execution_time = time.time() - start_time
                self.add_result(
                    "playwright_visual",
                    ValidationStatus.PASS,
                    f"Playwright and visual analysis working. Browser title: {title}",
                    {
                        "browser_test": "success",
                        "page_title": title,
                        "visual_capabilities": capabilities
                    },
                    execution_time
                )

        except ImportError as e:
            execution_time = time.time() - start_time
            self.add_result(
                "playwright_visual",
                ValidationStatus.FAIL,
                f"Playwright not installed or configured: {str(e)}",
                {"error": str(e)},
                execution_time
            )
        except Exception as e:
            execution_time = time.time() - start_time
            self.add_result(
                "playwright_visual",
                ValidationStatus.WARNING,
                f"Playwright available but test failed: {str(e)}",
                {"error": str(e)},
                execution_time
            )

    def validate_presentation_generation(self) -> None:
        """Test presentation and PDF generation functionality"""
        print("\n📊 TESTING PRESENTATION AND PDF GENERATION")
        print("=" * 60)

        start_time = time.time()
        try:
            from src.services.presentation_service import PresentationService

            # Initialize presentation service
            presentation_service = PresentationService()

            # Test service capabilities
            capabilities = presentation_service.get_capabilities()

            # Test data for presentation generation
            test_data = {
                "brand_overview": {
                    "name": "Test Brand",
                    "industry": "Technology",
                    "description": "A test brand for validation"
                },
                "competitive_analysis": {
                    "competitors": ["Competitor A", "Competitor B"],
                    "market_position": "Strong"
                },
                "visual_analysis": {
                    "primary_colors": ["#FF0000", "#00FF00"],
                    "logo_analysis": "Modern and clean design"
                }
            }

            # Test PDF generation capability
            pdf_available = capabilities.get('pdf_generation', False)
            pptx_available = capabilities.get('powerpoint_generation', False)
            html_available = capabilities.get('html_generation', False)

            execution_time = time.time() - start_time

            if pdf_available or pptx_available or html_available:
                self.add_result(
                    "presentation_generation",
                    ValidationStatus.PASS,
                    f"Presentation service operational. PDF: {pdf_available}, PPTX: {pptx_available}, HTML: {html_available}",
                    {
                        "capabilities": capabilities,
                        "pdf_available": pdf_available,
                        "pptx_available": pptx_available,
                        "html_available": html_available
                    },
                    execution_time
                )
            else:
                self.add_result(
                    "presentation_generation",
                    ValidationStatus.WARNING,
                    "Presentation service loaded but no generation capabilities available",
                    {"capabilities": capabilities},
                    execution_time
                )

        except Exception as e:
            execution_time = time.time() - start_time
            self.add_result(
                "presentation_generation",
                ValidationStatus.FAIL,
                f"Presentation generation test failed: {str(e)}",
                {"error": str(e)},
                execution_time
            )

    def validate_async_capabilities(self) -> None:
        """Test async analysis capabilities"""
        print("\n⚡ TESTING ASYNC ANALYSIS CAPABILITIES")
        print("=" * 60)

        start_time = time.time()
        try:
            from src.services.async_analysis_service import AsyncAnalysisService

            # Initialize async service
            async_service = AsyncAnalysisService()

            # Test service capabilities
            capabilities = async_service.get_capabilities()

            execution_time = time.time() - start_time
            self.add_result(
                "async_capabilities",
                ValidationStatus.PASS,
                "Async analysis service operational",
                {"capabilities": capabilities},
                execution_time
            )

        except Exception as e:
            execution_time = time.time() - start_time
            self.add_result(
                "async_capabilities",
                ValidationStatus.FAIL,
                f"Async analysis test failed: {str(e)}",
                {"error": str(e)},
                execution_time
            )

    def validate_environment_configuration(self) -> None:
        """Test environment configuration and API keys"""
        print("\n🔧 TESTING ENVIRONMENT CONFIGURATION")
        print("=" * 60)

        start_time = time.time()

        # Check required environment variables
        required_vars = [
            'OPENROUTER_API_KEY',
            'NEWS_API_KEY',
            'BRANDFETCH_API_KEY'
        ]

        optional_vars = [
            'OPENCORPORATES_API_KEY',
            'DATABASE_URL',
            'SECRET_KEY',
            'FLASK_ENV'
        ]

        env_status = {}
        missing_required = []

        for var in required_vars:
            value = os.environ.get(var)
            env_status[var] = {
                'present': bool(value),
                'length': len(value) if value else 0,
                'required': True
            }
            if not value:
                missing_required.append(var)

        for var in optional_vars:
            value = os.environ.get(var)
            env_status[var] = {
                'present': bool(value),
                'length': len(value) if value else 0,
                'required': False
            }

        execution_time = time.time() - start_time

        if len(missing_required) == 0:
            self.add_result(
                "environment_config",
                ValidationStatus.PASS,
                "All required environment variables are configured",
                {"env_status": env_status},
                execution_time
            )
        else:
            self.add_result(
                "environment_config",
                ValidationStatus.WARNING,
                f"Missing required environment variables: {', '.join(missing_required)}",
                {
                    "env_status": env_status,
                    "missing_required": missing_required
                },
                execution_time
            )

    def run_all_validations(self) -> None:
        """Run all validation tests"""
        print("🚀 COMPREHENSIVE SERVICE VALIDATION STARTING")
        print("=" * 60)
        print(f"Timestamp: {self.start_time}")
        print(f"Python Version: {sys.version}")
        print(f"Working Directory: {os.getcwd()}")

        # Run all validation tests
        self.validate_service_imports()
        self.validate_database_connectivity()
        self.validate_api_services()
        self.validate_playwright_capabilities()
        self.validate_presentation_generation()
        self.validate_async_capabilities()
        self.validate_environment_configuration()

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()

        # Categorize results
        passed = [r for r in self.results if r.status == ValidationStatus.PASS]
        failed = [r for r in self.results if r.status == ValidationStatus.FAIL]
        warnings = [r for r in self.results if r.status == ValidationStatus.WARNING]
        skipped = [r for r in self.results if r.status == ValidationStatus.SKIP]

        # Calculate overall status
        if len(failed) == 0 and len(warnings) == 0:
            overall_status = "HEALTHY"
        elif len(failed) == 0:
            overall_status = "DEGRADED"
        else:
            overall_status = "UNHEALTHY"

        report = {
            "validation_summary": {
                "overall_status": overall_status,
                "total_tests": len(self.results),
                "passed": len(passed),
                "failed": len(failed),
                "warnings": len(warnings),
                "skipped": len(skipped),
                "total_duration_seconds": total_duration,
                "timestamp": end_time.isoformat()
            },
            "detailed_results": [
                {
                    "service": result.service_name,
                    "status": result.status.value,
                    "message": result.message,
                    "execution_time": result.execution_time,
                    "details": result.details
                }
                for result in self.results
            ],
            "recommendations": self._generate_recommendations(failed, warnings)
        }

        return report

    def _generate_recommendations(self, failed: List[ValidationResult], warnings: List[ValidationResult]) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []

        if failed:
            recommendations.append("🔴 CRITICAL: Address failed services immediately before deployment")
            for failure in failed:
                if "Import failed" in failure.message:
                    recommendations.append(f"   - Install missing dependencies for {failure.service_name}")
                elif "Database" in failure.service_name:
                    recommendations.append(f"   - Check database configuration and connectivity")
                elif "API" in failure.service_name:
                    recommendations.append(f"   - Verify API keys and network connectivity")
                elif "Playwright" in failure.service_name:
                    recommendations.append(f"   - Run 'playwright install' to install browser dependencies")

        if warnings:
            recommendations.append("🟡 WARNINGS: Review and consider addressing these issues")
            for warning in warnings:
                if "environment" in warning.service_name:
                    recommendations.append(f"   - Configure missing environment variables")
                elif "API" in warning.service_name:
                    recommendations.append(f"   - Some APIs are degraded - monitor performance")

        if not failed and not warnings:
            recommendations.append("✅ All services are operational and ready for production")

        return recommendations

    def print_report(self) -> None:
        """Print formatted validation report"""
        report = self.generate_report()

        print("\n" + "=" * 80)
        print("📋 COMPREHENSIVE SERVICE VALIDATION REPORT")
        print("=" * 80)

        # Summary
        summary = report["validation_summary"]
        print(f"\n🎯 OVERALL STATUS: {summary['overall_status']}")
        print(f"📊 RESULTS: {summary['passed']} passed, {summary['failed']} failed, {summary['warnings']} warnings")
        print(f"⏱️ DURATION: {summary['total_duration_seconds']:.2f} seconds")
        print(f"🕐 COMPLETED: {summary['timestamp']}")

        # Detailed results
        print(f"\n📝 DETAILED RESULTS:")
        print("-" * 80)

        for result in report["detailed_results"]:
            status_icon = result["status"]
            exec_time = f" ({result['execution_time']:.3f}s)" if result['execution_time'] else ""
            print(f"{status_icon} {result['service']:<25} {result['message']}{exec_time}")

            if result.get('details') and isinstance(result['details'], dict):
                for key, value in result['details'].items():
                    if key not in ['error'] and not isinstance(value, dict):
                        print(f"    {key}: {value}")

        # Recommendations
        if report["recommendations"]:
            print(f"\n💡 RECOMMENDATIONS:")
            print("-" * 80)
            for rec in report["recommendations"]:
                print(rec)

        print("\n" + "=" * 80)
        print("✅ Validation completed successfully!")
        print("💾 Full report available in JSON format via generate_report() method")
        print("=" * 80)


def main():
    """Main execution function"""
    try:
        # Initialize validator
        validator = ServiceValidator()

        # Run all validations
        validator.run_all_validations()

        # Print report
        validator.print_report()

        # Save JSON report
        report = validator.generate_report()
        report_filename = f"service_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"\n📄 Detailed JSON report saved to: {report_filename}")

        # Return exit code based on results
        if report["validation_summary"]["overall_status"] == "UNHEALTHY":
            sys.exit(1)
        elif report["validation_summary"]["overall_status"] == "DEGRADED":
            sys.exit(2)
        else:
            sys.exit(0)

    except KeyboardInterrupt:
        print("\n⚠️ Validation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Validation failed with error: {e}")
        logger.exception("Validation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
