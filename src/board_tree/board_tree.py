from trace_back.trace_back import trace_back
from trace_forward.trace_forward import trace_forward


def board_tree(item_id: str, graph: dict[str, dict]) -> dict:
    """Build a combined back/forward tree view for an item in the graph."""
    return {
        "back": trace_back(item_id, graph),
        "forward": trace_forward(item_id, graph),
    }
