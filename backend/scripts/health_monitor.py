#!/usr/bin/env python3
"""
RAG AI Agent - Health Monitoring Script

This script monitors the health of all application components including
backend API, frontend, and external services like Pinecone.
"""

import os
import sys
import json
import time
import smtplib
import argparse
from datetime import datetime
from email.mime.text import MIMEText
from typing import Dict, Any, Optional, List

try:
    import requests
except ImportError:
    print("❌ Error: requests not installed")
    print("Install with: pip install requests")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  Warning: python-dotenv not installed, using system environment variables")


class HealthMonitor:
    """Monitors health of RAG AI Agent components"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._load_config()
        self.results = {}
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        return {
            "backend_url": os.getenv("BACKEND_URL", ""),
            "frontend_url": os.getenv("FRONTEND_URL", ""),
            "pinecone_api_key": os.getenv("PINECONE_API_KEY", ""),
            "pinecone_index_name": os.getenv("PINECONE_INDEX_NAME", ""),
            "groq_api_key": os.getenv("GROQ_API_KEY", ""),
            "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
            "timeout": int(os.getenv("HEALTH_CHECK_TIMEOUT", "30")),
            "smtp_server": os.getenv("SMTP_SERVER", ""),
            "smtp_port": int(os.getenv("SMTP_PORT", "587")),
            "email_user": os.getenv("EMAIL_USER", ""),
            "email_pass": os.getenv("EMAIL_PASS", ""),
            "alert_email": os.getenv("ALERT_EMAIL", "")
        }
    
    def check_backend_health(self) -> Dict[str, Any]:
        """Check backend API health"""
        result = {
            "service": "Backend API",
            "status": False,
            "response_time": None,
            "status_code": None,
            "error": None,
            "details": {}
        }
        
        if not self.config["backend_url"]:
            result["error"] = "Backend URL not configured"
            return result
        
        try:
            start_time = time.time()
            
            # Check health endpoint
            health_url = f"{self.config['backend_url'].rstrip('/')}/health"
            response = requests.get(health_url, timeout=self.config["timeout"])
            
            end_time = time.time()
            result["response_time"] = end_time - start_time
            result["status_code"] = response.status_code
            
            if response.status_code == 200:
                result["status"] = True
                try:
                    result["details"] = response.json()
                except:
                    result["details"] = {"response": "OK"}
            else:
                result["error"] = f"HTTP {response.status_code}"
                
        except requests.exceptions.Timeout:
            result["error"] = "Request timeout"
        except requests.exceptions.ConnectionError:
            result["error"] = "Connection failed"
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def check_frontend_health(self) -> Dict[str, Any]:
        """Check frontend availability"""
        result = {
            "service": "Frontend",
            "status": False,
            "response_time": None,
            "status_code": None,
            "error": None,
            "details": {}
        }
        
        if not self.config["frontend_url"]:
            result["error"] = "Frontend URL not configured"
            return result
        
        try:
            start_time = time.time()
            
            response = requests.get(
                self.config["frontend_url"], 
                timeout=self.config["timeout"],
                headers={"User-Agent": "HealthMonitor/1.0"}
            )
            
            end_time = time.time()
            result["response_time"] = end_time - start_time
            result["status_code"] = response.status_code
            
            if response.status_code == 200:
                result["status"] = True
                result["details"] = {
                    "content_length": len(response.content),
                    "content_type": response.headers.get("content-type", "")
                }
            else:
                result["error"] = f"HTTP {response.status_code}"
                
        except requests.exceptions.Timeout:
            result["error"] = "Request timeout"
        except requests.exceptions.ConnectionError:
            result["error"] = "Connection failed"
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def check_pinecone_health(self) -> Dict[str, Any]:
        """Check Pinecone connectivity"""
        result = {
            "service": "Pinecone",
            "status": False,
            "response_time": None,
            "error": None,
            "details": {}
        }
        
        if not self.config["pinecone_api_key"]:
            result["error"] = "Pinecone API key not configured"
            return result
        
        if not self.config["pinecone_index_name"]:
            result["error"] = "Pinecone index name not configured"
            return result
        
        try:
            import pinecone
            from pinecone import Pinecone
            
            start_time = time.time()
            
            # Initialize Pinecone
            pc = Pinecone(api_key=self.config["pinecone_api_key"])
            index = pc.Index(self.config["pinecone_index_name"])
            
            # Get index statistics
            stats = index.describe_index_stats()
            
            end_time = time.time()
            result["response_time"] = end_time - start_time
            result["status"] = True
            result["details"] = {
                "total_vector_count": stats.get("total_vector_count", 0),
                "dimension": stats.get("dimension", "unknown"),
                "index_fullness": stats.get("index_fullness", 0)
            }
            
        except ImportError:
            result["error"] = "pinecone-client not installed"
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def check_groq_health(self) -> Dict[str, Any]:
        """Check Groq API connectivity"""
        result = {
            "service": "Groq API",
            "status": False,
            "response_time": None,
            "error": None,
            "details": {}
        }
        
        if not self.config["groq_api_key"]:
            result["error"] = "Groq API key not configured"
            return result
        
        try:
            start_time = time.time()
            
            # Test Groq API with a simple request
            headers = {
                "Authorization": f"Bearer {self.config['groq_api_key']}",
                "Content-Type": "application/json"
            }
            
            # Use models endpoint to test connectivity
            response = requests.get(
                "https://api.groq.com/openai/v1/models",
                headers=headers,
                timeout=self.config["timeout"]
            )
            
            end_time = time.time()
            result["response_time"] = end_time - start_time
            result["status_code"] = response.status_code
            
            if response.status_code == 200:
                result["status"] = True
                models_data = response.json()
                result["details"] = {
                    "available_models": len(models_data.get("data", [])),
                    "api_accessible": True
                }
            else:
                result["error"] = f"HTTP {response.status_code}"
                
        except requests.exceptions.Timeout:
            result["error"] = "Request timeout"
        except requests.exceptions.ConnectionError:
            result["error"] = "Connection failed"
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def check_openai_health(self) -> Dict[str, Any]:
        """Check OpenAI API connectivity"""
        result = {
            "service": "OpenAI API",
            "status": False,
            "response_time": None,
            "error": None,
            "details": {}
        }
        
        if not self.config["openai_api_key"]:
            result["error"] = "OpenAI API key not configured"
            return result
        
        try:
            start_time = time.time()
            
            # Test OpenAI API with models endpoint
            headers = {
                "Authorization": f"Bearer {self.config['openai_api_key']}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                "https://api.openai.com/v1/models",
                headers=headers,
                timeout=self.config["timeout"]
            )
            
            end_time = time.time()
            result["response_time"] = end_time - start_time
            result["status_code"] = response.status_code
            
            if response.status_code == 200:
                result["status"] = True
                models_data = response.json()
                result["details"] = {
                    "available_models": len(models_data.get("data", [])),
                    "api_accessible": True
                }
            else:
                result["error"] = f"HTTP {response.status_code}"
                
        except requests.exceptions.Timeout:
            result["error"] = "Request timeout"
        except requests.exceptions.ConnectionError:
            result["error"] = "Connection failed"
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        print("🔍 Running health checks...")
        
        checks = {
            "backend": self.check_backend_health,
            "frontend": self.check_frontend_health,
            "pinecone": self.check_pinecone_health,
            "groq": self.check_groq_health,
            "openai": self.check_openai_health
        }
        
        results = {}
        
        for check_name, check_func in checks.items():
            print(f"  Checking {check_name}...", end=" ", flush=True)
            
            try:
                result = check_func()
                results[check_name] = result
                
                if result["status"]:
                    print("✅")
                else:
                    print(f"❌ ({result['error']})")
                    
            except Exception as e:
                print(f"❌ (Exception: {e})")
                results[check_name] = {
                    "service": check_name,
                    "status": False,
                    "error": f"Check failed: {e}"
                }
        
        return results
    
    def display_results(self, results: Dict[str, Any]):
        """Display health check results"""
        print("\n📊 Health Check Results:")
        print("=" * 60)
        
        total_checks = len(results)
        passed_checks = sum(1 for r in results.values() if r["status"])
        
        for check_name, result in results.items():
            status_icon = "✅" if result["status"] else "❌"
            service_name = result.get("service", check_name.title())
            
            print(f"{status_icon} {service_name}")
            
            if result["status"]:
                if result.get("response_time"):
                    print(f"   Response time: {result['response_time']:.2f}s")
                
                if result.get("details"):
                    for key, value in result["details"].items():
                        print(f"   {key.replace('_', ' ').title()}: {value}")
            else:
                print(f"   Error: {result.get('error', 'Unknown error')}")
            
            print()
        
        # Summary
        print(f"📈 Summary: {passed_checks}/{total_checks} checks passed")
        
        if passed_checks == total_checks:
            print("🎉 All systems operational!")
        else:
            failed_services = [
                result.get("service", name) 
                for name, result in results.items() 
                if not result["status"]
            ]
            print(f"⚠️  Issues detected with: {', '.join(failed_services)}")
        
        return passed_checks == total_checks
    
    def send_alert(self, results: Dict[str, Any]):
        """Send alert email for failed checks"""
        failed_checks = [
            result for result in results.values() 
            if not result["status"]
        ]
        
        if not failed_checks:
            return  # No failures to report
        
        # Check if email is configured
        if not all([
            self.config["smtp_server"],
            self.config["email_user"],
            self.config["email_pass"],
            self.config["alert_email"]
        ]):
            print("📧 Email configuration missing, skipping alert")
            return
        
        # Compose alert message
        message = "RAG AI Agent Health Check Alert\n"
        message += "=" * 40 + "\n\n"
        message += f"Timestamp: {datetime.now().isoformat()}\n\n"
        message += "Failed Health Checks:\n\n"
        
        for result in failed_checks:
            service = result.get("service", "Unknown")
            error = result.get("error", "Unknown error")
            message += f"❌ {service}: {error}\n"
        
        message += f"\nTotal failures: {len(failed_checks)}\n"
        message += f"Total checks: {len(results)}\n"
        
        # Send email
        try:
            msg = MIMEText(message)
            msg['Subject'] = f"RAG AI Agent Alert - {len(failed_checks)} service(s) down"
            msg['From'] = self.config["email_user"]
            msg['To'] = self.config["alert_email"]
            
            server = smtplib.SMTP(self.config["smtp_server"], self.config["smtp_port"])
            server.starttls()
            server.login(self.config["email_user"], self.config["email_pass"])
            server.send_message(msg)
            server.quit()
            
            print("📧 Alert email sent successfully")
            
        except Exception as e:
            print(f"📧 Failed to send alert email: {e}")
    
    def log_results(self, results: Dict[str, Any], log_file: str = "health_monitor.log"):
        """Log results to file"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "summary": {
                "total_checks": len(results),
                "passed_checks": sum(1 for r in results.values() if r["status"]),
                "failed_checks": [
                    result.get("service", name) 
                    for name, result in results.items() 
                    if not result["status"]
                ]
            }
        }
        
        try:
            with open(log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
            
            print(f"📝 Results logged to {log_file}")
            
        except Exception as e:
            print(f"📝 Failed to log results: {e}")


def continuous_monitoring(interval: int = 300, log_file: str = "health_monitor.log"):
    """Run continuous health monitoring"""
    print(f"🔄 Starting continuous monitoring (interval: {interval}s)")
    print("Press Ctrl+C to stop")
    
    monitor = HealthMonitor()
    
    try:
        while True:
            print(f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            results = monitor.run_all_checks()
            all_healthy = monitor.display_results(results)
            
            # Send alerts for failures
            if not all_healthy:
                monitor.send_alert(results)
            
            # Log results
            monitor.log_results(results, log_file)
            
            print(f"💤 Sleeping for {interval} seconds...")
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")


def main():
    """Main function with command line argument parsing"""
    parser = argparse.ArgumentParser(description="RAG AI Agent Health Monitor")
    parser.add_argument("--continuous", action="store_true", help="Run continuous monitoring")
    parser.add_argument("--interval", type=int, default=300, help="Monitoring interval in seconds (default: 300)")
    parser.add_argument("--no-alerts", action="store_true", help="Disable email alerts")
    parser.add_argument("--log-file", default="health_monitor.log", help="Log file path")
    parser.add_argument("--config", help="JSON config file path")
    
    args = parser.parse_args()
    
    # Load custom config if provided
    config = None
    if args.config:
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
        except Exception as e:
            print(f"❌ Failed to load config file: {e}")
            sys.exit(1)
    
    monitor = HealthMonitor(config)
    
    if args.continuous:
        continuous_monitoring(args.interval, args.log_file)
    else:
        # Single run
        results = monitor.run_all_checks()
        all_healthy = monitor.display_results(results)
        
        # Send alerts unless disabled
        if not args.no_alerts and not all_healthy:
            monitor.send_alert(results)
        
        # Log results
        monitor.log_results(results, args.log_file)
        
        # Exit with error code if any checks failed
        if not all_healthy:
            sys.exit(1)


if __name__ == "__main__":
    main()