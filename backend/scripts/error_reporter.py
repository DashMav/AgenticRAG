#!/usr/bin/env python3
"""
Error reporting and logging utility for RAG AI-Agent.

This script provides comprehensive error reporting, logging, and debugging
capabilities for the RAG AI-Agent application. It can collect logs,
generate error reports, and help with troubleshooting.

Usage:
    python scripts/error_reporter.py [--collect-logs] [--generate-report] [--debug-mode]

Requirements:
    - Python standard library
    - Access to application logs (if available)
"""

import os
import sys
import json
import time
import logging
import traceback
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess
import platform

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

class ErrorReporter:
    """Comprehensive error reporting and logging utility."""
    
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.report_data = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {},
            "environment": {},
            "logs": {},
            "errors": [],
            "diagnostics": {},
            "recommendations": []
        }
        
        # Setup logging
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration."""
        log_level = logging.DEBUG if self.debug_mode else logging.INFO
        
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f"logs/error_reporter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message with color coding."""
        if level == "SUCCESS":
            print(f"{Colors.GREEN}✅ {message}{Colors.END}")
            self.logger.info(message)
        elif level == "ERROR":
            print(f"{Colors.RED}❌ {message}{Colors.END}")
            self.logger.error(message)
        elif level == "WARNING":
            print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")
            self.logger.warning(message)
        elif level == "INFO":
            print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")
            self.logger.info(message)
        elif level == "DEBUG":
            if self.debug_mode:
                print(f"{Colors.PURPLE}🔍 {message}{Colors.END}")
            self.logger.debug(message)
        else:
            print(message)
            self.logger.info(message)
    
    def collect_system_info(self):
        """Collect system information."""
        self.log("Collecting system information...", "INFO")
        
        try:
            self.report_data["system_info"] = {
                "platform": platform.platform(),
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "python_implementation": platform.python_implementation(),
                "hostname": platform.node(),
                "current_directory": os.getcwd(),
                "user": os.getenv("USER") or os.getenv("USERNAME") or "unknown",
                "timestamp": datetime.now().isoformat()
            }
            
            # Add disk space information
            try:
                import shutil
                total, used, free = shutil.disk_usage(".")
                self.report_data["system_info"]["disk_space"] = {
                    "total_gb": round(total / (1024**3), 2),
                    "used_gb": round(used / (1024**3), 2),
                    "free_gb": round(free / (1024**3), 2),
                    "usage_percent": round((used / total) * 100, 2)
                }
            except Exception as e:
                self.log(f"Could not collect disk space info: {str(e)}", "WARNING")
            
            # Add memory information (if psutil is available)
            try:
                import psutil
                memory = psutil.virtual_memory()
                self.report_data["system_info"]["memory"] = {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_percent": memory.percent,
                    "free_gb": round((memory.total - memory.used) / (1024**3), 2)
                }
            except ImportError:
                self.log("psutil not available, skipping memory info", "DEBUG")
            except Exception as e:
                self.log(f"Could not collect memory info: {str(e)}", "WARNING")
            
            self.log("System information collected", "SUCCESS")
            
        except Exception as e:
            self.log(f"Error collecting system info: {str(e)}", "ERROR")
            self.report_data["errors"].append({
                "type": "system_info_error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    def collect_environment_info(self):
        """Collect environment variables and configuration."""
        self.log("Collecting environment information...", "INFO")
        
        try:
            # Collect relevant environment variables (mask sensitive ones)
            relevant_vars = [
                'GROQ_API_KEY', 'OPENAI_API_KEY', 'PINECONE_API_KEY', 'PINECONE_INDEX_NAME',
                'PINECONE_ENVIRONMENT', 'MAX_FILE_SIZE', 'EMBEDDING_MODEL',
                'PATH', 'PYTHONPATH', 'HOME', 'USER', 'USERNAME',
                'NODE_ENV', 'VITE_API_URL'
            ]
            
            env_info = {}
            for var in relevant_vars:
                value = os.getenv(var)
                if value:
                    # Mask API keys
                    if 'API_KEY' in var and len(value) > 12:
                        env_info[var] = f"{value[:8]}...{value[-4:]}"
                    else:
                        env_info[var] = value
                else:
                    env_info[var] = None
            
            self.report_data["environment"] = {
                "variables": env_info,
                "python_path": sys.path,
                "working_directory": os.getcwd(),
                "environment_files": self.check_environment_files()
            }
            
            self.log("Environment information collected", "SUCCESS")
            
        except Exception as e:
            self.log(f"Error collecting environment info: {str(e)}", "ERROR")
            self.report_data["errors"].append({
                "type": "environment_info_error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    def check_environment_files(self) -> Dict[str, bool]:
        """Check for environment configuration files."""
        env_files = {
            ".env": os.path.exists(".env"),
            "agent-frontend/.env": os.path.exists("agent-frontend/.env"),
            ".env.local": os.path.exists(".env.local"),
            ".env.production": os.path.exists(".env.production"),
            "agent-frontend/vercel.json": os.path.exists("agent-frontend/vercel.json"),
            "requirements.txt": os.path.exists("requirements.txt"),
            "agent-frontend/package.json": os.path.exists("agent-frontend/package.json")
        }
        
        return env_files
    
    def collect_application_logs(self):
        """Collect application logs from various sources."""
        self.log("Collecting application logs...", "INFO")
        
        log_sources = [
            "logs/",
            "agent-frontend/logs/",
            "/var/log/",
            "~/.pm2/logs/",
            "~/.vercel/",
            "~/.cache/huggingface/"
        ]
        
        collected_logs = {}
        
        for source in log_sources:
            try:
                source_path = Path(source).expanduser()
                if source_path.exists() and source_path.is_dir():
                    log_files = list(source_path.glob("*.log"))
                    for log_file in log_files[:5]:  # Limit to 5 most recent
                        try:
                            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                                # Read last 100 lines
                                lines = f.readlines()
                                recent_lines = lines[-100:] if len(lines) > 100 else lines
                                collected_logs[str(log_file)] = {
                                    "content": "".join(recent_lines),
                                    "size": log_file.stat().st_size,
                                    "modified": datetime.fromtimestamp(log_file.stat().st_mtime).isoformat()
                                }
                        except Exception as e:
                            self.log(f"Could not read log file {log_file}: {str(e)}", "WARNING")
            except Exception as e:
                self.log(f"Could not access log source {source}: {str(e)}", "DEBUG")
        
        self.report_data["logs"] = collected_logs
        self.log(f"Collected {len(collected_logs)} log files", "SUCCESS")
    
    def collect_recent_errors(self):
        """Collect recent errors from logs and system."""
        self.log("Analyzing recent errors...", "INFO")
        
        error_patterns = [
            "ERROR", "CRITICAL", "FATAL", "Exception", "Traceback",
            "Failed", "Error:", "ConnectionError", "TimeoutError",
            "ModuleNotFoundError", "ImportError", "KeyError"
        ]
        
        recent_errors = []
        
        # Analyze collected logs for errors
        for log_file, log_data in self.report_data["logs"].items():
            content = log_data["content"]
            lines = content.split('\n')
            
            for i, line in enumerate(lines):
                for pattern in error_patterns:
                    if pattern.lower() in line.lower():
                        error_context = {
                            "file": log_file,
                            "line_number": i + 1,
                            "content": line.strip(),
                            "context": lines[max(0, i-2):i+3],  # 2 lines before and after
                            "pattern": pattern,
                            "timestamp": self.extract_timestamp_from_line(line)
                        }
                        recent_errors.append(error_context)
                        break
        
        # Limit to most recent 50 errors
        recent_errors = sorted(recent_errors, key=lambda x: x.get("timestamp", ""), reverse=True)[:50]
        
        self.report_data["errors"].extend(recent_errors)
        self.log(f"Found {len(recent_errors)} recent errors", "SUCCESS" if len(recent_errors) == 0 else "WARNING")
    
    def extract_timestamp_from_line(self, line: str) -> str:
        """Extract timestamp from a log line."""
        import re
        
        # Common timestamp patterns
        patterns = [
            r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}',
            r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}',
            r'\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                return match.group()
        
        return datetime.now().isoformat()
    
    def run_diagnostics(self):
        """Run diagnostic checks."""
        self.log("Running diagnostic checks...", "INFO")
        
        diagnostics = {}
        
        # Check if validation script exists and run it
        if os.path.exists("validate_deployment.py"):
            try:
                result = subprocess.run(
                    [sys.executable, "validate_deployment.py"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                diagnostics["validation_script"] = {
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "success": result.returncode == 0
                }
            except subprocess.TimeoutExpired:
                diagnostics["validation_script"] = {
                    "error": "Validation script timed out",
                    "success": False
                }
            except Exception as e:
                diagnostics["validation_script"] = {
                    "error": str(e),
                    "success": False
                }
        
        # Check network connectivity
        try:
            import socket
            
            test_hosts = [
                ("api.groq.com", 443),
                ("api.openai.com", 443),
                ("api.pinecone.io", 443)
            ]
            
            connectivity = {}
            for host, port in test_hosts:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    result = sock.connect_ex((host, port))
                    sock.close()
                    connectivity[f"{host}:{port}"] = result == 0
                except Exception as e:
                    connectivity[f"{host}:{port}"] = False
            
            diagnostics["network_connectivity"] = connectivity
            
        except Exception as e:
            diagnostics["network_connectivity"] = {"error": str(e)}
        
        # Check Python packages
        try:
            import pkg_resources
            
            required_packages = [
                "fastapi", "uvicorn", "openai", "groq", "pinecone-client",
                "langchain", "python-dotenv", "requests"
            ]
            
            package_status = {}
            for package in required_packages:
                try:
                    version = pkg_resources.get_distribution(package).version
                    package_status[package] = {"installed": True, "version": version}
                except pkg_resources.DistributionNotFound:
                    package_status[package] = {"installed": False, "version": None}
            
            diagnostics["packages"] = package_status
            
        except Exception as e:
            diagnostics["packages"] = {"error": str(e)}
        
        self.report_data["diagnostics"] = diagnostics
        self.log("Diagnostic checks completed", "SUCCESS")
    
    def generate_recommendations(self):
        """Generate recommendations based on collected data."""
        self.log("Generating recommendations...", "INFO")
        
        recommendations = []
        
        # Check for missing environment variables
        env_vars = self.report_data["environment"]["variables"]
        required_vars = ["GROQ_API_KEY", "OPENAI_API_KEY", "PINECONE_API_KEY", "PINECONE_INDEX_NAME"]
        missing_vars = [var for var in required_vars if not env_vars.get(var)]
        
        if missing_vars:
            recommendations.append({
                "type": "environment",
                "priority": "high",
                "title": "Missing Required Environment Variables",
                "description": f"The following required environment variables are not set: {', '.join(missing_vars)}",
                "action": "Set these environment variables with valid API keys and configuration values."
            })
        
        # Check for package issues
        if "packages" in self.report_data["diagnostics"]:
            packages = self.report_data["diagnostics"]["packages"]
            if not isinstance(packages, dict) or "error" in packages:
                recommendations.append({
                    "type": "dependencies",
                    "priority": "high",
                    "title": "Package Installation Issues",
                    "description": "Could not verify Python package installations.",
                    "action": "Run 'pip install -r requirements.txt' to install required packages."
                })
            else:
                missing_packages = [pkg for pkg, info in packages.items() if not info.get("installed", False)]
                if missing_packages:
                    recommendations.append({
                        "type": "dependencies",
                        "priority": "high",
                        "title": "Missing Python Packages",
                        "description": f"Missing packages: {', '.join(missing_packages)}",
                        "action": f"Install missing packages: pip install {' '.join(missing_packages)}"
                    })
        
        # Check for network connectivity issues
        if "network_connectivity" in self.report_data["diagnostics"]:
            connectivity = self.report_data["diagnostics"]["network_connectivity"]
            if isinstance(connectivity, dict) and not connectivity.get("error"):
                failed_connections = [host for host, status in connectivity.items() if not status]
                if failed_connections:
                    recommendations.append({
                        "type": "network",
                        "priority": "medium",
                        "title": "Network Connectivity Issues",
                        "description": f"Cannot connect to: {', '.join(failed_connections)}",
                        "action": "Check your internet connection and firewall settings."
                    })
        
        # Check for recent errors
        if len(self.report_data["errors"]) > 10:
            recommendations.append({
                "type": "errors",
                "priority": "medium",
                "title": "High Error Rate",
                "description": f"Found {len(self.report_data['errors'])} recent errors in logs.",
                "action": "Review error logs and address recurring issues."
            })
        
        # Check disk space
        if "disk_space" in self.report_data["system_info"]:
            disk_info = self.report_data["system_info"]["disk_space"]
            if disk_info["free_gb"] < 1:
                recommendations.append({
                    "type": "system",
                    "priority": "high",
                    "title": "Low Disk Space",
                    "description": f"Only {disk_info['free_gb']}GB free disk space remaining.",
                    "action": "Free up disk space by removing unnecessary files."
                })
        
        # Check memory usage
        if "memory" in self.report_data["system_info"]:
            memory_info = self.report_data["system_info"]["memory"]
            if memory_info["used_percent"] > 90:
                recommendations.append({
                    "type": "system",
                    "priority": "medium",
                    "title": "High Memory Usage",
                    "description": f"Memory usage is at {memory_info['used_percent']}%.",
                    "action": "Close unnecessary applications or restart the system."
                })
        
        self.report_data["recommendations"] = recommendations
        self.log(f"Generated {len(recommendations)} recommendations", "SUCCESS")
    
    def generate_report(self, output_file: str = None) -> str:
        """Generate comprehensive error report."""
        self.log("Generating comprehensive error report...", "INFO")
        
        # Collect all information
        self.collect_system_info()
        self.collect_environment_info()
        self.collect_application_logs()
        self.collect_recent_errors()
        self.run_diagnostics()
        self.generate_recommendations()
        
        # Generate report filename if not provided
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"error_report_{timestamp}.json"
        
        # Save report
        try:
            with open(output_file, 'w') as f:
                json.dump(self.report_data, f, indent=2, default=str)
            
            self.log(f"Error report saved to: {output_file}", "SUCCESS")
            
            # Generate summary
            self.print_report_summary()
            
            return output_file
            
        except Exception as e:
            self.log(f"Error saving report: {str(e)}", "ERROR")
            return None
    
    def print_report_summary(self):
        """Print a summary of the error report."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}📊 Error Report Summary{Colors.END}")
        print(f"{Colors.BOLD}{'='*60}{Colors.END}")
        
        # System info summary
        system_info = self.report_data["system_info"]
        print(f"{Colors.BOLD}System:{Colors.END} {system_info.get('platform', 'Unknown')}")
        print(f"{Colors.BOLD}Python:{Colors.END} {system_info.get('python_version', 'Unknown')}")
        
        if "disk_space" in system_info:
            disk = system_info["disk_space"]
            print(f"{Colors.BOLD}Disk Space:{Colors.END} {disk['free_gb']}GB free ({disk['usage_percent']}% used)")
        
        if "memory" in system_info:
            memory = system_info["memory"]
            print(f"{Colors.BOLD}Memory:{Colors.END} {memory['available_gb']}GB available ({memory['used_percent']}% used)")
        
        # Environment summary
        env_vars = self.report_data["environment"]["variables"]
        required_vars = ["GROQ_API_KEY", "OPENAI_API_KEY", "PINECONE_API_KEY", "PINECONE_INDEX_NAME"]
        set_vars = sum(1 for var in required_vars if env_vars.get(var))
        print(f"{Colors.BOLD}Environment Variables:{Colors.END} {set_vars}/{len(required_vars)} required variables set")
        
        # Logs summary
        log_count = len(self.report_data["logs"])
        print(f"{Colors.BOLD}Log Files:{Colors.END} {log_count} files collected")
        
        # Errors summary
        error_count = len([e for e in self.report_data["errors"] if isinstance(e, dict) and "content" in e])
        print(f"{Colors.BOLD}Recent Errors:{Colors.END} {error_count} errors found")
        
        # Recommendations summary
        recommendations = self.report_data["recommendations"]
        high_priority = len([r for r in recommendations if r.get("priority") == "high"])
        medium_priority = len([r for r in recommendations if r.get("priority") == "medium"])
        
        print(f"{Colors.BOLD}Recommendations:{Colors.END} {high_priority} high priority, {medium_priority} medium priority")
        
        # Show high priority recommendations
        if high_priority > 0:
            print(f"\n{Colors.RED}{Colors.BOLD}High Priority Issues:{Colors.END}")
            for rec in recommendations:
                if rec.get("priority") == "high":
                    print(f"{Colors.RED}  ❌ {rec['title']}{Colors.END}")
                    print(f"     {rec['description']}")
                    print(f"     Action: {rec['action']}")
        
        print(f"\n{Colors.BOLD}Full report saved with detailed logs and diagnostics.{Colors.END}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="RAG AI-Agent Error Reporter")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug mode")
    parser.add_argument("--output", "-o", help="Output file for error report")
    parser.add_argument("--collect-logs", action="store_true", help="Only collect logs")
    parser.add_argument("--generate-report", action="store_true", help="Generate full error report")
    
    args = parser.parse_args()
    
    print(f"{Colors.BOLD}{Colors.BLUE}🚨 RAG AI-Agent Error Reporter{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")
    
    # Create error reporter
    reporter = ErrorReporter(debug_mode=args.debug)
    
    try:
        if args.collect_logs:
            reporter.collect_application_logs()
            print(f"\n{Colors.GREEN}✅ Logs collected successfully{Colors.END}")
        elif args.generate_report or not any([args.collect_logs]):
            # Generate full report by default
            report_file = reporter.generate_report(args.output)
            if report_file:
                print(f"\n{Colors.GREEN}✅ Error report generated: {report_file}{Colors.END}")
                sys.exit(0)
            else:
                print(f"\n{Colors.RED}❌ Failed to generate error report{Colors.END}")
                sys.exit(1)
    
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Error reporting interrupted by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Error reporting failed: {str(e)}{Colors.END}")
        if args.debug:
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()