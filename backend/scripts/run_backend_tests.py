#!/usr/bin/env python3
"""
Backend Test Runner for RAG AI-Agent

This script provides a simple interface to run various backend verification tests.

Usage:
    python run_backend_tests.py --url https://your-space.hf.space
    python run_backend_tests.py --url https://your-space.hf.space --quick
    python run_backend_tests.py --url https://your-space.hf.space --full
"""

import argparse
import sys
import subprocess
import os
from pathlib import Path


def run_health_check(backend_url: str) -> bool:
    """Run simple health check"""
    print("🏥 Running health check...")
    
    script_path = Path(__file__).parent / "health_check.py"
    
    try:
        result = subprocess.run([
            sys.executable, str(script_path), backend_url
        ], capture_output=True, text=True, timeout=60)
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ Health check timed out")
        return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def run_fastapi_tests(backend_url: str, test_cors: bool = False) -> bool:
    """Run FastAPI-specific tests"""
    print("⚡ Running FastAPI deployment tests...")
    
    script_path = Path(__file__).parent / "test_fastapi_deployment.py"
    
    cmd = [sys.executable, str(script_path), "--url", backend_url]
    if test_cors:
        cmd.append("--test-cors")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ FastAPI tests timed out")
        return False
    except Exception as e:
        print(f"❌ FastAPI tests failed: {e}")
        return False


def run_comprehensive_verification(backend_url: str, verbose: bool = False) -> bool:
    """Run comprehensive backend verification"""
    print("🔍 Running comprehensive backend verification...")
    
    script_path = Path(__file__).parent / "verify_backend_deployment.py"
    
    cmd = [sys.executable, str(script_path), "--url", backend_url]
    if verbose:
        cmd.append("--verbose")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ Comprehensive verification timed out")
        return False
    except Exception as e:
        print(f"❌ Comprehensive verification failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Run backend verification tests for RAG AI-Agent"
    )
    parser.add_argument(
        "--url",
        required=True,
        help="Backend URL (e.g., https://your-username-your-space.hf.space)"
    )
    
    test_group = parser.add_mutually_exclusive_group()
    test_group.add_argument(
        "--quick",
        action="store_true",
        help="Run quick health check only"
    )
    test_group.add_argument(
        "--full",
        action="store_true",
        help="Run comprehensive verification with all tests"
    )
    
    parser.add_argument(
        "--test-cors",
        action="store_true",
        help="Include CORS testing in FastAPI tests"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output for comprehensive tests"
    )
    
    args = parser.parse_args()
    
    # Validate URL
    if not args.url.startswith(('http://', 'https://')):
        print("❌ Error: URL must start with http:// or https://")
        sys.exit(1)
    
    print("🚀 RAG AI-Agent Backend Test Runner")
    print(f"🎯 Target: {args.url}")
    print("=" * 60)
    
    success = True
    
    if args.quick:
        # Quick health check only
        success = run_health_check(args.url)
        
    elif args.full:
        # Comprehensive verification
        success = run_comprehensive_verification(args.url, args.verbose)
        
    else:
        # Default: Run health check + FastAPI tests
        print("Running default test suite (health check + FastAPI tests)...\n")
        
        # Health check first
        health_ok = run_health_check(args.url)
        print()
        
        # FastAPI tests
        fastapi_ok = run_fastapi_tests(args.url, args.test_cors)
        
        success = health_ok and fastapi_ok
    
    # Final summary
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests completed successfully!")
        print("✅ Backend deployment verification passed.")
    else:
        print("⚠️  Some tests failed or had issues.")
        print("❌ Please review the output above for details.")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()