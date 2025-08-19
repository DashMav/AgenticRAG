#!/usr/bin/env python3
"""
Core Functionality Testing Script for RAG AI Agent

This script tests the core functionality of the deployed RAG AI Agent application:
- Document upload and processing
- Chat functionality (simple and agent modes)
- Chat management operations (create, rename, delete)

Requirements: 7.1, 7.2, 7.3, 7.4
"""

import os
import sys
import json
import time
import requests
import tempfile
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

@dataclass
class TestResult:
    """Represents the result of a test case"""
    test_name: str
    passed: bool
    message: str
    details: Optional[Dict] = None
    duration: float = 0.0

class CoreFunctionalityTester:
    """Tests core functionality of the RAG AI Agent application"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        """
        Initialize the tester with the base URL of the deployed application
        
        Args:
            base_url: The base URL of the deployed application (e.g., https://your-app.hf.space)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.test_results: List[TestResult] = []
        
    def log_result(self, test_name: str, passed: bool, message: str, details: Optional[Dict] = None, duration: float = 0.0):
        """Log a test result"""
        result = TestResult(test_name, passed, message, details, duration)
        self.test_results.append(result)
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details and not passed:
            print(f"   Details: {details}")
    
    def test_health_check(self) -> bool:
        """Test if the application is accessible"""
        start_time = time.time()
        try:
            response = self.session.get(f"{self.base_url}/docs", timeout=self.timeout)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.log_result("Health Check", True, "Application is accessible", duration=duration)
                return True
            else:
                self.log_result("Health Check", False, f"Unexpected status code: {response.status_code}", 
                              {"status_code": response.status_code}, duration)
                return False
                
        except requests.exceptions.RequestException as e:
            duration = time.time() - start_time
            self.log_result("Health Check", False, f"Connection failed: {str(e)}", 
                          {"error": str(e)}, duration)
            return False
    
    def test_chat_creation(self) -> Optional[int]:
        """Test creating a new chat"""
        start_time = time.time()
        try:
            response = self.session.post(f"{self.base_url}/api/chats/new/", timeout=self.timeout)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                chat_id = data.get('chat_id')
                if chat_id:
                    self.log_result("Chat Creation", True, f"Chat created with ID: {chat_id}", 
                                  {"chat_id": chat_id}, duration)
                    return chat_id
                else:
                    self.log_result("Chat Creation", False, "No chat_id in response", 
                                  {"response": data}, duration)
                    return None
            else:
                self.log_result("Chat Creation", False, f"Failed with status: {response.status_code}", 
                              {"status_code": response.status_code, "response": response.text}, duration)
                return None
                
        except requests.exceptions.RequestException as e:
            duration = time.time() - start_time
            self.log_result("Chat Creation", False, f"Request failed: {str(e)}", 
                          {"error": str(e)}, duration)
            return None
    
    def test_chat_listing(self) -> bool:
        """Test listing all chats"""
        start_time = time.time()
        try:
            response = self.session.get(f"{self.base_url}/api/chats/", timeout=self.timeout)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                chats = response.json()
                if isinstance(chats, list):
                    self.log_result("Chat Listing", True, f"Retrieved {len(chats)} chats", 
                                  {"chat_count": len(chats)}, duration)
                    return True
                else:
                    self.log_result("Chat Listing", False, "Response is not a list", 
                                  {"response_type": type(chats).__name__}, duration)
                    return False
            else:
                self.log_result("Chat Listing", False, f"Failed with status: {response.status_code}", 
                              {"status_code": response.status_code}, duration)
                return False
                
        except requests.exceptions.RequestException as e:
            duration = time.time() - start_time
            self.log_result("Chat Listing", False, f"Request failed: {str(e)}", 
                          {"error": str(e)}, duration)
            return False
    
    def test_chat_rename(self, chat_id: int) -> bool:
        """Test renaming a chat"""
        start_time = time.time()
        new_name = f"Test Chat {int(time.time())}"
        
        try:
            response = self.session.put(
                f"{self.base_url}/api/chats/{chat_id}/rename/",
                json={"name": new_name},
                timeout=self.timeout
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.log_result("Chat Rename", True, f"Chat renamed to: {new_name}", 
                              {"new_name": new_name}, duration)
                return True
            else:
                self.log_result("Chat Rename", False, f"Failed with status: {response.status_code}", 
                              {"status_code": response.status_code, "response": response.text}, duration)
                return False
                
        except requests.exceptions.RequestException as e:
            duration = time.time() - start_time
            self.log_result("Chat Rename", False, f"Request failed: {str(e)}", 
                          {"error": str(e)}, duration)
            return False
    
    def test_simple_chat_message(self, chat_id: int) -> bool:
        """Test sending a simple chat message (non-agent mode)"""
        start_time = time.time()
        test_query = "What is artificial intelligence?"
        
        try:
            data = {
                'query': test_query,
                'agent': False
            }
            
            response = self.session.post(
                f"{self.base_url}/api/chats/{chat_id}/send/",
                data=data,
                timeout=self.timeout
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                agent_response = result.get('agent_response', {})
                response_body = agent_response.get('body', '')
                
                if response_body and len(response_body) > 10:
                    self.log_result("Simple Chat Message", True, "Received valid response", 
                                  {"response_length": len(response_body), "query": test_query}, duration)
                    return True
                else:
                    self.log_result("Simple Chat Message", False, "Response too short or empty", 
                                  {"response": response_body}, duration)
                    return False
            else:
                self.log_result("Simple Chat Message", False, f"Failed with status: {response.status_code}", 
                              {"status_code": response.status_code, "response": response.text}, duration)
                return False
                
        except requests.exceptions.RequestException as e:
            duration = time.time() - start_time
            self.log_result("Simple Chat Message", False, f"Request failed: {str(e)}", 
                          {"error": str(e)}, duration)
            return False
    
    def test_agent_chat_message(self, chat_id: int) -> bool:
        """Test sending a chat message in agent mode"""
        start_time = time.time()
        test_query = "What is the current time?"
        
        try:
            data = {
                'query': test_query,
                'agent': True
            }
            
            response = self.session.post(
                f"{self.base_url}/api/chats/{chat_id}/send/",
                data=data,
                timeout=self.timeout
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                agent_response = result.get('agent_response', {})
                response_body = agent_response.get('body', '')
                reasoning_steps = agent_response.get('reasoning_steps', [])
                
                if response_body and len(response_body) > 10:
                    has_reasoning = len(reasoning_steps) > 0 if reasoning_steps else False
                    self.log_result("Agent Chat Message", True, 
                                  f"Received agent response with reasoning: {has_reasoning}", 
                                  {"response_length": len(response_body), "has_reasoning": has_reasoning}, duration)
                    return True
                else:
                    self.log_result("Agent Chat Message", False, "Response too short or empty", 
                                  {"response": response_body}, duration)
                    return False
            else:
                self.log_result("Agent Chat Message", False, f"Failed with status: {response.status_code}", 
                              {"status_code": response.status_code, "response": response.text}, duration)
                return False
                
        except requests.exceptions.RequestException as e:
            duration = time.time() - start_time
            self.log_result("Agent Chat Message", False, f"Request failed: {str(e)}", 
                          {"error": str(e)}, duration)
            return False
    
    def create_test_file(self) -> str:
        """Create a temporary test file for upload testing"""
        content = """
        Test Document for RAG AI Agent
        
        This is a test document containing sample information about artificial intelligence.
        
        Artificial Intelligence (AI) is a branch of computer science that aims to create 
        intelligent machines that can perform tasks that typically require human intelligence.
        
        Key concepts in AI include:
        - Machine Learning
        - Natural Language Processing
        - Computer Vision
        - Robotics
        
        This document is used for testing the document upload and processing functionality
        of the RAG AI Agent application.
        """
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        temp_file.write(content)
        temp_file.close()
        
        return temp_file.name
    
    def test_document_upload(self, chat_id: int) -> bool:
        """Test document upload and processing"""
        start_time = time.time()
        test_file_path = None
        
        try:
            # Create test file
            test_file_path = self.create_test_file()
            
            with open(test_file_path, 'rb') as f:
                files = {'files': ('test_document.txt', f, 'text/plain')}
                data = {
                    'query': 'I uploaded a test document',
                    'agent': False
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/chats/{chat_id}/send/",
                    data=data,
                    files=files,
                    timeout=self.timeout
                )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                agent_response = result.get('agent_response', {})
                response_body = agent_response.get('body', '')
                
                if 'test_document.txt' in response_body or 'uploaded' in response_body.lower():
                    self.log_result("Document Upload", True, "Document uploaded and processed successfully", 
                                  {"response_contains_filename": 'test_document.txt' in response_body}, duration)
                    return True
                else:
                    self.log_result("Document Upload", False, "Upload response doesn't confirm processing", 
                                  {"response": response_body}, duration)
                    return False
            else:
                self.log_result("Document Upload", False, f"Failed with status: {response.status_code}", 
                              {"status_code": response.status_code, "response": response.text}, duration)
                return False
                
        except requests.exceptions.RequestException as e:
            duration = time.time() - start_time
            self.log_result("Document Upload", False, f"Request failed: {str(e)}", 
                          {"error": str(e)}, duration)
            return False
        finally:
            # Clean up test file
            if test_file_path and os.path.exists(test_file_path):
                os.unlink(test_file_path)
    
    def test_document_query(self, chat_id: int) -> bool:
        """Test querying uploaded document content"""
        start_time = time.time()
        test_query = "What is mentioned about artificial intelligence in the uploaded document?"
        
        try:
            data = {
                'query': test_query,
                'agent': False
            }
            
            response = self.session.post(
                f"{self.base_url}/api/chats/{chat_id}/send/",
                data=data,
                timeout=self.timeout
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                agent_response = result.get('agent_response', {})
                response_body = agent_response.get('body', '')
                
                # Check if response contains relevant information from the uploaded document
                relevant_keywords = ['artificial intelligence', 'machine learning', 'computer science']
                has_relevant_content = any(keyword.lower() in response_body.lower() for keyword in relevant_keywords)
                
                if has_relevant_content:
                    self.log_result("Document Query", True, "Successfully retrieved information from uploaded document", 
                                  {"response_length": len(response_body)}, duration)
                    return True
                else:
                    self.log_result("Document Query", False, "Response doesn't contain expected document content", 
                                  {"response": response_body[:200] + "..." if len(response_body) > 200 else response_body}, duration)
                    return False
            else:
                self.log_result("Document Query", False, f"Failed with status: {response.status_code}", 
                              {"status_code": response.status_code}, duration)
                return False
                
        except requests.exceptions.RequestException as e:
            duration = time.time() - start_time
            self.log_result("Document Query", False, f"Request failed: {str(e)}", 
                          {"error": str(e)}, duration)
            return False
    
    def test_chat_messages_retrieval(self, chat_id: int) -> bool:
        """Test retrieving chat messages"""
        start_time = time.time()
        try:
            response = self.session.get(f"{self.base_url}/api/chats/{chat_id}/messages/", timeout=self.timeout)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                messages = response.json()
                if isinstance(messages, list) and len(messages) > 0:
                    self.log_result("Chat Messages Retrieval", True, f"Retrieved {len(messages)} messages", 
                                  {"message_count": len(messages)}, duration)
                    return True
                else:
                    self.log_result("Chat Messages Retrieval", False, "No messages found or invalid format", 
                                  {"messages": messages}, duration)
                    return False
            else:
                self.log_result("Chat Messages Retrieval", False, f"Failed with status: {response.status_code}", 
                              {"status_code": response.status_code}, duration)
                return False
                
        except requests.exceptions.RequestException as e:
            duration = time.time() - start_time
            self.log_result("Chat Messages Retrieval", False, f"Request failed: {str(e)}", 
                          {"error": str(e)}, duration)
            return False
    
    def test_chat_deletion(self, chat_id: int) -> bool:
        """Test deleting a chat"""
        start_time = time.time()
        try:
            response = self.session.delete(f"{self.base_url}/api/chats/{chat_id}/delete", timeout=self.timeout)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.log_result("Chat Deletion", True, f"Chat {chat_id} deleted successfully", 
                              {"chat_id": chat_id}, duration)
                return True
            else:
                self.log_result("Chat Deletion", False, f"Failed with status: {response.status_code}", 
                              {"status_code": response.status_code, "response": response.text}, duration)
                return False
                
        except requests.exceptions.RequestException as e:
            duration = time.time() - start_time
            self.log_result("Chat Deletion", False, f"Request failed: {str(e)}", 
                          {"error": str(e)}, duration)
            return False
    
    def run_all_tests(self) -> Dict[str, any]:
        """Run all core functionality tests"""
        print("🚀 Starting Core Functionality Tests")
        print(f"Testing application at: {self.base_url}")
        print("-" * 60)
        
        # Test 1: Health check
        if not self.test_health_check():
            print("❌ Application is not accessible. Stopping tests.")
            return self.generate_report()
        
        # Test 2: Chat listing (initial state)
        self.test_chat_listing()
        
        # Test 3: Create a new chat
        chat_id = self.test_chat_creation()
        if not chat_id:
            print("❌ Cannot create chat. Stopping tests.")
            return self.generate_report()
        
        # Test 4: Rename the chat
        self.test_chat_rename(chat_id)
        
        # Test 5: Send simple chat message
        self.test_simple_chat_message(chat_id)
        
        # Test 6: Send agent chat message
        self.test_agent_chat_message(chat_id)
        
        # Test 7: Upload and process document
        self.test_document_upload(chat_id)
        
        # Test 8: Query uploaded document
        self.test_document_query(chat_id)
        
        # Test 9: Retrieve chat messages
        self.test_chat_messages_retrieval(chat_id)
        
        # Test 10: Delete the chat
        self.test_chat_deletion(chat_id)
        
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, any]:
        """Generate a comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result.passed)
        failed_tests = total_tests - passed_tests
        
        total_duration = sum(result.duration for result in self.test_results)
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_duration": round(total_duration, 2)
            },
            "test_results": [
                {
                    "test_name": result.test_name,
                    "passed": result.passed,
                    "message": result.message,
                    "duration": round(result.duration, 2),
                    "details": result.details
                }
                for result in self.test_results
            ]
        }
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
        print(f"Total Duration: {total_duration:.2f}s")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result.passed:
                    print(f"  - {result.test_name}: {result.message}")
        
        return report

def main():
    """Main function to run the core functionality tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test core functionality of RAG AI Agent")
    parser.add_argument("--url", required=True, help="Base URL of the deployed application")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds")
    parser.add_argument("--output", help="Output file for test results (JSON format)")
    
    args = parser.parse_args()
    
    # Initialize tester
    tester = CoreFunctionalityTester(args.url, args.timeout)
    
    # Run tests
    report = tester.run_all_tests()
    
    # Save report if output file specified
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Test report saved to: {args.output}")
    
    # Exit with appropriate code
    sys.exit(0 if report['summary']['failed'] == 0 else 1)

if __name__ == "__main__":
    main()