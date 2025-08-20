#!/usr/bin/env python3
"""
Claude Sub-Agent: Project Review & Status Reporter
Provides comprehensive project status in both human and machine-readable formats
"""

import sys
import json
import os
import subprocess
from pathlib import Path
from datetime import datetime, timezone
import glob

def get_git_status():
    """Get comprehensive git repository status"""
    try:
        # Get current branch
        branch = subprocess.check_output(['git', 'branch', '--show-current'], text=True).strip()
        
        # Get last commit
        last_commit = subprocess.check_output(
            ['git', 'log', '-1', '--pretty=format:%h - %s (%ar)'], 
            text=True
        ).strip()
        
        # Get uncommitted changes
        status = subprocess.check_output(['git', 'status', '--porcelain'], text=True)
        uncommitted_files = len(status.strip().split('\n')) if status.strip() else 0
        
        # Get recent commits
        recent_commits = subprocess.check_output(
            ['git', 'log', '--oneline', '-5'],
            text=True
        ).strip().split('\n')
        
        return {
            "current_branch": branch,
            "last_commit": last_commit,
            "uncommitted_changes": uncommitted_files,
            "recent_commits": recent_commits,
            "clean": uncommitted_files == 0
        }
    except Exception as e:
        return {"error": str(e)}

def get_claude_logs():
    """Analyze Claude agent activity logs"""
    claude_data = Path(".claude/data")
    sessions_dir = claude_data / "sessions"
    
    sessions = []
    if sessions_dir.exists():
        # Get recent session files
        session_files = sorted(sessions_dir.glob("*_performance_report.json"), 
                             key=lambda x: x.stat().st_mtime, 
                             reverse=True)[:5]
        
        for session_file in session_files:
            try:
                with open(session_file, 'r') as f:
                    report = json.load(f)
                
                sessions.append({
                    "session_id": report.get("session_id", "unknown"),
                    "timestamp": report.get("timestamp", ""),
                    "completion_score": report.get("completion_score", 0),
                    "task_signature": report.get("task_signature", "")[:30] + "...",
                    "verification_passed": sum(1 for v in report.get("verification_results", {}).values() if v == True)
                })
            except:
                continue
    
    # Get performance insights if available
    insights = {}
    insights_file = claude_data / "performance_insights.json"
    if insights_file.exists():
        try:
            with open(insights_file, 'r') as f:
                insights = json.load(f)
        except:
            pass
    
    return {
        "recent_sessions": sessions,
        "insights": insights.get("overall_stats", {}),
        "alerts": insights.get("alerts", [])
    }

def get_project_structure():
    """Analyze project structure and key files"""
    # Key directories to check
    key_dirs = [
        ".claude",
        "apps/server", 
        "apps/client",
        "node_modules"
    ]
    
    # Key files to check
    key_files = [
        "package.json",
        "README.md",
        ".env",
        ".claude/settings.json",
        ".claude/claude.json"
    ]
    
    structure = {
        "directories": {},
        "key_files": {},
        "tech_stack": []
    }
    
    # Check directories
    for dir_path in key_dirs:
        if Path(dir_path).exists():
            try:
                file_count = len(list(Path(dir_path).rglob("*")))
                structure["directories"][dir_path] = {
                    "exists": True,
                    "file_count": file_count
                }
            except:
                structure["directories"][dir_path] = {"exists": True, "file_count": "unknown"}
        else:
            structure["directories"][dir_path] = {"exists": False}
    
    # Check key files
    for file_path in key_files:
        path = Path(file_path)
        if path.exists():
            structure["key_files"][file_path] = {
                "exists": True,
                "size": path.stat().st_size,
                "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat()
            }
        else:
            structure["key_files"][file_path] = {"exists": False}
    
    # Detect tech stack
    if Path("package.json").exists():
        try:
            with open("package.json", 'r') as f:
                pkg = json.load(f)
                
            deps = list(pkg.get("dependencies", {}).keys()) + list(pkg.get("devDependencies", {}).keys())
            
            # Common tech detection
            if "vue" in deps:
                structure["tech_stack"].append("Vue.js")
            if "react" in deps:
                structure["tech_stack"].append("React")
            if "typescript" in deps:
                structure["tech_stack"].append("TypeScript")
            if "bun" in pkg.get("scripts", {}).values() or "bun" in str(pkg):
                structure["tech_stack"].append("Bun")
            if "express" in deps:
                structure["tech_stack"].append("Express")
        except:
            pass
    
    return structure

def get_execution_instructions():
    """Get instructions for running the project"""
    instructions = {
        "server": [],
        "client": [],
        "setup": []
    }
    
    # Check package.json for scripts
    if Path("package.json").exists():
        try:
            with open("package.json", 'r') as f:
                pkg = json.load(f)
            
            scripts = pkg.get("scripts", {})
            
            # Common script patterns
            for script_name, script_cmd in scripts.items():
                if "server" in script_name or "backend" in script_name:
                    instructions["server"].append(f"npm run {script_name}")
                elif "client" in script_name or "frontend" in script_name or "dev" in script_name:
                    instructions["client"].append(f"npm run {script_name}")
                elif "install" in script_name or "setup" in script_name:
                    instructions["setup"].append(f"npm run {script_name}")
        except:
            pass
    
    # Check for specific project files
    if Path("apps/server/src/index.ts").exists():
        instructions["server"].append("cd apps/server && bun run src/index.ts")
    
    if Path("apps/client/package.json").exists():
        instructions["client"].append("cd apps/client && npm run dev")
    
    # Default setup
    if not instructions["setup"]:
        instructions["setup"] = ["npm install", "bun install"]
    
    return instructions

def format_human_report(data):
    """Format report for human consumption"""
    report = []
    report.append("=" * 60)
    report.append("📊 PROJECT STATUS REPORT")
    report.append("=" * 60)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Git Status
    git = data["git_status"]
    if "error" not in git:
        report.append("🔧 GIT STATUS")
        report.append(f"  Branch: {git['current_branch']}")
        report.append(f"  Last Commit: {git['last_commit']}")
        report.append(f"  Uncommitted Changes: {git['uncommitted_changes']} files")
        report.append(f"  Status: {'✅ Clean' if git['clean'] else '⚠️  Has changes'}")
        report.append("")
    
    # Tech Stack
    tech = data["project_structure"]["tech_stack"]
    if tech:
        report.append("💻 TECH STACK")
        for t in tech:
            report.append(f"  • {t}")
        report.append("")
    
    # How to Run
    instructions = data["execution_instructions"]
    report.append("🚀 HOW TO RUN")
    report.append("  Setup:")
    for cmd in instructions["setup"]:
        report.append(f"    $ {cmd}")
    report.append("  Server:")
    for cmd in instructions["server"]:
        report.append(f"    $ {cmd}")
    report.append("  Client:")
    for cmd in instructions["client"]:
        report.append(f"    $ {cmd}")
    report.append("")
    
    # Recent Claude Activity
    claude = data["claude_logs"]
    if claude["recent_sessions"]:
        report.append("🤖 RECENT CLAUDE ACTIVITY")
        for session in claude["recent_sessions"][:3]:
            score = session['completion_score']
            emoji = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
            report.append(f"  {emoji} {session['task_signature']} - Score: {score}/100")
        report.append("")
    
    # Alerts
    if claude.get("alerts"):
        report.append("⚠️  ALERTS")
        for alert in claude["alerts"][:3]:
            report.append(f"  • {alert['message']}")
        report.append("")
    
    # Last Working On
    if git.get("recent_commits"):
        report.append("📝 RECENT WORK")
        for commit in git["recent_commits"][:3]:
            report.append(f"  • {commit}")
        report.append("")
    
    return "\n".join(report)

def format_machine_report(data):
    """Format report for machine consumption (Claude's preference)"""
    # Structured, dense format optimized for AI parsing
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "git_clean": data["git_status"].get("clean", False),
            "uncommitted_changes": data["git_status"].get("uncommitted_changes", 0),
            "avg_claude_score": sum(s["completion_score"] for s in data["claude_logs"]["recent_sessions"]) / len(data["claude_logs"]["recent_sessions"]) if data["claude_logs"]["recent_sessions"] else 0,
            "critical_alerts": len([a for a in data["claude_logs"].get("alerts", []) if a.get("severity") == "critical"]),
            "primary_tech": data["project_structure"]["tech_stack"][:3] if data["project_structure"]["tech_stack"] else []
        },
        "execution": {
            "quick_start": data["execution_instructions"]["server"][0] if data["execution_instructions"]["server"] else "bun run src/index.ts",
            "dependencies_required": not Path("node_modules").exists()
        },
        "focus_areas": [
            alert["message"] for alert in data["claude_logs"].get("alerts", [])[:3]
        ],
        "last_activity": {
            "git": data["git_status"].get("last_commit", ""),
            "claude": data["claude_logs"]["recent_sessions"][0] if data["claude_logs"]["recent_sessions"] else None
        },
        "raw_data": data  # Full data for detailed analysis if needed
    }

def main():
    # Gather all data
    data = {
        "git_status": get_git_status(),
        "claude_logs": get_claude_logs(),
        "project_structure": get_project_structure(),
        "execution_instructions": get_execution_instructions()
    }
    
    # Generate both report formats
    human_report = format_human_report(data)
    machine_report = format_machine_report(data)
    
    # Save reports
    reports_dir = Path(".claude/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save human report
    with open(reports_dir / f"project_status_{timestamp}.txt", 'w') as f:
        f.write(human_report)
    
    # Save machine report
    with open(reports_dir / f"project_status_{timestamp}.json", 'w') as f:
        json.dump(machine_report, f, indent=2)
    
    # Output based on argument
    if len(sys.argv) > 1 and sys.argv[1] == "--machine":
        print(json.dumps(machine_report, indent=2))
    else:
        print(human_report)
        print(f"\n💾 Reports saved to {reports_dir}")

if __name__ == "__main__":
    main()