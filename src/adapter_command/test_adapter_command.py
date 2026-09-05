import shutil

import pytest

from adapter_command.adapter_command import adapter_command

ROOTS = {
    "board": "roles/board.toml",
    "manifest": "roles/manifest.json",
    "root": ".",
    "mcp": "roles/pullers/empty-mcp.json",
}


def test_exe_resolved(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda n: "C:/x/claude.cmd")
    item = {"id": "0001-1-thing-code", "kind": "code"}
    argv = adapter_command(item, "build", ROOTS)
    assert argv[0] == "C:/x/claude.cmd"


def test_missing_exe_raises(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda n: None)
    item = {"id": "0001-1-thing-code", "kind": "code"}
    with pytest.raises(RuntimeError):
        adapter_command(item, "build", ROOTS)


def test_model_from_manifest(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda n: "C:/x/claude.cmd")
    item = {"id": "0001-1-thing-code", "kind": "code"}
    argv = adapter_command(item, "build", ROOTS)
    assert "--model" in argv
    idx = argv.index("--model")
    assert argv[idx + 1] == "claude-sonnet-5"


def test_prompt_mentions_item_and_role(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda n: "C:/x/claude.cmd")
    item = {"id": "0001-1-thing-code", "kind": "code"}
    argv = adapter_command(item, "build", ROOTS)
    prompt = argv[2]
    assert "0001-1-thing-code" in prompt
    assert "You are the builder" in prompt


def test_test_kind_wording(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda n: "C:/x/claude.cmd")
    item = {"id": "0001-1-thing-test", "kind": "test"}
    argv = adapter_command(item, "test", ROOTS)
    prompt = argv[2]
    assert "never create or edit the code file" in prompt


def test_stripped_configuration(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda name: "C:/x/claude.cmd")
    item = {"id": "vm-1", "kind": "code", "title": "x code"}
    argv = adapter_command(item, "build", ROOTS)
    assert "--strict-mcp-config" in argv
    assert argv[argv.index("--mcp-config") + 1] == str(ROOTS["mcp"])
    assert "Read,Edit,Write,Bash,Glob,Grep" in argv
