from column_valid.column_valid import column_valid


def _valid_column():
    return {
        "kinds": ["intent"],
        "states": ["waiting"],
        "role": "builder",
        "tier": "human",
        "wip": 1,
        "poll_seconds": 0,
    }


def test_valid_column_empty():
    assert column_valid("intent", _valid_column()) == []


def test_missing_key_reported():
    column = _valid_column()
    del column["wip"]
    problems = column_valid("intent", column)
    assert any(p.startswith("wip:") for p in problems)


def test_unknown_key_reported():
    column = _valid_column()
    column["colour"] = "blue"
    problems = column_valid("intent", column)
    assert any(p.startswith("colour:") for p in problems)


def test_bad_tier_reported():
    column = _valid_column()
    column["tier"] = "gpt"
    problems = column_valid("intent", column)
    assert any(p.startswith("tier:") for p in problems)


def test_bad_kind_reported():
    column = _valid_column()
    column["kinds"] = ["bug"]
    problems = column_valid("intent", column)
    assert any(p.startswith("kinds:") for p in problems)


def test_wip_zero_allowed():
    column = _valid_column()
    column["wip"] = 0
    assert column_valid("intent", column) == []


def test_wip_negative_reported():
    column = _valid_column()
    column["wip"] = -1
    problems = column_valid("intent", column)
    assert any(p.startswith("wip:") for p in problems)


def test_note_kind_valid():
    column = _valid_column()
    column["kinds"] = ["note"]
    column["states"] = ["waiting", "ready"]
    assert column_valid("intent", column) == []


def test_adapter_key_allowed():
    column = {
        "kinds": ["code"],
        "states": ["ready"],
        "role": "builder",
        "tier": "cheap",
        "wip": 1,
        "poll_seconds": 1,
        "adapter": "opencode",
    }
    assert column_valid("build", column) == []
    column["adapter"] = ""
    assert column_valid("build", column) != []
