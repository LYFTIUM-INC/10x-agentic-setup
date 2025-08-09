# /orchestration:plan_and_run_10x - Planner + Parallel Executor

## Purpose
Plan complex tasks into a directed acyclic graph (DAG) of steps with explicit dependencies, then execute with parallel fan‑out/fan‑in, retries, and guardrails.

## Usage
```bash
/orchestration:plan_and_run_10x \
  --target "migrate auth to JWT" \
  --parallel 5 \
  --sync at:validate \
  --retry policy:exponential,max:2 \
  --reflexion lite \
  --budget-guard --max-seconds 900
```

## Standard Flags
- `--plan-only`: Emit DAG without executing
- `--parallel <N>`: Max concurrent sub-steps
- `--sync at:<phase>`: Force sync barrier at phase(s) (e.g., validate, test)
- `--retry policy:<fixed|exponential>,max:<n>`: Retry policy for failing nodes
- `--reflexion <none|lite|full>`: Insert self‑critique checkpoints
- `--budget-guard --max-seconds <t> --max-tools <k>`: Enforce time/tool ceilings
- `--trace-id <id>`: Propagate trace for observability

## Planning Template (DAG)
- Nodes: {id, title, description, inputs, outputs, cost_estimate, risk}
- Edges: {from, to, rationale}
- Phases: analyze → design → implement → test → validate → document

## Execution Rules
1. Resolve independent nodes and execute in parallel (`--parallel`).
2. Insert sync barriers at `--sync` phases.
3. On failure: apply `--retry` and/or alternate strategy; if budget exceeded, degrade depth.
4. Aggregate artifacts with lineage and metrics; store under `Knowledge/`.

## Notes
- Emits a machine‑readable `dag.json` for audit and re‑runs.
- Delegates to specialized commands (`/analyze_10x`, `/implement_10x`, `/qa:comprehensive_10x`, `/docs:generate_docs_10x`).