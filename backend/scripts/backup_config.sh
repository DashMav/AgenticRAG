#!/bin/bash

# RAG AI Agent - Configuration Backup Script
# This script creates backups of all configuration files and deployment settings

set -e  # Exit on any error

# Configuration
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🔄 Starting configuration backup..."
echo "Backup directory: $BACKUP_DIR"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup Python backend configuration
echo "📦 Backing up backend configuration..."
cp "$PROJECT_ROOT/requirements.txt" "$BACKUP_DIR/" 2>/dev/null || echo "⚠️  requirements.txt not found"
cp "$PROJECT_ROOT/Dockerfile" "$BACKUP_DIR/" 2>/dev/null || echo "⚠️  Dockerfile not found"
cp "$PROJECT_ROOT/render.yaml" "$BACKUP_DIR/" 2>/dev/null || echo "⚠️  render.yaml not found"
cp "$PROJECT_ROOT/.env.example" "$BACKUP_DIR/" 2>/dev/null || echo "⚠️  .env.example not found"

# Backup frontend configuration
echo "📦 Backing up frontend configuration..."
cp "$PROJECT_ROOT/agent-frontend/package.json" "$BACKUP_DIR/" 2>/dev/null || echo "⚠️  package.json not found"
cp "$PROJECT_ROOT/agent-frontend/package-lock.json" "$BACKUP_DIR/" 2>/dev/null || echo "⚠️  package-lock.json not found"
cp "$PROJECT_ROOT/agent-frontend/vite.config.js" "$BACKUP_DIR/" 2>/dev/null || echo "⚠️  vite.config.js not found"
cp "$PROJECT_ROOT/agent-frontend/vercel.json" "$BACKUP_DIR/" 2>/dev/null || echo "⚠️  vercel.json not found"

# Backup deployment documentation
echo "📦 Backing up deployment documentation..."
cp "$PROJECT_ROOT/DEPLOYMENT_GUIDE.md" "$BACKUP_DIR/" 2>/dev/null || echo "⚠️  DEPLOYMENT_GUIDE.md not found"
cp "$PROJECT_ROOT/DEPLOYMENT_CHECKLIST.md" "$BACKUP_DIR/" 2>/dev/null || echo "⚠️  DEPLOYMENT_CHECKLIST.md not found"
cp "$PROJECT_ROOT/ENVIRONMENT_VARIABLES.md" "$BACKUP_DIR/" 2>/dev/null || echo "⚠️  ENVIRONMENT_VARIABLES.md not found"

# Create backup manifest
echo "📝 Creating backup manifest..."
cat > "$BACKUP_DIR/manifest.txt" << EOF
RAG AI Agent Configuration Backup
================================

Backup created: $(date)
Git commit: $(git rev-parse HEAD 2>/dev/null || echo "Not a git repository")
Git branch: $(git branch --show-current 2>/dev/null || echo "Not a git repository")
Backup directory: $BACKUP_DIR

Files included:
$(ls -la "$BACKUP_DIR" | grep -v "^total" | grep -v "^d")

System information:
- OS: $(uname -s)
- Python version: $(python --version 2>/dev/null || echo "Python not found")
- Node.js version: $(node --version 2>/dev/null || echo "Node.js not found")
- npm version: $(npm --version 2>/dev/null || echo "npm not found")

Notes:
- This backup contains configuration files only
- Environment variables and secrets are NOT included
- Vector database data requires separate backup (use backup_pinecone.py)
EOF

# Create backup verification checksum
echo "🔐 Creating backup checksums..."
cd "$BACKUP_DIR"
find . -type f -not -name "checksums.txt" -exec sha256sum {} \; > checksums.txt
cd - > /dev/null

# Display backup summary
echo ""
echo "✅ Configuration backup completed successfully!"
echo "📁 Backup location: $BACKUP_DIR"
echo "📊 Files backed up: $(ls -1 "$BACKUP_DIR" | wc -l)"
echo "💾 Backup size: $(du -sh "$BACKUP_DIR" | cut -f1)"

# Cleanup old backups (keep last 10)
echo ""
echo "🧹 Cleaning up old backups..."
BACKUP_BASE_DIR="$(dirname "$BACKUP_DIR")"
if [ -d "$BACKUP_BASE_DIR" ]; then
    OLD_BACKUPS=$(ls -1t "$BACKUP_BASE_DIR" | tail -n +11)
    if [ ! -z "$OLD_BACKUPS" ]; then
        echo "Removing old backups:"
        echo "$OLD_BACKUPS" | while read backup; do
            echo "  - $backup"
            rm -rf "$BACKUP_BASE_DIR/$backup"
        done
    else
        echo "No old backups to clean up"
    fi
fi

echo ""
echo "🎉 Backup process completed!"
echo "To restore from this backup, use: ./scripts/restore_config.sh $BACKUP_DIR"