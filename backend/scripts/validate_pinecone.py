#!/usr/bin/env python3
"""
Simple Pinecone Validation Script

This script provides a quick way to validate your Pinecone configuration
and test connectivity without additional command-line arguments.

Usage:
    python validate_pinecone.py

Requirements: 2.2, 2.4
"""

import os
import sys
from datetime import datetime

# Add the parent directory to the path to import pinecone_utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from scripts.pinecone_utilities import PineconeValidator, PineconeConfig, generate_validation_report
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the RAG-AI-Agent directory and have installed dependencies:")
    print("pip install pinecone-client langchain-openai langchain-pinecone python-dotenv")
    sys.exit(1)

def main():
    """Run Pinecone validation with default settings"""
    print("🔍 Pinecone Configuration Validator")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Create configuration from environment variables
    config = PineconeConfig(
        api_key=os.getenv('PINECONE_API_KEY', ''),
        index_name=os.getenv('PINECONE_INDEX_NAME', 'rag-ai-agent'),
        dimension=int(os.getenv('PINECONE_DIMENSION', '1536')),
        metric=os.getenv('PINECONE_METRIC', 'cosine')
    )
    
    print(f"📋 Configuration:")
    print(f"   - Index Name: {config.index_name}")
    print(f"   - Dimensions: {config.dimension}")
    print(f"   - Metric: {config.metric}")
    print(f"   - API Key: {'Set' if config.api_key else 'Not Set'}")
    print()
    
    # Run validation
    validator = PineconeValidator(config)
    results = validator.run_all_validations()
    
    # Generate report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"pinecone_validation_report_{timestamp}.md"
    
    print(f"\n📄 Generating detailed report...")
    generate_validation_report(results, report_file)
    
    # Print summary
    passed = sum(1 for r in results if r.status)
    total = len(results)
    
    print(f"\n📊 Final Summary:")
    print(f"   - Total Checks: {total}")
    print(f"   - Passed: {passed}")
    print(f"   - Failed: {total - passed}")
    print(f"   - Success Rate: {(passed/total*100):.1f}%" if total > 0 else "   - Success Rate: N/A")
    
    if passed == total:
        print("\n🎉 SUCCESS: All validations passed!")
        print("   Your Pinecone configuration is ready for production use.")
        print(f"   Detailed report saved to: {report_file}")
        return 0
    else:
        print(f"\n⚠️ WARNING: {total - passed} validation(s) failed.")
        print("   Please review the issues above and fix them before deployment.")
        print(f"   Detailed report saved to: {report_file}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)