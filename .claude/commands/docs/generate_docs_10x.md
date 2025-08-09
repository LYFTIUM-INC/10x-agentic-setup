# /docs:generate_docs_10x - Unified Documentation Orchestrator

## Purpose
Create comprehensive, multi-audience documentation using granular scopes, ML-enhanced analysis, and knowledge storage. Acts as the high-level entrypoint and delegates to `/docs:granular_10x` for scoped generation.

## Recommended Usage
```bash
# Full project docs (summary + key APIs)
/docs:generate_docs_10x --mode standard --targets "src/**" --include-apis --store

# Deep API docs for critical modules
/docs:generate_docs_10x --mode api --targets "src/core/**" --depth detailed --store --ml

# Post-implementation docs refresh
/docs:generate_docs_10x --mode changed-only --git --store
```

## Parameters
- `--mode`: standard | api | quick | changed-only
- `--targets`: glob(s) or list of paths; with `--git` uses changed files
- `--depth`: summary | standard | detailed | api
- `--ml`: enable ML enhancements (patterns, concept linking)
- `--store`: persist outputs under `Knowledge/documentation/granular/`
- `--git`: detect changed files and functions to document
- `--audience`: developer | api-user | maintainer

## Orchestration Plan
1. Resolve targets (glob or git-changed if `--git`).
2. For each target, invoke `/docs:granular_10x` with appropriate scope:
   - Files → `--scope file`
   - Functions/classes (detected via code intelligence) → `--scope function|class`
   - Modules/directories → `--scope module`
3. Run parallel sub-requests where possible to accelerate generation.
4. When `--ml` is set, enable:
   - `extract-patterns`, `link-concepts`, `auto-categorize`.
5. If `--store`, write outputs to `Knowledge/documentation/granular/` per structure below.

## Storage Structure
```
Knowledge/documentation/granular/
├── files/[file-hash]/(full.md|summary.md|metadata.json)
├── functions/[function-name]/(doc.md|examples.md|usage-patterns.json)
├── modules/[module-name]/(overview.md|api.md)
└── findings/[source-hash]/(findings.md|ml-data.json)
```

## Integration
- During `/implement_10x`: auto-run with `--mode changed-only --git --store`.
- During `/qa:comprehensive_10x`: run with `--mode api --targets tests/** --store`.
- During `/workflows/feature_workflow_10x`: run in finalization phase.

## Notes
- Uses the same parameter schema as `/docs:granular_10x` where applicable.
- Prefer `/docs:granular_10x` for precise control; use this command for end-to-end orchestration.
