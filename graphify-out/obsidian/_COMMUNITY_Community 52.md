---
type: community
cohesion: 0.10
members: 36
---

# Community 52

**Cohesion:** 0.10 - loosely connected
**Members:** 36 nodes

## Members
- [[dot-__init__()_87]] - code - Trading/001WM_STRATEGY_BOT/app/backtesting/data_loader.py
- [[dot-_dict_to_record()]] - code - Trading/001WM_STRATEGY_BOT/app/backtesting/data_loader.py
- [[dot-_passes_filters()]] - code - Trading/001WM_STRATEGY_BOT/app/backtesting/data_loader.py
- [[dot-_resolve()]] - code - Trading/001WM_STRATEGY_BOT/app/backtesting/data_loader.py
- [[dot-_validate_price_df()]] - code - Trading/001WM_STRATEGY_BOT/app/backtesting/data_loader.py
- [[dot-load_price_data()]] - code - Trading/001WM_STRATEGY_BOT/app/backtesting/data_loader.py
- [[dot-load_signals_from_csv()]] - code - Trading/001WM_STRATEGY_BOT/app/backtesting/data_loader.py
- [[dot-load_signals_from_jsonl()]] - code - Trading/001WM_STRATEGY_BOT/app/backtesting/data_loader.py
- [[dot-risk_points_raw()]] - code - Trading/001WM_STRATEGY_BOT/app/backtesting/models.py
- [[dot-theoretical_tp1_r()]] - code - Trading/001WM_STRATEGY_BOT/app/backtesting/models.py
- [[dot-theoretical_tp2_r()]] - code - Trading/001WM_STRATEGY_BOT/app/backtesting/models.py
- [[A trading signal enriched with all data required for backtesting replay. This…]] - rationale - Trading/001WM_STRATEGY_BOT/app/backtesting/models.py
- [[Args base_dir Project root path. Auto-detected from file location if None.]] - rationale - Trading/001WM_STRATEGY_BOT/app/backtesting/data_loader.py
- [[BacktestSignalRecord]] - code - Trading/001WM_STRATEGY_BOT/app/backtesting/models.py
- [[Converts a raw dict (from JSONL or CSV) into a BacktestSignalRecord. Gracefully…]] - rationale - Trading/001WM_STRATEGY_BOT/app/backtesting/data_loader.py
- [[DataFrame_25]] - code
- [[Historical data loading utilities for the backtesting framework. Handles -…]] - rationale - Trading/001WM_STRATEGY_BOT/app/backtesting/data_loader.py
- [[HistoricalDataLoader]] - code - Trading/001WM_STRATEGY_BOT/app/backtesting/data_loader.py
- [[Loads OHLCV price data from a CSV or Parquet file for use in replay. Required…]] - rationale - Trading/001WM_STRATEGY_BOT/app/backtesting/data_loader.py
- [[Loads and transforms historical signal records and OHLCV price data for use in…]] - rationale - Trading/001WM_STRATEGY_BOT/app/backtesting/data_loader.py
- [[Loads signal records from a CSV file (SignalStore format). Arguments are…]] - rationale - Trading/001WM_STRATEGY_BOT/app/backtesting/data_loader.py
- [[Loads signal records from a JSONL file (SignalStore format). Args path Path…]] - rationale - Trading/001WM_STRATEGY_BOT/app/backtesting/data_loader.py
- [[Path_20]] - code
- [[Resolve relative paths from the project base directory.]] - rationale - Trading/001WM_STRATEGY_BOT/app/backtesting/data_loader.py
- [[Return a pandas UTC timestamp for safe comparisons with UTC-aware series.]] - rationale - Trading/001WM_STRATEGY_BOT/app/backtesting/data_loader.py
- [[Return a timezone-aware UTC datetime, treating naive values as UTC.]] - rationale - Trading/001WM_STRATEGY_BOT/app/backtesting/data_loader.py
- [[Returns True if the record passes all applied filters.]] - rationale - Trading/001WM_STRATEGY_BOT/app/backtesting/data_loader.py
- [[Risk in points from entry to SL, pre-slippage.]] - rationale - Trading/001WM_STRATEGY_BOT/app/backtesting/models.py
- [[Theoretical R-multiple to TP1 (pre-slippage).]] - rationale - Trading/001WM_STRATEGY_BOT/app/backtesting/models.py
- [[Theoretical R-multiple to TP2 (pre-slippage).]] - rationale - Trading/001WM_STRATEGY_BOT/app/backtesting/models.py
- [[Timestamp_2]] - code
- [[Validates schema, normalizes 'time' column, casts OHLC to float.]] - rationale - Trading/001WM_STRATEGY_BOT/app/backtesting/data_loader.py
- [[_to_utc_datetime()]] - code - Trading/001WM_STRATEGY_BOT/app/backtesting/data_loader.py
- [[_to_utc_timestamp()_1]] - code - Trading/001WM_STRATEGY_BOT/app/backtesting/data_loader.py
- [[data_loader.py]] - code - Trading/001WM_STRATEGY_BOT/app/backtesting/data_loader.py
- [[datetime_24]] - code

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Community_52
SORT file.name ASC
```

## Connections to other communities
- 9 edges to [[_COMMUNITY_Community 50]]
- 8 edges to [[_COMMUNITY_Community 62]]
- 4 edges to [[_COMMUNITY_Community 175]]
- 3 edges to [[_COMMUNITY_Community 222]]
- 2 edges to [[_COMMUNITY_Community 111]]
- 2 edges to [[_COMMUNITY_Community 224]]
- 2 edges to [[_COMMUNITY_Community 249]]
- 2 edges to [[_COMMUNITY_Community 5]]
- 1 edge to [[_COMMUNITY_Community 49]]
- 1 edge to [[_COMMUNITY_Community 223]]

## Top bridge nodes
- [[BacktestSignalRecord]] - degree 30, connects to 7 communities
- [[data_loader.py]] - degree 13, connects to 3 communities
- [[HistoricalDataLoader]] - degree 15, connects to 2 communities
- [[datetime_24]] - degree 8, connects to 1 community
- [[dot-_dict_to_record()]] - degree 7, connects to 1 community