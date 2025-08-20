#!/usr/bin/env python3
"""
Backup Manager for Security Validation System
Automated backup and recovery system for critical files
"""

import os
import shutil
import time
import logging
import hashlib
import json
import gzip
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import threading
from enum import Enum
import fnmatch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackupType(Enum):
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    PRE_MODIFICATION = "pre_modification"
    SCHEDULED = "scheduled"
    EMERGENCY = "emergency"

class BackupStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RESTORED = "restored"

@dataclass
class BackupMetadata:
    backup_id: str
    original_path: str
    backup_path: str
    backup_type: BackupType
    status: BackupStatus
    created_at: float
    file_size: int
    file_hash: str
    compression_ratio: float = 1.0
    retention_days: int = 30
    metadata: Dict[str, Any] = None
    tags: Set[str] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.tags is None:
            self.tags = set()

@dataclass
class RestoreOperation:
    restore_id: str
    backup_id: str
    original_path: str
    restore_path: str
    initiated_by: str
    initiated_at: float
    completed_at: Optional[float] = None
    status: BackupStatus = BackupStatus.PENDING
    verification_hash: Optional[str] = None
    notes: str = ""

class BackupManager:
    """Comprehensive backup and recovery manager"""
    
    def __init__(self, backup_root: str = None):
        self.backup_root = Path(backup_root or Path.home() / ".claude" / "backups")
        self.db_path = self.backup_root / "backup_metadata.db"
        self.db_lock = threading.RLock()
        
        # Configuration
        self.compression_enabled = True
        self.max_backup_size = 100 * 1024 * 1024  # 100MB
        self.default_retention_days = 30
        self.max_backups_per_file = 10
        
        # Critical patterns that always get backed up
        self.critical_patterns = [
            "mcp_servers/*/src/server.py",
            ".claude/hooks/**/*",
            ".claude/commands/**/*",
            ".claude/**/config*.json",
            "Knowledge/intelligence/**/*",
            "Instructions/**/*"
        ]
        
        # Patterns to exclude from backup
        self.exclude_patterns = [
            "**/__pycache__/**",
            "**/node_modules/**",
            "**/.git/**",
            "**/venv/**",
            "**/.venv/**",
            "**/*.tmp",
            "**/*.log",
            "**/backup_*"
        ]
        
        # File type compression settings
        self.compression_by_type = {
            '.txt': True, '.md': True, '.json': True, '.yaml': True, '.yml': True,
            '.py': True, '.js': True, '.ts': True, '.html': True, '.css': True,
            '.xml': True, '.sql': True, '.sh': True, '.bash': True,
            '.jpg': False, '.png': False, '.gif': False, '.zip': False,
            '.gz': False, '.tar': False, '.pdf': False, '.mp4': False
        }
        
        # Initialize backup system
        self.setup_backup_system()
        
        logger.info(f"Backup manager initialized with root: {self.backup_root}")
    
    def setup_backup_system(self):
        """Initialize the backup system"""
        
        # Create backup directory structure
        self.backup_root.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.backup_root / "automatic").mkdir(exist_ok=True)
        (self.backup_root / "manual").mkdir(exist_ok=True) 
        (self.backup_root / "emergency").mkdir(exist_ok=True)
        (self.backup_root / "archives").mkdir(exist_ok=True)
        
        # Initialize database
        self.init_database()
    
    def init_database(self):
        """Initialize backup metadata database"""
        
        with self.db_lock:
            conn = sqlite3.connect(str(self.db_path))
            
            # Create backup metadata table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS backup_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    backup_id TEXT UNIQUE NOT NULL,
                    original_path TEXT NOT NULL,
                    backup_path TEXT NOT NULL,
                    backup_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    file_size INTEGER NOT NULL,
                    file_hash TEXT NOT NULL,
                    compression_ratio REAL DEFAULT 1.0,
                    retention_days INTEGER DEFAULT 30,
                    metadata TEXT,
                    tags TEXT,
                    created_date DATE DEFAULT CURRENT_DATE
                )
            ''')
            
            # Create restore operations table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS restore_operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    restore_id TEXT UNIQUE NOT NULL,
                    backup_id TEXT NOT NULL,
                    original_path TEXT NOT NULL,
                    restore_path TEXT NOT NULL,
                    initiated_by TEXT NOT NULL,
                    initiated_at REAL NOT NULL,
                    completed_at REAL,
                    status TEXT NOT NULL,
                    verification_hash TEXT,
                    notes TEXT,
                    FOREIGN KEY (backup_id) REFERENCES backup_metadata (backup_id)
                )
            ''')
            
            # Create indexes
            conn.execute('CREATE INDEX IF NOT EXISTS idx_original_path ON backup_metadata(original_path)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON backup_metadata(created_at)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_backup_type ON backup_metadata(backup_type)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_status ON backup_metadata(status)')
            
            conn.commit()
            conn.close()
    
    def create_backup(self, file_path: str, backup_type: BackupType = BackupType.MANUAL,
                     tags: Set[str] = None, retention_days: int = None) -> Optional[str]:
        """Create a backup of the specified file"""
        
        try:
            file_path = Path(file_path).resolve()
            
            # Validate file
            if not file_path.exists():
                logger.error(f"File not found for backup: {file_path}")
                return None
            
            if not file_path.is_file():
                logger.error(f"Path is not a file: {file_path}")
                return None
            
            # Check if file should be excluded
            if self.should_exclude_file(str(file_path)):
                logger.debug(f"File excluded from backup: {file_path}")
                return None
            
            # Check file size
            file_size = file_path.stat().st_size
            if file_size > self.max_backup_size:
                logger.warning(f"File too large for backup: {file_path} ({file_size} bytes)")
                return None
            
            # Generate backup ID and paths
            backup_id = self.generate_backup_id()
            backup_dir = self.backup_root / backup_type.value / datetime.now().strftime("%Y/%m/%d")
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Create backup filename
            original_name = file_path.name
            timestamp = datetime.now().strftime("%H%M%S")
            backup_filename = f"{backup_id}_{timestamp}_{original_name}"
            
            # Add compression extension if needed
            should_compress = self.should_compress_file(str(file_path))
            if should_compress:
                backup_filename += ".gz"
            
            backup_path = backup_dir / backup_filename
            
            # Calculate file hash before backup
            file_hash = self.calculate_file_hash(file_path)
            
            # Perform backup
            compression_ratio = 1.0
            if should_compress:
                compression_ratio = self.backup_with_compression(file_path, backup_path)
            else:
                shutil.copy2(file_path, backup_path)
            
            # Create backup metadata
            metadata = BackupMetadata(
                backup_id=backup_id,
                original_path=str(file_path),
                backup_path=str(backup_path),
                backup_type=backup_type,
                status=BackupStatus.COMPLETED,
                created_at=time.time(),
                file_size=file_size,
                file_hash=file_hash,
                compression_ratio=compression_ratio,
                retention_days=retention_days or self.default_retention_days,
                metadata={
                    'original_modified_time': file_path.stat().st_mtime,
                    'original_permissions': oct(file_path.stat().st_mode)[-3:],
                    'backup_size': backup_path.stat().st_size,
                    'compressed': should_compress
                },
                tags=tags or set()
            )
            
            # Store metadata in database
            self.store_backup_metadata(metadata)
            
            # Clean up old backups for this file
            self.cleanup_old_backups(str(file_path))
            
            logger.info(f"Backup created successfully: {backup_id} for {file_path}")
            return backup_id
            
        except Exception as e:
            logger.error(f"Failed to create backup for {file_path}: {e}")
            return None
    
    def backup_with_compression(self, source_path: Path, backup_path: Path) -> float:
        """Backup file with gzip compression"""
        
        original_size = source_path.stat().st_size
        
        with open(source_path, 'rb') as f_in:
            with gzip.open(backup_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        compressed_size = backup_path.stat().st_size
        compression_ratio = compressed_size / original_size if original_size > 0 else 1.0
        
        return compression_ratio
    
    def restore_backup(self, backup_id: str, restore_path: str = None, 
                      initiated_by: str = "system") -> Optional[str]:
        """Restore a backup to the specified location"""
        
        try:
            # Get backup metadata
            backup_metadata = self.get_backup_metadata(backup_id)
            if not backup_metadata:
                logger.error(f"Backup not found: {backup_id}")
                return None
            
            # Determine restore path
            if restore_path is None:
                restore_path = backup_metadata.original_path
            
            restore_path = Path(restore_path)
            
            # Create restore operation record
            restore_id = self.generate_restore_id()
            restore_op = RestoreOperation(
                restore_id=restore_id,
                backup_id=backup_id,
                original_path=backup_metadata.original_path,
                restore_path=str(restore_path),
                initiated_by=initiated_by,
                initiated_at=time.time(),
                status=BackupStatus.IN_PROGRESS
            )
            
            self.store_restore_operation(restore_op)
            
            # Ensure restore directory exists
            restore_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Perform restore
            backup_path = Path(backup_metadata.backup_path)
            
            if not backup_path.exists():
                logger.error(f"Backup file not found: {backup_path}")
                restore_op.status = BackupStatus.FAILED
                restore_op.notes = "Backup file not found"
                self.update_restore_operation(restore_op)
                return None
            
            # Check if backup is compressed
            is_compressed = backup_metadata.metadata.get('compressed', False)
            
            if is_compressed:
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(restore_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                shutil.copy2(backup_path, restore_path)
            
            # Restore file permissions if available
            if 'original_permissions' in backup_metadata.metadata:
                permissions = backup_metadata.metadata['original_permissions']
                try:
                    os.chmod(restore_path, int(permissions, 8))
                except:
                    pass  # Permissions restoration is best effort
            
            # Verify restoration
            restored_hash = self.calculate_file_hash(restore_path)
            
            if restored_hash == backup_metadata.file_hash:
                restore_op.status = BackupStatus.COMPLETED
                restore_op.verification_hash = restored_hash
                restore_op.notes = "Restoration successful and verified"
            else:
                restore_op.status = BackupStatus.FAILED
                restore_op.notes = f"Hash verification failed: expected {backup_metadata.file_hash}, got {restored_hash}"
                logger.error(f"Restore verification failed for {backup_id}")
            
            restore_op.completed_at = time.time()
            self.update_restore_operation(restore_op)
            
            logger.info(f"Restore operation completed: {restore_id} -> {restore_path}")
            return restore_id
            
        except Exception as e:
            logger.error(f"Failed to restore backup {backup_id}: {e}")
            if 'restore_op' in locals():
                restore_op.status = BackupStatus.FAILED
                restore_op.notes = f"Restore error: {str(e)}"
                restore_op.completed_at = time.time()
                self.update_restore_operation(restore_op)
            return None
    
    def create_pre_modification_backup(self, file_path: str) -> Optional[str]:
        """Create automatic backup before file modification"""
        
        return self.create_backup(
            file_path,
            backup_type=BackupType.PRE_MODIFICATION,
            tags={"pre_modification", "automatic"},
            retention_days=7  # Shorter retention for pre-modification backups
        )
    
    def backup_critical_files(self) -> Dict[str, str]:
        """Backup all critical files matching patterns"""
        
        backup_results = {}
        
        # Find critical files
        critical_files = self.find_files_by_patterns(self.critical_patterns)
        
        logger.info(f"Starting backup of {len(critical_files)} critical files")
        
        for file_path in critical_files:
            backup_id = self.create_backup(
                file_path,
                backup_type=BackupType.AUTOMATIC,
                tags={"critical", "automatic", "scheduled"}
            )
            
            if backup_id:
                backup_results[file_path] = backup_id
            else:
                backup_results[file_path] = "FAILED"
        
        logger.info(f"Critical files backup completed: {len(backup_results)} files processed")
        return backup_results
    
    def find_files_by_patterns(self, patterns: List[str], base_path: str = ".") -> List[str]:
        """Find files matching the given patterns"""
        
        base_path = Path(base_path).resolve()
        matching_files = []
        
        for pattern in patterns:
            # Convert pattern to Path for proper handling
            pattern_path = base_path / pattern
            
            # Handle glob patterns
            if '*' in pattern:
                try:
                    matches = base_path.glob(pattern)
                    for match in matches:
                        if match.is_file() and not self.should_exclude_file(str(match)):
                            matching_files.append(str(match))
                except Exception as e:
                    logger.debug(f"Pattern matching failed for {pattern}: {e}")
            else:
                # Exact file path
                if pattern_path.exists() and pattern_path.is_file():
                    if not self.should_exclude_file(str(pattern_path)):
                        matching_files.append(str(pattern_path))
        
        return list(set(matching_files))  # Remove duplicates
    
    def should_exclude_file(self, file_path: str) -> bool:
        """Check if file should be excluded from backup"""
        
        for pattern in self.exclude_patterns:
            if fnmatch.fnmatch(file_path, pattern):
                return True
        
        return False
    
    def should_compress_file(self, file_path: str) -> bool:
        """Determine if file should be compressed"""
        
        if not self.compression_enabled:
            return False
        
        file_ext = Path(file_path).suffix.lower()
        return self.compression_by_type.get(file_ext, True)  # Default to compression
    
    def get_backup_metadata(self, backup_id: str) -> Optional[BackupMetadata]:
        """Get backup metadata by ID"""
        
        with self.db_lock:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM backup_metadata WHERE backup_id = ?
            ''', (backup_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return self.row_to_backup_metadata(row)
            
            return None
    
    def list_backups(self, file_path: str = None, backup_type: BackupType = None,
                    limit: int = 50) -> List[BackupMetadata]:
        """List backups with optional filters"""
        
        query = "SELECT * FROM backup_metadata WHERE 1=1"
        params = []
        
        if file_path:
            query += " AND original_path = ?"
            params.append(file_path)
        
        if backup_type:
            query += " AND backup_type = ?"
            params.append(backup_type.value)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        with self.db_lock:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            backups = []
            for row in cursor.fetchall():
                backups.append(self.row_to_backup_metadata(row))
            
            conn.close()
            return backups
    
    def cleanup_old_backups(self, file_path: str = None):
        """Clean up old backups based on retention policies"""
        
        current_time = time.time()
        
        with self.db_lock:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Get expired backups
            cursor.execute('''
                SELECT backup_id, backup_path, created_at, retention_days
                FROM backup_metadata
                WHERE status = 'completed'
                AND (? - created_at) > (retention_days * 24 * 3600)
            ''' + (" AND original_path = ?" if file_path else ""), 
            [current_time] + ([file_path] if file_path else []))
            
            expired_backups = cursor.fetchall()
            
            # Also clean up excess backups for each file (keep only max_backups_per_file)
            if file_path:
                cursor.execute('''
                    SELECT backup_id, backup_path FROM backup_metadata
                    WHERE original_path = ? AND status = 'completed'
                    ORDER BY created_at DESC
                    LIMIT -1 OFFSET ?
                ''', (file_path, self.max_backups_per_file))
                
                excess_backups = cursor.fetchall()
                expired_backups.extend(excess_backups)
            
            # Delete expired backup files and metadata
            deleted_count = 0
            for backup_id, backup_path, *_ in expired_backups:
                try:
                    # Delete backup file
                    Path(backup_path).unlink(missing_ok=True)
                    
                    # Delete metadata
                    cursor.execute('DELETE FROM backup_metadata WHERE backup_id = ?', (backup_id,))
                    deleted_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to delete backup {backup_id}: {e}")
            
            conn.commit()
            conn.close()
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old backups")
    
    def get_backup_statistics(self) -> Dict[str, Any]:
        """Get backup system statistics"""
        
        with self.db_lock:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Total backups by type and status
            cursor.execute('''
                SELECT backup_type, status, COUNT(*) as count
                FROM backup_metadata
                GROUP BY backup_type, status
            ''')
            
            backup_counts = {}
            for backup_type, status, count in cursor.fetchall():
                if backup_type not in backup_counts:
                    backup_counts[backup_type] = {}
                backup_counts[backup_type][status] = count
            
            # Storage statistics
            cursor.execute('''
                SELECT 
                    SUM(file_size) as total_original_size,
                    SUM(file_size * compression_ratio) as total_backup_size,
                    AVG(compression_ratio) as avg_compression_ratio,
                    COUNT(*) as total_backups
                FROM backup_metadata
                WHERE status = 'completed'
            ''')
            
            storage_stats = cursor.fetchone()
            
            # Recent activity
            cursor.execute('''
                SELECT COUNT(*) FROM backup_metadata
                WHERE created_at > ?
            ''', (time.time() - 24 * 3600,))  # Last 24 hours
            
            recent_backups = cursor.fetchone()[0]
            
            # Recent restores
            cursor.execute('''
                SELECT COUNT(*) FROM restore_operations
                WHERE initiated_at > ?
            ''', (time.time() - 24 * 3600,))
            
            recent_restores = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'backup_counts': backup_counts,
                'storage_stats': {
                    'total_original_size': storage_stats[0] or 0,
                    'total_backup_size': storage_stats[1] or 0,
                    'average_compression_ratio': storage_stats[2] or 1.0,
                    'total_backups': storage_stats[3] or 0
                },
                'recent_activity': {
                    'backups_24h': recent_backups,
                    'restores_24h': recent_restores
                },
                'retention_policy': {
                    'default_retention_days': self.default_retention_days,
                    'max_backups_per_file': self.max_backups_per_file
                }
            }
    
    def store_backup_metadata(self, metadata: BackupMetadata):
        """Store backup metadata in database"""
        
        with self.db_lock:
            conn = sqlite3.connect(str(self.db_path))
            conn.execute('''
                INSERT INTO backup_metadata
                (backup_id, original_path, backup_path, backup_type, status,
                 created_at, file_size, file_hash, compression_ratio,
                 retention_days, metadata, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metadata.backup_id,
                metadata.original_path,
                metadata.backup_path,
                metadata.backup_type.value,
                metadata.status.value,
                metadata.created_at,
                metadata.file_size,
                metadata.file_hash,
                metadata.compression_ratio,
                metadata.retention_days,
                json.dumps(metadata.metadata),
                json.dumps(list(metadata.tags))
            ))
            conn.commit()
            conn.close()
    
    def store_restore_operation(self, restore_op: RestoreOperation):
        """Store restore operation in database"""
        
        with self.db_lock:
            conn = sqlite3.connect(str(self.db_path))
            conn.execute('''
                INSERT INTO restore_operations
                (restore_id, backup_id, original_path, restore_path,
                 initiated_by, initiated_at, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                restore_op.restore_id,
                restore_op.backup_id,
                restore_op.original_path,
                restore_op.restore_path,
                restore_op.initiated_by,
                restore_op.initiated_at,
                restore_op.status.value,
                restore_op.notes
            ))
            conn.commit()
            conn.close()
    
    def update_restore_operation(self, restore_op: RestoreOperation):
        """Update restore operation in database"""
        
        with self.db_lock:
            conn = sqlite3.connect(str(self.db_path))
            conn.execute('''
                UPDATE restore_operations
                SET completed_at = ?, status = ?, verification_hash = ?, notes = ?
                WHERE restore_id = ?
            ''', (
                restore_op.completed_at,
                restore_op.status.value,
                restore_op.verification_hash,
                restore_op.notes,
                restore_op.restore_id
            ))
            conn.commit()
            conn.close()
    
    def row_to_backup_metadata(self, row) -> BackupMetadata:
        """Convert database row to BackupMetadata object"""
        
        return BackupMetadata(
            backup_id=row[1],
            original_path=row[2],
            backup_path=row[3],
            backup_type=BackupType(row[4]),
            status=BackupStatus(row[5]),
            created_at=row[6],
            file_size=row[7],
            file_hash=row[8],
            compression_ratio=row[9],
            retention_days=row[10],
            metadata=json.loads(row[11] or '{}'),
            tags=set(json.loads(row[12] or '[]'))
        )
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    def generate_backup_id(self) -> str:
        """Generate unique backup ID"""
        return f"bkp_{int(time.time())}_{hash(os.urandom(8)) & 0x7fffffff:08x}"
    
    def generate_restore_id(self) -> str:
        """Generate unique restore ID"""
        return f"rst_{int(time.time())}_{hash(os.urandom(8)) & 0x7fffffff:08x}"

# Example usage and testing
def test_backup_manager():
    """Test the backup manager functionality"""
    
    import tempfile
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        backup_root = Path(temp_dir) / "backups"
        manager = BackupManager(str(backup_root))
        
        print("🧪 Testing Backup Manager...")
        
        # Create a test file
        test_file = Path(temp_dir) / "test_file.txt"
        test_content = "This is a test file for backup testing.\nSecond line of content."
        test_file.write_text(test_content)
        
        # Test backup creation
        backup_id = manager.create_backup(str(test_file), BackupType.MANUAL, {"test"})
        print(f"✅ Backup created: {backup_id}")
        
        # Test backup listing
        backups = manager.list_backups(str(test_file))
        print(f"📋 Found {len(backups)} backups for file")
        
        # Test file modification and pre-modification backup
        test_file.write_text(test_content + "\nModified content.")
        pre_mod_backup = manager.create_pre_modification_backup(str(test_file))
        print(f"✅ Pre-modification backup: {pre_mod_backup}")
        
        # Test restore
        restore_file = Path(temp_dir) / "restored_file.txt"
        restore_id = manager.restore_backup(backup_id, str(restore_file))
        print(f"✅ Restore completed: {restore_id}")
        
        # Verify restore
        if restore_file.exists() and restore_file.read_text() == test_content:
            print("✅ Restore verification successful")
        else:
            print("❌ Restore verification failed")
        
        # Test statistics
        stats = manager.get_backup_statistics()
        print(f"📊 Backup Statistics:")
        print(f"  Total backups: {stats['storage_stats']['total_backups']}")
        print(f"  Backup counts: {stats['backup_counts']}")
        
        # Test cleanup
        manager.cleanup_old_backups()
        print("✅ Cleanup completed")
        
        print("🎉 Backup manager test completed successfully")

if __name__ == "__main__":
    test_backup_manager()