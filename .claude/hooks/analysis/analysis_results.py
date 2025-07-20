#!/usr/bin/env python3
"""Analysis results hook - placeholder"""
import os
import sys
print(f"Analysis results: {os.environ.get('CLAUDE_TOOL_NAME', 'unknown')}")
sys.exit(0)
