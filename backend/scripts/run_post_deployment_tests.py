#!/usr/bin/env python3
"""
Post-Deployment Test Runner for RAG AI Agent

This script runs the complete post-deployment testing suite including:
- Core functionality tests
- End-to-end workflow tests
- Performance and reliability checks

Requirements: 7.1, 7.2, 7.3, 7.4, 6.3, 6.4
"""

import os
import sys
import json
import time
import argparse
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

class PostDeploymentTestRunner:
    """Orchestrates all post-deployment tests"""
    
    def __init__(self, base_url: str, timeout: int = 60, output_dir: Optional[str] = None):
        """
        Initialize the test runner
        
        Args:
            base_url: The base URL of the deployed application
            timeout: Request timeout in seconds
            output_dir: Directory to save test reports
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.output_dir = output_dir or "test_reports"
        self.scripts_dir = Path(__file__).parent
        
        # Ensure output directory exists
        Path(self.output_dir).mkdir(exist_ok=True)
        
    def run_core_functionality_tests(self) -> Dict[str, Any]:
        """Run core functionality tests"""
        print("🔧 Running Core Functionality Tests...")
        print("-" * 50)
        
        script_path = self.scripts_dir / "test_core_functionality.py"
        output_file = Path(self.output_dir) / "core_functionality_results.json"
        
        try:
            cmd = [
                sys.executable, str(script_path),
                "--url", self.base_url,
                "--timeout", str(self.timeout),
                "--output", str(output_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # Load results from output file
            if output_file.exists():
                with open(output_file, 'r') as f:
                    results = json.load(f)
            else:
                results = {"error": "No output file generated"}
            
            results["exit_code"] = result.returncode
            results["stdout"] = result.stdout
            results["stderr"] = result.stderr
            
            return results
            
        except subprocess.TimeoutExpired:
            return {
                "error": "Core functionality tests timed out",
                "exit_code": -1,
                "timeout": True
            }
        except Exception as e:
            return {
                "error": f"Failed to run core functionality tests: {str(e)}",
                "exit_code": -1
            }
    
    def run_e2e_workflow_tests(self) -> Dict[str, Any]:
        """Run end-to-end workflow tests"""
        print("\n🌐 Running End-to-End Workflow Tests...")
        print("-" * 50)
        
        script_path = self.scripts_dir / "test_e2e_workflows.py"
        output_file = Path(self.output_dir) / "e2e_workflow_results.json"
        
        try:
            cmd = [
                sys.executable, str(script_path),
                "--url", self.base_url,
                "--timeout", str(self.timeout),
                "--output", str(output_file),
                "--concurrent-users", "3"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            # Load results from output file
            if output_file.exists():
                with open(output_file, 'r') as f:
                    results = json.load(f)
            else:
                results = {"error": "No output file generated"}
            
            results["exit_code"] = result.returncode
            results["stdout"] = result.stdout
            results["stderr"] = result.stderr
            
            return results
            
        except subprocess.TimeoutExpired:
            return {
                "error": "E2E workflow tests timed out",
                "exit_code": -1,
                "timeout": True
            }
        except Exception as e:
            return {
                "error": f"Failed to run E2E workflow tests: {str(e)}",
                "exit_code": -1
            }
    
    def check_prerequisites(self) -> Dict[str, bool]:
        """Check if all prerequisites are met"""
        print("🔍 Checking Prerequisites...")
        
        checks = {}
        
        # Check if required Python packages are installed
        required_packages = ['requests', 'aiohttp']
        for package in required_packages:
            try:
                __import__(package)
                checks[f"package_{package}"] = True
            except ImportError:
                checks[f"package_{package}"] = False
        
        # Check if test scripts exist
        core_script = self.scripts_dir / "test_core_functionality.py"
        e2e_script = self.scripts_dir / "test_e2e_workflows.py"
        
        checks["core_script_exists"] = core_script.exists()
        checks["e2e_script_exists"] = e2e_script.exists()
        
        # Check if application is accessible
        try:
            import requests
            response = requests.get(f"{self.base_url}/docs", timeout=10)
            checks["application_accessible"] = response.status_code == 200
        except Exception:
            checks["application_accessible"] = False
        
        # Print results
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check.replace('_', ' ').title()}")
        
        return checks
    
    def generate_consolidated_report(self, core_results: Dict[str, Any], 
                                   e2e_results: Dict[str, Any], 
                                   prerequisites: Dict[str, bool]) -> Dict[str, Any]:
        """Generate a consolidated test report"""
        
        # Extract key metrics
        core_success = core_results.get("summary", {}).get("success_rate", 0) if "summary" in core_results else 0
        e2e_success = e2e_results.get("summary", {}).get("success_rate", 0) if "summary" in e2e_results else 0
        
        core_tests = core_results.get("summary", {}).get("total_tests", 0) if "summary" in core_results else 0
        e2e_workflows = e2e_results.get("summary", {}).get("total_workflows", 0) if "summary" in e2e_results else 0
        
        # Calculate overall success
        all_prereqs_passed = all(prerequisites.values())
        core_passed = core_results.get("exit_code", -1) == 0
        e2e_passed = e2e_results.get("exit_code", -1) == 0
        
        overall_success = all_prereqs_passed and core_passed and e2e_passed
        
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "application_url": self.base_url,
            "overall_success": overall_success,
            "summary": {
                "prerequisites_passed": all_prereqs_passed,
                "core_functionality_passed": core_passed,
                "e2e_workflows_passed": e2e_passed,
                "core_success_rate": core_success,
                "e2e_success_rate": e2e_success,
                "total_core_tests": core_tests,
                "total_e2e_workflows": e2e_workflows
            },
            "prerequisites": prerequisites,
            "core_functionality_results": core_results,
            "e2e_workflow_results": e2e_results,
            "recommendations": self._generate_recommendations(core_results, e2e_results, prerequisites)
        }
        
        return report
    
    def _generate_recommendations(self, core_results: Dict[str, Any], 
                                e2e_results: Dict[str, Any], 
                                prerequisites: Dict[str, bool]) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Prerequisites recommendations
        if not prerequisites.get("application_accessible", True):
            recommendations.append("❌ Application is not accessible. Check deployment status and URL.")
        
        missing_packages = [pkg.replace("package_", "") for pkg, passed in prerequisites.items() 
                          if pkg.startswith("package_") and not passed]
        if missing_packages:
            recommendations.append(f"📦 Install missing packages: {', '.join(missing_packages)}")
        
        # Core functionality recommendations
        core_success_rate = core_results.get("summary", {}).get("success_rate", 0)
        if core_success_rate < 100:
            recommendations.append(f"🔧 Core functionality success rate is {core_success_rate:.1f}%. Review failed tests.")
        
        # E2E workflow recommendations
        e2e_success_rate = e2e_results.get("summary", {}).get("success_rate", 0)
        if e2e_success_rate < 80:
            recommendations.append(f"🌐 E2E workflow success rate is {e2e_success_rate:.1f}%. Review workflow failures.")
        
        # Performance recommendations
        if "summary" in e2e_results:
            avg_response_time = e2e_results["summary"].get("average_response_time", 0)
            if avg_response_time > 5.0:
                recommendations.append(f"⚡ Average response time is {avg_response_time:.2f}s. Consider performance optimization.")
        
        # API reliability recommendations
        if "summary" in e2e_results:
            api_success_rate = e2e_results["summary"].get("api_success_rate", 0)
            if api_success_rate < 95:
                recommendations.append(f"🔗 API success rate is {api_success_rate:.1f}%. Check for intermittent failures.")
        
        if not recommendations:
            recommendations.append("✅ All tests passed successfully! Your deployment is ready for production.")
        
        return recommendations
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run the complete post-deployment test suite"""
        print("🚀 Starting Post-Deployment Test Suite")
        print(f"Application URL: {self.base_url}")
        print(f"Output Directory: {self.output_dir}")
        print("=" * 60)
        
        start_time = time.time()
        
        # Step 1: Check prerequisites
        prerequisites = self.check_prerequisites()
        
        if not all(prerequisites.values()):
            print("\n❌ Prerequisites not met. Please resolve issues before running tests.")
            return self.generate_consolidated_report({}, {}, prerequisites)
        
        # Step 2: Run core functionality tests
        core_results = self.run_core_functionality_tests()
        
        # Step 3: Run E2E workflow tests
        e2e_results = self.run_e2e_workflow_tests()
        
        # Step 4: Generate consolidated report
        report = self.generate_consolidated_report(core_results, e2e_results, prerequisites)
        report["total_duration"] = round(time.time() - start_time, 2)
        
        # Step 5: Save consolidated report
        report_file = Path(self.output_dir) / "consolidated_test_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Step 6: Print final summary
        self.print_final_summary(report)
        
        return report
    
    def print_final_summary(self, report: Dict[str, Any]):
        """Print final test summary"""
        print("\n" + "=" * 60)
        print("📋 FINAL TEST SUMMARY")
        print("=" * 60)
        
        summary = report["summary"]
        
        print(f"Overall Success: {'✅ PASS' if report['overall_success'] else '❌ FAIL'}")
        print(f"Total Duration: {report.get('total_duration', 0):.2f}s")
        print()
        
        print("Component Results:")
        print(f"  Prerequisites: {'✅ PASS' if summary['prerequisites_passed'] else '❌ FAIL'}")
        print(f"  Core Functionality: {'✅ PASS' if summary['core_functionality_passed'] else '❌ FAIL'} ({summary['core_success_rate']:.1f}%)")
        print(f"  E2E Workflows: {'✅ PASS' if summary['e2e_workflows_passed'] else '❌ FAIL'} ({summary['e2e_success_rate']:.1f}%)")
        print()
        
        print("Test Coverage:")
        print(f"  Core Tests: {summary['total_core_tests']}")
        print(f"  E2E Workflows: {summary['total_e2e_workflows']}")
        print()
        
        print("Recommendations:")
        for rec in report["recommendations"]:
            print(f"  {rec}")
        
        print(f"\n📄 Detailed reports saved in: {self.output_dir}/")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Run complete post-deployment test suite for RAG AI Agent")
    parser.add_argument("--url", required=True, help="Base URL of the deployed application")
    parser.add_argument("--timeout", type=int, default=60, help="Request timeout in seconds")
    parser.add_argument("--output-dir", default="test_reports", help="Directory to save test reports")
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose output")
    
    args = parser.parse_args()
    
    # Initialize test runner
    runner = PostDeploymentTestRunner(args.url, args.timeout, args.output_dir)
    
    try:
        # Run all tests
        report = runner.run_all_tests()
        
        # Exit with appropriate code
        sys.exit(0 if report["overall_success"] else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()