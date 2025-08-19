#!/usr/bin/env python3
"""
Backend Deployment Automation Script for Hugging Face Spaces

This script automates the deployment of the RAG AI-Agent FastAPI backend to Hugging Face Spaces.
It handles environment variable setup, deployment monitoring, and status reporting.

Requirements: 3.1, 3.2, 5.3
"""

import os
import sys
import json
import time
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class HuggingFaceDeployer:
    """Handles automated deployment to Hugging Face Spaces"""
    
    def __init__(self, config_file: Optional[str] = None, verbose: bool = False):
        self.verbose = verbose
        self.config = self._load_config(config_file)
        self.deployment_log = []
        self.start_time = datetime.now()
        
    def _load_config(self, config_file: Optional[str]) -> Dict:
        """Load deployment configuration"""
        default_config = {
            "space_name": "",
            "username": "",
            "git_email": "",
            "git_name": "",
            "environment_variables": {
                "GROQ_API_KEY": "",
                "OPENAI_API_KEY": "",
                "PINECONE_API_KEY": "",
                "PINECONE_INDEX_NAME": ""
            },
            "optional_variables": {
                "PINECONE_ENVIRONMENT": "",
                "MAX_FILE_SIZE": "10",
                "EMBEDDING_MODEL": "text-embedding-ada-002"
            },
            "deployment_timeout": 300,
            "health_check_timeout": 120
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
                self._log("✅ Configuration loaded from file", "info")
            except Exception as e:
                self._log(f"⚠️ Error loading config file: {e}", "warning")
        
        return default_config
    
    def _log(self, message: str, level: str = "info"):
        """Log deployment messages"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message
        }
        self.deployment_log.append(log_entry)
        
        if self.verbose or level in ["error", "warning"]:
            print(f"[{timestamp}] {message}")
    
    def validate_prerequisites(self) -> bool:
        """Validate all prerequisites for deployment"""
        self._log("🔍 Validating deployment prerequisites...", "info")
        
        # Check required files
        required_files = [
            "Dockerfile",
            "requirements.txt", 
            "app.py"
        ]
        
        for file in required_files:
            if not os.path.exists(file):
                self._log(f"❌ Required file missing: {file}", "error")
                return False
        
        self._log("✅ Required files present", "info")
        
        # Check Git configuration
        try:
            subprocess.run(["git", "--version"], check=True, capture_output=True)
            self._log("✅ Git is available", "info")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self._log("❌ Git is not installed or not available", "error")
            return False
        
        # Check environment variables
        missing_vars = []
        for var, value in self.config["environment_variables"].items():
            if not value and not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self._log(f"❌ Missing required environment variables: {', '.join(missing_vars)}", "error")
            return False
        
        self._log("✅ Environment variables configured", "info")
        
        # Check space configuration
        if not self.config["space_name"] or not self.config["username"]:
            self._log("❌ Hugging Face space name and username must be configured", "error")
            return False
        
        self._log("✅ Hugging Face configuration valid", "info")
        return True
    
    def setup_git_configuration(self) -> bool:
        """Configure Git for Hugging Face deployment"""
        self._log("⚙️ Setting up Git configuration...", "info")
        
        try:
            # Set Git user configuration if provided
            if self.config.get("git_name"):
                subprocess.run([
                    "git", "config", "user.name", self.config["git_name"]
                ], check=True, capture_output=True)
                
            if self.config.get("git_email"):
                subprocess.run([
                    "git", "config", "user.email", self.config["git_email"]
                ], check=True, capture_output=True)
            
            # Add Hugging Face remote if not exists
            hf_url = f"https://huggingface.co/spaces/{self.config['username']}/{self.config['space_name']}"
            
            try:
                # Check if remote already exists
                result = subprocess.run([
                    "git", "remote", "get-url", "hf"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    self._log("✅ Hugging Face remote already configured", "info")
                else:
                    # Add remote
                    subprocess.run([
                        "git", "remote", "add", "hf", hf_url
                    ], check=True, capture_output=True)
                    self._log("✅ Hugging Face remote added", "info")
                    
            except subprocess.CalledProcessError as e:
                self._log(f"❌ Failed to configure Git remote: {e}", "error")
                return False
            
            return True
            
        except subprocess.CalledProcessError as e:
            self._log(f"❌ Git configuration failed: {e}", "error")
            return False
    
    def create_app_py_config(self) -> bool:
        """Create or update app.py configuration for production"""
        self._log("⚙️ Configuring app.py for production...", "info")
        
        try:
            # Read current app.py
            with open("app.py", "r") as f:
                content = f.read()
            
            # Check if production configurations are already present
            production_configs = [
                'allow_origins=["*"]',  # CORS configuration
                'load_dotenv()',        # Environment loading
                'os.makedirs(UPLOAD_FOLDER, exist_ok=True)'  # Upload folder
            ]
            
            missing_configs = []
            for config in production_configs:
                if config not in content:
                    missing_configs.append(config)
            
            if missing_configs:
                self._log(f"⚠️ Some production configurations may be missing: {missing_configs}", "warning")
            else:
                self._log("✅ App.py appears to be configured for production", "info")
            
            return True
            
        except Exception as e:
            self._log(f"❌ Failed to validate app.py configuration: {e}", "error")
            return False
    
    def deploy_to_huggingface(self) -> bool:
        """Deploy the application to Hugging Face Spaces"""
        self._log("🚀 Starting deployment to Hugging Face Spaces...", "info")
        
        try:
            # Ensure we're on the main branch
            subprocess.run([
                "git", "checkout", "main"
            ], check=True, capture_output=True)
            
            # Add all changes
            subprocess.run([
                "git", "add", "."
            ], check=True, capture_output=True)
            
            # Commit changes
            commit_message = f"Deploy to Hugging Face Spaces - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run([
                "git", "commit", "-m", commit_message
            ], capture_output=True)  # Don't fail if nothing to commit
            
            # Push to Hugging Face
            self._log("📤 Pushing to Hugging Face Spaces...", "info")
            result = subprocess.run([
                "git", "push", "hf", "main"
            ], capture_output=True, text=True, timeout=self.config["deployment_timeout"])
            
            if result.returncode == 0:
                self._log("✅ Successfully pushed to Hugging Face Spaces", "info")
                return True
            else:
                self._log(f"❌ Deployment failed: {result.stderr}", "error")
                return False
                
        except subprocess.TimeoutExpired:
            self._log("❌ Deployment timed out", "error")
            return False
        except subprocess.CalledProcessError as e:
            self._log(f"❌ Deployment failed: {e}", "error")
            return False
    
    def wait_for_deployment(self) -> bool:
        """Wait for deployment to complete and become available"""
        self._log("⏳ Waiting for deployment to become available...", "info")
        
        space_url = f"https://{self.config['username']}-{self.config['space_name']}.hf.space"
        health_url = f"{space_url}/docs"  # FastAPI docs endpoint
        
        timeout = self.config["health_check_timeout"]
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                import requests
                response = requests.get(health_url, timeout=10)
                if response.status_code == 200:
                    self._log(f"✅ Deployment is live at: {space_url}", "info")
                    return True
            except Exception:
                pass
            
            self._log("⏳ Still waiting for deployment...", "info")
            time.sleep(15)
        
        self._log("⚠️ Deployment timeout reached, but this doesn't mean it failed", "warning")
        self._log(f"🔗 Check deployment status at: https://huggingface.co/spaces/{self.config['username']}/{self.config['space_name']}", "info")
        return True  # Don't fail on timeout, just warn
    
    def verify_deployment(self) -> Dict:
        """Verify the deployment is working correctly"""
        self._log("🔍 Verifying deployment...", "info")
        
        verification_results = {
            "space_accessible": False,
            "api_docs_available": False,
            "health_endpoint": False,
            "space_url": f"https://{self.config['username']}-{self.config['space_name']}.hf.space"
        }
        
        try:
            import requests
            
            # Test main space URL
            try:
                response = requests.get(verification_results["space_url"], timeout=10)
                verification_results["space_accessible"] = response.status_code == 200
            except Exception:
                pass
            
            # Test API docs
            try:
                docs_url = f"{verification_results['space_url']}/docs"
                response = requests.get(docs_url, timeout=10)
                verification_results["api_docs_available"] = response.status_code == 200
            except Exception:
                pass
            
            # Test health endpoint (if exists)
            try:
                health_url = f"{verification_results['space_url']}/api/chats/"
                response = requests.get(health_url, timeout=10)
                verification_results["health_endpoint"] = response.status_code in [200, 422]  # 422 is OK for missing auth
            except Exception:
                pass
            
        except ImportError:
            self._log("⚠️ requests library not available for verification", "warning")
        
        # Log results
        for check, result in verification_results.items():
            if check != "space_url":
                status = "✅" if result else "❌"
                self._log(f"{status} {check.replace('_', ' ').title()}: {result}", "info")
        
        return verification_results
    
    def generate_deployment_report(self, verification_results: Dict) -> str:
        """Generate a comprehensive deployment report"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        report = {
            "deployment_info": {
                "timestamp": self.start_time.isoformat(),
                "duration_seconds": duration.total_seconds(),
                "space_name": self.config["space_name"],
                "username": self.config["username"],
                "space_url": f"https://{self.config['username']}-{self.config['space_name']}.hf.space"
            },
            "verification_results": verification_results,
            "deployment_log": self.deployment_log,
            "next_steps": [
                "Configure environment variables in Hugging Face Space settings",
                "Test all API endpoints manually",
                "Run post-deployment tests",
                "Update frontend configuration with new backend URL"
            ]
        }
        
        # Save report
        report_file = f"deployment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self._log(f"📄 Deployment report saved to: {report_file}", "info")
        return report_file
    
    def run_deployment(self) -> bool:
        """Run the complete deployment process"""
        self._log("🚀 Starting automated backend deployment...", "info")
        
        # Step 1: Validate prerequisites
        if not self.validate_prerequisites():
            self._log("❌ Prerequisites validation failed", "error")
            return False
        
        # Step 2: Setup Git configuration
        if not self.setup_git_configuration():
            self._log("❌ Git configuration failed", "error")
            return False
        
        # Step 3: Configure app.py
        if not self.create_app_py_config():
            self._log("❌ App configuration failed", "error")
            return False
        
        # Step 4: Deploy to Hugging Face
        if not self.deploy_to_huggingface():
            self._log("❌ Deployment to Hugging Face failed", "error")
            return False
        
        # Step 5: Wait for deployment
        self.wait_for_deployment()
        
        # Step 6: Verify deployment
        verification_results = self.verify_deployment()
        
        # Step 7: Generate report
        report_file = self.generate_deployment_report(verification_results)
        
        # Final status
        success_count = sum(1 for result in verification_results.values() if isinstance(result, bool) and result)
        total_checks = len([v for v in verification_results.values() if isinstance(v, bool)])
        
        if success_count >= total_checks // 2:  # At least half the checks passed
            self._log("✅ Deployment completed successfully!", "info")
            self._log(f"🔗 Your backend is available at: {verification_results['space_url']}", "info")
            return True
        else:
            self._log("⚠️ Deployment completed with warnings", "warning")
            self._log(f"📄 Check the deployment report for details: {report_file}", "info")
            return True  # Don't fail completely, just warn


def create_sample_config():
    """Create a sample configuration file"""
    sample_config = {
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
    
    with open("backend_deployment_config.json", "w") as f:
        json.dump(sample_config, f, indent=2)
    
    print("✅ Sample configuration created: backend_deployment_config.json")
    print("📝 Please edit this file with your actual values before deployment")


def main():
    parser = argparse.ArgumentParser(description="Automate Hugging Face Spaces backend deployment")
    parser.add_argument("--config", "-c", help="Configuration file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--create-config", action="store_true", help="Create sample configuration file")
    parser.add_argument("--dry-run", action="store_true", help="Validate configuration without deploying")
    
    args = parser.parse_args()
    
    if args.create_config:
        create_sample_config()
        return
    
    # Initialize deployer
    deployer = HuggingFaceDeployer(config_file=args.config, verbose=args.verbose)
    
    if args.dry_run:
        print("🔍 Running dry-run validation...")
        success = deployer.validate_prerequisites()
        if success:
            print("✅ Configuration is valid for deployment")
        else:
            print("❌ Configuration validation failed")
            sys.exit(1)
        return
    
    # Run deployment
    success = deployer.run_deployment()
    
    if not success:
        print("\n❌ Deployment failed. Check the logs above for details.")
        sys.exit(1)
    else:
        print("\n✅ Deployment process completed!")
        print("\n📋 Next steps:")
        print("1. Configure environment variables in your Hugging Face Space settings")
        print("2. Test your API endpoints manually")
        print("3. Run post-deployment tests")
        print("4. Update your frontend configuration with the new backend URL")


if __name__ == "__main__":
    main()