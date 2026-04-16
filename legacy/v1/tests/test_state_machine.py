"""Tests for state_machine.py — states, transitions, gates, checklists."""

import json
import pytest
from pathlib import Path
from devlead.state_machine import (
    STATES,
    VALID_TRANSITIONS,
    EXIT_CRITERIA,
    init_state,
    load_state,
    save_state,
    check_gate,
    do_transition,
    do_checklist,
    do_start,
)


def test_states_list():
    assert "SESSION_START" in STATES
    assert "ORIENT" in STATES
    assert "TRIAGE" in STATES
    assert "PRIORITIZE" in STATES
    assert "PLAN" in STATES
    assert "EXECUTE" in STATES
    assert "UPDATE" in STATES
    assert "SESSION_END" in STATES
    assert len(STATES) == 8


def test_valid_transitions_structure():
    """Every state in VALID_TRANSITIONS maps to a list of valid target states."""
    for state in STATES:
        assert state in VALID_TRANSITIONS
        assert isinstance(VALID_TRANSITIONS[state], list)


def test_init_state_structure():
    state = init_state()
    assert state["state"] == "SESSION_START"
    assert "checklists" in state
    assert "ORIENT" in state["checklists"]
    assert "TRIAGE" in state["checklists"]
    assert "PRIORITIZE" in state["checklists"]
    assert "status_read" in state["checklists"]["ORIENT"]
    assert "session_start" in state
    assert "transitions" in state
    assert isinstance(state["transitions"], list)


def test_save_load_roundtrip(state_file):
    state = init_state()
    save_state(state, state_file)
    loaded = load_state(state_file)
    assert loaded["state"] == state["state"]
    assert loaded["checklists"] == state["checklists"]


def test_gate_allows_execute_in_execute(state_file):
    """EXECUTE gate allows when current state is EXECUTE."""
    state = init_state()
    state["state"] = "EXECUTE"
    save_state(state, state_file)
    with pytest.raises(SystemExit) as exc:
        check_gate(state_file, "EXECUTE")
    assert exc.value.code == 0


def test_gate_allows_in_orient(state_file):
    """EXECUTE gate allows (warns) when current state is ORIENT."""
    state = init_state()
    state["state"] = "ORIENT"
    save_state(state, state_file)
    with pytest.raises(SystemExit) as exc:
        check_gate(state_file, "EXECUTE")
    assert exc.value.code == 0


def test_gate_allows_edit_in_update(state_file):
    """EXECUTE gate also allows in UPDATE (docs need editing)."""
    state = init_state()
    state["state"] = "UPDATE"
    save_state(state, state_file)
    with pytest.raises(SystemExit) as exc:
        check_gate(state_file, "EXECUTE")
    assert exc.value.code == 0


def test_gate_plan_allows_in_prioritize(state_file):
    """PLAN gate allows in PRIORITIZE (entering plan mode after prioritization)."""
    state = init_state()
    state["state"] = "PRIORITIZE"
    save_state(state, state_file)
    with pytest.raises(SystemExit) as exc:
        check_gate(state_file, "PLAN")
    assert exc.value.code == 0


def test_gate_plan_allows_in_execute(state_file):
    """PLAN gate allows in EXECUTE (re-planning mid-execution)."""
    state = init_state()
    state["state"] = "EXECUTE"
    save_state(state, state_file)
    with pytest.raises(SystemExit) as exc:
        check_gate(state_file, "PLAN")
    assert exc.value.code == 0


def test_gate_allows_plan_in_orient(state_file):
    """PLAN gate allows (warns) in ORIENT."""
    state = init_state()
    state["state"] = "ORIENT"
    save_state(state, state_file)
    with pytest.raises(SystemExit) as exc:
        check_gate(state_file, "PLAN")
    assert exc.value.code == 0


def test_gate_session_end_warns_not_blocks(state_file):
    """SESSION_END gate warns but doesn't block (exit 0)."""
    state = init_state()
    state["state"] = "EXECUTE"
    save_state(state, state_file)
    with pytest.raises(SystemExit) as exc:
        check_gate(state_file, "SESSION_END")
    assert exc.value.code == 0


def test_gate_allows_missing_state_file(state_file):
    """Gate allows (warns) when state file doesn't exist."""
    with pytest.raises(SystemExit) as exc:
        check_gate(state_file, "EXECUTE")
    assert exc.value.code == 0


def test_transition_orient_to_triage(state_file):
    """Valid transition ORIENT -> TRIAGE with complete checklist."""
    state = init_state()
    state["state"] = "ORIENT"
    for key in state["checklists"]["ORIENT"]:
        state["checklists"]["ORIENT"][key] = True
    save_state(state, state_file)
    with pytest.raises(SystemExit) as exc:
        do_transition(state_file, "TRIAGE")
    assert exc.value.code == 0
    loaded = load_state(state_file)
    assert loaded["state"] == "TRIAGE"


def test_transition_triage_to_prioritize(state_file):
    """Valid transition TRIAGE -> PRIORITIZE with complete checklist."""
    state = init_state()
    state["state"] = "TRIAGE"
    for key in state["checklists"]["TRIAGE"]:
        state["checklists"]["TRIAGE"][key] = True
    save_state(state, state_file)
    with pytest.raises(SystemExit) as exc:
        do_transition(state_file, "PRIORITIZE")
    assert exc.value.code == 0
    loaded = load_state(state_file)
    assert loaded["state"] == "PRIORITIZE"


def test_transition_warns_on_invalid(state_file):
    """Invalid transition (ORIENT -> EXECUTE) warns but succeeds."""
    state = init_state()
    state["state"] = "ORIENT"
    for key in state["checklists"]["ORIENT"]:
        state["checklists"]["ORIENT"][key] = True
    save_state(state, state_file)
    with pytest.raises(SystemExit) as exc:
        do_transition(state_file, "EXECUTE")
    assert exc.value.code == 0
    loaded = load_state(state_file)
    assert loaded["state"] == "EXECUTE"


def test_transition_allows_incomplete_checklist(state_file):
    """Transition warns but succeeds when exit criteria not met."""
    state = init_state()
    state["state"] = "ORIENT"
    state["checklists"]["ORIENT"]["status_read"] = True
    # others remain False
    save_state(state, state_file)
    with pytest.raises(SystemExit) as exc:
        do_transition(state_file, "TRIAGE")
    assert exc.value.code == 0
    loaded = load_state(state_file)
    assert loaded["state"] == "TRIAGE"


def test_transition_records_history(state_file):
    """Transition appends to the transitions list."""
    state = init_state()
    state["state"] = "ORIENT"
    for key in state["checklists"]["ORIENT"]:
        state["checklists"]["ORIENT"][key] = True
    save_state(state, state_file)
    with pytest.raises(SystemExit):
        do_transition(state_file, "TRIAGE")
    loaded = load_state(state_file)
    assert len(loaded["transitions"]) > 0
    last = loaded["transitions"][-1]
    assert last["from"] == "ORIENT"
    assert last["to"] == "TRIAGE"


def test_transition_no_checklist_state(state_file):
    """States without checklists (PLAN, EXECUTE) transition freely."""
    state = init_state()
    state["state"] = "PLAN"
    save_state(state, state_file)
    with pytest.raises(SystemExit) as exc:
        do_transition(state_file, "EXECUTE")
    assert exc.value.code == 0
    loaded = load_state(state_file)
    assert loaded["state"] == "EXECUTE"


def test_checklist_marks_item(state_file):
    """Marking a checklist item sets it to True."""
    state = init_state()
    state["state"] = "ORIENT"
    save_state(state, state_file)
    do_checklist(state_file, "ORIENT", "status_read")
    loaded = load_state(state_file)
    assert loaded["checklists"]["ORIENT"]["status_read"] is True


def test_checklist_triage(state_file):
    """TRIAGE checklist items work."""
    state = init_state()
    save_state(state, state_file)
    do_checklist(state_file, "TRIAGE", "scratchpad_reviewed")
    loaded = load_state(state_file)
    assert loaded["checklists"]["TRIAGE"]["scratchpad_reviewed"] is True


def test_checklist_prioritize(state_file):
    """PRIORITIZE checklist items work."""
    state = init_state()
    save_state(state, state_file)
    do_checklist(state_file, "PRIORITIZE", "priorities_assigned")
    loaded = load_state(state_file)
    assert loaded["checklists"]["PRIORITIZE"]["priorities_assigned"] is True


def test_checklist_invalid_key(state_file):
    """Invalid checklist key raises SystemExit."""
    state = init_state()
    save_state(state, state_file)
    with pytest.raises(SystemExit):
        do_checklist(state_file, "ORIENT", "nonexistent_key")


def test_checklist_invalid_state(state_file):
    """Invalid state name for checklist raises SystemExit."""
    state = init_state()
    save_state(state, state_file)
    with pytest.raises(SystemExit):
        do_checklist(state_file, "NONEXISTENT", "status_read")


def test_start_initializes_orient(state_file, tmp_docs):
    """do_start creates state file and transitions to ORIENT."""
    with pytest.raises(SystemExit) as exc:
        do_start(state_file, tmp_docs)
    assert exc.value.code == 0
    loaded = load_state(state_file)
    assert loaded["state"] == "ORIENT"


def test_start_overwrites_existing(state_file, tmp_docs):
    """do_start resets state even if file already exists."""
    state = init_state()
    state["state"] = "EXECUTE"
    save_state(state, state_file)
    with pytest.raises(SystemExit) as exc:
        do_start(state_file, tmp_docs)
    assert exc.value.code == 0
    loaded = load_state(state_file)
    assert loaded["state"] == "ORIENT"
