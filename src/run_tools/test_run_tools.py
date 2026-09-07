from run_tools.run_tools import run_tools


def _cc_line(ts, content):
    return {
        "ts": ts,
        "harness": "claude_code",
        "event": {"type": "assistant", "message": {"content": content}},
    }


def _cc_tool_use(name, tool_id="toolu_01"):
    return {"type": "tool_use", "id": tool_id, "name": name, "input": {}}


def _oc_line(ts, tool):
    return {
        "ts": ts,
        "harness": "opencode",
        "event": {
            "type": "tool_use",
            "part": {
                "type": "tool",
                "tool": tool,
                "callID": "call_01",
                "state": {"status": "completed"},
            },
        },
    }


def _oc_step_finish(ts):
    return {"ts": ts, "harness": "opencode", "event": {"type": "step_finish"}}


def test_a_claude_code_tool_use_block_gives_its_name():
    events = [_cc_line("2026-09-07T19:06:06.098000+00:00", [_cc_tool_use("Bash")])]

    result = run_tools(events)

    assert [r["name"] for r in result] == ["Bash"]


def test_an_opencode_tool_use_event_gives_its_tool_name():
    events = [_oc_line("2026-09-07T19:06:07.598000+00:00", "glob")]

    result = run_tools(events)

    assert [r["name"] for r in result] == ["glob"]


def test_an_entry_has_only_name_and_offset():
    events = [_cc_line("2026-09-07T19:06:06.098000+00:00", [_cc_tool_use("Bash")])]

    result = run_tools(events)

    assert set(result[0].keys()) == {"name", "offset"}


def test_two_tool_use_blocks_in_one_event_give_two_entries():
    events = [
        _cc_line(
            "2026-09-07T19:06:06.098000+00:00",
            [
                {"type": "thinking", "thinking": ""},
                _cc_tool_use("Bash", "toolu_01"),
                _cc_tool_use("Read", "toolu_02"),
            ],
        )
    ]

    result = run_tools(events)

    assert [r["name"] for r in result] == ["Bash", "Read"]
    assert result[0]["offset"] == result[1]["offset"]


def test_a_claude_code_text_block_is_not_a_tool_call():
    events = [
        _cc_line(
            "2026-09-07T19:06:06.098000+00:00",
            [{"type": "text", "text": "hello"}],
        )
    ]

    result = run_tools(events)

    assert result == []


def test_an_opencode_step_finish_is_not_a_tool_call():
    events = [_oc_step_finish("2026-09-07T19:06:07.598000+00:00")]

    result = run_tools(events)

    assert result == []


def test_the_first_line_has_offset_zero():
    events = [_cc_line("2026-09-07T19:06:06.098000+00:00", [_cc_tool_use("Bash")])]

    result = run_tools(events)

    assert result[0]["offset"] == 0.0


def test_the_offset_is_seconds_from_the_first_line():
    events = [
        _cc_line("2026-09-07T19:06:06.000000+00:00", [_cc_tool_use("Bash")]),
        _cc_line("2026-09-07T19:06:07.500000+00:00", [_cc_tool_use("Read")]),
    ]

    result = run_tools(events)

    assert result[1]["offset"] == 1.5


def test_the_offset_is_rounded_to_three_decimals():
    events = [
        _cc_line("2026-09-07T19:06:06.000000+00:00", [_cc_tool_use("Bash")]),
        _cc_line("2026-09-07T19:06:07.234560+00:00", [_cc_tool_use("Read")]),
    ]

    result = run_tools(events)

    assert result[1]["offset"] == 1.235


def test_tool_calls_keep_their_order():
    events = [
        _cc_line("2026-09-07T19:06:06.098000+00:00", [_cc_tool_use("Bash")]),
        _oc_line("2026-09-07T19:06:07.598000+00:00", "glob"),
        _cc_line("2026-09-07T19:06:08.098000+00:00", [_cc_tool_use("Read")]),
    ]

    result = run_tools(events)

    assert [r["name"] for r in result] == ["Bash", "glob", "Read"]


def test_an_unknown_harness_gives_no_entry():
    events = [
        {
            "ts": "2026-09-07T19:06:06.098000+00:00",
            "harness": "something_else",
            "event": {"type": "assistant"},
        }
    ]

    result = run_tools(events)

    assert result == []


def test_no_events_gives_an_empty_list():
    assert run_tools([]) == []
