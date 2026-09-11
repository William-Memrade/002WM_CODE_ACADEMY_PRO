---
type: community
cohesion: 0.25
members: 8
---

# Community 250

**Cohesion:** 0.25 - loosely connected
**Members:** 8 nodes

## Members
- [[dot-test_assert_read_only_passes_normally()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_security_no_trading.py
- [[dot-test_assert_read_only_raises_if_sentinel_tampered()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_security_no_trading.py
- [[dot-test_trading_forbidden_is_true()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_security_no_trading.py
- [[Simulates a malicious or accidental TRADING_FORBIDDEN = False scenario.…]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_security_no_trading.py
- [[TRADING_FORBIDDEN must be True. Any False value is a critical misconfiguration.]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_security_no_trading.py
- [[TestReadOnlySentinel]] - code - Trading/001WM_STRATEGY_BOT/tests/test_security_no_trading.py
- [[Verifies that the TRADING_FORBIDDEN sentinel and assert_read_only() guard…]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_security_no_trading.py
- [[assert_read_only() should complete without raising under normal conditions.]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_security_no_trading.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Community_250
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Community 235]]
- 1 edge to [[_COMMUNITY_Community 225]]
- 1 edge to [[_COMMUNITY_Community 32]]

## Top bridge nodes
- [[TestReadOnlySentinel]] - degree 6, connects to 2 communities
- [[dot-test_assert_read_only_passes_normally()]] - degree 3, connects to 1 community