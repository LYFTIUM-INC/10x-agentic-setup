#!/usr/bin/env python3
"""QA aggregation hook - placeholder"""
import os
import sys
print(f"QA aggregation: {os.environ.get('CLAUDE_TOOL_NAME', 'unknown')}")
sys.exit(0)
