from story_jobs.story_jobs import story_jobs
from timeline.timeline import timeline

_RUN_GATES = ("built", "proven", "ready")


def _job_entry(job_id: str, graph: dict, labels: dict) -> dict:
    item = graph[job_id]
    title = item.get("title", "")
    for suffix in (" code", " test"):
        if title.endswith(suffix):
            title = title[: -len(suffix)]
            break
    retries = 0
    for label in labels.get(job_id, []):
        if label.startswith("retry:"):
            retries = int(label[len("retry:") :])
    return {
        "id": job_id,
        "kind": item["kind"],
        "function": title,
        "state": item["state"],
        "retries": retries,
        "claimed": bool(item.get("claimed_by")),
    }


def _run_entry(event: dict) -> dict:
    inputs = event.get("inputs") or {}
    return {
        "item": event["item"],
        "ts": event["ts"],
        "gate": event["gate"],
        "rule": event["rule"],
        "retries": inputs.get("retries", 0),
        "tokens": event.get("tokens") or 0,
        "turns": event.get("turns") or 0,
        "usd": event.get("usd") or 0.0,
        "harness": inputs.get("harness", ""),
        "model": inputs.get("model", ""),
    }


def story_status(story_id: str, graph: dict, labels: dict) -> dict:
    """Summarise a Story: its jobs and their run history.

    Inputs: story_id, a Story item id; graph, as record_graph() returns
    it; labels, an id to its label strings, as record_labels() returns.
    Outputs: id, state, jobs (one per code/test job, ordered by id) and
    runs (built/proven/ready timeline events, in time order, deduped).
    Reads only its arguments, mutates nothing. Raises ValueError when
    story_id is absent from graph or is not a story.
    """
    if story_id not in graph or graph[story_id].get("kind") != "story":
        raise ValueError(story_id)

    jobs = story_jobs(story_id, graph)
    job_ids = sorted(jobs["code"] + [t for ts in jobs["tests"].values() for t in ts])

    seen = set()
    runs = []
    for event in timeline(story_id, graph):
        if event["gate"] not in _RUN_GATES:
            continue
        key = (event["item"], event["ts"], event["gate"], event["rule"])
        if key not in seen:
            seen.add(key)
            runs.append(_run_entry(event))

    return {
        "id": story_id,
        "state": graph[story_id]["state"],
        "jobs": [_job_entry(job_id, graph, labels) for job_id in job_ids],
        "runs": runs,
    }
