---
type: community
cohesion: 0.20
members: 11
---

# Community 207

**Cohesion:** 0.20 - loosely connected
**Members:** 11 nodes

## Members
- [[dot-_get_metrics_start_time()]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/prometheus_bridge.py
- [[dot-_rebuild_counters_from_journal()]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/prometheus_bridge.py
- [[dot-_rebuild_daily_metrics_from_journal()]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/prometheus_bridge.py
- [[dot-bootstrap_from_journal()]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/prometheus_bridge.py
- [[dot-refresh_from_grafana_if_stale()]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/prometheus_bridge.py
- [[Re-read the Grafana trade-entries file if it was modified since last check.…]] - rationale - Trading/001WM_STRATEGY_BOT/app/monitoring/prometheus_bridge.py
- [[Reconstruct bridge state from the Grafana trade-entries file. The Grafana file…]] - rationale - Trading/001WM_STRATEGY_BOT/app/monitoring/prometheus_bridge.py
- [[Reconstruct daily_trades and daily_pnl from the execution journal. The bridge…]] - rationale - Trading/001WM_STRATEGY_BOT/app/monitoring/prometheus_bridge.py
- [[Replay the execution journal into Prometheus Counters. Counters are monotonic…]] - rationale - Trading/001WM_STRATEGY_BOT/app/monitoring/prometheus_bridge.py
- [[Return the timestamp from which metrics should be accumulated. The first time…]] - rationale - Trading/001WM_STRATEGY_BOT/app/monitoring/prometheus_bridge.py
- [[datetime_15]] - code

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Community_207
SORT file.name ASC
```

## Connections to other communities
- 9 edges to [[_COMMUNITY_Community 90]]
- 1 edge to [[_COMMUNITY_Community 5]]

## Top bridge nodes
- [[dot-bootstrap_from_journal()]] - degree 7, connects to 1 community
- [[dot-_get_metrics_start_time()]] - degree 7, connects to 1 community
- [[dot-_rebuild_daily_metrics_from_journal()]] - degree 4, connects to 1 community
- [[dot-_rebuild_counters_from_journal()]] - degree 3, connects to 1 community
- [[dot-refresh_from_grafana_if_stale()]] - degree 3, connects to 1 community