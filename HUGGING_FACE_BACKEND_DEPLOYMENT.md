# Hugging Face Spaces Backend Deployment Guide

## Overview

This guide provides detailed instructions for deploying the RAG AI-Agent FastAPI backend to Hugging Face Spaces using Docker. Hugging Face Spaces offers free hosting for machine learning applications and is perfect for our FastAPI backend.

## Prerequisites

Before starting, ensure you have:
- A Hugging Face account ([Sign up here](https://huggingface.co/join))
- Git installed on your local machine
- All required API keys (Groq, OpenAI, Pinecone)
- A Pinecone index set up with 1536 dimensions

## Step 1: Account Creation and Setup

### 1.1 Create Hugging Face Account

1. Visit [huggingface.co](https://huggingface.co/)
2. Click "Sign Up" and create your account
3. Verify your email address
4. Complete your profile setup

### 1.2 Generate Access Token (Optional)

For programmatic access to your spaces:
1. Go to Settings → Access Tokens
2. Click "New token"
3. Name: `rag-ai-agent-deployment`
4. Role: `write`
5. Save the token securely

## Step 2: Create a New Space

### 2.1 Space Creation

1. **Navigate to Spaces**
   - From your Hugging Face dashboard, click "Spaces"
   - Click "Create new Space"

2. **Configure Space Settings**
   - **Owner**: Your username
   - **Space name**: Choose a unique name (e.g., `rag-ai-agent-backend`)
   - **License**: MIT
   - **Select the Space SDK**: **Docker** (This is crucial!)
   - **Visibility**: Public (required for free tier)
   - **Hardware**: CPU basic (free tier)

3. **Create Space**
   - Click "Create Space"
   - You'll be redirected to your new Space dashboard

### 2.2 Space Configuration

Your Space will have a unique URL: `https://huggingface.co/spaces/YOUR-USERNAME/YOUR-SPACE-NAME`

The application will be accessible at: `https://YOUR-USERNAME-YOUR-SPACE-NAME.hf.space`

## Step 3: Docker Configuration

### 3.1 Verify Dockerfile

Ensure your `Dockerfile` in the `RAG-AI-Agent/backend/` directory contains:

```dockerfile
# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY ./requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container at /app
COPY . /app/

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run app.py when the container launches
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3.2 Verify Requirements

Ensure your `requirements.txt` includes all necessary dependencies:

```txt
openai==1.76.0
uvicorn==0.34.2
langchain==0.3.24
langchain-community==0.3.22
fastapi==0.115.9
pypdf==5.4.0
python-dotenv==1.1.0
unstructured==0.17.2
langchain-openai==0.3.14
python-multipart==0.0.20
langchain-experimental==0.3.4
duckduckgo-search==8.0.1
SQLAlchemy==2.0.40
langchain-groq==0.2.0
pinecone-client==3.2.2
langchain-pinecone>=0.1.0
```

## Step 4: Environment Variables and Secrets Management

### 4.1 Understanding Hugging Face Secrets

Hugging Face Spaces provides a secure way to store sensitive information through "Secrets":
- Secrets are encrypted and not visible in logs
- They're accessible as environment variables in your application
- They're not visible to users viewing your Space

### 4.2 Configure Required Secrets

1. **Navigate to Space Settings**
   - Go to your Space dashboard
   - Click on "Settings" tab
   - Select "Variables and secrets"

2. **Add Each Required Secret**

   Click "New secret" for each of the following:

   **Secret 1: GROQ_API_KEY**
   - Name: `GROQ_API_KEY`
   - Value: Your Groq API key (starts with `gsk_`)
   - Click "Save"

   **Secret 2: OPENAI_API_KEY**
   - Name: `OPENAI_API_KEY`
   - Value: Your OpenAI API key (starts with `sk-`)
   - Click "Save"

   **Secret 3: PINECONE_API_KEY**
   - Name: `PINECONE_API_KEY`
   - Value: Your Pinecone API key (starts with `pcsk_`)
   - Click "Save"

   **Secret 4: PINECONE_INDEX_NAME**
   - Name: `PINECONE_INDEX_NAME`
   - Value: Your Pinecone index name (e.g., `rag-ai-agent`)
   - Click "Save"

### 4.3 Verify Secret Configuration

After adding all secrets, you should see:
- ✅ GROQ_API_KEY
- ✅ OPENAI_API_KEY  
- ✅ PINECONE_API_KEY
- ✅ PINECONE_INDEX_NAME

**Important**: Secret names are case-sensitive and must match exactly what your application expects.

## Step 5: Code Deployment

### 5.1 Prepare Your Repository

1. **Navigate to your project directory**
   ```bash
   cd RAG-AI-Agent/backend
   ```

2. **Ensure clean working directory**
   ```bash
   git status
   git add .
   git commit -m "Prepare for Hugging Face deployment"
   ```

### 5.2 Add Hugging Face Remote

1. **Get your Space's Git URL**
   - In your Space dashboard, you'll see Git commands
   - Copy the repository URL (looks like: `https://huggingface.co/spaces/YOUR-USERNAME/YOUR-SPACE-NAME`)

2. **Add Hugging Face as a remote**
   ```bash
   git remote add hf https://huggingface.co/spaces/YOUR-USERNAME/YOUR-SPACE-NAME
   ```

3. **Verify remote was added**
   ```bash
   git remote -v
   ```
   You should see both `origin` (your GitHub repo) and `hf` (Hugging Face Space).

### 5.3 Deploy to Hugging Face

1. **Push your code**
   ```bash
   git push hf main
   ```

   If you're using a different branch name:
   ```bash
   git push hf your-branch-name:main
   ```

2. **Authentication**
   - You'll be prompted for your Hugging Face username and password
   - Use your access token as the password if you created one

### 5.4 Monitor Deployment

1. **Watch Build Process**
   - Go to your Space dashboard
   - Click on "Logs" tab
   - Monitor the Docker build process

2. **Build Stages**
   - **Building**: Docker image is being created
   - **Starting**: Container is starting up
   - **Running**: Application is ready

3. **Expected Build Time**
   - Initial build: 3-5 minutes
   - Subsequent builds: 1-2 minutes (cached layers)

## Step 6: Deployment Verification

### 6.1 Check Space Status

1. **Space Dashboard**
   - Status should show "Running" with a green indicator
   - Build logs should show successful completion
   - No error messages in the logs

2. **Application URL**
   - Your backend is accessible at: `https://YOUR-USERNAME-YOUR-SPACE-NAME.hf.space`
   - This URL will be used by your frontend

### 6.2 Test Basic Connectivity

1. **Health Check** (if implemented)
   ```bash
   curl https://YOUR-USERNAME-YOUR-SPACE-NAME.hf.space/health
   ```

2. **API Documentation**
   - Visit: `https://YOUR-USERNAME-YOUR-SPACE-NAME.hf.space/docs`
   - Should display FastAPI's automatic documentation

3. **Root Endpoint**
   ```bash
   curl https://YOUR-USERNAME-YOUR-SPACE-NAME.hf.space/
   ```

## Step 7: CORS Configuration

### 7.1 Understanding CORS for Production

Your FastAPI application includes CORS middleware configured for development:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 7.2 Production CORS Considerations

For production, consider restricting origins to your frontend domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend.vercel.app",
        "http://localhost:3000",  # For local development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## Troubleshooting Common Issues

### Build Failures

**Issue**: Docker build fails with dependency errors
```
Solution:
1. Check requirements.txt for version conflicts
2. Review build logs for specific error messages
3. Ensure Python version compatibility (3.11)
```

**Issue**: Build timeout
```
Solution:
1. Reduce dependencies if possible
2. Use specific package versions instead of latest
3. Consider using a lighter base image
```

### Runtime Errors

**Issue**: Application starts but crashes immediately
```
Solution:
1. Check that all environment variables are set correctly
2. Verify Pinecone index exists and is accessible
3. Test API keys individually
```

**Issue**: Environment variables not accessible
```
Solution:
1. Verify secret names match exactly (case-sensitive)
2. Redeploy the Space after adding secrets
3. Check that secrets are saved properly
```

### API Connectivity Issues

**Issue**: External API calls fail (Groq, OpenAI, Pinecone)
```
Solution:
1. Verify API keys are valid and not expired
2. Check API service status pages
3. Ensure network connectivity from Hugging Face servers
```

**Issue**: CORS errors when frontend tries to connect
```
Solution:
1. Verify CORS middleware is properly configured
2. Check that frontend domain is allowed
3. Ensure preflight requests are handled
```

### Performance Issues

**Issue**: Slow response times
```
Solution:
1. Monitor API rate limits
2. Check Pinecone query performance
3. Consider caching strategies
```

**Issue**: Memory or CPU limits exceeded
```
Solution:
1. Optimize vector database queries
2. Implement request queuing
3. Consider upgrading to paid hardware tier
```

## Security Best Practices

### 7.1 Secret Management

- **Never commit API keys** to your repository
- **Use Hugging Face Secrets** for all sensitive data
- **Regularly rotate API keys** (monthly recommended)
- **Monitor API usage** for unusual activity

### 7.2 Application Security

- **Validate all inputs** to prevent injection attacks
- **Implement rate limiting** to prevent abuse
- **Use HTTPS only** for all communications
- **Log security events** for monitoring

### 7.3 Access Control

- **Keep Space public** only if necessary for free tier
- **Monitor Space access logs** regularly
- **Use minimal API key permissions** where possible
- **Implement authentication** for sensitive endpoints

## Maintenance and Updates

### 8.1 Regular Updates

1. **Dependency Updates**
   ```bash
   pip list --outdated
   # Update requirements.txt with new versions
   git commit -m "Update dependencies"
   git push hf main
   ```

2. **Security Patches**
   - Monitor security advisories for your dependencies
   - Update promptly when security issues are discovered

### 8.2 Monitoring

1. **Application Health**
   - Monitor Space status regularly
   - Set up external monitoring if needed
   - Check error rates in logs

2. **Resource Usage**
   - Monitor CPU and memory usage
   - Track API call volumes
   - Plan for scaling if needed

### 8.3 Backup Procedures

1. **Code Backup**
   - Maintain code in version control (GitHub)
   - Tag releases for easy rollback

2. **Configuration Backup**
   - Document all environment variables
   - Keep secure backup of API keys
   - Document Space configuration

## Next Steps

After successful backend deployment:

1. **Update Frontend Configuration**
   - Update `vercel.json` with your Hugging Face Space URL
   - Deploy frontend to Vercel

2. **End-to-End Testing**
   - Test complete user workflows
   - Verify frontend-backend communication
   - Test all API endpoints

3. **Production Monitoring**
   - Set up monitoring and alerting
   - Monitor performance metrics
   - Plan for scaling and optimization

## Support Resources

- **Hugging Face Spaces Documentation**: [https://huggingface.co/docs/hub/spaces](https://huggingface.co/docs/hub/spaces)
- **Docker Documentation**: [https://docs.docker.com/](https://docs.docker.com/)
- **FastAPI Documentation**: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
- **Hugging Face Community**: [https://discuss.huggingface.co/](https://discuss.huggingface.co/)

For project-specific issues, refer to the troubleshooting section above or check the main project documentation.
