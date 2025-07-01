#!/usr/bin/env python3
"""
Production startup script for AI Brand Audit Tool
"""
import os
import sys
import logging
from src.main import app

def setup_logging():
    """Setup production logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Main startup function"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Starting AI Brand Audit Tool")
    logger.info(f"📍 Python version: {sys.version}")
    logger.info(f"📍 Flask env: {os.environ.get('FLASK_ENV', 'development')}")
    logger.info(f"📍 Port: {os.environ.get('PORT', '8000')}")
    logger.info(f"📍 Railway env: {os.environ.get('RAILWAY_ENVIRONMENT', 'Not set')}")
    
    # Check API keys
    api_keys = {
        'OPENROUTER_API_KEY': bool(os.environ.get('OPENROUTER_API_KEY')),
        'NEWS_API_KEY': bool(os.environ.get('NEWS_API_KEY')),
        'BRANDFETCH_API_KEY': bool(os.environ.get('BRANDFETCH_API_KEY')),
        'OPENCORPORATES_API_KEY': bool(os.environ.get('OPENCORPORATES_API_KEY'))
    }
    
    for key, exists in api_keys.items():
        logger.info(f"📍 {key}: {'✅ Set' if exists else '❌ Missing (will use mock data)'}")
    
    # Test database connection
    try:
        with app.app_context():
            from src.extensions import db
            db.create_all()
            logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        sys.exit(1)
    
    # Test app routes
    try:
        with app.test_client() as client:
            response = client.get('/api/health')
            if response.status_code == 200:
                logger.info("✅ Health check endpoint working")
            else:
                logger.error(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Route test failed: {e}")
    
    logger.info("✅ Application startup complete")
    
    # Start the server
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    main()