#!/usr/bin/env python3
"""
Simple runner script for comprehensive service validation
"""

import os
import sys
import subprocess

def main():
    """Run the comprehensive service validation"""
    print("🚀 Starting Brand Audit App Service Validation")
    print("=" * 60)
    
    # Change to backend directory if not already there
    if not os.path.exists('src'):
        if os.path.exists('backend/src'):
            os.chdir('backend')
            print("📁 Changed to backend directory")
        else:
            print("❌ Could not find src directory. Please run from project root or backend directory.")
            sys.exit(1)
    
    # Check if validation script exists
    if not os.path.exists('comprehensive_service_validation.py'):
        print("❌ Validation script not found. Please ensure comprehensive_service_validation.py exists.")
        sys.exit(1)
    
    # Run the validation
    try:
        result = subprocess.run([sys.executable, 'comprehensive_service_validation.py'], 
                              capture_output=False, text=True)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\n⚠️ Validation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Failed to run validation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
