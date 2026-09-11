---
source_file: "Trading/001WM_STRATEGY_BOT/app/execution/execution_levels.py"
type: "code"
community: "Community 10"
location: "L37"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Community_10
---

# build_execution_levels()

## Connections
- [[dot-test_buy_uses_recent_swing_low_minus_atr_buffer()]] - `calls` [EXTRACTED]
- [[dot-test_h1_h4_are_never_used_for_execution_levels_by_default()]] - `calls` [EXTRACTED]
- [[dot-test_h4_h1_bearish_with_m5_swing_builds_sell_sl_from_m5()]] - `calls` [EXTRACTED]
- [[dot-test_h4_h1_bullish_with_m5_swing_builds_buy_sl_from_m5()]] - `calls` [EXTRACTED]
- [[dot-test_missing_m5_and_m15_blocks_without_using_h1_h4()]] - `calls` [EXTRACTED]
- [[dot-test_missing_m5_uses_m15_fallback()]] - `calls` [EXTRACTED]
- [[dot-test_recalculated_m5_sl_1_blocks_by_min_distance()]] - `calls` [EXTRACTED]
- [[dot-test_recalculated_m5_sl_above_20_blocks_by_max_distance()]] - `calls` [EXTRACTED]
- [[dot-test_sell_uses_recent_swing_high_plus_atr_buffer()]] - `calls` [EXTRACTED]
- [[dot-test_signal_original_sl_52_but_recalculated_m5_sl_8_allows_continue()]] - `calls` [EXTRACTED]
- [[dot-test_tp1_and_tp2_use_r_multiples()]] - `calls` [EXTRACTED]
- [[dot-test_tp1_is_capped_to_35_usd()]] - `calls` [EXTRACTED]
- [[dot-test_wide_m5_swing_rebuilds_from_m1()]] - `calls` [EXTRACTED]
- [[001WM_STRATEGY_BOTappmain.py]] - `imports` [EXTRACTED]
- [[Any_8]] - `references` [EXTRACTED]
- [[Build executable M15M5M1 levels without using H4H1 SLTP structure.]] - `rationale_for` [EXTRACTED]
- [[DataFrame_3]] - `references` [EXTRACTED]
- [[ExecutionLevels]] - `references` [EXTRACTED]
- [[SignalCandidate]] - `uses` [INFERRED]
- [[_blocked_levels()]] - `calls` [EXTRACTED]
- [[_build_first_valid_candidate()]] - `calls` [EXTRACTED]
- [[_handle_auto_execution()]] - `calls` [EXTRACTED]
- [[_overlay_execution_config()]] - `calls` [EXTRACTED]
- [[execution_levels.py]] - `contains` [EXTRACTED]
- [[resolve_symbol_config()]] - `calls` [EXTRACTED]
- [[test_eurusd_execution_levels_allow_0_00200_distance()]] - `calls` [EXTRACTED]
- [[test_execution.py]] - `imports` [EXTRACTED]
- [[test_symbol_config.py]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Community_10