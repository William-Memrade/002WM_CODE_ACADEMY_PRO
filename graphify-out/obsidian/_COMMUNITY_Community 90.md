---
type: community
cohesion: 0.11
members: 27
---

# Community 90

**Cohesion:** 0.11 - loosely connected
**Members:** 27 nodes

## Members
- [[dot-__init__()_106]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/prometheus_bridge.py
- [[dot-__new__()]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/prometheus_bridge.py
- [[dot-_ensure_state()]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/prometheus_bridge.py
- [[dot-_push_gauges()]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/prometheus_bridge.py
- [[dot-_rebuild_pnl_from_journal()]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/prometheus_bridge.py
- [[dot-_setup_metrics()]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/prometheus_bridge.py
- [[dot-get_metrics_body()]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/prometheus_bridge.py
- [[dot-record_execution()]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/prometheus_bridge.py
- [[dot-record_trade_closed()]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/prometheus_bridge.py
- [[dot-record_trade_filled()]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/prometheus_bridge.py
- [[dot-set_signal_score()]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/prometheus_bridge.py
- [[dot-setup_prometheus()]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/metrics_exporter.py
- [[dot-start_server()]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/prometheus_bridge.py
- [[dot-stop_server()]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/prometheus_bridge.py
- [[dot-sync_open_positions_from_mt5()]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/prometheus_bridge.py
- [[Any_54]] - code
- [[Call after every execution decision (approved, blocked, sent, filled).]] - rationale - Trading/001WM_STRATEGY_BOT/app/monitoring/prometheus_bridge.py
- [[Call when a trade closes (win, loss, breakeven).]] - rationale - Trading/001WM_STRATEGY_BOT/app/monitoring/prometheus_bridge.py
- [[Call when a trade is successfully filled (market or pending).]] - rationale - Trading/001WM_STRATEGY_BOT/app/monitoring/prometheus_bridge.py
- [[CollectorRegistry]] - code
- [[PrometheusBridge]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/prometheus_bridge.py
- [[Query MT5 for currently open positions and register them in the bridge. Call…]] - rationale - Trading/001WM_STRATEGY_BOT/app/monitoring/prometheus_bridge.py
- [[Rebuild cumulative P&L, winlossclose-reason gauges from the journal. The…]] - rationale - Trading/001WM_STRATEGY_BOT/app/monitoring/prometheus_bridge.py
- [[Return the current Prometheus exposition format.]] - rationale - Trading/001WM_STRATEGY_BOT/app/monitoring/prometheus_bridge.py
- [[Singleton bridge that holds metrics state and exposes them via HTTP.]] - rationale - Trading/001WM_STRATEGY_BOT/app/monitoring/prometheus_bridge.py
- [[Update the last signal score gauge.]] - rationale - Trading/001WM_STRATEGY_BOT/app/monitoring/prometheus_bridge.py
- [[_SymbolState]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/prometheus_bridge.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Community_90
SORT file.name ASC
```

## Connections to other communities
- 9 edges to [[_COMMUNITY_Community 207]]
- 2 edges to [[_COMMUNITY_Community 5]]
- 1 edge to [[_COMMUNITY_Community 118]]

## Top bridge nodes
- [[PrometheusBridge]] - degree 21, connects to 2 communities
- [[dot-_ensure_state()]] - degree 10, connects to 1 community
- [[dot-_push_gauges()]] - degree 7, connects to 1 community
- [[dot-_rebuild_pnl_from_journal()]] - degree 4, connects to 1 community
- [[_SymbolState]] - degree 3, connects to 1 community