# /governance:budget_guard_10x - Time/Tool Budget Guardrails

## Purpose
Enforce execution budgets for commands; degrade modes (deep → standard → quick) when limits are reached.

## Usage
```bash
/governance:budget_guard_10x --command "/implement_10x --feature \"auth\" --full" --max-seconds 1200 --max-tools 25 --fallback standard
```

## Parameters
- `--max-seconds`: Total wall time budget
- `--max-tools`: Max tool calls
- `--fallback`: quick | standard | skip-phase
- `--on-violation`: warn | abort | degrade

## Integration
- Pre-exec: estimate cost; set counters.
- During exec: enforce ceilings and trigger `--fallback`.
- Post-exec: emit budget report and metrics.