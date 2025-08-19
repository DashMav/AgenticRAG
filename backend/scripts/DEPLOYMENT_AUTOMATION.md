# Deployment Automation Scripts

This directory contains automated deployment scripts for the RAG AI-Agent application, providing one-click deployment to both Hugging Face Spaces (backend) and Vercel (frontend).

## Overview

The deployment automation consists of two main scripts:

- **`deploy_backend.py`**: Automates Hugging Face Spaces deployment for the FastAPI backend
- **`deploy_frontend.py`**: Automates Vercel deployment for the React frontend

Both scripts handle environment setup, configuration management, deployment monitoring, and verification.

## Quick Start

### 1. Backend Deployment

```bash
# Create configuration file
python scripts/deploy_backend.py --create-config

# Edit the configuration with your values
# backend_deployment_config.json

# Deploy to Hugging Face Spaces
python scripts/deploy_backend.py --config backend_deployment_config.json --verbose
```

### 2. Frontend Deployment

```bash
# Create configuration file
python scripts/deploy_frontend.py --create-config

# Edit the configuration with your backend URL
# frontend_deployment_config.json

# Deploy to Vercel
python scripts/deploy_frontend.py --config frontend_deployment_config.json --verbose
```

## Backend Deployment (`deploy_backend.py`)

### Features

- ✅ **Automated Git Configuration**: Sets up Hugging Face remote repository
- ✅ **Environment Variable Management**: Handles secure API key configuration
- ✅ **Docker Validation**: Ensures proper Docker configuration for HF Spaces
- ✅ **Deployment Monitoring**: Tracks deployment progress and status
- ✅ **Health Checks**: Verifies deployment is live and accessible
- ✅ **Comprehensive Reporting**: Generates detailed deployment reports

### Prerequisites

- Git installed and configured
- Hugging Face account and Space created
- Required API keys (Groq, OpenAI, Pinecone)
- Python 3.7+ with required dependencies

### Configuration

Create a configuration file using:

```bash
python scripts/deploy_backend.py --create-config
```

This creates `backend_deployment_config.json`:

```json
{
  "space_name": "your-rag-ai-agent",
  "username": "your-hf-username",
  "git_email": "your-email@example.com",
  "git_name": "Your Name",
  "environment_variables": {
    "GROQ_API_KEY": "your-groq-api-key",
    "OPENAI_API_KEY": "your-openai-api-key",
    "PINECONE_API_KEY": "your-pinecone-api-key",
    "PINECONE_INDEX_NAME": "your-pinecone-index"
  },
  "optional_variables": {
    "PINECONE_ENVIRONMENT": "",
    "MAX_FILE_SIZE": "10",
    "EMBEDDING_MODEL": "text-embedding-ada-002"
  },
  "deployment_timeout": 300,
  "health_check_timeout": 120
}
```

### Usage Examples

```bash
# Validate configuration without deploying
python scripts/deploy_backend.py --config backend_deployment_config.json --dry-run

# Deploy with verbose output
python scripts/deploy_backend.py --config backend_deployment_config.json --verbose

# Deploy with default configuration (uses environment variables)
python scripts/deploy_backend.py --verbose
```

### Command Line Options

- `--config, -c`: Path to configuration file
- `--verbose, -v`: Enable verbose output
- `--create-config`: Create sample configuration file
- `--dry-run`: Validate configuration without deploying

## Frontend Deployment (`deploy_frontend.py`)

### Features

- ✅ **Automated Build Process**: Handles npm install and build
- ✅ **Proxy Configuration**: Sets up API proxy for backend communication
- ✅ **Vercel CLI Integration**: Automated deployment using Vercel CLI
- ✅ **Build Optimization**: Configures production build settings
- ✅ **Deployment Verification**: Tests site accessibility and API proxy
- ✅ **Comprehensive Reporting**: Generates detailed deployment reports

### Prerequisites

- Node.js 16+ and npm installed
- Vercel account (CLI will prompt for login)
- Backend deployed and accessible
- Frontend built and tested locally

### Configuration

Create a configuration file using:

```bash
python scripts/deploy_frontend.py --create-config
```

This creates `frontend_deployment_config.json`:

```json
{
  "project_name": "rag-ai-agent-frontend",
  "backend_url": "https://your-username-your-space-name.hf.space",
  "vercel_org": "",
  "build_command": "npm run build",
  "output_directory": "dist",
  "install_command": "npm install",
  "node_version": "18.x",
  "environment_variables": {
    "VITE_APP_NAME": "RAG AI-Agent",
    "VITE_APP_VERSION": "1.0.0"
  },
  "custom_domain": "",
  "deployment_timeout": 600,
  "health_check_timeout": 120
}
```

### Usage Examples

```bash
# Validate configuration without deploying
python scripts/deploy_frontend.py --config frontend_deployment_config.json --dry-run

# Build only (no deployment)
python scripts/deploy_frontend.py --config frontend_deployment_config.json --build-only

# Deploy with verbose output
python scripts/deploy_frontend.py --config frontend_deployment_config.json --verbose

# Deploy with default configuration
python scripts/deploy_frontend.py --verbose
```

### Command Line Options

- `--config, -c`: Path to configuration file
- `--verbose, -v`: Enable verbose output
- `--create-config`: Create sample configuration file
- `--dry-run`: Validate configuration without deploying
- `--build-only`: Only build the application, don't deploy

## Complete Deployment Workflow

### Step 1: Prepare Environment

```bash
# Ensure you're in the project root
cd RAG-AI-Agent

# Install Python dependencies for scripts
pip install requests

# Ensure Node.js and npm are installed
node --version
npm --version
```

### Step 2: Deploy Backend

```bash
# Create and configure backend deployment
python scripts/deploy_backend.py --create-config
# Edit backend_deployment_config.json with your values

# Deploy backend
python scripts/deploy_backend.py --config backend_deployment_config.json --verbose
```

### Step 3: Configure Environment Variables

After backend deployment, configure environment variables in your Hugging Face Space:

1. Go to your Space settings
2. Add secrets for all API keys
3. Restart the Space if needed

### Step 4: Deploy Frontend

```bash
# Create and configure frontend deployment
python scripts/deploy_frontend.py --create-config
# Edit frontend_deployment_config.json with your backend URL

# Deploy frontend
python scripts/deploy_frontend.py --config frontend_deployment_config.json --verbose
```

### Step 5: Verify Deployment

Both scripts generate deployment reports with verification results. Check:

- Backend health endpoints
- Frontend site accessibility
- API proxy functionality
- End-to-end communication

## Troubleshooting

### Common Backend Issues

**Git Authentication Errors**
```bash
# Configure Git credentials
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"

# Use personal access token for Hugging Face
git config --global credential.helper store
```

**Docker Build Failures**
```bash
# Check Dockerfile and requirements.txt
# Ensure all dependencies are compatible
# Review Hugging Face Space build logs
```

**Environment Variable Issues**
```bash
# Verify all required API keys are set
# Check Hugging Face Space secrets configuration
# Ensure no extra spaces or special characters
```

### Common Frontend Issues

**Vercel CLI Not Found**
```bash
# Install Vercel CLI globally
npm install -g vercel

# Or let the script install it automatically
python scripts/deploy_frontend.py --verbose
```

**Build Failures**
```bash
# Clear node_modules and reinstall
cd agent-frontend
rm -rf node_modules package-lock.json
npm install

# Check for dependency conflicts
npm audit fix
```

**API Proxy Issues**
```bash
# Verify backend URL is correct and accessible
# Check vercel.json proxy configuration
# Test backend endpoints directly
```

### Script-Specific Issues

**Configuration File Errors**
```bash
# Recreate configuration file
python scripts/deploy_backend.py --create-config
python scripts/deploy_frontend.py --create-config

# Validate JSON syntax
python -m json.tool backend_deployment_config.json
```

**Permission Errors**
```bash
# Make scripts executable (Linux/Mac)
chmod +x scripts/deploy_*.py

# Or run with python explicitly
python scripts/deploy_backend.py
```

**Timeout Issues**
```bash
# Increase timeout in configuration file
{
  "deployment_timeout": 900,
  "health_check_timeout": 300
}
```

## Advanced Configuration

### Custom Build Settings

For the frontend, you can customize build settings in the configuration:

```json
{
  "build_command": "npm run build:production",
  "environment_variables": {
    "VITE_API_TIMEOUT": "30000",
    "VITE_DEBUG_MODE": "false"
  }
}
```

### Multiple Environment Support

Create different configuration files for different environments:

```bash
# Development
python scripts/deploy_frontend.py --config config/dev-frontend.json

# Staging
python scripts/deploy_frontend.py --config config/staging-frontend.json

# Production
python scripts/deploy_frontend.py --config config/prod-frontend.json
```

### CI/CD Integration

Use the scripts in your CI/CD pipeline:

```yaml
# GitHub Actions example
- name: Deploy Backend
  run: |
    python scripts/deploy_backend.py --config .github/configs/backend.json --verbose
    
- name: Deploy Frontend
  run: |
    python scripts/deploy_frontend.py --config .github/configs/frontend.json --verbose
```

## Monitoring and Maintenance

### Deployment Reports

Both scripts generate comprehensive reports:

- `deployment_report_YYYYMMDD_HHMMSS.json`: Backend deployment details
- `frontend_deployment_report_YYYYMMDD_HHMMSS.json`: Frontend deployment details

### Health Monitoring

Set up monitoring for your deployed applications:

```bash
# Use existing health check scripts
python scripts/health_check.py --backend-url https://your-backend.hf.space
python scripts/verify_frontend_deployment.py --frontend-url https://your-app.vercel.app
```

### Update Procedures

To update deployments:

```bash
# Update backend
git add .
git commit -m "Update backend"
python scripts/deploy_backend.py --config backend_deployment_config.json

# Update frontend
python scripts/deploy_frontend.py --config frontend_deployment_config.json
```

## Support and Resources

### Documentation Links

- [Hugging Face Spaces Documentation](https://huggingface.co/docs/hub/spaces)
- [Vercel Documentation](https://vercel.com/docs)
- [Project Deployment Guide](../DEPLOYMENT_GUIDE.md)
- [Troubleshooting Guide](../TROUBLESHOOTING_GUIDE.md)

### Getting Help

1. Check the deployment reports for detailed error information
2. Review the troubleshooting section above
3. Consult the main project documentation
4. Check the logs generated by the scripts

### Contributing

To improve the deployment automation:

1. Follow the existing code patterns
2. Add comprehensive error handling
3. Update documentation for new features
4. Test with various configurations

---

For more detailed information about manual deployment processes, see the main [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md) file.