#!/usr/bin/env python3
"""
Network connectivity testing script for RAG AI-Agent services.

This script tests network connectivity to all external services used by the
RAG AI-Agent application, including DNS resolution, port connectivity,
and HTTP/HTTPS response testing.

Usage:
    python scripts/test_network_connectivity.py [--timeout SECONDS] [--verbose]

Requirements:
    - Internet connection
    - Python requests library
"""

import socket
import requests
import time
import argparse
import sys
from urllib.parse import urlparse
from typing import Dict, List, Tuple, Optional

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

class NetworkTester:
    """Network connectivity testing class."""
    
    def __init__(self, timeout: int = 10, verbose: bool = False):
        self.timeout = timeout
        self.verbose = verbose
        self.results = []
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message with color coding."""
        if level == "SUCCESS":
            print(f"{Colors.GREEN}✅ {message}{Colors.END}")
        elif level == "ERROR":
            print(f"{Colors.RED}❌ {message}{Colors.END}")
        elif level == "WARNING":
            print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")
        elif level == "INFO":
            print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")
        else:
            print(message)
    
    def test_dns_resolution(self, hostname: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Test DNS resolution for a hostname."""
        try:
            start_time = time.time()
            ip = socket.gethostbyname(hostname)
            resolution_time = time.time() - start_time
            
            if self.verbose:
                self.log(f"DNS resolution for {hostname}: {ip} ({resolution_time:.3f}s)", "SUCCESS")
            else:
                self.log(f"DNS resolution for {hostname}: {ip}", "SUCCESS")
            
            return True, ip, None
        except socket.gaierror as e:
            error_msg = f"DNS resolution failed for {hostname}: {str(e)}"
            self.log(error_msg, "ERROR")
            return False, None, error_msg
        except Exception as e:
            error_msg = f"DNS error for {hostname}: {str(e)}"
            self.log(error_msg, "ERROR")
            return False, None, error_msg
    
    def test_port_connectivity(self, hostname: str, port: int, ip: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """Test TCP connectivity to a specific port."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            start_time = time.time()
            result = sock.connect_ex((hostname, port))
            connect_time = time.time() - start_time
            sock.close()
            
            if result == 0:
                if self.verbose:
                    self.log(f"Port {port} is open on {hostname} ({connect_time:.3f}s)", "SUCCESS")
                else:
                    self.log(f"Port {port} is open on {hostname}", "SUCCESS")
                return True, None
            else:
                error_msg = f"Port {port} is closed on {hostname}"
                self.log(error_msg, "ERROR")
                return False, error_msg
                
        except socket.timeout:
            error_msg = f"Port {port} connection timeout on {hostname}"
            self.log(error_msg, "ERROR")
            return False, error_msg
        except Exception as e:
            error_msg = f"Port {port} connection error on {hostname}: {str(e)}"
            self.log(error_msg, "ERROR")
            return False, error_msg
    
    def test_http_connectivity(self, url: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """Test HTTP/HTTPS connectivity and response."""
        try:
            start_time = time.time()
            response = requests.get(url, timeout=self.timeout, allow_redirects=True)
            response_time = time.time() - start_time
            
            response_info = {
                "status_code": response.status_code,
                "response_time": response_time,
                "headers": dict(response.headers),
                "url": response.url,
                "redirected": response.url != url
            }
            
            if response.status_code == 200:
                if self.verbose:
                    self.log(f"HTTP {response.status_code} from {url} ({response_time:.3f}s)", "SUCCESS")
                else:
                    self.log(f"HTTP {response.status_code} from {url}", "SUCCESS")
                return True, response_info, None
            else:
                error_msg = f"HTTP {response.status_code} from {url}"
                self.log(error_msg, "WARNING")
                return False, response_info, error_msg
                
        except requests.exceptions.Timeout:
            error_msg = f"HTTP timeout for {url} (>{self.timeout}s)"
            self.log(error_msg, "ERROR")
            return False, None, error_msg
        except requests.exceptions.ConnectionError as e:
            error_msg = f"HTTP connection error for {url}: {str(e)}"
            self.log(error_msg, "ERROR")
            return False, None, error_msg
        except requests.exceptions.RequestException as e:
            error_msg = f"HTTP request error for {url}: {str(e)}"
            self.log(error_msg, "ERROR")
            return False, None, error_msg
        except Exception as e:
            error_msg = f"HTTP error for {url}: {str(e)}"
            self.log(error_msg, "ERROR")
            return False, None, error_msg
    
    def test_service_connectivity(self, service_name: str, hostname: str, port: int, https_url: Optional[str] = None):
        """Test complete connectivity for a service."""
        print(f"\n{Colors.BOLD}🔍 Testing {service_name} ({hostname}:{port}){Colors.END}")
        
        service_result = {
            "service": service_name,
            "hostname": hostname,
            "port": port,
            "dns_success": False,
            "port_success": False,
            "http_success": False,
            "ip_address": None,
            "errors": []
        }
        
        # Test DNS resolution
        dns_success, ip, dns_error = self.test_dns_resolution(hostname)
        service_result["dns_success"] = dns_success
        service_result["ip_address"] = ip
        if dns_error:
            service_result["errors"].append(dns_error)
        
        # Test port connectivity (only if DNS succeeded)
        if dns_success:
            port_success, port_error = self.test_port_connectivity(hostname, port, ip)
            service_result["port_success"] = port_success
            if port_error:
                service_result["errors"].append(port_error)
        else:
            self.log(f"Skipping port test for {hostname} (DNS failed)", "WARNING")
        
        # Test HTTP connectivity (if URL provided and port is accessible)
        if https_url and dns_success and service_result.get("port_success", False):
            http_success, http_info, http_error = self.test_http_connectivity(https_url)
            service_result["http_success"] = http_success
            service_result["http_info"] = http_info
            if http_error:
                service_result["errors"].append(http_error)
        elif https_url:
            self.log(f"Skipping HTTP test for {https_url} (connectivity issues)", "WARNING")
        
        self.results.append(service_result)
        
        # Summary for this service
        total_tests = 2 + (1 if https_url else 0)
        passed_tests = sum([
            service_result["dns_success"],
            service_result["port_success"],
            service_result.get("http_success", False) if https_url else False
        ])
        
        if passed_tests == total_tests:
            self.log(f"{service_name}: All tests passed ✨", "SUCCESS")
        else:
            self.log(f"{service_name}: {passed_tests}/{total_tests} tests passed", "WARNING")
    
    def test_all_services(self):
        """Test all external services used by RAG AI-Agent."""
        print(f"{Colors.BOLD}{Colors.BLUE}🌐 RAG AI-Agent Network Connectivity Tests{Colors.END}")
        print(f"{Colors.BOLD}{'='*60}{Colors.END}")
        
        # Define all services to test
        services = [
            {
                "name": "Groq API",
                "hostname": "api.groq.com",
                "port": 443,
                "https_url": "https://api.groq.com"
            },
            {
                "name": "OpenAI API",
                "hostname": "api.openai.com",
                "port": 443,
                "https_url": "https://api.openai.com"
            },
            {
                "name": "Pinecone API",
                "hostname": "api.pinecone.io",
                "port": 443,
                "https_url": "https://api.pinecone.io"
            },
            {
                "name": "Hugging Face",
                "hostname": "huggingface.co",
                "port": 443,
                "https_url": "https://huggingface.co"
            },
            {
                "name": "Vercel",
                "hostname": "vercel.com",
                "port": 443,
                "https_url": "https://vercel.com"
            },
            {
                "name": "GitHub",
                "hostname": "github.com",
                "port": 443,
                "https_url": "https://github.com"
            }
        ]
        
        # Test each service
        for service in services:
            self.test_service_connectivity(
                service["name"],
                service["hostname"],
                service["port"],
                service.get("https_url")
            )
        
        # Generate summary
        self.generate_summary()
    
    def test_custom_backend(self, backend_url: str):
        """Test connectivity to a custom backend URL."""
        print(f"\n{Colors.BOLD}🔍 Testing Custom Backend{Colors.END}")
        
        try:
            parsed_url = urlparse(backend_url)
            hostname = parsed_url.hostname
            port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
            
            if not hostname:
                self.log(f"Invalid backend URL: {backend_url}", "ERROR")
                return
            
            self.test_service_connectivity(
                f"Custom Backend ({backend_url})",
                hostname,
                port,
                backend_url
            )
            
            # Test specific endpoints
            endpoints = ["/health", "/docs", "/api/health"]
            for endpoint in endpoints:
                test_url = f"{backend_url.rstrip('/')}{endpoint}"
                print(f"\n  Testing endpoint: {endpoint}")
                success, info, error = self.test_http_connectivity(test_url)
                
                if success and info:
                    self.log(f"Endpoint {endpoint}: HTTP {info['status_code']}", "SUCCESS")
                elif info and info.get('status_code'):
                    self.log(f"Endpoint {endpoint}: HTTP {info['status_code']}", "WARNING")
                else:
                    self.log(f"Endpoint {endpoint}: Failed", "ERROR")
        
        except Exception as e:
            self.log(f"Error testing backend {backend_url}: {str(e)}", "ERROR")
    
    def generate_summary(self):
        """Generate and display test summary."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}📊 Network Connectivity Summary{Colors.END}")
        print(f"{Colors.BOLD}{'='*60}{Colors.END}")
        
        total_services = len(self.results)
        fully_working = 0
        partially_working = 0
        not_working = 0
        
        for result in self.results:
            tests = [result["dns_success"], result["port_success"]]
            if "http_success" in result:
                tests.append(result["http_success"])
            
            passed = sum(tests)
            total = len(tests)
            
            if passed == total:
                fully_working += 1
            elif passed > 0:
                partially_working += 1
            else:
                not_working += 1
        
        print(f"{Colors.GREEN}✅ Fully Working: {fully_working}/{total_services}{Colors.END}")
        print(f"{Colors.YELLOW}⚠️  Partially Working: {partially_working}/{total_services}{Colors.END}")
        print(f"{Colors.RED}❌ Not Working: {not_working}/{total_services}{Colors.END}")
        
        if not_working > 0:
            print(f"\n{Colors.RED}{Colors.BOLD}Services with Issues:{Colors.END}")
            for result in self.results:
                if not result["dns_success"] or not result["port_success"]:
                    print(f"{Colors.RED}  ❌ {result['service']}{Colors.END}")
                    for error in result["errors"]:
                        print(f"     {error}")
        
        # Recommendations
        print(f"\n{Colors.BOLD}🔧 Recommendations:{Colors.END}")
        
        if not_working == 0 and partially_working == 0:
            print(f"{Colors.GREEN}  ✨ All services are fully accessible!{Colors.END}")
            print(f"{Colors.GREEN}  ✨ Your network configuration looks good for deployment.{Colors.END}")
        else:
            print(f"{Colors.YELLOW}  🔍 Check your internet connection and firewall settings{Colors.END}")
            print(f"{Colors.YELLOW}  🔍 Verify that ports 443 (HTTPS) and 80 (HTTP) are not blocked{Colors.END}")
            
            if any(not result["dns_success"] for result in self.results):
                print(f"{Colors.YELLOW}  🔍 DNS issues detected - check your DNS server configuration{Colors.END}")
            
            if any(not result["port_success"] for result in self.results if result["dns_success"]):
                print(f"{Colors.YELLOW}  🔍 Port connectivity issues - check firewall and proxy settings{Colors.END}")
        
        return {
            "total_services": total_services,
            "fully_working": fully_working,
            "partially_working": partially_working,
            "not_working": not_working,
            "results": self.results
        }

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="RAG AI-Agent Network Connectivity Tester")
    parser.add_argument("--timeout", "-t", type=int, default=10, help="Connection timeout in seconds")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output with timing information")
    parser.add_argument("--backend-url", help="Test connectivity to a specific backend URL")
    
    args = parser.parse_args()
    
    # Create network tester
    tester = NetworkTester(timeout=args.timeout, verbose=args.verbose)
    
    try:
        # Test all standard services
        tester.test_all_services()
        
        # Test custom backend if provided
        if args.backend_url:
            tester.test_custom_backend(args.backend_url)
        
        # Generate final summary
        summary = tester.generate_summary()
        
        # Exit with appropriate code
        if summary["not_working"] == 0:
            print(f"\n{Colors.GREEN}🎉 All network connectivity tests passed!{Colors.END}")
            sys.exit(0)
        else:
            print(f"\n{Colors.RED}⚠️  Some network connectivity issues detected.{Colors.END}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Network tests interrupted by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Network tests failed with error: {str(e)}{Colors.END}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()