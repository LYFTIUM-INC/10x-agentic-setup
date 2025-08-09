#!/usr/bin/env python3
import json
import os
import sys
import time

MAX_SECONDS = int(os.environ.get("BUDGET_MAX_SECONDS", "0")) or None
MAX_TOOLS = int(os.environ.get("BUDGET_MAX_TOOLS", "0")) or None
FALLBACK = os.environ.get("BUDGET_FALLBACK", "standard")

STATE_FILE = os.environ.get("BUDGET_STATE_FILE", ".claude/.budget_state.json")


def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"start": time.time(), "tools": 0}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def main() -> int:
    state = load_state()
    now = time.time()
    state.setdefault("start", now)
    # Increment tool count
    state["tools"] = int(state.get("tools", 0)) + 1

    # Enforce budgets if configured
    if MAX_SECONDS and now - state["start"] > MAX_SECONDS:
        print(f"[budget-guard] Time budget exceeded; suggest fallback={FALLBACK}", file=sys.stderr)
    if MAX_TOOLS and state["tools"] > MAX_TOOLS:
        print(f"[budget-guard] Tool budget exceeded; suggest fallback={FALLBACK}", file=sys.stderr)

    save_state(state)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())