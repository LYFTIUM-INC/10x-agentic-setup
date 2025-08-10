import os
import json
import tempfile
from pathlib import Path
import importlib.util
import types

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / ".claude" / "schemas"
BUDGET_STATE = ROOT / ".claude" / ".budget_state.json"


def load_module(path: Path) -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)  # type: ignore
    return mod


def test_schema_validator_pass(tmp_path: Path):
    SCHEMA_DIR.mkdir(parents=True, exist_ok=True)
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {"target": {"type": "string"}},
        "required": ["target"],
        "additionalProperties": True,
    }
    with open(SCHEMA_DIR / "analyze_10x.json", "w") as f:
        json.dump(schema, f)

    payload = {"command": "/analyze_10x", "input": {"target": "repo"}}
    os.environ["CLAUDE_HOOK_PAYLOAD"] = json.dumps(payload)
    os.environ["SCHEMA_VALIDATION_STRICT"] = "false"

    mod = load_module(ROOT / ".claude" / "hooks" / "governance" / "schema_validator.py")
    rc = mod.main()
    assert rc == 0


def test_schema_validator_strict_fail(tmp_path: Path):
    SCHEMA_DIR.mkdir(parents=True, exist_ok=True)
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {"target": {"type": "string"}},
        "required": ["target"],
        "additionalProperties": True,
    }
    with open(SCHEMA_DIR / "analyze_10x.json", "w") as f:
        json.dump(schema, f)

    payload = {"command": "/analyze_10x", "input": {}}
    os.environ["CLAUDE_HOOK_PAYLOAD"] = json.dumps(payload)
    os.environ["SCHEMA_VALIDATION_STRICT"] = "true"

    mod = load_module(ROOT / ".claude" / "hooks" / "governance" / "schema_validator.py")
    rc = mod.main()
    assert rc == 1


def test_budget_guard_state_increments(tmp_path: Path):
    if BUDGET_STATE.exists():
        BUDGET_STATE.unlink()
    os.environ.pop("BUDGET_MAX_SECONDS", None)
    os.environ.pop("BUDGET_MAX_TOOLS", None)
    os.environ["BUDGET_STATE_FILE"] = str(BUDGET_STATE)

    mod = load_module(ROOT / ".claude" / "hooks" / "governance" / "budget_guard.py")
    rc1 = mod.main()
    rc2 = mod.main()
    assert rc1 == 0 and rc2 == 0
    assert BUDGET_STATE.exists()
    state = json.loads(BUDGET_STATE.read_text())
    assert int(state.get("tools", 0)) >= 2