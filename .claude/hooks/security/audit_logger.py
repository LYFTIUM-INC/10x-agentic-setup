#!/usr/bin/env python3
"""
Audit Logger for Security Validation System
Comprehensive logging and audit trail for all security events
"""

import sqlite3
import json
import time
import logging
import os
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuditEventType(Enum):
    FILE_ACCESS = "file_access"
    COMMAND_EXECUTION = "command_execution"
    SECURITY_VIOLATION = "security_violation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    SYSTEM_CHANGE = "system_change"
    ALERT_TRIGGERED = "alert_triggered"

class AuditSeverity(Enum):
    INFO = "info"
    LOW = "low" 
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class AuditEvent:
    event_id: str
    timestamp: float
    event_type: AuditEventType
    severity: AuditSeverity
    user_id: str
    session_id: str
    action: str
    resource: str
    result: str
    details: Dict[str, Any]
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    risk_score: float = 0.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class SecurityAlert:
    def __init__(self, alert_id: str, severity: AuditSeverity, message: str, 
                 event_ids: List[str], triggered_at: float = None):
        self.alert_id = alert_id
        self.severity = severity
        self.message = message
        self.event_ids = event_ids
        self.triggered_at = triggered_at or time.time()
        self.acknowledged = False
        self.acknowledged_by = None
        self.acknowledged_at = None

class AuditLogger:
    """Comprehensive audit logging system"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(Path.home() / ".claude" / "security_audit.db")
        self.db_lock = threading.RLock()
        self.alert_handlers = []
        
        # Alert thresholds
        self.alert_rules = {
            'failed_attempts': {
                'threshold': 5,
                'window_minutes': 10,
                'severity': AuditSeverity.HIGH
            },
            'critical_violations': {
                'threshold': 1,
                'window_minutes': 1,
                'severity': AuditSeverity.CRITICAL
            },
            'suspicious_patterns': {
                'threshold': 3,
                'window_minutes': 5,
                'severity': AuditSeverity.MEDIUM
            }
        }
        
        # Initialize database
        self.init_database()
        
        logger.info(f"Audit logger initialized with database: {self.db_path}")
    
    def init_database(self):
        """Initialize the audit database with proper schemas"""
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            
            # Create audit events table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS audit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT UNIQUE NOT NULL,
                    timestamp REAL NOT NULL,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    resource TEXT NOT NULL,
                    result TEXT NOT NULL,
                    details TEXT NOT NULL,
                    source_ip TEXT,
                    user_agent TEXT,
                    risk_score REAL DEFAULT 0.0,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create alerts table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS security_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id TEXT UNIQUE NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    event_ids TEXT NOT NULL,
                    triggered_at REAL NOT NULL,
                    acknowledged BOOLEAN DEFAULT FALSE,
                    acknowledged_by TEXT,
                    acknowledged_at REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create audit summary table for quick lookups
            conn.execute('''
                CREATE TABLE IF NOT EXISTS audit_summary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date_key TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    event_count INTEGER DEFAULT 0,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(date_key, event_type, severity)
                )
            ''')
            
            # Create indexes for performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_events(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_event_type ON audit_events(event_type)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_severity ON audit_events(severity)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_user_session ON audit_events(user_id, session_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_resource ON audit_events(resource)')
            
            conn.commit()
            conn.close()
    
    def log_event(self, event: AuditEvent):
        """Log an audit event"""
        
        try:
            with self.db_lock:
                conn = sqlite3.connect(self.db_path)
                
                conn.execute('''
                    INSERT INTO audit_events 
                    (event_id, timestamp, event_type, severity, user_id, session_id,
                     action, resource, result, details, source_ip, user_agent, 
                     risk_score, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event.event_id,
                    event.timestamp,
                    event.event_type.value,
                    event.severity.value,
                    event.user_id,
                    event.session_id,
                    event.action,
                    event.resource,
                    event.result,
                    json.dumps(event.details),
                    event.source_ip,
                    event.user_agent,
                    event.risk_score,
                    json.dumps(event.metadata or {})
                ))
                
                conn.commit()
                conn.close()
                
                # Update summary statistics
                self.update_summary_stats(event)
                
                # Check for alert conditions
                self.check_alert_conditions(event)
                
                logger.debug(f"Audit event logged: {event.event_id}")
        
        except Exception as e:
            logger.error(f"Failed to log audit event {event.event_id}: {e}")
    
    def log_file_access(self, action: str, file_path: str, result: str, 
                       user_id: str, session_id: str, details: Dict[str, Any] = None):
        """Log file access event"""
        
        event = AuditEvent(
            event_id=self.generate_event_id(),
            timestamp=time.time(),
            event_type=AuditEventType.FILE_ACCESS,
            severity=self.calculate_file_access_severity(action, file_path, result),
            user_id=user_id,
            session_id=session_id,
            action=action,
            resource=file_path,
            result=result,
            details=details or {},
            metadata={
                'file_size': self.get_file_size(file_path),
                'file_type': self.get_file_type(file_path),
                'is_critical_path': self.is_critical_path(file_path)
            }
        )
        
        self.log_event(event)
    
    def log_command_execution(self, command: str, result: str, user_id: str, 
                            session_id: str, risk_score: float = 0.0, 
                            details: Dict[str, Any] = None):
        """Log command execution event"""
        
        event = AuditEvent(
            event_id=self.generate_event_id(),
            timestamp=time.time(),
            event_type=AuditEventType.COMMAND_EXECUTION,
            severity=self.calculate_command_severity(command, result, risk_score),
            user_id=user_id,
            session_id=session_id,
            action="execute_command",
            resource=command,
            result=result,
            details=details or {},
            risk_score=risk_score,
            metadata={
                'command_length': len(command),
                'has_sudo': 'sudo' in command.lower(),
                'has_pipes': '|' in command,
                'word_count': len(command.split())
            }
        )
        
        self.log_event(event)
    
    def log_security_violation(self, violation_type: str, resource: str, 
                             user_id: str, session_id: str, severity: AuditSeverity,
                             details: Dict[str, Any] = None):
        """Log security violation event"""
        
        event = AuditEvent(
            event_id=self.generate_event_id(),
            timestamp=time.time(),
            event_type=AuditEventType.SECURITY_VIOLATION,
            severity=severity,
            user_id=user_id,
            session_id=session_id,
            action=violation_type,
            resource=resource,
            result="blocked",
            details=details or {},
            risk_score=self.severity_to_risk_score(severity),
            metadata={
                'violation_category': self.categorize_violation(violation_type),
                'auto_blocked': True
            }
        )
        
        self.log_event(event)
    
    def log_system_change(self, change_type: str, resource: str, user_id: str,
                         session_id: str, result: str, details: Dict[str, Any] = None):
        """Log system change event"""
        
        event = AuditEvent(
            event_id=self.generate_event_id(),
            timestamp=time.time(),
            event_type=AuditEventType.SYSTEM_CHANGE,
            severity=self.calculate_change_severity(change_type, resource),
            user_id=user_id,
            session_id=session_id,
            action=change_type,
            resource=resource,
            result=result,
            details=details or {},
            metadata={
                'change_category': self.categorize_change(change_type),
                'reversible': self.is_reversible_change(change_type)
            }
        )
        
        self.log_event(event)
    
    def query_events(self, filters: Dict[str, Any] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Query audit events with filters"""
        
        query = "SELECT * FROM audit_events WHERE 1=1"
        params = []
        
        if filters:
            if 'start_time' in filters:
                query += " AND timestamp >= ?"
                params.append(filters['start_time'])
            
            if 'end_time' in filters:
                query += " AND timestamp <= ?"
                params.append(filters['end_time'])
            
            if 'event_type' in filters:
                query += " AND event_type = ?"
                params.append(filters['event_type'])
            
            if 'severity' in filters:
                query += " AND severity = ?"
                params.append(filters['severity'])
            
            if 'user_id' in filters:
                query += " AND user_id = ?"
                params.append(filters['user_id'])
            
            if 'session_id' in filters:
                query += " AND session_id = ?"
                params.append(filters['session_id'])
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            events = []
            for row in cursor.fetchall():
                event_dict = dict(row)
                event_dict['details'] = json.loads(event_dict['details'])
                event_dict['metadata'] = json.loads(event_dict['metadata'] or '{}')
                events.append(event_dict)
            
            conn.close()
            return events
    
    def get_security_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get security summary for the specified time period"""
        
        start_time = time.time() - (hours * 3600)
        
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get event counts by type and severity
            cursor.execute('''
                SELECT event_type, severity, COUNT(*) as count
                FROM audit_events 
                WHERE timestamp >= ?
                GROUP BY event_type, severity
            ''', (start_time,))
            
            event_counts = {}
            for row in cursor.fetchall():
                event_type, severity, count = row
                if event_type not in event_counts:
                    event_counts[event_type] = {}
                event_counts[event_type][severity] = count
            
            # Get top users by activity
            cursor.execute('''
                SELECT user_id, COUNT(*) as count
                FROM audit_events 
                WHERE timestamp >= ?
                GROUP BY user_id
                ORDER BY count DESC
                LIMIT 10
            ''', (start_time,))
            
            top_users = cursor.fetchall()
            
            # Get recent alerts
            cursor.execute('''
                SELECT * FROM security_alerts
                WHERE triggered_at >= ?
                ORDER BY triggered_at DESC
                LIMIT 10
            ''', (start_time,))
            
            recent_alerts = cursor.fetchall()
            
            # Get high-risk events
            cursor.execute('''
                SELECT event_id, timestamp, event_type, action, resource, risk_score
                FROM audit_events
                WHERE timestamp >= ? AND risk_score >= 0.7
                ORDER BY risk_score DESC, timestamp DESC
                LIMIT 20
            ''', (start_time,))
            
            high_risk_events = cursor.fetchall()
            
            conn.close()
            
            return {
                'time_period_hours': hours,
                'total_events': sum(sum(severities.values()) for severities in event_counts.values()),
                'event_counts': event_counts,
                'top_users': top_users,
                'recent_alerts': recent_alerts,
                'high_risk_events': high_risk_events,
                'summary_generated_at': time.time()
            }
    
    def check_alert_conditions(self, event: AuditEvent):
        """Check if event triggers any alert conditions"""
        
        # Critical violations trigger immediate alerts
        if event.severity == AuditSeverity.CRITICAL:
            self.trigger_alert(
                severity=AuditSeverity.CRITICAL,
                message=f"Critical security violation: {event.action}",
                event_ids=[event.event_id]
            )
        
        # Check for failed attempts pattern
        if event.result == "blocked" or event.result == "failed":
            failed_events = self.query_events({
                'start_time': time.time() - (self.alert_rules['failed_attempts']['window_minutes'] * 60),
                'user_id': event.user_id
            })
            
            failed_count = len([e for e in failed_events if e['result'] in ['blocked', 'failed']])
            
            if failed_count >= self.alert_rules['failed_attempts']['threshold']:
                self.trigger_alert(
                    severity=self.alert_rules['failed_attempts']['severity'],
                    message=f"Multiple failed attempts by user {event.user_id}",
                    event_ids=[e['event_id'] for e in failed_events[-5:]]  # Last 5 events
                )
        
        # Check for suspicious patterns
        if event.risk_score >= 0.8:
            high_risk_events = self.query_events({
                'start_time': time.time() - (self.alert_rules['suspicious_patterns']['window_minutes'] * 60),
                'user_id': event.user_id
            })
            
            suspicious_count = len([e for e in high_risk_events if e['risk_score'] >= 0.6])
            
            if suspicious_count >= self.alert_rules['suspicious_patterns']['threshold']:
                self.trigger_alert(
                    severity=self.alert_rules['suspicious_patterns']['severity'],
                    message=f"Suspicious activity pattern detected for user {event.user_id}",
                    event_ids=[e['event_id'] for e in high_risk_events[-3:]]
                )
    
    def trigger_alert(self, severity: AuditSeverity, message: str, event_ids: List[str]):
        """Trigger a security alert"""
        
        alert_id = self.generate_alert_id()
        alert = SecurityAlert(alert_id, severity, message, event_ids)
        
        # Store alert in database
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            conn.execute('''
                INSERT INTO security_alerts 
                (alert_id, severity, message, event_ids, triggered_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                alert.alert_id,
                alert.severity.value,
                alert.message,
                json.dumps(alert.event_ids),
                alert.triggered_at
            ))
            conn.commit()
            conn.close()
        
        # Notify alert handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")
        
        logger.warning(f"Security alert triggered: {alert.alert_id} - {message}")
    
    def add_alert_handler(self, handler):
        """Add an alert handler function"""
        self.alert_handlers.append(handler)
    
    def update_summary_stats(self, event: AuditEvent):
        """Update summary statistics"""
        
        date_key = datetime.fromtimestamp(event.timestamp).strftime('%Y-%m-%d')
        
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            conn.execute('''
                INSERT INTO audit_summary (date_key, event_type, severity, event_count)
                VALUES (?, ?, ?, 1)
                ON CONFLICT(date_key, event_type, severity) 
                DO UPDATE SET 
                    event_count = event_count + 1,
                    last_updated = CURRENT_TIMESTAMP
            ''', (date_key, event.event_type.value, event.severity.value))
            conn.commit()
            conn.close()
    
    def cleanup_old_events(self, retention_days: int = 90):
        """Clean up old audit events beyond retention period"""
        
        cutoff_time = time.time() - (retention_days * 24 * 3600)
        
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            
            # Delete old events
            cursor = conn.execute('DELETE FROM audit_events WHERE timestamp < ?', (cutoff_time,))
            deleted_count = cursor.rowcount
            
            # Delete old alerts
            cursor = conn.execute('DELETE FROM security_alerts WHERE triggered_at < ?', (cutoff_time,))
            deleted_alerts = cursor.rowcount
            
            # Clean up old summary entries
            cutoff_date = datetime.fromtimestamp(cutoff_time).strftime('%Y-%m-%d')
            cursor = conn.execute('DELETE FROM audit_summary WHERE date_key < ?', (cutoff_date,))
            deleted_summaries = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            logger.info(f"Cleanup completed: {deleted_count} events, {deleted_alerts} alerts, {deleted_summaries} summaries deleted")
    
    def generate_event_id(self) -> str:
        """Generate unique event ID"""
        return f"evt_{int(time.time())}_{hash(os.urandom(8)) & 0x7fffffff:08x}"
    
    def generate_alert_id(self) -> str:
        """Generate unique alert ID"""
        return f"alt_{int(time.time())}_{hash(os.urandom(8)) & 0x7fffffff:08x}"
    
    def calculate_file_access_severity(self, action: str, file_path: str, result: str) -> AuditSeverity:
        """Calculate severity for file access events"""
        
        if result == "blocked":
            return AuditSeverity.HIGH
        
        if self.is_critical_path(file_path):
            if action in ['write', 'delete', 'modify']:
                return AuditSeverity.HIGH
            else:
                return AuditSeverity.MEDIUM
        
        return AuditSeverity.LOW
    
    def calculate_command_severity(self, command: str, result: str, risk_score: float) -> AuditSeverity:
        """Calculate severity for command execution events"""
        
        if result == "blocked":
            return AuditSeverity.HIGH
        
        if risk_score >= 0.8:
            return AuditSeverity.HIGH
        elif risk_score >= 0.6:
            return AuditSeverity.MEDIUM
        elif risk_score >= 0.3:
            return AuditSeverity.LOW
        
        return AuditSeverity.INFO
    
    def calculate_change_severity(self, change_type: str, resource: str) -> AuditSeverity:
        """Calculate severity for system changes"""
        
        high_impact_changes = ['permission_change', 'configuration_change', 'user_change']
        medium_impact_changes = ['file_modification', 'setting_change']
        
        if change_type in high_impact_changes:
            return AuditSeverity.HIGH
        elif change_type in medium_impact_changes:
            return AuditSeverity.MEDIUM
        
        return AuditSeverity.LOW
    
    def is_critical_path(self, file_path: str) -> bool:
        """Check if file path is critical"""
        
        critical_indicators = [
            '.claude/hooks', '.claude/commands', 'mcp_servers', 
            'Knowledge/intelligence', 'Instructions', '.env', 
            'secrets', 'credentials', 'config'
        ]
        
        return any(indicator in file_path for indicator in critical_indicators)
    
    def get_file_size(self, file_path: str) -> int:
        """Get file size safely"""
        try:
            return os.path.getsize(file_path) if os.path.exists(file_path) else 0
        except:
            return 0
    
    def get_file_type(self, file_path: str) -> str:
        """Get file type/extension"""
        return Path(file_path).suffix.lower()
    
    def severity_to_risk_score(self, severity: AuditSeverity) -> float:
        """Convert severity to risk score"""
        
        mapping = {
            AuditSeverity.INFO: 0.1,
            AuditSeverity.LOW: 0.3,
            AuditSeverity.MEDIUM: 0.6,
            AuditSeverity.HIGH: 0.8,
            AuditSeverity.CRITICAL: 1.0
        }
        
        return mapping.get(severity, 0.5)
    
    def categorize_violation(self, violation_type: str) -> str:
        """Categorize security violation"""
        
        categories = {
            'path_traversal': 'access_control',
            'command_injection': 'injection',
            'privilege_escalation': 'authorization',
            'data_exfiltration': 'data_protection',
            'malicious_pattern': 'threat_detection'
        }
        
        return categories.get(violation_type, 'unknown')
    
    def categorize_change(self, change_type: str) -> str:
        """Categorize system change"""
        
        categories = {
            'file_creation': 'filesystem',
            'file_modification': 'filesystem', 
            'file_deletion': 'filesystem',
            'permission_change': 'security',
            'configuration_change': 'system',
            'user_change': 'identity'
        }
        
        return categories.get(change_type, 'unknown')
    
    def is_reversible_change(self, change_type: str) -> bool:
        """Check if change is reversible"""
        
        reversible_changes = [
            'file_modification', 'configuration_change', 
            'permission_change', 'setting_change'
        ]
        
        return change_type in reversible_changes

# Example usage and testing
def test_audit_logger():
    """Test the audit logger functionality"""
    
    import tempfile
    import uuid
    
    # Create temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
        db_path = temp_db.name
    
    try:
        logger_instance = AuditLogger(db_path)
        user_id = "test_user"
        session_id = str(uuid.uuid4())
        
        print("🧪 Testing Audit Logger...")
        
        # Test file access logging
        logger_instance.log_file_access(
            action="read",
            file_path="/sensitive/config.json",
            result="allowed",
            user_id=user_id,
            session_id=session_id,
            details={"file_size": 1024, "operation": "cat"}
        )
        
        # Test command execution logging
        logger_instance.log_command_execution(
            command="rm -rf /tmp/test",
            result="blocked",
            user_id=user_id,
            session_id=session_id,
            risk_score=0.9,
            details={"risk_factors": ["recursive_delete", "system_path"]}
        )
        
        # Test security violation logging
        logger_instance.log_security_violation(
            violation_type="path_traversal",
            resource="../../../etc/passwd",
            user_id=user_id,
            session_id=session_id,
            severity=AuditSeverity.HIGH,
            details={"attack_pattern": "directory_traversal"}
        )
        
        # Query events
        recent_events = logger_instance.query_events(limit=10)
        print(f"📊 Logged {len(recent_events)} events")
        
        for event in recent_events:
            print(f"  {event['event_type']}: {event['action']} -> {event['result']} (severity: {event['severity']})")
        
        # Get security summary
        summary = logger_instance.get_security_summary(hours=1)
        print(f"🔍 Security Summary:")
        print(f"  Total events: {summary['total_events']}")
        print(f"  Event types: {list(summary['event_counts'].keys())}")
        print(f"  High-risk events: {len(summary['high_risk_events'])}")
        
        print("✅ Audit logger test completed successfully")
        
    finally:
        # Cleanup
        os.unlink(db_path)

if __name__ == "__main__":
    test_audit_logger()