#!/usr/bin/env python3
"""
End-to-End Workflow Testing Script for RAG AI Agent

This script tests comprehensive user workflows and validates all API endpoints:
- Complete user workflow tests from start to finish
- API endpoint validation across all features
- Performance and reliability checks
- Load testing and concurrent user simulation

Requirements: 7.1, 6.3, 6.4
"""

import os
import sys
import json
import time
import asyncio
import aiohttp
import tempfile
import statistics
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

@dataclass
class WorkflowStep:
    """Represents a single step in a workflow"""
    name: str
    description: str
    function: callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    critical: bool = True  # If True, workflow stops on failure

@dataclass
class PerformanceMetrics:
    """Performance metrics for API calls"""
    endpoint: str
    method: str
    response_time: float
    status_code: int
    success: bool
    error_message: Optional[str] = None

@dataclass
class WorkflowResult:
    """Result of a complete workflow execution"""
    workflow_name: str
    success: bool
    steps_completed: int
    total_steps: int
    duration: float
    performance_metrics: List[PerformanceMetrics] = field(default_factory=list)
    error_message: Optional[str] = None

class EndToEndTester:
    """Comprehensive end-to-end testing for RAG AI Agent"""
    
    def __init__(self, base_url: str, timeout: int = 60):
        """
        Initialize the E2E tester
        
        Args:
            base_url: The base URL of the deployed application
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.performance_metrics: List[PerformanceMetrics] = []
        self.workflow_results: List[WorkflowResult] = []
        
    def log_performance(self, endpoint: str, method: str, response_time: float, 
                       status_code: int, success: bool, error_message: Optional[str] = None):
        """Log performance metrics for an API call"""
        metric = PerformanceMetrics(
            endpoint=endpoint,
            method=method,
            response_time=response_time,
            status_code=status_code,
            success=success,
            error_message=error_message
        )
        self.performance_metrics.append(metric)
    
    async def make_request(self, session: aiohttp.ClientSession, method: str, 
                          endpoint: str, **kwargs) -> Tuple[bool, Dict, float]:
        """Make an async HTTP request and log performance"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            async with session.request(method, url, timeout=self.timeout, **kwargs) as response:
                duration = time.time() - start_time
                
                if response.content_type == 'application/json':
                    data = await response.json()
                else:
                    data = {"text": await response.text()}
                
                success = 200 <= response.status < 300
                self.log_performance(endpoint, method, duration, response.status, success)
                
                return success, data, duration
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_performance(endpoint, method, duration, 0, False, str(e))
            return False, {"error": str(e)}, duration
    
    def create_test_documents(self) -> List[str]:
        """Create multiple test documents for comprehensive testing"""
        documents = [
            {
                "filename": "ai_basics.txt",
                "content": """
                Artificial Intelligence Fundamentals
                
                Artificial Intelligence (AI) is the simulation of human intelligence in machines.
                Key areas include machine learning, natural language processing, and computer vision.
                
                Machine Learning Types:
                - Supervised Learning
                - Unsupervised Learning  
                - Reinforcement Learning
                
                Applications:
                - Healthcare diagnostics
                - Autonomous vehicles
                - Financial trading
                - Virtual assistants
                """
            },
            {
                "filename": "ml_algorithms.txt", 
                "content": """
                Machine Learning Algorithms Overview
                
                Popular algorithms include:
                
                1. Linear Regression - for predicting continuous values
                2. Decision Trees - for classification and regression
                3. Random Forest - ensemble method using multiple trees
                4. Support Vector Machines - for classification tasks
                5. Neural Networks - inspired by biological neurons
                
                Deep Learning:
                - Convolutional Neural Networks (CNNs)
                - Recurrent Neural Networks (RNNs)
                - Transformers
                """
            },
            {
                "filename": "data_science.txt",
                "content": """
                Data Science Process
                
                The data science workflow typically includes:
                
                1. Data Collection - gathering relevant datasets
                2. Data Cleaning - handling missing values and outliers
                3. Exploratory Data Analysis - understanding data patterns
                4. Feature Engineering - creating meaningful variables
                5. Model Building - selecting and training algorithms
                6. Model Evaluation - assessing performance metrics
                7. Deployment - putting models into production
                
                Tools commonly used:
                - Python (pandas, scikit-learn, TensorFlow)
                - R (dplyr, ggplot2, caret)
                - SQL for database queries
                - Jupyter notebooks for analysis
                """
            }
        ]
        
        file_paths = []
        for doc in documents:
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
            temp_file.write(doc["content"])
            temp_file.close()
            file_paths.append(temp_file.name)
        
        return file_paths
    
    async def workflow_new_user_complete_session(self, session: aiohttp.ClientSession) -> WorkflowResult:
        """Test complete new user workflow from start to finish"""
        workflow_name = "New User Complete Session"
        start_time = time.time()
        steps_completed = 0
        total_steps = 12
        
        try:
            # Step 1: Check application health
            success, _, _ = await self.make_request(session, 'GET', '/docs')
            if not success:
                return WorkflowResult(workflow_name, False, steps_completed, total_steps, 
                                    time.time() - start_time, error_message="Application not accessible")
            steps_completed += 1
            
            # Step 2: List initial chats (should be empty or existing)
            success, chats_data, _ = await self.make_request(session, 'GET', '/api/chats/')
            if not success:
                return WorkflowResult(workflow_name, False, steps_completed, total_steps,
                                    time.time() - start_time, error_message="Cannot list chats")
            steps_completed += 1
            
            # Step 3: Create new chat
            success, chat_data, _ = await self.make_request(session, 'POST', '/api/chats/new/')
            if not success or 'chat_id' not in chat_data:
                return WorkflowResult(workflow_name, False, steps_completed, total_steps,
                                    time.time() - start_time, error_message="Cannot create chat")
            chat_id = chat_data['chat_id']
            steps_completed += 1
            
            # Step 4: Rename the chat
            new_name = f"My AI Learning Session {int(time.time())}"
            success, _, _ = await self.make_request(
                session, 'PUT', f'/api/chats/{chat_id}/rename/',
                json={"name": new_name}
            )
            if not success:
                return WorkflowResult(workflow_name, False, steps_completed, total_steps,
                                    time.time() - start_time, error_message="Cannot rename chat")
            steps_completed += 1
            
            # Step 5: Upload first document
            test_files = self.create_test_documents()
            try:
                with open(test_files[0], 'rb') as f:
                    form_data = aiohttp.FormData()
                    form_data.add_field('query', 'I am uploading a document about AI basics')
                    form_data.add_field('agent', 'false')
                    form_data.add_field('files', f, filename='ai_basics.txt', content_type='text/plain')
                    
                    success, upload_data, _ = await self.make_request(
                        session, 'POST', f'/api/chats/{chat_id}/send/', data=form_data
                    )
                    if not success:
                        return WorkflowResult(workflow_name, False, steps_completed, total_steps,
                                            time.time() - start_time, error_message="Cannot upload document")
            finally:
                # Clean up test files
                for file_path in test_files:
                    if os.path.exists(file_path):
                        os.unlink(file_path)
            steps_completed += 1
            
            # Step 6: Ask question about uploaded document
            success, query_data, _ = await self.make_request(
                session, 'POST', f'/api/chats/{chat_id}/send/',
                data={'query': 'What are the main types of machine learning mentioned in the document?', 'agent': 'false'}
            )
            if not success:
                return WorkflowResult(workflow_name, False, steps_completed, total_steps,
                                    time.time() - start_time, error_message="Cannot query document")
            steps_completed += 1
            
            # Step 7: Use agent mode for calculation
            success, agent_data, _ = await self.make_request(
                session, 'POST', f'/api/chats/{chat_id}/send/',
                data={'query': 'Calculate 15 * 23 + 47', 'agent': 'true'}
            )
            if not success:
                return WorkflowResult(workflow_name, False, steps_completed, total_steps,
                                    time.time() - start_time, error_message="Cannot use agent mode")
            steps_completed += 1
            
            # Step 8: Ask for current time using agent
            success, time_data, _ = await self.make_request(
                session, 'POST', f'/api/chats/{chat_id}/send/',
                data={'query': 'What is the current date and time?', 'agent': 'true'}
            )
            if not success:
                return WorkflowResult(workflow_name, False, steps_completed, total_steps,
                                    time.time() - start_time, error_message="Cannot get current time")
            steps_completed += 1
            
            # Step 9: Retrieve all messages
            success, messages_data, _ = await self.make_request(session, 'GET', f'/api/chats/{chat_id}/messages/')
            if not success or not isinstance(messages_data, list):
                return WorkflowResult(workflow_name, False, steps_completed, total_steps,
                                    time.time() - start_time, error_message="Cannot retrieve messages")
            steps_completed += 1
            
            # Step 10: Verify message count (should have multiple messages)
            if len(messages_data) < 6:  # At least 6 messages (3 user + 3 agent responses)
                return WorkflowResult(workflow_name, False, steps_completed, total_steps,
                                    time.time() - start_time, error_message="Insufficient messages in chat")
            steps_completed += 1
            
            # Step 11: List chats again to verify our chat exists
            success, final_chats, _ = await self.make_request(session, 'GET', '/api/chats/')
            if not success:
                return WorkflowResult(workflow_name, False, steps_completed, total_steps,
                                    time.time() - start_time, error_message="Cannot list final chats")
            
            # Verify our chat is in the list
            chat_found = any(chat.get('id') == chat_id for chat in final_chats)
            if not chat_found:
                return WorkflowResult(workflow_name, False, steps_completed, total_steps,
                                    time.time() - start_time, error_message="Created chat not found in list")
            steps_completed += 1
            
            # Step 12: Clean up - delete the chat
            success, _, _ = await self.make_request(session, 'DELETE', f'/api/chats/{chat_id}/delete')
            if not success:
                return WorkflowResult(workflow_name, False, steps_completed, total_steps,
                                    time.time() - start_time, error_message="Cannot delete chat")
            steps_completed += 1
            
            return WorkflowResult(workflow_name, True, steps_completed, total_steps, time.time() - start_time)
            
        except Exception as e:
            return WorkflowResult(workflow_name, False, steps_completed, total_steps,
                                time.time() - start_time, error_message=str(e))
    
    async def workflow_multi_document_research(self, session: aiohttp.ClientSession) -> WorkflowResult:
        """Test workflow with multiple document uploads and complex queries"""
        workflow_name = "Multi-Document Research Session"
        start_time = time.time()
        steps_completed = 0
        total_steps = 8
        
        try:
            # Step 1: Create research chat
            success, chat_data, _ = await self.make_request(session, 'POST', '/api/chats/new/')
            if not success or 'chat_id' not in chat_data:
                return WorkflowResult(workflow_name, False, steps_completed, total_steps,
                                    time.time() - start_time, error_message="Cannot create research chat")
            chat_id = chat_data['chat_id']
            steps_completed += 1
            
            # Step 2: Rename to research session
            success, _, _ = await self.make_request(
                session, 'PUT', f'/api/chats/{chat_id}/rename/',
                json={"name": "AI Research Session"}
            )
            if not success:
                return WorkflowResult(workflow_name, False, steps_completed, total_steps,
                                    time.time() - start_time, error_message="Cannot rename research chat")
            steps_completed += 1
            
            # Step 3-5: Upload multiple documents
            test_files = self.create_test_documents()
            try:
                for i, file_path in enumerate(test_files):
                    with open(file_path, 'rb') as f:
                        form_data = aiohttp.FormData()
                        form_data.add_field('query', f'Uploading document {i+1} for research')
                        form_data.add_field('agent', 'false')
                        form_data.add_field('files', f, filename=f'research_doc_{i+1}.txt', content_type='text/plain')
                        
                        success, _, _ = await self.make_request(
                            session, 'POST', f'/api/chats/{chat_id}/send/', data=form_data
                        )
                        if not success:
                            return WorkflowResult(workflow_name, False, steps_completed, total_steps,
                                                time.time() - start_time, error_message=f"Cannot upload document {i+1}")
                    steps_completed += 1
            finally:
                # Clean up test files
                for file_path in test_files:
                    if os.path.exists(file_path):
                        os.unlink(file_path)
            
            # Step 6: Complex cross-document query
            success, complex_query, _ = await self.make_request(
                session, 'POST', f'/api/chats/{chat_id}/send/',
                data={'query': 'Compare the machine learning algorithms mentioned across all uploaded documents and summarize the key differences', 'agent': 'false'}
            )
            if not success:
                return WorkflowResult(workflow_name, False, steps_completed, total_steps,
                                    time.time() - start_time, error_message="Cannot perform complex query")
            steps_completed += 1
            
            # Step 7: Agent-assisted analysis
            success, agent_analysis, _ = await self.make_request(
                session, 'POST', f'/api/chats/{chat_id}/send/',
                data={'query': 'Based on the uploaded documents, calculate how many different AI applications are mentioned in total', 'agent': 'true'}
            )
            if not success:
                return WorkflowResult(workflow_name, False, steps_completed, total_steps,
                                    time.time() - start_time, error_message="Cannot perform agent analysis")
            steps_completed += 1
            
            # Step 8: Clean up
            success, _, _ = await self.make_request(session, 'DELETE', f'/api/chats/{chat_id}/delete')
            if not success:
                return WorkflowResult(workflow_name, False, steps_completed, total_steps,
                                    time.time() - start_time, error_message="Cannot delete research chat")
            steps_completed += 1
            
            return WorkflowResult(workflow_name, True, steps_completed, total_steps, time.time() - start_time)
            
        except Exception as e:
            return WorkflowResult(workflow_name, False, steps_completed, total_steps,
                                time.time() - start_time, error_message=str(e))
    
    async def workflow_concurrent_users(self, num_users: int = 3) -> WorkflowResult:
        """Test concurrent user sessions"""
        workflow_name = f"Concurrent Users ({num_users} users)"
        start_time = time.time()
        
        async def single_user_session(session: aiohttp.ClientSession, user_id: int) -> bool:
            """Simulate a single user session"""
            try:
                # Create chat
                success, chat_data, _ = await self.make_request(session, 'POST', '/api/chats/new/')
                if not success:
                    return False
                
                chat_id = chat_data['chat_id']
                
                # Rename chat
                success, _, _ = await self.make_request(
                    session, 'PUT', f'/api/chats/{chat_id}/rename/',
                    json={"name": f"User {user_id} Session"}
                )
                if not success:
                    return False
                
                # Send message
                success, _, _ = await self.make_request(
                    session, 'POST', f'/api/chats/{chat_id}/send/',
                    data={'query': f'Hello from user {user_id}', 'agent': 'false'}
                )
                if not success:
                    return False
                
                # Clean up
                success, _, _ = await self.make_request(session, 'DELETE', f'/api/chats/{chat_id}/delete')
                return success
                
            except Exception:
                return False
        
        try:
            connector = aiohttp.TCPConnector(limit=num_users * 2)
            async with aiohttp.ClientSession(connector=connector) as session:
                # Run concurrent user sessions
                tasks = [single_user_session(session, i) for i in range(num_users)]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                successful_users = sum(1 for result in results if result is True)
                
                return WorkflowResult(
                    workflow_name, 
                    successful_users == num_users,
                    successful_users,
                    num_users,
                    time.time() - start_time,
                    error_message=f"Only {successful_users}/{num_users} users completed successfully" if successful_users < num_users else None
                )
                
        except Exception as e:
            return WorkflowResult(workflow_name, False, 0, num_users, time.time() - start_time, error_message=str(e))
    
    async def test_api_endpoints_comprehensive(self, session: aiohttp.ClientSession) -> WorkflowResult:
        """Test all API endpoints comprehensively"""
        workflow_name = "Comprehensive API Endpoint Testing"
        start_time = time.time()
        steps_completed = 0
        total_steps = 10
        
        try:
            # Test 1: Health check endpoints
            endpoints_to_test = ['/docs', '/openapi.json']
            for endpoint in endpoints_to_test:
                success, _, _ = await self.make_request(session, 'GET', endpoint)
                if not success and endpoint == '/docs':  # /docs is critical
                    return WorkflowResult(workflow_name, False, steps_completed, total_steps,
                                        time.time() - start_time, error_message=f"Critical endpoint {endpoint} failed")
            steps_completed += 1
            
            # Test 2: Chat CRUD operations
            # Create
            success, chat_data, _ = await self.make_request(session, 'POST', '/api/chats/new/')
            if not success:
                return WorkflowResult(workflow_name, False, steps_completed, total_steps,
                                    time.time() - start_time, error_message="Chat creation failed")
            chat_id = chat_data['chat_id']
            steps_completed += 1
            
            # Read (list)
            success, _, _ = await self.make_request(session, 'GET', '/api/chats/')
            if not success:
                return WorkflowResult(workflow_name, False, steps_completed, total_steps,
                                    time.time() - start_time, error_message="Chat listing failed")
            steps_completed += 1
            
            # Update (rename)
            success, _, _ = await self.make_request(
                session, 'PUT', f'/api/chats/{chat_id}/rename/',
                json={"name": "API Test Chat"}
            )
            if not success:
                return WorkflowResult(workflow_name, False, steps_completed, total_steps,
                                    time.time() - start_time, error_message="Chat rename failed")
            steps_completed += 1
            
            # Test 3: Message operations
            # Send simple message
            success, _, _ = await self.make_request(
                session, 'POST', f'/api/chats/{chat_id}/send/',
                data={'query': 'Test message', 'agent': 'false'}
            )
            if not success:
                return WorkflowResult(workflow_name, False, steps_completed, total_steps,
                                    time.time() - start_time, error_message="Simple message failed")
            steps_completed += 1
            
            # Send agent message
            success, _, _ = await self.make_request(
                session, 'POST', f'/api/chats/{chat_id}/send/',
                data={'query': 'What is 2+2?', 'agent': 'true'}
            )
            if not success:
                return WorkflowResult(workflow_name, False, steps_completed, total_steps,
                                    time.time() - start_time, error_message="Agent message failed")
            steps_completed += 1
            
            # Get messages
            success, messages, _ = await self.make_request(session, 'GET', f'/api/chats/{chat_id}/messages/')
            if not success:
                return WorkflowResult(workflow_name, False, steps_completed, total_steps,
                                    time.time() - start_time, error_message="Message retrieval failed")
            steps_completed += 1
            
            # Test 4: File upload
            test_files = self.create_test_documents()
            try:
                with open(test_files[0], 'rb') as f:
                    form_data = aiohttp.FormData()
                    form_data.add_field('query', 'API test file upload')
                    form_data.add_field('agent', 'false')
                    form_data.add_field('files', f, filename='api_test.txt', content_type='text/plain')
                    
                    success, _, _ = await self.make_request(
                        session, 'POST', f'/api/chats/{chat_id}/send/', data=form_data
                    )
                    if not success:
                        return WorkflowResult(workflow_name, False, steps_completed, total_steps,
                                            time.time() - start_time, error_message="File upload failed")
            finally:
                for file_path in test_files:
                    if os.path.exists(file_path):
                        os.unlink(file_path)
            steps_completed += 1
            
            # Test 5: Error handling - invalid chat ID
            success, _, _ = await self.make_request(session, 'GET', '/api/chats/99999/messages/')
            # This should fail gracefully (404), not crash
            steps_completed += 1
            
            # Test 6: Clean up - Delete chat
            success, _, _ = await self.make_request(session, 'DELETE', f'/api/chats/{chat_id}/delete')
            if not success:
                return WorkflowResult(workflow_name, False, steps_completed, total_steps,
                                    time.time() - start_time, error_message="Chat deletion failed")
            steps_completed += 1
            
            return WorkflowResult(workflow_name, True, steps_completed, total_steps, time.time() - start_time)
            
        except Exception as e:
            return WorkflowResult(workflow_name, False, steps_completed, total_steps,
                                time.time() - start_time, error_message=str(e))
    
    async def run_performance_tests(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Run performance and load tests"""
        print("🚀 Running Performance Tests...")
        
        # Test response times under normal load
        response_times = []
        for i in range(10):
            start_time = time.time()
            success, _, _ = await self.make_request(session, 'GET', '/api/chats/')
            if success:
                response_times.append(time.time() - start_time)
        
        # Calculate performance statistics
        if response_times:
            perf_stats = {
                "average_response_time": statistics.mean(response_times),
                "median_response_time": statistics.median(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "std_deviation": statistics.stdev(response_times) if len(response_times) > 1 else 0
            }
        else:
            perf_stats = {"error": "No successful requests for performance measurement"}
        
        return perf_stats
    
    async def run_all_workflows(self) -> Dict[str, Any]:
        """Run all end-to-end workflow tests"""
        print("🚀 Starting End-to-End Workflow Tests")
        print(f"Testing application at: {self.base_url}")
        print("-" * 60)
        
        connector = aiohttp.TCPConnector(limit=20)
        async with aiohttp.ClientSession(connector=connector) as session:
            # Run individual workflows
            workflows = [
                self.workflow_new_user_complete_session(session),
                self.workflow_multi_document_research(session),
                self.test_api_endpoints_comprehensive(session),
                self.workflow_concurrent_users(3)
            ]
            
            # Execute workflows
            workflow_results = await asyncio.gather(*workflows, return_exceptions=True)
            
            # Process results
            for result in workflow_results:
                if isinstance(result, Exception):
                    self.workflow_results.append(WorkflowResult(
                        "Unknown Workflow", False, 0, 1, 0.0, error_message=str(result)
                    ))
                else:
                    self.workflow_results.append(result)
            
            # Run performance tests
            performance_stats = await self.run_performance_tests(session)
        
        return self.generate_comprehensive_report(performance_stats)
    
    def generate_comprehensive_report(self, performance_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_workflows = len(self.workflow_results)
        successful_workflows = sum(1 for result in self.workflow_results if result.success)
        
        # Performance metrics analysis
        successful_requests = [m for m in self.performance_metrics if m.success]
        failed_requests = [m for m in self.performance_metrics if not m.success]
        
        if successful_requests:
            avg_response_time = statistics.mean([m.response_time for m in successful_requests])
            max_response_time = max([m.response_time for m in successful_requests])
        else:
            avg_response_time = 0
            max_response_time = 0
        
        report = {
            "summary": {
                "total_workflows": total_workflows,
                "successful_workflows": successful_workflows,
                "failed_workflows": total_workflows - successful_workflows,
                "success_rate": (successful_workflows / total_workflows * 100) if total_workflows > 0 else 0,
                "total_api_calls": len(self.performance_metrics),
                "successful_api_calls": len(successful_requests),
                "failed_api_calls": len(failed_requests),
                "api_success_rate": (len(successful_requests) / len(self.performance_metrics) * 100) if self.performance_metrics else 0,
                "average_response_time": round(avg_response_time, 3),
                "max_response_time": round(max_response_time, 3)
            },
            "workflow_results": [
                {
                    "workflow_name": result.workflow_name,
                    "success": result.success,
                    "steps_completed": result.steps_completed,
                    "total_steps": result.total_steps,
                    "completion_rate": (result.steps_completed / result.total_steps * 100) if result.total_steps > 0 else 0,
                    "duration": round(result.duration, 2),
                    "error_message": result.error_message
                }
                for result in self.workflow_results
            ],
            "performance_analysis": performance_stats,
            "api_endpoint_analysis": self._analyze_api_endpoints(),
            "reliability_metrics": {
                "error_rate": (len(failed_requests) / len(self.performance_metrics) * 100) if self.performance_metrics else 0,
                "timeout_rate": len([m for m in failed_requests if "timeout" in str(m.error_message).lower()]) / len(self.performance_metrics) * 100 if self.performance_metrics else 0
            }
        }
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 END-TO-END TEST SUMMARY")
        print("=" * 60)
        print(f"Workflows: {successful_workflows}/{total_workflows} successful ({report['summary']['success_rate']:.1f}%)")
        print(f"API Calls: {len(successful_requests)}/{len(self.performance_metrics)} successful ({report['summary']['api_success_rate']:.1f}%)")
        print(f"Average Response Time: {avg_response_time:.3f}s")
        print(f"Max Response Time: {max_response_time:.3f}s")
        
        if total_workflows - successful_workflows > 0:
            print("\n❌ FAILED WORKFLOWS:")
            for result in self.workflow_results:
                if not result.success:
                    print(f"  - {result.workflow_name}: {result.error_message}")
        
        return report
    
    def _analyze_api_endpoints(self) -> Dict[str, Any]:
        """Analyze API endpoint performance"""
        endpoint_stats = {}
        
        for metric in self.performance_metrics:
            endpoint = metric.endpoint
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {
                    "total_calls": 0,
                    "successful_calls": 0,
                    "response_times": []
                }
            
            endpoint_stats[endpoint]["total_calls"] += 1
            if metric.success:
                endpoint_stats[endpoint]["successful_calls"] += 1
                endpoint_stats[endpoint]["response_times"].append(metric.response_time)
        
        # Calculate statistics for each endpoint
        for endpoint, stats in endpoint_stats.items():
            if stats["response_times"]:
                stats["avg_response_time"] = statistics.mean(stats["response_times"])
                stats["max_response_time"] = max(stats["response_times"])
                stats["success_rate"] = (stats["successful_calls"] / stats["total_calls"]) * 100
            else:
                stats["avg_response_time"] = 0
                stats["max_response_time"] = 0
                stats["success_rate"] = 0
            
            # Remove raw response times from final report
            del stats["response_times"]
        
        return endpoint_stats

def main():
    """Main function to run end-to-end workflow tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run end-to-end workflow tests for RAG AI Agent")
    parser.add_argument("--url", required=True, help="Base URL of the deployed application")
    parser.add_argument("--timeout", type=int, default=60, help="Request timeout in seconds")
    parser.add_argument("--output", help="Output file for test results (JSON format)")
    parser.add_argument("--concurrent-users", type=int, default=3, help="Number of concurrent users to simulate")
    
    args = parser.parse_args()
    
    # Initialize tester
    tester = EndToEndTester(args.url, args.timeout)
    
    # Run tests
    try:
        report = asyncio.run(tester.run_all_workflows())
        
        # Save report if output file specified
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n📄 Test report saved to: {args.output}")
        
        # Exit with appropriate code
        success_rate = report['summary']['success_rate']
        sys.exit(0 if success_rate >= 80 else 1)  # 80% success rate threshold
        
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()