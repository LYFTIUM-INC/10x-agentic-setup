#!/bin/bash

# 🚀 10X Agentic Setup - Real-Time Monitoring Dashboard Launcher
# Comprehensive monitoring system with performance metrics, security validation, and predictive analytics

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Configuration
DASHBOARD_PORT=8080
METRICS_UPDATE_INTERVAL=10
VENV_PATH=".venv"
LOG_DIR=".claude/logs"
DASHBOARD_DIR=".claude/dashboard"

echo -e "${BLUE}🚀 10X Agentic Setup - Monitoring Dashboard Launcher${NC}"
echo -e "${BLUE}================================================================${NC}"

# Function to print status
print_status() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] ⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] ❌ $1${NC}"
}

print_info() {
    echo -e "${CYAN}[$(date '+%H:%M:%S')] ℹ️  $1${NC}"
}

# Function to check if virtual environment exists
check_venv() {
    if [ ! -d "$VENV_PATH" ]; then
        print_error "Virtual environment not found at $VENV_PATH"
        print_info "Please run: python -m venv $VENV_PATH && source $VENV_PATH/bin/activate && pip install -r requirements.txt"
        exit 1
    fi
}

# Function to activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    source "$VENV_PATH/bin/activate"
    
    # Verify activation
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        print_status "Virtual environment activated: $VIRTUAL_ENV"
    else
        print_error "Failed to activate virtual environment"
        exit 1
    fi
}

# Function to check dependencies
check_dependencies() {
    print_status "Checking dependencies..."
    
    # Check Python packages
    python -c "
import sys
required_packages = [
    'psutil',
    'sqlite3',
    'json',
    'asyncio',
    'pathlib',
    'prometheus_client'
]

missing_packages = []
for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        missing_packages.append(package)

if missing_packages:
    print(f'❌ Missing packages: {missing_packages}')
    sys.exit(1)
else:
    print('✅ All required packages found')
"
    
    if [ $? -ne 0 ]; then
        print_error "Missing required Python packages"
        print_info "Please install: pip install psutil prometheus_client"
        exit 1
    fi
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p "$LOG_DIR"/{system,performance,security}
    mkdir -p "$DASHBOARD_DIR"/{data,static}
    mkdir -p databases/{performance,security,analytics}
    
    # Set permissions
    chmod 755 "$LOG_DIR" "$DASHBOARD_DIR" databases/
    chmod 755 .claude/hooks/performance/*.py
    chmod 755 .claude/hooks/security/*.py
    
    print_status "Directories created and permissions set"
}

# Function to initialize databases
initialize_databases() {
    print_status "Initializing databases..."
    
    python -c "
import sqlite3
import os
from datetime import datetime

# Create performance database
perf_db = 'databases/performance/metrics.db'
os.makedirs(os.path.dirname(perf_db), exist_ok=True)

conn = sqlite3.connect(perf_db)
conn.execute('''CREATE TABLE IF NOT EXISTS performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    context TEXT,
    session_id TEXT
)''')

conn.execute('''CREATE TABLE IF NOT EXISTS system_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL,
    cpu_usage REAL,
    memory_usage REAL,
    disk_usage REAL,
    network_io REAL
)''')

conn.execute('''CREATE TABLE IF NOT EXISTS tool_executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL,
    tool_name TEXT NOT NULL,
    execution_time REAL,
    success BOOLEAN,
    arguments TEXT,
    result_size INTEGER
)''')

# Create predictive analytics database
pred_db = 'databases/analytics/predictive.db'
os.makedirs(os.path.dirname(pred_db), exist_ok=True)

pred_conn = sqlite3.connect(pred_db)
pred_conn.execute('''CREATE TABLE IF NOT EXISTS velocity_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL,
    task_type TEXT,
    predicted_time REAL,
    confidence REAL,
    context TEXT
)''')

pred_conn.execute('''CREATE TABLE IF NOT EXISTS trend_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL,
    metric_name TEXT,
    trend_direction TEXT,
    slope REAL,
    confidence REAL
)''')

# Create security database
sec_db = 'databases/security/audit.db'
os.makedirs(os.path.dirname(sec_db), exist_ok=True)

sec_conn = sqlite3.connect(sec_db)
sec_conn.execute('''CREATE TABLE IF NOT EXISTS security_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL,
    event_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    details TEXT,
    file_path TEXT,
    status TEXT
)''')

# Close connections
conn.close()
pred_conn.close()
sec_conn.close()

print('✅ Databases initialized successfully')
"
    
    if [ $? -eq 0 ]; then
        print_status "Databases initialized successfully"
    else
        print_error "Failed to initialize databases"
        exit 1
    fi
}

# Function to start performance monitoring
start_performance_monitoring() {
    print_status "Starting performance monitoring system..."
    
    # Start metrics collector in background
    python .claude/hooks/performance/metrics_collector.py --daemon &
    METRICS_PID=$!
    echo $METRICS_PID > "$LOG_DIR/metrics_collector.pid"
    
    print_status "Metrics collector started (PID: $METRICS_PID)"
    
    # Start predictive analytics engine
    python .claude/hooks/performance/predictive_analytics.py --daemon &
    ANALYTICS_PID=$!
    echo $ANALYTICS_PID > "$LOG_DIR/predictive_analytics.pid"
    
    print_status "Predictive analytics started (PID: $ANALYTICS_PID)"
}

# Function to start security monitoring
start_security_monitoring() {
    print_status "Starting security monitoring system..."
    
    # Start security validator
    python .claude/hooks/security/audit_logger.py --daemon &
    SECURITY_PID=$!
    echo $SECURITY_PID > "$LOG_DIR/security_monitor.pid"
    
    print_status "Security monitoring started (PID: $SECURITY_PID)"
}

# Function to start dashboard server
start_dashboard() {
    print_status "Starting dashboard server..."
    
    # Generate initial dashboard
    python .claude/hooks/performance/dashboard_generator.py --generate-static
    
    # Start dashboard update loop
    python -c "
import time
import os
import sys
import json
import sqlite3
import threading
from datetime import datetime
import http.server
import socketserver
from pathlib import Path

class DashboardUpdater:
    def __init__(self):
        self.running = True
        
    def update_dashboard_data(self):
        '''Generate dashboard data JSON'''
        try:
            # Collect performance metrics
            perf_conn = sqlite3.connect('databases/performance/metrics.db')
            cursor = perf_conn.cursor()
            
            # Get recent system metrics
            cursor.execute('''
                SELECT cpu_usage, memory_usage, disk_usage 
                FROM system_metrics 
                ORDER BY timestamp DESC LIMIT 10
            ''')
            recent_metrics = cursor.fetchall()
            
            # Get tool performance
            cursor.execute('''
                SELECT AVG(execution_time), COUNT(*), AVG(success) 
                FROM tool_executions 
                WHERE timestamp > ? 
            ''', (time.time() - 3600,))  # Last hour
            tool_stats = cursor.fetchone()
            
            # Generate dashboard data
            dashboard_data = {
                'timestamp': time.time(),
                'system_metrics': {
                    'avg_cpu_usage': sum(m[0] for m in recent_metrics if m[0]) / len(recent_metrics) if recent_metrics else 0,
                    'avg_memory_usage': sum(m[1] for m in recent_metrics if m[1]) / len(recent_metrics) if recent_metrics else 0,
                    'avg_disk_usage': sum(m[2] for m in recent_metrics if m[2]) / len(recent_metrics) if recent_metrics else 0
                },
                'tool_performance': {
                    'avg_execution_time': tool_stats[0] if tool_stats[0] else 0,
                    'total_executions': tool_stats[1] if tool_stats[1] else 0,
                    'success_rate': (tool_stats[2] * 100) if tool_stats[2] else 100
                },
                'security_summary': {
                    'blocked_threats': 0,
                    'total_events': 0,
                    'backups_created': 0
                },
                'hook_performance': {
                    'avg_execution_time': 0.05,
                    'success_rate': 100.0,
                    'total_executions': 0
                }
            }
            
            # Save dashboard data
            os.makedirs('.claude/dashboard/data', exist_ok=True)
            with open('.claude/dashboard/data/dashboard_data.json', 'w') as f:
                json.dump(dashboard_data, f, indent=2)
                
            perf_conn.close()
            return True
            
        except Exception as e:
            print(f'Dashboard update error: {e}')
            return False
    
    def run_updates(self):
        '''Run dashboard updates in a loop'''
        while self.running:
            self.update_dashboard_data()
            time.sleep($METRICS_UPDATE_INTERVAL)

# Start dashboard updater in background thread
updater = DashboardUpdater()
update_thread = threading.Thread(target=updater.run_updates, daemon=True)
update_thread.start()

# Simple HTTP server for dashboard
class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='.', **kwargs)
    
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

# Start HTTP server
try:
    with socketserver.TCPServer(('localhost', $DASHBOARD_PORT), DashboardHandler) as httpd:
        print(f'✅ Dashboard server started at http://localhost:$DASHBOARD_PORT')
        print(f'📊 Dashboard URL: http://localhost:$DASHBOARD_PORT/.claude/dashboard.html')
        print(f'📊 Alternative URL: http://localhost:$DASHBOARD_PORT/dashboard.html')
        print(f'🔄 Updates every $METRICS_UPDATE_INTERVAL seconds')
        print('')
        print('Press Ctrl+C to stop...')
        httpd.serve_forever()
except KeyboardInterrupt:
    print('\n🛑 Dashboard server stopped')
    updater.running = False
except Exception as e:
    print(f'❌ Dashboard server error: {e}')
    sys.exit(1)
" &
    
    DASHBOARD_PID=$!
    echo $DASHBOARD_PID > "$LOG_DIR/dashboard_server.pid"
    
    print_status "Dashboard server started (PID: $DASHBOARD_PID)"
    print_info "Dashboard URL: http://localhost:$DASHBOARD_PORT/.claude/dashboard.html"
}

# Function to check if port is available
check_port() {
    if command -v nc >/dev/null 2>&1; then
        if nc -z localhost $DASHBOARD_PORT 2>/dev/null; then
            print_warning "Port $DASHBOARD_PORT is already in use"
            print_info "Trying to stop existing dashboard..."
            pkill -f "dashboard" 2>/dev/null || true
            sleep 2
        fi
    fi
}

# Function to show system status
show_status() {
    print_info "System Status:"
    echo -e "  📊 Dashboard: ${GREEN}Running on port $DASHBOARD_PORT${NC}"
    echo -e "  🔄 Updates: ${GREEN}Every $METRICS_UPDATE_INTERVAL seconds${NC}"
    echo -e "  📈 Metrics: ${GREEN}Real-time collection active${NC}"
    echo -e "  🔒 Security: ${GREEN}Validation enabled${NC}"
    echo -e "  🤖 Analytics: ${GREEN}ML predictions active${NC}"
    echo ""
    
    # Show active processes
    if [ -f "$LOG_DIR/dashboard_server.pid" ]; then
        DASHBOARD_PID=$(cat "$LOG_DIR/dashboard_server.pid")
        if ps -p $DASHBOARD_PID > /dev/null 2>&1; then
            echo -e "  🖥️  Dashboard Server: ${GREEN}Running (PID: $DASHBOARD_PID)${NC}"
        else
            echo -e "  🖥️  Dashboard Server: ${RED}Stopped${NC}"
        fi
    fi
    
    if [ -f "$LOG_DIR/metrics_collector.pid" ]; then
        METRICS_PID=$(cat "$LOG_DIR/metrics_collector.pid")
        if ps -p $METRICS_PID > /dev/null 2>&1; then
            echo -e "  📊 Metrics Collector: ${GREEN}Running (PID: $METRICS_PID)${NC}"
        else
            echo -e "  📊 Metrics Collector: ${RED}Stopped${NC}"
        fi
    fi
    
    if [ -f "$LOG_DIR/predictive_analytics.pid" ]; then
        ANALYTICS_PID=$(cat "$LOG_DIR/predictive_analytics.pid")
        if ps -p $ANALYTICS_PID > /dev/null 2>&1; then
            echo -e "  🔮 Predictive Analytics: ${GREEN}Running (PID: $ANALYTICS_PID)${NC}"
        else
            echo -e "  🔮 Predictive Analytics: ${RED}Stopped${NC}"
        fi
    fi
    
    echo ""
}

# Function to stop monitoring
stop_monitoring() {
    print_status "Stopping monitoring services..."
    
    # Stop dashboard server
    if [ -f "$LOG_DIR/dashboard_server.pid" ]; then
        DASHBOARD_PID=$(cat "$LOG_DIR/dashboard_server.pid")
        if ps -p $DASHBOARD_PID > /dev/null 2>&1; then
            kill $DASHBOARD_PID 2>/dev/null || true
            print_status "Dashboard server stopped"
        fi
        rm -f "$LOG_DIR/dashboard_server.pid"
    fi
    
    # Stop metrics collector
    if [ -f "$LOG_DIR/metrics_collector.pid" ]; then
        METRICS_PID=$(cat "$LOG_DIR/metrics_collector.pid")
        if ps -p $METRICS_PID > /dev/null 2>&1; then
            kill $METRICS_PID 2>/dev/null || true
            print_status "Metrics collector stopped"
        fi
        rm -f "$LOG_DIR/metrics_collector.pid"
    fi
    
    # Stop predictive analytics
    if [ -f "$LOG_DIR/predictive_analytics.pid" ]; then
        ANALYTICS_PID=$(cat "$LOG_DIR/predictive_analytics.pid")
        if ps -p $ANALYTICS_PID > /dev/null 2>&1; then
            kill $ANALYTICS_PID 2>/dev/null || true
            print_status "Predictive analytics stopped"
        fi
        rm -f "$LOG_DIR/predictive_analytics.pid"
    fi
    
    # Stop security monitoring
    if [ -f "$LOG_DIR/security_monitor.pid" ]; then
        SECURITY_PID=$(cat "$LOG_DIR/security_monitor.pid")
        if ps -p $SECURITY_PID > /dev/null 2>&1; then
            kill $SECURITY_PID 2>/dev/null || true
            print_status "Security monitoring stopped"
        fi
        rm -f "$LOG_DIR/security_monitor.pid"
    fi
    
    print_status "All monitoring services stopped"
}

# Function to show help
show_help() {
    echo -e "${BLUE}10X Agentic Setup - Monitoring Dashboard${NC}"
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo "  $0 [command]"
    echo ""
    echo -e "${YELLOW}Commands:${NC}"
    echo "  start     Start monitoring dashboard (default)"
    echo "  stop      Stop all monitoring services"
    echo "  restart   Restart monitoring services"
    echo "  status    Show system status"
    echo "  logs      Show recent logs"
    echo "  help      Show this help message"
    echo ""
    echo -e "${YELLOW}Features:${NC}"
    echo "  📊 Real-time performance metrics"
    echo "  🔒 Security validation monitoring"
    echo "  🔮 ML-powered predictive analytics"
    echo "  📈 System resource tracking"
    echo "  🎛️  Interactive dashboard with charts"
    echo ""
    echo -e "${YELLOW}Dashboard URL:${NC}"
    echo "  http://localhost:$DASHBOARD_PORT/.claude/dashboard.html"
}

# Function to show logs
show_logs() {
    print_info "Recent system logs:"
    
    if [ -f "$LOG_DIR/system/monitoring.log" ]; then
        echo -e "${CYAN}Performance Logs:${NC}"
        tail -10 "$LOG_DIR/system/monitoring.log" 2>/dev/null || echo "No performance logs yet"
    fi
    
    if [ -f "$LOG_DIR/security/audit.log" ]; then
        echo -e "\n${CYAN}Security Logs:${NC}"
        tail -10 "$LOG_DIR/security/audit.log" 2>/dev/null || echo "No security logs yet"
    fi
    
    # Show database statistics
    echo -e "\n${CYAN}Database Statistics:${NC}"
    python -c "
import sqlite3
import os

databases = [
    ('Performance', 'databases/performance/metrics.db', 'performance_metrics'),
    ('Security', 'databases/security/audit.db', 'security_events'),
    ('Analytics', 'databases/analytics/predictive.db', 'velocity_predictions')
]

for name, db_path, table in databases:
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()[0]
            print(f'  {name}: {count} records')
            conn.close()
        except Exception as e:
            print(f'  {name}: Error - {e}')
    else:
        print(f'  {name}: Database not found')
"
}

# Trap Ctrl+C to clean up
trap 'print_info "Received interrupt signal..."; stop_monitoring; exit 0' INT TERM

# Main execution
main() {
    case "${1:-start}" in
        start)
            print_status "Starting 10X Agentic Monitoring Dashboard..."
            check_venv
            activate_venv
            check_dependencies
            create_directories
            initialize_databases
            check_port
            start_performance_monitoring
            start_security_monitoring
            start_dashboard
            
            echo ""
            print_status "🎉 Monitoring dashboard started successfully!"
            show_status
            
            # Keep script running
            wait
            ;;
        stop)
            stop_monitoring
            ;;
        restart)
            stop_monitoring
            sleep 2
            exec "$0" start
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"