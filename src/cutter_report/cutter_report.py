_KEYS = ("story", "setting", "pairs", "tokens", "usd", "bounces", "blocked")


def cutter_report(cuts: list[dict]) -> list[dict]:
    """Roll cutter_gather's per-Story cuts up into one row per setting.

    Inputs: cuts, the list cutter_gather.cutter_gather returns, each a dict
    with the keys story, setting, pairs, tokens, usd, bounces and blocked.
    Outputs: one dict per distinct setting, sorted by setting, with keys
    setting, stories, pairs, tokens, usd, bounces, blocked, bounces_per_pair
    and blocked_per_story. Pure: reads nothing outside its argument.
    """
    rows = {}
    for cut in cuts:
        for key in _KEYS:
            if key not in cut:
                raise ValueError(key)
        row = rows.setdefault(
            cut["setting"],
            {
                "setting": cut["setting"],
                "stories": 0,
                "pairs": 0,
                "tokens": 0,
                "usd": 0.0,
                "bounces": 0,
                "blocked": 0,
            },
        )
        row["stories"] += 1
        row["pairs"] += cut["pairs"]
        row["tokens"] += cut["tokens"]
        row["usd"] += cut["usd"]
        row["bounces"] += cut["bounces"]
        row["blocked"] += cut["blocked"]

    result = []
    for setting in sorted(rows):
        row = rows[setting]
        row["bounces_per_pair"] = (
            round(row["bounces"] / row["pairs"], 2) if row["pairs"] else 0.0
        )
        row["blocked_per_story"] = (
            round(row["blocked"] / row["stories"], 2) if row["stories"] else 0.0
        )
        result.append(row)
    return result
