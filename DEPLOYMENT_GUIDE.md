# RAG AI-Agent Deployment Guide

## Overview

This comprehensive guide will walk you through deploying the RAG AI-Agent application to production using a completely free deployment stack:

- **Frontend**: React/Vite application deployed on Vercel
- **Backend**: FastAPI application deployed on Hugging Face Spaces using Docker
- **Vector Database**: Pinecone cloud service
- **LLM Services**: Groq API for inference, OpenAI API for embeddings

## Prerequisites Checklist

Before starting the deployment process, ensure you have completed all the following prerequisites:

### Required Accounts

- [ ] **GitHub Account**: For code repository management
- [ ] **Pinecone Account**: For vector database service ([Sign up here](https://www.pinecone.io/))
- [ ] **Hugging Face Account**: For backend deployment ([Sign up here](https://huggingface.co/))
- [ ] **Vercel Account**: For frontend deployment ([Sign up here](https://vercel.com/))
- [ ] **Groq Account**: For LLM inference API ([Sign up here](https://console.groq.com/))
- [ ] **OpenAI Account**: For embeddings API ([Sign up here](https://platform.openai.com/))

### Required API Keys

- [ ] **Groq API Key**: Obtained from Groq Console
- [ ] **OpenAI API Key**: Obtained from OpenAI Platform
- [ ] **Pinecone API Key**: Obtained from Pinecone Dashboard

### Local Development Environment

- [ ] **Git**: Version control system installed
- [ ] **Python 3.9+**: For backend development and testing
- [ ] **Node.js 16+**: For frontend development and building
- [ ] **Docker** (optional): For local testing of containerized backend

## Environment Variables Reference

### Backend Environment Variables (Hugging Face Spaces)

The following environment variables must be configured as **Secrets** in your Hugging Face Space:

| Variable Name | Description | Required | Example Value |
|---------------|-------------|----------|---------------|
| `GROQ_API_KEY` | API key for Groq LLM service | Yes | `gsk_...` |
| `OPENAI_API_KEY` | API key for OpenAI embeddings | Yes | `sk-...` |
| `PINECONE_API_KEY` | API key for Pinecone vector database | Yes | `pcsk_...` |
| `PINECONE_INDEX_NAME` | Name of your Pinecone index | Yes | `rag-ai-agent` |

### Frontend Environment Variables (Vercel)

The frontend uses build-time environment variables that are configured in the `vercel.json` file:

| Variable Name | Description | Configuration Method |
|---------------|-------------|---------------------|
| `VITE_API_URL` | Backend API URL | Configured via proxy in `vercel.json` |

## Step-by-Step Deployment Instructions

### Step 1: Prepare Your Repository

1. **Fork or Clone the Repository**
   ```bash
   git clone https://github.com/DashMav/AgenticRAG.git
   cd AgenticRAG
   ```

2. **Verify Project Structure**
   Ensure your project has the following structure:
   ```
   RAG-AI-Agent/
   ├── app.py                 # FastAPI backend
   ├── agent.py              # AI agent logic
   ├── requirements.txt      # Python dependencies
   ├── Dockerfile           # Docker configuration
   ├── .env                 # Local environment variables (DO NOT COMMIT)
   └── agent-frontend/
       ├── package.json     # Frontend dependencies
       ├── vite.config.js   # Vite configuration
       ├── vercel.json      # Vercel deployment config
       └── src/             # React source code
   ```

### Step 2: Set Up Pinecone Vector Database

1. **Create Pinecone Account**
   - Go to [Pinecone](https://www.pinecone.io/) and sign up for a free account
   - Verify your email address

2. **Create a New Index**
   - In the Pinecone dashboard, click "Create Index"
   - **Index Name**: `rag-ai-agent` (or your preferred name)
   - **Dimensions**: `1536` (required for OpenAI embeddings)
   - **Metric**: `cosine` (recommended)
   - **Pod Type**: Select the free tier option
   - Click "Create Index"

3. **Get Your API Key**
   - Navigate to "API Keys" in the Pinecone dashboard
   - Copy your API key (starts with `pcsk_`)
   - Save this key securely for later use

### Step 3: Deploy Backend to Hugging Face Spaces

1. **Create a New Hugging Face Space**
   - Go to [Hugging Face](https://huggingface.co/) and log in
   - Click on your profile → "New Space"
   - **Space Name**: Choose a unique name (e.g., `your-username-rag-ai-agent`)
   - **License**: MIT
   - **Space SDK**: Select "Docker"
   - **Visibility**: Public (for free tier)
   - Click "Create Space"

2. **Configure Environment Variables (Secrets)**
   - In your new Space, go to "Settings" → "Variables and secrets"
   - Add the following secrets (click "New secret" for each):
     - **Name**: `GROQ_API_KEY`, **Value**: Your Groq API key
     - **Name**: `OPENAI_API_KEY`, **Value**: Your OpenAI API key
     - **Name**: `PINECONE_API_KEY`, **Value**: Your Pinecone API key
     - **Name**: `PINECONE_INDEX_NAME`, **Value**: `rag-ai-agent` (or your index name)

3. **Deploy Your Code**
   - Hugging Face will provide Git commands in your Space
   - Copy the repository URL from your Space
   - In your local project directory:
   ```bash
   cd RAG-AI-Agent
   git remote add hf https://huggingface.co/spaces/YOUR-USERNAME/YOUR-SPACE-NAME
   git push hf main
   ```

4. **Monitor Deployment**
   - Hugging Face will automatically build your Docker container
   - Monitor the build logs in the "Logs" tab
   - Once complete, your backend will be available at: `https://YOUR-USERNAME-YOUR-SPACE-NAME.hf.space`

### Step 4: Deploy Frontend to Vercel

1. **Update Vercel Configuration**
   - Open `RAG-AI-Agent/agent-frontend/vercel.json`
   - Update the destination URL to your Hugging Face Space URL:
   ```json
   {
     "rewrites": [
       {
         "source": "/api/:path*",
         "destination": "https://YOUR-USERNAME-YOUR-SPACE-NAME.hf.space/api/:path*"
       }
     ]
   }
   ```

2. **Commit and Push Changes**
   ```bash
   git add agent-frontend/vercel.json
   git commit -m "Update backend URL for production deployment"
   git push origin main
   ```

3. **Deploy to Vercel**
   - Go to [Vercel Dashboard](https://vercel.com/new)
   - Click "Import" next to your GitHub repository
   - **Framework Preset**: Vite (should be auto-detected)
   - **Root Directory**: `agent-frontend`
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `dist` (default)
   - Click "Deploy"

4. **Verify Deployment**
   - Vercel will provide a deployment URL (e.g., `https://your-app.vercel.app`)
   - The deployment should complete in 1-2 minutes

## Environment Variable Security Best Practices

### DO NOT Commit Sensitive Information

- Never commit `.env` files containing API keys to version control
- Use `.gitignore` to exclude environment files:
  ```gitignore
  .env
  .env.local
  .env.production
  ```

### Platform-Specific Security

1. **Hugging Face Spaces**
   - Use the "Secrets" feature for all sensitive environment variables
   - Secrets are encrypted and not visible in logs or public space information
   - Access secrets in your application using standard environment variable methods

2. **Vercel**
   - Frontend environment variables are build-time only
   - Use the proxy configuration in `vercel.json` to avoid exposing backend URLs
   - Never store API keys in frontend environment variables

3. **Pinecone**
   - Regularly rotate API keys
   - Use index-specific API keys when possible
   - Monitor usage in the Pinecone dashboard

## Verification Steps

After completing the deployment, verify that everything is working correctly:

### Backend Verification

1. **Check Health Endpoint**
   ```bash
   curl https://YOUR-USERNAME-YOUR-SPACE-NAME.hf.space/health
   ```
   Expected response: `{"status": "healthy"}`

2. **Test API Documentation**
   - Visit: `https://YOUR-USERNAME-YOUR-SPACE-NAME.hf.space/docs`
   - Verify that the FastAPI documentation loads correctly

### Frontend Verification

1. **Access Application**
   - Visit your Vercel deployment URL
   - Verify that the application loads without errors

2. **Test API Connectivity**
   - Open browser developer tools (F12)
   - Check that API requests are being proxied correctly to your backend
   - Look for successful responses from `/api/*` endpoints

### End-to-End Verification

1. **Document Upload Test**
   - Upload a test document (PDF, TXT, or DOCX)
   - Verify successful processing and storage

2. **Chat Functionality Test**
   - Start a new conversation
   - Ask a question about the uploaded document
   - Verify that responses are generated correctly

3. **Agent Mode Test**
   - Switch to Agent mode
   - Test advanced reasoning capabilities
   - Verify tool usage (calculator, current time)

## Troubleshooting Common Issues

### Backend Issues

**Problem**: Docker build fails on Hugging Face Spaces
- **Solution**: Check that all dependencies in `requirements.txt` are compatible
- **Check**: Review build logs in the Hugging Face Space logs tab

**Problem**: Environment variables not accessible
- **Solution**: Ensure secrets are properly configured in Space settings
- **Check**: Verify secret names match exactly with your code

**Problem**: Pinecone connection fails
- **Solution**: Verify API key and index name are correct
- **Check**: Ensure index dimensions are set to 1536

### Frontend Issues

**Problem**: API requests failing with CORS errors
- **Solution**: Verify `vercel.json` proxy configuration is correct
- **Check**: Ensure backend URL in proxy matches your Hugging Face Space URL

**Problem**: Build fails on Vercel
- **Solution**: Check that Node.js version is compatible (16+)
- **Check**: Verify all dependencies are properly listed in `package.json`

**Problem**: Frontend loads but API calls fail
- **Solution**: Check that proxy rewrite rules are working
- **Check**: Inspect network tab in browser developer tools

### General Issues

**Problem**: Application works locally but not in production
- **Solution**: Compare local and production environment variables
- **Check**: Ensure all required services (Pinecone, Groq, OpenAI) are accessible from production

**Problem**: Slow response times
- **Solution**: Check API rate limits and quotas for external services
- **Check**: Monitor usage in service dashboards (Groq, OpenAI, Pinecone)

## Next Steps

After successful deployment:

1. **Monitor Application Performance**
   - Set up monitoring for API response times
   - Track usage metrics in service dashboards

2. **Set Up Automated Updates**
   - Configure GitHub Actions for automated deployments
   - Set up dependency update notifications

3. **Scale Considerations**
   - Monitor Pinecone usage and upgrade plan if needed
   - Consider upgrading to paid tiers for higher API limits

4. **Security Maintenance**
   - Regularly rotate API keys
   - Monitor for security updates in dependencies
   - Review access logs periodically

## Support and Resources

- **Hugging Face Spaces Documentation**: [https://huggingface.co/docs/hub/spaces](https://huggingface.co/docs/hub/spaces)
- **Vercel Documentation**: [https://vercel.com/docs](https://vercel.com/docs)
- **Pinecone Documentation**: [https://docs.pinecone.io/](https://docs.pinecone.io/)
- **Groq API Documentation**: [https://console.groq.com/docs](https://console.groq.com/docs)
- **OpenAI API Documentation**: [https://platform.openai.com/docs](https://platform.openai.com/docs)

For project-specific issues, refer to the main README.md or contact the project maintainer.