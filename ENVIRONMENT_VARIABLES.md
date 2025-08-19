# Environment Variables Reference

## Overview

This document provides a comprehensive reference for all environment variables used in the RAG AI-Agent application across different deployment platforms.

## Backend Environment Variables

### Required Variables (Hugging Face Spaces Secrets)

| Variable | Platform | Required | Description | Example Value | Where to Get |
|----------|----------|----------|-------------|---------------|--------------|
| `GROQ_API_KEY` | HF Spaces | Yes | API key for Groq LLM inference | `gsk_...` | [Groq Console](https://console.groq.com/) |
| `OPENAI_API_KEY` | HF Spaces | Yes | API key for OpenAI embeddings | `sk-...` | [OpenAI Platform](https://platform.openai.com/) |
| `PINECONE_API_KEY` | HF Spaces | Yes | API key for Pinecone vector database | `pcsk_...` | [Pinecone Dashboard](https://app.pinecone.io/) |
| `PINECONE_INDEX_NAME` | HF Spaces | Yes | Name of your Pinecone index | `rag-ai-agent` | Pinecone Dashboard |

### Optional Variables

| Variable | Platform | Required | Description | Default Value | Notes |
|----------|----------|----------|-------------|---------------|-------|
| `PINECONE_ENVIRONMENT` | HF Spaces | No | Pinecone environment region | Auto-detected | Usually not needed |
| `MAX_FILE_SIZE` | HF Spaces | No | Maximum upload file size in MB | 10 | Adjust based on needs |
| `EMBEDDING_MODEL` | HF Spaces | No | OpenAI embedding model to use | `text-embedding-ada-002` | Use latest available |

## Frontend Environment Variables

### Build-Time Variables

| Variable | Platform | Required | Description | Configuration Method |
|----------|----------|----------|-------------|---------------------|
| `VITE_API_URL` | Vercel | No | Backend API URL | Configured via `vercel.json` proxy |

### Vercel Configuration

The frontend uses a proxy configuration instead of environment variables for API routing:

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://YOUR-BACKEND-URL.hf.space/api/:path*"
    }
  ]
}
```

## Local Development Environment Variables

### Backend (.env file in RAG-AI-Agent/)

```env
# Required for local development
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=rag-ai-agent

# Optional for local development
PINECONE_ENVIRONMENT=us-east-1-aws
MAX_FILE_SIZE=10
EMBEDDING_MODEL=text-embedding-ada-002
```

### Frontend (.env file in RAG-AI-Agent/agent-frontend/)

```env
# Local development API URL
VITE_API_URL=http://127.0.0.1:8000
```

## Platform-Specific Configuration Instructions

### Hugging Face Spaces

1. **Navigate to your Space Settings**
   - Go to your Space dashboard
   - Click on "Settings" tab
   - Select "Variables and secrets"

2. **Add Each Secret**
   - Click "New secret"
   - Enter the variable name exactly as shown above
   - Paste the corresponding API key value
   - Click "Save"

3. **Verify Configuration**
   - Ensure all required secrets are listed
   - Check that secret names match exactly (case-sensitive)
   - Redeploy your Space if you add secrets after initial deployment

### Vercel

1. **Update vercel.json**
   - Located in `agent-frontend/vercel.json`
   - Replace `YOUR-BACKEND-URL` with your actual Hugging Face Space URL
   - Commit and push changes to trigger redeployment

2. **No Environment Variables Needed**
   - Vercel frontend uses proxy configuration only
   - All API calls are routed through the proxy to the backend

### Local Development

1. **Create .env Files**
   - Backend: Create `.env` in `RAG-AI-Agent/` directory
   - Frontend: Create `.env` in `RAG-AI-Agent/agent-frontend/` directory

2. **Add to .gitignore**
   - Ensure `.env` files are not committed to version control
   - Check that `.gitignore` includes `.env` entries

## Security Best Practices

### API Key Management

1. **Never Commit API Keys**
   - Use `.gitignore` to exclude `.env` files
   - Use platform-specific secret management
   - Regularly rotate API keys

2. **Use Minimum Required Permissions**
   - Create API keys with minimal necessary scopes
   - Use separate keys for development and production
   - Monitor API key usage regularly

3. **Secure Storage**
   - Store API keys in platform secret managers
   - Never share API keys in plain text
   - Use environment variables, not hardcoded values

### Platform Security

1. **Hugging Face Spaces**
   - Use "Secrets" feature for all sensitive data
   - Secrets are encrypted and not visible in logs
   - Access through standard environment variable methods

2. **Vercel**
   - Frontend environment variables are build-time only
   - Use proxy configuration to avoid exposing backend URLs
   - Never store API keys in frontend environment variables

## Validation and Testing

### Environment Variable Validation

Create a simple validation script to check if all required environment variables are set:

```python
import os
import sys

required_vars = [
    'GROQ_API_KEY',
    'OPENAI_API_KEY', 
    'PINECONE_API_KEY',
    'PINECONE_INDEX_NAME'
]

missing_vars = []
for var in required_vars:
    if not os.getenv(var):
        missing_vars.append(var)

if missing_vars:
    print(f"Missing required environment variables: {', '.join(missing_vars)}")
    sys.exit(1)
else:
    print("All required environment variables are set!")
```

### API Key Testing

Test each API key to ensure it's valid and has the necessary permissions:

```python
# Test Groq API
from groq import Groq
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Test OpenAI API
import openai
openai.api_key = os.getenv('OPENAI_API_KEY')

# Test Pinecone API
import pinecone
pinecone.init(api_key=os.getenv('PINECONE_API_KEY'))
```

## Troubleshooting

### Common Issues

1. **Environment Variable Not Found**
   - Check spelling and case sensitivity
   - Verify the variable is set in the correct platform
   - Restart the application after setting variables

2. **API Key Invalid**
   - Verify the key is copied correctly (no extra spaces)
   - Check if the key has expired or been revoked
   - Ensure the key has the necessary permissions

3. **Pinecone Connection Issues**
   - Verify index name matches exactly
   - Check that index dimensions are set to 1536
   - Ensure index is in "Ready" state

### Debugging Steps

1. **Check Environment Variable Access**
   ```python
   import os
   print(f"GROQ_API_KEY: {'Set' if os.getenv('GROQ_API_KEY') else 'Not set'}")
   ```

2. **Test API Connectivity**
   - Use the validation scripts above
   - Check service status pages
   - Verify network connectivity

3. **Review Application Logs**
   - Check Hugging Face Space logs for backend issues
   - Check Vercel deployment logs for frontend issues
   - Look for specific error messages related to environment variables

## Migration Notes

### From ChromaDB to Pinecone

If migrating from a ChromaDB setup:

1. **Update Environment Variables**
   - Remove ChromaDB-related variables
   - Add Pinecone-specific variables

2. **Update Application Code**
   - Ensure vector database code uses Pinecone client
   - Update embedding dimensions if necessary

3. **Data Migration**
   - Export existing vectors from ChromaDB
   - Import vectors to Pinecone index
   - Verify data integrity after migration

### Version Updates

When updating the application:

1. **Check for New Variables**
   - Review changelog for new environment variables
   - Update documentation and configuration

2. **Deprecated Variables**
   - Remove unused environment variables
   - Update platform configurations

3. **API Version Changes**
   - Update API keys if service versions change
   - Test compatibility with new API versions