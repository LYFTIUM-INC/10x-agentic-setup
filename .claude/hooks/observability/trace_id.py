#!/usr/bin/env python3
import os
import sys
import uuid

TRACE_ENV = "CLAUDE_TRACE_ID"

def main() -> int:
    trace_id = os.environ.get(TRACE_ENV)
    if not trace_id:
        trace_id = uuid.uuid4().hex[:16]
        print(f"[trace] generated {trace_id}", file=sys.stderr)
    else:
        print(f"[trace] propagate {trace_id}", file=sys.stderr)
    # In a full integration, export this to subsequent tool envs
    return 0

if __name__ == "__main__":
    raise SystemExit(main())