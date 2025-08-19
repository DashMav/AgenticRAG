# RAG AI-Agent Scripts

This directory contains comprehensive scripts for deployment, validation, and testing of the RAG AI-Agent application.

## 🚀 Quick Start Scripts

### Master Deployment Validation
- **`master_deployment_validator.py`** - **[NEW]** Comprehensive deployment validation orchestrator
  - Runs all validation phases automatically
  - Generates detailed reports
  - Provides deployment readiness assessment
  - **Usage**: `python scripts/master_deployment_validator.py --generate-report`

### Interactive Pre-Flight Checklist
- **`pre_flight_checklist.py`** - **[NEW]** Interactive checklist for deployment preparation
  - Step-by-step guidance for first-time users
  - Auto-checking of verifiable items
  - Progress saving and resuming
  - **Usage**: `python scripts/pre_flight_checklist.py --auto-check --save-progress`

### Deployment Success Reporter
- **`deployment_success_reporter.py`** - **[NEW]** Post-deployment validation and success reporting
  - Verifies deployed application health
  - Provides next steps guidance
  - Generates success reports
  - **Usage**: `python scripts/deployment_success_reporter.py --backend-url URL --frontend-url URL`

## 📋 Script Categories

### Validation Scripts
- `validate_api_keys.py` - Validates API connectivity for Groq, OpenAI, and Pinecone
- `validate_environment.py` - Checks local development environment setup
- `validate_pinecone.py` - Validates Pinecone configuration and connectivity
- `test_network_connectivity.py` - Tests network connectivity to deployment platforms

### Deployment Scripts
- `deploy_backend.py` - Automates backend deployment to Hugging Face Spaces
- `deploy_frontend.py` - Automates frontend deployment to Vercel

### Testing Scripts
- `test_core_functionality.py` - Tests core application features
- `test_e2e_workflows.py` - End-to-end workflow testing
- `run_post_deployment_tests.py` - Comprehensive post-deployment testing
- `test_fastapi_deployment.py` - FastAPI-specific deployment tests
- `test_frontend_backend_integration.py` - Frontend-backend integration tests

### Utility Scripts
- `diagnose_issues.py` - Diagnoses common deployment problems
- `health_check.py` - Performs health checks on deployed services
- `pinecone_utilities.py` - Pinecone management utilities
- `error_reporter.py` - Error reporting and logging utilities
- `run_diagnostics.py` - Comprehensive diagnostic runner

### Verification Scripts
- `verify_backend_deployment.py` - Backend deployment verification
- `verify_frontend_deployment.py` - Frontend deployment verification
- `vector_data_validator.py` - Vector database data validation

## 🎯 Recommended Workflow

### For First-Time Users:
1. **`python scripts/pre_flight_checklist.py --auto-check --save-progress`**
2. **`python scripts/master_deployment_validator.py --generate-report`**
3. Deploy using platform-specific guides
4. **`python scripts/deployment_success_reporter.py --backend-url URL --frontend-url URL`**

### For Experienced Users:
1. **`python scripts/master_deployment_validator.py`**
2. Deploy using automated scripts
3. **`python scripts/run_post_deployment_tests.py`**

### For Troubleshooting:
1. **`python scripts/diagnose_issues.py`**
2. **`python scripts/run_diagnostics.py`**
3. Check specific validation scripts

## 🔧 Usage Examples

### Master Validation
```bash
# Quick validation
python scripts/master_deployment_validator.py

# Detailed validation with report
python scripts/master_deployment_validator.py --generate-report --verbose

# Use config file for API keys
python scripts/master_deployment_validator.py --config scripts/config.json
```

### Interactive Checklist
```bash
# Full interactive experience
python scripts/pre_flight_checklist.py --auto-check --save-progress

# Resume previous session
python scripts/pre_flight_checklist.py --save-progress
```

### Success Reporting
```bash
# Basic health check
python scripts/deployment_success_reporter.py

# Full report with URLs
python scripts/deployment_success_reporter.py \
  --backend-url https://your-backend.hf.space \
  --frontend-url https://your-frontend.vercel.app \
  --full-report
```

### Individual Validations
```bash
# API key validation
python scripts/validate_api_keys.py

# Environment validation
python scripts/validate_environment.py --verbose

# Pinecone validation
python scripts/validate_pinecone.py
```

### Diagnostic Scripts
```bash
# Run all diagnostics
python scripts/run_diagnostics.py --all

# Quick diagnostics
python scripts/run_diagnostics.py --quick

# Test specific backend
python scripts/run_diagnostics.py --backend-url https://your-backend.hf.space
```

## ⚙️ Configuration

### Config File Support
Many scripts support configuration files for API keys and settings:

```bash
# Create sample config
python scripts/validate_api_keys.py --create-sample-config config.json

# Use config file
python scripts/validate_api_keys.py --config config.json
```

### Environment Variables
All scripts support environment variables:
- `GROQ_API_KEY`
- `OPENAI_API_KEY`
- `PINECONE_API_KEY`
- `PINECONE_INDEX_NAME`

## 📊 Reports and Logs

Scripts generate various reports:
- `deployment_validation_report.json` - Master validation results
- `deployment_success_report.json` - Success verification results
- `pre_flight_progress.json` - Checklist progress (if --save-progress used)
- `diagnostic_report.json` - Comprehensive diagnostic results
- `error_report_YYYYMMDD_HHMMSS.json` - Error and log collection

## 🔍 Help and Documentation

Get help for any script:
```bash
python scripts/script_name.py --help
```

## 📚 Additional Resources

For detailed deployment instructions, see:
- `../DEPLOYMENT_GUIDE.md` - Complete deployment guide
- `../DEPLOYMENT_CHECKLIST.md` - Step-by-step checklist
- `../TROUBLESHOOTING_GUIDE.md` - Common issues and solutions
- `../ENVIRONMENT_VARIABLES.md` - Environment configuration

## 🆘 Support

If you encounter issues:
1. Run the diagnostic scripts first
2. Check the troubleshooting guide
3. Review the generated reports for detailed error information
4. Ensure all prerequisites are met using the validation scripts

---

## Legacy Diagnostic Scripts Documentation

### `run_diagnostics.py` - Unified Diagnostic Runner

**Purpose**: Provides a single interface to run all diagnostic utilities.

**Usage**:
```bash
python scripts/run_diagnostics.py [OPTIONS]
```

**Options**:
- `--all`: Run all diagnostic tests (default)
- `--quick`: Run quick diagnostic tests only
- `--backend-url URL`: Test connectivity to specific backend
- `--verbose, -v`: Enable verbose output

### `diagnose_issues.py` - Comprehensive Diagnostic Tool

**Purpose**: Performs detailed diagnostics of the entire RAG AI-Agent system.

**What it checks**:
- Environment variables configuration
- File structure and required files
- Python dependencies and versions
- API service connectivity (Groq, OpenAI, Pinecone)
- Backend health and endpoints
- Network connectivity to external services
- System performance (disk space, memory)
- Vercel configuration

### `test_network_connectivity.py` - Network Connectivity Tester

**Purpose**: Tests network connectivity to all external services.

**Services tested**:
- Groq API (`api.groq.com`)
- OpenAI API (`api.openai.com`)
- Pinecone API (`api.pinecone.io`)
- Hugging Face (`huggingface.co`)
- Vercel (`vercel.com`)
- GitHub (`github.com`)

### `error_reporter.py` - Error Reporting and Log Collection

**Purpose**: Collects comprehensive error information and system logs.

**What it collects**:
- System information (OS, Python version, hardware)
- Environment variables (masked for security)
- Application logs from multiple sources
- Recent errors from log files
- Diagnostic test results
- Performance metrics
- Configuration file status