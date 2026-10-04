from pathlib import Path

import pytest

from local_agent.code_workspace import CodeWorkspace, CodeWorkspaceError


def test_create_file_is_audited_and_backed_up_on_overwrite(tmp_path: Path):
    target = tmp_path / "module.py"
    target.write_text("x = 1\n", encoding="utf-8")
    result = CodeWorkspace(str(tmp_path)).apply({"operations": [{
        "action": "create_file", "path": "module.py", "content": "x = 2\n", "overwrite": True
    }]})
    assert result["ok"] is True
    assert result["changes"][0]["backup"]
    assert target.read_text(encoding="utf-8") == "x = 2\n"


def test_replace_requires_exactly_one_match(tmp_path: Path):
    (tmp_path / "a.py").write_text("x = 1\nx = 1\n", encoding="utf-8")
    with pytest.raises(CodeWorkspaceError):
        CodeWorkspace(str(tmp_path)).apply({"operations": [{
            "action": "replace_text", "path": "a.py", "old_text": "x = 1", "new_text": "x = 2"
        }]})


def test_code_dry_run_does_not_modify(tmp_path: Path):
    target = tmp_path / "a.py"
    target.write_text("x = 1\n", encoding="utf-8")
    result = CodeWorkspace(str(tmp_path)).apply({"operations": [{
        "action": "replace_text", "path": "a.py", "old_text": "x = 1", "new_text": "x = 2"
    }]}, dry_run=True)
    assert result["dry_run"] is True
    assert target.read_text(encoding="utf-8") == "x = 1\n"


def test_code_workspace_blocks_escape(tmp_path: Path):
    with pytest.raises(CodeWorkspaceError):
        CodeWorkspace(str(tmp_path)).apply({"operations": [{
            "action": "create_file", "path": "../evil.py", "content": "print(1)"
        }]})


def test_rollback_restores_previous_bytes(tmp_path: Path):
    target = tmp_path / "a.py"
    target.write_text("x = 1\n", encoding="utf-8")
    ws = CodeWorkspace(str(tmp_path))
    result = ws.apply({"operations": [{
        "action": "replace_text", "path": "a.py", "old_text": "x = 1", "new_text": "x = 2"
    }]})
    assert target.read_text(encoding="utf-8") == "x = 2\n"
    ws.rollback(result)
    assert target.read_text(encoding="utf-8") == "x = 1\n"
