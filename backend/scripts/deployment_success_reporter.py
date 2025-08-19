#!/usr/bin/env python3
"""
Deployment Success Reporter for RAG AI-Agent

This script provides deployment success reporting and next steps guidance
after successful deployment validation and deployment completion.

Usage:
    python scripts/deployment_success_reporter.py
    python scripts/deployment_success_reporter.py --backend-url https://your-backend.hf.space
    python scripts/deployment_success_reporter.py --frontend-url https://your-frontend.vercel.app
    python scripts/deployment_success_reporter.py --full-report

Requirements:
    - Successful deployment validation
    - Backend and frontend URLs (optional)
"""

import os
import sys
import json
import argparse
import datetime
import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
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
class DeploymentStatus:
    """Deployment status information."""
    component: str
    status: str  # 'success', 'warning', 'error', 'unknown'
    url: Optional[str] = None
    message: str = ""
    details: Dict = None

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

def print_celebration(text: str):
    """Print celebration message."""
    print(f"{Colors.MAGENTA}{Colors.BOLD}🎉 {text} 🎉{Colors.END}")

class DeploymentSuccessReporter:
    """Reports deployment success and provides next steps guidance."""
    
    def __init__(self, backend_url: Optional[str] = None, frontend_url: Optional[str] = None):
        self.backend_url = backend_url
        self.frontend_url = frontend_url
        self.deployment_status = []
        self.timestamp = datetime.datetime.now()
    
    def check_backend_health(self) -> DeploymentStatus:
        """Check backend deployment health."""
        if not self.backend_url:
            return DeploymentStatus(
                component="Backend",
                status="unknown",
                message="Backend URL not provided"
            )
        
        try:
            # Check health endpoint
            health_url = f"{self.backend_url.rstrip('/')}/health"
            response = requests.get(health_url, timeout=10)
            
            if response.status_code == 200:
                return DeploymentStatus(
                    component="Backend",
                    status="success",
                    url=self.backend_url,
                    message="Backend is healthy and responding",
                    details={"health_endpoint": health_url, "response_time": response.elapsed.total_seconds()}
                )
            else:
                return DeploymentStatus(
                    component="Backend",
                    status="warning",
                    url=self.backend_url,
                    message=f"Backend responding but health check returned {response.status_code}",
                    details={"health_endpoint": health_url, "status_code": response.status_code}
                )
                
        except requests.exceptions.Timeout:
            return DeploymentStatus(
                component="Backend",
                status="error",
                url=self.backend_url,
                message="Backend health check timed out"
            )
        except requests.exceptions.ConnectionError:
            return DeploymentStatus(
                component="Backend",
                status="error",
                url=self.backend_url,
                message="Cannot connect to backend"
            )
        except Exception as e:
            return DeploymentStatus(
                component="Backend",
                status="error",
                url=self.backend_url,
                message=f"Backend health check failed: {str(e)}"
            )
    
    def check_frontend_health(self) -> DeploymentStatus:
        """Check frontend deployment health."""
        if not self.frontend_url:
            return DeploymentStatus(
                component="Frontend",
                status="unknown",
                message="Frontend URL not provided"
            )
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            
            if response.status_code == 200:
                # Check if it's actually the React app (look for common indicators)
                content = response.text.lower()
                if 'react' in content or 'vite' in content or 'rag ai-agent' in content:
                    return DeploymentStatus(
                        component="Frontend",
                        status="success",
                        url=self.frontend_url,
                        message="Frontend is accessible and appears to be the correct application",
                        details={"response_time": response.elapsed.total_seconds()}
                    )
                else:
                    return DeploymentStatus(
                        component="Frontend",
                        status="warning",
                        url=self.frontend_url,
                        message="Frontend is accessible but content may not be correct",
                        details={"response_time": response.elapsed.total_seconds()}
                    )
            else:
                return DeploymentStatus(
                    component="Frontend",
                    status="error",
                    url=self.frontend_url,
                    message=f"Frontend returned status code {response.status_code}",
                    details={"status_code": response.status_code}
                )
                
        except requests.exceptions.Timeout:
            return DeploymentStatus(
                component="Frontend",
                status="error",
                url=self.frontend_url,
                message="Frontend request timed out"
            )
        except requests.exceptions.ConnectionError:
            return DeploymentStatus(
                component="Frontend",
                status="error",
                url=self.frontend_url,
                message="Cannot connect to frontend"
            )
        except Exception as e:
            return DeploymentStatus(
                component="Frontend",
                status="error",
                url=self.frontend_url,
                message=f"Frontend health check failed: {str(e)}"
            )
    
    def check_api_integration(self) -> DeploymentStatus:
        """Check frontend-backend integration."""
        if not self.backend_url or not self.frontend_url:
            return DeploymentStatus(
                component="API Integration",
                status="unknown",
                message="Both frontend and backend URLs required for integration test"
            )
        
        try:
            # Check if backend API is accessible from frontend perspective
            api_url = f"{self.backend_url.rstrip('/')}/docs"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                return DeploymentStatus(
                    component="API Integration",
                    status="success",
                    message="Backend API documentation is accessible",
                    details={"api_docs_url": api_url}
                )
            else:
                return DeploymentStatus(
                    component="API Integration",
                    status="warning",
                    message="Backend API may not be properly configured",
                    details={"api_docs_url": api_url, "status_code": response.status_code}
                )
                
        except Exception as e:
            return DeploymentStatus(
                component="API Integration",
                status="error",
                message=f"API integration check failed: {str(e)}"
            )
    
    def load_validation_report(self) -> Optional[Dict]:
        """Load the latest validation report if available."""
        report_path = Path("deployment_validation_report.json")
        
        if report_path.exists():
            try:
                with open(report_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print_warning(f"Could not load validation report: {e}")
        
        return None
    
    def generate_success_report(self) -> Dict:
        """Generate comprehensive success report."""
        print_header("RAG AI-Agent Deployment Success Report", 1)
        
        # Check deployment status
        print_header("Deployment Status Check", 2)
        
        backend_status = self.check_backend_health()
        frontend_status = self.check_frontend_health()
        integration_status = self.check_api_integration()
        
        self.deployment_status = [backend_status, frontend_status, integration_status]
        
        # Print status for each component
        for status in self.deployment_status:
            if status.status == "success":
                print_success(f"{status.component}: {status.message}")
                if status.url:
                    print_info(f"  URL: {status.url}")
            elif status.status == "warning":
                print_warning(f"{status.component}: {status.message}")
                if status.url:
                    print_info(f"  URL: {status.url}")
            elif status.status == "error":
                print_error(f"{status.component}: {status.message}")
                if status.url:
                    print_info(f"  URL: {status.url}")
            else:
                print_info(f"{status.component}: {status.message}")
        
        # Overall assessment
        successful_components = len([s for s in self.deployment_status if s.status == "success"])
        total_components = len([s for s in self.deployment_status if s.status != "unknown"])
        
        print_header("Overall Assessment", 2)
        
        if successful_components == total_components and total_components > 0:
            print_celebration("DEPLOYMENT SUCCESSFUL!")
            print_success("All components are working correctly!")
            overall_status = "success"
        elif successful_components > 0:
            print_warning(f"PARTIAL SUCCESS: {successful_components}/{total_components} components working")
            overall_status = "partial"
        else:
            print_error("DEPLOYMENT ISSUES DETECTED")
            print_error("Please check the issues above and redeploy if necessary")
            overall_status = "failed"
        
        # Load validation report for context
        validation_report = self.load_validation_report()
        
        # Generate next steps
        next_steps = self.generate_next_steps(overall_status)
        
        # Create report
        report = {
            "timestamp": self.timestamp.isoformat(),
            "overall_status": overall_status,
            "deployment_status": [
                {
                    "component": s.component,
                    "status": s.status,
                    "url": s.url,
                    "message": s.message,
                    "details": s.details
                }
                for s in self.deployment_status
            ],
            "summary": {
                "successful_components": successful_components,
                "total_components": total_components,
                "backend_url": self.backend_url,
                "frontend_url": self.frontend_url
            },
            "validation_report": validation_report,
            "next_steps": next_steps
        }
        
        return report
    
    def generate_next_steps(self, overall_status: str) -> List[str]:
        """Generate next steps based on deployment status."""
        if overall_status == "success":
            return [
                "🎉 Congratulations! Your RAG AI-Agent is successfully deployed!",
                "",
                "Immediate Next Steps:",
                "1. Test the application end-to-end by uploading a document and asking questions",
                "2. Verify both Simple Chat and Agent modes are working",
                "3. Test chat management features (create, rename, delete chats)",
                "4. Share the frontend URL with intended users",
                "",
                "Recommended Actions:",
                "5. Set up monitoring for both frontend and backend",
                "6. Configure backup procedures for important data",
                "7. Document any custom configurations for future reference",
                "8. Plan regular maintenance and updates",
                "",
                "Monitoring & Maintenance:",
                "9. Bookmark the backend health endpoint for monitoring",
                "10. Set up alerts for service downtime (optional)",
                "11. Review API usage and quotas regularly",
                "12. Keep dependencies updated for security",
                "",
                "Support Resources:",
                "- Check TROUBLESHOOTING_GUIDE.md for common issues",
                "- Review API documentation at your backend URL + '/docs'",
                "- Monitor application logs for any errors",
                "- Keep your API keys secure and rotate them regularly"
            ]
        elif overall_status == "partial":
            return [
                "⚠️ Partial deployment success - some components need attention",
                "",
                "Immediate Actions Required:",
                "1. Review the component status above",
                "2. Fix any failed components before proceeding",
                "3. Re-run this script after fixes to verify",
                "",
                "Common Issues to Check:",
                "4. Verify all environment variables are set correctly",
                "5. Check that API keys have proper permissions",
                "6. Ensure network connectivity between components",
                "7. Verify CORS configuration allows frontend-backend communication",
                "",
                "If Backend Failed:",
                "8. Check Hugging Face Spaces logs for errors",
                "9. Verify Docker build completed successfully",
                "10. Ensure all secrets are properly configured",
                "",
                "If Frontend Failed:",
                "11. Check Vercel deployment logs",
                "12. Verify vercel.json proxy configuration",
                "13. Ensure build process completed without errors",
                "",
                "Get Help:",
                "- Review TROUBLESHOOTING_GUIDE.md",
                "- Check deployment platform documentation",
                "- Verify all prerequisites are met"
            ]
        else:
            return [
                "❌ Deployment failed - immediate action required",
                "",
                "Critical Actions:",
                "1. Do not share URLs with users until issues are resolved",
                "2. Review all error messages above carefully",
                "3. Check deployment platform logs for detailed errors",
                "",
                "Troubleshooting Steps:",
                "4. Re-run the master validation script:",
                "   python scripts/master_deployment_validator.py",
                "5. Address any validation failures",
                "6. Redeploy components that failed",
                "7. Re-run this success reporter after fixes",
                "",
                "Common Failure Causes:",
                "8. Missing or incorrect environment variables",
                "9. API keys without proper permissions",
                "10. Network connectivity issues",
                "11. Incorrect deployment configuration",
                "12. Service quotas or limits exceeded",
                "",
                "Get Help:",
                "- Start with TROUBLESHOOTING_GUIDE.md",
                "- Check DEPLOYMENT_GUIDE.md for step-by-step instructions",
                "- Verify all prerequisites in DEPLOYMENT_CHECKLIST.md",
                "- Review platform-specific documentation"
            ]
    
    def print_next_steps(self, next_steps: List[str]):
        """Print next steps in a formatted way."""
        print_header("Next Steps", 2)
        
        for step in next_steps:
            if step.startswith(('🎉', '⚠️', '❌')):
                if step.startswith('🎉'):
                    print_celebration(step)
                elif step.startswith('⚠️'):
                    print_warning(step)
                else:
                    print_error(step)
            elif step == "":
                print()  # Empty line
            elif step.endswith(':'):
                print(f"{Colors.BOLD}{Colors.CYAN}{step}{Colors.END}")
            elif step.startswith(('Immediate', 'Recommended', 'Monitoring', 'Support', 'Critical', 'Troubleshooting', 'Common', 'Get Help')):
                print(f"{Colors.BOLD}{Colors.BLUE}{step}{Colors.END}")
            else:
                print_info(step)
    
    def save_report(self, report: Dict, output_path: str):
        """Save the success report to a JSON file."""
        try:
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            print_success(f"Success report saved to: {output_path}")
        except Exception as e:
            print_error(f"Failed to save report: {e}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Generate deployment success report for RAG AI-Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/deployment_success_reporter.py
  python scripts/deployment_success_reporter.py --backend-url https://your-backend.hf.space
  python scripts/deployment_success_reporter.py --frontend-url https://your-frontend.vercel.app
  python scripts/deployment_success_reporter.py --full-report --output success_report.json
        """
    )
    
    parser.add_argument(
        "--backend-url",
        type=str,
        help="Backend URL (Hugging Face Spaces)"
    )
    
    parser.add_argument(
        "--frontend-url",
        type=str,
        help="Frontend URL (Vercel)"
    )
    
    parser.add_argument(
        "--full-report",
        action="store_true",
        help="Generate and save a detailed JSON report"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="deployment_success_report.json",
        help="Output file for JSON report (default: deployment_success_report.json)"
    )
    
    args = parser.parse_args()
    
    # Create reporter
    reporter = DeploymentSuccessReporter(
        backend_url=args.backend_url,
        frontend_url=args.frontend_url
    )
    
    try:
        # Generate report
        report = reporter.generate_success_report()
        
        # Print next steps
        reporter.print_next_steps(report["next_steps"])
        
        # Save report if requested
        if args.full_report:
            reporter.save_report(report, args.output)
        
        # Print final message
        print_header("Report Complete", 2)
        if report["overall_status"] == "success":
            print_celebration("Your RAG AI-Agent deployment is ready for users!")
            print_info("Share your frontend URL and start helping users with their documents!")
        elif report["overall_status"] == "partial":
            print_warning("Please address the issues above before sharing with users.")
        else:
            print_error("Deployment needs attention before it can be used.")
        
        # Exit with appropriate code
        return 0 if report["overall_status"] in ["success", "partial"] else 1
        
    except KeyboardInterrupt:
        print_error("\nReport generation interrupted by user")
        return 1
    except Exception as e:
        print_error(f"Report generation failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())