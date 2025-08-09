#!/usr/bin/env python3
import json
import os
import sys
from typing import Any, Dict

# Minimal schema validator stub (extend to load per-command schemas)
try:
    import jsonschema  # type: ignore
except Exception:
    jsonschema = None

def main() -> int:
    # In a real integration, receive payload via stdin or env
    payload = os.environ.get("CLAUDE_HOOK_PAYLOAD", "{}")
    try:
        data: Dict[str, Any] = json.loads(payload)
    except Exception:
        print("[schema-validator] No/invalid payload; skipping", file=sys.stderr)
        return 0

    command = data.get("command", "")
    # TODO: load schema by command name
    schema = None
    if jsonschema and schema:
        try:
            jsonschema.validate(instance=data.get("input", {}), schema=schema)
        except Exception as e:
            print(f"[schema-validator] Validation error for {command}: {e}", file=sys.stderr)
            # Fail closed only in strict mode
    else:
        print("[schema-validator] No schema; pass", file=sys.stderr)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())