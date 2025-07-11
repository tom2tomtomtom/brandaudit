"""
Secure Brand Audit Routes with Authentication and Validation
"""

from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
import os
import uuid
import threading
from datetime import datetime, timedelta

# Import models and schemas
from src.models.user_model import User, Analysis, UploadedFile, db
from src.schemas.validation import (
    BrandSearchSchema,
    BrandAssetsSchema,
    AnalysisRequestSchema,
    FileUploadSchema,
    ReportGenerationSchema,
    validate_file_upload,
    sanitize_filename,
    validate_analysis_id,
)

# Import services
from src.services.llm_service import LLMService
from src.services.news_service import NewsService
from src.services.brand_data_service import BrandDataService
from src.services.visual_analysis_service import VisualAnalysisService
from src.services.async_analysis_service import AsyncAnalysisService
from src.services.intelligent_cache_service import intelligent_cache
from src.services.database_optimization_service import db_optimizer

brand_audit_bp = Blueprint("brand_audit", __name__)

# Initialize services
llm_service = LLMService()
news_service = NewsService()
brand_data_service = BrandDataService()
visual_analysis_service = VisualAnalysisService()
async_analysis_service = AsyncAnalysisService()

# Configuration
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "svg", "webp", "pdf"}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@brand_audit_bp.route("/brand/search", methods=["POST"])
@jwt_required()
def search_brand():
    """Search for brand information with authentication and validation"""
    try:
        # Get current user
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or not user.is_active:
            return jsonify(
                {"success": False, "error": "User not found or inactive"}
            ), 401

        # Validate input
        schema = BrandSearchSchema()
        data = schema.load(request.get_json() or {})

        # Log the search request
        current_app.logger.info(
            f"Brand search request from user {user.email}: {data['query']}"
        )

        # Perform brand search
        result = brand_data_service.search_company(data["query"])

        return jsonify({"success": True, "data": result}), 200

    except ValidationError as e:
        return jsonify(
            {"success": False, "error": "Validation error", "details": e.messages}
        ), 400
    except Exception as e:
        current_app.logger.error(f"Brand search error: {str(e)}")
        return jsonify({"success": False, "error": "Brand search failed"}), 500


@brand_audit_bp.route("/brand/assets", methods=["POST"])
@jwt_required()
def get_brand_assets():
    """Get brand assets with authentication and validation"""
    try:
        # Get current user
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or not user.is_active:
            return jsonify(
                {"success": False, "error": "User not found or inactive"}
            ), 401

        # Validate input
        schema = BrandAssetsSchema()
        data = schema.load(request.get_json() or {})

        # Log the assets request
        current_app.logger.info(
            f"Brand assets request from user {user.email}: {data['website']}"
        )

        # Get brand assets
        result = brand_data_service.get_brand_assets(data["website"])

        return jsonify({"success": True, "data": result}), 200

    except ValidationError as e:
        return jsonify(
            {"success": False, "error": "Validation error", "details": e.messages}
        ), 400
    except Exception as e:
        current_app.logger.error(f"Brand assets error: {str(e)}")
        return jsonify({"success": False, "error": "Failed to get brand assets"}), 500


@brand_audit_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_files():
    """Secure file upload with authentication and validation"""
    try:
        # Get current user
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or not user.is_active:
            return jsonify(
                {"success": False, "error": "User not found or inactive"}
            ), 401

        # Check if files are present
        if "files" not in request.files:
            return jsonify({"success": False, "error": "No files provided"}), 400

        files = request.files.getlist("files")
        if not files or all(f.filename == "" for f in files):
            return jsonify({"success": False, "error": "No files selected"}), 400

        # Validate file type from form data
        file_type = request.form.get("file_type", "other")
        description = request.form.get("description", "")

        # Validate form data
        form_schema = FileUploadSchema()
        form_data = form_schema.load(
            {"file_type": file_type, "description": description}
        )

        uploaded_files = []

        for file in files:
            # Validate file
            validate_file_upload(file)

            # Generate secure filename
            file_id = str(uuid.uuid4())
            original_filename = file.filename
            safe_filename = sanitize_filename(original_filename)
            filename = f"{file_id}_{safe_filename}"

            # Create user-specific upload directory
            user_upload_dir = os.path.join(UPLOAD_FOLDER, current_user_id)
            os.makedirs(user_upload_dir, exist_ok=True)

            # Save file
            file_path = os.path.join(user_upload_dir, filename)
            file.save(file_path)

            # Get file info
            file_size = os.path.getsize(file_path)
            mime_type = file.content_type or "application/octet-stream"

            # Save file record to database
            uploaded_file = UploadedFile(
                id=file_id,
                user_id=current_user_id,
                filename=filename,
                original_filename=original_filename,
                file_path=file_path,
                file_size=file_size,
                mime_type=mime_type,
                file_type=form_data["file_type"],
            )

            db.session.add(uploaded_file)
            uploaded_files.append(uploaded_file.to_dict())

        db.session.commit()

        current_app.logger.info(
            f"Files uploaded by user {user.email}: {len(uploaded_files)} files"
        )

        return jsonify(
            {
                "success": True,
                "message": f"Successfully uploaded {len(uploaded_files)} files",
                "data": {"files": uploaded_files},
            }
        ), 200

    except ValidationError as e:
        return jsonify(
            {"success": False, "error": "Validation error", "details": e.messages}
        ), 400
    except Exception as e:
        current_app.logger.error(f"File upload error: {str(e)}")
        return jsonify({"success": False, "error": "File upload failed"}), 500


@brand_audit_bp.route("/analyze", methods=["POST"])
@jwt_required()
def analyze_brand():
    """Start brand analysis with authentication and validation"""
    try:
        # Get current user
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or not user.is_active:
            return jsonify(
                {"success": False, "error": "User not found or inactive"}
            ), 401

        # Validate input
        schema = AnalysisRequestSchema()
        data = schema.load(request.get_json() or {})

        # Create analysis record
        analysis_id = str(uuid.uuid4())
        analysis = Analysis(
            id=analysis_id,
            user_id=current_user_id,
            company_name=data["company_name"],
            website=data.get("website"),
            status="pending",
            progress=0,
            analysis_options=data["analysis_options"],
        )

        db.session.add(analysis)
        db.session.commit()

        # Start background analysis with performance optimization
        use_async_processing = data.get("use_async_processing", True)

        if use_async_processing:
            # Use async processing for better performance
            thread = threading.Thread(
                target=run_async_analysis, args=(analysis_id, data, current_user_id)
            )
        else:
            # Fallback to original sequential processing
            thread = threading.Thread(
                target=run_analysis, args=(analysis_id, data, current_user_id)
            )

        thread.daemon = True
        thread.start()

        current_app.logger.info(f"Analysis started by user {user.email}: {analysis_id}")

        return jsonify(
            {
                "success": True,
                "analysis_id": analysis_id,
                "estimated_completion": (
                    datetime.utcnow() + timedelta(minutes=5)
                ).isoformat(),
            }
        ), 200

    except ValidationError as e:
        return jsonify(
            {"success": False, "error": "Validation error", "details": e.messages}
        ), 400
    except Exception as e:
        current_app.logger.error(f"Analysis start error: {str(e)}")
        return jsonify({"success": False, "error": "Failed to start analysis"}), 500


@brand_audit_bp.route("/analyze/<analysis_id>/status", methods=["GET"])
@jwt_required()
def get_analysis_status(analysis_id):
    """Get analysis status with authentication and validation"""
    try:
        # Validate analysis ID format
        validate_analysis_id(analysis_id)

        # Get current user
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or not user.is_active:
            return jsonify(
                {"success": False, "error": "User not found or inactive"}
            ), 401

        # Get analysis (ensure user owns it)
        analysis = Analysis.query.filter_by(
            id=analysis_id, user_id=current_user_id
        ).first()

        if not analysis:
            return jsonify({"success": False, "error": "Analysis not found"}), 404

        # Determine current step based on progress
        steps = [
            "Initializing analysis...",
            "Collecting brand information...",
            "Analyzing brand sentiment...",
            "Gathering news coverage...",
            "Capturing visual assets...",
            "Analyzing competitive landscape...",
            "Generating insights...",
            "Analysis complete!",
        ]

        step_index = min(int(analysis.progress / 100 * len(steps)), len(steps) - 1)
        current_step = steps[step_index]

        return jsonify(
            {
                "success": True,
                "data": {
                    "analysis_id": analysis.id,
                    "status": analysis.status,
                    "progress": analysis.progress,
                    "current_step": current_step,
                },
            }
        ), 200

    except ValidationError:
        return jsonify({"success": False, "error": "Invalid analysis ID"}), 400
    except Exception as e:
        current_app.logger.error(f"Analysis status error: {str(e)}")
        return jsonify(
            {"success": False, "error": "Failed to get analysis status"}
        ), 500


@brand_audit_bp.route("/analyze/<analysis_id>/results", methods=["GET"])
@jwt_required()
def get_analysis_results(analysis_id):
    """Get analysis results with authentication and validation"""
    try:
        # Validate analysis ID format
        validate_analysis_id(analysis_id)

        # Get current user
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or not user.is_active:
            return jsonify(
                {"success": False, "error": "User not found or inactive"}
            ), 401

        # Get analysis (ensure user owns it)
        analysis = Analysis.query.filter_by(
            id=analysis_id, user_id=current_user_id
        ).first()

        if not analysis:
            return jsonify({"success": False, "error": "Analysis not found"}), 404

        if analysis.status != "completed":
            return jsonify(
                {"success": False, "error": "Analysis not completed yet"}
            ), 400

        return jsonify({"success": True, "data": analysis.results}), 200

    except ValidationError:
        return jsonify({"success": False, "error": "Invalid analysis ID"}), 400
    except Exception as e:
        current_app.logger.error(f"Analysis results error: {str(e)}")
        return jsonify(
            {"success": False, "error": "Failed to get analysis results"}
        ), 500


@brand_audit_bp.route("/report/generate", methods=["POST"])
@jwt_required()
def generate_report():
    """Generate analysis report with authentication and validation"""
    try:
        # Get current user
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or not user.is_active:
            return jsonify(
                {"success": False, "error": "User not found or inactive"}
            ), 401

        # Validate input
        schema = ReportGenerationSchema()
        data = schema.load(request.get_json() or {})

        # Get analysis (ensure user owns it)
        analysis = Analysis.query.filter_by(
            id=data["analysis_id"], user_id=current_user_id
        ).first()

        if not analysis:
            return jsonify({"success": False, "error": "Analysis not found"}), 404

        if analysis.status != "completed":
            return jsonify(
                {"success": False, "error": "Analysis not completed yet"}
            ), 400

        # Generate professional markdown report
        try:
            from src.services.report_generation_service import ReportGenerationService
            report_service = ReportGenerationService()

            # Generate comprehensive markdown report
            report_result = report_service.generate_comprehensive_report(
                analysis.company_name,
                analysis.results or {}
            )

            if report_result.get('success'):
                report_data = {
                    "analysis_id": analysis.id,
                    "company_name": analysis.company_name,
                    "generated_at": datetime.utcnow().isoformat(),
                    "format": data["format"],
                    "sections": data["include_sections"],
                    "results": analysis.results,
                    "markdown_report": {
                        "filename": report_result.get('filename'),
                        "filepath": report_result.get('root_filepath'),
                        "file_size": report_result.get('file_size'),
                        "sections_generated": report_result.get('sections_generated')
                    }
                }

                current_app.logger.info(f"Professional report generated by user {user.email}: {analysis.id}")
                current_app.logger.info(f"Report file: {report_result.get('filename')}")

                return jsonify(
                    {
                        "success": True,
                        "message": "Professional report generated successfully",
                        "data": report_data,
                    }
                ), 200
            else:
                # Fallback to basic report if markdown generation fails
                report_data = {
                    "analysis_id": analysis.id,
                    "company_name": analysis.company_name,
                    "generated_at": datetime.utcnow().isoformat(),
                    "format": data["format"],
                    "sections": data["include_sections"],
                    "results": analysis.results,
                    "markdown_report": {"error": report_result.get('error')}
                }

                current_app.logger.warning(f"Markdown report generation failed for {user.email}: {report_result.get('error')}")

                return jsonify(
                    {
                        "success": True,
                        "message": "Basic report generated (markdown generation failed)",
                        "data": report_data,
                    }
                ), 200

        except Exception as e:
            current_app.logger.error(f"Report generation error for {user.email}: {str(e)}")

            # Fallback to basic report
            report_data = {
                "analysis_id": analysis.id,
                "company_name": analysis.company_name,
                "generated_at": datetime.utcnow().isoformat(),
                "format": data["format"],
                "sections": data["include_sections"],
                "results": analysis.results,
                "markdown_report": {"error": f"Report generation failed: {str(e)}"}
            }

            return jsonify(
                {
                    "success": True,
                    "message": "Basic report generated (service error)",
                    "data": report_data,
                }
            ), 200

    except ValidationError as e:
        return jsonify(
            {"success": False, "error": "Validation error", "details": e.messages}
        ), 400
    except Exception as e:
        current_app.logger.error(f"Report generation error: {str(e)}")
        return jsonify({"success": False, "error": "Failed to generate report"}), 500


@brand_audit_bp.route("/analyses", methods=["GET"])
@jwt_required()
def get_user_analyses():
    """Get user's analysis history"""
    try:
        # Get current user
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or not user.is_active:
            return jsonify(
                {"success": False, "error": "User not found or inactive"}
            ), 401

        # Get pagination parameters
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 10, type=int), 100)

        # Get user's analyses
        analyses = (
            Analysis.query.filter_by(user_id=current_user_id)
            .order_by(Analysis.created_at.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

        return jsonify(
            {
                "success": True,
                "data": {
                    "analyses": [analysis.to_dict() for analysis in analyses.items],
                    "pagination": {
                        "page": page,
                        "per_page": per_page,
                        "total": analyses.total,
                        "pages": analyses.pages,
                    },
                },
            }
        ), 200

    except Exception as e:
        current_app.logger.error(f"Get analyses error: {str(e)}")
        return jsonify({"success": False, "error": "Failed to get analyses"}), 500


def run_async_analysis(analysis_id, analysis_data, user_id):
    """Optimized background analysis function with concurrent processing"""
    import asyncio

    try:
        with current_app.app_context():
            # Get analysis record
            analysis = Analysis.query.get(analysis_id)
            if not analysis:
                return

            # Update status to processing
            analysis.status = "processing"
            analysis.progress = 5
            db.session.commit()

            # Create progress callback
            async def progress_callback(progress, message):
                try:
                    analysis.progress = progress
                    analysis.status_message = message
                    db.session.commit()
                    current_app.logger.info(f"Analysis {analysis_id} progress: {progress}% - {message}")
                except Exception as e:
                    current_app.logger.error(f"Progress update failed: {str(e)}")

            # Add analysis_id to data
            analysis_data["analysis_id"] = analysis_id

            # Run async analysis
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                results = loop.run_until_complete(
                    async_analysis_service.run_concurrent_analysis(
                        analysis_data,
                        progress_callback
                    )
                )

                # Store results
                analysis.results = results
                analysis.status = "completed"
                analysis.progress = 100
                analysis.completed_at = datetime.utcnow()
                db.session.commit()

                current_app.logger.info(f"Async analysis completed for {analysis_data['company_name']} in {results.get('performance_metrics', {}).get('total_duration_seconds', 'unknown')}s")

            finally:
                loop.close()

    except Exception as e:
        current_app.logger.error(f"Async analysis failed: {str(e)}")
        try:
            with current_app.app_context():
                analysis = Analysis.query.get(analysis_id)
                if analysis:
                    analysis.status = "failed"
                    analysis.error_message = str(e)
                    db.session.commit()
        except:
            pass


def run_analysis(analysis_id, analysis_data, user_id):
    """Background analysis function with comprehensive error handling"""
    try:
        with current_app.app_context():
            # Get analysis record
            analysis = Analysis.query.get(analysis_id)
            if not analysis:
                return

            # Update status to processing
            analysis.status = "processing"
            analysis.progress = 10
            db.session.commit()

            # Initialize results
            results = {
                "analysis_id": analysis_id,
                "company_name": analysis_data["company_name"],
                "website": analysis_data.get("website"),
                "started_at": datetime.utcnow().isoformat(),
                "brand_health_score": 0,
                "key_findings": [],
                "llm_insights": None,
                "news_analysis": None,
                "brand_info": None,
                "visual_analysis": None,
                "competitive_analysis": None,
            }

            # Step 1: Get brand information
            analysis.progress = 20
            db.session.commit()

            if analysis_data.get("website"):
                brand_info = brand_data_service.get_company_info(
                    analysis_data["company_name"]
                )
                results["brand_info"] = brand_info

            # Step 2: LLM Analysis
            if analysis_data["analysis_options"].get("brandPerception"):
                analysis.progress = 40
                db.session.commit()

                llm_insights = llm_service.analyze_brand_sentiment(
                    f"Brand analysis for {analysis_data['company_name']}",
                    analysis_data["company_name"],
                )
                results["llm_insights"] = llm_insights

            # Step 3: News Analysis
            if analysis_data["analysis_options"].get("pressCoverage"):
                analysis.progress = 60
                db.session.commit()

                news_analysis = news_service.get_brand_news(
                    analysis_data["company_name"]
                )
                results["news_analysis"] = news_analysis

            # Step 4: Visual Analysis
            if analysis_data["analysis_options"].get("visualAnalysis", True):  # Default to True
                analysis.progress = 70
                db.session.commit()

                try:
                    # Get brand data for enhanced visual analysis
                    brand_info = results.get("brand_info", {})
                    website_url = analysis_data.get("website", f"https://{analysis_data['company_name'].lower().replace(' ', '')}.com")

                    # Run async visual analysis
                    import asyncio
                    visual_analysis = asyncio.run(
                        visual_analysis_service.analyze_brand_visuals(
                            analysis_data["company_name"],
                            website_url,
                            brand_info
                        )
                    )
                    results["visual_analysis"] = visual_analysis

                    current_app.logger.info(f"Visual analysis completed for {analysis_data['company_name']}")

                except Exception as e:
                    error_msg = f"Visual analysis failed: {str(e)}"
                    current_app.logger.error(error_msg)
                    results["visual_analysis"] = {
                        "error": error_msg,
                        "visual_assets": {},
                        "visual_scores": {}
                    }

            # Step 5: Competitive Analysis
            if analysis_data["analysis_options"].get("competitiveAnalysis"):
                analysis.progress = 80
                db.session.commit()

                competitive_analysis = llm_service.analyze_competitive_landscape(
                    analysis_data["company_name"],
                    [],  # Placeholder for competitor data
                )
                results["competitive_analysis"] = competitive_analysis

            # Step 6: Calculate brand health score
            analysis.progress = 90
            db.session.commit()

            # Simple scoring algorithm (can be enhanced)
            score = 75  # Base score
            if results.get("news_analysis", {}).get("sentiment_score", 0) > 0.5:
                score += 10
            if (
                results.get("llm_insights", {}).get("sentiment", "neutral")
                == "positive"
            ):
                score += 15

            results["brand_health_score"] = min(score, 100)

            # Add key findings
            results["key_findings"] = [
                {
                    "type": "positive",
                    "text": f"{analysis_data['company_name']} shows strong brand recognition in the market.",
                },
                {
                    "type": "neutral",
                    "text": "Visual consistency could be improved across digital platforms.",
                },
                {
                    "type": "positive",
                    "text": "Overall sentiment analysis indicates positive brand perception.",
                },
            ]

            # Complete analysis
            analysis.status = "completed"
            analysis.progress = 100
            analysis.results = results
            analysis.completed_at = datetime.utcnow()
            results["completed_at"] = analysis.completed_at.isoformat()

            db.session.commit()

            current_app.logger.info(f"Analysis completed: {analysis_id}")

    except Exception as e:
        # Handle analysis failure
        try:
            with current_app.app_context():
                analysis = Analysis.query.get(analysis_id)
                if analysis:
                    analysis.status = "failed"
                    analysis.results = {
                        "error": "Analysis failed",
                        "message": str(e),
                        "failed_at": datetime.utcnow().isoformat(),
                    }
                    db.session.commit()
        except Exception as inner_e:
            current_app.logger.error(
                f"Failed to update analysis status after failure: {analysis_id} - {str(inner_e)}"
            )

        current_app.logger.error(f"Analysis failed: {analysis_id} - {str(e)}")


@brand_audit_bp.route("/analyze/<analysis_id>/performance", methods=["GET"])
@jwt_required()
def get_analysis_performance(analysis_id):
    """Get performance metrics for an analysis"""
    try:
        # Get current user
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or not user.is_active:
            return jsonify(
                {"success": False, "error": "User not found or inactive"}
            ), 401

        # Validate analysis ID
        if not validate_analysis_id(analysis_id):
            return jsonify(
                {"success": False, "error": "Invalid analysis ID format"}
            ), 400

        # Get analysis
        analysis = Analysis.query.filter_by(
            id=analysis_id, user_id=current_user_id
        ).first()

        if not analysis:
            return jsonify(
                {"success": False, "error": "Analysis not found"}
            ), 404

        # Get performance metrics
        performance_metrics = {
            "totalDuration": analysis.processing_time_seconds or 0,
            "concurrentTasks": 1 if analysis.concurrent_processing_used else 0,
            "cacheHitRate": analysis.cache_hit_rate or 0,
            "imageOptimization": {
                "processed": 0,  # Would be tracked in results
                "compressionRatio": 0,
                "totalSizeSaved": 0
            },
            "apiPerformance": {
                "totalCalls": 0,  # Would be tracked during analysis
                "averageResponseTime": 0,
                "successRate": 100
            },
            "databasePerformance": db_optimizer.query_stats
        }

        # Get real-time stats if analysis is in progress
        real_time_stats = {
            "currentStep": analysis.status_message or "",
            "progress": analysis.progress,
            "estimatedTimeRemaining": 0
        }

        # Calculate estimated time remaining
        if analysis.status == "processing" and analysis.progress > 0:
            elapsed_time = (datetime.utcnow() - analysis.created_at).total_seconds()
            estimated_total = elapsed_time * (100 / analysis.progress)
            real_time_stats["estimatedTimeRemaining"] = max(0, estimated_total - elapsed_time)

        return jsonify({
            "success": True,
            "metrics": performance_metrics,
            "realTimeStats": real_time_stats
        }), 200

    except Exception as e:
        current_app.logger.error(f"Performance metrics error: {str(e)}")
        return jsonify({"success": False, "error": "Failed to get performance metrics"}), 500
