#!/usr/bin/env python3
"""
Environment Setup Verification Script for RAG AI-Agent

This script validates the local development environment requirements including
Python dependencies, Node.js setup, and Docker availability.

Usage:
    python scripts/validate_environment.py
    python scripts/validate_environment.py --verbose

Requirements:
    - Python 3.8+
    - Node.js 16+
    - Docker (optional, for local testing)
"""

import os
import sys
import subprocess
import json
import argparse
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import importlib.util

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

@dataclass
class EnvironmentCheck:
    """Result of an environment check."""
    name: str
    status: bool
    message: str
    version: Optional[str] = None
    details: Optional[Dict] = None

def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text.center(60)}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}\n")

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

class EnvironmentValidator:
    """Validates local development environment."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def run_command(self, command: List[str]) -> Tuple[bool, str, str]:
        """Run a command and return success status, stdout, and stderr."""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except FileNotFoundError:
            return False, "", f"Command not found: {command[0]}"
        except Exception as e:
            return False, "", str(e)
    
    def check_python_version(self) -> EnvironmentCheck:
        """Check Python version."""
        try:
            version = sys.version_info
            version_str = f"{version.major}.{version.minor}.{version.micro}"
            
            if version.major >= 3 and version.minor >= 8:
                return EnvironmentCheck(
                    name="Python",
                    status=True,
                    message="Version compatible",
                    version=version_str,
                    details={"required": "3.8+", "found": version_str}
                )
            else:
                return EnvironmentCheck(
                    name="Python",
                    status=False,
                    message="Version too old",
                    version=version_str,
                    details={"required": "3.8+", "found": version_str}
                )
        except Exception as e:
            return EnvironmentCheck(
                name="Python",
                status=False,
                message=f"Error checking version: {e}"
            )
    
    def check_pip(self) -> EnvironmentCheck:
        """Check pip availability."""
        success, stdout, stderr = self.run_command([sys.executable, "-m", "pip", "--version"])
        
        if success:
            version = stdout.split()[1] if stdout else "unknown"
            return EnvironmentCheck(
                name="pip",
                status=True,
                message="Available",
                version=version
            )
        else:
            return EnvironmentCheck(
                name="pip",
                status=False,
                message="Not available or not working",
                details={"error": stderr}
            )
    
    def check_python_dependencies(self) -> EnvironmentCheck:
        """Check Python dependencies from requirements.txt."""
        requirements_file = Path("requirements.txt")
        
        if not requirements_file.exists():
            return EnvironmentCheck(
                name="Python Dependencies",
                status=False,
                message="requirements.txt not found"
            )
        
        try:
            with open(requirements_file, 'r') as f:
                requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            missing_packages = []
            installed_packages = []
            
            for requirement in requirements:
                # Parse package name (handle version specifiers)
                package_name = requirement.split('==')[0].split('>=')[0].split('<=')[0].split('>')[0].split('<')[0].split('~=')[0]
                package_name = package_name.replace('-', '_')  # Handle package name variations
                
                try:
                    spec = importlib.util.find_spec(package_name)
                    if spec is not None:
                        installed_packages.append(requirement)
                    else:
                        missing_packages.append(requirement)
                except (ImportError, ModuleNotFoundError):
                    missing_packages.append(requirement)
            
            if not missing_packages:
                return EnvironmentCheck(
                    name="Python Dependencies",
                    status=True,
                    message=f"All {len(installed_packages)} packages installed",
                    details={
                        "total_packages": len(requirements),
                        "installed": len(installed_packages),
                        "missing": 0
                    }
                )
            else:
                return EnvironmentCheck(
                    name="Python Dependencies",
                    status=False,
                    message=f"{len(missing_packages)} packages missing",
                    details={
                        "total_packages": len(requirements),
                        "installed": len(installed_packages),
                        "missing": len(missing_packages),
                        "missing_packages": missing_packages[:5]  # Show first 5
                    }
                )
                
        except Exception as e:
            return EnvironmentCheck(
                name="Python Dependencies",
                status=False,
                message=f"Error checking dependencies: {e}"
            )
    
    def check_nodejs(self) -> EnvironmentCheck:
        """Check Node.js installation."""
        success, stdout, stderr = self.run_command(["node", "--version"])
        
        if success:
            version_str = stdout.replace('v', '')
            try:
                major_version = int(version_str.split('.')[0])
                if major_version >= 16:
                    return EnvironmentCheck(
                        name="Node.js",
                        status=True,
                        message="Version compatible",
                        version=version_str,
                        details={"required": "16+", "found": version_str}
                    )
                else:
                    return EnvironmentCheck(
                        name="Node.js",
                        status=False,
                        message="Version too old",
                        version=version_str,
                        details={"required": "16+", "found": version_str}
                    )
            except (ValueError, IndexError):
                return EnvironmentCheck(
                    name="Node.js",
                    status=False,
                    message="Could not parse version",
                    version=version_str
                )
        else:
            return EnvironmentCheck(
                name="Node.js",
                status=False,
                message="Not installed or not in PATH",
                details={"error": stderr}
            )
    
    def check_npm(self) -> EnvironmentCheck:
        """Check npm availability."""
        success, stdout, stderr = self.run_command(["npm", "--version"])
        
        if success:
            return EnvironmentCheck(
                name="npm",
                status=True,
                message="Available",
                version=stdout
            )
        else:
            return EnvironmentCheck(
                name="npm",
                status=False,
                message="Not available",
                details={"error": stderr}
            )
    
    def check_frontend_dependencies(self) -> EnvironmentCheck:
        """Check frontend dependencies."""
        package_json_path = Path("agent-frontend/package.json")
        
        if not package_json_path.exists():
            return EnvironmentCheck(
                name="Frontend Dependencies",
                status=False,
                message="package.json not found in agent-frontend/"
            )
        
        node_modules_path = Path("agent-frontend/node_modules")
        
        if not node_modules_path.exists():
            return EnvironmentCheck(
                name="Frontend Dependencies",
                status=False,
                message="node_modules not found. Run 'npm install' in agent-frontend/",
                details={"action": "cd agent-frontend && npm install"}
            )
        
        try:
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
            
            dependencies = package_data.get('dependencies', {})
            dev_dependencies = package_data.get('devDependencies', {})
            total_deps = len(dependencies) + len(dev_dependencies)
            
            return EnvironmentCheck(
                name="Frontend Dependencies",
                status=True,
                message=f"node_modules exists with {total_deps} declared dependencies",
                details={
                    "dependencies": len(dependencies),
                    "devDependencies": len(dev_dependencies),
                    "total": total_deps
                }
            )
            
        except json.JSONDecodeError:
            return EnvironmentCheck(
                name="Frontend Dependencies",
                status=False,
                message="Invalid package.json format"
            )
        except Exception as e:
            return EnvironmentCheck(
                name="Frontend Dependencies",
                status=False,
                message=f"Error checking dependencies: {e}"
            )
    
    def check_docker(self) -> EnvironmentCheck:
        """Check Docker availability (optional)."""
        success, stdout, stderr = self.run_command(["docker", "--version"])
        
        if success:
            version_line = stdout.split('\n')[0] if stdout else ""
            return EnvironmentCheck(
                name="Docker",
                status=True,
                message="Available (optional for local testing)",
                version=version_line,
                details={"optional": True}
            )
        else:
            return EnvironmentCheck(
                name="Docker",
                status=False,
                message="Not available (optional for local testing)",
                details={"optional": True, "error": stderr}
            )
    
    def check_git(self) -> EnvironmentCheck:
        """Check Git availability."""
        success, stdout, stderr = self.run_command(["git", "--version"])
        
        if success:
            version_line = stdout.split('\n')[0] if stdout else ""
            return EnvironmentCheck(
                name="Git",
                status=True,
                message="Available",
                version=version_line
            )
        else:
            return EnvironmentCheck(
                name="Git",
                status=False,
                message="Not available",
                details={"error": stderr}
            )
    
    def check_file_structure(self) -> EnvironmentCheck:
        """Check required file structure."""
        required_files = [
            "app.py",
            "agent.py",
            "requirements.txt",
            "Dockerfile",
            "agent-frontend/package.json",
            "agent-frontend/vite.config.js"
        ]
        
        missing_files = []
        existing_files = []
        
        for file_path in required_files:
            if Path(file_path).exists():
                existing_files.append(file_path)
            else:
                missing_files.append(file_path)
        
        if not missing_files:
            return EnvironmentCheck(
                name="File Structure",
                status=True,
                message="All required files present",
                details={
                    "total_files": len(required_files),
                    "existing": len(existing_files),
                    "missing": 0
                }
            )
        else:
            return EnvironmentCheck(
                name="File Structure",
                status=False,
                message=f"{len(missing_files)} required files missing",
                details={
                    "total_files": len(required_files),
                    "existing": len(existing_files),
                    "missing": len(missing_files),
                    "missing_files": missing_files
                }
            )
    
    def validate_all(self) -> Dict[str, EnvironmentCheck]:
        """Validate all environment requirements."""
        results = {}
        
        print_header("ENVIRONMENT VALIDATION")
        
        # Define checks
        checks = [
            ("python_version", self.check_python_version),
            ("pip", self.check_pip),
            ("python_deps", self.check_python_dependencies),
            ("nodejs", self.check_nodejs),
            ("npm", self.check_npm),
            ("frontend_deps", self.check_frontend_dependencies),
            ("docker", self.check_docker),
            ("git", self.check_git),
            ("file_structure", self.check_file_structure)
        ]
        
        for check_key, check_func in checks:
            result = check_func()
            results[check_key] = result
            
            if result.status:
                version_info = f" (v{result.version})" if result.version else ""
                print_success(f"{result.name}: {result.message}{version_info}")
                
                if self.verbose and result.details:
                    for key, value in result.details.items():
                        if key != "optional":
                            print_info(f"  {key}: {value}")
            else:
                print_error(f"{result.name}: {result.message}")
                
                if result.details:
                    if result.details.get("optional"):
                        print_info("  (This is optional and won't prevent deployment)")
                    
                    if "missing_packages" in result.details:
                        packages = result.details["missing_packages"]
                        print_info(f"  Missing packages: {', '.join(packages)}")
                        print_info("  Run: pip install -r requirements.txt")
                    
                    if "missing_files" in result.details:
                        files = result.details["missing_files"]
                        print_info(f"  Missing files: {', '.join(files)}")
                    
                    if "action" in result.details:
                        print_info(f"  Action: {result.details['action']}")
        
        return results

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Validate environment setup for RAG AI-Agent")
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Show detailed information about checks"
    )
    
    args = parser.parse_args()
    
    print(f"{Colors.BOLD}RAG AI-Agent Environment Validation{Colors.END}")
    print("This script validates your local development environment.\n")
    
    # Validate environment
    validator = EnvironmentValidator(verbose=args.verbose)
    results = validator.validate_all()
    
    # Summary
    print_header("VALIDATION SUMMARY")
    
    required_checks = [k for k, v in results.items() if not v.details or not v.details.get("optional")]
    optional_checks = [k for k, v in results.items() if v.details and v.details.get("optional")]
    
    successful_required = [k for k in required_checks if results[k].status]
    failed_required = [k for k in required_checks if not results[k].status]
    
    successful_optional = [k for k in optional_checks if results[k].status]
    failed_optional = [k for k in optional_checks if not results[k].status]
    
    if len(failed_required) == 0:
        print_success("All required environment checks passed! ✨")
        print_info("Your development environment is ready for deployment.")
        
        if failed_optional:
            print_warning(f"Optional checks failed: {len(failed_optional)}")
            for check_key in failed_optional:
                result = results[check_key]
                print_info(f"  {result.name}: {result.message}")
    else:
        print_error(f"{len(failed_required)} required checks failed! ❌")
        print_error("Please address these issues before proceeding:")
        
        for check_key in failed_required:
            result = results[check_key]
            print_error(f"  {result.name}: {result.message}")
    
    print_info(f"\nSummary:")
    print_info(f"  Required checks: {len(successful_required)}/{len(required_checks)} passed")
    print_info(f"  Optional checks: {len(successful_optional)}/{len(optional_checks)} passed")
    
    print_info("\nFor detailed setup instructions, see:")
    print_info("- README.md")
    print_info("- DEPLOYMENT_GUIDE.md")
    
    return 0 if len(failed_required) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())