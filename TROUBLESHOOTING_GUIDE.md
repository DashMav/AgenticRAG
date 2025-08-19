# RAG AI-Agent Troubleshooting and Debugging Guide

## Overview

This comprehensive troubleshooting guide helps you diagnose and resolve common deployment and runtime issues with the RAG AI-Agent application. The guide is organized by problem category and includes step-by-step debugging procedures.

## Quick Diagnostic Commands

Before diving into specific issues, run these quick diagnostic commands:

```bash
# Validate deployment configuration
python validate_deployment.py

# Check backend health (replace with your URL)
curl https://your-username-your-space-name.hf.space/health

# Check frontend build locally
cd agent-frontend && npm run build

# Test API connectivity
python scripts/test_api_connectivity.py
```

## Common Deployment Issues

### 1. Backend Deployment Issues (Hugging Face Spaces)

#### Issue: Docker Build Fails

**Symptoms:**
- Build logs show dependency installation errors
- Container fails to start
- "ModuleNotFoundError" in logs

**Debugging Steps:**
1. Check the build logs in your Hugging Face Space
2. Verify `requirements.txt` contains all dependencies
3. Check for version conflicts

**Solutions:**
```bash
# Update requirements.txt with specific versions
pip freeze > requirements.txt

# Test Docker build locally
docker build -t rag-ai-agent .
docker run -p 8000:8000 rag-ai-agent
```

**Common Fixes:**
- Pin dependency versions in `requirements.txt`
- Remove conflicting packages
- Update Python version in Dockerfile if needed

#### Issue: Environment Variables Not Accessible

**Symptoms:**
- "API key not found" errors
- Services fail to initialize
- 500 Internal Server Error responses

**Debugging Steps:**
1. Check Hugging Face Space Settings → Variables and secrets
2. Verify secret names match exactly (case-sensitive)
3. Check application logs for environment variable access

**Solutions:**
```python
# Add debug logging to your app
import os
print(f"GROQ_API_KEY present: {'GROQ_API_KEY' in os.environ}")
print(f"Environment variables: {list(os.environ.keys())}")
```

**Common Fixes:**
- Ensure secrets are added as "Secrets" not "Variables"
- Check for typos in secret names
- Redeploy Space after adding secrets

#### Issue: Pinecone Connection Failures

**Symptoms:**
- "Index not found" errors
- Vector operations fail
- Timeout errors when connecting to Pinecone

**Debugging Steps:**
1. Verify Pinecone index exists and is "Ready"
2. Check index dimensions (must be 1536)
3. Test API key permissions

**Solutions:**
```python
# Test Pinecone connection
from pinecone import Pinecone
import os

pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
print("Available indexes:", [idx.name for idx in pc.list_indexes()])

# Check index stats
index = pc.Index(os.getenv('PINECONE_INDEX_NAME'))
print("Index stats:", index.describe_index_stats())
```

**Common Fixes:**
- Create index with correct dimensions (1536)
- Verify API key has read/write permissions
- Check index name spelling

### 2. Frontend Deployment Issues (Vercel)

#### Issue: Build Fails on Vercel

**Symptoms:**
- Vercel deployment fails during build step
- "Module not found" errors
- Build timeout errors

**Debugging Steps:**
1. Check Vercel deployment logs
2. Verify `package.json` dependencies
3. Test build locally

**Solutions:**
```bash
# Test build locally
cd agent-frontend
npm install
npm run build

# Check for missing dependencies
npm audit
npm update
```

**Common Fixes:**
- Update Node.js version in Vercel settings
- Fix dependency version conflicts
- Increase build timeout in Vercel settings

#### Issue: API Proxy Not Working

**Symptoms:**
- Frontend loads but API calls fail
- CORS errors in browser console
- 404 errors for API endpoints

**Debugging Steps:**
1. Check `vercel.json` proxy configuration
2. Verify backend URL is correct
3. Test API endpoints directly

**Solutions:**
```json
// Correct vercel.json configuration
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://your-username-your-space-name.hf.space/:path*"
    }
  ]
}
```

**Common Fixes:**
- Update backend URL in `vercel.json`
- Remove `/api` prefix from destination URL if backend doesn't use it
- Ensure backend has CORS configured

### 3. API Connectivity Issues

#### Issue: Groq API Failures

**Symptoms:**
- Chat responses fail to generate
- "Rate limit exceeded" errors
- Authentication errors

**Debugging Steps:**
1. Test API key directly
2. Check rate limits in Groq console
3. Verify model availability

**Solutions:**
```python
# Test Groq API
from groq import Groq
import os

client = Groq(api_key=os.getenv('GROQ_API_KEY'))
try:
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": "Hello"}],
        model="llama3-8b-8192",
        max_tokens=10
    )
    print("Groq API working:", response.choices[0].message.content)
except Exception as e:
    print("Groq API error:", str(e))
```

**Common Fixes:**
- Check API key validity
- Switch to different model if current one is unavailable
- Implement retry logic with exponential backoff

#### Issue: OpenAI API Failures

**Symptoms:**
- Document embedding fails
- "Insufficient quota" errors
- Slow embedding generation

**Debugging Steps:**
1. Check OpenAI usage dashboard
2. Verify API key permissions
3. Test with smaller documents

**Solutions:**
```python
# Test OpenAI API
import openai
import os

client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
try:
    response = client.embeddings.create(
        input="test document",
        model="text-embedding-ada-002"
    )
    print("OpenAI API working, embedding dimension:", len(response.data[0].embedding))
except Exception as e:
    print("OpenAI API error:", str(e))
```

**Common Fixes:**
- Add billing information to OpenAI account
- Use smaller text chunks for embedding
- Implement batch processing for large documents

### 4. Performance Issues

#### Issue: Slow Response Times

**Symptoms:**
- Chat responses take >30 seconds
- Document processing times out
- Frontend becomes unresponsive

**Debugging Steps:**
1. Monitor API response times
2. Check vector database query performance
3. Profile document processing pipeline

**Performance Optimization Solutions:**

```python
# Optimize document chunking
def optimize_chunking(text, max_chunk_size=1000):
    """Optimize text chunking for better performance."""
    chunks = []
    sentences = text.split('. ')
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk + sentence) < max_chunk_size:
            current_chunk += sentence + ". "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

# Implement caching for embeddings
import hashlib
import json

def cache_embedding(text, embedding):
    """Cache embeddings to avoid recomputation."""
    text_hash = hashlib.md5(text.encode()).hexdigest()
    cache_key = f"embedding_{text_hash}"
    # Store in your preferred cache (Redis, file system, etc.)
    return cache_key
```

**Common Fixes:**
- Reduce document chunk sizes
- Implement embedding caching
- Use async processing for large documents
- Optimize vector database queries

#### Issue: Memory Usage Problems

**Symptoms:**
- Application crashes with out-of-memory errors
- Slow performance over time
- High memory usage in monitoring

**Solutions:**
```python
# Implement memory-efficient document processing
import gc

def process_document_efficiently(file_path):
    """Process documents with memory management."""
    try:
        # Process in chunks
        with open(file_path, 'r') as f:
            while True:
                chunk = f.read(1024 * 1024)  # 1MB chunks
                if not chunk:
                    break
                
                # Process chunk
                process_chunk(chunk)
                
                # Force garbage collection
                gc.collect()
                
    except MemoryError:
        print("Memory error: Document too large")
        return False
    
    return True
```

**Common Fixes:**
- Process documents in smaller chunks
- Implement garbage collection
- Use streaming for large files
- Set memory limits in deployment configuration

### 5. Security Issues

#### Issue: API Keys Exposed

**Symptoms:**
- API keys visible in logs
- Keys committed to version control
- Unauthorized API usage

**Immediate Actions:**
1. Rotate all exposed API keys immediately
2. Remove keys from version control history
3. Update all deployment configurations

**Prevention Solutions:**
```bash
# Check for exposed keys in git history
git log --all --full-history -- "*.env"
git log --all --full-history -S "sk-" -- "*.py" "*.js" "*.json"

# Remove sensitive data from git history
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .env' \
  --prune-empty --tag-name-filter cat -- --all
```

**Security Best Practices:**
- Use `.gitignore` for all environment files
- Implement key rotation procedures
- Monitor API usage regularly
- Use least-privilege access for API keys

#### Issue: CORS Configuration Problems

**Symptoms:**
- Browser blocks API requests
- "Access-Control-Allow-Origin" errors
- Frontend can't communicate with backend

**Solutions:**
```python
# Proper CORS configuration in FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend.vercel.app",
        "http://localhost:5173",  # Local development
        "http://localhost:5174"   # Alternative local port
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

**Common Fixes:**
- Add production frontend URL to CORS origins
- Remove wildcard origins in production
- Ensure credentials are handled properly

## Debugging Tools and Scripts

### 1. Comprehensive Diagnostic Script

Create `scripts/diagnose_issues.py`:

```python
#!/usr/bin/env python3
"""
Comprehensive diagnostic script for RAG AI-Agent issues.
"""

import os
import sys
import requests
import json
import time
from datetime import datetime

def diagnose_backend_health(backend_url):
    """Diagnose backend health and performance."""
    print(f"🔍 Diagnosing backend: {backend_url}")
    
    try:
        # Test health endpoint
        start_time = time.time()
        response = requests.get(f"{backend_url}/health", timeout=10)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ Health check passed ({response_time:.2f}s)")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            
        # Test API documentation
        docs_response = requests.get(f"{backend_url}/docs", timeout=10)
        if docs_response.status_code == 200:
            print("✅ API documentation accessible")
        else:
            print("❌ API documentation not accessible")
            
    except requests.exceptions.Timeout:
        print("❌ Backend timeout - check if service is running")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend - check URL")
    except Exception as e:
        print(f"❌ Backend error: {str(e)}")

def diagnose_api_services():
    """Diagnose external API service connectivity."""
    print("🔍 Diagnosing API services...")
    
    # Test each service with detailed error reporting
    services = {
        'Groq': test_groq_detailed,
        'OpenAI': test_openai_detailed,
        'Pinecone': test_pinecone_detailed
    }
    
    for service_name, test_func in services.items():
        try:
            result = test_func()
            if result:
                print(f"✅ {service_name}: Working")
            else:
                print(f"❌ {service_name}: Failed")
        except Exception as e:
            print(f"❌ {service_name}: Error - {str(e)}")

def test_groq_detailed():
    """Detailed Groq API testing."""
    from groq import Groq
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("  - API key not found")
        return False
    
    client = Groq(api_key=api_key)
    
    try:
        # Test different models
        models = ["llama3-8b-8192", "mixtral-8x7b-32768"]
        for model in models:
            try:
                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": "Hi"}],
                    model=model,
                    max_tokens=5
                )
                print(f"  - Model {model}: Available")
                return True
            except Exception as e:
                print(f"  - Model {model}: {str(e)}")
        
        return False
        
    except Exception as e:
        print(f"  - Connection error: {str(e)}")
        return False

def test_openai_detailed():
    """Detailed OpenAI API testing."""
    import openai
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("  - API key not found")
        return False
    
    client = openai.OpenAI(api_key=api_key)
    
    try:
        # Test embedding
        response = client.embeddings.create(
            input="test",
            model="text-embedding-ada-002"
        )
        
        if response.data:
            embedding_dim = len(response.data[0].embedding)
            print(f"  - Embeddings working (dimension: {embedding_dim})")
            return True
        
        return False
        
    except Exception as e:
        print(f"  - Error: {str(e)}")
        return False

def test_pinecone_detailed():
    """Detailed Pinecone API testing."""
    from pinecone import Pinecone
    
    api_key = os.getenv('PINECONE_API_KEY')
    index_name = os.getenv('PINECONE_INDEX_NAME')
    
    if not api_key:
        print("  - API key not found")
        return False
    
    if not index_name:
        print("  - Index name not found")
        return False
    
    try:
        pc = Pinecone(api_key=api_key)
        
        # List indexes
        indexes = pc.list_indexes()
        available_indexes = [idx.name for idx in indexes]
        print(f"  - Available indexes: {available_indexes}")
        
        if index_name not in available_indexes:
            print(f"  - Index '{index_name}' not found")
            return False
        
        # Test index operations
        index = pc.Index(index_name)
        stats = index.describe_index_stats()
        print(f"  - Index stats: {stats.total_vector_count} vectors")
        
        # Test query
        test_vector = [0.1] * 1536  # Test vector with correct dimensions
        results = index.query(vector=test_vector, top_k=1)
        print(f"  - Query test: {len(results.matches)} results")
        
        return True
        
    except Exception as e:
        print(f"  - Error: {str(e)}")
        return False

def generate_diagnostic_report():
    """Generate a comprehensive diagnostic report."""
    report = {
        'timestamp': datetime.now().isoformat(),
        'environment_variables': {},
        'system_info': {},
        'api_tests': {},
        'recommendations': []
    }
    
    # Check environment variables
    required_vars = ['GROQ_API_KEY', 'OPENAI_API_KEY', 'PINECONE_API_KEY', 'PINECONE_INDEX_NAME']
    for var in required_vars:
        report['environment_variables'][var] = bool(os.getenv(var))
    
    # System information
    report['system_info'] = {
        'python_version': sys.version,
        'platform': sys.platform,
        'working_directory': os.getcwd()
    }
    
    # Save report
    with open('diagnostic_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📊 Diagnostic report saved to: diagnostic_report.json")

if __name__ == "__main__":
    print("🚀 RAG AI-Agent Diagnostic Tool")
    print("=" * 50)
    
    # Run diagnostics
    diagnose_api_services()
    
    # Generate report
    generate_diagnostic_report()
    
    print("\n✨ Diagnostic complete!")
```

### 2. Network Connectivity Tester

Create `scripts/test_network_connectivity.py`:

```python
#!/usr/bin/env python3
"""
Network connectivity testing for RAG AI-Agent services.
"""

import socket
import requests
import time
from urllib.parse import urlparse

def test_dns_resolution(hostname):
    """Test DNS resolution for a hostname."""
    try:
        ip = socket.gethostbyname(hostname)
        print(f"✅ DNS resolution for {hostname}: {ip}")
        return True
    except socket.gaierror as e:
        print(f"❌ DNS resolution failed for {hostname}: {e}")
        return False

def test_port_connectivity(hostname, port, timeout=5):
    """Test TCP connectivity to a specific port."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((hostname, port))
        sock.close()
        
        if result == 0:
            print(f"✅ Port {port} is open on {hostname}")
            return True
        else:
            print(f"❌ Port {port} is closed on {hostname}")
            return False
    except Exception as e:
        print(f"❌ Error testing port {port} on {hostname}: {e}")
        return False

def test_http_connectivity(url, timeout=10):
    """Test HTTP connectivity and response time."""
    try:
        start_time = time.time()
        response = requests.get(url, timeout=timeout)
        response_time = time.time() - start_time
        
        print(f"✅ HTTP {response.status_code} from {url} ({response_time:.2f}s)")
        return True
    except requests.exceptions.Timeout:
        print(f"❌ HTTP timeout for {url}")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ HTTP connection error for {url}")
        return False
    except Exception as e:
        print(f"❌ HTTP error for {url}: {e}")
        return False

def main():
    """Run network connectivity tests."""
    print("🌐 Network Connectivity Tests")
    print("=" * 40)
    
    # Test external services
    services = [
        ("api.groq.com", 443),
        ("api.openai.com", 443),
        ("api.pinecone.io", 443),
        ("huggingface.co", 443),
        ("vercel.com", 443)
    ]
    
    for hostname, port in services:
        print(f"\n🔍 Testing {hostname}:")
        test_dns_resolution(hostname)
        test_port_connectivity(hostname, port)
        test_http_connectivity(f"https://{hostname}", timeout=10)

if __name__ == "__main__":
    main()
```

## Performance Optimization Recommendations

### 1. Backend Optimization

```python
# Implement connection pooling
import asyncio
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_db_connection():
    """Manage database connections efficiently."""
    connection = await create_connection()
    try:
        yield connection
    finally:
        await connection.close()

# Cache frequently accessed data
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_embedding(text_hash):
    """Cache embeddings to reduce API calls."""
    # Implementation here
    pass

# Implement async processing
async def process_document_async(file_path):
    """Process documents asynchronously."""
    tasks = []
    chunks = split_document(file_path)
    
    for chunk in chunks:
        task = asyncio.create_task(process_chunk_async(chunk))
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results
```

### 2. Frontend Optimization

```javascript
// Implement request debouncing
import { debounce } from 'lodash';

const debouncedSearch = debounce(async (query) => {
  const response = await fetch('/api/search', {
    method: 'POST',
    body: JSON.stringify({ query }),
    headers: { 'Content-Type': 'application/json' }
  });
  return response.json();
}, 300);

// Add loading states and error boundaries
function ChatComponent() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const handleSubmit = async (message) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await sendMessage(message);
      // Handle response
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  if (error) {
    return <ErrorComponent error={error} onRetry={() => setError(null)} />;
  }
  
  return (
    <div>
      {loading && <LoadingSpinner />}
      {/* Chat interface */}
    </div>
  );
}
```

### 3. Database Optimization

```python
# Optimize vector queries
def optimize_vector_search(query_vector, top_k=5):
    """Optimize vector search with proper indexing."""
    # Use appropriate similarity metric
    results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True,
        filter={"source": {"$ne": "system"}}  # Filter out system documents
    )
    
    return results

# Implement batch operations
def batch_upsert_vectors(vectors, batch_size=100):
    """Upsert vectors in batches for better performance."""
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        index.upsert(vectors=batch)
        time.sleep(0.1)  # Rate limiting
```

## Emergency Recovery Procedures

### 1. Service Outage Recovery

```bash
#!/bin/bash
# Emergency recovery script

echo "🚨 Emergency Recovery Procedure"

# Check service status
echo "Checking service status..."
curl -f https://your-backend.hf.space/health || echo "Backend down"
curl -f https://your-frontend.vercel.app || echo "Frontend down"

# Restart services if needed
echo "Restarting services..."
# Trigger Hugging Face Space restart
# Trigger Vercel redeployment

# Verify recovery
echo "Verifying recovery..."
sleep 30
curl -f https://your-backend.hf.space/health && echo "Backend recovered"
curl -f https://your-frontend.vercel.app && echo "Frontend recovered"
```

### 2. Data Recovery

```python
# Backup and restore procedures
def backup_vector_data(index_name, backup_file):
    """Backup vector database data."""
    index = pc.Index(index_name)
    
    # Export all vectors
    vectors = []
    for ids in index.list():
        fetch_response = index.fetch(ids=ids)
        vectors.extend(fetch_response.vectors.values())
    
    # Save to backup file
    with open(backup_file, 'w') as f:
        json.dump(vectors, f)
    
    print(f"Backup saved to {backup_file}")

def restore_vector_data(index_name, backup_file):
    """Restore vector database data."""
    index = pc.Index(index_name)
    
    # Load backup data
    with open(backup_file, 'r') as f:
        vectors = json.load(f)
    
    # Restore vectors
    index.upsert(vectors=vectors)
    print(f"Data restored from {backup_file}")
```

## Getting Help

### 1. Log Collection

```bash
# Collect logs for support
mkdir -p logs
curl https://your-backend.hf.space/logs > logs/backend.log
# Copy Vercel deployment logs
# Copy browser console logs
tar -czf support-logs.tar.gz logs/
```

### 2. Support Information Template

When seeking help, provide:

```
**Environment:**
- Backend URL: 
- Frontend URL: 
- Deployment date: 
- Last working version: 

**Issue Description:**
- What were you trying to do?
- What happened instead?
- Error messages (exact text):

**Steps to Reproduce:**
1. 
2. 
3. 

**Diagnostic Information:**
- Validation script output: [attach validate_deployment.py output]
- Browser console errors: [attach screenshot]
- Network tab information: [attach screenshot]

**Configuration:**
- Pinecone index name: 
- API services used: 
- Custom modifications: 
```

### 3. Community Resources

- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Check latest deployment guides
- **Service Status Pages**: 
  - Hugging Face: https://status.huggingface.co/
  - Vercel: https://vercel-status.com/
  - Pinecone: https://status.pinecone.io/
  - OpenAI: https://status.openai.com/

---

*This troubleshooting guide is regularly updated. For the latest version, check the project repository.*