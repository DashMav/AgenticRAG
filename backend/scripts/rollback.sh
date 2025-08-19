#!/bin/bash

# RAG AI Agent - Rollback Script
# This script provides various rollback options for the application

set -e  # Exit on any error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display usage
show_usage() {
    echo "RAG AI Agent Rollback Script"
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  quick           - Quick rollback to last stable commit"
    echo "  selective       - Interactive selective rollback"
    echo "  backend         - Rollback backend only"
    echo "  frontend        - Rollback frontend only"
    echo "  config          - Rollback from configuration backup"
    echo "  list-commits    - List recent commits for manual rollback"
    echo "  help            - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 quick"
    echo "  $0 selective"
    echo "  $0 backend"
}

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to get last stable commit
get_last_stable_commit() {
    # Look for commits that don't contain rollback, debug, or WIP keywords
    git log --oneline -n 20 | grep -v -i "rollback\|debug\|wip\|test\|temp" | head -n 1 | cut -d' ' -f1
}

# Function to create rollback branch
create_rollback_branch() {
    local branch_name="rollback-$(date +%Y%m%d-%H%M%S)"
    git checkout -b "$branch_name"
    print_status $GREEN "Created rollback branch: $branch_name"
    echo "$branch_name"
}

# Function to backup current state before rollback
backup_current_state() {
    print_status $BLUE "Creating backup of current state..."
    
    # Create configuration backup
    if [ -f "scripts/backup_config.sh" ]; then
        ./scripts/backup_config.sh
    else
        print_status $YELLOW "Warning: backup_config.sh not found, creating manual backup"
        
        BACKUP_DIR="backups/pre-rollback-$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        
        # Backup key files
        cp requirements.txt "$BACKUP_DIR/" 2>/dev/null || true
        cp Dockerfile "$BACKUP_DIR/" 2>/dev/null || true
        cp agent-frontend/package.json "$BACKUP_DIR/" 2>/dev/null || true
        cp agent-frontend/package-lock.json "$BACKUP_DIR/" 2>/dev/null || true
        
        print_status $GREEN "Manual backup created: $BACKUP_DIR"
    fi
}

# Function for quick rollback
quick_rollback() {
    print_status $BLUE "🔄 Starting quick rollback..."
    
    # Get last stable commit
    LAST_COMMIT=$(get_last_stable_commit)
    
    if [ -z "$LAST_COMMIT" ]; then
        print_status $RED "❌ Could not find a suitable commit to rollback to"
        exit 1
    fi
    
    print_status $BLUE "Last stable commit found: $LAST_COMMIT"
    
    # Show commit details
    echo ""
    print_status $BLUE "Commit details:"
    git show --stat "$LAST_COMMIT"
    echo ""
    
    # Confirm rollback
    read -p "Do you want to rollback to this commit? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status $RED "❌ Rollback cancelled"
        exit 1
    fi
    
    # Backup current state
    backup_current_state
    
    # Create rollback branch
    ROLLBACK_BRANCH=$(create_rollback_branch)
    
    # Reset to last stable commit
    print_status $BLUE "Resetting to commit: $LAST_COMMIT"
    git reset --hard "$LAST_COMMIT"
    
    # Force push to trigger redeployment
    print_status $BLUE "Pushing rollback to trigger redeployment..."
    git push origin main --force
    
    print_status $GREEN "✅ Quick rollback completed!"
    print_status $BLUE "Monitor deployments:"
    print_status $BLUE "   Backend: Check Hugging Face Spaces dashboard"
    print_status $BLUE "   Frontend: Check Vercel dashboard"
}

# Function for selective rollback
selective_rollback() {
    print_status $BLUE "🔄 Starting selective rollback..."
    
    echo "Select rollback option:"
    echo "1. Rollback specific files"
    echo "2. Rollback to specific commit"
    echo "3. Rollback specific component (backend/frontend)"
    echo "4. Cancel"
    
    read -p "Enter your choice (1-4): " choice
    
    case $choice in
        1)
            selective_file_rollback
            ;;
        2)
            selective_commit_rollback
            ;;
        3)
            selective_component_rollback
            ;;
        4)
            print_status $RED "❌ Rollback cancelled"
            exit 0
            ;;
        *)
            print_status $RED "❌ Invalid choice"
            exit 1
            ;;
    esac
}

# Function for selective file rollback
selective_file_rollback() {
    print_status $BLUE "Available files for rollback:"
    
    # Show modified files in recent commits
    git diff --name-only HEAD~5 HEAD
    
    echo ""
    read -p "Enter file paths to rollback (space-separated): " files
    
    if [ -z "$files" ]; then
        print_status $RED "❌ No files specified"
        exit 1
    fi
    
    # Backup current state
    backup_current_state
    
    # Create rollback branch
    ROLLBACK_BRANCH=$(create_rollback_branch)
    
    # Rollback specific files
    for file in $files; do
        if git checkout HEAD~1 -- "$file" 2>/dev/null; then
            print_status $GREEN "✅ Rolled back: $file"
        else
            print_status $RED "❌ Failed to rollback: $file"
        fi
    done
    
    # Commit changes
    git add .
    git commit -m "ROLLBACK: Selective file rollback - $(date)"
    git push origin main
    
    print_status $GREEN "✅ Selective file rollback completed!"
}

# Function for selective commit rollback
selective_commit_rollback() {
    print_status $BLUE "Recent commits:"
    git log --oneline -n 10
    
    echo ""
    read -p "Enter commit hash to rollback to: " commit_hash
    
    if [ -z "$commit_hash" ]; then
        print_status $RED "❌ No commit hash specified"
        exit 1
    fi
    
    # Validate commit hash
    if ! git cat-file -e "$commit_hash" 2>/dev/null; then
        print_status $RED "❌ Invalid commit hash"
        exit 1
    fi
    
    # Show commit details
    echo ""
    print_status $BLUE "Commit details:"
    git show --stat "$commit_hash"
    echo ""
    
    # Confirm rollback
    read -p "Do you want to rollback to this commit? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status $RED "❌ Rollback cancelled"
        exit 1
    fi
    
    # Backup current state
    backup_current_state
    
    # Create rollback branch
    ROLLBACK_BRANCH=$(create_rollback_branch)
    
    # Reset to specified commit
    git reset --hard "$commit_hash"
    git push origin main --force
    
    print_status $GREEN "✅ Rollback to commit $commit_hash completed!"
}

# Function for selective component rollback
selective_component_rollback() {
    echo "Select component to rollback:"
    echo "1. Backend only"
    echo "2. Frontend only"
    echo "3. Both"
    echo "4. Cancel"
    
    read -p "Enter your choice (1-4): " choice
    
    case $choice in
        1)
            backend_rollback
            ;;
        2)
            frontend_rollback
            ;;
        3)
            backend_rollback
            frontend_rollback
            ;;
        4)
            print_status $RED "❌ Rollback cancelled"
            exit 0
            ;;
        *)
            print_status $RED "❌ Invalid choice"
            exit 1
            ;;
    esac
}

# Function for backend rollback
backend_rollback() {
    print_status $BLUE "🔄 Rolling back backend..."
    
    # Backup current state
    backup_current_state
    
    # Create rollback branch if not already created
    if ! git branch | grep -q "rollback-"; then
        ROLLBACK_BRANCH=$(create_rollback_branch)
    fi
    
    # Rollback backend files
    BACKEND_FILES=(
        "requirements.txt"
        "Dockerfile"
        "app.py"
        "agent.py"
        "database.py"
        "vector_database.py"
        "render.yaml"
    )
    
    for file in "${BACKEND_FILES[@]}"; do
        if [ -f "$file" ] && git checkout HEAD~1 -- "$file" 2>/dev/null; then
            print_status $GREEN "✅ Rolled back: $file"
        fi
    done
    
    # Commit backend rollback
    git add .
    git commit -m "ROLLBACK: Backend rollback - $(date)"
    git push origin main
    
    print_status $GREEN "✅ Backend rollback completed!"
    print_status $BLUE "Monitor backend deployment at Hugging Face Spaces"
}

# Function for frontend rollback
frontend_rollback() {
    print_status $BLUE "🔄 Rolling back frontend..."
    
    # Backup current state
    backup_current_state
    
    # Create rollback branch if not already created
    if ! git branch | grep -q "rollback-"; then
        ROLLBACK_BRANCH=$(create_rollback_branch)
    fi
    
    # Rollback frontend directory
    if git checkout HEAD~1 -- agent-frontend/ 2>/dev/null; then
        print_status $GREEN "✅ Rolled back: agent-frontend/"
    else
        print_status $RED "❌ Failed to rollback frontend"
        return 1
    fi
    
    # Commit frontend rollback
    git add .
    git commit -m "ROLLBACK: Frontend rollback - $(date)"
    git push origin main
    
    print_status $GREEN "✅ Frontend rollback completed!"
    print_status $BLUE "Monitor frontend deployment at Vercel"
}

# Function for configuration rollback
config_rollback() {
    print_status $BLUE "🔄 Configuration rollback..."
    
    # List available backups
    if [ ! -d "backups" ]; then
        print_status $RED "❌ No backups directory found"
        exit 1
    fi
    
    BACKUPS=($(ls -1t backups/ | head -10))
    
    if [ ${#BACKUPS[@]} -eq 0 ]; then
        print_status $RED "❌ No backups found"
        exit 1
    fi
    
    print_status $BLUE "Available configuration backups:"
    for i in "${!BACKUPS[@]}"; do
        echo "$((i+1)). ${BACKUPS[$i]}"
    done
    
    echo ""
    read -p "Select backup to restore (1-${#BACKUPS[@]}): " backup_choice
    
    if [[ ! "$backup_choice" =~ ^[0-9]+$ ]] || [ "$backup_choice" -lt 1 ] || [ "$backup_choice" -gt ${#BACKUPS[@]} ]; then
        print_status $RED "❌ Invalid selection"
        exit 1
    fi
    
    SELECTED_BACKUP="backups/${BACKUPS[$((backup_choice-1))]}"
    
    # Use restore script if available
    if [ -f "scripts/restore_config.sh" ]; then
        ./scripts/restore_config.sh "$SELECTED_BACKUP"
    else
        print_status $RED "❌ restore_config.sh not found"
        exit 1
    fi
}

# Function to list commits for manual rollback
list_commits() {
    print_status $BLUE "Recent commits (last 20):"
    echo ""
    git log --oneline --graph -n 20
    echo ""
    print_status $BLUE "To manually rollback to a specific commit:"
    print_status $BLUE "  git reset --hard <commit-hash>"
    print_status $BLUE "  git push origin main --force"
    echo ""
    print_status $YELLOW "⚠️  Always create a backup before manual rollback!"
}

# Main script logic
case "${1:-help}" in
    "quick")
        quick_rollback
        ;;
    "selective")
        selective_rollback
        ;;
    "backend")
        backend_rollback
        ;;
    "frontend")
        frontend_rollback
        ;;
    "config")
        config_rollback
        ;;
    "list-commits")
        list_commits
        ;;
    "help"|*)
        show_usage
        ;;
esac