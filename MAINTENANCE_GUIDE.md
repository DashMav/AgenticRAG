# RAG AI Agent - Maintenance and Update Guide

## Overview

This guide provides comprehensive procedures for maintaining, updating, and managing the RAG AI Agent application in production. It covers dependency updates, security patches, backup procedures, and recovery processes.

## Table of Contents

1. [Regular Maintenance Schedule](#regular-maintenance-schedule)
2. [Dependency Updates](#dependency-updates)
3. [Security Patches](#security-patches)
4. [Backup Procedures](#backup-procedures)
5. [Recovery Procedures](#recovery-procedures)
6. [Monitoring and Health Checks](#monitoring-and-health-checks)
7. [Rollback Procedures](#rollback-procedures)
8. [Environment Variable Management](#environment-variable-management)

## Regular Maintenance Schedule

### Weekly Tasks
- [ ] Check application health and performance metrics
- [ ] Review error logs and resolve any issues
- [ ] Verify backup integrity
- [ ] Monitor API usage and rate limits

### Monthly Tasks
- [ ] Update dependencies (following procedures below)
- [ ] Review and rotate API keys if necessary
- [ ] Check for security vulnerabilities
- [ ] Update documentation if needed

### Quarterly Tasks
- [ ] Comprehensive security audit
- [ ] Performance optimization review
- [ ] Disaster recovery testing
- [ ] Update deployment procedures if needed

## Dependency Updates

### Backend Dependencies (Python)

#### 1. Check for Updates

```bash
# Navigate to the backend directory
cd RAG-AI-Agent

# Check for outdated packages
pip list --outdated

# Or use pip-check for better formatting
pip install pip-check
pip-check
```

#### 2. Update Dependencies Safely

```bash
# Create a backup of current requirements
cp requirements.txt requirements.txt.backup

# Update specific packages (recommended approach)
pip install --upgrade openai
pip install --upgrade fastapi
pip install --upgrade uvicorn

# Generate new requirements file
pip freeze > requirements_new.txt

# Compare changes
diff requirements.txt requirements_new.txt
```

#### 3. Test Updates Locally

```bash
# Install updated dependencies
pip install -r requirements_new.txt

# Run local tests
python -m pytest tests/ -v

# Test API endpoints
python validate_deployment.py
```

#### 4. Deploy Updated Backend

```bash
# Update requirements.txt with tested versions
mv requirements_new.txt requirements.txt

# Commit changes
git add requirements.txt
git commit -m "Update backend dependencies - [date]"
git push

# Hugging Face Spaces will automatically rebuild
# Monitor deployment at: https://huggingface.co/spaces/[your-username]/[space-name]
```

### Frontend Dependencies (Node.js)

#### 1. Check for Updates

```bash
# Navigate to frontend directory
cd RAG-AI-Agent/agent-frontend

# Check for outdated packages
npm outdated

# Or use npm-check-updates
npx npm-check-updates
```

#### 2. Update Dependencies

```bash
# Update minor and patch versions
npm update

# For major version updates (be cautious)
npx npm-check-updates -u
npm install
```

#### 3. Test Frontend Updates

```bash
# Run development server
npm run dev

# Build for production
npm run build

# Test build locally
npm run preview
```

#### 4. Deploy Updated Frontend

```bash
# Commit changes
git add package.json package-lock.json
git commit -m "Update frontend dependencies - [date]"
git push

# Vercel will automatically redeploy
# Monitor at: https://vercel.com/dashboard
```

## Security Patches

### Critical Security Updates

#### Immediate Response (within 24 hours)

1. **Identify the vulnerability**
   ```bash
   # Check for known vulnerabilities
   pip audit  # For Python
   npm audit  # For Node.js
   ```

2. **Apply security patches**
   ```bash
   # Update specific vulnerable package
   pip install --upgrade [package-name]
   # or
   npm install [package-name]@latest
   ```

3. **Emergency deployment**
   ```bash
   # Skip normal testing for critical security issues
   git add .
   git commit -m "SECURITY: Fix [vulnerability-name] - [CVE-number]"
   git push
   ```

4. **Verify fix**
   ```bash
   # Re-run security audit
   pip audit
   npm audit
   ```

### Regular Security Updates

#### Monthly Security Review

```bash
# Run comprehensive security checks
pip audit --desc
npm audit --audit-level moderate

# Check for outdated packages with known vulnerabilities
safety check  # Install with: pip install safety
```

#### API Key Rotation

1. **Generate new API keys**
   - Groq API: https://console.groq.com/keys
   - OpenAI API: https://platform.openai.com/api-keys
   - Pinecone: https://app.pinecone.io/

2. **Update environment variables**
   ```bash
   # Hugging Face Spaces
   # Go to Settings > Repository secrets
   # Update: GROQ_API_KEY, OPENAI_API_KEY, PINECONE_API_KEY
   
   # Vercel
   # Go to Project Settings > Environment Variables
   # Update: VITE_API_URL (if changed)
   ```

3. **Test with new keys**
   ```bash
   python validate_deployment.py
   ```

## Backup Procedures

### Data Backup Strategy

#### 1. Pinecone Vector Database Backup

The Pinecone backup script is available at `scripts/backup_pinecone.py`. This script creates comprehensive backups of Pinecone index metadata and statistics.

**Usage:**
```bash
# Create new backup
python scripts/backup_pinecone.py

# List all backups
python scripts/backup_pinecone.py list

# Verify backup integrity
python scripts/backup_pinecone.py verify backups/pinecone_backup_20241217_143022.json

# Show help
python scripts/backup_pinecone.py help
```

**Features:**
- Comprehensive index metadata backup
- Statistics and configuration preservation
- Backup verification and integrity checks
- Automatic backup listing and management
- Cross-platform compatibility

#### 2. Application Configuration Backup

The configuration backup scripts are available for both Unix/Linux and Windows systems:

**Unix/Linux/macOS:**
```bash
# Create configuration backup
./scripts/backup_config.sh

# Restore from backup
./scripts/restore_config.sh backups/20241217_143022
```

**Windows:**
```cmd
# Create configuration backup
scripts\backup_config.bat

# Restore from backup (manual process - see restore_config.sh for reference)
```

**Features:**
- Automatic backup of all configuration files
- Backup verification with checksums
- Backup manifest with system information
- Automatic cleanup of old backups (keeps last 10)
- Cross-platform compatibility

#### 3. Automated Backup Schedule

```bash
# Add to crontab for automated backups
# Run: crontab -e

# Daily backup at 2 AM
0 2 * * * /path/to/backup_config.sh

# Weekly Pinecone backup on Sundays at 3 AM
0 3 * * 0 cd /path/to/project && python backup_pinecone.py
```

### Backup Verification

```bash
# Create verification script: verify_backup.py
import json
import os
from datetime import datetime, timedelta

def verify_backup_integrity():
    """Verify backup files are recent and valid"""
    
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        print("❌ No backup directory found")
        return False
    
    # Check for recent backups (within last 7 days)
    recent_backups = []
    cutoff_date = datetime.now() - timedelta(days=7)
    
    for backup_folder in os.listdir(backup_dir):
        try:
            backup_date = datetime.strptime(backup_folder, "%Y%m%d_%H%M%S")
            if backup_date > cutoff_date:
                recent_backups.append(backup_folder)
        except ValueError:
            continue
    
    if not recent_backups:
        print("❌ No recent backups found (within 7 days)")
        return False
    
    print(f"✅ Found {len(recent_backups)} recent backups")
    
    # Verify backup contents
    latest_backup = max(recent_backups)
    backup_path = os.path.join(backup_dir, latest_backup)
    
    required_files = ["requirements.txt", "Dockerfile", "package.json", "manifest.txt"]
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(os.path.join(backup_path, file)):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files in latest backup: {missing_files}")
        return False
    
    print("✅ Backup integrity verified")
    return True

if __name__ == "__main__":
    verify_backup_integrity()
```

## Recovery Procedures

### Application Recovery

#### 1. Quick Recovery (Configuration Issues)

```bash
# Restore from latest backup
LATEST_BACKUP=$(ls -t backups/ | head -n1)
echo "Restoring from backup: $LATEST_BACKUP"

# Restore configuration files
cp backups/$LATEST_BACKUP/requirements.txt .
cp backups/$LATEST_BACKUP/Dockerfile .
cp backups/$LATEST_BACKUP/package.json agent-frontend/
cp backups/$LATEST_BACKUP/package-lock.json agent-frontend/

# Redeploy
git add .
git commit -m "RECOVERY: Restore from backup $LATEST_BACKUP"
git push
```

#### 2. Full Recovery (Complete Failure)

```bash
# 1. Clone fresh repository
git clone https://github.com/[username]/RAG-AI-Agent.git rag-ai-agent-recovery
cd rag-ai-agent-recovery

# 2. Restore from backup
BACKUP_DIR="/path/to/backups/[latest-backup]"
cp $BACKUP_DIR/* .
cp $BACKUP_DIR/package.json agent-frontend/
cp $BACKUP_DIR/package-lock.json agent-frontend/

# 3. Restore environment variables
# Manually configure in Hugging Face Spaces and Vercel

# 4. Test recovery
python validate_deployment.py
```

### Database Recovery

#### Pinecone Index Recreation

The Pinecone recovery script is available at `scripts/recover_pinecone.py`. This script helps recover from Pinecone index issues by recreating the index from backup metadata.

**Usage:**
```bash
# Interactive recovery (recommended)
python scripts/recover_pinecone.py

# Recover from specific backup
python scripts/recover_pinecone.py recover backups/pinecone_backup_20241217_143022.json

# Force recovery (skip confirmations)
python scripts/recover_pinecone.py recover backups/pinecone_backup_20241217_143022.json --force

# List available backups
python scripts/recover_pinecone.py list

# Show help
python scripts/recover_pinecone.py help
```

**Features:**
- Interactive recovery process with backup selection
- Automatic index deletion and recreation
- Backup validation and verification
- Force mode for automated recovery
- Comprehensive error handling and logging

**Important Notes:**
- Vector data cannot be recovered and must be re-uploaded
- Keep your document sources for full recovery
- The recovery process recreates the index structure only

## Monitoring and Health Checks

### Automated Health Monitoring

The health monitoring script is available at `scripts/health_monitor.py`. This script provides comprehensive monitoring of all application components.

**Usage:**
```bash
# Single health check run
python scripts/health_monitor.py

# Continuous monitoring (5-minute intervals)
python scripts/health_monitor.py --continuous

# Custom monitoring interval (10 minutes)
python scripts/health_monitor.py --continuous --interval 600

# Disable email alerts
python scripts/health_monitor.py --no-alerts

# Custom log file
python scripts/health_monitor.py --log-file custom_health.log

# Use custom configuration file
python scripts/health_monitor.py --config health_config.json

# Show help
python scripts/health_monitor.py --help
```

**Features:**
- Comprehensive health checks for all services (Backend, Frontend, Pinecone, Groq, OpenAI)
- Response time monitoring and performance metrics
- Email alerts for service failures
- Continuous monitoring with configurable intervals
- JSON logging for analysis and reporting
- Configurable timeouts and thresholds
- Cross-platform compatibility

**Monitored Services:**
- **Backend API**: Health endpoint, response time, status codes
- **Frontend**: Availability, response time, content validation
- **Pinecone**: Connectivity, index statistics, vector counts
- **Groq API**: Authentication, model availability, response time
- **OpenAI API**: Authentication, model availability, response time

### Performance Monitoring

```python
# Create performance monitoring script: performance_monitor.py
import requests
import time
import json
from datetime import datetime
import statistics

def measure_api_performance():
    """Measure API response times"""
    backend_url = os.getenv("BACKEND_URL")
    endpoints = [
        "/health",
        "/api/chats",
        "/api/upload"  # Test with small file
    ]
    
    results = {}
    
    for endpoint in endpoints:
        response_times = []
        
        for _ in range(5):  # Test 5 times
            start_time = time.time()
            try:
                if endpoint == "/api/upload":
                    # Skip upload test for now
                    continue
                
                response = requests.get(f"{backend_url}{endpoint}", timeout=30)
                end_time = time.time()
                
                if response.status_code == 200:
                    response_times.append(end_time - start_time)
            except:
                response_times.append(None)
        
        valid_times = [t for t in response_times if t is not None]
        
        if valid_times:
            results[endpoint] = {
                "avg_response_time": statistics.mean(valid_times),
                "max_response_time": max(valid_times),
                "min_response_time": min(valid_times),
                "success_rate": len(valid_times) / len(response_times)
            }
        else:
            results[endpoint] = {
                "avg_response_time": None,
                "success_rate": 0
            }
    
    return results

def log_performance_metrics():
    """Log performance metrics to file"""
    metrics = measure_api_performance()
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "metrics": metrics
    }
    
    with open("performance_log.json", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    print(f"Performance metrics logged: {datetime.now()}")
    
    # Check for performance issues
    for endpoint, data in metrics.items():
        if data["avg_response_time"] and data["avg_response_time"] > 5.0:
            print(f"⚠️  Slow response detected for {endpoint}: {data['avg_response_time']:.2f}s")
        
        if data["success_rate"] < 0.8:
            print(f"⚠️  Low success rate for {endpoint}: {data['success_rate']:.2%}")

if __name__ == "__main__":
    log_performance_metrics()
```

## Rollback Procedures

### Rollback Procedures

The rollback script is available at `scripts/rollback.sh` and provides multiple rollback options for different scenarios.

**Usage:**
```bash
# Quick rollback to last stable commit
./scripts/rollback.sh quick

# Interactive selective rollback
./scripts/rollback.sh selective

# Rollback backend only
./scripts/rollback.sh backend

# Rollback frontend only
./scripts/rollback.sh frontend

# Rollback from configuration backup
./scripts/rollback.sh config

# List recent commits for manual rollback
./scripts/rollback.sh list-commits

# Show help
./scripts/rollback.sh help
```

**Rollback Options:**

1. **Quick Rollback**: Automatically finds and rolls back to the last stable commit
2. **Selective Rollback**: Interactive process to choose specific files, commits, or components
3. **Component Rollback**: Rollback specific parts (backend/frontend) independently
4. **Configuration Rollback**: Restore from configuration backups
5. **Manual Rollback**: List commits for manual selection

**Features:**
- Automatic backup creation before rollback
- Interactive confirmation prompts
- Rollback branch creation for safety
- Component-specific rollback options
- Integration with configuration backup system
- Comprehensive error handling and validation

### Staged Rollback

```bash
# For more controlled rollback
# 1. Rollback backend only
git checkout HEAD~1 -- requirements.txt Dockerfile app.py
git commit -m "ROLLBACK: Backend to previous version"
git push

# 2. Test backend
python validate_deployment.py

# 3. Rollback frontend if needed
git checkout HEAD~1 -- agent-frontend/
git commit -m "ROLLBACK: Frontend to previous version"
git push
```

## Environment Variable Management

### Environment Variable Audit

```python
# Create env audit script: audit_env_vars.py
import os
import json
from datetime import datetime

def audit_environment_variables():
    """Audit and document current environment variables"""
    
    required_vars = {
        "GROQ_API_KEY": "Groq API key for LLM inference",
        "OPENAI_API_KEY": "OpenAI API key for embeddings",
        "PINECONE_API_KEY": "Pinecone API key for vector database",
        "PINECONE_INDEX_NAME": "Name of the Pinecone index",
        "PINECONE_ENVIRONMENT": "Pinecone environment (optional)"
    }
    
    audit_results = {
        "timestamp": datetime.now().isoformat(),
        "variables": {}
    }
    
    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        audit_results["variables"][var_name] = {
            "description": description,
            "is_set": value is not None,
            "value_length": len(value) if value else 0,
            "masked_value": f"{value[:4]}...{value[-4:]}" if value and len(value) > 8 else "Not set"
        }
    
    # Save audit results
    with open("env_audit.json", "w") as f:
        json.dump(audit_results, f, indent=2)
    
    print("Environment Variable Audit Results:")
    print("=" * 40)
    
    for var_name, info in audit_results["variables"].items():
        status = "✅ SET" if info["is_set"] else "❌ MISSING"
        print(f"{var_name}: {status}")
        if info["is_set"]:
            print(f"  Value: {info['masked_value']}")
        print(f"  Description: {info['description']}")
        print()

if __name__ == "__main__":
    audit_environment_variables()
```

### Environment Variable Rotation

```bash
# Create rotation script: rotate_api_keys.sh
#!/bin/bash

echo "🔄 Starting API key rotation..."

# Backup current environment variables
echo "Creating backup of current environment variables..."
python audit_env_vars.py

echo "Please update the following API keys:"
echo "1. Groq API: https://console.groq.com/keys"
echo "2. OpenAI API: https://platform.openai.com/api-keys"
echo "3. Pinecone API: https://app.pinecone.io/"

echo ""
echo "After generating new keys, update them in:"
echo "- Hugging Face Spaces: Settings > Repository secrets"
echo "- Vercel: Project Settings > Environment Variables"

echo ""
echo "Then run: python validate_deployment.py"
```

## Troubleshooting Common Issues

### Issue Resolution Checklist

```markdown
## Common Issues and Solutions

### 1. Backend Not Responding
- [ ] Check Hugging Face Spaces status
- [ ] Verify environment variables are set
- [ ] Check Docker build logs
- [ ] Validate API keys
- [ ] Test Pinecone connectivity

### 2. Frontend Build Failures
- [ ] Check Node.js version compatibility
- [ ] Verify package.json dependencies
- [ ] Clear npm cache: `npm cache clean --force`
- [ ] Delete node_modules and reinstall
- [ ] Check Vercel build logs

### 3. API Connection Issues
- [ ] Verify CORS configuration
- [ ] Check API endpoint URLs
- [ ] Test with curl/Postman
- [ ] Validate SSL certificates
- [ ] Check rate limits

### 4. Database Connection Problems
- [ ] Verify Pinecone API key
- [ ] Check index name and environment
- [ ] Test with Pinecone console
- [ ] Verify index dimensions (1536)
- [ ] Check quota limits
```

## Emergency Contacts and Resources

```markdown
## Emergency Response

### Critical Issues (Production Down)
1. Check status pages:
   - Hugging Face: https://status.huggingface.co/
   - Vercel: https://www.vercel-status.com/
   - Pinecone: https://status.pinecone.io/

2. Quick fixes:
   - Restart services via platform dashboards
   - Rollback to last known good version
   - Switch to backup API keys

3. Communication:
   - Update status page/users
   - Document incident
   - Plan post-mortem

### Support Resources
- Hugging Face Spaces: https://huggingface.co/docs/hub/spaces
- Vercel Documentation: https://vercel.com/docs
- Pinecone Support: https://docs.pinecone.io/
```

---

**Last Updated:** [Current Date]
**Version:** 1.0
**Maintainer:** [Your Name/Team]