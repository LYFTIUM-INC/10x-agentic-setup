#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

# Minimal schema validator stub (extend to load per-command schemas)
try:
    import jsonschema  # type: ignore
except Exception:
    jsonschema = None

SCHEMA_DIR = Path(".claude/schemas")
STRICT = os.environ.get("SCHEMA_VALIDATION_STRICT", "false").lower() == "true"


def load_schema(command: str):
    fname = command.strip("/").replace(":", "_").replace("/", "_") + ".json"
    path = SCHEMA_DIR / fname
    if path.exists():
        with open(path, "r") as f:
            return json.load(f)
    return None


def main() -> int:
    # In a real integration, receive payload via stdin or env
    payload = os.environ.get("CLAUDE_HOOK_PAYLOAD", "{}")
    try:
        data: Dict[str, Any] = json.loads(payload)
    except Exception:
        print("[schema-validator] No/invalid payload; skipping", file=sys.stderr)
        return 0

    command = (data.get("command") or "").strip()
    schema = load_schema(command) if jsonschema else None
    if schema and jsonschema:
        try:
            jsonschema.validate(instance=data.get("input", {}), schema=schema)
            print(f"[schema-validator] {command} input ok", file=sys.stderr)
        except Exception as e:
            print(f"[schema-validator] Validation error for {command}: {e}", file=sys.stderr)
            if STRICT:
                return 1
    else:
        print(f"[schema-validator] No schema for {command}; pass", file=sys.stderr)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())