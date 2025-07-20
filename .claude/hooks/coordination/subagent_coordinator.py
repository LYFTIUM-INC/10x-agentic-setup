#!/usr/bin/env python3
"""Subagent coordinator hook - placeholder"""
import os
import sys
print(f"Subagent coordination: {os.environ.get('CLAUDE_TOOL_NAME', 'unknown')}")
sys.exit(0)
