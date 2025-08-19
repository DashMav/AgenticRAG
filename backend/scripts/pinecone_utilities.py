#!/usr/bin/env python3
"""
Pinecone Migration and Validation Utilities

This script provides utilities for:
1. Verifying existing Pinecone index configuration
2. Testing Pinecone connectivity and operations
3. Implementing data validation for vector database operations
4. Migrating data from ChromaDB to Pinecone (if needed)

Requirements: 2.2, 2.4
"""

import os
import sys
import json
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

try:
    from pinecone import Pinecone, ServerlessSpec
    from langchain_openai import OpenAIEmbeddings
    from langchain_pinecone import Pinecone as LangchainPinecone
    import openai
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Missing required dependencies: {e}")
    print("Install with: pip install pinecone-client langchain-openai langchain-pinecone python-dotenv")
    sys.exit(1)

# Load environment variables
load_dotenv()

@dataclass
class PineconeConfig:
    """Configuration for Pinecone connection"""
    api_key: str
    index_name: str
    dimension: int = 1536
    metric: str = "cosine"
    environment: Optional[str] = None

@dataclass
class ValidationResult:
    """Result of a validation check"""
    check_name: str
    status: bool
    message: str
    details: Optional[Dict] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class PineconeValidator:
    """Validates Pinecone configuration and connectivity"""
    
    def __init__(self, config: PineconeConfig):
        self.config = config
        self.pc = None
        self.index = None
        self.results: List[ValidationResult] = []
    
    def validate_environment_variables(self) -> ValidationResult:
        """Validate that all required environment variables are set"""
        required_vars = {
            'PINECONE_API_KEY': 'Pinecone API key',
            'PINECONE_INDEX_NAME': 'Pinecone index name',
            'OPENAI_API_KEY': 'OpenAI API key for embeddings'
        }
        
        missing_vars = []
        for var, description in required_vars.items():
            if not os.getenv(var):
                missing_vars.append(f"{var} ({description})")
        
        if missing_vars:
            return ValidationResult(
                check_name="Environment Variables",
                status=False,
                message=f"Missing required environment variables: {', '.join(missing_vars)}",
                details={"missing_variables": missing_vars}
            )
        
        return ValidationResult(
            check_name="Environment Variables",
            status=True,
            message="All required environment variables are set",
            details={"validated_variables": list(required_vars.keys())}
        )
    
    def validate_api_key(self) -> ValidationResult:
        """Validate Pinecone API key format and accessibility"""
        if not self.config.api_key:
            return ValidationResult(
                check_name="API Key Validation",
                status=False,
                message="Pinecone API key is not provided"
            )
        
        if not self.config.api_key.startswith('pcsk_'):
            return ValidationResult(
                check_name="API Key Validation",
                status=False,
                message="Pinecone API key should start with 'pcsk_'",
                details={"provided_prefix": self.config.api_key[:10] + "..."}
            )
        
        try:
            self.pc = Pinecone(api_key=self.config.api_key)
            # Test API key by listing indexes
            indexes = self.pc.list_indexes()
            
            return ValidationResult(
                check_name="API Key Validation",
                status=True,
                message="Pinecone API key is valid and accessible",
                details={"available_indexes": [idx.name for idx in indexes]}
            )
        
        except Exception as e:
            return ValidationResult(
                check_name="API Key Validation",
                status=False,
                message=f"Failed to authenticate with Pinecone: {str(e)}",
                details={"error_type": type(e).__name__}
            )
    
    def validate_index_existence(self) -> ValidationResult:
        """Check if the specified index exists"""
        if not self.pc:
            return ValidationResult(
                check_name="Index Existence",
                status=False,
                message="Pinecone client not initialized"
            )
        
        try:
            indexes = self.pc.list_indexes()
            index_names = [idx.name for idx in indexes]
            
            if self.config.index_name not in index_names:
                return ValidationResult(
                    check_name="Index Existence",
                    status=False,
                    message=f"Index '{self.config.index_name}' not found",
                    details={
                        "available_indexes": index_names,
                        "requested_index": self.config.index_name
                    }
                )
            
            return ValidationResult(
                check_name="Index Existence",
                status=True,
                message=f"Index '{self.config.index_name}' exists and is accessible",
                details={"index_name": self.config.index_name}
            )
        
        except Exception as e:
            return ValidationResult(
                check_name="Index Existence",
                status=False,
                message=f"Failed to check index existence: {str(e)}",
                details={"error_type": type(e).__name__}
            )
    
    def validate_index_configuration(self) -> ValidationResult:
        """Validate index configuration (dimensions, metric, etc.)"""
        if not self.pc:
            return ValidationResult(
                check_name="Index Configuration",
                status=False,
                message="Pinecone client not initialized"
            )
        
        try:
            self.index = self.pc.Index(self.config.index_name)
            stats = self.index.describe_index_stats()
            
            # Get index description for configuration details
            index_description = None
            for idx in self.pc.list_indexes():
                if idx.name == self.config.index_name:
                    index_description = idx
                    break
            
            validation_issues = []
            config_details = {
                "index_stats": stats,
                "expected_dimension": self.config.dimension,
                "expected_metric": self.config.metric
            }
            
            # Check dimensions if vectors exist
            if stats.get('total_vector_count', 0) > 0:
                actual_dimension = stats.get('dimension')
                if actual_dimension and actual_dimension != self.config.dimension:
                    validation_issues.append(
                        f"Dimension mismatch: expected {self.config.dimension}, got {actual_dimension}"
                    )
                config_details["actual_dimension"] = actual_dimension
            
            # Add index description details if available
            if index_description:
                config_details["index_description"] = {
                    "name": index_description.name,
                    "dimension": getattr(index_description, 'dimension', 'unknown'),
                    "metric": getattr(index_description, 'metric', 'unknown')
                }
            
            if validation_issues:
                return ValidationResult(
                    check_name="Index Configuration",
                    status=False,
                    message=f"Index configuration issues: {'; '.join(validation_issues)}",
                    details=config_details
                )
            
            return ValidationResult(
                check_name="Index Configuration",
                status=True,
                message="Index configuration is valid",
                details=config_details
            )
        
        except Exception as e:
            return ValidationResult(
                check_name="Index Configuration",
                status=False,
                message=f"Failed to validate index configuration: {str(e)}",
                details={"error_type": type(e).__name__}
            )
    
    def test_vector_operations(self) -> ValidationResult:
        """Test basic vector operations (upsert, query, delete)"""
        if not self.index:
            return ValidationResult(
                check_name="Vector Operations",
                status=False,
                message="Index not initialized"
            )
        
        try:
            # Create test vectors
            test_vectors = [
                {
                    "id": "test-vector-1",
                    "values": [0.1] * self.config.dimension,
                    "metadata": {"test": True, "type": "validation"}
                },
                {
                    "id": "test-vector-2", 
                    "values": [0.2] * self.config.dimension,
                    "metadata": {"test": True, "type": "validation"}
                }
            ]
            
            operations_results = {}
            
            # Test upsert
            try:
                upsert_response = self.index.upsert(vectors=test_vectors)
                operations_results["upsert"] = {
                    "status": "success",
                    "upserted_count": upsert_response.get('upserted_count', len(test_vectors))
                }
                
                # Wait for vectors to be indexed
                time.sleep(2)
                
            except Exception as e:
                operations_results["upsert"] = {
                    "status": "failed",
                    "error": str(e)
                }
                raise e
            
            # Test query
            try:
                query_response = self.index.query(
                    vector=[0.1] * self.config.dimension,
                    top_k=2,
                    include_metadata=True,
                    filter={"test": True}
                )
                
                operations_results["query"] = {
                    "status": "success",
                    "matches_count": len(query_response.get('matches', [])),
                    "top_score": query_response.get('matches', [{}])[0].get('score', 0) if query_response.get('matches') else 0
                }
                
            except Exception as e:
                operations_results["query"] = {
                    "status": "failed",
                    "error": str(e)
                }
            
            # Test delete (cleanup)
            try:
                delete_response = self.index.delete(
                    ids=["test-vector-1", "test-vector-2"]
                )
                operations_results["delete"] = {
                    "status": "success"
                }
                
            except Exception as e:
                operations_results["delete"] = {
                    "status": "failed",
                    "error": str(e)
                }
            
            # Check if all operations succeeded
            failed_operations = [op for op, result in operations_results.items() 
                               if result["status"] == "failed"]
            
            if failed_operations:
                return ValidationResult(
                    check_name="Vector Operations",
                    status=False,
                    message=f"Failed operations: {', '.join(failed_operations)}",
                    details=operations_results
                )
            
            return ValidationResult(
                check_name="Vector Operations",
                status=True,
                message="All vector operations completed successfully",
                details=operations_results
            )
        
        except Exception as e:
            return ValidationResult(
                check_name="Vector Operations",
                status=False,
                message=f"Vector operations test failed: {str(e)}",
                details={"error_type": type(e).__name__}
            )
    
    def validate_openai_integration(self) -> ValidationResult:
        """Test OpenAI embeddings integration"""
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            return ValidationResult(
                check_name="OpenAI Integration",
                status=False,
                message="OpenAI API key not found in environment variables"
            )
        
        try:
            # Test OpenAI embeddings
            embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
            test_text = "This is a test document for embedding validation."
            
            # Generate embedding
            embedding_vector = embeddings.embed_query(test_text)
            
            # Validate embedding properties
            if len(embedding_vector) != self.config.dimension:
                return ValidationResult(
                    check_name="OpenAI Integration",
                    status=False,
                    message=f"Embedding dimension mismatch: expected {self.config.dimension}, got {len(embedding_vector)}",
                    details={
                        "expected_dimension": self.config.dimension,
                        "actual_dimension": len(embedding_vector)
                    }
                )
            
            # Test with Pinecone if index is available
            integration_details = {
                "embedding_dimension": len(embedding_vector),
                "test_text": test_text
            }
            
            if self.index:
                try:
                    # Test storing and querying the embedding
                    test_id = f"openai-test-{int(time.time())}"
                    self.index.upsert(vectors=[{
                        "id": test_id,
                        "values": embedding_vector,
                        "metadata": {"test": True, "source": "openai_validation"}
                    }])
                    
                    # Wait for indexing
                    time.sleep(1)
                    
                    # Query back
                    query_result = self.index.query(
                        vector=embedding_vector,
                        top_k=1,
                        include_metadata=True,
                        filter={"test": True}
                    )
                    
                    # Cleanup
                    self.index.delete(ids=[test_id])
                    
                    integration_details["pinecone_integration"] = {
                        "upsert_successful": True,
                        "query_successful": len(query_result.get('matches', [])) > 0,
                        "top_score": query_result.get('matches', [{}])[0].get('score', 0) if query_result.get('matches') else 0
                    }
                    
                except Exception as e:
                    integration_details["pinecone_integration"] = {
                        "error": str(e)
                    }
            
            return ValidationResult(
                check_name="OpenAI Integration",
                status=True,
                message="OpenAI embeddings integration is working correctly",
                details=integration_details
            )
        
        except Exception as e:
            return ValidationResult(
                check_name="OpenAI Integration",
                status=False,
                message=f"OpenAI integration test failed: {str(e)}",
                details={"error_type": type(e).__name__}
            )
    
    def run_all_validations(self) -> List[ValidationResult]:
        """Run all validation checks"""
        print("🔍 Starting Pinecone validation checks...")
        
        # Environment variables check
        result = self.validate_environment_variables()
        self.results.append(result)
        print(f"{'✅' if result.status else '❌'} {result.check_name}: {result.message}")
        
        if not result.status:
            print("❌ Cannot proceed without required environment variables")
            return self.results
        
        # API key validation
        result = self.validate_api_key()
        self.results.append(result)
        print(f"{'✅' if result.status else '❌'} {result.check_name}: {result.message}")
        
        if not result.status:
            print("❌ Cannot proceed without valid API key")
            return self.results
        
        # Index existence check
        result = self.validate_index_existence()
        self.results.append(result)
        print(f"{'✅' if result.status else '❌'} {result.check_name}: {result.message}")
        
        if not result.status:
            print("❌ Cannot proceed without existing index")
            return self.results
        
        # Index configuration check
        result = self.validate_index_configuration()
        self.results.append(result)
        print(f"{'✅' if result.status else '❌'} {result.check_name}: {result.message}")
        
        # Vector operations test
        result = self.test_vector_operations()
        self.results.append(result)
        print(f"{'✅' if result.status else '❌'} {result.check_name}: {result.message}")
        
        # OpenAI integration test
        result = self.validate_openai_integration()
        self.results.append(result)
        print(f"{'✅' if result.status else '❌'} {result.check_name}: {result.message}")
        
        return self.results

class PineconeMigrator:
    """Handles migration from ChromaDB to Pinecone"""
    
    def __init__(self, config: PineconeConfig):
        self.config = config
        self.pc = None
        self.index = None
    
    def initialize_pinecone(self) -> bool:
        """Initialize Pinecone client and index"""
        try:
            self.pc = Pinecone(api_key=self.config.api_key)
            self.index = self.pc.Index(self.config.index_name)
            return True
        except Exception as e:
            print(f"❌ Failed to initialize Pinecone: {e}")
            return False
    
    def create_index_if_not_exists(self) -> bool:
        """Create Pinecone index if it doesn't exist"""
        if not self.pc:
            print("❌ Pinecone client not initialized")
            return False
        
        try:
            indexes = self.pc.list_indexes()
            index_names = [idx.name for idx in indexes]
            
            if self.config.index_name in index_names:
                print(f"✅ Index '{self.config.index_name}' already exists")
                return True
            
            print(f"📝 Creating index '{self.config.index_name}'...")
            
            # Create index with serverless spec (free tier)
            self.pc.create_index(
                name=self.config.index_name,
                dimension=self.config.dimension,
                metric=self.config.metric,
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'
                )
            )
            
            # Wait for index to be ready
            print("⏳ Waiting for index to be ready...")
            while True:
                try:
                    index_description = self.pc.describe_index(self.config.index_name)
                    if index_description.status.ready:
                        break
                    time.sleep(5)
                except:
                    time.sleep(5)
            
            print(f"✅ Index '{self.config.index_name}' created successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create index: {e}")
            return False
    
    def migrate_from_chromadb(self, chromadb_path: str = "./chroma_db", 
                             collection_name: str = "documents",
                             batch_size: int = 100) -> bool:
        """Migrate data from ChromaDB to Pinecone"""
        try:
            import chromadb
        except ImportError:
            print("❌ ChromaDB not installed. Install with: pip install chromadb")
            return False
        
        if not self.initialize_pinecone():
            return False
        
        try:
            # Initialize ChromaDB
            print(f"📂 Loading ChromaDB from {chromadb_path}")
            chroma_client = chromadb.PersistentClient(path=chromadb_path)
            
            try:
                collection = chroma_client.get_collection(collection_name)
            except Exception:
                print(f"❌ Collection '{collection_name}' not found in ChromaDB")
                return False
            
            # Get all documents from ChromaDB
            print("📊 Retrieving documents from ChromaDB...")
            results = collection.get(include=['embeddings', 'documents', 'metadatas'])
            
            if not results['embeddings']:
                print("⚠️ No embeddings found in ChromaDB collection")
                return True
            
            total_vectors = len(results['embeddings'])
            print(f"📋 Found {total_vectors} vectors to migrate")
            
            # Prepare vectors for Pinecone
            vectors_to_upsert = []
            for i, (embedding, document, metadata) in enumerate(
                zip(results['embeddings'], results['documents'], results['metadatas'] or [{}] * len(results['embeddings']))
            ):
                vector_data = {
                    'id': f'migrated_doc_{i}',
                    'values': embedding,
                    'metadata': {
                        'text': document,
                        'migrated_from': 'chromadb',
                        'migration_timestamp': datetime.now().isoformat(),
                        **(metadata or {})
                    }
                }
                vectors_to_upsert.append(vector_data)
            
            # Upsert vectors in batches
            print(f"📤 Uploading vectors to Pinecone in batches of {batch_size}...")
            for i in range(0, len(vectors_to_upsert), batch_size):
                batch = vectors_to_upsert[i:i + batch_size]
                try:
                    self.index.upsert(vectors=batch)
                    print(f"✅ Uploaded batch {i//batch_size + 1}/{(len(vectors_to_upsert) + batch_size - 1)//batch_size}")
                except Exception as e:
                    print(f"❌ Failed to upload batch {i//batch_size + 1}: {e}")
                    return False
                
                # Small delay to avoid rate limits
                time.sleep(0.1)
            
            print(f"✅ Successfully migrated {total_vectors} vectors to Pinecone")
            
            # Verify migration
            print("🔍 Verifying migration...")
            stats = self.index.describe_index_stats()
            print(f"📊 Pinecone index now contains {stats.get('total_vector_count', 0)} vectors")
            
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False

def generate_validation_report(results: List[ValidationResult], output_file: str = None) -> str:
    """Generate a detailed validation report"""
    report_lines = [
        "# Pinecone Validation Report",
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Summary",
        ""
    ]
    
    passed_checks = sum(1 for r in results if r.status)
    total_checks = len(results)
    
    report_lines.extend([
        f"- **Total Checks**: {total_checks}",
        f"- **Passed**: {passed_checks}",
        f"- **Failed**: {total_checks - passed_checks}",
        f"- **Success Rate**: {(passed_checks/total_checks*100):.1f}%" if total_checks > 0 else "- **Success Rate**: N/A",
        ""
    ])
    
    # Overall status
    if passed_checks == total_checks:
        report_lines.append("🎉 **Overall Status**: All checks passed! Pinecone is ready for use.")
    else:
        report_lines.append("⚠️ **Overall Status**: Some checks failed. Review the details below.")
    
    report_lines.extend(["", "## Detailed Results", ""])
    
    # Detailed results
    for result in results:
        status_icon = "✅" if result.status else "❌"
        report_lines.extend([
            f"### {status_icon} {result.check_name}",
            f"**Status**: {'PASS' if result.status else 'FAIL'}",
            f"**Message**: {result.message}",
            f"**Timestamp**: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ])
        
        if result.details:
            report_lines.extend([
                "**Details**:",
                "```json",
                json.dumps(result.details, indent=2, default=str),
                "```",
                ""
            ])
    
    report_content = "\n".join(report_lines)
    
    if output_file:
        try:
            with open(output_file, 'w') as f:
                f.write(report_content)
            print(f"📄 Validation report saved to: {output_file}")
        except Exception as e:
            print(f"❌ Failed to save report: {e}")
    
    return report_content

def main():
    """Main function to run Pinecone utilities"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Pinecone Migration and Validation Utilities")
    parser.add_argument("--validate", action="store_true", help="Run validation checks")
    parser.add_argument("--migrate", action="store_true", help="Migrate from ChromaDB to Pinecone")
    parser.add_argument("--create-index", action="store_true", help="Create Pinecone index if it doesn't exist")
    parser.add_argument("--chromadb-path", default="./chroma_db", help="Path to ChromaDB directory")
    parser.add_argument("--collection-name", default="documents", help="ChromaDB collection name")
    parser.add_argument("--report-file", help="Output file for validation report")
    parser.add_argument("--batch-size", type=int, default=100, help="Batch size for migration")
    
    args = parser.parse_args()
    
    # Load configuration from environment
    config = PineconeConfig(
        api_key=os.getenv('PINECONE_API_KEY', ''),
        index_name=os.getenv('PINECONE_INDEX_NAME', 'rag-ai-agent'),
        dimension=int(os.getenv('PINECONE_DIMENSION', '1536')),
        metric=os.getenv('PINECONE_METRIC', 'cosine')
    )
    
    if not any([args.validate, args.migrate, args.create_index]):
        print("❌ Please specify an action: --validate, --migrate, or --create-index")
        parser.print_help()
        return
    
    if args.create_index:
        print("🏗️ Creating Pinecone index...")
        migrator = PineconeMigrator(config)
        if migrator.create_index_if_not_exists():
            print("✅ Index creation completed")
        else:
            print("❌ Index creation failed")
            return
    
    if args.validate:
        print("🔍 Running Pinecone validation...")
        validator = PineconeValidator(config)
        results = validator.run_all_validations()
        
        # Generate report
        report = generate_validation_report(results, args.report_file)
        
        # Print summary
        passed = sum(1 for r in results if r.status)
        total = len(results)
        print(f"\n📊 Validation Summary: {passed}/{total} checks passed")
        
        if passed == total:
            print("🎉 All validations passed! Pinecone is ready for use.")
        else:
            print("⚠️ Some validations failed. Check the report for details.")
            sys.exit(1)
    
    if args.migrate:
        print("🚀 Starting migration from ChromaDB to Pinecone...")
        migrator = PineconeMigrator(config)
        
        if migrator.migrate_from_chromadb(
            chromadb_path=args.chromadb_path,
            collection_name=args.collection_name,
            batch_size=args.batch_size
        ):
            print("✅ Migration completed successfully")
        else:
            print("❌ Migration failed")
            sys.exit(1)

if __name__ == "__main__":
    main()