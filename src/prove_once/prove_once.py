from board_config.board_config import board_config
from column_items.column_items import column_items
from gate_ready.gate_ready import gate_ready
from proposal_sweep.proposal_sweep import proposal_sweep
from prove_apply.prove_apply import prove_apply
from prove_gather.prove_gather import prove_gather
from ready_apply.ready_apply import ready_apply
from ready_gather.ready_gather import ready_gather
from record_graph.record_graph import record_graph
from record_labels.record_labels import record_labels
from record_set_state.record_set_state import record_set_state


def _folder_of(title: str) -> str:
    for suffix in (" code", " test"):
        if title.endswith(suffix):
            return title[: -len(suffix)]
    return title


def _ready() -> None:
    graph = record_graph()
    labels = record_labels()
    for story_id, item in graph.items():
        if (
            item["kind"] != "story"
            or item["state"] not in ("waiting", "in_progress")
            or item["claimed_by"]
            or "cut" not in labels.get(story_id, [])
        ):
            continue
        gathered = ready_gather(story_id, ".")
        extra = {"checklist": gathered["checklist"], "existing": gathered["existing"]}
        rules = gate_ready(story_id, gathered["graph"], gathered["sheets"], extra)
        ready_apply(story_id, rules, gathered)


def _advance() -> None:
    graph = record_graph()
    for item in graph.values():
        if (
            item["kind"] != "story"
            or item["state"] not in ("waiting", "ready")
            or item["claimed_by"]
        ):
            continue
        jobs = [
            j
            for j in graph.values()
            if j["parent"] == item["id"] and j["kind"] in ("code", "test")
        ]
        if jobs and all(job["state"] == "done" for job in jobs):
            record_set_state(item["id"], "checking")


def prove_once(config_path: str) -> list[str]:
    """Gate prove jobs, then cut stories, then advance done stories.

    Args: config_path: board config path. Returns: prove job ids.
    Side effects: record states, one ready event per cut story.
    """
    config = board_config(config_path)
    graph = record_graph()
    labels = record_labels()
    processed = []
    for item in column_items("prove", graph, labels, config):
        job_id = item["id"]
        folder = _folder_of(item["title"])
        gathered = prove_gather(job_id, folder)
        gathered["folder"] = folder
        gathered["repo"] = "."
        prove_apply(job_id, gathered)
        processed.append(job_id)

    graph = record_graph()
    proposal_sweep(graph)
    _ready()
    _advance()

    return processed
