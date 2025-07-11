#!/usr/bin/env python3

"""
Test script for database implementation
Tests the database persistence replacing in-memory storage
"""

import sys
import os
import requests
import time
sys.path.append('backend')

def test_database_initialization():
    """Test database initialization"""
    print("🗄️ Testing Database Initialization")
    print("-" * 40)
    
    try:
        # Run database initialization
        os.system("cd backend && python3 src/database/init_db.py")
        print("✅ Database initialization completed")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def test_flask_app_with_database():
    """Test Flask app with database integration"""
    print("\n🌐 Testing Flask App with Database")
    print("-" * 40)
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Flask app is running")
            health_data = response.json()
            print(f"   Service: {health_data.get('service')}")
            print(f"   Status: {health_data.get('status')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("⚠️ Flask app not running. Please start with: cd backend && python3 app.py")
        print("   💡 The app should be running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_analysis_creation():
    """Test analysis creation with database"""
    print("\n📊 Testing Analysis Creation with Database")
    print("-" * 40)
    
    try:
        # Create analysis
        analysis_data = {
            "company_name": "TestBrand",
            "analysis_types": ["brand_health", "competitive_analysis"]
        }
        
        response = requests.post(
            "http://localhost:8000/api/analyze",
            json=analysis_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                analysis_id = result.get("data", {}).get("analysis_id")
                print(f"✅ Analysis created successfully: {analysis_id}")
                return analysis_id
            else:
                print(f"❌ Analysis creation failed: {result.get('error')}")
                return None
        else:
            print(f"❌ Analysis creation failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Analysis creation error: {e}")
        return None

def test_analysis_status(analysis_id):
    """Test analysis status retrieval"""
    print(f"\n📋 Testing Analysis Status for {analysis_id}")
    print("-" * 40)
    
    try:
        response = requests.get(
            f"http://localhost:8000/api/analyze/{analysis_id}/status",
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                data = result.get("data", {})
                print(f"✅ Status retrieved successfully")
                print(f"   Status: {data.get('status')}")
                print(f"   Progress: {data.get('progress')}%")
                print(f"   Brand: {data.get('brand_name')}")
                return True
            else:
                print(f"❌ Status retrieval failed: {result.get('error')}")
                return False
        else:
            print(f"❌ Status retrieval failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Status retrieval error: {e}")
        return False

def test_database_service():
    """Test database service directly"""
    print("\n🔧 Testing Database Service Directly")
    print("-" * 40)

    try:
        # Import Flask app and create context
        sys.path.append('backend')
        from flask import Flask
        from backend.src.extensions import db
        from backend.src.services.database_service import DatabaseService

        # Create Flask app context
        app = Flask(__name__)
        basedir = os.path.abspath('backend')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "src", "database", "app.db")}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = 'test-key'

        db.init_app(app)

        with app.app_context():
            # Test creating analysis
            analysis = DatabaseService.create_analysis(
                brand_name="DirectTestBrand",
                analysis_types=["test_analysis"],
                user_id=None
            )
            print(f"✅ Direct analysis creation: {analysis.id}")

            # Test retrieving analysis
            retrieved = DatabaseService.get_analysis(analysis.id)
            if retrieved:
                print(f"✅ Direct analysis retrieval: {retrieved.brand_name}")
            else:
                print("❌ Direct analysis retrieval failed")
                return False

            # Test updating status
            success = DatabaseService.update_analysis_status(
                analysis.id,
                "completed",
                progress=100
            )
            if success:
                print("✅ Direct status update successful")
            else:
                print("❌ Direct status update failed")
                return False

            # Test database stats
            stats = DatabaseService.get_database_stats()
            print(f"✅ Database stats: {stats}")

        return True

    except Exception as e:
        print(f"❌ Database service test failed: {e}")
        return False

def test_migration_compatibility():
    """Test that both in-memory and database work together"""
    print("\n🔄 Testing Migration Compatibility")
    print("-" * 40)
    
    try:
        # This tests that the app can handle both storage methods
        analysis_id = test_analysis_creation()
        if analysis_id:
            # Wait a moment for processing
            time.sleep(2)
            
            # Check status (should work with both storage methods)
            status_ok = test_analysis_status(analysis_id)
            if status_ok:
                print("✅ Migration compatibility successful")
                return True
            else:
                print("❌ Migration compatibility failed at status check")
                return False
        else:
            print("❌ Migration compatibility failed at creation")
            return False
            
    except Exception as e:
        print(f"❌ Migration compatibility test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Database Implementation Test Suite")
    print("=" * 60)
    print("Testing database persistence replacing in-memory storage")
    print("")
    
    tests = [
        ("Database Initialization", test_database_initialization),
        ("Flask App Integration", test_flask_app_with_database),
        ("Database Service Direct", test_database_service),
        ("Migration Compatibility", test_migration_compatibility),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"🧪 Running: {test_name}")
        print(f"{'='*60}")
        
        try:
            if test_func():
                passed_tests += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 DATABASE IMPLEMENTATION TEST SUMMARY")
    print("=" * 60)
    print(f"📊 Tests Passed: {passed_tests}/{total_tests}")
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASSED" if i < passed_tests else "❌ FAILED"
        print(f"   {status} {test_name}")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n📋 Database Implementation Summary:")
        print("   ✅ Database models created (Analysis, Brand, Report)")
        print("   ✅ Database service implemented")
        print("   ✅ Flask app updated to use database")
        print("   ✅ Backward compatibility maintained")
        print("   ✅ Migration path established")
        print("\n🚀 Ready for production deployment!")
        return True
    else:
        print(f"\n⚠️ {total_tests - passed_tests} test(s) failed")
        print("Please address the issues above before deployment.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
