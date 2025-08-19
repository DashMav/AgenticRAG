#!/usr/bin/env python3
"""
Master Deployment Validation Script for RAG AI-Agent

This script runs all verification steps and provides comprehensive deployment
validation and success reporting. It orchestrates all existing validation
tools and provides a final deployment readiness assessment.

Usage:
    python scripts/master_deployment_validator.py
    python scripts/master_deployment_validator.py --config config.json
    python scripts/master_deployment_validator.py --generate-report

Requirements:
    - All validation scripts in scripts/ directory
    - API keys configured (environment variables or config file)
    - Internet connection for API testing
"""

import os
import sys
import json
import argparse
import subprocess
import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import importlib.util

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from validate_api_keys import APIKeyValidator, APIConfig
    from validate_environment import EnvironmentValidator
except ImportError as e:
    print(f"Error importing validation modules: {e}")
    print("Please ensure all validation scripts are in the scripts/ directory")
    sys.exit(1)

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

@dataclass
class ValidationPhase:
    """Represents a validation phase with its results."""
    name: str
    status: bool
    message: str
    details: Dict = None
    duration: float = 0.0
    critical: bool = True  # Whether failure blocks deployment

@dataclass
class DeploymentReport:
    """Comprehensive deployment validation report."""
    timestamp: str
    overall_status: bool
    phases: List[ValidationPhase]
    summary: Dict
    recommendations: List[str]
    next_steps: List[str]

def print_header(text: str, level: int = 1):
    """Print a formatted header."""
    if level == 1:
        print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.END}")
        print(f"{Colors.BLUE}{Colors.BOLD}{text.center(70)}{Colors.END}")
        print(f"{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.END}\n")
    elif level == 2:
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'-'*50}{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD}{text}{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'-'*50}{Colors.END}\n")
    else:
        print(f"\n{Colors.MAGENTA}{Colors.UNDERLINE}{text}{Colors.END}\n")

def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_info(text: str):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def print_step(text: str):
    """Print step message."""
    print(f"{Colors.CYAN}→ {text}{Colors.END}")

class MasterDeploymentValidator:
    """Master validator that orchestrates all validation phases."""
    
    def __init__(self, config_path: Optional[str] = None, verbose: bool = False):
        self.config_path = config_path
        self.verbose = verbose
        self.validation_phases = []
        self.start_time = datetime.datetime.now()
        
        # Load configuration
        if config_path:
            self.api_config = APIConfig.from_file(config_path)
        else:
            self.api_config = APIConfig.from_env()
    
    def run_subprocess_validation(self, script_name: str, args: List[str] = None) -> Tuple[bool, str, str]:
        """Run a validation script as subprocess."""
        script_path = Path(__file__).parent / script_name
        
        if not script_path.exists():
            return False, "", f"Script not found: {script_name}"
        
        cmd = [sys.executable, str(script_path)]
        if args:
            cmd.extend(args)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 minutes timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Validation script timed out"
        except Exception as e:
            return False, "", str(e)
    
    def validate_environment(self) -> ValidationPhase:
        """Validate local development environment."""
        print_step("Validating local development environment...")
        
        start_time = datetime.datetime.now()
        
        try:
            validator = EnvironmentValidator(verbose=self.verbose)
            results = validator.validate_all()
            
            # Analyze results
            required_checks = [k for k, v in results.items() 
                             if not (v.details and v.details.get("optional"))]
            failed_required = [k for k in required_checks if not results[k].status]
            
            duration = (datetime.datetime.now() - start_time).total_seconds()
            
            if not failed_required:
                return ValidationPhase(
                    name="Environment Setup",
                    status=True,
                    message="All required environment checks passed",
                    details={
                        "total_checks": len(results),
                        "required_passed": len(required_checks) - len(failed_required),
                        "required_total": len(required_checks),
                        "failed_checks": []
                    },
                    duration=duration
                )
            else:
                failed_details = {k: results[k].message for k in failed_required}
                return ValidationPhase(
                    name="Environment Setup",
                    status=False,
                    message=f"{len(failed_required)} required environment checks failed",
                    details={
                        "total_checks": len(results),
                        "required_passed": len(required_checks) - len(failed_required),
                        "required_total": len(required_checks),
                        "failed_checks": failed_details
                    },
                    duration=duration
                )
                
        except Exception as e:
            duration = (datetime.datetime.now() - start_time).total_seconds()
            return ValidationPhase(
                name="Environment Setup",
                status=False,
                message=f"Environment validation failed: {str(e)}",
                duration=duration
            )
    
    def validate_api_keys(self) -> ValidationPhase:
        """Validate API key connectivity."""
        print_step("Validating API key connectivity...")
        
        start_time = datetime.datetime.now()
        
        try:
            validator = APIKeyValidator(self.api_config)
            results = validator.validate_all()
            
            successful_services = [name for name, result in results.items() if result.status]
            failed_services = [name for name, result in results.items() if not result.status]
            
            duration = (datetime.datetime.now() - start_time).total_seconds()
            
            if not failed_services:
                return ValidationPhase(
                    name="API Connectivity",
                    status=True,
                    message="All API services validated successfully",
                    details={
                        "total_services": len(results),
                        "successful": len(successful_services),
                        "failed": 0,
                        "services": {name: result.message for name, result in results.items()}
                    },
                    duration=duration
                )
            else:
                return ValidationPhase(
                    name="API Connectivity",
                    status=False,
                    message=f"{len(failed_services)} API services failed validation",
                    details={
                        "total_services": len(results),
                        "successful": len(successful_services),
                        "failed": len(failed_services),
                        "failed_services": failed_services,
                        "services": {name: result.message for name, result in results.items()}
                    },
                    duration=duration
                )
                
        except Exception as e:
            duration = (datetime.datetime.now() - start_time).total_seconds()
            return ValidationPhase(
                name="API Connectivity",
                status=False,
                message=f"API validation failed: {str(e)}",
                duration=duration
            )
    
    def validate_pinecone_setup(self) -> ValidationPhase:
        """Validate Pinecone configuration and setup."""
        print_step("Validating Pinecone setup...")
        
        start_time = datetime.datetime.now()
        
        success, stdout, stderr = self.run_subprocess_validation("validate_pinecone.py")
        duration = (datetime.datetime.now() - start_time).total_seconds()
        
        if success:
            return ValidationPhase(
                name="Pinecone Setup",
                status=True,
                message="Pinecone configuration validated",
                details={"output": stdout[:500] if stdout else ""},
                duration=duration
            )
        else:
            return ValidationPhase(
                name="Pinecone Setup",
                status=False,
                message="Pinecone validation failed",
                details={"error": stderr[:500] if stderr else "Unknown error"},
                duration=duration
            )
    
    def validate_deployment_files(self) -> ValidationPhase:
        """Validate deployment configuration files."""
        print_step("Validating deployment configuration files...")
        
        start_time = datetime.datetime.now()
        
        required_files = {
            "Dockerfile": "Backend Docker configuration",
            "requirements.txt": "Python dependencies",
            "agent-frontend/package.json": "Frontend dependencies",
            "agent-frontend/vite.config.js": "Frontend build configuration",
            "agent-frontend/vercel.json": "Vercel deployment configuration"
        }
        
        missing_files = []
        invalid_files = []
        valid_files = []
        
        for file_path, description in required_files.items():
            if not Path(file_path).exists():
                missing_files.append(f"{file_path} ({description})")
            else:
                # Basic validation for specific files
                try:
                    if file_path.endswith('.json'):
                        with open(file_path, 'r') as f:
                            json.load(f)  # Validate JSON syntax
                    valid_files.append(file_path)
                except json.JSONDecodeError:
                    invalid_files.append(f"{file_path} (Invalid JSON)")
                except Exception:
                    invalid_files.append(f"{file_path} (Read error)")
        
        duration = (datetime.datetime.now() - start_time).total_seconds()
        
        if not missing_files and not invalid_files:
            return ValidationPhase(
                name="Deployment Files",
                status=True,
                message="All deployment configuration files are valid",
                details={
                    "total_files": len(required_files),
                    "valid_files": len(valid_files),
                    "missing": 0,
                    "invalid": 0
                },
                duration=duration
            )
        else:
            return ValidationPhase(
                name="Deployment Files",
                status=False,
                message=f"{len(missing_files + invalid_files)} deployment files have issues",
                details={
                    "total_files": len(required_files),
                    "valid_files": len(valid_files),
                    "missing": len(missing_files),
                    "invalid": len(invalid_files),
                    "missing_files": missing_files,
                    "invalid_files": invalid_files
                },
                duration=duration
            )
    
    def validate_network_connectivity(self) -> ValidationPhase:
        """Validate network connectivity to deployment platforms."""
        print_step("Validating network connectivity...")
        
        start_time = datetime.datetime.now()
        
        success, stdout, stderr = self.run_subprocess_validation("test_network_connectivity.py")
        duration = (datetime.datetime.now() - start_time).total_seconds()
        
        if success:
            return ValidationPhase(
                name="Network Connectivity",
                status=True,
                message="Network connectivity validated",
                details={"output": stdout[:500] if stdout else ""},
                duration=duration,
                critical=False  # Non-critical for pre-deployment
            )
        else:
            return ValidationPhase(
                name="Network Connectivity",
                status=False,
                message="Network connectivity issues detected",
                details={"error": stderr[:500] if stderr else "Unknown error"},
                duration=duration,
                critical=False  # Non-critical for pre-deployment
            )
    
    def run_all_validations(self) -> DeploymentReport:
        """Run all validation phases and generate report."""
        print_header("RAG AI-Agent Master Deployment Validation", 1)
        print_info(f"Starting comprehensive deployment validation at {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Define validation phases
        validation_functions = [
            self.validate_environment,
            self.validate_api_keys,
            self.validate_pinecone_setup,
            self.validate_deployment_files,
            self.validate_network_connectivity
        ]
        
        phases = []
        critical_failures = 0
        total_duration = 0
        
        # Run each validation phase
        for i, validation_func in enumerate(validation_functions, 1):
            print_header(f"Phase {i}/{len(validation_functions)}: {validation_func.__name__.replace('validate_', '').replace('_', ' ').title()}", 2)
            
            phase = validation_func()
            phases.append(phase)
            total_duration += phase.duration
            
            if phase.status:
                print_success(f"{phase.name}: {phase.message}")
                if self.verbose and phase.details:
                    for key, value in phase.details.items():
                        if isinstance(value, dict):
                            print_info(f"  {key}:")
                            for sub_key, sub_value in value.items():
                                print_info(f"    {sub_key}: {sub_value}")
                        else:
                            print_info(f"  {key}: {value}")
            else:
                print_error(f"{phase.name}: {phase.message}")
                if phase.critical:
                    critical_failures += 1
                
                if phase.details:
                    for key, value in phase.details.items():
                        if isinstance(value, (list, dict)) and len(str(value)) > 100:
                            print_info(f"  {key}: [Details available in report]")
                        else:
                            print_info(f"  {key}: {value}")
            
            print_info(f"Phase completed in {phase.duration:.2f} seconds")
        
        # Generate overall assessment
        overall_status = critical_failures == 0
        
        # Create summary
        summary = {
            "total_phases": len(phases),
            "passed_phases": len([p for p in phases if p.status]),
            "failed_phases": len([p for p in phases if not p.status]),
            "critical_failures": critical_failures,
            "total_duration": total_duration,
            "deployment_ready": overall_status
        }
        
        # Generate recommendations
        recommendations = self.generate_recommendations(phases)
        
        # Generate next steps
        next_steps = self.generate_next_steps(phases, overall_status)
        
        # Create report
        report = DeploymentReport(
            timestamp=datetime.datetime.now().isoformat(),
            overall_status=overall_status,
            phases=phases,
            summary=summary,
            recommendations=recommendations,
            next_steps=next_steps
        )
        
        return report
    
    def generate_recommendations(self, phases: List[ValidationPhase]) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        for phase in phases:
            if not phase.status:
                if phase.name == "Environment Setup":
                    recommendations.append("Install missing dependencies: pip install -r requirements.txt")
                    recommendations.append("Ensure Node.js 16+ is installed for frontend development")
                elif phase.name == "API Connectivity":
                    recommendations.append("Verify API keys are correct and have proper permissions")
                    recommendations.append("Check network connectivity to API services")
                elif phase.name == "Pinecone Setup":
                    recommendations.append("Create Pinecone index with correct dimensions (1536)")
                    recommendations.append("Verify Pinecone API key and index name configuration")
                elif phase.name == "Deployment Files":
                    recommendations.append("Ensure all required deployment files are present and valid")
                    recommendations.append("Update vercel.json with correct backend URL for production")
                elif phase.name == "Network Connectivity":
                    recommendations.append("Check internet connection and firewall settings")
        
        # General recommendations
        if any(not p.status for p in phases):
            recommendations.append("Review DEPLOYMENT_GUIDE.md for detailed setup instructions")
            recommendations.append("Check TROUBLESHOOTING_GUIDE.md for common issues and solutions")
        
        return recommendations
    
    def generate_next_steps(self, phases: List[ValidationPhase], overall_status: bool) -> List[str]:
        """Generate next steps based on validation results."""
        if overall_status:
            return [
                "🎉 All critical validations passed! You're ready to deploy.",
                "1. Deploy backend to Hugging Face Spaces using scripts/deploy_backend.py",
                "2. Update agent-frontend/vercel.json with your backend URL",
                "3. Deploy frontend to Vercel using scripts/deploy_frontend.py",
                "4. Run post-deployment tests using scripts/run_post_deployment_tests.py",
                "5. Monitor deployment status and check application functionality"
            ]
        else:
            failed_critical = [p for p in phases if not p.status and p.critical]
            return [
                f"❌ {len(failed_critical)} critical validation(s) failed. Deployment blocked.",
                "1. Address all critical failures listed above",
                "2. Re-run this validation script to verify fixes",
                "3. Once all validations pass, proceed with deployment",
                "4. Consult DEPLOYMENT_GUIDE.md for detailed instructions",
                "5. Check TROUBLESHOOTING_GUIDE.md if you encounter issues"
            ]
    
    def print_final_report(self, report: DeploymentReport):
        """Print the final validation report."""
        print_header("DEPLOYMENT VALIDATION REPORT", 1)
        
        # Overall status
        if report.overall_status:
            print_success("🎉 DEPLOYMENT READY! All critical validations passed.")
        else:
            print_error("❌ DEPLOYMENT BLOCKED! Critical validations failed.")
        
        # Summary statistics
        print_header("Summary", 3)
        print_info(f"Validation completed at: {report.timestamp}")
        print_info(f"Total phases: {report.summary['total_phases']}")
        print_info(f"Passed phases: {report.summary['passed_phases']}")
        print_info(f"Failed phases: {report.summary['failed_phases']}")
        print_info(f"Critical failures: {report.summary['critical_failures']}")
        print_info(f"Total duration: {report.summary['total_duration']:.2f} seconds")
        
        # Phase details
        print_header("Phase Results", 3)
        for phase in report.phases:
            status_icon = "✓" if phase.status else "✗"
            critical_marker = " (CRITICAL)" if not phase.status and phase.critical else ""
            print(f"{status_icon} {phase.name}: {phase.message}{critical_marker}")
            print_info(f"  Duration: {phase.duration:.2f}s")
        
        # Recommendations
        if report.recommendations:
            print_header("Recommendations", 3)
            for i, rec in enumerate(report.recommendations, 1):
                print_info(f"{i}. {rec}")
        
        # Next steps
        print_header("Next Steps", 3)
        for step in report.next_steps:
            if step.startswith(('🎉', '❌')):
                if step.startswith('🎉'):
                    print_success(step)
                else:
                    print_error(step)
            else:
                print_info(step)
        
        # Additional resources
        print_header("Additional Resources", 3)
        print_info("📚 Documentation:")
        print_info("  - DEPLOYMENT_GUIDE.md - Complete deployment instructions")
        print_info("  - DEPLOYMENT_CHECKLIST.md - Step-by-step checklist")
        print_info("  - TROUBLESHOOTING_GUIDE.md - Common issues and solutions")
        print_info("  - ENVIRONMENT_VARIABLES.md - Environment configuration")
        
        print_info("\n🔧 Validation Scripts:")
        print_info("  - scripts/validate_api_keys.py - Test API connectivity")
        print_info("  - scripts/validate_environment.py - Check local setup")
        print_info("  - scripts/run_post_deployment_tests.py - Test deployed app")
    
    def save_report(self, report: DeploymentReport, output_path: str):
        """Save the validation report to a JSON file."""
        try:
            # Convert dataclasses to dictionaries
            report_dict = asdict(report)
            
            with open(output_path, 'w') as f:
                json.dump(report_dict, f, indent=2, default=str)
            
            print_success(f"Validation report saved to: {output_path}")
        except Exception as e:
            print_error(f"Failed to save report: {e}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Master deployment validation for RAG AI-Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/master_deployment_validator.py
  python scripts/master_deployment_validator.py --config config.json
  python scripts/master_deployment_validator.py --generate-report --output validation_report.json
  python scripts/master_deployment_validator.py --verbose
        """
    )
    
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration JSON file with API keys"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed validation information"
    )
    
    parser.add_argument(
        "--generate-report",
        action="store_true",
        help="Generate and save a detailed JSON report"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="deployment_validation_report.json",
        help="Output file for JSON report (default: deployment_validation_report.json)"
    )
    
    args = parser.parse_args()
    
    # Create validator
    validator = MasterDeploymentValidator(
        config_path=args.config,
        verbose=args.verbose
    )
    
    # Run validations
    try:
        report = validator.run_all_validations()
        
        # Print report
        validator.print_final_report(report)
        
        # Save report if requested
        if args.generate_report:
            validator.save_report(report, args.output)
        
        # Exit with appropriate code
        return 0 if report.overall_status else 1
        
    except KeyboardInterrupt:
        print_error("\nValidation interrupted by user")
        return 1
    except Exception as e:
        print_error(f"Validation failed with error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())