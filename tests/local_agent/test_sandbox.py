from pathlib import Path

import pytest

from local_agent.sandbox import LocalAgentSandbox, LocalAgentSandboxError


def test_sandbox_compileall(tmp_path: Path):
    (tmp_path / "sample.py").write_text("x = 1\n", encoding="utf-8")
    result = LocalAgentSandbox(root=str(tmp_path)).run({"operation": "compileall", "target": "."})
    assert result["ok"] is True


def test_sandbox_rejects_arbitrary_operation(tmp_path: Path):
    with pytest.raises(LocalAgentSandboxError):
        LocalAgentSandbox(root=str(tmp_path)).run({"operation": "shell", "command": "echo unsafe"})


def test_sandbox_blocks_path_escape(tmp_path: Path):
    with pytest.raises(LocalAgentSandboxError):
        LocalAgentSandbox(root=str(tmp_path)).run({"operation": "compileall", "target": "../outside"})
