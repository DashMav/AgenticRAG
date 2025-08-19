# RAG AI Agent - Update Procedures

## Overview

This document provides step-by-step procedures for updating the RAG AI Agent application, including dependency updates, security patches, and feature updates. Follow these procedures to ensure safe and reliable updates in production.

## Table of Contents

1. [Pre-Update Checklist](#pre-update-checklist)
2. [Dependency Updates](#dependency-updates)
3. [Security Patch Updates](#security-patch-updates)
4. [Feature Updates](#feature-updates)
5. [Post-Update Verification](#post-update-verification)
6. [Rollback Procedures](#rollback-procedures)

## Pre-Update Checklist

Before performing any updates, complete this checklist:

### 1. Backup Current State

```bash
# Create configuration backup
./scripts/backup_config.sh  # Unix/Linux/macOS
# OR
scripts\backup_config.bat   # Windows

# Create Pinecone backup
python scripts/backup_pinecone.py

# Verify backups
ls -la backups/  # Unix/Linux/macOS
# OR
dir backups\     # Windows
```

### 2. Document Current State

```bash
# Record current versions
echo "=== Current State ===" > update_log.txt
echo "Date: $(date)" >> update_log.txt
echo "Git commit: $(git rev-parse HEAD)" >> update_log.txt
echo "Git branch: $(git branch --show-current)" >> update_log.txt
echo "" >> update_log.txt

# Backend dependencies
echo "Backend Dependencies:" >> update_log.txt
pip freeze >> update_log.txt
echo "" >> update_log.txt

# Frontend dependencies
echo "Frontend Dependencies:" >> update_log.txt
cd agent-frontend && npm list --depth=0 >> ../update_log.txt
cd ..
```

### 3. Health Check

```bash
# Run comprehensive health monitoring
python scripts/health_monitor.py --no-alerts

# Verify all services are healthy before proceeding
# Check specific services if needed:
# - Backend API health
# - Frontend availability  
# - Pinecone connectivity
# - Groq API access
# - OpenAI API access
```

### 4. Notify Stakeholders

- [ ] Inform users of planned maintenance window
- [ ] Set up monitoring alerts
- [ ] Prepare rollback plan

## Dependency Updates

### Backend Dependencies (Python)

#### 1. Check for Updates

```bash
# Navigate to project root
cd RAG-AI-Agent

# Check for outdated packages
pip list --outdated

# Check for security vulnerabilities
pip audit
```

#### 2. Update Strategy

**Option A: Conservative Update (Recommended)**

```bash
# Update patch versions only
pip install --upgrade openai~=1.76.0
pip install --upgrade fastapi~=0.115.0
pip install --upgrade uvicorn~=0.34.0

# Update specific packages with known fixes
pip install --upgrade langchain
pip install --upgrade pinecone-client
```

**Option B: Full Update (Use with caution)**

```bash
# Create virtual environment for testing
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install current requirements
pip install -r requirements.txt

# Update all packages
pip install --upgrade -r requirements.txt

# Generate new requirements
pip freeze > requirements_new.txt
```

#### 3. Test Updates Locally

```bash
# Install updated dependencies
pip install -r requirements_new.txt

# Run application locally
uvicorn app:app --host 0.0.0.0 --port 8000

# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/chats

# Run validation script
python validate_deployment.py
```

#### 4. Deploy Backend Updates

```bash
# If tests pass, update requirements.txt
cp requirements_new.txt requirements.txt

# Commit changes
git add requirements.txt
git commit -m "Update backend dependencies - $(date +%Y-%m-%d)"

# Push to trigger Hugging Face Spaces rebuild
git push origin main

# Monitor deployment
echo "Monitor at: https://huggingface.co/spaces/[username]/[space-name]"
```

### Frontend Dependencies (Node.js)

#### 1. Check for Updates

```bash
cd agent-frontend

# Check for outdated packages
npm outdated

# Check for security vulnerabilities
npm audit
```

#### 2. Update Strategy

**Option A: Conservative Update**

```bash
# Update patch and minor versions
npm update

# Update specific packages
npm install react@latest react-dom@latest
npm install axios@latest
```

**Option B: Major Version Updates**

```bash
# Check what would be updated
npx npm-check-updates

# Update major versions (be cautious)
npx npm-check-updates -u
npm install
```

#### 3. Test Frontend Updates

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Test in browser at http://localhost:5173

# Build for production
npm run build

# Test production build
npm run preview
```

#### 4. Deploy Frontend Updates

```bash
# Commit changes
git add package.json package-lock.json
git commit -m "Update frontend dependencies - $(date +%Y-%m-%d)"

# Push to trigger Vercel rebuild
git push origin main

# Monitor deployment
echo "Monitor at: https://vercel.com/dashboard"
```

## Security Patch Updates

### Critical Security Updates (Emergency)

#### Immediate Response Process

1. **Assess Severity**
   ```bash
   # Check vulnerability details
   pip audit --desc
   npm audit --audit-level high
   ```

2. **Apply Emergency Patch**
   ```bash
   # Update vulnerable package immediately
   pip install --upgrade [vulnerable-package]
   # or
   npm install [vulnerable-package]@latest
   ```

3. **Emergency Deployment**
   ```bash
   # Skip normal testing for critical security issues
   git add .
   git commit -m "SECURITY: Emergency patch for [CVE-ID] - $(date)"
   git push origin main
   ```

4. **Verify Fix**
   ```bash
   # Confirm vulnerability is resolved
   pip audit
   npm audit
   
   # Test basic functionality
   python scripts/health_monitor.py
   ```

5. **Post-Emergency Actions**
   - Document the incident
   - Schedule comprehensive testing
   - Review security practices

### Regular Security Updates

#### Monthly Security Review

```bash
# Create security update branch
git checkout -b security-updates-$(date +%Y-%m)

# Run comprehensive security audit
pip audit --desc > security_audit_backend.txt
cd agent-frontend && npm audit > ../security_audit_frontend.txt && cd ..

# Review audit results and plan updates
cat security_audit_*.txt
```

#### API Key Rotation

```bash
# Use the rotation script
./scripts/rotate_api_keys.sh

# Or manual process:
# 1. Generate new keys at provider websites
# 2. Update environment variables in deployment platforms
# 3. Test with new keys
python validate_deployment.py
```

## Feature Updates

### Planning Feature Updates

#### 1. Review Changes

```bash
# Review commits since last update
git log --oneline --since="1 month ago"

# Review pull requests or feature branches
git branch -a
```

#### 2. Test Feature Updates

```bash
# Create feature testing branch
git checkout -b feature-update-$(date +%Y-%m-%d)

# Merge or cherry-pick features
git merge feature-branch-name

# Test locally
python scripts/health_monitor.py
```

#### 3. Staged Deployment

```bash
# Deploy backend first
git push origin main

# Wait for backend deployment to complete
sleep 300

# Test backend
curl https://[your-backend-url]/health

# Deploy frontend
cd agent-frontend
git push origin main
```

### Database Schema Updates

#### Pinecone Index Updates

```bash
# If index configuration changes are needed
python scripts/backup_pinecone.py

# Create new index with updated configuration
python -c "
import pinecone
import os
pinecone.init(api_key=os.getenv('PINECONE_API_KEY'))
pinecone.create_index(
    name='new-index-name',
    dimension=1536,
    metric='cosine'
)
"

# Migrate data (if needed)
# This would require custom migration script based on changes
```

## Post-Update Verification

### Comprehensive Testing

```bash
# Run health checks
python scripts/health_monitor.py

# Test all major functionality
python validate_deployment.py

# Performance testing
python scripts/performance_monitor.py
```

### User Acceptance Testing

1. **Document Upload Test**
   - Upload a test document
   - Verify processing completes
   - Check vector storage

2. **Chat Functionality Test**
   - Test simple chat mode
   - Test agent mode with web search
   - Verify responses are appropriate

3. **Chat Management Test**
   - Create new chat
   - Rename chat
   - Delete chat
   - Verify persistence

### Monitoring Setup

```bash
# Set up continuous monitoring
python scripts/health_monitor.py --continuous &

# Monitor logs
tail -f logs/health_monitor.log
```

## Rollback Procedures

### Quick Rollback

```bash
# Use the rollback script
./scripts/rollback.sh quick

# Or manual rollback
git log --oneline -n 5
git reset --hard [previous-commit-hash]
git push origin main --force
```

### Selective Rollback

```bash
# Rollback specific components
./scripts/rollback.sh

# Choose component rollback option
# Follow interactive prompts
```

### Database Rollback

```bash
# Restore Pinecone index from backup
python scripts/recover_pinecone.py

# Follow interactive prompts to select backup
```

## Update Schedule

### Regular Update Schedule

#### Weekly
- [ ] Security vulnerability scan
- [ ] Dependency security updates (if any)
- [ ] Health monitoring review

#### Monthly
- [ ] Dependency updates (patch versions)
- [ ] Performance review
- [ ] Backup verification
- [ ] Documentation updates

#### Quarterly
- [ ] Major dependency updates
- [ ] Feature updates
- [ ] Security audit
- [ ] Disaster recovery testing

### Emergency Updates

- **Critical Security**: Within 24 hours
- **High Security**: Within 1 week
- **Bug Fixes**: Within 2 weeks
- **Feature Updates**: Monthly cycle

## Update Checklist Template

```markdown
## Update Checklist - [Date]

### Pre-Update
- [ ] Created configuration backup
- [ ] Created Pinecone backup
- [ ] Documented current state
- [ ] Ran health checks
- [ ] Notified stakeholders

### Update Process
- [ ] Updated backend dependencies
- [ ] Tested backend locally
- [ ] Deployed backend updates
- [ ] Updated frontend dependencies
- [ ] Tested frontend locally
- [ ] Deployed frontend updates

### Post-Update
- [ ] Ran comprehensive health checks
- [ ] Performed user acceptance testing
- [ ] Verified all functionality
- [ ] Set up monitoring
- [ ] Documented changes

### Rollback Plan
- [ ] Rollback procedure identified
- [ ] Rollback tested (if needed)
- [ ] Stakeholders notified of completion
```

## Troubleshooting Update Issues

### Common Update Problems

#### Backend Update Issues

```bash
# Dependency conflicts
pip install --force-reinstall [package-name]

# Build failures
docker build --no-cache .

# Runtime errors
tail -f logs/app.log
```

#### Frontend Update Issues

```bash
# Node modules issues
rm -rf node_modules package-lock.json
npm install

# Build failures
npm run build --verbose

# Runtime errors
npm run dev
```

#### Deployment Issues

```bash
# Hugging Face Spaces issues
# Check build logs in HF Spaces interface
# Verify environment variables

# Vercel issues
# Check deployment logs in Vercel dashboard
# Verify build settings
```

### Recovery Procedures

If updates fail:

1. **Immediate Actions**
   ```bash
   # Quick rollback
   ./scripts/rollback.sh quick
   ```

2. **Investigate Issues**
   ```bash
   # Check logs
   python scripts/health_monitor.py
   
   # Review error messages
   git log --oneline -n 10
   ```

3. **Fix and Retry**
   ```bash
   # Fix issues
   # Test locally
   # Redeploy
   ```

---

**Last Updated:** [Current Date]
**Version:** 1.0
**Maintainer:** [Your Name/Team]