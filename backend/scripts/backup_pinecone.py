#!/usr/bin/env python3
"""
RAG AI Agent - Pinecone Vector Database Backup Script

This script creates backups of Pinecone index metadata and statistics.
Note: Pinecone doesn't support full vector data export, so this backup
contains index configuration and statistics for recovery purposes.
"""

import os
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional

try:
    import pinecone
    from pinecone import Pinecone
except ImportError:
    print("❌ Error: pinecone-client not installed")
    print("Install with: pip install pinecone-client")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  Warning: python-dotenv not installed, using system environment variables")


class PineconeBackup:
    """Handles Pinecone vector database backup operations"""
    
    def __init__(self):
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.index_name = os.getenv("PINECONE_INDEX_NAME")
        
        if not self.api_key:
            raise ValueError("PINECONE_API_KEY environment variable not set")
        
        if not self.index_name:
            raise ValueError("PINECONE_INDEX_NAME environment variable not set")
        
        # Initialize Pinecone
        try:
            self.pc = Pinecone(api_key=self.api_key)
            self.index = self.pc.Index(self.index_name)
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Pinecone: {e}")
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get comprehensive index statistics"""
        try:
            stats = self.index.describe_index_stats()
            return stats
        except Exception as e:
            print(f"❌ Error getting index stats: {e}")
            return {}
    
    def get_index_info(self) -> Dict[str, Any]:
        """Get index configuration information"""
        try:
            # Get index description
            indexes = self.pc.list_indexes()
            index_info = None
            
            for idx in indexes:
                if idx.name == self.index_name:
                    index_info = {
                        "name": idx.name,
                        "dimension": idx.dimension,
                        "metric": idx.metric,
                        "host": idx.host,
                        "status": idx.status
                    }
                    break
            
            return index_info or {}
        except Exception as e:
            print(f"❌ Error getting index info: {e}")
            return {}
    
    def test_connectivity(self) -> bool:
        """Test connection to Pinecone index"""
        try:
            # Try a simple operation
            stats = self.index.describe_index_stats()
            return True
        except Exception as e:
            print(f"❌ Connectivity test failed: {e}")
            return False
    
    def create_backup(self) -> str:
        """Create a comprehensive backup of Pinecone index metadata"""
        print("🔄 Starting Pinecone backup...")
        
        # Test connectivity first
        if not self.test_connectivity():
            raise ConnectionError("Cannot connect to Pinecone index")
        
        print("✅ Connected to Pinecone successfully")
        
        # Gather backup data
        backup_data = {
            "backup_info": {
                "timestamp": datetime.now().isoformat(),
                "backup_version": "1.0",
                "script_version": "1.0"
            },
            "index_config": self.get_index_info(),
            "index_stats": self.get_index_stats(),
            "environment": {
                "index_name": self.index_name,
                "api_key_prefix": self.api_key[:8] + "..." if self.api_key else None
            }
        }
        
        # Create backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"pinecone_backup_{timestamp}.json"
        backup_path = os.path.join("backups", backup_filename)
        
        # Ensure backup directory exists
        os.makedirs("backups", exist_ok=True)
        
        # Save backup
        try:
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            print(f"✅ Backup saved to: {backup_path}")
            
            # Display backup summary
            self._display_backup_summary(backup_data, backup_path)
            
            return backup_path
            
        except Exception as e:
            raise IOError(f"Failed to save backup: {e}")
    
    def _display_backup_summary(self, backup_data: Dict[str, Any], backup_path: str):
        """Display a summary of the backup"""
        print("\n📊 Backup Summary:")
        print("=" * 50)
        
        # Index information
        index_config = backup_data.get("index_config", {})
        if index_config:
            print(f"Index Name: {index_config.get('name', 'Unknown')}")
            print(f"Dimension: {index_config.get('dimension', 'Unknown')}")
            print(f"Metric: {index_config.get('metric', 'Unknown')}")
            print(f"Status: {index_config.get('status', 'Unknown')}")
        
        # Statistics
        index_stats = backup_data.get("index_stats", {})
        if index_stats:
            total_vectors = index_stats.get("total_vector_count", 0)
            print(f"Total Vectors: {total_vectors:,}")
            
            namespaces = index_stats.get("namespaces", {})
            if namespaces:
                print(f"Namespaces: {len(namespaces)}")
                for ns_name, ns_stats in namespaces.items():
                    ns_count = ns_stats.get("vector_count", 0)
                    print(f"  - {ns_name}: {ns_count:,} vectors")
        
        # File information
        file_size = os.path.getsize(backup_path)
        print(f"Backup Size: {file_size:,} bytes")
        print(f"Backup File: {backup_path}")
        
        print("\n⚠️  Important Notes:")
        print("- This backup contains metadata and statistics only")
        print("- Vector data cannot be exported from Pinecone")
        print("- To restore, you'll need to recreate the index and re-upload documents")
        print("- Keep your document sources for full recovery")


def verify_backup(backup_file: str) -> bool:
    """Verify a backup file is valid and complete"""
    try:
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
        
        # Check required fields
        required_fields = ["backup_info", "index_config", "index_stats", "environment"]
        missing_fields = [field for field in required_fields if field not in backup_data]
        
        if missing_fields:
            print(f"❌ Backup verification failed: Missing fields {missing_fields}")
            return False
        
        # Check backup timestamp
        backup_time = backup_data["backup_info"].get("timestamp")
        if not backup_time:
            print("❌ Backup verification failed: No timestamp found")
            return False
        
        print(f"✅ Backup verification passed: {backup_file}")
        print(f"   Created: {backup_time}")
        return True
        
    except Exception as e:
        print(f"❌ Backup verification failed: {e}")
        return False


def list_backups() -> None:
    """List all available Pinecone backups"""
    backup_dir = "backups"
    
    if not os.path.exists(backup_dir):
        print("📁 No backup directory found")
        return
    
    backup_files = [f for f in os.listdir(backup_dir) if f.startswith("pinecone_backup_") and f.endswith(".json")]
    
    if not backup_files:
        print("📁 No Pinecone backups found")
        return
    
    print(f"📁 Found {len(backup_files)} Pinecone backup(s):")
    print("=" * 60)
    
    for backup_file in sorted(backup_files, reverse=True):
        backup_path = os.path.join(backup_dir, backup_file)
        
        try:
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)
            
            timestamp = backup_data["backup_info"]["timestamp"]
            index_name = backup_data["environment"]["index_name"]
            total_vectors = backup_data["index_stats"].get("total_vector_count", 0)
            file_size = os.path.getsize(backup_path)
            
            print(f"📄 {backup_file}")
            print(f"   Created: {timestamp}")
            print(f"   Index: {index_name}")
            print(f"   Vectors: {total_vectors:,}")
            print(f"   Size: {file_size:,} bytes")
            print()
            
        except Exception as e:
            print(f"📄 {backup_file} (corrupted: {e})")


def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "list":
            list_backups()
            return
        elif command == "verify" and len(sys.argv) > 2:
            backup_file = sys.argv[2]
            verify_backup(backup_file)
            return
        elif command == "help":
            print("Pinecone Backup Script")
            print("Usage:")
            print("  python backup_pinecone.py          - Create new backup")
            print("  python backup_pinecone.py list     - List all backups")
            print("  python backup_pinecone.py verify <file> - Verify backup file")
            print("  python backup_pinecone.py help     - Show this help")
            return
    
    # Default action: create backup
    try:
        backup = PineconeBackup()
        backup_path = backup.create_backup()
        
        print(f"\n🎉 Backup completed successfully!")
        print(f"📁 Backup saved to: {backup_path}")
        
        # Verify the backup we just created
        print("\n🔍 Verifying backup...")
        if verify_backup(backup_path):
            print("✅ Backup verification passed")
        else:
            print("❌ Backup verification failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()