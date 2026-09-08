import pytest

from cutter_report.cutter_report import cutter_report


def _cut(setting, story="s", pairs=0, tokens=0, usd=0.0, bounces=0, blocked=0):
    return {
        "story": story,
        "setting": setting,
        "pairs": pairs,
        "tokens": tokens,
        "usd": usd,
        "bounces": bounces,
        "blocked": blocked,
    }


def test_one_cut_gives_one_row():
    result = cutter_report([_cut("a/b/c")])

    assert len(result) == 1
    assert result[0]["setting"] == "a/b/c"
    assert result[0]["stories"] == 1


def test_cuts_sharing_a_setting_give_one_row():
    result = cutter_report([_cut("a/b/c", story="s1"), _cut("a/b/c", story="s2")])

    assert len(result) == 1
    assert result[0]["stories"] == 2


def test_two_settings_give_two_rows():
    result = cutter_report([_cut("a/b/c"), _cut("d/e/f")])

    assert len(result) == 2


def test_rows_are_sorted_by_setting():
    result = cutter_report([_cut("z/z/z"), _cut("a/a/a")])

    assert [r["setting"] for r in result] == ["a/a/a", "z/z/z"]


def test_pairs_and_tokens_are_summed():
    cuts = [
        _cut("a/b/c", story="s1", pairs=2, tokens=100),
        _cut("a/b/c", story="s2", pairs=4, tokens=250),
    ]

    result = cutter_report(cuts)

    assert result[0]["pairs"] == 6
    assert result[0]["tokens"] == 350


def test_usd_is_summed_as_a_float():
    cuts = [
        _cut("a/b/c", story="s1", usd=1.5),
        _cut("a/b/c", story="s2", usd=2.25),
    ]

    result = cutter_report(cuts)

    assert result[0]["usd"] == 3.75


def test_bounces_and_blocked_are_summed():
    cuts = [
        _cut("a/b/c", story="s1", bounces=1, blocked=0),
        _cut("a/b/c", story="s2", bounces=2, blocked=3),
    ]

    result = cutter_report(cuts)

    assert result[0]["bounces"] == 3
    assert result[0]["blocked"] == 3


def test_bounces_per_pair_is_rounded_to_two_places():
    result = cutter_report([_cut("a/b/c", bounces=1, pairs=3)])

    assert result[0]["bounces_per_pair"] == 0.33


def test_zero_pairs_gives_zero_bounces_per_pair():
    result = cutter_report([_cut("a/b/c", pairs=0, bounces=2)])

    assert result[0]["bounces_per_pair"] == 0.0


def test_blocked_per_story_divides_by_stories():
    cuts = [
        _cut("a/b/c", story="s1", blocked=3),
        _cut("a/b/c", story="s2", blocked=0),
    ]

    result = cutter_report(cuts)

    assert result[0]["blocked_per_story"] == 1.5


def test_empty_cuts_gives_an_empty_list():
    assert cutter_report([]) == []


def test_missing_key_raises():
    bad_cut = _cut("a/b/c")
    del bad_cut["bounces"]

    with pytest.raises(ValueError):
        cutter_report([bad_cut])
