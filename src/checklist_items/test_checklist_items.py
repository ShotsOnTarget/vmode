from checklist_items.checklist_items import checklist_items


def test_numbered_one_line():
    assert checklist_items("1. a [testing] 2. b [looking]") == [
        "a [testing]",
        "b [looking]",
    ]


def test_numbered_multiline():
    assert checklist_items("1. a [testing]\n2. b [looking]") == [
        "a [testing]",
        "b [looking]",
    ]


def test_number_inside_item_not_split():
    assert checklist_items("1. wait for 10. then go 2. b") == [
        "wait for 10. then go",
        "b",
    ]


def test_blank_returns_empty():
    assert checklist_items("") == []
    assert checklist_items("   ") == []


def test_unnumbered_single_item():
    assert checklist_items("just one line [looking]") == ["just one line [looking]"]


def test_items_stripped():
    assert checklist_items("1.  a   2.  b  ") == ["a", "b"]
