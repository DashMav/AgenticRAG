#!/usr/bin/env python3
"""
FastAPI Deployment Test Suite for RAG AI-Agent

This script provides comprehensive testing of the FastAPI application
deployed on Hugging Face Spaces, including CORS validation and
endpoint-specific health checks.

Usage:
    python test_fastapi_deployment.py --url https://your-space.hf.space
    python test_fastapi_deployment.py --url https://your-space.hf.space --test-cors
"""

import argparse
import json
import requests
import sys
import time
from typing import Dict, Any, Optional
from urllib.parse import urljoin


class FastAPITester:
    """Test suite for FastAPI deployment"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 30
        
    def test_openapi_schema(self) -> Dict[str, Any]:
        """Test OpenAPI schema endpoint"""
        print("🔍 Testing OpenAPI schema...")
        
        try:
            response = self.session.get(urljoin(self.base_url, "/openapi.json"))
            
            if response.status_code == 200:
                schema = response.json()
                
                # Validate schema structure
                required_fields = ["openapi", "info", "paths"]
                missing_fields = [field for field in required_fields if field not in schema]
                
                if not missing_fields:
                    print("✅ OpenAPI schema is valid")
                    print(f"   API Title: {schema.get('info', {}).get('title', 'Unknown')}")
                    print(f"   API Version: {schema.get('info', {}).get('version', 'Unknown')}")
                    print(f"   Endpoints: {len(schema.get('paths', {}))}")
                    
                    return {
                        "status": "success",
                        "schema": schema,
                        "endpoint_count": len(schema.get('paths', {}))
                    }
                else:
                    print(f"❌ OpenAPI schema missing required fields: {missing_fields}")
                    return {"status": "error", "message": f"Missing fields: {missing_fields}"}
            else:
                print(f"❌ OpenAPI schema endpoint returned status {response.status_code}")
                return {"status": "error", "message": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Failed to fetch OpenAPI schema: {e}")
            return {"status": "error", "message": str(e)}
    
    def test_cors_headers(self, test_origin: str = "https://example.com") -> Dict[str, Any]:
        """Test CORS configuration"""
        print(f"🔍 Testing CORS headers with origin: {test_origin}")
        
        try:
            # Test preflight request
            headers = {
                'Origin': test_origin,
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type, Authorization'
            }
            
            response = self.session.options(
                urljoin(self.base_url, "/api/chats/"),
                headers=headers
            )
            
            cors_headers = {
                'access-control-allow-origin': response.headers.get('Access-Control-Allow-Origin'),
                'access-control-allow-methods': response.headers.get('Access-Control-Allow-Methods'),
                'access-control-allow-headers': response.headers.get('Access-Control-Allow-Headers'),
                'access-control-allow-credentials': response.headers.get('Access-Control-Allow-Credentials'),
            }
            
            # Check if CORS is properly configured
            allow_origin = cors_headers['access-control-allow-origin']
            
            if allow_origin == "*" or allow_origin == test_origin:
                print("✅ CORS headers are properly configured")
                print(f"   Allow-Origin: {allow_origin}")
                print(f"   Allow-Methods: {cors_headers['access-control-allow-methods']}")
                print(f"   Allow-Headers: {cors_headers['access-control-allow-headers']}")
                
                return {
                    "status": "success",
                    "headers": cors_headers,
                    "allows_origin": True
                }
            else:
                print(f"❌ CORS not configured for origin {test_origin}")
                print(f"   Allow-Origin: {allow_origin}")
                return {
                    "status": "warning",
                    "headers": cors_headers,
                    "allows_origin": False
                }
                
        except Exception as e:
            print(f"❌ CORS test failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def test_fastapi_docs(self) -> Dict[str, Any]:
        """Test FastAPI documentation endpoints"""
        print("🔍 Testing FastAPI documentation endpoints...")
        
        results = {}
        
        # Test Swagger UI
        try:
            docs_response = self.session.get(urljoin(self.base_url, "/docs"))
            if docs_response.status_code == 200 and "swagger" in docs_response.text.lower():
                print("✅ Swagger UI documentation accessible")
                results["swagger"] = True
            else:
                print(f"❌ Swagger UI not accessible (status: {docs_response.status_code})")
                results["swagger"] = False
        except Exception as e:
            print(f"❌ Swagger UI test failed: {e}")
            results["swagger"] = False
        
        # Test ReDoc
        try:
            redoc_response = self.session.get(urljoin(self.base_url, "/redoc"))
            if redoc_response.status_code == 200 and "redoc" in redoc_response.text.lower():
                print("✅ ReDoc documentation accessible")
                results["redoc"] = True
            else:
                print(f"❌ ReDoc not accessible (status: {redoc_response.status_code})")
                results["redoc"] = False
        except Exception as e:
            print(f"❌ ReDoc test failed: {e}")
            results["redoc"] = False
        
        return {
            "status": "success" if any(results.values()) else "error",
            "results": results
        }
    
    def test_api_endpoints(self) -> Dict[str, Any]:
        """Test specific API endpoints"""
        print("🔍 Testing API endpoints...")
        
        endpoints = [
            ("GET", "/api/chats/", "List chats"),
            ("POST", "/api/chats/new/", "Create new chat"),
        ]
        
        results = {}
        
        for method, endpoint, description in endpoints:
            try:
                url = urljoin(self.base_url, endpoint)
                
                if method == "GET":
                    response = self.session.get(url)
                elif method == "POST":
                    response = self.session.post(url)
                else:
                    continue
                
                if response.status_code in [200, 201]:
                    print(f"✅ {method} {endpoint} - {description}")
                    results[endpoint] = {"status": "success", "code": response.status_code}
                else:
                    print(f"❌ {method} {endpoint} - Status {response.status_code}")
                    results[endpoint] = {"status": "error", "code": response.status_code}
                    
            except Exception as e:
                print(f"❌ {method} {endpoint} - Error: {e}")
                results[endpoint] = {"status": "error", "message": str(e)}
        
        return {"results": results}
    
    def test_application_startup(self) -> Dict[str, Any]:
        """Test if the application started properly"""
        print("🔍 Testing application startup...")
        
        try:
            # Test root endpoint
            response = self.session.get(self.base_url)
            
            if response.status_code == 200:
                print("✅ Application is running and accessible")
                
                # Check response time
                response_time = response.elapsed.total_seconds()
                if response_time < 5:
                    print(f"✅ Good response time: {response_time:.2f}s")
                else:
                    print(f"⚠️  Slow response time: {response_time:.2f}s")
                
                return {
                    "status": "success",
                    "response_time": response_time,
                    "status_code": response.status_code
                }
            else:
                print(f"❌ Application returned status {response.status_code}")
                return {
                    "status": "error",
                    "status_code": response.status_code
                }
                
        except requests.exceptions.Timeout:
            print("❌ Application startup test timed out")
            return {"status": "error", "message": "timeout"}
        except Exception as e:
            print(f"❌ Application startup test failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def run_comprehensive_test(self, test_cors: bool = False) -> Dict[str, Any]:
        """Run comprehensive test suite"""
        print("🚀 Starting comprehensive FastAPI deployment test...")
        print(f"🎯 Target URL: {self.base_url}")
        print("=" * 60)
        
        results = {}
        
        # Test 1: Application startup
        results["startup"] = self.test_application_startup()
        
        # Test 2: OpenAPI schema
        results["openapi"] = self.test_openapi_schema()
        
        # Test 3: Documentation endpoints
        results["docs"] = self.test_fastapi_docs()
        
        # Test 4: API endpoints
        results["api_endpoints"] = self.test_api_endpoints()
        
        # Test 5: CORS (optional)
        if test_cors:
            results["cors"] = self.test_cors_headers()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() 
                          if result.get("status") == "success")
        
        print(f"Backend URL: {self.base_url}")
        print(f"Tests Run: {total_tests}")
        print(f"Tests Passed: {passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! FastAPI deployment is successful.")
        else:
            print(f"⚠️  {total_tests - passed_tests} test(s) failed or had warnings.")
        
        return results


def main():
    parser = argparse.ArgumentParser(
        description="Test FastAPI deployment on Hugging Face Spaces"
    )
    parser.add_argument(
        "--url",
        required=True,
        help="Backend URL (e.g., https://your-username-your-space.hf.space)"
    )
    parser.add_argument(
        "--test-cors",
        action="store_true",
        help="Include CORS testing"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Request timeout in seconds (default: 30)"
    )
    
    args = parser.parse_args()
    
    # Validate URL
    if not args.url.startswith(('http://', 'https://')):
        print("❌ Error: URL must start with http:// or https://")
        sys.exit(1)
    
    # Run tests
    tester = FastAPITester(args.url)
    tester.session.timeout = args.timeout
    
    try:
        results = tester.run_comprehensive_test(test_cors=args.test_cors)
        
        # Determine exit code based on results
        success_count = sum(1 for result in results.values() 
                           if result.get("status") == "success")
        total_count = len(results)
        
        if success_count == total_count:
            sys.exit(0)  # All tests passed
        elif success_count > 0:
            sys.exit(1)  # Some tests passed
        else:
            sys.exit(2)  # All tests failed
            
    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user")
        sys.exit(3)
    except Exception as e:
        print(f"🚨 Testing failed with error: {e}")
        sys.exit(4)


if __name__ == "__main__":
    main()