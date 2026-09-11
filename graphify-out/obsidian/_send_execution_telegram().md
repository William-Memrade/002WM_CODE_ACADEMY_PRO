---
source_file: "Trading/001WM_STRATEGY_BOT/app/main.py"
type: "code"
community: "Community 28"
location: "L522"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Community_28
---

# _send_execution_telegram()

## Connections
- [[001WM_STRATEGY_BOTappmain.py]] - `contains` [EXTRACTED]
- [[Send an execution alert to Telegram if the matching flag is enabled.]] - `rationale_for` [EXTRACTED]
- [[TelegramNotifier]] - `uses` [INFERRED]
- [[_extract_blocked_reason()]] - `calls` [EXTRACTED]
- [[_handle_auto_execution()]] - `calls` [EXTRACTED]
- [[_should_send_blocked_telegram()]] - `calls` [EXTRACTED]
- [[_should_send_pending_telegram()]] - `calls` [EXTRACTED]
- [[run_cycle()]] - `calls` [EXTRACTED]
- [[test_auto_trade_filled_sends_message()]] - `calls` [EXTRACTED]
- [[test_blocked_open_position_limit_not_sent_to_telegram()]] - `calls` [EXTRACTED]
- [[test_pending_order_blocked_sends_message()]] - `calls` [EXTRACTED]
- [[test_pending_order_placed_not_sent_when_only_filled_and_important()]] - `calls` [EXTRACTED]
- [[test_pending_order_placed_sends_message()]] - `calls` [EXTRACTED]
- [[test_repeated_critical_blocked_is_deduped()]] - `calls` [EXTRACTED]
- [[test_technical_log_text_is_not_sent_by_router()]] - `calls` [EXTRACTED]
- [[test_telegram_notifications.py]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Community_28