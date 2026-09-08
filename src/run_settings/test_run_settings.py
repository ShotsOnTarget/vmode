from run_choice.run_choice import run_choice
from run_settings.run_settings import run_settings


def test_harness_and_model_as_run_choice():
    column = {"tier": "cheap", "adapter": "opencode"}
    manifest = {"opencode_models": {"cheap": "opencode/glm-5.3-flash"}}
    labels: list[str] = []
    expected = run_choice(labels, column, manifest)
    actual = run_settings(labels, column, manifest)
    assert actual["harness"] == expected["harness"]
    assert actual["model"] == expected["model"]


def test_effort_from_label():
    actual = run_settings(["effort:high"], {"tier": "cheap"}, {})
    assert actual["effort"] == "high"


def test_effort_from_manifest_tier():
    column = {"tier": "engineer"}
    manifest = {"efforts": {"engineer": "medium"}}
    assert run_settings([], column, manifest)["effort"] == "medium"


def test_effort_none_when_unset():
    assert run_settings([], {"tier": "cheap"}, {})["effort"] is None


def test_label_beats_manifest():
    column = {"tier": "cheap"}
    manifest = {"efforts": {"cheap": "high"}}
    actual = run_settings(["effort:low"], column, manifest)
    assert actual["effort"] == "low"


def test_empty_effort_label_ignored():
    actual = run_settings(["effort:"], {"tier": "cheap"}, {})
    assert actual["effort"] is None
