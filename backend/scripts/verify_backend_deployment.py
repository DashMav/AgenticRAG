#!/usr/bin/env python3
"""
Backend Deployment Verification Script for RAG AI-Agent

This script tests the deployed FastAPI backend on Hugging Face Spaces to ensure
all endpoints are working correctly and the application is properly configured.

Usage:
    python verify_backend_deployment.py --url https://your-space.hf.space
    python verify_backend_deployment.py --url https://your-space.hf.space --verbose
"""

import argparse
import json
import requests
import sys
import time
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin


class BackendVerifier:
    """Verifies backend deployment functionality"""
    
    def __init__(self, base_url: str, verbose: bool = False):
        self.base_url = base_url.rstrip('/')
        self.verbose = verbose
        self.session = requests.Session()
        self.session.timeout = 30
        self.results = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages with optional verbose output"""
        if self.verbose or level in ["ERROR", "SUCCESS", "FAIL"]:
            prefix = {
                "INFO": "ℹ️",
                "SUCCESS": "✅", 
                "FAIL": "❌",
                "ERROR": "🚨",
                "WARNING": "⚠️"
            }.get(level, "📝")
            print(f"{prefix} {message}")
    
    def test_health_endpoint(self) -> bool:
        """Test basic health/root endpoint"""
        self.log("Testing basic connectivity...")
        
        try:
            # Test root endpoint
            response = self.session.get(self.base_url)
            if response.status_code == 200:
                self.log("Root endpoint accessible", "SUCCESS")
                return True
            else:
                self.log(f"Root endpoint returned status {response.status_code}", "FAIL")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log(f"Failed to connect to backend: {e}", "ERROR")
            return False
    
    def test_api_documentation(self) -> bool:
        """Test FastAPI automatic documentation endpoint"""
        self.log("Testing API documentation endpoint...")
        
        try:
            docs_url = urljoin(self.base_url, "/docs")
            response = self.session.get(docs_url)
            
            if response.status_code == 200:
                if "FastAPI" in response.text or "swagger" in response.text.lower():
                    self.log("API documentation accessible", "SUCCESS")
                    return True
                else:
                    self.log("API docs endpoint accessible but content unexpected", "WARNING")
                    return False
            else:
                self.log(f"API documentation returned status {response.status_code}", "FAIL")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log(f"Failed to access API documentation: {e}", "ERROR")
            return False
    
    def test_cors_configuration(self) -> bool:
        """Test CORS headers are properly configured"""
        self.log("Testing CORS configuration...")
        
        try:
            # Test preflight request
            headers = {
                'Origin': 'https://example.com',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            
            response = self.session.options(
                urljoin(self.base_url, "/api/chats/"),
                headers=headers
            )
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            }
            
            if cors_headers['Access-Control-Allow-Origin']:
                self.log("CORS headers present", "SUCCESS")
                if self.verbose:
                    for header, value in cors_headers.items():
                        if value:
                            self.log(f"  {header}: {value}")
                return True
            else:
                self.log("CORS headers missing or incomplete", "FAIL")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log(f"Failed to test CORS configuration: {e}", "ERROR")
            return False
    
    def test_chat_endpoints(self) -> bool:
        """Test chat-related API endpoints"""
        self.log("Testing chat API endpoints...")
        
        success_count = 0
        total_tests = 0
        
        # Test 1: Get chats (should return empty list initially)
        total_tests += 1
        try:
            response = self.session.get(urljoin(self.base_url, "/api/chats/"))
            if response.status_code == 200:
                chats = response.json()
                if isinstance(chats, list):
                    self.log(f"GET /api/chats/ - Success (found {len(chats)} chats)", "SUCCESS")
                    success_count += 1
                else:
                    self.log("GET /api/chats/ - Invalid response format", "FAIL")
            else:
                self.log(f"GET /api/chats/ - Status {response.status_code}", "FAIL")
        except Exception as e:
            self.log(f"GET /api/chats/ - Error: {e}", "ERROR")
        
        # Test 2: Create new chat
        total_tests += 1
        chat_id = None
        try:
            response = self.session.post(urljoin(self.base_url, "/api/chats/new/"))
            if response.status_code == 200:
                result = response.json()
                if "chat_id" in result:
                    chat_id = result["chat_id"]
                    self.log(f"POST /api/chats/new/ - Success (chat_id: {chat_id})", "SUCCESS")
                    success_count += 1
                else:
                    self.log("POST /api/chats/new/ - Missing chat_id in response", "FAIL")
            else:
                self.log(f"POST /api/chats/new/ - Status {response.status_code}", "FAIL")
        except Exception as e:
            self.log(f"POST /api/chats/new/ - Error: {e}", "ERROR")
        
        # Test 3: Get chat messages (if we have a chat_id)
        if chat_id:
            total_tests += 1
            try:
                response = self.session.get(urljoin(self.base_url, f"/api/chats/{chat_id}/messages/"))
                if response.status_code == 200:
                    messages = response.json()
                    if isinstance(messages, list):
                        self.log(f"GET /api/chats/{chat_id}/messages/ - Success", "SUCCESS")
                        success_count += 1
                    else:
                        self.log("GET /api/chats/{chat_id}/messages/ - Invalid response format", "FAIL")
                else:
                    self.log(f"GET /api/chats/{chat_id}/messages/ - Status {response.status_code}", "FAIL")
            except Exception as e:
                self.log(f"GET /api/chats/{chat_id}/messages/ - Error: {e}", "ERROR")
            
            # Test 4: Rename chat
            total_tests += 1
            try:
                payload = {"name": "Test Chat Verification"}
                response = self.session.put(
                    urljoin(self.base_url, f"/api/chats/{chat_id}/rename/"),
                    json=payload
                )
                if response.status_code == 200:
                    self.log(f"PUT /api/chats/{chat_id}/rename/ - Success", "SUCCESS")
                    success_count += 1
                else:
                    self.log(f"PUT /api/chats/{chat_id}/rename/ - Status {response.status_code}", "FAIL")
            except Exception as e:
                self.log(f"PUT /api/chats/{chat_id}/rename/ - Error: {e}", "ERROR")
            
            # Test 5: Delete chat (cleanup)
            total_tests += 1
            try:
                response = self.session.delete(urljoin(self.base_url, f"/api/chats/{chat_id}/delete"))
                if response.status_code == 200:
                    self.log(f"DELETE /api/chats/{chat_id}/delete - Success", "SUCCESS")
                    success_count += 1
                else:
                    self.log(f"DELETE /api/chats/{chat_id}/delete - Status {response.status_code}", "FAIL")
            except Exception as e:
                self.log(f"DELETE /api/chats/{chat_id}/delete - Error: {e}", "ERROR")
        
        success_rate = (success_count / total_tests) * 100 if total_tests > 0 else 0
        self.log(f"Chat endpoints test completed: {success_count}/{total_tests} passed ({success_rate:.1f}%)")
        
        return success_count == total_tests
    
    def test_environment_variables(self) -> bool:
        """Test that required environment variables are accessible (indirectly)"""
        self.log("Testing environment variable configuration...")
        
        # We can't directly test environment variables, but we can test if the app
        # starts properly, which indicates they're likely configured correctly
        try:
            response = self.session.get(urljoin(self.base_url, "/docs"))
            if response.status_code == 200:
                self.log("Application started successfully (environment variables likely configured)", "SUCCESS")
                return True
            else:
                self.log("Application may have environment variable issues", "WARNING")
                return False
        except Exception as e:
            self.log(f"Could not verify environment variables: {e}", "ERROR")
            return False
    
    def test_file_upload_endpoint(self) -> bool:
        """Test file upload endpoint (without actually uploading files)"""
        self.log("Testing file upload endpoint structure...")
        
        try:
            # Test with minimal data to see if endpoint exists and handles requests
            # We expect this to fail gracefully with proper error handling
            response = self.session.post(
                urljoin(self.base_url, "/api/chats/newChat/send/"),
                data={"query": "test", "agent": "false"}
            )
            
            # We expect either success or a proper error response
            if response.status_code in [200, 400, 422]:  # 422 is validation error
                self.log("File upload endpoint accessible and handling requests", "SUCCESS")
                return True
            else:
                self.log(f"File upload endpoint returned unexpected status {response.status_code}", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"File upload endpoint test failed: {e}", "ERROR")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all verification tests"""
        self.log("Starting backend deployment verification...", "INFO")
        self.log(f"Testing backend at: {self.base_url}", "INFO")
        
        tests = [
            ("Basic Connectivity", self.test_health_endpoint),
            ("API Documentation", self.test_api_documentation),
            ("CORS Configuration", self.test_cors_configuration),
            ("Environment Variables", self.test_environment_variables),
            ("Chat Endpoints", self.test_chat_endpoints),
            ("File Upload Endpoint", self.test_file_upload_endpoint),
        ]
        
        results = {}
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            self.log(f"\n--- {test_name} ---")
            try:
                result = test_func()
                results[test_name] = result
                if result:
                    passed += 1
            except Exception as e:
                self.log(f"Test {test_name} failed with exception: {e}", "ERROR")
                results[test_name] = False
        
        # Summary
        self.log(f"\n{'='*50}")
        self.log(f"VERIFICATION SUMMARY")
        self.log(f"{'='*50}")
        self.log(f"Backend URL: {self.base_url}")
        self.log(f"Tests Passed: {passed}/{total}")
        self.log(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            self.log("🎉 All tests passed! Backend deployment is successful.", "SUCCESS")
        else:
            self.log(f"⚠️  {total-passed} test(s) failed. Please review the issues above.", "WARNING")
        
        return results


def main():
    parser = argparse.ArgumentParser(
        description="Verify RAG AI-Agent backend deployment on Hugging Face Spaces"
    )
    parser.add_argument(
        "--url", 
        required=True,
        help="Backend URL (e.g., https://your-username-your-space.hf.space)"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Request timeout in seconds (default: 30)"
    )
    
    args = parser.parse_args()
    
    # Validate URL format
    if not args.url.startswith(('http://', 'https://')):
        print("❌ Error: URL must start with http:// or https://")
        sys.exit(1)
    
    # Run verification
    verifier = BackendVerifier(args.url, args.verbose)
    verifier.session.timeout = args.timeout
    
    try:
        results = verifier.run_all_tests()
        
        # Exit with appropriate code
        if all(results.values()):
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Some tests failed
            
    except KeyboardInterrupt:
        print("\n⚠️  Verification interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"🚨 Verification failed with error: {e}")
        sys.exit(3)


if __name__ == "__main__":
    main()