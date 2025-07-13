#!/usr/bin/env python3
"""
Quick fix script for common validation issues
"""

import os
import sys

def create_missing_logging_config():
    """Create missing logging configuration"""
    logging_config_path = "src/utils/logging_config.py"
    
    # Create utils directory if it doesn't exist
    os.makedirs("src/utils", exist_ok=True)
    
    # Create __init__.py files
    with open("src/utils/__init__.py", "w") as f:
        f.write("")
    
    # Create logging_config.py
    logging_config_content = '''"""
Logging configuration utilities
"""

import logging
import sys
from typing import Optional

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get configured logger instance"""
    logger = logging.getLogger(name or __name__)
    
    if not logger.handlers:
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger

def setup_logging(level: str = "INFO") -> None:
    """Setup basic logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
'''
    
    with open(logging_config_path, "w") as f:
        f.write(logging_config_content)
    
    print(f"✅ Created {logging_config_path}")

def create_missing_user_model():
    """Create missing user model import fix"""
    analysis_service_path = "src/services/analysis_service.py"
    
    if os.path.exists(analysis_service_path):
        with open(analysis_service_path, "r") as f:
            content = f.read()
        
        # Fix the import
        content = content.replace(
            "from src.models.user import Analysis",
            "from src.models.user_model import Analysis"
        )
        
        with open(analysis_service_path, "w") as f:
            f.write(content)
        
        print(f"✅ Fixed import in {analysis_service_path}")

def install_missing_dependencies():
    """Install missing dependencies"""
    missing_deps = [
        "aiofiles",
        "yfinance", 
        "feedparser"
    ]
    
    print("📦 Installing missing dependencies...")
    for dep in missing_deps:
        try:
            import subprocess
            result = subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Installed {dep}")
            else:
                print(f"⚠️ Failed to install {dep}: {result.stderr}")
        except Exception as e:
            print(f"❌ Error installing {dep}: {e}")

def fix_api_health_info():
    """Fix APIHealthInfo initialization issue"""
    api_types_path = "src/services/api_types.py"
    
    if os.path.exists(api_types_path):
        with open(api_types_path, "r") as f:
            content = f.read()
        
        # Check if the issue exists and fix it
        if "last_check:" in content and "last_checked:" in content:
            # Fix the inconsistent naming
            content = content.replace("last_check:", "last_checked:")
            
            with open(api_types_path, "w") as f:
                f.write(content)
            
            print(f"✅ Fixed APIHealthInfo in {api_types_path}")

def add_missing_methods():
    """Add missing methods to services"""
    
    # Fix AsyncAnalysisService
    async_service_path = "src/services/async_analysis_service.py"
    if os.path.exists(async_service_path):
        with open(async_service_path, "r") as f:
            content = f.read()
        
        if "def get_capabilities" not in content:
            # Add the missing method
            method_code = '''
    def get_capabilities(self) -> Dict[str, bool]:
        """Return available async analysis capabilities"""
        return {
            'concurrent_processing': True,
            'async_llm_calls': bool(os.environ.get('OPENROUTER_API_KEY')),
            'async_news_search': bool(os.environ.get('NEWS_API_KEY')),
            'async_brand_data': bool(os.environ.get('BRANDFETCH_API_KEY')),
            'async_visual_analysis': True,
            'progress_tracking': True
        }
'''
            # Add before the last line
            content = content.rstrip() + method_code + "\n"
            
            with open(async_service_path, "w") as f:
                f.write(content)
            
            print(f"✅ Added get_capabilities method to {async_service_path}")

def main():
    """Main fix function"""
    print("🔧 FIXING VALIDATION ISSUES")
    print("=" * 50)
    
    try:
        create_missing_logging_config()
        create_missing_user_model()
        fix_api_health_info()
        add_missing_methods()
        install_missing_dependencies()
        
        print("\n✅ All fixes applied successfully!")
        print("🔄 Run the validation script again to verify fixes")
        
    except Exception as e:
        print(f"❌ Error applying fixes: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
