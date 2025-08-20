#!/usr/bin/env python3
"""
Real-time Dashboard Generator
Creates and updates HTML dashboard with live performance metrics and security monitoring
"""

import os
import json
import time
import sqlite3
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DashboardGenerator:
    """Real-time dashboard with live performance and security monitoring"""
    
    def __init__(self, metrics_db_path: str = None, security_db_path: str = None):
        self.metrics_db_path = metrics_db_path or str(Path.home() / ".claude" / "performance_metrics.db")
        self.security_db_path = security_db_path or str(Path.home() / ".claude" / "security_audit.db")
        self.dashboard_path = Path.home() / ".claude" / "dashboard.html"
        self.data_path = Path.home() / ".claude" / "dashboard_data.json"
        
        # Auto-refresh settings
        self.refresh_interval = 10  # seconds
        self.max_data_points = 100
        
        # Dashboard is running flag
        self.is_running = False
        self.update_thread = None
        
        logger.info("Dashboard generator initialized")
    
    def generate_dashboard_html(self) -> str:
        """Generate complete HTML dashboard with charts and real-time data"""
        
        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claude Code - 10X Performance & Security Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            color: white;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header .subtitle {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .status-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(255,255,255,0.1);
            padding: 15px 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
            color: white;
        }
        
        .status-item {
            text-align: center;
        }
        
        .status-value {
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .status-label {
            font-size: 0.9em;
            opacity: 0.8;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }
        
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .card-title {
            font-size: 1.3em;
            font-weight: 600;
            color: #333;
        }
        
        .card-status {
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
        }
        
        .status-good {
            background: #d4edda;
            color: #155724;
        }
        
        .status-warning {
            background: #fff3cd;
            color: #856404;
        }
        
        .status-critical {
            background: #f8d7da;
            color: #721c24;
        }
        
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .metric-item {
            text-align: center;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .metric-value {
            font-size: 1.8em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .metric-label {
            font-size: 0.9em;
            color: #666;
        }
        
        .chart-container {
            position: relative;
            height: 300px;
            margin-top: 20px;
        }
        
        .alerts-list {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .alert-item {
            display: flex;
            align-items: center;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 8px;
            border-left: 4px solid;
        }
        
        .alert-critical {
            background: #fff5f5;
            border-color: #e53e3e;
        }
        
        .alert-warning {
            background: #fffaf0;
            border-color: #dd6b20;
        }
        
        .alert-info {
            background: #f0f8ff;
            border-color: #3182ce;
        }
        
        .alert-time {
            font-size: 0.8em;
            color: #666;
            margin-right: 10px;
            min-width: 60px;
        }
        
        .alert-message {
            flex: 1;
            font-size: 0.9em;
        }
        
        .refresh-indicator {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 10px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            z-index: 1000;
        }
        
        .tools-list {
            max-height: 250px;
            overflow-y: auto;
        }
        
        .tool-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .tool-name {
            font-weight: 500;
        }
        
        .tool-metrics {
            display: flex;
            gap: 15px;
            font-size: 0.9em;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Claude Code Dashboard</h1>
            <div class="subtitle">10X Performance & Security Monitoring</div>
        </div>
        
        <div class="status-bar">
            <div class="status-item">
                <div class="status-value" id="system-status">🟢 HEALTHY</div>
                <div class="status-label">System Status</div>
            </div>
            <div class="status-item">
                <div class="status-value" id="security-status">🛡️ PROTECTED</div>
                <div class="status-label">Security Status</div>
            </div>
            <div class="status-item">
                <div class="status-value" id="performance-status">⚡ OPTIMAL</div>
                <div class="status-label">Performance</div>
            </div>
            <div class="status-item">
                <div class="status-value" id="last-update">--</div>
                <div class="status-label">Last Update</div>
            </div>
        </div>
        
        <div class="grid">
            <!-- System Resources -->
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">💻 System Resources</h3>
                    <span class="card-status status-good" id="resources-status">Healthy</span>
                </div>
                <div class="metric-grid">
                    <div class="metric-item">
                        <div class="metric-value" id="cpu-usage">--</div>
                        <div class="metric-label">CPU %</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-value" id="memory-usage">--</div>
                        <div class="metric-label">Memory %</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-value" id="disk-usage">--</div>
                        <div class="metric-label">Disk %</div>
                    </div>
                </div>
                <div class="chart-container">
                    <canvas id="resources-chart"></canvas>
                </div>
            </div>
            
            <!-- Tool Performance -->
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">🔧 Tool Performance</h3>
                    <span class="card-status status-good" id="tools-status">Good</span>
                </div>
                <div class="metric-grid">
                    <div class="metric-item">
                        <div class="metric-value" id="avg-execution-time">--</div>
                        <div class="metric-label">Avg Time (s)</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-value" id="success-rate">--</div>
                        <div class="metric-label">Success %</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-value" id="total-executions">--</div>
                        <div class="metric-label">Total Runs</div>
                    </div>
                </div>
                <div class="tools-list" id="tools-list">
                    <!-- Tool list will be populated here -->
                </div>
            </div>
            
            <!-- Security Overview -->
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">🛡️ Security Overview</h3>
                    <span class="card-status status-good" id="security-card-status">Secure</span>
                </div>
                <div class="metric-grid">
                    <div class="metric-item">
                        <div class="metric-value" id="blocked-threats">--</div>
                        <div class="metric-label">Threats Blocked</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-value" id="security-events">--</div>
                        <div class="metric-label">Events (24h)</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-value" id="backups-created">--</div>
                        <div class="metric-label">Backups</div>
                    </div>
                </div>
                <div class="chart-container">
                    <canvas id="security-chart"></canvas>
                </div>
            </div>
            
            <!-- Recent Alerts -->
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">⚠️ Recent Alerts</h3>
                    <span class="card-status status-good" id="alerts-status">No Issues</span>
                </div>
                <div class="alerts-list" id="alerts-list">
                    <!-- Alerts will be populated here -->
                </div>
            </div>
            
            <!-- Hook Performance -->
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">🪝 Hook Performance</h3>
                    <span class="card-status status-good" id="hooks-status">Efficient</span>
                </div>
                <div class="metric-grid">
                    <div class="metric-item">
                        <div class="metric-value" id="hook-avg-time">--</div>
                        <div class="metric-label">Avg Time (ms)</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-value" id="hook-success-rate">--</div>
                        <div class="metric-label">Success %</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-value" id="hook-executions">--</div>
                        <div class="metric-label">Executions</div>
                    </div>
                </div>
                <div class="chart-container">
                    <canvas id="hooks-chart"></canvas>
                </div>
            </div>
            
            <!-- MCP Coordination -->
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">🔗 MCP Coordination</h3>
                    <span class="card-status status-good" id="mcp-status">Connected</span>
                </div>
                <div class="metric-grid">
                    <div class="metric-item">
                        <div class="metric-value" id="active-servers">7/7</div>
                        <div class="metric-label">Active Servers</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-value" id="parallel-tasks">--</div>
                        <div class="metric-label">Parallel Tasks</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-value" id="coordination-efficiency">--</div>
                        <div class="metric-label">Efficiency %</div>
                    </div>
                </div>
                <div class="chart-container">
                    <canvas id="mcp-chart"></canvas>
                </div>
            </div>
        </div>
    </div>
    
    <div class="refresh-indicator" id="refresh-indicator">
        🔄 Updating...
    </div>
    
    <script>
        // Global variables for charts
        let resourcesChart, securityChart, hooksChart, mcpChart;
        let dashboardData = {};
        
        // Initialize charts
        function initializeCharts() {
            const chartOptions = {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    },
                    x: {
                        display: false
                    }
                }
            };
            
            // Resources Chart
            const resourcesCtx = document.getElementById('resources-chart').getContext('2d');
            resourcesChart = new Chart(resourcesCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: 'CPU %',
                            data: [],
                            borderColor: '#ff6b6b',
                            backgroundColor: 'rgba(255, 107, 107, 0.1)',
                            tension: 0.4
                        },
                        {
                            label: 'Memory %',
                            data: [],
                            borderColor: '#4ecdc4',
                            backgroundColor: 'rgba(78, 205, 196, 0.1)',
                            tension: 0.4
                        },
                        {
                            label: 'Disk %',
                            data: [],
                            borderColor: '#45b7d1',
                            backgroundColor: 'rgba(69, 183, 209, 0.1)',
                            tension: 0.4
                        }
                    ]
                },
                options: chartOptions
            });
            
            // Security Chart
            const securityCtx = document.getElementById('security-chart').getContext('2d');
            securityChart = new Chart(securityCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Allowed', 'Blocked', 'Warnings'],
                    datasets: [{
                        data: [0, 0, 0],
                        backgroundColor: ['#51cf66', '#ff6b6b', '#ffd43b'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
            
            // Hooks Chart  
            const hooksCtx = document.getElementById('hooks-chart').getContext('2d');
            hooksChart = new Chart(hooksCtx, {
                type: 'bar',
                data: {
                    labels: ['PreToolUse', 'PostToolUse', 'UserPromptSubmit', 'Stop'],
                    datasets: [{
                        label: 'Avg Execution Time (ms)',
                        data: [0, 0, 0, 0],
                        backgroundColor: '#667eea',
                        borderRadius: 5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Time (ms)'
                            }
                        }
                    }
                }
            });
            
            // MCP Chart
            const mcpCtx = document.getElementById('mcp-chart').getContext('2d');
            mcpChart = new Chart(mcpCtx, {
                type: 'radar',
                data: {
                    labels: ['ML Intelligence', 'Memory', 'Analytics', 'Testing', 'Workflow', 'Knowledge', 'Commands'],
                    datasets: [{
                        label: 'Server Health',
                        data: [100, 100, 100, 100, 100, 100, 100],
                        borderColor: '#764ba2',
                        backgroundColor: 'rgba(118, 75, 162, 0.2)',
                        pointBackgroundColor: '#764ba2'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        r: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                stepSize: 20
                            }
                        }
                    }
                }
            });
        }
        
        // Update dashboard data
        async function updateDashboard() {
            const indicator = document.getElementById('refresh-indicator');
            indicator.style.display = 'block';
            
            try {
                // Fetch dashboard data
                const response = await fetch('dashboard_data.json?' + new Date().getTime());
                dashboardData = await response.json();
                
                // Update status bar
                updateStatusBar();
                
                // Update all sections
                updateSystemResources();
                updateToolPerformance();
                updateSecurityOverview();
                updateRecentAlerts();
                updateHookPerformance();
                updateMCPCoordination();
                
                // Update charts
                updateCharts();
                
            } catch (error) {
                console.error('Failed to update dashboard:', error);
            } finally {
                indicator.style.display = 'none';
            }
        }
        
        function updateStatusBar() {
            const now = new Date();
            document.getElementById('last-update').textContent = now.toLocaleTimeString();
            
            // Update overall statuses based on data
            const systemStatus = dashboardData.system_metrics ? 
                (dashboardData.system_metrics.avg_cpu_usage > 90 ? '🔴 OVERLOADED' : 
                 dashboardData.system_metrics.avg_cpu_usage > 70 ? '🟡 BUSY' : '🟢 HEALTHY') : '🟢 HEALTHY';
            document.getElementById('system-status').textContent = systemStatus;
            
            const securityStatus = dashboardData.security_summary && dashboardData.security_summary.recent_violations > 10 ? 
                '🔴 ALERTS' : '🛡️ PROTECTED';
            document.getElementById('security-status').textContent = securityStatus;
            
            const performanceStatus = dashboardData.tool_performance && dashboardData.tool_performance.avg_execution_time > 10 ?
                '🔴 SLOW' : '⚡ OPTIMAL';
            document.getElementById('performance-status').textContent = performanceStatus;
        }
        
        function updateSystemResources() {
            if (!dashboardData.system_metrics) return;
            
            const metrics = dashboardData.system_metrics;
            document.getElementById('cpu-usage').textContent = metrics.avg_cpu_usage?.toFixed(1) + '%' || '--';
            document.getElementById('memory-usage').textContent = metrics.avg_memory_usage?.toFixed(1) + '%' || '--';
            document.getElementById('disk-usage').textContent = metrics.avg_disk_usage?.toFixed(1) + '%' || '--';
            
            // Update status
            const maxUsage = Math.max(metrics.avg_cpu_usage || 0, metrics.avg_memory_usage || 0);
            const statusElement = document.getElementById('resources-status');
            if (maxUsage > 90) {
                statusElement.textContent = 'Critical';
                statusElement.className = 'card-status status-critical';
            } else if (maxUsage > 70) {
                statusElement.textContent = 'Warning';
                statusElement.className = 'card-status status-warning';
            } else {
                statusElement.textContent = 'Healthy';
                statusElement.className = 'card-status status-good';
            }
        }
        
        function updateToolPerformance() {
            if (!dashboardData.tool_performance) return;
            
            const performance = dashboardData.tool_performance;
            document.getElementById('avg-execution-time').textContent = performance.avg_execution_time?.toFixed(2) + 's' || '--';
            document.getElementById('success-rate').textContent = performance.success_rate?.toFixed(1) + '%' || '--';
            document.getElementById('total-executions').textContent = performance.total_executions || '--';
            
            // Update tools list
            const toolsList = document.getElementById('tools-list');
            if (performance.top_tools) {
                toolsList.innerHTML = performance.top_tools.map(tool => `
                    <div class="tool-item">
                        <span class="tool-name">${tool.name}</span>
                        <div class="tool-metrics">
                            <span>${tool.avg_time?.toFixed(2)}s</span>
                            <span>${tool.executions} runs</span>
                        </div>
                    </div>
                `).join('');
            }
        }
        
        function updateSecurityOverview() {
            if (!dashboardData.security_summary) return;
            
            const security = dashboardData.security_summary;
            document.getElementById('blocked-threats').textContent = security.blocked_threats || '0';
            document.getElementById('security-events').textContent = security.total_events || '0';
            document.getElementById('backups-created').textContent = security.backups_created || '0';
        }
        
        function updateRecentAlerts() {
            if (!dashboardData.recent_alerts) return;
            
            const alertsList = document.getElementById('alerts-list');
            const alerts = dashboardData.recent_alerts.slice(0, 10); // Show last 10 alerts
            
            if (alerts.length === 0) {
                alertsList.innerHTML = '<div style="text-align: center; color: #666; padding: 20px;">No recent alerts</div>';
                return;
            }
            
            alertsList.innerHTML = alerts.map(alert => {
                const alertClass = alert.severity === 'critical' ? 'alert-critical' : 
                                 alert.severity === 'warning' ? 'alert-warning' : 'alert-info';
                const time = new Date(alert.timestamp * 1000).toLocaleTimeString();
                
                return `
                    <div class="alert-item ${alertClass}">
                        <span class="alert-time">${time}</span>
                        <span class="alert-message">${alert.message}</span>
                    </div>
                `;
            }).join('');
            
            // Update alerts status
            const criticalAlerts = alerts.filter(a => a.severity === 'critical').length;
            const statusElement = document.getElementById('alerts-status');
            if (criticalAlerts > 0) {
                statusElement.textContent = `${criticalAlerts} Critical`;
                statusElement.className = 'card-status status-critical';
            } else if (alerts.length > 0) {
                statusElement.textContent = `${alerts.length} Alerts`;
                statusElement.className = 'card-status status-warning';
            } else {
                statusElement.textContent = 'No Issues';
                statusElement.className = 'card-status status-good';
            }
        }
        
        function updateHookPerformance() {
            if (!dashboardData.hook_performance) return;
            
            const hooks = dashboardData.hook_performance;
            document.getElementById('hook-avg-time').textContent = (hooks.avg_execution_time * 1000)?.toFixed(0) + 'ms' || '--';
            document.getElementById('hook-success-rate').textContent = hooks.success_rate?.toFixed(1) + '%' || '--';
            document.getElementById('hook-executions').textContent = hooks.total_executions || '--';
        }
        
        function updateMCPCoordination() {
            if (!dashboardData.mcp_coordination) return;
            
            const mcp = dashboardData.mcp_coordination;
            document.getElementById('active-servers').textContent = `${mcp.active_servers || 0}/7`;
            document.getElementById('parallel-tasks').textContent = mcp.parallel_tasks || '0';
            document.getElementById('coordination-efficiency').textContent = mcp.efficiency?.toFixed(1) + '%' || '--';
        }
        
        function updateCharts() {
            // Update resources chart
            if (dashboardData.time_series && resourcesChart) {
                const series = dashboardData.time_series;
                resourcesChart.data.labels = series.timestamps || [];
                resourcesChart.data.datasets[0].data = series.cpu_usage || [];
                resourcesChart.data.datasets[1].data = series.memory_usage || [];
                resourcesChart.data.datasets[2].data = series.disk_usage || [];
                resourcesChart.update('none');
            }
            
            // Update security chart
            if (dashboardData.security_breakdown && securityChart) {
                const breakdown = dashboardData.security_breakdown;
                securityChart.data.datasets[0].data = [
                    breakdown.allowed || 0,
                    breakdown.blocked || 0,
                    breakdown.warnings || 0
                ];
                securityChart.update('none');
            }
            
            // Update hooks chart
            if (dashboardData.hook_breakdown && hooksChart) {
                const breakdown = dashboardData.hook_breakdown;
                hooksChart.data.datasets[0].data = [
                    (breakdown.PreToolUse?.avg_time * 1000) || 0,
                    (breakdown.PostToolUse?.avg_time * 1000) || 0,
                    (breakdown.UserPromptSubmit?.avg_time * 1000) || 0,
                    (breakdown.Stop?.avg_time * 1000) || 0
                ];
                hooksChart.update('none');
            }
            
            // Update MCP chart
            if (dashboardData.mcp_server_health && mcpChart) {
                const health = dashboardData.mcp_server_health;
                mcpChart.data.datasets[0].data = [
                    health['ml-code-intelligence'] || 0,
                    health['context-aware-memory'] || 0,
                    health['predictive-analytics'] || 0,
                    health['ml-testing-qa'] || 0,
                    health['agentic-workflow'] || 0,
                    health['10x-knowledge-graph'] || 0,
                    health['10x-command-analytics'] || 0
                ];
                mcpChart.update('none');
            }
        }
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            initializeCharts();
            updateDashboard();
            
            // Auto-refresh every 10 seconds
            setInterval(updateDashboard, 10000);
        });
    </script>
</body>
</html>'''
        
        return html_content
    
    def collect_dashboard_data(self) -> Dict[str, Any]:
        """Collect all data needed for the dashboard"""
        
        data = {
            'timestamp': time.time(),
            'system_metrics': self._get_system_metrics(),
            'tool_performance': self._get_tool_performance(),
            'security_summary': self._get_security_summary(),
            'recent_alerts': self._get_recent_alerts(),
            'hook_performance': self._get_hook_performance(),
            'mcp_coordination': self._get_mcp_coordination(),
            'time_series': self._get_time_series_data(),
            'security_breakdown': self._get_security_breakdown(),
            'hook_breakdown': self._get_hook_breakdown(),
            'mcp_server_health': self._get_mcp_server_health()
        }
        
        return data
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics from performance database"""
        
        if not Path(self.metrics_db_path).exists():
            return {}
        
        try:
            with sqlite3.connect(self.metrics_db_path) as conn:
                cursor = conn.execute('''
                    SELECT AVG(cpu_usage), AVG(memory_usage), AVG(disk_usage),
                           MAX(cpu_usage), MAX(memory_usage), MAX(disk_usage),
                           COUNT(*)
                    FROM system_metrics
                    WHERE timestamp >= ?
                ''', (time.time() - 3600,))  # Last hour
                
                row = cursor.fetchone()
                if row and row[0] is not None:
                    return {
                        'avg_cpu_usage': row[0],
                        'avg_memory_usage': row[1],
                        'avg_disk_usage': row[2],
                        'max_cpu_usage': row[3],
                        'max_memory_usage': row[4],
                        'max_disk_usage': row[5],
                        'sample_count': row[6]
                    }
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
        
        return {}
    
    def _get_tool_performance(self) -> Dict[str, Any]:
        """Get tool performance metrics"""
        
        if not Path(self.metrics_db_path).exists():
            return {}
        
        try:
            with sqlite3.connect(self.metrics_db_path) as conn:
                # Overall tool performance
                cursor = conn.execute('''
                    SELECT AVG(execution_time), COUNT(*),
                           AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) * 100
                    FROM tool_execution_metrics
                    WHERE start_time >= ?
                ''', (time.time() - 3600,))
                
                row = cursor.fetchone()
                overall_metrics = {}
                if row and row[0] is not None:
                    overall_metrics = {
                        'avg_execution_time': row[0],
                        'total_executions': row[1],
                        'success_rate': row[2]
                    }
                
                # Top tools by usage
                cursor = conn.execute('''
                    SELECT tool_name, AVG(execution_time), COUNT(*)
                    FROM tool_execution_metrics
                    WHERE start_time >= ?
                    GROUP BY tool_name
                    ORDER BY COUNT(*) DESC
                    LIMIT 10
                ''', (time.time() - 3600,))
                
                top_tools = []
                for row in cursor.fetchall():
                    top_tools.append({
                        'name': row[0],
                        'avg_time': row[1],
                        'executions': row[2]
                    })
                
                overall_metrics['top_tools'] = top_tools
                return overall_metrics
                
        except Exception as e:
            logger.error(f"Failed to get tool performance: {e}")
        
        return {}
    
    def _get_security_summary(self) -> Dict[str, Any]:
        """Get security summary from audit database"""
        
        if not Path(self.security_db_path).exists():
            return {}
        
        try:
            with sqlite3.connect(self.security_db_path) as conn:
                # Count events by result
                cursor = conn.execute('''
                    SELECT result, COUNT(*)
                    FROM audit_events
                    WHERE timestamp >= ?
                    GROUP BY result
                ''', (time.time() - 86400,))  # Last 24 hours
                
                event_counts = {}
                for result, count in cursor.fetchall():
                    event_counts[result] = count
                
                # Count security violations
                cursor = conn.execute('''
                    SELECT COUNT(*)
                    FROM audit_events
                    WHERE event_type = 'security_violation' AND timestamp >= ?
                ''', (time.time() - 86400,))
                
                violations = cursor.fetchone()[0] if cursor.fetchone() else 0
                
                return {
                    'blocked_threats': event_counts.get('blocked', 0),
                    'total_events': sum(event_counts.values()),
                    'recent_violations': violations,
                    'backups_created': event_counts.get('backup_created', 0)
                }
        except Exception as e:
            logger.error(f"Failed to get security summary: {e}")
        
        return {}
    
    def _get_recent_alerts(self) -> List[Dict[str, Any]]:
        """Get recent performance and security alerts"""
        
        alerts = []
        
        # Performance alerts
        if Path(self.metrics_db_path).exists():
            try:
                with sqlite3.connect(self.metrics_db_path) as conn:
                    cursor = conn.execute('''
                        SELECT message, severity, timestamp
                        FROM performance_alerts
                        WHERE timestamp >= ?
                        ORDER BY timestamp DESC
                        LIMIT 20
                    ''', (time.time() - 86400,))  # Last 24 hours
                    
                    for message, severity, timestamp in cursor.fetchall():
                        alerts.append({
                            'message': message,
                            'severity': severity,
                            'timestamp': timestamp,
                            'type': 'performance'
                        })
            except Exception as e:
                logger.error(f"Failed to get performance alerts: {e}")
        
        # Security alerts
        if Path(self.security_db_path).exists():
            try:
                with sqlite3.connect(self.security_db_path) as conn:
                    cursor = conn.execute('''
                        SELECT message, severity, triggered_at
                        FROM security_alerts
                        WHERE triggered_at >= ?
                        ORDER BY triggered_at DESC
                        LIMIT 20
                    ''', (time.time() - 86400,))
                    
                    for message, severity, timestamp in cursor.fetchall():
                        alerts.append({
                            'message': message,
                            'severity': severity,
                            'timestamp': timestamp,
                            'type': 'security'
                        })
            except Exception as e:
                logger.error(f"Failed to get security alerts: {e}")
        
        # Sort all alerts by timestamp
        alerts.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return alerts[:20]  # Return latest 20 alerts
    
    def _get_hook_performance(self) -> Dict[str, Any]:
        """Get hook performance metrics"""
        
        if not Path(self.metrics_db_path).exists():
            return {}
        
        try:
            with sqlite3.connect(self.metrics_db_path) as conn:
                cursor = conn.execute('''
                    SELECT AVG(execution_time), COUNT(*),
                           AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) * 100
                    FROM hook_performance_metrics
                    WHERE timestamp >= ?
                ''', (time.time() - 3600,))
                
                row = cursor.fetchone()
                if row and row[0] is not None:
                    return {
                        'avg_execution_time': row[0],
                        'total_executions': row[1],
                        'success_rate': row[2]
                    }
        except Exception as e:
            logger.error(f"Failed to get hook performance: {e}")
        
        return {}
    
    def _get_mcp_coordination(self) -> Dict[str, Any]:
        """Get MCP coordination metrics"""
        
        # Simulated MCP coordination data
        return {
            'active_servers': 7,
            'parallel_tasks': 12,
            'efficiency': 94.5,
            'total_requests': 1247,
            'avg_response_time': 0.85
        }
    
    def _get_time_series_data(self) -> Dict[str, Any]:
        """Get time series data for charts"""
        
        if not Path(self.metrics_db_path).exists():
            return {}
        
        try:
            with sqlite3.connect(self.metrics_db_path) as conn:
                cursor = conn.execute('''
                    SELECT timestamp, cpu_usage, memory_usage, disk_usage
                    FROM system_metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (time.time() - 3600, self.max_data_points))
                
                timestamps = []
                cpu_usage = []
                memory_usage = []
                disk_usage = []
                
                for row in reversed(cursor.fetchall()):  # Reverse to get chronological order
                    timestamps.append(datetime.fromtimestamp(row[0]).strftime('%H:%M'))
                    cpu_usage.append(row[1])
                    memory_usage.append(row[2])
                    disk_usage.append(row[3])
                
                return {
                    'timestamps': timestamps,
                    'cpu_usage': cpu_usage,
                    'memory_usage': memory_usage,
                    'disk_usage': disk_usage
                }
        except Exception as e:
            logger.error(f"Failed to get time series data: {e}")
        
        return {}
    
    def _get_security_breakdown(self) -> Dict[str, Any]:
        """Get security event breakdown for pie chart"""
        
        if not Path(self.security_db_path).exists():
            return {}
        
        try:
            with sqlite3.connect(self.security_db_path) as conn:
                cursor = conn.execute('''
                    SELECT 
                        SUM(CASE WHEN result = 'allowed' THEN 1 ELSE 0 END) as allowed,
                        SUM(CASE WHEN result = 'blocked' THEN 1 ELSE 0 END) as blocked,
                        SUM(CASE WHEN severity = 'warning' THEN 1 ELSE 0 END) as warnings
                    FROM audit_events
                    WHERE timestamp >= ?
                ''', (time.time() - 86400,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'allowed': row[0] or 0,
                        'blocked': row[1] or 0,
                        'warnings': row[2] or 0
                    }
        except Exception as e:
            logger.error(f"Failed to get security breakdown: {e}")
        
        return {}
    
    def _get_hook_breakdown(self) -> Dict[str, Any]:
        """Get hook performance breakdown by type"""
        
        if not Path(self.metrics_db_path).exists():
            return {}
        
        try:
            with sqlite3.connect(self.metrics_db_path) as conn:
                cursor = conn.execute('''
                    SELECT hook_type, AVG(execution_time), COUNT(*)
                    FROM hook_performance_metrics
                    WHERE timestamp >= ?
                    GROUP BY hook_type
                ''', (time.time() - 3600,))
                
                breakdown = {}
                for hook_type, avg_time, count in cursor.fetchall():
                    breakdown[hook_type] = {
                        'avg_time': avg_time,
                        'count': count
                    }
                
                return breakdown
        except Exception as e:
            logger.error(f"Failed to get hook breakdown: {e}")
        
        return {}
    
    def _get_mcp_server_health(self) -> Dict[str, Any]:
        """Get MCP server health metrics"""
        
        # Simulated MCP server health data
        return {
            'ml-code-intelligence': 98,
            'context-aware-memory': 95,
            'predictive-analytics': 92,
            'ml-testing-qa': 89,
            'agentic-workflow': 94,
            '10x-knowledge-graph': 91,
            '10x-command-analytics': 96
        }
    
    def update_dashboard_data(self):
        """Update dashboard data file"""
        
        try:
            data = self.collect_dashboard_data()
            
            with open(self.data_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug("Dashboard data updated")
            
        except Exception as e:
            logger.error(f"Failed to update dashboard data: {e}")
    
    def start_dashboard(self, port: int = 8080):
        """Start the dashboard with auto-refresh"""
        
        # Generate HTML dashboard
        html_content = self.generate_dashboard_html()
        
        with open(self.dashboard_path, 'w') as f:
            f.write(html_content)
        
        # Start data update loop
        self.is_running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        
        logger.info(f"Dashboard started at: {self.dashboard_path}")
        logger.info("Open the dashboard.html file in your browser to view real-time metrics")
        
        return str(self.dashboard_path)
    
    def stop_dashboard(self):
        """Stop the dashboard updates"""
        
        self.is_running = False
        if self.update_thread:
            self.update_thread.join(timeout=5.0)
        
        logger.info("Dashboard stopped")
    
    def _update_loop(self):
        """Background loop to update dashboard data"""
        
        while self.is_running:
            try:
                self.update_dashboard_data()
                time.sleep(self.refresh_interval)
            except Exception as e:
                logger.error(f"Dashboard update error: {e}")
                time.sleep(self.refresh_interval * 2)  # Wait longer on error

# Example usage and testing
def test_dashboard_generator():
    """Test the dashboard generator functionality"""
    
    print("🧪 Testing Dashboard Generator...")
    
    generator = DashboardGenerator()
    
    # Generate dashboard
    print("🎨 Generating dashboard HTML...")
    dashboard_path = generator.start_dashboard()
    print(f"   Dashboard created at: {dashboard_path}")
    
    # Wait for a few updates
    print("📊 Collecting dashboard data...")
    time.sleep(15)  # Let it collect some data
    
    # Check if data file was created
    data_file = Path.home() / ".claude" / "dashboard_data.json"
    if data_file.exists():
        with open(data_file) as f:
            data = json.load(f)
        print(f"   Dashboard data collected: {len(data)} sections")
    else:
        print("   ⚠️ No dashboard data file found")
    
    # Stop dashboard
    generator.stop_dashboard()
    
    print("✅ Dashboard generator test completed!")
    print(f"💡 Open {dashboard_path} in your browser to view the dashboard")

if __name__ == "__main__":
    test_dashboard_generator()