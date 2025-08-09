# /eval:agent_bench_10x - Agent Evaluation Harness

## Purpose
Benchmark agent workflows on a curated suite (quick/core/full) and report solve rate, latency, retries, failures, and parallel efficiency.

## Usage
```bash
/eval:agent_bench_10x --suite quick --report junit --compare latest
```

## Suite Levels
- `quick`: 5 tasks, sanity
- `core`: 20 tasks, representative
- `full`: 100+ tasks, nightly

## Metrics
- Solve rate, avg/p95 latency, retry count, tool failure rate, cache hit rate, parallel efficiency.

## Output
- `Knowledge/quality/agent_bench_[timestamp].json` + optional JUnit XML