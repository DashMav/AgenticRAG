#!/usr/bin/env python3
"""
API Key Validation Script for RAG AI-Agent

This script validates API connectivity for Groq, OpenAI, and Pinecone services.
It includes proper error handling and configuration file support.

Usage:
    python scripts/validate_api_keys.py
    python scripts/validate_api_keys.py --config config.json

Requirements:
    - API keys set in environment variables or config file
    - Internet connection for API testing
    - Required Python packages installed
"""

import os
import sys
import json
import argparse
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

@dataclass
class APIConfig:
    """Configuration for API services."""
    groq_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    pinecone_api_key: Optional[str] = None
    pinecone_index_name: Optional[str] = None
    pinecone_environment: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'APIConfig':
        """Load configuration from environment variables."""
        return cls(
            groq_api_key=os.getenv('GROQ_API_KEY'),
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            pinecone_api_key=os.getenv('PINECONE_API_KEY'),
            pinecone_index_name=os.getenv('PINECONE_INDEX_NAME'),
            pinecone_environment=os.getenv('PINECONE_ENVIRONMENT')
        )
    
    @classmethod
    def from_file(cls, config_path: str) -> 'APIConfig':
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            return cls(
                groq_api_key=config_data.get('groq_api_key'),
                openai_api_key=config_data.get('openai_api_key'),
                pinecone_api_key=config_data.get('pinecone_api_key'),
                pinecone_index_name=config_data.get('pinecone_index_name'),
                pinecone_environment=config_data.get('pinecone_environment')
            )
        except FileNotFoundError:
            print_error(f"Configuration file not found: {config_path}")
            return cls()
        except json.JSONDecodeError as e:
            print_error(f"Invalid JSON in configuration file: {e}")
            return cls()
        except Exception as e:
            print_error(f"Error loading configuration file: {e}")
            return cls()

@dataclass
class ValidationResult:
    """Result of API validation."""
    service_name: str
    status: bool
    message: str
    details: Optional[Dict] = None

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

class APIKeyValidator:
    """Validates API keys for various services."""
    
    def __init__(self, config: APIConfig):
        self.config = config
    
    def validate_groq_api(self) -> ValidationResult:
        """Validate Groq API connectivity."""
        if not self.config.groq_api_key:
            return ValidationResult(
                service_name="Groq",
                status=False,
                message="API key not provided"
            )
        
        try:
            from groq import Groq
            
            client = Groq(api_key=self.config.groq_api_key)
            
            # Test with a minimal completion request
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": "test"}],
                model="llama3-8b-8192",
                max_tokens=1
            )
            
            if response.choices:
                return ValidationResult(
                    service_name="Groq",
                    status=True,
                    message="API connection successful",
                    details={"model": "llama3-8b-8192", "response_received": True}
                )
            else:
                return ValidationResult(
                    service_name="Groq",
                    status=False,
                    message="No response received from API"
                )
                
        except ImportError:
            return ValidationResult(
                service_name="Groq",
                status=False,
                message="groq package not installed. Run: pip install groq"
            )
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "unauthorized" in error_msg.lower():
                return ValidationResult(
                    service_name="Groq",
                    status=False,
                    message="Invalid API key or unauthorized access"
                )
            elif "429" in error_msg or "rate limit" in error_msg.lower():
                return ValidationResult(
                    service_name="Groq",
                    status=False,
                    message="Rate limit exceeded. Try again later."
                )
            else:
                return ValidationResult(
                    service_name="Groq",
                    status=False,
                    message=f"API error: {error_msg}"
                )
    
    def validate_openai_api(self) -> ValidationResult:
        """Validate OpenAI API connectivity."""
        if not self.config.openai_api_key:
            return ValidationResult(
                service_name="OpenAI",
                status=False,
                message="API key not provided"
            )
        
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.config.openai_api_key)
            
            # Test with a minimal embedding request
            response = client.embeddings.create(
                input="test",
                model="text-embedding-ada-002"
            )
            
            if response.data and len(response.data) > 0:
                embedding_dim = len(response.data[0].embedding)
                return ValidationResult(
                    service_name="OpenAI",
                    status=True,
                    message="API connection successful",
                    details={
                        "model": "text-embedding-ada-002",
                        "embedding_dimension": embedding_dim,
                        "response_received": True
                    }
                )
            else:
                return ValidationResult(
                    service_name="OpenAI",
                    status=False,
                    message="No embedding data received from API"
                )
                
        except ImportError:
            return ValidationResult(
                service_name="OpenAI",
                status=False,
                message="openai package not installed. Run: pip install openai"
            )
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "unauthorized" in error_msg.lower():
                return ValidationResult(
                    service_name="OpenAI",
                    status=False,
                    message="Invalid API key or unauthorized access"
                )
            elif "429" in error_msg or "rate limit" in error_msg.lower():
                return ValidationResult(
                    service_name="OpenAI",
                    status=False,
                    message="Rate limit exceeded. Try again later."
                )
            elif "quota" in error_msg.lower():
                return ValidationResult(
                    service_name="OpenAI",
                    status=False,
                    message="API quota exceeded. Check your billing."
                )
            else:
                return ValidationResult(
                    service_name="OpenAI",
                    status=False,
                    message=f"API error: {error_msg}"
                )
    
    def validate_pinecone_api(self) -> ValidationResult:
        """Validate Pinecone API connectivity."""
        if not self.config.pinecone_api_key:
            return ValidationResult(
                service_name="Pinecone",
                status=False,
                message="API key not provided"
            )
        
        if not self.config.pinecone_index_name:
            return ValidationResult(
                service_name="Pinecone",
                status=False,
                message="Index name not provided"
            )
        
        try:
            from pinecone import Pinecone
            
            pc = Pinecone(api_key=self.config.pinecone_api_key)
            
            # List indexes to test connection
            indexes = pc.list_indexes()
            index_names = [idx.name for idx in indexes]
            
            # Check if our index exists
            if self.config.pinecone_index_name in index_names:
                # Test index connection and get stats
                index = pc.Index(self.config.pinecone_index_name)
                stats = index.describe_index_stats()
                
                return ValidationResult(
                    service_name="Pinecone",
                    status=True,
                    message=f"API connection successful, index '{self.config.pinecone_index_name}' found",
                    details={
                        "index_name": self.config.pinecone_index_name,
                        "total_vectors": stats.total_vector_count,
                        "dimension": stats.dimension,
                        "available_indexes": index_names
                    }
                )
            else:
                return ValidationResult(
                    service_name="Pinecone",
                    status=False,
                    message=f"Index '{self.config.pinecone_index_name}' not found",
                    details={"available_indexes": index_names}
                )
                
        except ImportError:
            return ValidationResult(
                service_name="Pinecone",
                status=False,
                message="pinecone-client package not installed. Run: pip install pinecone-client"
            )
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "unauthorized" in error_msg.lower():
                return ValidationResult(
                    service_name="Pinecone",
                    status=False,
                    message="Invalid API key or unauthorized access"
                )
            elif "403" in error_msg or "forbidden" in error_msg.lower():
                return ValidationResult(
                    service_name="Pinecone",
                    status=False,
                    message="Access forbidden. Check API key permissions."
                )
            else:
                return ValidationResult(
                    service_name="Pinecone",
                    status=False,
                    message=f"API error: {error_msg}"
                )
    
    def validate_all(self) -> Dict[str, ValidationResult]:
        """Validate all API services."""
        results = {}
        
        print_header("API KEY VALIDATION")
        
        # Validate each service
        services = [
            ("groq", self.validate_groq_api),
            ("openai", self.validate_openai_api),
            ("pinecone", self.validate_pinecone_api)
        ]
        
        for service_key, validator_func in services:
            result = validator_func()
            results[service_key] = result
            
            if result.status:
                print_success(f"{result.service_name}: {result.message}")
                if result.details:
                    for key, value in result.details.items():
                        print_info(f"  {key}: {value}")
            else:
                print_error(f"{result.service_name}: {result.message}")
                if result.details:
                    for key, value in result.details.items():
                        print_info(f"  {key}: {value}")
        
        return results

def create_sample_config(config_path: str):
    """Create a sample configuration file."""
    sample_config = {
        "groq_api_key": "your_groq_api_key_here",
        "openai_api_key": "your_openai_api_key_here",
        "pinecone_api_key": "your_pinecone_api_key_here",
        "pinecone_index_name": "your_pinecone_index_name",
        "pinecone_environment": "your_pinecone_environment"
    }
    
    try:
        with open(config_path, 'w') as f:
            json.dump(sample_config, f, indent=2)
        print_success(f"Sample configuration file created: {config_path}")
        print_info("Please update the file with your actual API keys.")
    except Exception as e:
        print_error(f"Failed to create sample config: {e}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Validate API keys for RAG AI-Agent")
    parser.add_argument(
        "--config", 
        type=str, 
        help="Path to configuration JSON file"
    )
    parser.add_argument(
        "--create-sample-config",
        type=str,
        help="Create a sample configuration file at the specified path"
    )
    
    args = parser.parse_args()
    
    # Create sample config if requested
    if args.create_sample_config:
        create_sample_config(args.create_sample_config)
        return 0
    
    print(f"{Colors.BOLD}RAG AI-Agent API Key Validation{Colors.END}")
    print("This script validates API connectivity for all required services.\n")
    
    # Load configuration
    if args.config:
        print_info(f"Loading configuration from: {args.config}")
        config = APIConfig.from_file(args.config)
    else:
        print_info("Loading configuration from environment variables")
        config = APIConfig.from_env()
    
    # Validate APIs
    validator = APIKeyValidator(config)
    results = validator.validate_all()
    
    # Summary
    print_header("VALIDATION SUMMARY")
    
    successful_services = [name for name, result in results.items() if result.status]
    failed_services = [name for name, result in results.items() if not result.status]
    
    if len(successful_services) == len(results):
        print_success("All API services validated successfully! ✨")
        print_info("Your API keys are working correctly.")
    elif successful_services:
        print_warning(f"Partial success: {len(successful_services)}/{len(results)} services validated")
        print_success(f"Working services: {', '.join(successful_services)}")
        print_error(f"Failed services: {', '.join(failed_services)}")
    else:
        print_error("All API validations failed! ❌")
        print_info("Please check your API keys and network connection.")
    
    print_info("\nFor detailed setup instructions, see:")
    print_info("- ENVIRONMENT_VARIABLES.md")
    print_info("- DEPLOYMENT_GUIDE.md")
    
    return 0 if len(failed_services) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())