#!/usr/bin/env python3
"""
Test runner for existing Flask API functionality
Runs comprehensive tests on the EXISTING implementation
"""
import os
import sys
import subprocess
import time
import json
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_test_suite():
    """Run comprehensive test suite for existing API"""
    
    print("🧪 Starting comprehensive test suite for EXISTING Flask API")
    print("=" * 60)
    
    # Test configuration
    test_env = os.environ.copy()
    test_env.update({
        'FLASK_ENV': 'testing',
        'TESTING': 'true',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        # Mock API keys for testing
        'OPENROUTER_API_KEY': 'test-openrouter-key',
        'NEWS_API_KEY': 'test-news-key',
        'BRANDFETCH_API_KEY': 'test-brandfetch-key',
        'OPENCORPORATES_API_KEY': 'test-opencorporates-key'
    })
    
    # Test results
    results = {
        'total_tests': 0,
        'passed': 0,
        'failed': 0,
        'skipped': 0,
        'test_files': [],
        'start_time': datetime.now(),
        'errors': []
    }
    
    # Test files to run
    test_files = [
        'test_existing_api.py',
        'test_existing_database.py', 
        'test_integration_workflow.py'
    ]
    
    print(f"📋 Running tests from {len(test_files)} test files:")
    for test_file in test_files:
        print(f"   • {test_file}")
    print()
    
    # Run each test file
    for test_file in test_files:
        print(f"🔍 Running {test_file}...")
        
        try:
            # Run pytest on specific file
            cmd = [
                sys.executable, '-m', 'pytest', 
                test_file,
                '-v',
                '--tb=short',
                '--no-header',
                '--disable-warnings'
            ]
            
            result = subprocess.run(
                cmd,
                cwd=os.path.dirname(__file__),
                env=test_env,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per file
            )
            
            # Parse results
            output_lines = result.stdout.split('\n')
            test_summary = None
            
            for line in output_lines:
                if '=====' in line and ('passed' in line or 'failed' in line):
                    test_summary = line
                    break
            
            file_results = {
                'file': test_file,
                'return_code': result.returncode,
                'summary': test_summary,
                'output': result.stdout,
                'errors': result.stderr
            }
            
            results['test_files'].append(file_results)
            
            if result.returncode == 0:
                print(f"   ✅ {test_file} - PASSED")
                if test_summary:
                    print(f"      {test_summary.strip()}")
            else:
                print(f"   ❌ {test_file} - FAILED")
                if test_summary:
                    print(f"      {test_summary.strip()}")
                if result.stderr:
                    print(f"      Error: {result.stderr[:200]}...")
                    
        except subprocess.TimeoutExpired:
            print(f"   ⏰ {test_file} - TIMEOUT")
            results['errors'].append(f"{test_file}: Test timeout")
            
        except Exception as e:
            print(f"   💥 {test_file} - ERROR: {e}")
            results['errors'].append(f"{test_file}: {str(e)}")
        
        print()
    
    # Calculate totals
    for file_result in results['test_files']:
        if file_result['summary']:
            # Parse pytest summary line
            summary = file_result['summary']
            if 'passed' in summary:
                # Extract numbers from summary
                import re
                numbers = re.findall(r'(\d+)', summary)
                if numbers:
                    if 'failed' in summary:
                        results['failed'] += int(numbers[1]) if len(numbers) > 1 else 0
                        results['passed'] += int(numbers[0])
                    else:
                        results['passed'] += int(numbers[0])
                    
                    results['total_tests'] += sum(int(n) for n in numbers[:2])
    
    # Print final summary
    results['end_time'] = datetime.now()
    results['duration'] = (results['end_time'] - results['start_time']).total_seconds()
    
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests:     {results['total_tests']}")
    print(f"Passed:          {results['passed']} ✅")
    print(f"Failed:          {results['failed']} ❌")
    print(f"Duration:        {results['duration']:.1f} seconds")
    print(f"Success Rate:    {(results['passed']/max(results['total_tests'], 1)*100):.1f}%")
    
    if results['errors']:
        print(f"\n⚠️  Errors encountered:")
        for error in results['errors']:
            print(f"   • {error}")
    
    print("\n" + "=" * 60)
    
    # Return success if no failures
    return results['failed'] == 0 and len(results['errors']) == 0

def run_quick_api_validation():
    """Run quick validation of existing API endpoints"""
    
    print("🚀 Quick API Validation")
    print("-" * 30)
    
    try:
        # Import and test basic app functionality
        from app import app
        
        with app.test_client() as client:
            
            # Test health endpoint
            print("Testing /api/health...")
            response = client.get('/api/health')
            if response.status_code == 200:
                print("   ✅ Health endpoint working")
            else:
                print(f"   ❌ Health endpoint failed: {response.status_code}")
                return False
            
            # Test root endpoint
            print("Testing / endpoint...")
            response = client.get('/')
            if response.status_code == 200:
                print("   ✅ Root endpoint working")
            else:
                print(f"   ❌ Root endpoint failed: {response.status_code}")
                return False
            
            # Test brand search
            print("Testing /api/brand/search...")
            response = client.post('/api/brand/search',
                                 data=json.dumps({'query': 'Test'}),
                                 content_type='application/json')
            if response.status_code == 200:
                print("   ✅ Brand search endpoint working")
            else:
                print(f"   ❌ Brand search failed: {response.status_code}")
                return False
            
            # Test analysis start
            print("Testing /api/analyze...")
            response = client.post('/api/analyze',
                                 data=json.dumps({'company_name': 'Test Company'}),
                                 content_type='application/json')
            if response.status_code == 200:
                print("   ✅ Analysis endpoint working")
                
                # Get analysis ID and test status
                data = response.get_json()
                analysis_id = data['data']['analysis_id']
                
                print(f"Testing /api/analyze/{analysis_id}/status...")
                response = client.get(f'/api/analyze/{analysis_id}/status')
                if response.status_code == 200:
                    print("   ✅ Analysis status endpoint working")
                else:
                    print(f"   ❌ Analysis status failed: {response.status_code}")
                    return False
            else:
                print(f"   ❌ Analysis endpoint failed: {response.status_code}")
                return False
        
        print("\n✅ All basic API endpoints are working!")
        return True
        
    except Exception as e:
        print(f"\n❌ API validation failed: {e}")
        return False

def main():
    """Main test runner"""
    
    print("🎯 EXISTING FLASK API TEST SUITE")
    print("Testing what EXISTS, not what we think should exist")
    print("=" * 60)
    
    # Step 1: Quick validation
    print("\n1️⃣ QUICK API VALIDATION")
    if not run_quick_api_validation():
        print("\n❌ Quick validation failed. Stopping tests.")
        return 1
    
    # Step 2: Comprehensive tests
    print("\n2️⃣ COMPREHENSIVE TEST SUITE")
    if not run_test_suite():
        print("\n❌ Some tests failed. Check output above.")
        return 1
    
    print("\n🎉 ALL TESTS PASSED!")
    print("The existing Flask API is working correctly.")
    return 0

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
