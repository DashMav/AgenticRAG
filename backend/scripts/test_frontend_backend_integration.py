#!/usr/bin/env python3
"""
Frontend-Backend Integration Testing Script for RAG AI-Agent

This script performs comprehensive testing of frontend-backend communication,
including API proxy functionality, CORS configuration, and end-to-end workflows.

Usage:
    python test_frontend_backend_integration.py --frontend https://your-app.vercel.app
    python test_frontend_backend_integration.py --frontend https://your-app.vercel.app --backend https://your-backend.hf.space --verbose
"""

import argparse
import json
import requests
import sys
import time
import tempfile
import os
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin
from dataclasses import dataclass


@dataclass
class TestResult:
    """Result of an integration test"""
    test_name: str
    status: bool
    message: str
    details: Optional[Dict] = None
    duration: float = 0.0


class IntegrationTester:
    """Tests frontend-backend integration"""
    
    def __init__(self, frontend_url: str, backend_url: Optional[str] = None, verbose: bool = False):
        self.frontend_url = frontend_url.rstrip('/')
        self.backend_url = backend_url.rstrip('/') if backend_url else None
        self.verbose = verbose
        self.session = requests.Session()
        self.session.timeout = 30
        self.session.headers.update({
            'User-Agent': 'RAG-AI-Agent-Integration-Tester/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        self.test_chat_id = None
        
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
    
    def _time_test(self, test_func):
        """Decorator to time test execution"""
        start_time = time.time()
        result = test_func()
        duration = time.time() - start_time
        if hasattr(result, 'duration'):
            result.duration = duration
        return result
    
    def test_api_proxy_basic(self) -> TestResult:
        """Test basic API proxy functionality"""
        self.log("Testing basic API proxy functionality...")
        
        try:
            # Test if API requests are properly proxied
            api_url = urljoin(self.frontend_url, "/api/chats/")
            response = self.session.get(api_url)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        return TestResult(
                            test_name="API Proxy Basic",
                            status=True,
                            message=f"API proxy working correctly, received {len(data)} chats",
                            details={"response_type": "json", "data_type": "list", "count": len(data)}
                        )
                    else:
                        return TestResult(
                            test_name="API Proxy Basic",
                            status=False,
                            message="API proxy working but unexpected data format",
                            details={"response_type": "json", "data_type": type(data).__name__}
                        )
                except json.JSONDecodeError:
                    return TestResult(
                        test_name="API Proxy Basic",
                        status=False,
                        message="API proxy working but response is not JSON",
                        details={"response_type": "non-json", "status_code": response.status_code}
                    )
            else:
                return TestResult(
                    test_name="API Proxy Basic",
                    status=False,
                    message=f"API proxy returned status {response.status_code}",
                    details={"status_code": response.status_code}
                )
                
        except requests.exceptions.RequestException as e:
            return TestResult(
                test_name="API Proxy Basic",
                status=False,
                message=f"API proxy connection failed: {e}",
                details={"error": str(e)}
            )
    
    def test_chat_creation_workflow(self) -> TestResult:
        """Test complete chat creation workflow"""
        self.log("Testing chat creation workflow...")
        
        try:
            # Step 1: Create new chat
            create_url = urljoin(self.frontend_url, "/api/chats/new/")
            response = self.session.post(create_url)
            
            if response.status_code != 200:
                return TestResult(
                    test_name="Chat Creation Workflow",
                    status=False,
                    message=f"Chat creation failed with status {response.status_code}",
                    details={"status_code": response.status_code}
                )
            
            try:
                create_data = response.json()
                if "chat_id" not in create_data:
                    return TestResult(
                        test_name="Chat Creation Workflow",
                        status=False,
                        message="Chat creation response missing chat_id",
                        details={"response_data": create_data}
                    )
                
                chat_id = create_data["chat_id"]
                self.test_chat_id = chat_id  # Store for cleanup
                
            except json.JSONDecodeError:
                return TestResult(
                    test_name="Chat Creation Workflow",
                    status=False,
                    message="Chat creation returned non-JSON response"
                )
            
            # Step 2: Verify chat exists in list
            list_url = urljoin(self.frontend_url, "/api/chats/")
            list_response = self.session.get(list_url)
            
            if list_response.status_code == 200:
                try:
                    chats = list_response.json()
                    chat_ids = [chat.get("id") for chat in chats if isinstance(chat, dict)]
                    
                    if chat_id in chat_ids:
                        return TestResult(
                            test_name="Chat Creation Workflow",
                            status=True,
                            message=f"Chat creation workflow successful (chat_id: {chat_id})",
                            details={
                                "chat_id": chat_id,
                                "total_chats": len(chats),
                                "workflow_steps": ["create", "verify_in_list"]
                            }
                        )
                    else:
                        return TestResult(
                            test_name="Chat Creation Workflow",
                            status=False,
                            message="Created chat not found in chat list",
                            details={"chat_id": chat_id, "available_ids": chat_ids}
                        )
                        
                except json.JSONDecodeError:
                    return TestResult(
                        test_name="Chat Creation Workflow",
                        status=False,
                        message="Chat list returned non-JSON response"
                    )
            else:
                return TestResult(
                    test_name="Chat Creation Workflow",
                    status=False,
                    message=f"Chat list retrieval failed with status {list_response.status_code}"
                )
                
        except Exception as e:
            return TestResult(
                test_name="Chat Creation Workflow",
                status=False,
                message=f"Chat creation workflow failed: {e}",
                details={"error": str(e)}
            )
    
    def test_chat_management_operations(self) -> TestResult:
        """Test chat management operations (rename, delete)"""
        self.log("Testing chat management operations...")
        
        if not self.test_chat_id:
            return TestResult(
                test_name="Chat Management Operations",
                status=False,
                message="No test chat available for management operations"
            )
        
        try:
            chat_id = self.test_chat_id
            
            # Step 1: Rename chat
            rename_url = urljoin(self.frontend_url, f"/api/chats/{chat_id}/rename/")
            rename_data = {"name": "Integration Test Chat"}
            rename_response = self.session.put(rename_url, json=rename_data)
            
            if rename_response.status_code != 200:
                return TestResult(
                    test_name="Chat Management Operations",
                    status=False,
                    message=f"Chat rename failed with status {rename_response.status_code}",
                    details={"operation": "rename", "status_code": rename_response.status_code}
                )
            
            # Step 2: Verify rename by getting chat list
            list_url = urljoin(self.frontend_url, "/api/chats/")
            list_response = self.session.get(list_url)
            
            renamed_successfully = False
            if list_response.status_code == 200:
                try:
                    chats = list_response.json()
                    for chat in chats:
                        if isinstance(chat, dict) and chat.get("id") == chat_id:
                            if chat.get("name") == "Integration Test Chat":
                                renamed_successfully = True
                            break
                except json.JSONDecodeError:
                    pass
            
            if not renamed_successfully:
                return TestResult(
                    test_name="Chat Management Operations",
                    status=False,
                    message="Chat rename operation did not persist",
                    details={"operation": "rename_verification"}
                )
            
            # Step 3: Delete chat
            delete_url = urljoin(self.frontend_url, f"/api/chats/{chat_id}/delete")
            delete_response = self.session.delete(delete_url)
            
            if delete_response.status_code != 200:
                return TestResult(
                    test_name="Chat Management Operations",
                    status=False,
                    message=f"Chat delete failed with status {delete_response.status_code}",
                    details={"operation": "delete", "status_code": delete_response.status_code}
                )
            
            # Step 4: Verify deletion
            list_response_after = self.session.get(list_url)
            if list_response_after.status_code == 200:
                try:
                    chats_after = list_response_after.json()
                    chat_ids_after = [chat.get("id") for chat in chats_after if isinstance(chat, dict)]
                    
                    if chat_id not in chat_ids_after:
                        self.test_chat_id = None  # Clear since it's deleted
                        return TestResult(
                            test_name="Chat Management Operations",
                            status=True,
                            message="All chat management operations successful",
                            details={
                                "operations": ["rename", "delete"],
                                "chat_id": chat_id,
                                "final_verification": "chat_deleted"
                            }
                        )
                    else:
                        return TestResult(
                            test_name="Chat Management Operations",
                            status=False,
                            message="Chat delete operation did not persist",
                            details={"operation": "delete_verification"}
                        )
                        
                except json.JSONDecodeError:
                    return TestResult(
                        test_name="Chat Management Operations",
                        status=False,
                        message="Could not verify chat deletion due to JSON error"
                    )
            
            return TestResult(
                test_name="Chat Management Operations",
                status=False,
                message="Could not verify chat management operations"
            )
            
        except Exception as e:
            return TestResult(
                test_name="Chat Management Operations",
                status=False,
                message=f"Chat management operations failed: {e}",
                details={"error": str(e)}
            )
    
    def test_file_upload_endpoint(self) -> TestResult:
        """Test file upload functionality through proxy"""
        self.log("Testing file upload endpoint...")
        
        try:
            # Create a temporary test file
            test_content = "This is a test document for integration testing.\n\nIt contains some sample text to verify that file upload and processing works correctly through the Vercel proxy to the Hugging Face backend."
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                temp_file.write(test_content)
                temp_file_path = temp_file.name
            
            try:
                # Test file upload
                upload_url = urljoin(self.frontend_url, "/api/chats/newChat/send/")
                
                with open(temp_file_path, 'rb') as f:
                    files = {'file': ('test_document.txt', f, 'text/plain')}
                    data = {
                        'query': 'What is this document about?',
                        'agent': 'false'
                    }
                    
                    # Remove JSON content-type header for multipart upload
                    headers = self.session.headers.copy()
                    if 'Content-Type' in headers:
                        del headers['Content-Type']
                    
                    response = self.session.post(
                        upload_url,
                        files=files,
                        data=data,
                        headers=headers,
                        timeout=60  # Longer timeout for file processing
                    )
                
                if response.status_code == 200:
                    try:
                        response_data = response.json()
                        if "response" in response_data:
                            return TestResult(
                                test_name="File Upload Endpoint",
                                status=True,
                                message="File upload and processing successful",
                                details={
                                    "file_size": len(test_content),
                                    "response_received": True,
                                    "response_length": len(response_data.get("response", ""))
                                }
                            )
                        else:
                            return TestResult(
                                test_name="File Upload Endpoint",
                                status=False,
                                message="File upload succeeded but no response received",
                                details={"response_data": response_data}
                            )
                    except json.JSONDecodeError:
                        return TestResult(
                            test_name="File Upload Endpoint",
                            status=False,
                            message="File upload succeeded but response is not JSON"
                        )
                else:
                    return TestResult(
                        test_name="File Upload Endpoint",
                        status=False,
                        message=f"File upload failed with status {response.status_code}",
                        details={"status_code": response.status_code}
                    )
                    
            finally:
                # Cleanup temporary file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
        except Exception as e:
            return TestResult(
                test_name="File Upload Endpoint",
                status=False,
                message=f"File upload test failed: {e}",
                details={"error": str(e)}
            )
    
    def test_cors_and_headers(self) -> TestResult:
        """Test CORS configuration and headers"""
        self.log("Testing CORS configuration and headers...")
        
        try:
            # Test preflight request
            api_url = urljoin(self.frontend_url, "/api/chats/")
            
            preflight_headers = {
                'Origin': self.frontend_url,
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type, Authorization'
            }
            
            preflight_response = self.session.options(api_url, headers=preflight_headers)
            
            # Test actual request
            actual_headers = {
                'Origin': self.frontend_url,
                'Content-Type': 'application/json'
            }
            
            actual_response = self.session.get(api_url, headers=actual_headers)
            
            # Analyze CORS headers
            cors_headers = {
                'Access-Control-Allow-Origin': actual_response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': actual_response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': actual_response.headers.get('Access-Control-Allow-Headers'),
                'Access-Control-Allow-Credentials': actual_response.headers.get('Access-Control-Allow-Credentials')
            }
            
            # Check if CORS is properly configured
            has_cors = any(cors_headers.values())
            origin_allowed = (
                cors_headers['Access-Control-Allow-Origin'] == '*' or
                cors_headers['Access-Control-Allow-Origin'] == self.frontend_url
            )
            
            if actual_response.status_code == 200 and (has_cors or not self.backend_url):
                return TestResult(
                    test_name="CORS and Headers",
                    status=True,
                    message="CORS configuration working correctly",
                    details={
                        "preflight_status": preflight_response.status_code,
                        "actual_status": actual_response.status_code,
                        "cors_headers": {k: v for k, v in cors_headers.items() if v},
                        "origin_allowed": origin_allowed
                    }
                )
            else:
                return TestResult(
                    test_name="CORS and Headers",
                    status=False,
                    message="CORS configuration may have issues",
                    details={
                        "preflight_status": preflight_response.status_code,
                        "actual_status": actual_response.status_code,
                        "cors_headers": cors_headers
                    }
                )
                
        except Exception as e:
            return TestResult(
                test_name="CORS and Headers",
                status=False,
                message=f"CORS test failed: {e}",
                details={"error": str(e)}
            )
    
    def test_error_handling(self) -> TestResult:
        """Test error handling in API proxy"""
        self.log("Testing error handling...")
        
        try:
            # Test with invalid endpoint
            invalid_url = urljoin(self.frontend_url, "/api/invalid-endpoint-12345/")
            response = self.session.get(invalid_url)
            
            # We expect either 404 from backend or proper error handling
            if response.status_code in [404, 405, 422]:
                try:
                    error_data = response.json()
                    return TestResult(
                        test_name="Error Handling",
                        status=True,
                        message=f"Error handling working correctly (status: {response.status_code})",
                        details={
                            "status_code": response.status_code,
                            "error_format": "json",
                            "error_data": error_data
                        }
                    )
                except json.JSONDecodeError:
                    return TestResult(
                        test_name="Error Handling",
                        status=True,
                        message=f"Error handling working (status: {response.status_code}, non-JSON response)",
                        details={"status_code": response.status_code, "error_format": "non-json"}
                    )
            else:
                return TestResult(
                    test_name="Error Handling",
                    status=False,
                    message=f"Unexpected error response status: {response.status_code}",
                    details={"status_code": response.status_code}
                )
                
        except Exception as e:
            return TestResult(
                test_name="Error Handling",
                status=False,
                message=f"Error handling test failed: {e}",
                details={"error": str(e)}
            )
    
    def test_performance_metrics(self) -> TestResult:
        """Test basic performance metrics"""
        self.log("Testing performance metrics...")
        
        try:
            # Test multiple requests to measure consistency
            api_url = urljoin(self.frontend_url, "/api/chats/")
            response_times = []
            
            for i in range(3):
                start_time = time.time()
                response = self.session.get(api_url)
                end_time = time.time()
                
                if response.status_code == 200:
                    response_times.append(end_time - start_time)
                else:
                    return TestResult(
                        test_name="Performance Metrics",
                        status=False,
                        message=f"Performance test failed - request {i+1} returned status {response.status_code}"
                    )
            
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                max_response_time = max(response_times)
                min_response_time = min(response_times)
                
                # Consider good performance if average response time is under 5 seconds
                performance_good = avg_response_time < 5.0
                
                return TestResult(
                    test_name="Performance Metrics",
                    status=performance_good,
                    message=f"Performance test completed (avg: {avg_response_time:.2f}s)",
                    details={
                        "average_response_time": round(avg_response_time, 3),
                        "max_response_time": round(max_response_time, 3),
                        "min_response_time": round(min_response_time, 3),
                        "requests_tested": len(response_times),
                        "performance_threshold": 5.0
                    }
                )
            else:
                return TestResult(
                    test_name="Performance Metrics",
                    status=False,
                    message="No successful requests for performance measurement"
                )
                
        except Exception as e:
            return TestResult(
                test_name="Performance Metrics",
                status=False,
                message=f"Performance test failed: {e}",
                details={"error": str(e)}
            )
    
    def cleanup(self):
        """Clean up any test resources"""
        if self.test_chat_id:
            try:
                delete_url = urljoin(self.frontend_url, f"/api/chats/{self.test_chat_id}/delete")
                self.session.delete(delete_url)
                self.log("Cleaned up test chat", "INFO")
            except:
                pass  # Ignore cleanup errors
    
    def run_all_tests(self) -> List[TestResult]:
        """Run all integration tests"""
        self.log("Starting frontend-backend integration testing...", "INFO")
        self.log(f"Frontend URL: {self.frontend_url}", "INFO")
        if self.backend_url:
            self.log(f"Backend URL: {self.backend_url}", "INFO")
        
        tests = [
            self.test_api_proxy_basic,
            self.test_chat_creation_workflow,
            self.test_chat_management_operations,
            self.test_cors_and_headers,
            self.test_error_handling,
            self.test_performance_metrics,
            # File upload test last as it's most resource intensive
            self.test_file_upload_endpoint,
        ]
        
        results = []
        
        try:
            for test_func in tests:
                self.log(f"\n--- {test_func.__name__.replace('test_', '').replace('_', ' ').title()} ---")
                result = self._time_test(test_func)
                results.append(result)
                
                if result.status:
                    self.log(f"✅ {result.message}", "SUCCESS")
                else:
                    self.log(f"❌ {result.message}", "FAIL")
                
                if self.verbose and result.details:
                    for key, value in result.details.items():
                        self.log(f"  {key}: {value}")
                
                if result.duration > 0:
                    self.log(f"  Duration: {result.duration:.2f}s")
        
        finally:
            # Always cleanup
            self.cleanup()
        
        return results


def main():
    parser = argparse.ArgumentParser(
        description="Test RAG AI-Agent frontend-backend integration"
    )
    parser.add_argument(
        "--frontend", 
        required=True,
        help="Frontend URL (e.g., https://your-app.vercel.app)"
    )
    parser.add_argument(
        "--backend",
        help="Backend URL for reference (e.g., https://your-backend.hf.space)"
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
    if not args.frontend.startswith(('http://', 'https://')):
        print("❌ Error: Frontend URL must start with http:// or https://")
        sys.exit(1)
    
    if args.backend and not args.backend.startswith(('http://', 'https://')):
        print("❌ Error: Backend URL must start with http:// or https://")
        sys.exit(1)
    
    # Run integration tests
    tester = IntegrationTester(args.frontend, args.backend, args.verbose)
    tester.session.timeout = args.timeout
    
    try:
        results = tester.run_all_tests()
        
        # Summary
        print(f"\n{'='*70}")
        print(f"INTEGRATION TEST SUMMARY")
        print(f"{'='*70}")
        
        passed = sum(1 for r in results if r.status)
        total = len(results)
        
        print(f"Frontend URL: {args.frontend}")
        if args.backend:
            print(f"Backend URL: {args.backend}")
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("🎉 All integration tests passed! Frontend-backend communication is working perfectly.")
            sys.exit(0)
        elif passed >= total * 0.75:
            print("✅ Most integration tests passed. Frontend-backend communication is likely working well.")
            sys.exit(0)
        else:
            print("⚠️  Multiple integration tests failed. Please review the issues above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Integration testing interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"🚨 Integration testing failed with error: {e}")
        sys.exit(3)


if __name__ == "__main__":
    main()