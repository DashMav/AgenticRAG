#!/bin/bash

# RAG AI Agent - Configuration Restore Script
# This script restores configuration files from a backup

set -e  # Exit on any error

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Function to display usage
show_usage() {
    echo "Usage: $0 <backup_directory>"
    echo ""
    echo "Example:"
    echo "  $0 backups/20241217_143022"
    echo ""
    echo "Available backups:"
    if [ -d "backups" ]; then
        ls -1t backups/ | head -5
    else
        echo "  No backups directory found"
    fi
}

# Check if backup directory is provided
if [ $# -eq 0 ]; then
    echo "❌ Error: No backup directory specified"
    show_usage
    exit 1
fi

BACKUP_DIR="$1"

# Validate backup directory
if [ ! -d "$BACKUP_DIR" ]; then
    echo "❌ Error: Backup directory '$BACKUP_DIR' does not exist"
    show_usage
    exit 1
fi

# Check if manifest exists
if [ ! -f "$BACKUP_DIR/manifest.txt" ]; then
    echo "❌ Error: Invalid backup - manifest.txt not found"
    exit 1
fi

echo "🔄 Starting configuration restore..."
echo "📁 Backup directory: $BACKUP_DIR"
echo ""

# Display backup information
echo "📋 Backup Information:"
echo "====================="
head -10 "$BACKUP_DIR/manifest.txt"
echo ""

# Confirm restore
read -p "Do you want to proceed with the restore? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Restore cancelled"
    exit 1
fi

# Create backup of current configuration before restore
CURRENT_BACKUP_DIR="backups/pre-restore-$(date +%Y%m%d_%H%M%S)"
echo "💾 Creating backup of current configuration..."
mkdir -p "$CURRENT_BACKUP_DIR"

# Backup current files that will be overwritten
FILES_TO_BACKUP=(
    "requirements.txt"
    "Dockerfile"
    "render.yaml"
    ".env.example"
    "agent-frontend/package.json"
    "agent-frontend/package-lock.json"
    "agent-frontend/vite.config.js"
    "agent-frontend/vercel.json"
)

for file in "${FILES_TO_BACKUP[@]}"; do
    if [ -f "$PROJECT_ROOT/$file" ]; then
        mkdir -p "$CURRENT_BACKUP_DIR/$(dirname "$file")"
        cp "$PROJECT_ROOT/$file" "$CURRENT_BACKUP_DIR/$file"
        echo "  ✅ Backed up: $file"
    fi
done

echo ""
echo "🔄 Restoring configuration files..."

# Restore backend configuration
echo "📦 Restoring backend configuration..."
if [ -f "$BACKUP_DIR/requirements.txt" ]; then
    cp "$BACKUP_DIR/requirements.txt" "$PROJECT_ROOT/"
    echo "  ✅ Restored: requirements.txt"
fi

if [ -f "$BACKUP_DIR/Dockerfile" ]; then
    cp "$BACKUP_DIR/Dockerfile" "$PROJECT_ROOT/"
    echo "  ✅ Restored: Dockerfile"
fi

if [ -f "$BACKUP_DIR/render.yaml" ]; then
    cp "$BACKUP_DIR/render.yaml" "$PROJECT_ROOT/"
    echo "  ✅ Restored: render.yaml"
fi

if [ -f "$BACKUP_DIR/.env.example" ]; then
    cp "$BACKUP_DIR/.env.example" "$PROJECT_ROOT/"
    echo "  ✅ Restored: .env.example"
fi

# Restore frontend configuration
echo "📦 Restoring frontend configuration..."
if [ -f "$BACKUP_DIR/package.json" ]; then
    cp "$BACKUP_DIR/package.json" "$PROJECT_ROOT/agent-frontend/"
    echo "  ✅ Restored: agent-frontend/package.json"
fi

if [ -f "$BACKUP_DIR/package-lock.json" ]; then
    cp "$BACKUP_DIR/package-lock.json" "$PROJECT_ROOT/agent-frontend/"
    echo "  ✅ Restored: agent-frontend/package-lock.json"
fi

if [ -f "$BACKUP_DIR/vite.config.js" ]; then
    cp "$BACKUP_DIR/vite.config.js" "$PROJECT_ROOT/agent-frontend/"
    echo "  ✅ Restored: agent-frontend/vite.config.js"
fi

if [ -f "$BACKUP_DIR/vercel.json" ]; then
    cp "$BACKUP_DIR/vercel.json" "$PROJECT_ROOT/agent-frontend/"
    echo "  ✅ Restored: agent-frontend/vercel.json"
fi

# Verify checksums if available
if [ -f "$BACKUP_DIR/checksums.txt" ]; then
    echo ""
    echo "🔍 Verifying restored files..."
    cd "$PROJECT_ROOT"
    
    # Create temporary checksum file for verification
    TEMP_CHECKSUMS=$(mktemp)
    
    # Calculate checksums for restored files
    while IFS= read -r line; do
        checksum=$(echo "$line" | cut -d' ' -f1)
        file=$(echo "$line" | cut -d' ' -f2- | sed 's|^\./||')
        
        if [ -f "$file" ]; then
            actual_checksum=$(sha256sum "$file" | cut -d' ' -f1)
            if [ "$checksum" = "$actual_checksum" ]; then
                echo "  ✅ Verified: $file"
            else
                echo "  ❌ Checksum mismatch: $file"
            fi
        fi
    done < "$BACKUP_DIR/checksums.txt"
    
    rm -f "$TEMP_CHECKSUMS"
fi

echo ""
echo "✅ Configuration restore completed successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Review the restored configuration files"
echo "2. Update environment variables if needed"
echo "3. Test the application locally:"
echo "   - Backend: uvicorn app:app --reload"
echo "   - Frontend: cd agent-frontend && npm install && npm run dev"
echo "4. Deploy the changes if everything works correctly"
echo ""
echo "💾 Your previous configuration was backed up to: $CURRENT_BACKUP_DIR"
echo ""
echo "🔄 To rollback this restore, run:"
echo "   $0 $CURRENT_BACKUP_DIR"