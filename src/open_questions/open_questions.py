from datetime import UTC, datetime


def _story_for(parent_id, items):
    item = items[parent_id]
    if item["kind"] in ("story", "intent"):
        return parent_id
    return item["parent"]


def open_questions(notes, items, hours, now):
    """Return the notes that are unanswered questions older than `hours` hours.

    A question is a note owned by a role other than analyst or supervisor with
    no comment starting `answer (<owner>): ` or `answer (board): `, created
    more than `hours` hours before `now`. Each result carries the note's id,
    title, owner, the Story it hangs under, and its age in hours, ordered
    oldest first. A note under a job walks to the job's Story; a note under a
    Story or Intent reports that item. Pure: reads only its inputs.
    """
    out = []
    for note in notes:
        if note["owner"] in ("analyst", "supervisor"):
            continue
        texts = [c.get("text", "") for c in note.get("comments", [])]
        answered = any(
            t.startswith(f"answer ({note['owner']}): ")
            or t.startswith("answer (board): ")
            for t in texts
        )
        if answered:
            continue
        created = datetime.strptime(note["created_at"], "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=UTC
        )
        age = (now - created).total_seconds() / 3600
        if age <= hours:
            continue
        out.append(
            {
                "id": note["id"],
                "title": note["title"],
                "owner": note["owner"],
                "story": _story_for(note["parent"], items),
                "age_hours": age,
            }
        )
    return sorted(out, key=lambda q: q["age_hours"], reverse=True)
