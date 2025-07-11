#!/usr/bin/env python3
"""
Comprehensive integration test runner and reporting system
"""
import os
import sys
import json
import time
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import concurrent.futures
from dataclasses import dataclass, asdict

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.logging_config import setup_logging, IntegrationTestLogger


@dataclass
class TestResult:
    """Test result data structure"""
    name: str
    category: str
    status: str  # 'passed', 'failed', 'skipped', 'error'
    duration: float
    message: str = ""
    details: Dict[str, Any] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()
        if self.details is None:
            self.details = {}


class IntegrationTestRunner:
    """Main integration test runner"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.results: List[TestResult] = []
        self.session_id = f"test_session_{int(time.time())}"
        
        # Setup logging
        self.loggers = setup_logging(
            log_level=self.config.get('log_level', 'INFO'),
            log_dir=self.config.get('log_dir', 'logs')
        )
        self.test_logger = IntegrationTestLogger('integration_test_runner')
        self.test_logger.start_test_session(self.session_id)
        
        # Test categories
        self.test_categories = {
            'backend_api': 'Backend API Integration Tests',
            'websocket': 'WebSocket Integration Tests',
            'frontend_components': 'Frontend Component Tests',
            'end_to_end': 'End-to-End Data Flow Tests',
            'error_handling': 'Error Handling Tests',
            'performance': 'Performance Tests'
        }
    
    def run_backend_tests(self) -> List[TestResult]:
        """Run backend integration tests"""
        self.test_logger.log_test_start('backend_integration_tests', 'backend')
        results = []
        
        test_files = [
            'test_api_integration.py',
            'test_websocket_integration.py',
            'test_error_handling.py'
        ]
        
        for test_file in test_files:
            test_path = Path(__file__).parent / test_file
            if test_path.exists():
                result = self._run_pytest(test_file, 'backend_api')
                results.append(result)
            else:
                results.append(TestResult(
                    name=test_file,
                    category='backend_api',
                    status='skipped',
                    duration=0,
                    message=f"Test file not found: {test_file}"
                ))
        
        return results
    
    def run_frontend_tests(self) -> List[TestResult]:
        """Run frontend integration tests"""
        self.test_logger.log_test_start('frontend_integration_tests', 'frontend')
        results = []
        
        # Run Vitest for component tests
        frontend_dir = Path(__file__).parent.parent.parent / 'frontend'
        if frontend_dir.exists():
            result = self._run_vitest(frontend_dir)
            results.append(result)
        else:
            results.append(TestResult(
                name='frontend_component_tests',
                category='frontend_components',
                status='skipped',
                duration=0,
                message="Frontend directory not found"
            ))
        
        return results
    
    def run_e2e_tests(self) -> List[TestResult]:
        """Run end-to-end tests"""
        self.test_logger.log_test_start('e2e_tests', 'e2e')
        results = []
        
        # Run Playwright tests
        frontend_dir = Path(__file__).parent.parent.parent / 'frontend'
        if frontend_dir.exists():
            result = self._run_playwright(frontend_dir)
            results.append(result)
        else:
            results.append(TestResult(
                name='e2e_data_flow_tests',
                category='end_to_end',
                status='skipped',
                duration=0,
                message="Frontend directory not found"
            ))
        
        return results
    
    def run_all_tests(self, parallel: bool = False) -> List[TestResult]:
        """Run all integration tests"""
        print(f"🚀 Starting comprehensive integration test suite...")
        print(f"📋 Session ID: {self.session_id}")
        
        all_results = []
        
        if parallel:
            # Run tests in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                futures = {
                    executor.submit(self.run_backend_tests): 'backend',
                    executor.submit(self.run_frontend_tests): 'frontend',
                    executor.submit(self.run_e2e_tests): 'e2e'
                }
                
                for future in concurrent.futures.as_completed(futures):
                    test_type = futures[future]
                    try:
                        results = future.result()
                        all_results.extend(results)
                        print(f"✅ {test_type} tests completed")
                    except Exception as e:
                        print(f"❌ {test_type} tests failed: {e}")
                        all_results.append(TestResult(
                            name=f'{test_type}_tests',
                            category=test_type,
                            status='error',
                            duration=0,
                            message=str(e)
                        ))
        else:
            # Run tests sequentially
            print("🔧 Running backend tests...")
            all_results.extend(self.run_backend_tests())
            
            print("🎨 Running frontend tests...")
            all_results.extend(self.run_frontend_tests())
            
            print("🌐 Running end-to-end tests...")
            all_results.extend(self.run_e2e_tests())
        
        self.results = all_results
        return all_results
    
    def _run_pytest(self, test_file: str, category: str) -> TestResult:
        """Run a pytest file and return result"""
        start_time = time.time()
        
        try:
            cmd = ['python', '-m', 'pytest', test_file, '-v', '--tb=short']
            result = subprocess.run(
                cmd,
                cwd=Path(__file__).parent,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                status = 'passed'
                message = "All tests passed"
            else:
                status = 'failed'
                message = result.stdout + result.stderr
            
            return TestResult(
                name=test_file,
                category=category,
                status=status,
                duration=duration,
                message=message,
                details={
                    'return_code': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
            )
            
        except subprocess.TimeoutExpired:
            return TestResult(
                name=test_file,
                category=category,
                status='error',
                duration=time.time() - start_time,
                message="Test timed out after 5 minutes"
            )
        except Exception as e:
            return TestResult(
                name=test_file,
                category=category,
                status='error',
                duration=time.time() - start_time,
                message=str(e)
            )
    
    def _run_vitest(self, frontend_dir: Path) -> TestResult:
        """Run Vitest tests"""
        start_time = time.time()
        
        try:
            cmd = ['npm', 'run', 'test:integration']
            result = subprocess.run(
                cmd,
                cwd=frontend_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                status = 'passed'
                message = "Frontend component tests passed"
            else:
                status = 'failed'
                message = result.stdout + result.stderr
            
            return TestResult(
                name='frontend_component_tests',
                category='frontend_components',
                status=status,
                duration=duration,
                message=message,
                details={
                    'return_code': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
            )
            
        except Exception as e:
            return TestResult(
                name='frontend_component_tests',
                category='frontend_components',
                status='error',
                duration=time.time() - start_time,
                message=str(e)
            )
    
    def _run_playwright(self, frontend_dir: Path) -> TestResult:
        """Run Playwright E2E tests"""
        start_time = time.time()
        
        try:
            cmd = ['npx', 'playwright', 'test', 'end-to-end-data-flow.spec.js']
            result = subprocess.run(
                cmd,
                cwd=frontend_dir,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes for E2E tests
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                status = 'passed'
                message = "End-to-end tests passed"
            else:
                status = 'failed'
                message = result.stdout + result.stderr
            
            return TestResult(
                name='e2e_data_flow_tests',
                category='end_to_end',
                status=status,
                duration=duration,
                message=message,
                details={
                    'return_code': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
            )
            
        except Exception as e:
            return TestResult(
                name='e2e_data_flow_tests',
                category='end_to_end',
                status='error',
                duration=time.time() - start_time,
                message=str(e)
            )
    
    def generate_report(self, output_format: str = 'json') -> str:
        """Generate test report"""
        summary = self._generate_summary()
        
        if output_format == 'json':
            return self._generate_json_report(summary)
        elif output_format == 'html':
            return self._generate_html_report(summary)
        elif output_format == 'console':
            return self._generate_console_report(summary)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate test summary statistics"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.status == 'passed')
        failed_tests = sum(1 for r in self.results if r.status == 'failed')
        error_tests = sum(1 for r in self.results if r.status == 'error')
        skipped_tests = sum(1 for r in self.results if r.status == 'skipped')
        
        total_duration = sum(r.duration for r in self.results)
        
        # Group by category
        by_category = {}
        for result in self.results:
            if result.category not in by_category:
                by_category[result.category] = []
            by_category[result.category].append(result)
        
        return {
            'session_id': self.session_id,
            'timestamp': datetime.utcnow().isoformat(),
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'error_tests': error_tests,
            'skipped_tests': skipped_tests,
            'success_rate': passed_tests / total_tests if total_tests > 0 else 0,
            'total_duration': total_duration,
            'average_duration': total_duration / total_tests if total_tests > 0 else 0,
            'by_category': {
                category: {
                    'total': len(results),
                    'passed': sum(1 for r in results if r.status == 'passed'),
                    'failed': sum(1 for r in results if r.status == 'failed'),
                    'error': sum(1 for r in results if r.status == 'error'),
                    'skipped': sum(1 for r in results if r.status == 'skipped'),
                    'duration': sum(r.duration for r in results)
                }
                for category, results in by_category.items()
            },
            'test_results': [asdict(result) for result in self.results]
        }
    
    def _generate_json_report(self, summary: Dict[str, Any]) -> str:
        """Generate JSON report"""
        report_path = Path('logs') / f'integration_test_report_{self.session_id}.json'
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return str(report_path)
    
    def _generate_console_report(self, summary: Dict[str, Any]) -> str:
        """Generate console report"""
        report = []
        report.append("=" * 80)
        report.append("🧪 INTEGRATION TEST REPORT")
        report.append("=" * 80)
        report.append(f"Session ID: {summary['session_id']}")
        report.append(f"Timestamp: {summary['timestamp']}")
        report.append(f"Total Duration: {summary['total_duration']:.2f}s")
        report.append("")
        
        # Summary statistics
        report.append("📊 SUMMARY")
        report.append("-" * 40)
        report.append(f"Total Tests: {summary['total_tests']}")
        report.append(f"✅ Passed: {summary['passed_tests']}")
        report.append(f"❌ Failed: {summary['failed_tests']}")
        report.append(f"🚨 Errors: {summary['error_tests']}")
        report.append(f"⏭️  Skipped: {summary['skipped_tests']}")
        report.append(f"📈 Success Rate: {summary['success_rate']:.1%}")
        report.append("")
        
        # By category
        report.append("📋 BY CATEGORY")
        report.append("-" * 40)
        for category, stats in summary['by_category'].items():
            report.append(f"{category}:")
            report.append(f"  Total: {stats['total']}, Passed: {stats['passed']}, "
                         f"Failed: {stats['failed']}, Duration: {stats['duration']:.2f}s")
        report.append("")
        
        # Individual test results
        report.append("🔍 DETAILED RESULTS")
        report.append("-" * 40)
        for result in self.results:
            status_icon = {
                'passed': '✅',
                'failed': '❌',
                'error': '🚨',
                'skipped': '⏭️'
            }.get(result.status, '❓')
            
            report.append(f"{status_icon} {result.name} ({result.category}) - {result.duration:.2f}s")
            if result.message and result.status in ['failed', 'error']:
                # Truncate long messages
                message = result.message[:200] + "..." if len(result.message) > 200 else result.message
                report.append(f"   {message}")
        
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_artifacts(self):
        """Save test artifacts"""
        artifacts_dir = Path('logs') / 'test_artifacts' / self.session_id
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        
        # Save detailed results
        with open(artifacts_dir / 'results.json', 'w') as f:
            json.dump([asdict(result) for result in self.results], f, indent=2)
        
        # Save test logs
        test_summary = self.test_logger.get_test_summary()
        with open(artifacts_dir / 'test_summary.json', 'w') as f:
            json.dump(test_summary, f, indent=2)
        
        print(f"📁 Test artifacts saved to: {artifacts_dir}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Run integration tests for brand audit application')
    parser.add_argument('--parallel', action='store_true', help='Run tests in parallel')
    parser.add_argument('--format', choices=['json', 'console', 'html'], default='console',
                       help='Report output format')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='Logging level')
    parser.add_argument('--category', choices=['backend', 'frontend', 'e2e', 'all'], 
                       default='all', help='Test category to run')
    
    args = parser.parse_args()
    
    # Configuration
    config = {
        'log_level': args.log_level,
        'log_dir': 'logs'
    }
    
    # Create test runner
    runner = IntegrationTestRunner(config)
    
    # Run tests based on category
    if args.category == 'backend':
        results = runner.run_backend_tests()
    elif args.category == 'frontend':
        results = runner.run_frontend_tests()
    elif args.category == 'e2e':
        results = runner.run_e2e_tests()
    else:
        results = runner.run_all_tests(parallel=args.parallel)
    
    # Generate and display report
    report = runner.generate_report(args.format)
    
    if args.format == 'console':
        print(report)
    else:
        print(f"📄 Report saved to: {report}")
    
    # Save artifacts
    runner.save_artifacts()
    
    # Exit with appropriate code
    failed_tests = sum(1 for r in results if r.status in ['failed', 'error'])
    sys.exit(1 if failed_tests > 0 else 0)


if __name__ == '__main__':
    main()
