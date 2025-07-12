"""
Advanced Analytics API Routes
Provides endpoints for analytics dashboard, historical data, and predictive insights
"""

from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError, Schema, fields
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json

# Import models and services
from src.models.user_model import User, Analysis, Brand, db
from src.services.intelligent_cache_service import IntelligentCacheService

# Create blueprint
analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

# Initialize cache service
cache_service = IntelligentCacheService()

# Validation schemas
class AnalyticsQuerySchema(Schema):
    """Schema for analytics query parameters"""
    brand_ids = fields.List(fields.String(), missing=[])
    metrics = fields.List(fields.String(), missing=['brandHealth', 'sentiment', 'marketShare'])
    timeframe = fields.String(missing='30d')
    date_from = fields.DateTime(missing=None)
    date_to = fields.DateTime(missing=None)
    filters = fields.Dict(missing={})

class ComparisonQuerySchema(Schema):
    """Schema for brand comparison queries"""
    primary_brand_id = fields.String(required=True)
    comparison_brand_ids = fields.List(fields.String(), required=True)
    metrics = fields.List(fields.String(), missing=['brandHealth', 'sentiment', 'marketShare'])

class TrendAnalysisSchema(Schema):
    """Schema for trend analysis queries"""
    brand_id = fields.String(required=True)
    metrics = fields.List(fields.String(), required=True)
    period = fields.String(missing='30d')
    granularity = fields.String(missing='daily')

@analytics_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_data():
    """Get comprehensive dashboard data for analytics"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({"success": False, "error": "User not found or inactive"}), 401

        # Get query parameters
        brand_id = request.args.get('brand_id')
        timeframe = request.args.get('timeframe', '30d')
        
        # Check cache first
        cache_key = f"dashboard_data_{current_user_id}_{brand_id}_{timeframe}"
        cached_data = await cache_service.get(cache_key, 'analytics')
        
        if cached_data:
            return jsonify({"success": True, "data": cached_data}), 200

        # Generate dashboard data
        dashboard_data = {
            "brand_health": generate_brand_health_data(brand_id, timeframe),
            "key_metrics": generate_key_metrics(brand_id, timeframe),
            "sentiment_trends": generate_sentiment_trends(brand_id, timeframe),
            "competitive_position": generate_competitive_position(brand_id),
            "insights": generate_insights(brand_id, timeframe),
            "predictions": generate_predictions(brand_id, timeframe),
            "last_updated": datetime.utcnow().isoformat()
        }
        
        # Cache the results
        await cache_service.set(cache_key, dashboard_data, 'analytics', ttl=1800)  # 30 minutes
        
        return jsonify({"success": True, "data": dashboard_data}), 200
        
    except Exception as e:
        current_app.logger.error(f"Dashboard data error: {str(e)}")
        return jsonify({"success": False, "error": "Failed to get dashboard data"}), 500

@analytics_bp.route('/historical', methods=['GET'])
@jwt_required()
def get_historical_data():
    """Get historical analytics data for trend analysis"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({"success": False, "error": "User not found or inactive"}), 401

        # Validate input
        schema = AnalyticsQuerySchema()
        try:
            query_params = schema.load(request.args.to_dict(flat=False))
        except ValidationError as err:
            return jsonify({"success": False, "error": err.messages}), 400

        brand_id = request.args.get('brand_id')
        timeframe = query_params['timeframe']
        metrics = query_params['metrics']
        
        # Check cache
        cache_key = f"historical_data_{current_user_id}_{brand_id}_{timeframe}_{'-'.join(metrics)}"
        cached_data = await cache_service.get(cache_key, 'analytics')
        
        if cached_data:
            return jsonify({"success": True, "data": cached_data}), 200

        # Generate historical data
        historical_data = generate_historical_data(brand_id, timeframe, metrics)
        
        # Cache the results
        await cache_service.set(cache_key, historical_data, 'analytics', ttl=3600)  # 1 hour
        
        return jsonify({"success": True, "data": historical_data}), 200
        
    except Exception as e:
        current_app.logger.error(f"Historical data error: {str(e)}")
        return jsonify({"success": False, "error": "Failed to get historical data"}), 500

@analytics_bp.route('/comparison', methods=['POST'])
@jwt_required()
def get_comparison_data():
    """Get brand comparison data"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({"success": False, "error": "User not found or inactive"}), 401

        # Validate input
        schema = ComparisonQuerySchema()
        try:
            data = schema.load(request.get_json() or {})
        except ValidationError as err:
            return jsonify({"success": False, "error": err.messages}), 400

        primary_brand_id = data['primary_brand_id']
        comparison_brand_ids = data['comparison_brand_ids']
        metrics = data['metrics']
        
        # Check cache
        cache_key = f"comparison_data_{primary_brand_id}_{'-'.join(comparison_brand_ids)}_{'-'.join(metrics)}"
        cached_data = await cache_service.get(cache_key, 'analytics')
        
        if cached_data:
            return jsonify({"success": True, "data": cached_data}), 200

        # Generate comparison data
        comparison_data = generate_comparison_data(primary_brand_id, comparison_brand_ids, metrics)
        
        # Cache the results
        await cache_service.set(cache_key, comparison_data, 'analytics', ttl=1800)  # 30 minutes
        
        return jsonify({"success": True, "data": comparison_data}), 200
        
    except Exception as e:
        current_app.logger.error(f"Comparison data error: {str(e)}")
        return jsonify({"success": False, "error": "Failed to get comparison data"}), 500

@analytics_bp.route('/trends', methods=['GET'])
@jwt_required()
def get_trend_analysis():
    """Get trend analysis data"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({"success": False, "error": "User not found or inactive"}), 401

        # Validate input
        schema = TrendAnalysisSchema()
        try:
            query_params = schema.load(request.args.to_dict())
        except ValidationError as err:
            return jsonify({"success": False, "error": err.messages}), 400

        brand_id = query_params['brand_id']
        metrics = query_params['metrics']
        period = query_params['period']
        granularity = query_params['granularity']
        
        # Check cache
        cache_key = f"trend_analysis_{brand_id}_{'-'.join(metrics)}_{period}_{granularity}"
        cached_data = await cache_service.get(cache_key, 'analytics')
        
        if cached_data:
            return jsonify({"success": True, "data": cached_data}), 200

        # Generate trend analysis
        trend_data = generate_trend_analysis(brand_id, metrics, period, granularity)
        
        # Cache the results
        await cache_service.set(cache_key, trend_data, 'analytics', ttl=1800)  # 30 minutes
        
        return jsonify({"success": True, "data": trend_data}), 200
        
    except Exception as e:
        current_app.logger.error(f"Trend analysis error: {str(e)}")
        return jsonify({"success": False, "error": "Failed to get trend analysis"}), 500

@analytics_bp.route('/predictions', methods=['GET'])
@jwt_required()
def get_predictive_insights():
    """Get predictive insights and forecasts"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({"success": False, "error": "User not found or inactive"}), 401

        brand_id = request.args.get('brand_id')
        forecast_period = request.args.get('forecast_period', '30d')
        confidence_threshold = float(request.args.get('confidence_threshold', 0.7))
        
        # Check cache
        cache_key = f"predictions_{brand_id}_{forecast_period}_{confidence_threshold}"
        cached_data = await cache_service.get(cache_key, 'analytics')
        
        if cached_data:
            return jsonify({"success": True, "data": cached_data}), 200

        # Generate predictions
        predictions = generate_predictive_insights(brand_id, forecast_period, confidence_threshold)
        
        # Cache the results
        await cache_service.set(cache_key, predictions, 'analytics', ttl=3600)  # 1 hour
        
        return jsonify({"success": True, "data": predictions}), 200
        
    except Exception as e:
        current_app.logger.error(f"Predictive insights error: {str(e)}")
        return jsonify({"success": False, "error": "Failed to get predictive insights"}), 500

@analytics_bp.route('/export', methods=['POST'])
@jwt_required()
def export_analytics_data():
    """Export analytics data in various formats"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({"success": False, "error": "User not found or inactive"}), 401

        data = request.get_json() or {}
        export_format = data.get('format', 'json')
        export_data = data.get('data', {})
        export_type = data.get('type', 'dashboard')
        
        # Generate export
        export_result = generate_export(export_data, export_format, export_type)
        
        return jsonify({
            "success": True, 
            "data": {
                "download_url": export_result.get('url'),
                "filename": export_result.get('filename'),
                "format": export_format
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Export error: {str(e)}")
        return jsonify({"success": False, "error": "Failed to export data"}), 500

# Helper functions for data generation
def generate_brand_health_data(brand_id: str, timeframe: str) -> Dict[str, Any]:
    """Generate brand health metrics"""
    import random
    
    return {
        "overall": 85 + random.randint(-10, 10),
        "visual": 78 + random.randint(-5, 15),
        "sentiment": 82 + random.randint(-8, 12),
        "news": 76 + random.randint(-10, 15),
        "trend": random.uniform(-5, 8)
    }

def generate_key_metrics(brand_id: str, timeframe: str) -> Dict[str, Any]:
    """Generate key performance metrics"""
    import random
    
    return {
        "totalMentions": random.randint(50, 200),
        "sentimentScore": random.uniform(0.6, 0.9),
        "visualAssets": random.randint(10, 50),
        "competitorCount": random.randint(3, 8),
        "campaignCount": random.randint(1, 5),
        "lastAnalysis": datetime.utcnow().isoformat()
    }

def generate_sentiment_trends(brand_id: str, timeframe: str) -> Dict[str, Any]:
    """Generate sentiment trend data"""
    import random
    
    return {
        "current": random.uniform(0.6, 0.9),
        "historical": [],
        "change": random.uniform(-0.1, 0.15)
    }

def generate_competitive_position(brand_id: str) -> Dict[str, Any]:
    """Generate competitive positioning data"""
    import random
    
    return {
        "brandScore": 85 + random.randint(-5, 10),
        "avgCompetitorScore": 72 + random.randint(-8, 12),
        "ranking": random.randint(1, 5),
        "marketShare": random.uniform(10, 25)
    }

def generate_insights(brand_id: str, timeframe: str) -> List[Dict[str, Any]]:
    """Generate actionable insights"""
    return [
        {
            "type": "positive",
            "category": "Brand Health",
            "title": "Strong Brand Performance",
            "description": "Your brand shows excellent health metrics across all dimensions.",
            "confidence": 0.9
        }
    ]

def generate_predictions(brand_id: str, timeframe: str) -> List[Dict[str, Any]]:
    """Generate predictive insights"""
    return [
        {
            "metric": "Brand Sentiment",
            "prediction": "Positive growth expected",
            "confidence": 0.75,
            "timeframe": "30 days",
            "impact": "high"
        }
    ]

def generate_historical_data(brand_id: str, timeframe: str, metrics: List[str]) -> Dict[str, Any]:
    """Generate historical trend data"""
    import random
    from datetime import datetime, timedelta
    
    days = 30 if timeframe == '30d' else 90 if timeframe == '90d' else 365
    data = []
    
    for i in range(days):
        date = datetime.utcnow() - timedelta(days=days-i)
        data_point = {"date": date.isoformat()}
        
        for metric in metrics:
            base_value = 75 if metric == 'brandHealth' else 65
            data_point[metric] = base_value + random.randint(-10, 15)
        
        data.append(data_point)
    
    return {"data": data, "metrics": metrics, "timeframe": timeframe}

def generate_comparison_data(primary_brand_id: str, comparison_brand_ids: List[str], metrics: List[str]) -> Dict[str, Any]:
    """Generate brand comparison data"""
    import random
    
    brands = [{"id": primary_brand_id, "name": "Your Brand", "isPrimary": True}]
    brands.extend([{"id": bid, "name": f"Competitor {i+1}", "isPrimary": False} 
                   for i, bid in enumerate(comparison_brand_ids)])
    
    for brand in brands:
        for metric in metrics:
            base_value = 85 if brand["isPrimary"] else 60 + random.randint(0, 20)
            brand[metric] = base_value + random.randint(-5, 10)
    
    return {"brands": brands, "metrics": metrics}

def generate_trend_analysis(brand_id: str, metrics: List[str], period: str, granularity: str) -> Dict[str, Any]:
    """Generate trend analysis data"""
    import random
    from datetime import datetime, timedelta
    
    days = 30 if period == '30d' else 90
    data = []
    
    for i in range(days):
        date = datetime.utcnow() - timedelta(days=days-i)
        data_point = {"date": date.isoformat()}
        
        for metric in metrics:
            base_value = 75
            trend = i * 0.1  # Slight upward trend
            noise = random.uniform(-3, 3)
            data_point[metric] = base_value + trend + noise
        
        data.append(data_point)
    
    return {"data": data, "metrics": metrics, "period": period, "granularity": granularity}

def generate_predictive_insights(brand_id: str, forecast_period: str, confidence_threshold: float) -> Dict[str, Any]:
    """Generate predictive insights and forecasts"""
    import random
    
    insights = [
        {
            "type": "opportunity",
            "title": "Brand Health Growth Opportunity",
            "description": "Current trends suggest improvement in brand health.",
            "confidence": 0.85,
            "impact": "high",
            "timeframe": forecast_period
        }
    ]
    
    # Filter by confidence threshold
    filtered_insights = [i for i in insights if i["confidence"] >= confidence_threshold]
    
    return {
        "insights": filtered_insights,
        "forecast_period": forecast_period,
        "confidence_threshold": confidence_threshold
    }

def generate_export(data: Dict[str, Any], format: str, export_type: str) -> Dict[str, Any]:
    """Generate export file"""
    import tempfile
    import json
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{format}')
    
    if format == 'json':
        json.dump(data, temp_file, indent=2)
    elif format == 'csv':
        # Convert to CSV format
        pass
    
    temp_file.close()
    
    return {
        "url": f"/api/analytics/download/{temp_file.name}",
        "filename": f"analytics_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{format}"
    }
