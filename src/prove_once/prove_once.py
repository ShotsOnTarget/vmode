from board_config.board_config import board_config
from column_items.column_items import column_items
from prove_apply.prove_apply import prove_apply
from prove_gather.prove_gather import prove_gather
from record_graph.record_graph import record_graph
from record_labels.record_labels import record_labels
from record_set_state.record_set_state import record_set_state


def _folder_of(title: str) -> str:
    for suffix in (" code", " test"):
        if title.endswith(suffix):
            return title[: -len(suffix)]
    return title


def prove_once(config_path: str, log_path: str) -> list[str]:
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
        prove_apply(job_id, gathered, log_path)
        processed.append(job_id)

    graph = record_graph()
    for item in graph.values():
        if item["kind"] != "story" or item["state"] in ("done", "checking"):
            continue
        codes = [i for i in graph.values() if i["parent"] == item["id"]]
        tests = [i for i in graph.values() if i["parent"] in {c["id"] for c in codes}]
        jobs = codes + tests
        if jobs and all(job["state"] == "done" for job in jobs):
            record_set_state(item["id"], "checking")

    return processed
