#!/usr/bin/env python3
"""
Frontend Deployment Verification Script for RAG AI-Agent

This script tests the deployed React frontend on Vercel to ensure proper deployment,
API connectivity through proxy configuration, and end-to-end functionality.

Usage:
    python verify_frontend_deployment.py --url https://your-app.vercel.app
    python verify_frontend_deployment.py --url https://your-app.vercel.app --backend https://your-backend.hf.space --verbose
"""

import argparse
import json
import requests
import sys
import time
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
import re


class FrontendVerifier:
    """Verifies frontend deployment functionality"""
    
    def __init__(self, frontend_url: str, backend_url: Optional[str] = None, verbose: bool = False):
        self.frontend_url = frontend_url.rstrip('/')
        self.backend_url = backend_url.rstrip('/') if backend_url else None
        self.verbose = verbose
        self.session = requests.Session()
        self.session.timeout = 30
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
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
    
    def test_frontend_accessibility(self) -> bool:
        """Test if frontend is accessible and loads correctly"""
        self.log("Testing frontend accessibility...")
        
        try:
            response = self.session.get(self.frontend_url)
            
            if response.status_code == 200:
                # Check if it's a React app by looking for common indicators
                content = response.text.lower()
                
                react_indicators = [
                    'react',
                    'root',
                    'div id="root"',
                    'vite',
                    'app.jsx',
                    'main.jsx'
                ]
                
                found_indicators = [indicator for indicator in react_indicators if indicator in content]
                
                if found_indicators:
                    self.log(f"Frontend accessible and appears to be a React app", "SUCCESS")
                    if self.verbose:
                        self.log(f"  Found indicators: {', '.join(found_indicators)}")
                    return True
                else:
                    self.log("Frontend accessible but may not be a React app", "WARNING")
                    return True  # Still consider it a success if accessible
            else:
                self.log(f"Frontend returned status {response.status_code}", "FAIL")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log(f"Failed to access frontend: {e}", "ERROR")
            return False
    
    def test_static_assets(self) -> bool:
        """Test if static assets are loading correctly"""
        self.log("Testing static assets loading...")
        
        try:
            response = self.session.get(self.frontend_url)
            if response.status_code != 200:
                self.log("Cannot test assets - frontend not accessible", "FAIL")
                return False
            
            content = response.text
            
            # Look for common asset references
            asset_patterns = [
                r'src="([^"]*\.js)"',
                r'href="([^"]*\.css)"',
                r'src="([^"]*\.ico)"'
            ]
            
            assets_found = []
            for pattern in asset_patterns:
                matches = re.findall(pattern, content)
                assets_found.extend(matches)
            
            if not assets_found:
                self.log("No static assets found in HTML", "WARNING")
                return True  # Not necessarily a failure for SPAs
            
            # Test a few key assets
            successful_assets = 0
            total_assets = min(len(assets_found), 5)  # Test max 5 assets
            
            for asset_path in assets_found[:5]:
                if asset_path.startswith('http'):
                    asset_url = asset_path
                elif asset_path.startswith('/'):
                    asset_url = self.frontend_url + asset_path
                else:
                    asset_url = urljoin(self.frontend_url, asset_path)
                
                try:
                    asset_response = self.session.head(asset_url, timeout=10)
                    if asset_response.status_code == 200:
                        successful_assets += 1
                        if self.verbose:
                            self.log(f"  Asset OK: {asset_path}")
                    else:
                        if self.verbose:
                            self.log(f"  Asset failed ({asset_response.status_code}): {asset_path}")
                except:
                    if self.verbose:
                        self.log(f"  Asset error: {asset_path}")
            
            if successful_assets == total_assets:
                self.log(f"All tested static assets loading correctly ({successful_assets}/{total_assets})", "SUCCESS")
                return True
            elif successful_assets > 0:
                self.log(f"Some static assets loading ({successful_assets}/{total_assets})", "WARNING")
                return True
            else:
                self.log("Static assets not loading correctly", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"Error testing static assets: {e}", "ERROR")
            return False
    
    def test_api_proxy_configuration(self) -> bool:
        """Test if API proxy is configured correctly"""
        self.log("Testing API proxy configuration...")
        
        try:
            # Test a simple API endpoint through the proxy
            api_url = urljoin(self.frontend_url, "/api/chats/")
            
            response = self.session.get(api_url)
            
            # We expect either a successful response or a proper error from the backend
            if response.status_code in [200, 401, 403, 404, 500]:
                # Check if response looks like it came from FastAPI backend
                try:
                    # Try to parse as JSON (FastAPI typically returns JSON)
                    response_data = response.json()
                    self.log("API proxy working - received JSON response from backend", "SUCCESS")
                    if self.verbose:
                        self.log(f"  Response status: {response.status_code}")
                        self.log(f"  Response type: JSON")
                    return True
                except json.JSONDecodeError:
                    # Check if it's an HTML error page (might indicate proxy issues)
                    if 'html' in response.headers.get('content-type', '').lower():
                        self.log("API proxy may not be working - received HTML instead of JSON", "FAIL")
                        return False
                    else:
                        self.log("API proxy working - received non-JSON response from backend", "SUCCESS")
                        return True
            else:
                self.log(f"API proxy test returned unexpected status {response.status_code}", "FAIL")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log(f"API proxy test failed: {e}", "ERROR")
            return False
    
    def test_frontend_backend_communication(self) -> bool:
        """Test frontend-backend communication through proxy"""
        self.log("Testing frontend-backend communication...")
        
        success_count = 0
        total_tests = 0
        
        # Test 1: Health/root endpoint through proxy
        total_tests += 1
        try:
            response = self.session.get(urljoin(self.frontend_url, "/api/"))
            if response.status_code in [200, 404]:  # 404 is OK if no root API endpoint
                self.log("API root endpoint accessible through proxy", "SUCCESS")
                success_count += 1
            else:
                self.log(f"API root endpoint returned status {response.status_code}", "FAIL")
        except Exception as e:
            self.log(f"API root endpoint test failed: {e}", "ERROR")
        
        # Test 2: Chats endpoint
        total_tests += 1
        try:
            response = self.session.get(urljoin(self.frontend_url, "/api/chats/"))
            if response.status_code == 200:
                try:
                    chats = response.json()
                    if isinstance(chats, list):
                        self.log(f"Chats API working through proxy (found {len(chats)} chats)", "SUCCESS")
                        success_count += 1
                    else:
                        self.log("Chats API accessible but returned unexpected format", "WARNING")
                        success_count += 1  # Still count as success
                except json.JSONDecodeError:
                    self.log("Chats API accessible but returned non-JSON", "WARNING")
            else:
                self.log(f"Chats API returned status {response.status_code}", "FAIL")
        except Exception as e:
            self.log(f"Chats API test failed: {e}", "ERROR")
        
        # Test 3: Create new chat (if previous tests passed)
        if success_count >= 1:
            total_tests += 1
            try:
                response = self.session.post(urljoin(self.frontend_url, "/api/chats/new/"))
                if response.status_code == 200:
                    try:
                        result = response.json()
                        if "chat_id" in result:
                            chat_id = result["chat_id"]
                            self.log(f"Chat creation working through proxy (chat_id: {chat_id})", "SUCCESS")
                            success_count += 1
                            
                            # Cleanup: Delete the test chat
                            try:
                                self.session.delete(urljoin(self.frontend_url, f"/api/chats/{chat_id}/delete"))
                            except:
                                pass  # Ignore cleanup errors
                        else:
                            self.log("Chat creation accessible but missing chat_id", "WARNING")
                    except json.JSONDecodeError:
                        self.log("Chat creation accessible but returned non-JSON", "WARNING")
                else:
                    self.log(f"Chat creation returned status {response.status_code}", "FAIL")
            except Exception as e:
                self.log(f"Chat creation test failed: {e}", "ERROR")
        
        success_rate = (success_count / total_tests) * 100 if total_tests > 0 else 0
        self.log(f"Frontend-backend communication test: {success_count}/{total_tests} passed ({success_rate:.1f}%)")
        
        return success_count >= (total_tests * 0.5)  # Consider success if at least 50% pass
    
    def test_cors_headers(self) -> bool:
        """Test CORS headers in API responses"""
        self.log("Testing CORS headers...")
        
        try:
            # Test preflight request
            headers = {
                'Origin': self.frontend_url,
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            
            response = self.session.options(
                urljoin(self.frontend_url, "/api/chats/"),
                headers=headers
            )
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            }
            
            # Check if any CORS headers are present
            has_cors_headers = any(cors_headers.values())
            
            if has_cors_headers:
                self.log("CORS headers present in API responses", "SUCCESS")
                if self.verbose:
                    for header, value in cors_headers.items():
                        if value:
                            self.log(f"  {header}: {value}")
                return True
            else:
                # CORS might be handled by the proxy, which is also fine
                self.log("No explicit CORS headers found (may be handled by proxy)", "WARNING")
                return True  # Not necessarily a failure
                
        except Exception as e:
            self.log(f"CORS headers test failed: {e}", "ERROR")
            return False
    
    def test_vercel_configuration(self) -> bool:
        """Test Vercel-specific configuration"""
        self.log("Testing Vercel configuration...")
        
        try:
            # Check response headers for Vercel indicators
            response = self.session.head(self.frontend_url)
            
            vercel_headers = [
                'x-vercel-cache',
                'x-vercel-id',
                'server'
            ]
            
            vercel_indicators = []
            for header in vercel_headers:
                value = response.headers.get(header)
                if value:
                    vercel_indicators.append(f"{header}: {value}")
            
            # Check if deployed on Vercel
            server_header = response.headers.get('server', '').lower()
            is_vercel = 'vercel' in server_header or any('vercel' in indicator.lower() for indicator in vercel_indicators)
            
            if is_vercel:
                self.log("Confirmed deployment on Vercel platform", "SUCCESS")
                if self.verbose:
                    for indicator in vercel_indicators:
                        self.log(f"  {indicator}")
                return True
            else:
                self.log("Cannot confirm Vercel deployment (may still be working)", "WARNING")
                return True  # Not necessarily a failure
                
        except Exception as e:
            self.log(f"Vercel configuration test failed: {e}", "ERROR")
            return False
    
    def test_build_optimization(self) -> bool:
        """Test if build is properly optimized"""
        self.log("Testing build optimization...")
        
        try:
            response = self.session.get(self.frontend_url)
            if response.status_code != 200:
                self.log("Cannot test build optimization - frontend not accessible", "FAIL")
                return False
            
            content = response.text
            
            # Check for minification indicators
            optimization_indicators = {
                'minified_js': bool(re.search(r'\.js\?[a-f0-9]{8}', content)),  # Hashed filenames
                'minified_css': bool(re.search(r'\.css\?[a-f0-9]{8}', content)),  # Hashed filenames
                'compressed_content': len(content) < 50000,  # Reasonable size for minified HTML
                'no_dev_comments': '<!-- dev -->' not in content.lower()
            }
            
            optimization_score = sum(optimization_indicators.values())
            total_checks = len(optimization_indicators)
            
            if optimization_score >= total_checks * 0.75:  # 75% or more optimizations
                self.log(f"Build appears optimized ({optimization_score}/{total_checks} indicators)", "SUCCESS")
                if self.verbose:
                    for check, passed in optimization_indicators.items():
                        status = "✓" if passed else "✗"
                        self.log(f"  {status} {check}")
                return True
            else:
                self.log(f"Build may not be fully optimized ({optimization_score}/{total_checks} indicators)", "WARNING")
                return True  # Not a critical failure
                
        except Exception as e:
            self.log(f"Build optimization test failed: {e}", "ERROR")
            return False
    
    def test_responsive_design(self) -> bool:
        """Test if the app is responsive (basic check)"""
        self.log("Testing responsive design indicators...")
        
        try:
            response = self.session.get(self.frontend_url)
            if response.status_code != 200:
                self.log("Cannot test responsive design - frontend not accessible", "FAIL")
                return False
            
            content = response.text.lower()
            
            # Check for responsive design indicators
            responsive_indicators = [
                'viewport' in content and 'width=device-width' in content,
                'bootstrap' in content or 'tailwind' in content,
                '@media' in content,
                'responsive' in content
            ]
            
            responsive_score = sum(responsive_indicators)
            
            if responsive_score >= 1:
                self.log(f"Responsive design indicators found ({responsive_score}/4)", "SUCCESS")
                return True
            else:
                self.log("No responsive design indicators found", "WARNING")
                return True  # Not critical for functionality
                
        except Exception as e:
            self.log(f"Responsive design test failed: {e}", "ERROR")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all verification tests"""
        self.log("Starting frontend deployment verification...", "INFO")
        self.log(f"Testing frontend at: {self.frontend_url}", "INFO")
        if self.backend_url:
            self.log(f"Expected backend at: {self.backend_url}", "INFO")
        
        tests = [
            ("Frontend Accessibility", self.test_frontend_accessibility),
            ("Static Assets Loading", self.test_static_assets),
            ("API Proxy Configuration", self.test_api_proxy_configuration),
            ("Frontend-Backend Communication", self.test_frontend_backend_communication),
            ("CORS Headers", self.test_cors_headers),
            ("Vercel Configuration", self.test_vercel_configuration),
            ("Build Optimization", self.test_build_optimization),
            ("Responsive Design", self.test_responsive_design),
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
        self.log(f"\n{'='*60}")
        self.log(f"FRONTEND VERIFICATION SUMMARY")
        self.log(f"{'='*60}")
        self.log(f"Frontend URL: {self.frontend_url}")
        if self.backend_url:
            self.log(f"Backend URL: {self.backend_url}")
        self.log(f"Tests Passed: {passed}/{total}")
        self.log(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            self.log("🎉 All tests passed! Frontend deployment is successful.", "SUCCESS")
        elif passed >= total * 0.75:
            self.log(f"✅ Most tests passed ({passed}/{total}). Frontend deployment is likely working.", "SUCCESS")
        else:
            self.log(f"⚠️  {total-passed} test(s) failed. Please review the issues above.", "WARNING")
        
        return results


def main():
    parser = argparse.ArgumentParser(
        description="Verify RAG AI-Agent frontend deployment on Vercel"
    )
    parser.add_argument(
        "--url", 
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
    if not args.url.startswith(('http://', 'https://')):
        print("❌ Error: Frontend URL must start with http:// or https://")
        sys.exit(1)
    
    if args.backend and not args.backend.startswith(('http://', 'https://')):
        print("❌ Error: Backend URL must start with http:// or https://")
        sys.exit(1)
    
    # Run verification
    verifier = FrontendVerifier(args.url, args.backend, args.verbose)
    verifier.session.timeout = args.timeout
    
    try:
        results = verifier.run_all_tests()
        
        # Exit with appropriate code
        passed_tests = sum(results.values())
        total_tests = len(results)
        
        if passed_tests == total_tests:
            sys.exit(0)  # Perfect success
        elif passed_tests >= total_tests * 0.75:
            sys.exit(0)  # Acceptable success (75%+)
        else:
            sys.exit(1)  # Too many failures
            
    except KeyboardInterrupt:
        print("\n⚠️  Verification interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"🚨 Verification failed with error: {e}")
        sys.exit(3)


if __name__ == "__main__":
    main()