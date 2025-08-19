#!/usr/bin/env python3
"""
Comprehensive diagnostic script for RAG AI-Agent deployment issues.

This script performs detailed diagnostics of the RAG AI-Agent application,
including environment validation, API connectivity testing, and performance analysis.

Usage:
    python scripts/diagnose_issues.py [--backend-url URL] [--verbose] [--output-file FILE]

Requirements:
    - All required Python packages installed
    - Environment variables configured (for API testing)
    - Internet connection for external service testing
"""

import os
import sys
import json
import time
import argparse
import requests
import traceback
from datetime import datetime
from typing import Dict, List, Tuple, Optional
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

class DiagnosticResult:
    """Container for diagnostic test results."""
    
    def __init__(self, test_name: str, passed: bool, message: str, details: Optional[Dict] = None):
        self.test_name = test_name
        self.passed = passed
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()

class DiagnosticRunner:
    """Main diagnostic runner class."""
    
    def __init__(self, verbose: bool = False, backend_url: Optional[str] = None):
        self.verbose = verbose
        self.backend_url = backend_url
        self.results: List[DiagnosticResult] = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if level == "ERROR":
            print(f"{Colors.RED}[{timestamp}] ERROR: {message}{Colors.END}")
        elif level == "WARNING":
            print(f"{Colors.YELLOW}[{timestamp}] WARNING: {message}{Colors.END}")
        elif level == "SUCCESS":
            print(f"{Colors.GREEN}[{timestamp}] SUCCESS: {message}{Colors.END}")
        elif level == "INFO":
            print(f"{Colors.BLUE}[{timestamp}] INFO: {message}{Colors.END}")
        else:
            print(f"[{timestamp}] {message}")
    
    def add_result(self, result: DiagnosticResult):
        """Add a diagnostic result."""
        self.results.append(result)
        
        if result.passed:
            self.log(f"✅ {result.test_name}: {result.message}", "SUCCESS")
        else:
            self.log(f"❌ {result.test_name}: {result.message}", "ERROR")
            
        if self.verbose and result.details:
            for key, value in result.details.items():
                self.log(f"   {key}: {value}")
    
    def run_all_diagnostics(self) -> Dict:
        """Run all diagnostic tests."""
        self.log("🚀 Starting comprehensive diagnostics...", "INFO")
        
        # Environment diagnostics
        self.diagnose_environment()
        
        # File structure diagnostics
        self.diagnose_file_structure()
        
        # Dependencies diagnostics
        self.diagnose_dependencies()
        
        # API services diagnostics
        self.diagnose_api_services()
        
        # Backend diagnostics (if URL provided)
        if self.backend_url:
            self.diagnose_backend()
        
        # Network diagnostics
        self.diagnose_network_connectivity()
        
        # Performance diagnostics
        self.diagnose_performance()
        
        # Generate summary
        return self.generate_summary()
    
    def diagnose_environment(self):
        """Diagnose environment variables."""
        self.log("🔍 Checking environment variables...", "INFO")
        
        required_vars = [
            'GROQ_API_KEY',
            'OPENAI_API_KEY',
            'PINECONE_API_KEY',
            'PINECONE_INDEX_NAME'
        ]
        
        optional_vars = [
            'PINECONE_ENVIRONMENT',
            'MAX_FILE_SIZE',
            'EMBEDDING_MODEL'
        ]
        
        # Check required variables
        missing_required = []
        for var in required_vars:
            value = os.getenv(var)
            if value:
                # Mask sensitive values
                masked_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
                self.add_result(DiagnosticResult(
                    f"Environment Variable: {var}",
                    True,
                    f"Set ({masked_value})",
                    {"length": len(value)}
                ))
            else:
                missing_required.append(var)
                self.add_result(DiagnosticResult(
                    f"Environment Variable: {var}",
                    False,
                    "Not set",
                    {"required": True}
                ))
        
        # Check optional variables
        for var in optional_vars:
            value = os.getenv(var)
            self.add_result(DiagnosticResult(
                f"Optional Variable: {var}",
                True,
                f"Set: {value}" if value else "Not set (using default)",
                {"value": value, "required": False}
            ))
        
        # Overall environment check
        env_passed = len(missing_required) == 0
        self.add_result(DiagnosticResult(
            "Environment Configuration",
            env_passed,
            "All required variables set" if env_passed else f"Missing: {', '.join(missing_required)}",
            {"missing_count": len(missing_required), "missing_vars": missing_required}
        ))
    
    def diagnose_file_structure(self):
        """Diagnose project file structure."""
        self.log("🔍 Checking file structure...", "INFO")
        
        required_files = [
            'app.py',
            'agent.py',
            'requirements.txt',
            'Dockerfile',
            'agent-frontend/package.json',
            'agent-frontend/vite.config.js',
            'agent-frontend/vercel.json'
        ]
        
        missing_files = []
        for file_path in required_files:
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                self.add_result(DiagnosticResult(
                    f"File: {file_path}",
                    True,
                    f"Found ({file_size} bytes)",
                    {"size": file_size, "exists": True}
                ))
            else:
                missing_files.append(file_path)
                self.add_result(DiagnosticResult(
                    f"File: {file_path}",
                    False,
                    "Missing",
                    {"exists": False}
                ))
        
        # Check Vercel configuration
        self.diagnose_vercel_config()
        
        # Overall file structure check
        files_passed = len(missing_files) == 0
        self.add_result(DiagnosticResult(
            "File Structure",
            files_passed,
            "All required files present" if files_passed else f"Missing: {', '.join(missing_files)}",
            {"missing_count": len(missing_files), "missing_files": missing_files}
        ))
    
    def diagnose_vercel_config(self):
        """Diagnose Vercel configuration."""
        vercel_config_path = 'agent-frontend/vercel.json'
        
        if not os.path.exists(vercel_config_path):
            self.add_result(DiagnosticResult(
                "Vercel Configuration",
                False,
                "vercel.json not found",
                {"path": vercel_config_path}
            ))
            return
        
        try:
            with open(vercel_config_path, 'r') as f:
                config = json.load(f)
            
            if 'rewrites' in config and config['rewrites']:
                rewrite = config['rewrites'][0]
                destination = rewrite.get('destination', '')
                
                if 'hf.space' in destination:
                    self.add_result(DiagnosticResult(
                        "Vercel Configuration",
                        True,
                        "Configured for Hugging Face Spaces",
                        {"destination": destination, "source": rewrite.get('source')}
                    ))
                else:
                    self.add_result(DiagnosticResult(
                        "Vercel Configuration",
                        False,
                        "Backend URL may need updating",
                        {"destination": destination}
                    ))
            else:
                self.add_result(DiagnosticResult(
                    "Vercel Configuration",
                    False,
                    "No rewrites configured",
                    {"config": config}
                ))
                
        except json.JSONDecodeError as e:
            self.add_result(DiagnosticResult(
                "Vercel Configuration",
                False,
                f"Invalid JSON: {str(e)}",
                {"error": str(e)}
            ))
        except Exception as e:
            self.add_result(DiagnosticResult(
                "Vercel Configuration",
                False,
                f"Error reading config: {str(e)}",
                {"error": str(e)}
            ))
    
    def diagnose_dependencies(self):
        """Diagnose Python dependencies."""
        self.log("🔍 Checking dependencies...", "INFO")
        
        required_packages = [
            'fastapi',
            'uvicorn',
            'openai',
            'groq',
            'pinecone-client',
            'langchain',
            'python-dotenv',
            'requests'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                module_name = package.replace('-', '_')
                __import__(module_name)
                
                # Try to get version info
                try:
                    import importlib.metadata
                    version = importlib.metadata.version(package)
                    self.add_result(DiagnosticResult(
                        f"Package: {package}",
                        True,
                        f"Installed (v{version})",
                        {"version": version}
                    ))
                except:
                    self.add_result(DiagnosticResult(
                        f"Package: {package}",
                        True,
                        "Installed (version unknown)",
                        {"version": "unknown"}
                    ))
                    
            except ImportError:
                missing_packages.append(package)
                self.add_result(DiagnosticResult(
                    f"Package: {package}",
                    False,
                    "Not installed",
                    {"installed": False}
                ))
        
        # Overall dependencies check
        deps_passed = len(missing_packages) == 0
        self.add_result(DiagnosticResult(
            "Dependencies",
            deps_passed,
            "All packages installed" if deps_passed else f"Missing: {', '.join(missing_packages)}",
            {"missing_count": len(missing_packages), "missing_packages": missing_packages}
        ))
    
    def diagnose_api_services(self):
        """Diagnose external API services."""
        self.log("🔍 Testing API services...", "INFO")
        
        # Test each service
        groq_result = self.test_groq_api()
        openai_result = self.test_openai_api()
        pinecone_result = self.test_pinecone_api()
        
        # Overall API services check
        all_apis_working = groq_result and openai_result and pinecone_result
        failed_apis = []
        if not groq_result:
            failed_apis.append("Groq")
        if not openai_result:
            failed_apis.append("OpenAI")
        if not pinecone_result:
            failed_apis.append("Pinecone")
        
        self.add_result(DiagnosticResult(
            "API Services",
            all_apis_working,
            "All APIs working" if all_apis_working else f"Failed: {', '.join(failed_apis)}",
            {"failed_apis": failed_apis, "total_apis": 3}
        ))
    
    def test_groq_api(self) -> bool:
        """Test Groq API connectivity."""
        try:
            from groq import Groq
            
            api_key = os.getenv('GROQ_API_KEY')
            if not api_key:
                self.add_result(DiagnosticResult(
                    "Groq API",
                    False,
                    "API key not found",
                    {"error": "missing_api_key"}
                ))
                return False
            
            client = Groq(api_key=api_key)
            
            # Test with a simple completion
            start_time = time.time()
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama3-8b-8192",
                max_tokens=5
            )
            response_time = time.time() - start_time
            
            if response.choices:
                self.add_result(DiagnosticResult(
                    "Groq API",
                    True,
                    f"Working ({response_time:.2f}s)",
                    {
                        "response_time": response_time,
                        "model": "llama3-8b-8192",
                        "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else 'unknown'
                    }
                ))
                return True
            else:
                self.add_result(DiagnosticResult(
                    "Groq API",
                    False,
                    "No response received",
                    {"error": "empty_response"}
                ))
                return False
                
        except ImportError:
            self.add_result(DiagnosticResult(
                "Groq API",
                False,
                "groq package not installed",
                {"error": "missing_package"}
            ))
            return False
        except Exception as e:
            self.add_result(DiagnosticResult(
                "Groq API",
                False,
                f"Error: {str(e)}",
                {"error": str(e), "error_type": type(e).__name__}
            ))
            return False
    
    def test_openai_api(self) -> bool:
        """Test OpenAI API connectivity."""
        try:
            import openai
            
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                self.add_result(DiagnosticResult(
                    "OpenAI API",
                    False,
                    "API key not found",
                    {"error": "missing_api_key"}
                ))
                return False
            
            client = openai.OpenAI(api_key=api_key)
            
            # Test with a simple embedding request
            start_time = time.time()
            response = client.embeddings.create(
                input="test",
                model="text-embedding-ada-002"
            )
            response_time = time.time() - start_time
            
            if response.data:
                embedding_dim = len(response.data[0].embedding)
                self.add_result(DiagnosticResult(
                    "OpenAI API",
                    True,
                    f"Working ({response_time:.2f}s, dim: {embedding_dim})",
                    {
                        "response_time": response_time,
                        "embedding_dimension": embedding_dim,
                        "model": "text-embedding-ada-002",
                        "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else 'unknown'
                    }
                ))
                return True
            else:
                self.add_result(DiagnosticResult(
                    "OpenAI API",
                    False,
                    "No response received",
                    {"error": "empty_response"}
                ))
                return False
                
        except ImportError:
            self.add_result(DiagnosticResult(
                "OpenAI API",
                False,
                "openai package not installed",
                {"error": "missing_package"}
            ))
            return False
        except Exception as e:
            self.add_result(DiagnosticResult(
                "OpenAI API",
                False,
                f"Error: {str(e)}",
                {"error": str(e), "error_type": type(e).__name__}
            ))
            return False
    
    def test_pinecone_api(self) -> bool:
        """Test Pinecone API connectivity."""
        try:
            from pinecone import Pinecone
            
            api_key = os.getenv('PINECONE_API_KEY')
            index_name = os.getenv('PINECONE_INDEX_NAME')
            
            if not api_key:
                self.add_result(DiagnosticResult(
                    "Pinecone API",
                    False,
                    "API key not found",
                    {"error": "missing_api_key"}
                ))
                return False
            
            if not index_name:
                self.add_result(DiagnosticResult(
                    "Pinecone API",
                    False,
                    "Index name not found",
                    {"error": "missing_index_name"}
                ))
                return False
            
            pc = Pinecone(api_key=api_key)
            
            # List indexes to test connection
            start_time = time.time()
            indexes = pc.list_indexes()
            list_time = time.time() - start_time
            
            # Check if our index exists
            available_indexes = [idx.name for idx in indexes]
            index_exists = index_name in available_indexes
            
            if index_exists:
                # Test index operations
                index = pc.Index(index_name)
                stats = index.describe_index_stats()
                
                # Test query
                test_vector = [0.1] * 1536  # Test vector with correct dimensions
                query_start = time.time()
                results = index.query(vector=test_vector, top_k=1)
                query_time = time.time() - query_start
                
                self.add_result(DiagnosticResult(
                    "Pinecone API",
                    True,
                    f"Working (list: {list_time:.2f}s, query: {query_time:.2f}s)",
                    {
                        "index_name": index_name,
                        "vector_count": stats.total_vector_count,
                        "dimension": stats.dimension,
                        "list_time": list_time,
                        "query_time": query_time,
                        "available_indexes": available_indexes
                    }
                ))
                return True
            else:
                self.add_result(DiagnosticResult(
                    "Pinecone API",
                    False,
                    f"Index '{index_name}' not found",
                    {
                        "requested_index": index_name,
                        "available_indexes": available_indexes,
                        "error": "index_not_found"
                    }
                ))
                return False
                
        except ImportError:
            self.add_result(DiagnosticResult(
                "Pinecone API",
                False,
                "pinecone-client package not installed",
                {"error": "missing_package"}
            ))
            return False
        except Exception as e:
            self.add_result(DiagnosticResult(
                "Pinecone API",
                False,
                f"Error: {str(e)}",
                {"error": str(e), "error_type": type(e).__name__}
            ))
            return False
    
    def diagnose_backend(self):
        """Diagnose backend deployment."""
        if not self.backend_url:
            return
            
        self.log(f"🔍 Testing backend: {self.backend_url}", "INFO")
        
        # Test health endpoint
        try:
            start_time = time.time()
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                self.add_result(DiagnosticResult(
                    "Backend Health",
                    True,
                    f"Healthy ({response_time:.2f}s)",
                    {
                        "response_time": response_time,
                        "status_code": response.status_code,
                        "response": response.text
                    }
                ))
            else:
                self.add_result(DiagnosticResult(
                    "Backend Health",
                    False,
                    f"Unhealthy (HTTP {response.status_code})",
                    {
                        "status_code": response.status_code,
                        "response": response.text
                    }
                ))
                
        except requests.exceptions.Timeout:
            self.add_result(DiagnosticResult(
                "Backend Health",
                False,
                "Timeout (>10s)",
                {"error": "timeout"}
            ))
        except requests.exceptions.ConnectionError:
            self.add_result(DiagnosticResult(
                "Backend Health",
                False,
                "Connection failed",
                {"error": "connection_error"}
            ))
        except Exception as e:
            self.add_result(DiagnosticResult(
                "Backend Health",
                False,
                f"Error: {str(e)}",
                {"error": str(e)}
            ))
        
        # Test API documentation
        try:
            docs_response = requests.get(f"{self.backend_url}/docs", timeout=10)
            if docs_response.status_code == 200:
                self.add_result(DiagnosticResult(
                    "Backend Documentation",
                    True,
                    "API docs accessible",
                    {"status_code": docs_response.status_code}
                ))
            else:
                self.add_result(DiagnosticResult(
                    "Backend Documentation",
                    False,
                    f"API docs not accessible (HTTP {docs_response.status_code})",
                    {"status_code": docs_response.status_code}
                ))
        except Exception as e:
            self.add_result(DiagnosticResult(
                "Backend Documentation",
                False,
                f"Error accessing docs: {str(e)}",
                {"error": str(e)}
            ))
    
    def diagnose_network_connectivity(self):
        """Diagnose network connectivity to external services."""
        self.log("🔍 Testing network connectivity...", "INFO")
        
        services = [
            ("api.groq.com", 443),
            ("api.openai.com", 443),
            ("api.pinecone.io", 443),
            ("huggingface.co", 443),
            ("vercel.com", 443)
        ]
        
        for hostname, port in services:
            self.test_network_connectivity(hostname, port)
    
    def test_network_connectivity(self, hostname: str, port: int):
        """Test network connectivity to a specific host and port."""
        import socket
        
        try:
            # Test DNS resolution
            ip = socket.gethostbyname(hostname)
            
            # Test port connectivity
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((hostname, port))
            sock.close()
            
            if result == 0:
                self.add_result(DiagnosticResult(
                    f"Network: {hostname}:{port}",
                    True,
                    f"Reachable (IP: {ip})",
                    {"ip": ip, "port": port, "hostname": hostname}
                ))
            else:
                self.add_result(DiagnosticResult(
                    f"Network: {hostname}:{port}",
                    False,
                    f"Port closed (IP: {ip})",
                    {"ip": ip, "port": port, "hostname": hostname}
                ))
                
        except socket.gaierror as e:
            self.add_result(DiagnosticResult(
                f"Network: {hostname}:{port}",
                False,
                f"DNS resolution failed: {str(e)}",
                {"error": str(e), "hostname": hostname}
            ))
        except Exception as e:
            self.add_result(DiagnosticResult(
                f"Network: {hostname}:{port}",
                False,
                f"Connection error: {str(e)}",
                {"error": str(e), "hostname": hostname}
            ))
    
    def diagnose_performance(self):
        """Diagnose performance-related issues."""
        self.log("🔍 Running performance diagnostics...", "INFO")
        
        # Check disk space
        try:
            import shutil
            total, used, free = shutil.disk_usage(".")
            free_gb = free // (1024**3)
            
            self.add_result(DiagnosticResult(
                "Disk Space",
                free_gb > 1,  # At least 1GB free
                f"{free_gb}GB free",
                {
                    "total_gb": total // (1024**3),
                    "used_gb": used // (1024**3),
                    "free_gb": free_gb
                }
            ))
        except Exception as e:
            self.add_result(DiagnosticResult(
                "Disk Space",
                False,
                f"Error checking disk space: {str(e)}",
                {"error": str(e)}
            ))
        
        # Check memory usage (if psutil is available)
        try:
            import psutil
            memory = psutil.virtual_memory()
            memory_available_gb = memory.available // (1024**3)
            
            self.add_result(DiagnosticResult(
                "Memory",
                memory_available_gb > 0.5,  # At least 500MB available
                f"{memory_available_gb}GB available ({memory.percent}% used)",
                {
                    "total_gb": memory.total // (1024**3),
                    "available_gb": memory_available_gb,
                    "percent_used": memory.percent
                }
            ))
        except ImportError:
            self.add_result(DiagnosticResult(
                "Memory",
                True,
                "psutil not available (skipped)",
                {"skipped": True}
            ))
        except Exception as e:
            self.add_result(DiagnosticResult(
                "Memory",
                False,
                f"Error checking memory: {str(e)}",
                {"error": str(e)}
            ))
    
    def generate_summary(self) -> Dict:
        """Generate diagnostic summary."""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "overall_status": "PASS" if failed_tests == 0 else "FAIL",
            "results": [
                {
                    "test_name": r.test_name,
                    "passed": r.passed,
                    "message": r.message,
                    "details": r.details,
                    "timestamp": r.timestamp
                }
                for r in self.results
            ]
        }
        
        # Print summary
        self.log("📊 Diagnostic Summary", "INFO")
        print(f"{Colors.BOLD}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}Total Tests: {total_tests}{Colors.END}")
        print(f"{Colors.GREEN}Passed: {passed_tests}{Colors.END}")
        print(f"{Colors.RED}Failed: {failed_tests}{Colors.END}")
        print(f"{Colors.BLUE}Success Rate: {summary['success_rate']:.1f}%{Colors.END}")
        print(f"{Colors.BOLD}Overall Status: {Colors.GREEN if summary['overall_status'] == 'PASS' else Colors.RED}{summary['overall_status']}{Colors.END}")
        print(f"{Colors.BOLD}{'='*60}{Colors.END}")
        
        if failed_tests > 0:
            print(f"\n{Colors.RED}{Colors.BOLD}Failed Tests:{Colors.END}")
            for result in self.results:
                if not result.passed:
                    print(f"{Colors.RED}  ❌ {result.test_name}: {result.message}{Colors.END}")
        
        return summary
    
    def save_report(self, output_file: str):
        """Save diagnostic report to file."""
        summary = self.generate_summary()
        
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        self.log(f"📄 Report saved to: {output_file}", "SUCCESS")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="RAG AI-Agent Diagnostic Tool")
    parser.add_argument("--backend-url", help="Backend URL to test")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--output-file", "-o", default="diagnostic_report.json", help="Output file for report")
    
    args = parser.parse_args()
    
    print(f"{Colors.BOLD}{Colors.BLUE}🚀 RAG AI-Agent Diagnostic Tool{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")
    
    # Create diagnostic runner
    runner = DiagnosticRunner(verbose=args.verbose, backend_url=args.backend_url)
    
    try:
        # Run all diagnostics
        summary = runner.run_all_diagnostics()
        
        # Save report
        runner.save_report(args.output_file)
        
        # Exit with appropriate code
        sys.exit(0 if summary['overall_status'] == 'PASS' else 1)
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Diagnostic interrupted by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Diagnostic failed with error: {str(e)}{Colors.END}")
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()