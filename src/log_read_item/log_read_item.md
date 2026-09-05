purpose: read every gate event recorded against a work item, in order
signature: log_read_item(item_id: str) -> list[dict]
inputs: item_id: the target item.
outputs: list of dicts, one per matching event, sorted by created_at: {'id', 'ts' (created_at), 'actor', 'gate' (event_kind), 'item' (target)} merged with payload keys rule, inputs, state, tokens, seconds. [] when none.
side effects: none; reads events through record_run (bd list --all --type event)
work item id: 0005-1-log_read_item-code
