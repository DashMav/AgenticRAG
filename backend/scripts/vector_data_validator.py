#!/usr/bin/env python3
"""
Vector Data Validation Utilities

This script provides utilities for validating vector database operations
including data integrity, embedding quality, and search accuracy.

Requirements: 2.2, 2.4
"""

import os
import sys
import json
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

try:
    from pinecone import Pinecone
    from langchain_openai import OpenAIEmbeddings
    import openai
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Missing required dependencies: {e}")
    print("Install with: pip install pinecone-client langchain-openai python-dotenv numpy")
    sys.exit(1)

load_dotenv()

@dataclass
class VectorValidationResult:
    """Result of vector data validation"""
    test_name: str
    status: bool
    message: str
    score: Optional[float] = None
    details: Optional[Dict] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class VectorDataValidator:
    """Validates vector data quality and operations"""
    
    def __init__(self, api_key: str, index_name: str):
        self.api_key = api_key
        self.index_name = index_name
        self.pc = None
        self.index = None
        self.embeddings = None
        self.results: List[VectorValidationResult] = []
        
    def initialize(self) -> bool:
        """Initialize Pinecone and OpenAI clients"""
        try:
            # Initialize Pinecone
            self.pc = Pinecone(api_key=self.api_key)
            self.index = self.pc.Index(self.index_name)
            
            # Initialize OpenAI embeddings
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if not openai_api_key:
                print("❌ OpenAI API key not found")
                return False
            
            self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
            return True
            
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            return False
    
    def validate_embedding_dimensions(self, test_texts: List[str] = None) -> VectorValidationResult:
        """Validate that embeddings have correct dimensions"""
        if not test_texts:
            test_texts = [
                "This is a test document about artificial intelligence.",
                "Machine learning is a subset of AI that focuses on algorithms.",
                "Natural language processing helps computers understand human language."
            ]
        
        try:
            dimension_results = []
            
            for text in test_texts:
                embedding = self.embeddings.embed_query(text)
                dimension_results.append({
                    "text": text[:50] + "..." if len(text) > 50 else text,
                    "dimension": len(embedding),
                    "expected": 1536
                })
            
            # Check if all dimensions are correct
            incorrect_dimensions = [r for r in dimension_results if r["dimension"] != 1536]
            
            if incorrect_dimensions:
                return VectorValidationResult(
                    test_name="Embedding Dimensions",
                    status=False,
                    message=f"Found {len(incorrect_dimensions)} embeddings with incorrect dimensions",
                    details={
                        "incorrect_dimensions": incorrect_dimensions,
                        "all_results": dimension_results
                    }
                )
            
            return VectorValidationResult(
                test_name="Embedding Dimensions",
                status=True,
                message=f"All {len(test_texts)} embeddings have correct dimensions (1536)",
                details={"results": dimension_results}
            )
            
        except Exception as e:
            return VectorValidationResult(
                test_name="Embedding Dimensions",
                status=False,
                message=f"Embedding dimension validation failed: {str(e)}",
                details={"error": str(e)}
            )
    
    def validate_embedding_quality(self, test_pairs: List[Tuple[str, str]] = None) -> VectorValidationResult:
        """Validate embedding quality by testing semantic similarity"""
        if not test_pairs:
            test_pairs = [
                ("dog", "puppy"),  # Should be similar
                ("car", "automobile"),  # Should be similar
                ("happy", "joyful"),  # Should be similar
                ("dog", "mathematics"),  # Should be dissimilar
                ("car", "happiness"),  # Should be dissimilar
            ]
        
        try:
            similarity_results = []
            
            for text1, text2 in test_pairs:
                # Generate embeddings
                emb1 = self.embeddings.embed_query(text1)
                emb2 = self.embeddings.embed_query(text2)
                
                # Calculate cosine similarity
                similarity = self._cosine_similarity(emb1, emb2)
                
                # Determine if this pair should be similar or not
                expected_similar = any([
                    ("dog" in text1.lower() and "puppy" in text2.lower()) or ("puppy" in text1.lower() and "dog" in text2.lower()),
                    ("car" in text1.lower() and "automobile" in text2.lower()) or ("automobile" in text1.lower() and "car" in text2.lower()),
                    ("happy" in text1.lower() and "joyful" in text2.lower()) or ("joyful" in text1.lower() and "happy" in text2.lower()),
                ])
                
                similarity_results.append({
                    "text1": text1,
                    "text2": text2,
                    "similarity": similarity,
                    "expected_similar": expected_similar,
                    "meets_expectation": (similarity > 0.7) == expected_similar
                })
            
            # Calculate overall quality score
            correct_predictions = sum(1 for r in similarity_results if r["meets_expectation"])
            quality_score = correct_predictions / len(similarity_results)
            
            return VectorValidationResult(
                test_name="Embedding Quality",
                status=quality_score >= 0.8,  # 80% threshold
                message=f"Embedding quality score: {quality_score:.2f} ({correct_predictions}/{len(similarity_results)} correct)",
                score=quality_score,
                details={"results": similarity_results}
            )
            
        except Exception as e:
            return VectorValidationResult(
                test_name="Embedding Quality",
                status=False,
                message=f"Embedding quality validation failed: {str(e)}",
                details={"error": str(e)}
            )
    
    def validate_vector_storage_integrity(self, test_documents: List[str] = None) -> VectorValidationResult:
        """Validate that vectors are stored and retrieved correctly"""
        if not test_documents:
            test_documents = [
                "The quick brown fox jumps over the lazy dog.",
                "Artificial intelligence is transforming modern technology.",
                "Climate change is one of the most pressing issues of our time."
            ]
        
        try:
            test_vectors = []
            
            # Generate embeddings and prepare test vectors
            for i, doc in enumerate(test_documents):
                embedding = self.embeddings.embed_query(doc)
                vector_id = f"integrity_test_{i}_{int(datetime.now().timestamp())}"
                
                test_vectors.append({
                    "id": vector_id,
                    "values": embedding,
                    "metadata": {
                        "text": doc,
                        "test_type": "integrity_validation",
                        "timestamp": datetime.now().isoformat()
                    }
                })
            
            # Store vectors
            upsert_response = self.index.upsert(vectors=test_vectors)
            
            # Wait for indexing
            import time
            time.sleep(2)
            
            # Retrieve and validate each vector
            retrieval_results = []
            
            for test_vector in test_vectors:
                # Query for the exact vector
                query_response = self.index.query(
                    vector=test_vector["values"],
                    top_k=1,
                    include_metadata=True,
                    filter={"test_type": "integrity_validation"}
                )
                
                if query_response.matches:
                    match = query_response.matches[0]
                    retrieval_results.append({
                        "vector_id": test_vector["id"],
                        "found": True,
                        "score": match.score,
                        "metadata_match": match.metadata.get("text") == test_vector["metadata"]["text"]
                    })
                else:
                    retrieval_results.append({
                        "vector_id": test_vector["id"],
                        "found": False,
                        "score": 0.0,
                        "metadata_match": False
                    })
            
            # Cleanup test vectors
            vector_ids = [v["id"] for v in test_vectors]
            self.index.delete(ids=vector_ids)
            
            # Analyze results
            successful_retrievals = sum(1 for r in retrieval_results if r["found"] and r["score"] > 0.99)
            metadata_matches = sum(1 for r in retrieval_results if r["metadata_match"])
            
            integrity_score = successful_retrievals / len(test_vectors)
            
            return VectorValidationResult(
                test_name="Vector Storage Integrity",
                status=integrity_score >= 0.9,  # 90% threshold
                message=f"Storage integrity: {successful_retrievals}/{len(test_vectors)} vectors retrieved correctly",
                score=integrity_score,
                details={
                    "retrieval_results": retrieval_results,
                    "metadata_matches": metadata_matches,
                    "total_vectors": len(test_vectors)
                }
            )
            
        except Exception as e:
            return VectorValidationResult(
                test_name="Vector Storage Integrity",
                status=False,
                message=f"Storage integrity validation failed: {str(e)}",
                details={"error": str(e)}
            )
    
    def validate_search_accuracy(self, test_queries: List[Dict[str, Any]] = None) -> VectorValidationResult:
        """Validate search accuracy with known query-document pairs"""
        if not test_queries:
            # Create test documents and queries
            test_docs = [
                "Python is a high-level programming language known for its simplicity and readability.",
                "Machine learning algorithms can automatically improve through experience and data.",
                "The solar system consists of the Sun and eight planets orbiting around it.",
                "Photosynthesis is the process by which plants convert sunlight into chemical energy."
            ]
            
            test_queries = [
                {"query": "programming language Python", "expected_doc_index": 0},
                {"query": "artificial intelligence and machine learning", "expected_doc_index": 1},
                {"query": "planets and the Sun", "expected_doc_index": 2},
                {"query": "how plants make energy from sunlight", "expected_doc_index": 3}
            ]
        else:
            # Extract documents from test_queries if provided
            test_docs = [q.get("document", f"Test document {i}") for i, q in enumerate(test_queries)]
        
        try:
            # Store test documents
            test_vectors = []
            for i, doc in enumerate(test_docs):
                embedding = self.embeddings.embed_query(doc)
                vector_id = f"search_test_{i}_{int(datetime.now().timestamp())}"
                
                test_vectors.append({
                    "id": vector_id,
                    "values": embedding,
                    "metadata": {
                        "text": doc,
                        "doc_index": i,
                        "test_type": "search_accuracy"
                    }
                })
            
            self.index.upsert(vectors=test_vectors)
            
            # Wait for indexing
            import time
            time.sleep(3)
            
            # Test each query
            search_results = []
            
            for query_data in test_queries:
                query_text = query_data["query"]
                expected_index = query_data["expected_doc_index"]
                
                # Generate query embedding
                query_embedding = self.embeddings.embed_query(query_text)
                
                # Search
                search_response = self.index.query(
                    vector=query_embedding,
                    top_k=3,
                    include_metadata=True,
                    filter={"test_type": "search_accuracy"}
                )
                
                # Check if expected document is in top results
                top_match = search_response.matches[0] if search_response.matches else None
                expected_found = False
                expected_rank = None
                
                if search_response.matches:
                    for rank, match in enumerate(search_response.matches):
                        if match.metadata.get("doc_index") == expected_index:
                            expected_found = True
                            expected_rank = rank + 1
                            break
                
                search_results.append({
                    "query": query_text,
                    "expected_doc_index": expected_index,
                    "expected_found": expected_found,
                    "expected_rank": expected_rank,
                    "top_score": top_match.score if top_match else 0.0,
                    "correct_top_result": top_match.metadata.get("doc_index") == expected_index if top_match else False
                })
            
            # Cleanup
            vector_ids = [v["id"] for v in test_vectors]
            self.index.delete(ids=vector_ids)
            
            # Calculate accuracy metrics
            correct_top_results = sum(1 for r in search_results if r["correct_top_result"])
            found_in_results = sum(1 for r in search_results if r["expected_found"])
            
            accuracy_score = correct_top_results / len(test_queries)
            recall_score = found_in_results / len(test_queries)
            
            return VectorValidationResult(
                test_name="Search Accuracy",
                status=accuracy_score >= 0.7,  # 70% threshold
                message=f"Search accuracy: {correct_top_results}/{len(test_queries)} queries returned correct top result",
                score=accuracy_score,
                details={
                    "search_results": search_results,
                    "accuracy_score": accuracy_score,
                    "recall_score": recall_score,
                    "total_queries": len(test_queries)
                }
            )
            
        except Exception as e:
            return VectorValidationResult(
                test_name="Search Accuracy",
                status=False,
                message=f"Search accuracy validation failed: {str(e)}",
                details={"error": str(e)}
            )
    
    def validate_metadata_filtering(self) -> VectorValidationResult:
        """Validate metadata filtering functionality"""
        try:
            # Create test vectors with different metadata
            test_vectors = [
                {
                    "id": f"filter_test_1_{int(datetime.now().timestamp())}",
                    "values": [0.1] * 1536,
                    "metadata": {"category": "science", "type": "article", "test_type": "filter_validation"}
                },
                {
                    "id": f"filter_test_2_{int(datetime.now().timestamp())}",
                    "values": [0.2] * 1536,
                    "metadata": {"category": "technology", "type": "article", "test_type": "filter_validation"}
                },
                {
                    "id": f"filter_test_3_{int(datetime.now().timestamp())}",
                    "values": [0.3] * 1536,
                    "metadata": {"category": "science", "type": "blog", "test_type": "filter_validation"}
                }
            ]
            
            # Store vectors
            self.index.upsert(vectors=test_vectors)
            
            # Wait for indexing
            import time
            time.sleep(2)
            
            # Test different filters
            filter_tests = [
                {"filter": {"category": "science"}, "expected_count": 2},
                {"filter": {"type": "article"}, "expected_count": 2},
                {"filter": {"category": "technology", "type": "article"}, "expected_count": 1},
                {"filter": {"category": "nonexistent"}, "expected_count": 0}
            ]
            
            filter_results = []
            
            for test in filter_tests:
                query_response = self.index.query(
                    vector=[0.15] * 1536,  # Query vector
                    top_k=10,
                    include_metadata=True,
                    filter={**test["filter"], "test_type": "filter_validation"}
                )
                
                actual_count = len(query_response.matches)
                filter_results.append({
                    "filter": test["filter"],
                    "expected_count": test["expected_count"],
                    "actual_count": actual_count,
                    "correct": actual_count == test["expected_count"]
                })
            
            # Cleanup
            vector_ids = [v["id"] for v in test_vectors]
            self.index.delete(ids=vector_ids)
            
            # Calculate success rate
            correct_filters = sum(1 for r in filter_results if r["correct"])
            success_rate = correct_filters / len(filter_tests)
            
            return VectorValidationResult(
                test_name="Metadata Filtering",
                status=success_rate >= 0.9,  # 90% threshold
                message=f"Metadata filtering: {correct_filters}/{len(filter_tests)} filter tests passed",
                score=success_rate,
                details={"filter_results": filter_results}
            )
            
        except Exception as e:
            return VectorValidationResult(
                test_name="Metadata Filtering",
                status=False,
                message=f"Metadata filtering validation failed: {str(e)}",
                details={"error": str(e)}
            )
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def run_all_validations(self) -> List[VectorValidationResult]:
        """Run all vector data validations"""
        print("🔍 Starting vector data validation...")
        
        if not self.initialize():
            return [VectorValidationResult(
                test_name="Initialization",
                status=False,
                message="Failed to initialize Pinecone and OpenAI clients"
            )]
        
        # Run all validation tests
        validations = [
            ("Embedding Dimensions", self.validate_embedding_dimensions),
            ("Embedding Quality", self.validate_embedding_quality),
            ("Vector Storage Integrity", self.validate_vector_storage_integrity),
            ("Search Accuracy", self.validate_search_accuracy),
            ("Metadata Filtering", self.validate_metadata_filtering)
        ]
        
        for test_name, test_func in validations:
            print(f"🧪 Running {test_name} validation...")
            try:
                result = test_func()
                self.results.append(result)
                
                status_icon = "✅" if result.status else "❌"
                score_text = f" (Score: {result.score:.2f})" if result.score is not None else ""
                print(f"{status_icon} {test_name}: {result.message}{score_text}")
                
            except Exception as e:
                error_result = VectorValidationResult(
                    test_name=test_name,
                    status=False,
                    message=f"Test failed with exception: {str(e)}",
                    details={"error": str(e)}
                )
                self.results.append(error_result)
                print(f"❌ {test_name}: Test failed with exception: {str(e)}")
        
        return self.results

def main():
    """Main function for vector data validation"""
    print("🧪 Vector Data Validation Utility")
    print("=" * 50)
    
    # Load configuration
    api_key = os.getenv('PINECONE_API_KEY')
    index_name = os.getenv('PINECONE_INDEX_NAME', 'rag-ai-agent')
    
    if not api_key:
        print("❌ PINECONE_API_KEY not found in environment variables")
        return 1
    
    print(f"📋 Configuration:")
    print(f"   - Index Name: {index_name}")
    print(f"   - API Key: {'Set' if api_key else 'Not Set'}")
    print()
    
    # Run validations
    validator = VectorDataValidator(api_key, index_name)
    results = validator.run_all_validations()
    
    # Generate summary
    passed = sum(1 for r in results if r.status)
    total = len(results)
    
    print(f"\n📊 Validation Summary:")
    print(f"   - Total Tests: {total}")
    print(f"   - Passed: {passed}")
    print(f"   - Failed: {total - passed}")
    
    if passed == total:
        print("\n🎉 SUCCESS: All vector data validations passed!")
        print("   Your vector database is working correctly.")
        return 0
    else:
        print(f"\n⚠️ WARNING: {total - passed} validation(s) failed.")
        print("   Please review the issues above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)