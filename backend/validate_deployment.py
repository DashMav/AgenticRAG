#!/usr/bin/env python3
"""
RAG AI-Agent Deployment Validation Script

This script validates that all required environment variables and services
are properly configured for deployment.

Usage:
    python validate_deployment.py

Requirements:
    - All required environment variables set
    - Internet connection for API testing
    - Required Python packages installed
"""

import os
import sys
import requests
from typing import Dict, List, Tuple
import json

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text.center(60)}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}\n")

def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_info(text: str):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def check_environment_variables() -> Tuple[bool, List[str]]:
    """Check if all required environment variables are set."""
    print_header("ENVIRONMENT VARIABLES CHECK")
    
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
    
    missing_vars = []
    
    # Check required variables
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask the API key for security
            masked_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            print_success(f"{var}: {masked_value}")
        else:
            print_error(f"{var}: Not set")
            missing_vars.append(var)
    
    # Check optional variables
    print(f"\n{Colors.BOLD}Optional Variables:{Colors.END}")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print_success(f"{var}: {value}")
        else:
            print_info(f"{var}: Not set (using default)")
    
    return len(missing_vars) == 0, missing_vars

def test_groq_api() -> bool:
    """Test Groq API connectivity."""
    try:
        from groq import Groq
        
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            print_error("Groq API key not found")
            return False
        
        client = Groq(api_key=api_key)
        
        # Test with a simple completion
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": "Hello"}],
            model="llama3-8b-8192",
            max_tokens=10
        )
        
        if response.choices:
            print_success("Groq API: Connection successful")
            return True
        else:
            print_error("Groq API: No response received")
            return False
            
    except ImportError:
        print_error("Groq API: groq package not installed")
        return False
    except Exception as e:
        print_error(f"Groq API: {str(e)}")
        return False

def test_openai_api() -> bool:
    """Test OpenAI API connectivity."""
    try:
        import openai
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print_error("OpenAI API key not found")
            return False
        
        client = openai.OpenAI(api_key=api_key)
        
        # Test with a simple embedding request
        response = client.embeddings.create(
            input="test",
            model="text-embedding-ada-002"
        )
        
        if response.data:
            print_success("OpenAI API: Connection successful")
            return True
        else:
            print_error("OpenAI API: No response received")
            return False
            
    except ImportError:
        print_error("OpenAI API: openai package not installed")
        return False
    except Exception as e:
        print_error(f"OpenAI API: {str(e)}")
        return False

def test_pinecone_api() -> bool:
    """Test Pinecone API connectivity."""
    try:
        from pinecone import Pinecone
        
        api_key = os.getenv('PINECONE_API_KEY')
        index_name = os.getenv('PINECONE_INDEX_NAME')
        
        if not api_key:
            print_error("Pinecone API key not found")
            return False
        
        if not index_name:
            print_error("Pinecone index name not found")
            return False
        
        pc = Pinecone(api_key=api_key)
        
        # List indexes to test connection
        indexes = pc.list_indexes()
        
        # Check if our index exists
        index_exists = any(idx.name == index_name for idx in indexes)
        
        if index_exists:
            print_success(f"Pinecone API: Connection successful, index '{index_name}' found")
            
            # Test index connection
            index = pc.Index(index_name)
            stats = index.describe_index_stats()
            print_info(f"Index stats: {stats.total_vector_count} vectors")
            return True
        else:
            print_error(f"Pinecone API: Index '{index_name}' not found")
            available_indexes = [idx.name for idx in indexes]
            if available_indexes:
                print_info(f"Available indexes: {', '.join(available_indexes)}")
            return False
            
    except ImportError:
        print_error("Pinecone API: pinecone-client package not installed")
        return False
    except Exception as e:
        print_error(f"Pinecone API: {str(e)}")
        return False

def test_api_services() -> Tuple[bool, Dict[str, bool]]:
    """Test all API services."""
    print_header("API SERVICES CHECK")
    
    services = {
        'Groq': test_groq_api(),
        'OpenAI': test_openai_api(),
        'Pinecone': test_pinecone_api()
    }
    
    all_services_ok = all(services.values())
    return all_services_ok, services

def check_local_dependencies() -> bool:
    """Check if required Python packages are installed."""
    print_header("DEPENDENCIES CHECK")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'openai',
        'groq',
        'pinecone-client',
        'langchain',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print_success(f"{package}: Installed")
        except ImportError:
            print_error(f"{package}: Not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print_warning(f"\nTo install missing packages, run:")
        print_warning(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_file_structure() -> bool:
    """Check if required files exist."""
    print_header("FILE STRUCTURE CHECK")
    
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
            print_success(f"{file_path}: Found")
        else:
            print_error(f"{file_path}: Missing")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def validate_vercel_config() -> bool:
    """Validate Vercel configuration."""
    print_header("VERCEL CONFIGURATION CHECK")
    
    vercel_config_path = 'agent-frontend/vercel.json'
    
    if not os.path.exists(vercel_config_path):
        print_error("vercel.json not found")
        return False
    
    try:
        with open(vercel_config_path, 'r') as f:
            config = json.load(f)
        
        if 'rewrites' in config:
            rewrites = config['rewrites']
            if rewrites and len(rewrites) > 0:
                destination = rewrites[0].get('destination', '')
                if 'hf.space' in destination:
                    print_success("Vercel config: Backend URL configured for Hugging Face Spaces")
                    return True
                else:
                    print_warning("Vercel config: Backend URL may need updating for production")
                    print_info(f"Current destination: {destination}")
                    return True
            else:
                print_error("Vercel config: No rewrites configured")
                return False
        else:
            print_error("Vercel config: No rewrites section found")
            return False
            
    except json.JSONDecodeError:
        print_error("Vercel config: Invalid JSON format")
        return False
    except Exception as e:
        print_error(f"Vercel config: {str(e)}")
        return False

def main():
    """Main validation function."""
    print(f"{Colors.BOLD}RAG AI-Agent Deployment Validation{Colors.END}")
    print("This script will validate your deployment configuration.\n")
    
    # Track overall status
    all_checks_passed = True
    
    # Check environment variables
    env_ok, missing_vars = check_environment_variables()
    if not env_ok:
        all_checks_passed = False
        print_error(f"\nMissing environment variables: {', '.join(missing_vars)}")
        print_info("Please set these variables before proceeding with deployment.")
    
    # Check dependencies
    deps_ok = check_local_dependencies()
    if not deps_ok:
        all_checks_passed = False
    
    # Check file structure
    files_ok = check_file_structure()
    if not files_ok:
        all_checks_passed = False
    
    # Check Vercel configuration
    vercel_ok = validate_vercel_config()
    if not vercel_ok:
        all_checks_passed = False
    
    # Test API services (only if environment variables are set)
    if env_ok:
        services_ok, service_results = test_api_services()
        if not services_ok:
            all_checks_passed = False
            failed_services = [name for name, status in service_results.items() if not status]
            print_error(f"\nFailed API services: {', '.join(failed_services)}")
    else:
        print_warning("\nSkipping API service tests due to missing environment variables.")
    
    # Final summary
    print_header("VALIDATION SUMMARY")
    
    if all_checks_passed:
        print_success("All validation checks passed! ✨")
        print_success("Your deployment configuration looks good.")
        print_info("\nNext steps:")
        print_info("1. Deploy backend to Hugging Face Spaces")
        print_info("2. Update vercel.json with your backend URL")
        print_info("3. Deploy frontend to Vercel")
        print_info("4. Test the deployed application")
    else:
        print_error("Some validation checks failed. ❌")
        print_error("Please address the issues above before deploying.")
        print_info("\nFor detailed deployment instructions, see:")
        print_info("- DEPLOYMENT_GUIDE.md")
        print_info("- DEPLOYMENT_CHECKLIST.md")
        print_info("- ENVIRONMENT_VARIABLES.md")
    
    return 0 if all_checks_passed else 1

if __name__ == "__main__":
    sys.exit(main())