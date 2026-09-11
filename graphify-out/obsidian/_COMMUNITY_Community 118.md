---
type: community
cohesion: 0.20
members: 21
---

# Community 118

**Cohesion:** 0.20 - loosely connected
**Members:** 21 nodes

## Members
- [[dot-_compute_derived()]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/metrics_exporter.py
- [[dot-_compute_loss_streak()]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/metrics_exporter.py
- [[dot-_ensure_symbol()]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/metrics_exporter.py
- [[dot-_read_execution_journal()]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/metrics_exporter.py
- [[dot-_read_jsonl()]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/metrics_exporter.py
- [[dot-_read_trade_entries()]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/metrics_exporter.py
- [[dot-_read_trade_results()]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/metrics_exporter.py
- [[dot-_to_float()]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/metrics_exporter.py
- [[dot-export_to_prometheus()]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/metrics_exporter.py
- [[dot-get_all_metrics()]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/metrics_exporter.py
- [[dot-get_global_metrics()]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/metrics_exporter.py
- [[dot-get_symbol_metrics()]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/metrics_exporter.py
- [[dot-refresh()]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/metrics_exporter.py
- [[dot-should_refresh()]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/metrics_exporter.py
- [[Count consecutive losses at the end of the trade history.]] - rationale - Trading/001WM_STRATEGY_BOT/app/monitoring/metrics_exporter.py
- [[Legacy fallback read trade_results.jsonl only when trade_entries.jsonl is…]] - rationale - Trading/001WM_STRATEGY_BOT/app/monitoring/metrics_exporter.py
- [[Re-read files and recompute all metrics.]] - rationale - Trading/001WM_STRATEGY_BOT/app/monitoring/metrics_exporter.py
- [[Read the canonical trade_entries.jsonl (single source of truth).]] - rationale - Trading/001WM_STRATEGY_BOT/app/monitoring/metrics_exporter.py
- [[Reads JSONL trade files and aggregates metrics per symbol.]] - rationale - Trading/001WM_STRATEGY_BOT/app/monitoring/metrics_exporter.py
- [[SymbolMetrics]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/metrics_exporter.py
- [[TradeMetricsCollector]] - code - Trading/001WM_STRATEGY_BOT/app/monitoring/metrics_exporter.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Community_118
SORT file.name ASC
```

## Connections to other communities
- 9 edges to [[_COMMUNITY_Community 136]]
- 5 edges to [[_COMMUNITY_Community 296]]
- 1 edge to [[_COMMUNITY_Community 90]]

## Top bridge nodes
- [[TradeMetricsCollector]] - degree 23, connects to 3 communities
- [[dot-refresh()]] - degree 9, connects to 1 community
- [[SymbolMetrics]] - degree 7, connects to 1 community
- [[dot-_read_trade_entries()]] - degree 7, connects to 1 community
- [[dot-_read_trade_results()]] - degree 7, connects to 1 community