#!/usr/bin/env python3
"""
Pre-Flight Checklist Script for RAG AI-Agent

This script provides an interactive pre-flight checklist for developers
to ensure all prerequisites are met before deployment.

Usage:
    python scripts/pre_flight_checklist.py
    python scripts/pre_flight_checklist.py --auto-check
    python scripts/pre_flight_checklist.py --save-progress

Requirements:
    - Interactive terminal for checklist
    - All validation scripts available
"""

import os
import sys
import json
import argparse
import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

@dataclass
class ChecklistItem:
    """Represents a single checklist item."""
    id: str
    category: str
    description: str
    completed: bool = False
    auto_checkable: bool = False
    help_text: Optional[str] = None
    validation_command: Optional[str] = None

@dataclass
class ChecklistProgress:
    """Tracks checklist progress."""
    timestamp: str
    total_items: int
    completed_items: int
    completion_percentage: float
    items: Dict[str, bool]
    notes: Dict[str, str]

def print_header(text: str, level: int = 1):
    """Print a formatted header."""
    if level == 1:
        print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.END}")
        print(f"{Colors.BLUE}{Colors.BOLD}{text.center(70)}{Colors.END}")
        print(f"{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.END}\n")
    elif level == 2:
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'-'*50}{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD}{text}{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'-'*50}{Colors.END}\n")
    else:
        print(f"\n{Colors.MAGENTA}{Colors.UNDERLINE}{text}{Colors.END}\n")

def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️ {text}{Colors.END}")

def print_info(text: str):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ️ {text}{Colors.END}")

def print_step(text: str):
    """Print step message."""
    print(f"{Colors.CYAN}→ {text}{Colors.END}")

class PreFlightChecklist:
    """Interactive pre-flight checklist for deployment preparation."""
    
    def __init__(self, auto_check: bool = False, save_progress: bool = False):
        self.auto_check = auto_check
        self.save_progress = save_progress
        self.progress_file = Path("pre_flight_progress.json")
        self.checklist_items = self.create_checklist_items()
        self.progress = self.load_progress()
    
    def create_checklist_items(self) -> List[ChecklistItem]:
        """Create the comprehensive checklist items."""
        items = [
            # Account Setup
            ChecklistItem(
                id="github_account",
                category="Account Setup",
                description="GitHub account created and repository forked/cloned",
                help_text="You need a GitHub account to fork the repository and manage your code."
            ),
            ChecklistItem(
                id="pinecone_account",
                category="Account Setup",
                description="Pinecone account created and verified",
                help_text="Sign up at https://www.pinecone.io/ for vector database service."
            ),
            ChecklistItem(
                id="huggingface_account",
                category="Account Setup",
                description="Hugging Face account created and verified",
                help_text="Sign up at https://huggingface.co/ for backend deployment."
            ),
            ChecklistItem(
                id="vercel_account",
                category="Account Setup",
                description="Vercel account created and verified",
                help_text="Sign up at https://vercel.com/ for frontend deployment."
            ),
            ChecklistItem(
                id="groq_account",
                category="Account Setup",
                description="Groq account created and API access enabled",
                help_text="Sign up at https://console.groq.com/ for LLM inference."
            ),
            ChecklistItem(
                id="openai_account",
                category="Account Setup",
                description="OpenAI account created and API access enabled",
                help_text="Sign up at https://platform.openai.com/ for embeddings."
            ),
            
            # API Keys
            ChecklistItem(
                id="groq_api_key",
                category="API Keys",
                description="Groq API key obtained and saved securely",
                auto_checkable=True,
                help_text="Get your API key from https://console.groq.com/keys",
                validation_command="Check GROQ_API_KEY environment variable"
            ),
            ChecklistItem(
                id="openai_api_key",
                category="API Keys",
                description="OpenAI API key obtained and saved securely",
                auto_checkable=True,
                help_text="Get your API key from https://platform.openai.com/api-keys",
                validation_command="Check OPENAI_API_KEY environment variable"
            ),
            ChecklistItem(
                id="pinecone_api_key",
                category="API Keys",
                description="Pinecone API key obtained and saved securely",
                auto_checkable=True,
                help_text="Get your API key from Pinecone console",
                validation_command="Check PINECONE_API_KEY environment variable"
            ),
            
            # Local Environment
            ChecklistItem(
                id="git_installed",
                category="Local Environment",
                description="Git installed and configured",
                auto_checkable=True,
                help_text="Install Git from https://git-scm.com/",
                validation_command="git --version"
            ),
            ChecklistItem(
                id="python_installed",
                category="Local Environment",
                description="Python 3.8+ installed",
                auto_checkable=True,
                help_text="Install Python from https://python.org/",
                validation_command="python --version"
            ),
            ChecklistItem(
                id="nodejs_installed",
                category="Local Environment",
                description="Node.js 16+ installed",
                auto_checkable=True,
                help_text="Install Node.js from https://nodejs.org/",
                validation_command="node --version"
            ),
            ChecklistItem(
                id="repository_cloned",
                category="Local Environment",
                description="Project repository cloned locally",
                auto_checkable=True,
                help_text="Clone the repository: git clone <repository-url>",
                validation_command="Check for app.py and agent-frontend/ directory"
            ),
            ChecklistItem(
                id="python_deps_installed",
                category="Local Environment",
                description="Python dependencies installed",
                auto_checkable=True,
                help_text="Run: pip install -r requirements.txt",
                validation_command="Check installed packages"
            ),
            ChecklistItem(
                id="frontend_deps_installed",
                category="Local Environment",
                description="Frontend dependencies installed",
                auto_checkable=True,
                help_text="Run: cd agent-frontend && npm install",
                validation_command="Check for node_modules directory"
            ),
            
            # Pinecone Setup
            ChecklistItem(
                id="pinecone_index_created",
                category="Pinecone Setup",
                description="Pinecone index created with correct dimensions (1536)",
                auto_checkable=True,
                help_text="Create index in Pinecone console with 1536 dimensions",
                validation_command="Validate Pinecone index configuration"
            ),
            ChecklistItem(
                id="pinecone_index_name_set",
                category="Pinecone Setup",
                description="Pinecone index name configured in environment",
                auto_checkable=True,
                help_text="Set PINECONE_INDEX_NAME environment variable",
                validation_command="Check PINECONE_INDEX_NAME environment variable"
            ),
            
            # Configuration Files
            ChecklistItem(
                id="dockerfile_present",
                category="Configuration Files",
                description="Dockerfile present and valid",
                auto_checkable=True,
                help_text="Dockerfile should be in the root directory",
                validation_command="Check for Dockerfile"
            ),
            ChecklistItem(
                id="requirements_txt_present",
                category="Configuration Files",
                description="requirements.txt present and valid",
                auto_checkable=True,
                help_text="requirements.txt should list all Python dependencies",
                validation_command="Check for requirements.txt"
            ),
            ChecklistItem(
                id="package_json_present",
                category="Configuration Files",
                description="Frontend package.json present and valid",
                auto_checkable=True,
                help_text="package.json should be in agent-frontend/ directory",
                validation_command="Check for agent-frontend/package.json"
            ),
            ChecklistItem(
                id="vercel_json_present",
                category="Configuration Files",
                description="vercel.json present and configured",
                auto_checkable=True,
                help_text="vercel.json should be in agent-frontend/ directory with proxy config",
                validation_command="Check for agent-frontend/vercel.json"
            ),
            
            # Security
            ChecklistItem(
                id="env_file_gitignored",
                category="Security",
                description=".env files properly ignored in .gitignore",
                auto_checkable=True,
                help_text="Ensure .env is listed in .gitignore to prevent committing secrets",
                validation_command="Check .gitignore for .env"
            ),
            ChecklistItem(
                id="no_hardcoded_keys",
                category="Security",
                description="No API keys hardcoded in source files",
                help_text="All API keys should be in environment variables, not in code"
            ),
            
            # Pre-deployment Testing
            ChecklistItem(
                id="api_keys_validated",
                category="Pre-deployment Testing",
                description="All API keys validated and working",
                auto_checkable=True,
                help_text="Run: python scripts/validate_api_keys.py",
                validation_command="python scripts/validate_api_keys.py"
            ),
            ChecklistItem(
                id="environment_validated",
                category="Pre-deployment Testing",
                description="Local environment validated",
                auto_checkable=True,
                help_text="Run: python scripts/validate_environment.py",
                validation_command="python scripts/validate_environment.py"
            ),
            ChecklistItem(
                id="local_app_tested",
                category="Pre-deployment Testing",
                description="Application tested locally",
                help_text="Run the app locally to ensure it works: python app.py"
            )
        ]
        
        return items
    
    def load_progress(self) -> ChecklistProgress:
        """Load existing progress if available."""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    data = json.load(f)
                
                # Update checklist items with saved progress
                saved_items = data.get('items', {})
                for item in self.checklist_items:
                    if item.id in saved_items:
                        item.completed = saved_items[item.id]
                
                return ChecklistProgress(
                    timestamp=data.get('timestamp', ''),
                    total_items=data.get('total_items', len(self.checklist_items)),
                    completed_items=data.get('completed_items', 0),
                    completion_percentage=data.get('completion_percentage', 0.0),
                    items=saved_items,
                    notes=data.get('notes', {})
                )
            except Exception as e:
                print_warning(f"Could not load progress file: {e}")
        
        return ChecklistProgress(
            timestamp=datetime.datetime.now().isoformat(),
            total_items=len(self.checklist_items),
            completed_items=0,
            completion_percentage=0.0,
            items={},
            notes={}
        )
    
    def save_progress_to_file(self):
        """Save current progress to file."""
        if not self.save_progress:
            return
        
        completed_count = len([item for item in self.checklist_items if item.completed])
        completion_percentage = (completed_count / len(self.checklist_items)) * 100
        
        progress = ChecklistProgress(
            timestamp=datetime.datetime.now().isoformat(),
            total_items=len(self.checklist_items),
            completed_items=completed_count,
            completion_percentage=completion_percentage,
            items={item.id: item.completed for item in self.checklist_items},
            notes={}
        )
        
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(asdict(progress), f, indent=2)
            print_info(f"Progress saved to {self.progress_file}")
        except Exception as e:
            print_warning(f"Could not save progress: {e}")
    
    def auto_check_item(self, item: ChecklistItem) -> bool:
        """Automatically check if an item is completed."""
        if not item.auto_checkable:
            return False
        
        try:
            if item.id == "groq_api_key":
                return bool(os.getenv('GROQ_API_KEY'))
            elif item.id == "openai_api_key":
                return bool(os.getenv('OPENAI_API_KEY'))
            elif item.id == "pinecone_api_key":
                return bool(os.getenv('PINECONE_API_KEY'))
            elif item.id == "pinecone_index_name_set":
                return bool(os.getenv('PINECONE_INDEX_NAME'))
            elif item.id == "git_installed":
                import subprocess
                result = subprocess.run(['git', '--version'], capture_output=True)
                return result.returncode == 0
            elif item.id == "python_installed":
                return sys.version_info >= (3, 8)
            elif item.id == "nodejs_installed":
                import subprocess
                result = subprocess.run(['node', '--version'], capture_output=True, text=True)
                if result.returncode == 0:
                    version = result.stdout.strip().replace('v', '')
                    major_version = int(version.split('.')[0])
                    return major_version >= 16
                return False
            elif item.id == "repository_cloned":
                return Path("app.py").exists() and Path("agent-frontend").exists()
            elif item.id == "python_deps_installed":
                # Check if key packages are installed
                try:
                    import fastapi, openai, groq
                    return True
                except ImportError:
                    return False
            elif item.id == "frontend_deps_installed":
                return Path("agent-frontend/node_modules").exists()
            elif item.id == "dockerfile_present":
                return Path("Dockerfile").exists()
            elif item.id == "requirements_txt_present":
                return Path("requirements.txt").exists()
            elif item.id == "package_json_present":
                return Path("agent-frontend/package.json").exists()
            elif item.id == "vercel_json_present":
                return Path("agent-frontend/vercel.json").exists()
            elif item.id == "env_file_gitignored":
                gitignore_path = Path(".gitignore")
                if gitignore_path.exists():
                    with open(gitignore_path, 'r') as f:
                        return '.env' in f.read()
                return False
            elif item.id in ["pinecone_index_created", "api_keys_validated", "environment_validated"]:
                # These require running validation scripts
                return False  # Skip for now, would need subprocess calls
            
        except Exception:
            return False
        
        return False
    
    def run_interactive_checklist(self):
        """Run the interactive checklist."""
        print_header("RAG AI-Agent Pre-Flight Checklist", 1)
        print_info("This checklist ensures you have everything needed for deployment.")
        print_info("Press Enter to mark items as complete, 's' to skip, 'h' for help, 'q' to quit.\n")
        
        # Group items by category
        categories = {}
        for item in self.checklist_items:
            if item.category not in categories:
                categories[item.category] = []
            categories[item.category].append(item)
        
        # Process each category
        for category_name, items in categories.items():
            print_header(category_name, 2)
            
            for item in items:
                # Auto-check if enabled
                if self.auto_check and item.auto_checkable:
                    auto_result = self.auto_check_item(item)
                    if auto_result:
                        item.completed = True
                        print_success(f"✓ {item.description} (auto-checked)")
                        continue
                
                # Show current status
                status = "✓" if item.completed else "○"
                print(f"\n{status} {item.description}")
                
                if item.completed:
                    print_success("Already completed")
                    continue
                
                # Get user input
                while True:
                    try:
                        response = input(f"{Colors.CYAN}Mark as complete? (Enter/s/h/q): {Colors.END}").strip().lower()
                        
                        if response == '' or response == 'y':
                            item.completed = True
                            print_success("Marked as complete")
                            break
                        elif response == 's':
                            print_warning("Skipped")
                            break
                        elif response == 'h':
                            if item.help_text:
                                print_info(f"Help: {item.help_text}")
                            if item.validation_command:
                                print_info(f"Validation: {item.validation_command}")
                        elif response == 'q':
                            print_info("Quitting checklist...")
                            return False
                        else:
                            print_warning("Invalid input. Use Enter, 's', 'h', or 'q'")
                    except KeyboardInterrupt:
                        print_info("\nQuitting checklist...")
                        return False
            
            # Save progress after each category
            if self.save_progress:
                self.save_progress_to_file()
        
        return True
    
    def print_summary(self):
        """Print checklist summary."""
        completed_count = len([item for item in self.checklist_items if item.completed])
        total_count = len(self.checklist_items)
        completion_percentage = (completed_count / total_count) * 100
        
        print_header("Checklist Summary", 2)
        print_info(f"Completed: {completed_count}/{total_count} ({completion_percentage:.1f}%)")
        
        if completion_percentage == 100:
            print_success("🎉 All checklist items completed! You're ready for deployment!")
            print_info("Next step: Run the master validation script:")
            print_info("python scripts/master_deployment_validator.py")
        elif completion_percentage >= 80:
            print_warning("Almost ready! Complete the remaining items:")
            incomplete_items = [item for item in self.checklist_items if not item.completed]
            for item in incomplete_items:
                print_warning(f"  - {item.description}")
        else:
            print_error("More preparation needed. Focus on these categories:")
            categories = {}
            for item in self.checklist_items:
                if not item.completed:
                    if item.category not in categories:
                        categories[item.category] = 0
                    categories[item.category] += 1
            
            for category, count in categories.items():
                print_error(f"  - {category}: {count} items remaining")
        
        # Save final progress
        if self.save_progress:
            self.save_progress_to_file()

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Interactive pre-flight checklist for RAG AI-Agent deployment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/pre_flight_checklist.py
  python scripts/pre_flight_checklist.py --auto-check
  python scripts/pre_flight_checklist.py --save-progress
        """
    )
    
    parser.add_argument(
        "--auto-check",
        action="store_true",
        help="Automatically check items that can be validated"
    )
    
    parser.add_argument(
        "--save-progress",
        action="store_true",
        help="Save progress to file for resuming later"
    )
    
    args = parser.parse_args()
    
    # Create and run checklist
    checklist = PreFlightChecklist(
        auto_check=args.auto_check,
        save_progress=args.save_progress
    )
    
    try:
        completed = checklist.run_interactive_checklist()
        
        if completed:
            checklist.print_summary()
        else:
            print_info("Checklist incomplete. Run again to continue.")
        
        return 0
        
    except KeyboardInterrupt:
        print_info("\nChecklist interrupted by user")
        if args.save_progress:
            checklist.save_progress_to_file()
        return 1
    except Exception as e:
        print_error(f"Checklist failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())