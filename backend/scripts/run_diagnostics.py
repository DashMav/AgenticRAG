#!/usr/bin/env python3
"""
Diagnostic script runner for RAG AI-Agent.

This script provides a unified interface to run all diagnostic utilities
and troubleshooting tools for the RAG AI-Agent application.

Usage:
    python scripts/run_diagnostics.py [--all] [--quick] [--backend-url URL]

Requirements:
    - All diagnostic scripts in the scripts/ directory
    - Python standard library
"""

import os
import sys
import argparse
import subprocess
import time
from datetime import datetime
from pathlib import Path

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class DiagnosticRunner:
    """Unified diagnostic script runner."""
    
    def __init__(self, backend_url=None, verbose=False):
        self.backend_url = backend_url
        self.verbose = verbose
        self.scripts_dir = Path(__file__).parent
        self.results = {}
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message with color coding."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if level == "SUCCESS":
            print(f"{Colors.GREEN}[{timestamp}] ✅ {message}{Colors.END}")
        elif level == "ERROR":
            print(f"{Colors.RED}[{timestamp}] ❌ {message}{Colors.END}")
        elif level == "WARNING":
            print(f"{Colors.YELLOW}[{timestamp}] ⚠️  {message}{Colors.END}")
        elif level == "INFO":
            print(f"{Colors.BLUE}[{timestamp}] ℹ️  {message}{Colors.END}")
        elif level == "HEADER":
            print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
            print(f"{Colors.BOLD}{Colors.CYAN}{message.center(60)}{Colors.END}")
            print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}\n")
        else:
            print(f"[{timestamp}] {message}")
    
    def run_script(self, script_name: str, args: list = None, timeout: int = 300) -> dict:
        """Run a diagnostic script and return results."""
        script_path = self.scripts_dir / script_name
        
        if not script_path.exists():
            return {
                "success": False,
                "error": f"Script not found: {script_path}",
                "exit_code": -1,
                "stdout": "",
                "stderr": "",
                "duration": 0
            }
        
        cmd = [sys.executable, str(script_path)]
        if args:
            cmd.extend(args)
        
        self.log(f"Running: {' '.join(cmd)}", "INFO")
        
        try:
            start_time = time.time()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.scripts_dir.parent  # Run from project root
            )
            duration = time.time() - start_time
            
            return {
                "success": result.returncode == 0,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration": duration,
                "command": ' '.join(cmd)
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Script timed out after {timeout} seconds",
                "exit_code": -2,
                "stdout": "",
                "stderr": "",
                "duration": timeout
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "exit_code": -3,
                "stdout": "",
                "stderr": "",
                "duration": 0
            }
    
    def run_validation_script(self):
        """Run the main validation script."""
        self.log("DEPLOYMENT VALIDATION", "HEADER")
        
        # Check if validation script exists in root directory
        validation_script = Path("validate_deployment.py")
        if validation_script.exists():
            result = self.run_script("../validate_deployment.py")
        else:
            result = {
                "success": False,
                "error": "validate_deployment.py not found in project root",
                "exit_code": -1,
                "stdout": "",
                "stderr": "",
                "duration": 0
            }
        
        self.results["validation"] = result
        
        if result["success"]:
            self.log(f"Validation completed successfully ({result['duration']:.1f}s)", "SUCCESS")
        else:
            self.log(f"Validation failed: {result.get('error', 'Unknown error')}", "ERROR")
            if result["stderr"]:
                print(f"{Colors.RED}Error output:{Colors.END}")
                print(result["stderr"])
        
        return result["success"]
    
    def run_comprehensive_diagnostics(self):
        """Run comprehensive diagnostic checks."""
        self.log("COMPREHENSIVE DIAGNOSTICS", "HEADER")
        
        args = []
        if self.backend_url:
            args.extend(["--backend-url", self.backend_url])
        if self.verbose:
            args.append("--verbose")
        
        result = self.run_script("diagnose_issues.py", args)
        self.results["diagnostics"] = result
        
        if result["success"]:
            self.log(f"Diagnostics completed successfully ({result['duration']:.1f}s)", "SUCCESS")
        else:
            self.log(f"Diagnostics failed: {result.get('error', 'Unknown error')}", "ERROR")
            if result["stderr"]:
                print(f"{Colors.RED}Error output:{Colors.END}")
                print(result["stderr"])
        
        return result["success"]
    
    def run_network_tests(self):
        """Run network connectivity tests."""
        self.log("NETWORK CONNECTIVITY TESTS", "HEADER")
        
        args = []
        if self.backend_url:
            args.extend(["--backend-url", self.backend_url])
        if self.verbose:
            args.append("--verbose")
        
        result = self.run_script("test_network_connectivity.py", args)
        self.results["network"] = result
        
        if result["success"]:
            self.log(f"Network tests completed successfully ({result['duration']:.1f}s)", "SUCCESS")
        else:
            self.log(f"Network tests failed: {result.get('error', 'Unknown error')}", "ERROR")
            if result["stderr"]:
                print(f"{Colors.RED}Error output:{Colors.END}")
                print(result["stderr"])
        
        return result["success"]
    
    def run_error_reporting(self):
        """Run error reporting and log collection."""
        self.log("ERROR REPORTING AND LOG COLLECTION", "HEADER")
        
        args = ["--generate-report"]
        if self.verbose:
            args.append("--debug")
        
        result = self.run_script("error_reporter.py", args)
        self.results["error_reporting"] = result
        
        if result["success"]:
            self.log(f"Error reporting completed successfully ({result['duration']:.1f}s)", "SUCCESS")
        else:
            self.log(f"Error reporting failed: {result.get('error', 'Unknown error')}", "ERROR")
            if result["stderr"]:
                print(f"{Colors.RED}Error output:{Colors.END}")
                print(result["stderr"])
        
        return result["success"]
    
    def run_quick_diagnostics(self):
        """Run quick diagnostic checks."""
        self.log("QUICK DIAGNOSTICS", "HEADER")
        
        success_count = 0
        total_count = 0
        
        # Run validation
        total_count += 1
        if self.run_validation_script():
            success_count += 1
        
        # Run network tests
        total_count += 1
        if self.run_network_tests():
            success_count += 1
        
        return success_count, total_count
    
    def run_full_diagnostics(self):
        """Run all diagnostic checks."""
        self.log("FULL DIAGNOSTIC SUITE", "HEADER")
        
        success_count = 0
        total_count = 0
        
        # Run validation
        total_count += 1
        if self.run_validation_script():
            success_count += 1
        
        # Run comprehensive diagnostics
        total_count += 1
        if self.run_comprehensive_diagnostics():
            success_count += 1
        
        # Run network tests
        total_count += 1
        if self.run_network_tests():
            success_count += 1
        
        # Run error reporting
        total_count += 1
        if self.run_error_reporting():
            success_count += 1
        
        return success_count, total_count
    
    def generate_summary(self, success_count: int, total_count: int):
        """Generate and display summary of all diagnostic runs."""
        self.log("DIAGNOSTIC SUMMARY", "HEADER")
        
        print(f"{Colors.BOLD}Total Tests Run: {total_count}{Colors.END}")
        print(f"{Colors.GREEN}Successful: {success_count}{Colors.END}")
        print(f"{Colors.RED}Failed: {total_count - success_count}{Colors.END}")
        
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0
        print(f"{Colors.BLUE}Success Rate: {success_rate:.1f}%{Colors.END}")
        
        # Show individual results
        print(f"\n{Colors.BOLD}Individual Results:{Colors.END}")
        for test_name, result in self.results.items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            duration = f"({result['duration']:.1f}s)" if result.get("duration") else ""
            print(f"  {status} {test_name.title()} {duration}")
            
            if not result["success"] and result.get("error"):
                print(f"    Error: {result['error']}")
        
        # Recommendations
        print(f"\n{Colors.BOLD}Recommendations:{Colors.END}")
        
        if success_count == total_count:
            print(f"{Colors.GREEN}  ✨ All diagnostics passed! Your system appears to be ready for deployment.{Colors.END}")
        else:
            print(f"{Colors.YELLOW}  🔧 Some diagnostics failed. Review the errors above and:{Colors.END}")
            print(f"{Colors.YELLOW}     1. Check the troubleshooting guide (TROUBLESHOOTING_GUIDE.md){Colors.END}")
            print(f"{Colors.YELLOW}     2. Review generated error reports{Colors.END}")
            print(f"{Colors.YELLOW}     3. Fix identified issues and re-run diagnostics{Colors.END}")
        
        # Show generated files
        generated_files = []
        if os.path.exists("diagnostic_report.json"):
            generated_files.append("diagnostic_report.json")
        
        error_reports = [f for f in os.listdir(".") if f.startswith("error_report_") and f.endswith(".json")]
        generated_files.extend(error_reports)
        
        if generated_files:
            print(f"\n{Colors.BOLD}Generated Files:{Colors.END}")
            for file in generated_files:
                print(f"  📄 {file}")
        
        return success_count == total_count

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="RAG AI-Agent Diagnostic Runner")
    parser.add_argument("--all", action="store_true", help="Run all diagnostic tests")
    parser.add_argument("--quick", action="store_true", help="Run quick diagnostic tests only")
    parser.add_argument("--backend-url", help="Backend URL to test")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    print(f"{Colors.BOLD}{Colors.BLUE}🚀 RAG AI-Agent Diagnostic Runner{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    
    # Create diagnostic runner
    runner = DiagnosticRunner(
        backend_url=args.backend_url,
        verbose=args.verbose
    )
    
    try:
        if args.quick:
            success_count, total_count = runner.run_quick_diagnostics()
        elif args.all or not any([args.quick]):
            # Run full diagnostics by default
            success_count, total_count = runner.run_full_diagnostics()
        
        # Generate summary
        all_passed = runner.generate_summary(success_count, total_count)
        
        # Exit with appropriate code
        sys.exit(0 if all_passed else 1)
    
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Diagnostics interrupted by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Diagnostics failed with error: {str(e)}{Colors.END}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()