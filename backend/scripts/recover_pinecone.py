#!/usr/bin/env python3
"""
RAG AI Agent - Pinecone Recovery Script

This script helps recover from Pinecone index issues by recreating the index
from backup metadata. Note that vector data cannot be recovered and will need
to be re-uploaded by processing documents again.
"""

import os
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List

try:
    import pinecone
    from pinecone import Pinecone, ServerlessSpec
except ImportError:
    print("❌ Error: pinecone-client not installed")
    print("Install with: pip install pinecone-client")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  Warning: python-dotenv not installed, using system environment variables")


class PineconeRecovery:
    """Handles Pinecone vector database recovery operations"""
    
    def __init__(self):
        self.api_key = os.getenv("PINECONE_API_KEY")
        
        if not self.api_key:
            raise ValueError("PINECONE_API_KEY environment variable not set")
        
        # Initialize Pinecone
        try:
            self.pc = Pinecone(api_key=self.api_key)
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Pinecone: {e}")
    
    def list_available_backups(self) -> List[str]:
        """List all available Pinecone backup files"""
        backup_dir = "backups"
        
        if not os.path.exists(backup_dir):
            return []
        
        backup_files = [
            os.path.join(backup_dir, f) 
            for f in os.listdir(backup_dir) 
            if f.startswith("pinecone_backup_") and f.endswith(".json")
        ]
        
        return sorted(backup_files, reverse=True)  # Most recent first
    
    def load_backup(self, backup_file: str) -> Dict[str, Any]:
        """Load and validate a backup file"""
        try:
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)
            
            # Validate backup structure
            required_fields = ["backup_info", "index_config", "index_stats", "environment"]
            missing_fields = [field for field in required_fields if field not in backup_data]
            
            if missing_fields:
                raise ValueError(f"Invalid backup: Missing fields {missing_fields}")
            
            return backup_data
            
        except Exception as e:
            raise IOError(f"Failed to load backup: {e}")
    
    def display_backup_info(self, backup_data: Dict[str, Any]):
        """Display information about a backup"""
        print("📋 Backup Information:")
        print("=" * 50)
        
        # Backup metadata
        backup_info = backup_data.get("backup_info", {})
        print(f"Created: {backup_info.get('timestamp', 'Unknown')}")
        print(f"Version: {backup_info.get('backup_version', 'Unknown')}")
        
        # Index configuration
        index_config = backup_data.get("index_config", {})
        if index_config:
            print(f"Index Name: {index_config.get('name', 'Unknown')}")
            print(f"Dimension: {index_config.get('dimension', 'Unknown')}")
            print(f"Metric: {index_config.get('metric', 'Unknown')}")
            print(f"Host: {index_config.get('host', 'Unknown')}")
        
        # Statistics
        index_stats = backup_data.get("index_stats", {})
        if index_stats:
            total_vectors = index_stats.get("total_vector_count", 0)
            print(f"Total Vectors (at backup): {total_vectors:,}")
            
            namespaces = index_stats.get("namespaces", {})
            if namespaces:
                print(f"Namespaces: {len(namespaces)}")
                for ns_name, ns_stats in namespaces.items():
                    ns_count = ns_stats.get("vector_count", 0)
                    print(f"  - {ns_name}: {ns_count:,} vectors")
    
    def check_index_exists(self, index_name: str) -> bool:
        """Check if an index exists"""
        try:
            indexes = self.pc.list_indexes()
            return any(idx.name == index_name for idx in indexes)
        except Exception as e:
            print(f"❌ Error checking index existence: {e}")
            return False
    
    def delete_index(self, index_name: str) -> bool:
        """Delete an existing index"""
        try:
            self.pc.delete_index(index_name)
            print(f"✅ Deleted existing index: {index_name}")
            
            # Wait for deletion to complete
            import time
            print("⏳ Waiting for index deletion to complete...")
            while self.check_index_exists(index_name):
                time.sleep(2)
                print(".", end="", flush=True)
            print(" Done!")
            
            return True
        except Exception as e:
            print(f"❌ Error deleting index: {e}")
            return False
    
    def create_index_from_backup(self, backup_data: Dict[str, Any], force: bool = False) -> bool:
        """Create a new index from backup configuration"""
        index_config = backup_data.get("index_config", {})
        
        if not index_config:
            print("❌ Error: No index configuration found in backup")
            return False
        
        index_name = index_config.get("name")
        dimension = index_config.get("dimension")
        metric = index_config.get("metric", "cosine")
        
        if not index_name or not dimension:
            print("❌ Error: Missing required index configuration (name or dimension)")
            return False
        
        print(f"🔄 Creating index: {index_name}")
        print(f"   Dimension: {dimension}")
        print(f"   Metric: {metric}")
        
        # Check if index already exists
        if self.check_index_exists(index_name):
            if not force:
                print(f"❌ Error: Index '{index_name}' already exists")
                print("Use --force to delete and recreate the index")
                return False
            else:
                print(f"⚠️  Index '{index_name}' exists, deleting...")
                if not self.delete_index(index_name):
                    return False
        
        try:
            # Create the index with serverless spec (free tier)
            self.pc.create_index(
                name=index_name,
                dimension=int(dimension),
                metric=metric,
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'
                )
            )
            
            print(f"✅ Created index: {index_name}")
            
            # Wait for index to be ready
            import time
            print("⏳ Waiting for index to be ready...")
            max_wait = 60  # Maximum wait time in seconds
            wait_time = 0
            
            while wait_time < max_wait:
                try:
                    index = self.pc.Index(index_name)
                    stats = index.describe_index_stats()
                    print(" Ready!")
                    break
                except:
                    time.sleep(2)
                    wait_time += 2
                    print(".", end="", flush=True)
            else:
                print(" Timeout!")
                print("⚠️  Index creation may still be in progress")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating index: {e}")
            return False
    
    def recover_from_backup(self, backup_file: str, force: bool = False) -> bool:
        """Complete recovery process from a backup file"""
        print(f"🔄 Starting recovery from backup: {backup_file}")
        
        # Load backup
        try:
            backup_data = self.load_backup(backup_file)
        except Exception as e:
            print(f"❌ Failed to load backup: {e}")
            return False
        
        # Display backup information
        self.display_backup_info(backup_data)
        
        # Confirm recovery
        if not force:
            print("\n⚠️  Important Notes:")
            print("- This will recreate the index structure only")
            print("- Vector data cannot be recovered from backup")
            print("- You will need to re-upload and process all documents")
            print("- Existing index will be deleted if it exists")
            
            response = input("\nDo you want to proceed with recovery? (y/N): ")
            if response.lower() != 'y':
                print("❌ Recovery cancelled")
                return False
        
        # Create index from backup
        success = self.create_index_from_backup(backup_data, force=True)
        
        if success:
            print("\n✅ Recovery completed successfully!")
            print("\n📋 Next Steps:")
            print("1. Update your environment variables if needed:")
            print(f"   PINECONE_INDEX_NAME={backup_data['index_config']['name']}")
            print("2. Re-upload and process your documents to restore vector data")
            print("3. Test the application to ensure everything works")
            
            # Update environment variable suggestion
            current_index = os.getenv("PINECONE_INDEX_NAME")
            backup_index = backup_data['index_config']['name']
            
            if current_index != backup_index:
                print(f"\n⚠️  Environment variable mismatch:")
                print(f"   Current PINECONE_INDEX_NAME: {current_index}")
                print(f"   Backup index name: {backup_index}")
                print("   Update your environment variables accordingly")
        
        return success


def interactive_recovery():
    """Interactive recovery process"""
    recovery = PineconeRecovery()
    
    # List available backups
    backups = recovery.list_available_backups()
    
    if not backups:
        print("❌ No Pinecone backups found")
        print("Create a backup first with: python backup_pinecone.py")
        return False
    
    print(f"📁 Found {len(backups)} backup(s):")
    print("=" * 60)
    
    for i, backup_file in enumerate(backups):
        try:
            backup_data = recovery.load_backup(backup_file)
            timestamp = backup_data["backup_info"]["timestamp"]
            index_name = backup_data["index_config"]["name"]
            total_vectors = backup_data["index_stats"].get("total_vector_count", 0)
            
            print(f"{i + 1}. {os.path.basename(backup_file)}")
            print(f"   Created: {timestamp}")
            print(f"   Index: {index_name}")
            print(f"   Vectors: {total_vectors:,}")
            print()
            
        except Exception as e:
            print(f"{i + 1}. {os.path.basename(backup_file)} (corrupted)")
            print()
    
    # Select backup
    while True:
        try:
            choice = input(f"Select backup to recover from (1-{len(backups)}, or 'q' to quit): ")
            
            if choice.lower() == 'q':
                print("❌ Recovery cancelled")
                return False
            
            backup_index = int(choice) - 1
            if 0 <= backup_index < len(backups):
                selected_backup = backups[backup_index]
                break
            else:
                print("❌ Invalid selection")
                
        except ValueError:
            print("❌ Invalid input")
    
    # Perform recovery
    return recovery.recover_from_backup(selected_backup)


def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "list":
            recovery = PineconeRecovery()
            backups = recovery.list_available_backups()
            
            if not backups:
                print("📁 No Pinecone backups found")
            else:
                print(f"📁 Found {len(backups)} backup(s):")
                for backup in backups:
                    print(f"  - {backup}")
            return
            
        elif command == "recover" and len(sys.argv) > 2:
            backup_file = sys.argv[2]
            force = "--force" in sys.argv
            
            if not os.path.exists(backup_file):
                print(f"❌ Error: Backup file '{backup_file}' not found")
                return
            
            recovery = PineconeRecovery()
            success = recovery.recover_from_backup(backup_file, force=force)
            
            if not success:
                sys.exit(1)
            return
            
        elif command == "help":
            print("Pinecone Recovery Script")
            print("Usage:")
            print("  python recover_pinecone.py                    - Interactive recovery")
            print("  python recover_pinecone.py list               - List available backups")
            print("  python recover_pinecone.py recover <file>     - Recover from specific backup")
            print("  python recover_pinecone.py recover <file> --force - Force recovery (skip confirmations)")
            print("  python recover_pinecone.py help               - Show this help")
            return
    
    # Default action: interactive recovery
    try:
        success = interactive_recovery()
        if not success:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n❌ Recovery cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Recovery failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()