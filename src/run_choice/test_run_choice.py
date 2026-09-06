from run_choice.run_choice import run_choice

MANIFEST = {
    "models": {"cheap": "anthropic/claude-sonnet-5", "frontier": "anthropic/claude-fable-5-1"},
    "opencode_models": {"cheap": "opencode/muse-spark-1.3-contributor-free", "frontier": None},
}


def test_column_defaults_to_claude_code():
    choice = run_choice([], {"tier": "cheap"}, MANIFEST)
    assert choice == {"harness": "claude_code", "model": "anthropic/claude-sonnet-5"}


def test_column_adapter_picks_its_model_table():
    choice = run_choice([], {"tier": "cheap", "adapter": "opencode"}, MANIFEST)
    assert choice == {
        "harness": "opencode",
        "model": "opencode/muse-spark-1.3-contributor-free",
    }


def test_tier_without_model_leaves_harness_default():
    choice = run_choice([], {"tier": "frontier", "adapter": "opencode"}, MANIFEST)
    assert choice["model"] is None


def test_harness_label_overrides_column():
    choice = run_choice(["state:ready", "harness:opencode"], {"tier": "cheap"}, MANIFEST)
    assert choice["harness"] == "opencode"
    assert choice["model"] == "opencode/muse-spark-1.3-contributor-free"


def test_model_label_overrides_manifest():
    labels = ["harness:opencode", "model:opencode/glm-5.3-flash"]
    choice = run_choice(labels, {"tier": "cheap"}, MANIFEST)
    assert choice == {"harness": "opencode", "model": "opencode/glm-5.3-flash"}


def test_unknown_harness_has_no_table():
    choice = run_choice(["harness:pi"], {"tier": "cheap"}, MANIFEST)
    assert choice == {"harness": "pi", "model": None}


def test_empty_label_values_ignored():
    choice = run_choice(["harness:", "model:"], {"tier": "cheap"}, MANIFEST)
    assert choice["harness"] == "claude_code"
    assert choice["model"] == "anthropic/claude-sonnet-5"
