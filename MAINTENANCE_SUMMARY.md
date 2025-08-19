# RAG AI Agent - Maintenance and Update Summary

## Overview

This document provides a quick reference for all maintenance and update procedures for the RAG AI Agent application. It serves as a central hub linking to detailed documentation and scripts.

## Quick Reference

### 🔧 Maintenance Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/backup_config.sh` | Configuration backup (Unix/Linux/macOS) | `./scripts/backup_config.sh` |
| `scripts/backup_config.bat` | Configuration backup (Windows) | `scripts\backup_config.bat` |
| `scripts/backup_pinecone.py` | Pinecone vector database backup | `python scripts/backup_pinecone.py` |
| `scripts/restore_config.sh` | Configuration restore | `./scripts/restore_config.sh <backup_dir>` |
| `scripts/recover_pinecone.py` | Pinecone index recovery | `python scripts/recover_pinecone.py` |
| `scripts/health_monitor.py` | Health monitoring | `python scripts/health_monitor.py` |
| `scripts/rollback.sh` | Application rollback | `./scripts/rollback.sh <option>` |

### 📚 Documentation Files

| Document | Purpose | Key Sections |
|----------|---------|--------------|
| `MAINTENANCE_GUIDE.md` | Comprehensive maintenance procedures | Schedules, Backups, Recovery, Monitoring |
| `UPDATE_PROCEDURES.md` | Step-by-step update procedures | Dependencies, Security, Features |
| `MAINTENANCE_CHECKLIST.md` | Systematic maintenance checklist | Daily, Weekly, Monthly, Quarterly |
| `MAINTENANCE_SUMMARY.md` | This quick reference guide | Scripts, Documentation, Workflows |

## Common Maintenance Tasks

### Daily Tasks (5 minutes)
```bash
# Check system health
python scripts/health_monitor.py --no-alerts

# Review logs for issues
tail -20 health_monitor.log | grep -E "(FAILED|ERROR|❌)"
```

### Weekly Tasks (30 minutes)
```bash
# Create backups
./scripts/backup_config.sh
python scripts/backup_pinecone.py

# Security scan
pip audit
cd agent-frontend && npm audit

# Verify service status
python scripts/health_monitor.py
```

### Monthly Tasks (2 hours)
```bash
# Update dependencies (test first!)
pip list --outdated
cd agent-frontend && npm outdated

# Rotate API keys
# 1. Generate new keys at provider websites
# 2. Update in Hugging Face Spaces and Vercel
# 3. Test with: python scripts/health_monitor.py

# Clean old backups
find backups/ -mtime +90 -type d -exec rm -rf {} \;
```

### Emergency Procedures (10 minutes)
```bash
# Quick health check
python scripts/health_monitor.py --no-alerts

# Emergency rollback if needed
./scripts/rollback.sh quick

# Check service status pages
# - Pinecone: https://status.pinecone.io/
# - Vercel: https://www.vercel-status.com/
# - Hugging Face: https://status.huggingface.co/
```

## Maintenance Workflows

### 🔄 Regular Update Workflow

1. **Pre-Update** (15 minutes)
   - Create backups: `./scripts/backup_config.sh`
   - Health check: `python scripts/health_monitor.py`
   - Document current state

2. **Update Process** (30-60 minutes)
   - Update dependencies (backend then frontend)
   - Test locally before deployment
   - Deploy and monitor

3. **Post-Update** (15 minutes)
   - Verify functionality: `python scripts/health_monitor.py`
   - Test core features
   - Monitor for issues

### 🚨 Emergency Response Workflow

1. **Immediate Assessment** (2 minutes)
   - Run: `python scripts/health_monitor.py --no-alerts`
   - Check deployment dashboards

2. **Quick Fix Attempt** (5 minutes)
   - Restart services if possible
   - Check for obvious configuration issues

3. **Rollback if Needed** (3 minutes)
   - Run: `./scripts/rollback.sh quick`
   - Monitor deployment status

4. **Post-Incident** (30 minutes)
   - Document incident
   - Investigate root cause
   - Update procedures if needed

### 🔐 Security Incident Workflow

1. **Immediate Response** (5 minutes)
   - Assess severity: `pip audit` and `npm audit`
   - Check for active exploitation

2. **Apply Patches** (15 minutes)
   - Update vulnerable packages
   - Deploy emergency fixes
   - Rotate compromised keys if needed

3. **Verification** (10 minutes)
   - Confirm vulnerabilities are patched
   - Test system functionality
   - Monitor for issues

## Environment Variables Reference

### Required for Maintenance Scripts

```bash
# Core Application
GROQ_API_KEY="your_groq_api_key"
OPENAI_API_KEY="your_openai_api_key"
PINECONE_API_KEY="your_pinecone_api_key"
PINECONE_INDEX_NAME="your_index_name"

# Monitoring (Optional)
BACKEND_URL="https://your-backend-url"
FRONTEND_URL="https://your-frontend-url"
HEALTH_CHECK_TIMEOUT="30"

# Email Alerts (Optional)
SMTP_SERVER="smtp.gmail.com"
SMTP_PORT="587"
EMAIL_USER="your_email@gmail.com"
EMAIL_PASS="your_app_password"
ALERT_EMAIL="alerts@yourdomain.com"
```

## Troubleshooting Quick Reference

### Common Issues and Solutions

| Issue | Quick Fix | Detailed Solution |
|-------|-----------|-------------------|
| Backend not responding | Check HF Spaces dashboard | See MAINTENANCE_GUIDE.md → Troubleshooting |
| Frontend build fails | Clear npm cache: `npm cache clean --force` | See UPDATE_PROCEDURES.md → Frontend Issues |
| Pinecone connection fails | Verify API key and index name | Run `python scripts/health_monitor.py` |
| API rate limits exceeded | Check usage dashboards | Implement rate limiting or upgrade plans |
| Deployment fails | Check build logs | Review environment variables |

### Health Check Interpretation

| Status | Meaning | Action |
|--------|---------|--------|
| ✅ All services operational | Everything working | Continue monitoring |
| ⚠️ Slow response times | Performance degradation | Investigate and optimize |
| ❌ Service failures | Critical issues | Follow emergency procedures |
| 🔄 Intermittent issues | Unstable service | Monitor closely, prepare rollback |

## Monitoring and Alerting Setup

### Automated Monitoring
```bash
# Start continuous monitoring (runs in background)
nohup python scripts/health_monitor.py --continuous --interval 300 > health_monitor.log 2>&1 &

# Check monitoring status
ps aux | grep health_monitor.py
```

### Log Analysis
```bash
# Check recent failures
grep -E "(FAILED|ERROR|❌)" health_monitor.log | tail -10

# Performance analysis
grep "response_time" health_monitor.log | tail -20

# Service availability summary
grep -c "✅" health_monitor.log
grep -c "❌" health_monitor.log
```

## Backup and Recovery Strategy

### Backup Types and Frequency

| Backup Type | Frequency | Retention | Script |
|-------------|-----------|-----------|---------|
| Configuration | Weekly | 3 months | `backup_config.sh` |
| Pinecone metadata | Weekly | 6 months | `backup_pinecone.py` |
| Pre-update snapshots | Before updates | 1 month | Automatic in update scripts |
| Emergency snapshots | Before rollbacks | 2 weeks | Automatic in rollback scripts |

### Recovery Scenarios

| Scenario | Recovery Method | Estimated Time |
|----------|----------------|----------------|
| Configuration corruption | `restore_config.sh` | 5 minutes |
| Pinecone index issues | `recover_pinecone.py` | 10 minutes + re-upload time |
| Bad deployment | `rollback.sh quick` | 3 minutes |
| Complete failure | Full recovery procedure | 30 minutes + data re-upload |

## Performance Baselines

### Expected Response Times
- Backend API health check: < 2 seconds
- Frontend page load: < 3 seconds
- Pinecone query: < 1 second
- Document upload (1MB): < 10 seconds
- Chat response: < 5 seconds

### Resource Usage Limits
- Pinecone free tier: 1M vectors, 5MB metadata
- Hugging Face Spaces: 16GB storage, 2 CPU cores
- Vercel free tier: 100GB bandwidth, 6000 build minutes/month

## Contact Information and Resources

### Emergency Contacts
- Primary Maintainer: [Your Name] - [Your Email]
- Backup Maintainer: [Backup Name] - [Backup Email]
- On-call Schedule: [Link to schedule]

### External Resources
- **Hugging Face Spaces**: https://huggingface.co/docs/hub/spaces
- **Vercel Documentation**: https://vercel.com/docs
- **Pinecone Support**: https://docs.pinecone.io/
- **Groq API Docs**: https://console.groq.com/docs
- **OpenAI API Docs**: https://platform.openai.com/docs

### Status Pages
- **Pinecone**: https://status.pinecone.io/
- **Vercel**: https://www.vercel-status.com/
- **Hugging Face**: https://status.huggingface.co/
- **OpenAI**: https://status.openai.com/

---

**Last Updated:** December 17, 2024
**Version:** 1.0
**Maintainer:** RAG AI Agent Team

**Quick Help:**
- For detailed procedures: See `MAINTENANCE_GUIDE.md`
- For update procedures: See `UPDATE_PROCEDURES.md`
- For systematic checklists: See `MAINTENANCE_CHECKLIST.md`
- For emergency help: Run `python scripts/health_monitor.py --help`