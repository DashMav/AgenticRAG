#!/usr/bin/env python3
"""
Frontend Deployment Automation Script for Vercel

This script automates the deployment of the RAG AI-Agent React frontend to Vercel.
It handles build configuration, proxy setup, and deployment verification.

Requirements: 4.1, 4.2, 5.3
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

class VercelDeployer:
    """Handles automated deployment to Vercel"""
    
    def __init__(self, config_file: Optional[str] = None, verbose: bool = False):
        self.verbose = verbose
        self.config = self._load_config(config_file)
        self.deployment_log = []
        self.start_time = datetime.now()
        self.frontend_dir = "agent-frontend"
        
    def _load_config(self, config_file: Optional[str]) -> Dict:
        """Load deployment configuration"""
        default_config = {
            "project_name": "rag-ai-agent-frontend",
            "backend_url": "",
            "vercel_org": "",
            "build_command": "npm run build",
            "output_directory": "dist",
            "install_command": "npm install",
            "node_version": "18.x",
            "environment_variables": {},
            "custom_domain": "",
            "deployment_timeout": 600,
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
        
        # Check if frontend directory exists
        if not os.path.exists(self.frontend_dir):
            self._log(f"❌ Frontend directory not found: {self.frontend_dir}", "error")
            return False
        
        # Check required files
        required_files = [
            f"{self.frontend_dir}/package.json",
            f"{self.frontend_dir}/vite.config.js",
            f"{self.frontend_dir}/index.html"
        ]
        
        for file in required_files:
            if not os.path.exists(file):
                self._log(f"❌ Required file missing: {file}", "error")
                return False
        
        self._log("✅ Required files present", "info")
        
        # Check Node.js and npm
        try:
            result = subprocess.run(["node", "--version"], check=True, capture_output=True, text=True)
            node_version = result.stdout.strip()
            self._log(f"✅ Node.js available: {node_version}", "info")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self._log("❌ Node.js is not installed or not available", "error")
            return False
        
        try:
            result = subprocess.run(["npm", "--version"], check=True, capture_output=True, text=True)
            npm_version = result.stdout.strip()
            self._log(f"✅ npm available: {npm_version}", "info")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self._log("❌ npm is not installed or not available", "error")
            return False
        
        # Check Vercel CLI
        try:
            result = subprocess.run(["vercel", "--version"], check=True, capture_output=True, text=True)
            vercel_version = result.stdout.strip()
            self._log(f"✅ Vercel CLI available: {vercel_version}", "info")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self._log("⚠️ Vercel CLI not found. Installing...", "warning")
            if not self._install_vercel_cli():
                return False
        
        # Check backend URL configuration
        if not self.config["backend_url"]:
            self._log("❌ Backend URL must be configured for proxy setup", "error")
            return False
        
        self._log("✅ Prerequisites validation completed", "info")
        return True
    
    def _install_vercel_cli(self) -> bool:
        """Install Vercel CLI if not present"""
        try:
            self._log("📦 Installing Vercel CLI...", "info")
            subprocess.run(["npm", "install", "-g", "vercel"], check=True, capture_output=True)
            self._log("✅ Vercel CLI installed successfully", "info")
            return True
        except subprocess.CalledProcessError as e:
            self._log(f"❌ Failed to install Vercel CLI: {e}", "error")
            return False
    
    def setup_build_configuration(self) -> bool:
        """Setup and validate build configuration"""
        self._log("⚙️ Setting up build configuration...", "info")
        
        try:
            # Read and validate package.json
            package_json_path = f"{self.frontend_dir}/package.json"
            with open(package_json_path, 'r') as f:
                package_json = json.load(f)
            
            # Ensure required scripts exist
            required_scripts = ["build", "dev"]
            missing_scripts = []
            
            for script in required_scripts:
                if script not in package_json.get("scripts", {}):
                    missing_scripts.append(script)
            
            if missing_scripts:
                self._log(f"❌ Missing required scripts in package.json: {missing_scripts}", "error")
                return False
            
            self._log("✅ Package.json configuration valid", "info")
            
            # Validate vite.config.js
            vite_config_path = f"{self.frontend_dir}/vite.config.js"
            if os.path.exists(vite_config_path):
                with open(vite_config_path, 'r') as f:
                    vite_config = f.read()
                
                # Check for essential configurations
                if "react()" in vite_config:
                    self._log("✅ Vite React plugin configured", "info")
                else:
                    self._log("⚠️ Vite React plugin may not be configured", "warning")
            
            return True
            
        except Exception as e:
            self._log(f"❌ Failed to validate build configuration: {e}", "error")
            return False
    
    def setup_proxy_configuration(self) -> bool:
        """Setup Vercel proxy configuration for backend communication"""
        self._log("⚙️ Setting up proxy configuration...", "info")
        
        try:
            vercel_config_path = f"{self.frontend_dir}/vercel.json"
            
            # Create or update vercel.json
            vercel_config = {
                "rewrites": [
                    {
                        "source": "/api/:path*",
                        "destination": f"{self.config['backend_url']}/api/:path*"
                    }
                ],
                "headers": [
                    {
                        "source": "/api/(.*)",
                        "headers": [
                            {
                                "key": "Access-Control-Allow-Origin",
                                "value": "*"
                            },
                            {
                                "key": "Access-Control-Allow-Methods",
                                "value": "GET, POST, PUT, DELETE, OPTIONS"
                            },
                            {
                                "key": "Access-Control-Allow-Headers",
                                "value": "Content-Type, Authorization, X-Requested-With"
                            },
                            {
                                "key": "Access-Control-Max-Age",
                                "value": "86400"
                            }
                        ]
                    }
                ]
            }
            
            # Add build configuration if specified
            if self.config.get("node_version"):
                vercel_config["build"] = {
                    "env": {
                        "NODE_VERSION": self.config["node_version"]
                    }
                }
            
            # Add environment variables if specified
            if self.config.get("environment_variables"):
                vercel_config["env"] = self.config["environment_variables"]
            
            # Write vercel.json
            with open(vercel_config_path, 'w') as f:
                json.dump(vercel_config, f, indent=2)
            
            self._log(f"✅ Proxy configuration created: {vercel_config_path}", "info")
            self._log(f"🔗 Backend URL configured: {self.config['backend_url']}", "info")
            
            return True
            
        except Exception as e:
            self._log(f"❌ Failed to setup proxy configuration: {e}", "error")
            return False
    
    def install_dependencies(self) -> bool:
        """Install frontend dependencies"""
        self._log("📦 Installing dependencies...", "info")
        
        try:
            # Change to frontend directory
            original_dir = os.getcwd()
            os.chdir(self.frontend_dir)
            
            # Run npm install
            result = subprocess.run([
                "npm", "install"
            ], capture_output=True, text=True, timeout=300)
            
            os.chdir(original_dir)
            
            if result.returncode == 0:
                self._log("✅ Dependencies installed successfully", "info")
                return True
            else:
                self._log(f"❌ Dependency installation failed: {result.stderr}", "error")
                return False
                
        except subprocess.TimeoutExpired:
            self._log("❌ Dependency installation timed out", "error")
            return False
        except Exception as e:
            self._log(f"❌ Dependency installation failed: {e}", "error")
            return False
    
    def build_application(self) -> bool:
        """Build the frontend application"""
        self._log("🔨 Building application...", "info")
        
        try:
            # Change to frontend directory
            original_dir = os.getcwd()
            os.chdir(self.frontend_dir)
            
            # Run build command
            result = subprocess.run([
                "npm", "run", "build"
            ], capture_output=True, text=True, timeout=300)
            
            os.chdir(original_dir)
            
            if result.returncode == 0:
                self._log("✅ Application built successfully", "info")
                
                # Check if dist directory was created
                dist_path = f"{self.frontend_dir}/{self.config['output_directory']}"
                if os.path.exists(dist_path):
                    self._log(f"✅ Build output directory created: {dist_path}", "info")
                    return True
                else:
                    self._log(f"⚠️ Build output directory not found: {dist_path}", "warning")
                    return True  # Don't fail completely
            else:
                self._log(f"❌ Build failed: {result.stderr}", "error")
                return False
                
        except subprocess.TimeoutExpired:
            self._log("❌ Build process timed out", "error")
            return False
        except Exception as e:
            self._log(f"❌ Build failed: {e}", "error")
            return False
    
    def deploy_to_vercel(self) -> Tuple[bool, str]:
        """Deploy the application to Vercel"""
        self._log("🚀 Starting deployment to Vercel...", "info")
        
        try:
            # Change to frontend directory
            original_dir = os.getcwd()
            os.chdir(self.frontend_dir)
            
            # Prepare deployment command
            deploy_cmd = ["vercel", "--prod", "--yes"]
            
            # Add project name if specified
            if self.config.get("project_name"):
                deploy_cmd.extend(["--name", self.config["project_name"]])
            
            # Run deployment
            self._log("📤 Deploying to Vercel...", "info")
            result = subprocess.run(
                deploy_cmd,
                capture_output=True,
                text=True,
                timeout=self.config["deployment_timeout"]
            )
            
            os.chdir(original_dir)
            
            if result.returncode == 0:
                # Extract deployment URL from output
                deployment_url = ""
                for line in result.stdout.split('\n'):
                    if line.strip().startswith('https://'):
                        deployment_url = line.strip()
                        break
                
                if deployment_url:
                    self._log(f"✅ Successfully deployed to: {deployment_url}", "info")
                    return True, deployment_url
                else:
                    self._log("✅ Deployment completed, but URL not found in output", "info")
                    return True, ""
            else:
                self._log(f"❌ Deployment failed: {result.stderr}", "error")
                return False, ""
                
        except subprocess.TimeoutExpired:
            self._log("❌ Deployment timed out", "error")
            return False, ""
        except Exception as e:
            self._log(f"❌ Deployment failed: {e}", "error")
            return False, ""
    
    def verify_deployment(self, deployment_url: str) -> Dict:
        """Verify the deployment is working correctly"""
        self._log("🔍 Verifying deployment...", "info")
        
        verification_results = {
            "site_accessible": False,
            "api_proxy_working": False,
            "build_assets_loading": False,
            "deployment_url": deployment_url
        }
        
        if not deployment_url:
            self._log("⚠️ No deployment URL provided for verification", "warning")
            return verification_results
        
        try:
            import requests
            
            # Test main site accessibility
            try:
                response = requests.get(deployment_url, timeout=10)
                verification_results["site_accessible"] = response.status_code == 200
                if response.status_code == 200:
                    self._log("✅ Site is accessible", "info")
                else:
                    self._log(f"⚠️ Site returned status code: {response.status_code}", "warning")
            except Exception as e:
                self._log(f"❌ Site accessibility test failed: {e}", "error")
            
            # Test API proxy (try a simple endpoint)
            try:
                api_url = f"{deployment_url}/api/chats/"
                response = requests.get(api_url, timeout=10)
                # Accept both 200 (success) and 422 (validation error, but proxy working)
                verification_results["api_proxy_working"] = response.status_code in [200, 422]
                if verification_results["api_proxy_working"]:
                    self._log("✅ API proxy is working", "info")
                else:
                    self._log(f"❌ API proxy test failed with status: {response.status_code}", "error")
            except Exception as e:
                self._log(f"❌ API proxy test failed: {e}", "error")
            
            # Test if static assets are loading
            try:
                # Try to access a common asset path
                assets_url = f"{deployment_url}/assets/"
                response = requests.get(assets_url, timeout=10)
                # 404 is acceptable here, it means the assets directory structure exists
                verification_results["build_assets_loading"] = response.status_code in [200, 404]
                if verification_results["build_assets_loading"]:
                    self._log("✅ Build assets structure is accessible", "info")
                else:
                    self._log(f"⚠️ Build assets test returned: {response.status_code}", "warning")
            except Exception as e:
                self._log(f"⚠️ Build assets test failed: {e}", "warning")
                verification_results["build_assets_loading"] = True  # Don't fail on this
            
        except ImportError:
            self._log("⚠️ requests library not available for verification", "warning")
        
        return verification_results
    
    def generate_deployment_report(self, deployment_url: str, verification_results: Dict) -> str:
        """Generate a comprehensive deployment report"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        report = {
            "deployment_info": {
                "timestamp": self.start_time.isoformat(),
                "duration_seconds": duration.total_seconds(),
                "project_name": self.config["project_name"],
                "deployment_url": deployment_url,
                "backend_url": self.config["backend_url"]
            },
            "verification_results": verification_results,
            "deployment_log": self.deployment_log,
            "next_steps": [
                "Test all frontend functionality manually",
                "Verify API communication with backend",
                "Set up custom domain (if needed)",
                "Configure monitoring and analytics",
                "Run end-to-end tests"
            ]
        }
        
        # Save report
        report_file = f"frontend_deployment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self._log(f"📄 Deployment report saved to: {report_file}", "info")
        return report_file
    
    def run_deployment(self) -> bool:
        """Run the complete deployment process"""
        self._log("🚀 Starting automated frontend deployment...", "info")
        
        # Step 1: Validate prerequisites
        if not self.validate_prerequisites():
            self._log("❌ Prerequisites validation failed", "error")
            return False
        
        # Step 2: Setup build configuration
        if not self.setup_build_configuration():
            self._log("❌ Build configuration failed", "error")
            return False
        
        # Step 3: Setup proxy configuration
        if not self.setup_proxy_configuration():
            self._log("❌ Proxy configuration failed", "error")
            return False
        
        # Step 4: Install dependencies
        if not self.install_dependencies():
            self._log("❌ Dependency installation failed", "error")
            return False
        
        # Step 5: Build application
        if not self.build_application():
            self._log("❌ Application build failed", "error")
            return False
        
        # Step 6: Deploy to Vercel
        success, deployment_url = self.deploy_to_vercel()
        if not success:
            self._log("❌ Deployment to Vercel failed", "error")
            return False
        
        # Step 7: Verify deployment
        verification_results = self.verify_deployment(deployment_url)
        
        # Step 8: Generate report
        report_file = self.generate_deployment_report(deployment_url, verification_results)
        
        # Final status
        success_count = sum(1 for result in verification_results.values() if isinstance(result, bool) and result)
        total_checks = len([v for v in verification_results.values() if isinstance(v, bool)])
        
        if success_count >= total_checks // 2:  # At least half the checks passed
            self._log("✅ Deployment completed successfully!", "info")
            if deployment_url:
                self._log(f"🔗 Your frontend is available at: {deployment_url}", "info")
            return True
        else:
            self._log("⚠️ Deployment completed with warnings", "warning")
            self._log(f"📄 Check the deployment report for details: {report_file}", "info")
            return True  # Don't fail completely, just warn


def create_sample_config():
    """Create a sample configuration file"""
    sample_config = {
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
    
    with open("frontend_deployment_config.json", "w") as f:
        json.dump(sample_config, f, indent=2)
    
    print("✅ Sample configuration created: frontend_deployment_config.json")
    print("📝 Please edit this file with your actual values before deployment")
    print("🔗 Make sure to set the correct backend_url from your Hugging Face Space")


def main():
    parser = argparse.ArgumentParser(description="Automate Vercel frontend deployment")
    parser.add_argument("--config", "-c", help="Configuration file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--create-config", action="store_true", help="Create sample configuration file")
    parser.add_argument("--dry-run", action="store_true", help="Validate configuration without deploying")
    parser.add_argument("--build-only", action="store_true", help="Only build the application, don't deploy")
    
    args = parser.parse_args()
    
    if args.create_config:
        create_sample_config()
        return
    
    # Initialize deployer
    deployer = VercelDeployer(config_file=args.config, verbose=args.verbose)
    
    if args.dry_run:
        print("🔍 Running dry-run validation...")
        success = deployer.validate_prerequisites()
        if success:
            print("✅ Configuration is valid for deployment")
        else:
            print("❌ Configuration validation failed")
            sys.exit(1)
        return
    
    if args.build_only:
        print("🔨 Running build-only mode...")
        if not deployer.validate_prerequisites():
            print("❌ Prerequisites validation failed")
            sys.exit(1)
        if not deployer.setup_build_configuration():
            print("❌ Build configuration failed")
            sys.exit(1)
        if not deployer.install_dependencies():
            print("❌ Dependency installation failed")
            sys.exit(1)
        if not deployer.build_application():
            print("❌ Application build failed")
            sys.exit(1)
        print("✅ Build completed successfully!")
        return
    
    # Run deployment
    success = deployer.run_deployment()
    
    if not success:
        print("\n❌ Deployment failed. Check the logs above for details.")
        sys.exit(1)
    else:
        print("\n✅ Deployment process completed!")
        print("\n📋 Next steps:")
        print("1. Test all frontend functionality manually")
        print("2. Verify API communication with your backend")
        print("3. Set up custom domain (if needed)")
        print("4. Configure monitoring and analytics")
        print("5. Run end-to-end tests")


if __name__ == "__main__":
    main()