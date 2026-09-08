from builder_prompt.builder_prompt import builder_prompt


def test_names_role_item_and_root():
    text = builder_prompt({"id": "vm-1", "kind": "code"}, "builder", "C:/w")
    assert "vm-1" in text and "builder" in text and "C:/w" in text


def test_test_kind_wording():
    text = builder_prompt({"id": "vm-1", "kind": "test"}, "builder", ".")
    assert "never create or edit the code file" in text


def test_code_kind_wording():
    text = builder_prompt({"id": "vm-1", "kind": "code"}, "builder", ".")
    assert "Do not write tests" in text


def test_the_last_gate_word_is_carried():
    item = {"id": "vm-1", "kind": "test", "last_gate": "bounce: case_missing"}
    text = builder_prompt(item, "builder", ".")
    tail = "The last gate on this item said: bounce: case_missing. Fix that first."
    assert text.endswith(tail)


def test_no_last_gate_adds_nothing():
    plain = builder_prompt({"id": "vm-1", "kind": "code"}, "builder", ".")
    item = {"id": "vm-1", "kind": "code", "last_gate": ""}
    assert builder_prompt(item, "builder", ".") == plain
