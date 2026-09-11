---
type: community
cohesion: 0.12
members: 16
---

# Community 163

**Cohesion:** 0.12 - loosely connected
**Members:** 16 nodes

## Members
- [[dot-test_fail_safe_disabled_allows_on_failure()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_news_filter.py
- [[dot-test_fail_safe_enabled_blocks_on_failure()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_news_filter.py
- [[dot-test_high_impact_outside_window_allows()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_news_filter.py
- [[dot-test_high_impact_post_event_blocks()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_news_filter.py
- [[dot-test_high_impact_upcoming_blocks()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_news_filter.py
- [[dot-test_medium_impact_does_not_block_but_flags()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_news_filter.py
- [[dot-test_safe_market_no_events()]] - code - Trading/001WM_STRATEGY_BOT/tests/test_news_filter.py
- [[Asserts that a high-impact event 20 minutes ago blocks signals (within 30m…]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_news_filter.py
- [[Asserts that a high-impact event in 15 minutes blocks signals.]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_news_filter.py
- [[Asserts that a high-impact event in 75 minutes does NOT block signals (outside…]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_news_filter.py
- [[Asserts that a medium-impact event does not block signals, but is collected and…]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_news_filter.py
- [[Asserts that when fail-safe is disabled, provider failures do NOT block signals.]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_news_filter.py
- [[Asserts that when fail-safe is enabled, provider failures block signals.]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_news_filter.py
- [[Asserts that when there are no events, signals are allowed and risk is low.]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_news_filter.py
- [[TestNewsFilter]] - code - Trading/001WM_STRATEGY_BOT/tests/test_news_filter.py
- [[Unit tests for the NewsFilter risk engine.]] - rationale - Trading/001WM_STRATEGY_BOT/tests/test_news_filter.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Community_163
SORT file.name ASC
```

## Connections to other communities
- 8 edges to [[_COMMUNITY_Community 153]]
- 2 edges to [[_COMMUNITY_Community 110]]

## Top bridge nodes
- [[TestNewsFilter]] - degree 12, connects to 2 communities
- [[dot-test_fail_safe_disabled_allows_on_failure()]] - degree 3, connects to 1 community
- [[dot-test_fail_safe_enabled_blocks_on_failure()]] - degree 3, connects to 1 community
- [[dot-test_high_impact_outside_window_allows()]] - degree 3, connects to 1 community
- [[dot-test_high_impact_post_event_blocks()]] - degree 3, connects to 1 community