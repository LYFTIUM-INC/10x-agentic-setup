#!/usr/bin/env python3
"""Context analyzer hook - placeholder"""
import os
import sys
print(f"Context analysis: {os.environ.get('CLAUDE_TOOL_NAME', 'unknown')}")
sys.exit(0)
