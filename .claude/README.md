# Claude Sub-Agent Performance Analysis System

## Overview

This system uses Claude Code's built-in sub-agent capabilities to intelligently track, analyze, and improve task completion performance. No external API calls or rule-based logic - pure Claude intelligence.

## How It Works

### 1. **Goal Analysis (UserPromptSubmit Hook)**
- **Trigger**: Every time you submit a prompt
- **Agent**: `goal_analyzer.py`
- **Actions**:
  - Creates unique task signature for similarity detection
  - Tracks repeated attempts of similar tasks
  - Saves analysis to `.claude/data/sessions/{session_id}_goal_analysis.json`
  - Updates task history in `.claude/data/task_history_{signature}.json`

### 2. **Execution Tracking (PostToolUse Hook)**
- **Trigger**: After every tool use (Read, Write, Bash, etc.)
- **Agent**: `execution_tracker.py`
- **Actions**:
  - Tracks tools used, files modified, commands executed
  - Detects code creation, test running, dependency installation
  - Records errors and meaningful outputs
  - Saves to `.claude/data/sessions/{session_id}_execution_log.json`

### 3. **Performance Analysis (Stop Hook)**
- **Trigger**: When Claude session ends
- **Agent**: `performance_analyzer.py`
- **Actions**:
  - **Actually tests** if code compiles/runs
  - Verifies syntax, runs tests if possible
  - Calculates objective completion score (0-100)
  - Updates performance history for repeated tasks
  - **Detects user dissatisfaction** when tasks are repeated
  - Saves to `.claude/data/sessions/{session_id}_performance_report.json`

## Key Features

### 🔍 **Intelligent Task Recognition**
```bash
# Same task attempted multiple times gets flagged
⚠️ Warning: Similar task attempted 3 times
🚨 USER LIKELY UNSATISFIED - Consider alternative approach
```

### 🧪 **Actual Code Verification**
- Compiles JavaScript/TypeScript with Node.js
- Compiles Python with py_compile
- Checks for syntax errors
- Monitors test execution results

### 📊 **Objective Scoring System**
```
📊 Completion Score: 85.2/100
✅ Code compiles/parses correctly (+15)
✅ No syntax errors (+15)
✅ Tests pass (+20)
✅ Functionality appears to work (+20)
✅ Code was created (+10)
⚠️ Performance concerns (-10)
```

### 📈 **Pattern Recognition**
- Tracks declining performance on repeated tasks
- Identifies user dissatisfaction patterns
- Flags tasks that consistently fail

## File Structure

```
.claude/
├── claude.json                    # Hook configuration
├── hooks/
│   ├── goal_analyzer.py          # Intent analysis
│   ├── execution_tracker.py      # Real-time tracking
│   └── performance_analyzer.py   # Completion analysis
├── commands/
│   └── performance_insights.py   # On-demand insights
└── data/
    ├── sessions/                  # Per-session data
    │   ├── {session}_goal_analysis.json
    │   ├── {session}_execution_log.json
    │   └── {session}_performance_report.json
    ├── task_history_{sig}.json   # Task repetition tracking
    ├── performance_history_{sig}.json  # Performance trends
    └── performance_insights.json # Generated insights
```

## Usage

### Automatic Operation
Once configured, the system works automatically:
1. Submit any prompt → Goal analysis begins
2. Use tools → Execution tracking continues  
3. End session → Performance analysis runs

### Manual Insights Generation
```bash
python3 .claude/commands/performance_insights.py
```

### Sample Output
```
🎯 CLAUDE SUB-AGENT PERFORMANCE INSIGHTS
==================================================
📊 Overall Performance:
   Total Tasks: 15
   Repeated Tasks: 4
   Avg Completion Score: 78.3/100
   User Satisfaction Concerns: 2

🚨 IMMEDIATE ALERTS:
   🔴 Task 'implement login system...' failing repeatedly (avg: 45.2)
      → Consider alternative implementation strategy
   🔴 User persistently unsatisfied with task 'fix database connection...'
      → Manual review required - may need human intervention

🔄 MOST REPEATED TASKS:
   🔴 fix database connection issue... (4 attempts, 52.1 avg)
   🟡 implement user authentication... (3 attempts, 73.5 avg)
   🟢 create React component... (2 attempts, 89.2 avg)

💡 RECOMMENDATIONS:
   🔴 Task repeated 4 times with low avg score (52.1)
      → Consider fundamentally different approach or break into smaller subtasks
   🟠 Overall completion score is low (78.3)
      → Review common failure patterns and improve verification processes
```

## Benefits Over Rule-Based Systems

### ❌ **What We Removed:**
- External API calls to Claude
- Rule-based if/then logic
- Pattern matching with regex
- Statistical correlation calculations
- Predefined recommendation templates

### ✅ **What We Gained:**
- **Native Claude Intelligence**: Uses your Claude Code subscription directly
- **Actual Code Testing**: Runs real verification checks
- **Local Data Storage**: Everything saved locally in JSON
- **Task Signature Detection**: Identifies similar tasks intelligently
- **Performance Degradation Tracking**: Notices when repeated tasks get worse scores
- **User Dissatisfaction Detection**: Flags when users keep asking for the same thing

## Advanced Features

### Task Similarity Detection
```python
# Creates unique signatures for similar tasks
def create_task_signature(prompt):
    normalized = prompt.lower().strip()
    normalized = normalized.replace("please", "").replace("can you", "")
    return hashlib.md5(normalized.encode()).hexdigest()[:12]
```

### Performance Trend Analysis
```json
{
  "trend": "declining",
  "user_satisfaction_pattern": "user_unsatisfied_persistent",
  "attempts": [
    {"completion_score": 85.0},
    {"completion_score": 72.3}, 
    {"completion_score": 58.1}
  ]
}
```

### Real Verification Testing
- Syntax checking with language compilers
- Test execution monitoring
- Error pattern detection
- Output analysis for success indicators

This system provides **genuine intelligence** about task completion using Claude's reasoning capabilities while maintaining **complete local control** over data and analysis.