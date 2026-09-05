from pattern_stale.pattern_stale import pattern_stale

LABELS = {
    "p-old": ["kind:pattern", "used:3", "last_used:2026-05-01"],
    "p-new": ["kind:pattern", "used:1", "last_used:2026-09-01"],
    "p-none": ["kind:pattern", "used:0"],
    "s": ["kind:story", "state:done"],
}


def test_stale_after_ninety_days():
    assert pattern_stale(LABELS, "2026-09-05") == ["p-none", "p-old"]


def test_window_can_change():
    assert pattern_stale(LABELS, "2026-09-05", days=1) == ["p-new", "p-none", "p-old"]


def test_non_patterns_ignored():
    assert "s" not in pattern_stale(LABELS, "2026-09-05")
