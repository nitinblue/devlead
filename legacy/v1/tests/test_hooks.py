import json
import pytest
from devlead.hooks import hook_allow, hook_block, hook_context

def test_hook_allow_exits_zero():
    with pytest.raises(SystemExit) as exc:
        hook_allow()
    assert exc.value.code == 0

def test_hook_allow_outputs_json(capsys):
    with pytest.raises(SystemExit):
        hook_allow("test message")
    out = json.loads(capsys.readouterr().out)
    assert out["systemMessage"] == "[DevLead] test message"

def test_hook_allow_empty_message(capsys):
    with pytest.raises(SystemExit):
        hook_allow()
    out = json.loads(capsys.readouterr().out)
    assert out == {}

def test_hook_block_exits_two():
    with pytest.raises(SystemExit) as exc:
        hook_block("blocked")
    assert exc.value.code == 2

def test_hook_block_writes_stderr(capsys):
    with pytest.raises(SystemExit):
        hook_block("blocked reason")
    assert "blocked reason" in capsys.readouterr().err

def test_hook_context_exits_zero(capsys):
    with pytest.raises(SystemExit) as exc:
        hook_context("context info")
    assert exc.value.code == 0
    out = json.loads(capsys.readouterr().out)
    assert out["systemMessage"] == "[DevLead] context info"
