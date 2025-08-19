#!/usr/bin/env python3
"""
Simple Health Check Script for RAG AI-Agent Backend

This script performs a quick health check of the deployed backend to ensure
it's running and accessible.

Usage:
    python health_check.py https://your-space.hf.space
"""

import sys
import requests
from urllib.parse import urljoin


def health_check(base_url: str) -> bool:
    """Perform a simple health check of the backend"""
    
    print(f"🔍 Checking backend health at: {base_url}")
    
    try:
        # Test basic connectivity
        response = requests.get(base_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Backend is accessible")
            
            # Test API documentation endpoint
            docs_response = requests.get(urljoin(base_url, "/docs"), timeout=10)
            if docs_response.status_code == 200:
                print("✅ API documentation is accessible")
                
                # Test a simple API endpoint
                chats_response = requests.get(urljoin(base_url, "/api/chats/"), timeout=10)
                if chats_response.status_code == 200:
                    print("✅ API endpoints are responding")
                    print("🎉 Backend health check passed!")
                    return True
                else:
                    print(f"❌ API endpoints not responding (status: {chats_response.status_code})")
            else:
                print(f"❌ API documentation not accessible (status: {docs_response.status_code})")
        else:
            print(f"❌ Backend not accessible (status: {response.status_code})")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out - backend may be starting up or overloaded")
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - check if the URL is correct and backend is deployed")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    return False


def main():
    if len(sys.argv) != 2:
        print("Usage: python health_check.py <backend_url>")
        print("Example: python health_check.py https://your-username-your-space.hf.space")
        sys.exit(1)
    
    backend_url = sys.argv[1].rstrip('/')
    
    if not backend_url.startswith(('http://', 'https://')):
        print("❌ Error: URL must start with http:// or https://")
        sys.exit(1)
    
    success = health_check(backend_url)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()