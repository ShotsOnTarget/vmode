import json
import os


def cost_rollup(path: str, item_id: str) -> dict:
    result = {'item': item_id, 'tokens': 0, 'seconds': 0.0, 'runs': 0}
    if not os.path.exists(path):
        return result
    prefix = item_id + '-'
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except ValueError:
                raise ValueError('invalid JSON line: ' + line)
            line_item = record.get('item')
            if line_item != item_id and not (
                isinstance(line_item, str) and line_item.startswith(prefix)
            ):
                continue
            tokens = record.get('tokens', 0)
            if not isinstance(tokens, (int, float)):
                tokens = 0
            result['tokens'] += max(tokens, 0)
            seconds = record.get('seconds', 0.0)
            if not isinstance(seconds, (int, float)):
                seconds = 0.0
            result['seconds'] += seconds
            result['runs'] += 1
    return result
