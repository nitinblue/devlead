"""Tests for convergence.py — weighted convergence formula."""
import pytest
from devlead.convergence import (
    story_convergence,
    tbo_convergence,
    bo_convergence,
    phase_convergence,
    coverage_score,
    traceability_score,
)
from devlead.workbook import BO, TBO, Story


def test_story_convergence_done():
    assert story_convergence("DONE") == 1.0

def test_story_convergence_not_done():
    assert story_convergence("IN_PROGRESS") == 0.0

def test_story_convergence_acceptance():
    assert story_convergence("ACCEPTANCE") == 0.0

def test_tbo_convergence_all_done():
    stories = [
        Story(id="S-1", description="a", epic_id="", tbo_ids=[], status="DONE", dod="", weight=60),
        Story(id="S-2", description="b", epic_id="", tbo_ids=[], status="DONE", dod="", weight=40),
    ]
    tbo = TBO(id="TBO-1", objective="x", status="DONE", planned="", actual="", metric="", weight=50, dod="", stories=stories)
    assert tbo_convergence(tbo) == 100.0

def test_tbo_convergence_partial():
    stories = [
        Story(id="S-1", description="a", epic_id="", tbo_ids=[], status="DONE", dod="", weight=60),
        Story(id="S-2", description="b", epic_id="", tbo_ids=[], status="IN_PROGRESS", dod="", weight=40),
    ]
    tbo = TBO(id="TBO-1", objective="x", status="IN_PROGRESS", planned="", actual="", metric="", weight=50, dod="", stories=stories)
    assert tbo_convergence(tbo) == 60.0

def test_tbo_convergence_no_stories():
    tbo = TBO(id="TBO-1", objective="x", status="NOT_STARTED", planned="", actual="", metric="", weight=50, dod="")
    assert tbo_convergence(tbo) == 0.0

def test_bo_convergence():
    s1 = Story(id="S-1", description="a", epic_id="", tbo_ids=[], status="DONE", dod="", weight=100)
    s2 = Story(id="S-2", description="b", epic_id="", tbo_ids=[], status="IN_PROGRESS", dod="", weight=100)
    tbo1 = TBO(id="TBO-1", objective="x", status="DONE", planned="", actual="", metric="", weight=30, dod="", stories=[s1])
    tbo2 = TBO(id="TBO-2", objective="y", status="IP", planned="", actual="", metric="", weight=70, dod="", stories=[s2])
    bo = BO(id="BO-1", objective="test", weight=100, status="FROZEN", phase="P1", tbos=[tbo1, tbo2])
    assert bo_convergence(bo) == 30.0

def test_bo_convergence_no_tbos():
    bo = BO(id="BO-1", objective="test", weight=100, status="DRAFT", phase="P1")
    assert bo_convergence(bo) == 0.0

def test_phase_convergence():
    s1 = Story(id="S-1", description="a", epic_id="", tbo_ids=[], status="DONE", dod="", weight=100)
    tbo1 = TBO(id="TBO-1", objective="x", status="DONE", planned="", actual="", metric="", weight=100, dod="", stories=[s1])
    bo1 = BO(id="BO-1", objective="a", weight=60, status="FROZEN", phase="P1", tbos=[tbo1])
    bo2 = BO(id="BO-2", objective="b", weight=40, status="FROZEN", phase="P1", tbos=[])
    assert phase_convergence([bo1, bo2]) == 60.0

def test_phase_convergence_empty():
    assert phase_convergence([]) == 0.0

def test_coverage_score_full():
    tbo = TBO(id="T1", objective="x", status="DONE", planned="", actual="", metric="", weight=100, dod="")
    bo = BO(id="BO-1", objective="test", weight=100, status="FROZEN", phase="P1", tbos=[tbo])
    assert coverage_score(bo) == 100.0

def test_coverage_score_partial():
    tbo = TBO(id="T1", objective="x", status="DONE", planned="", actual="", metric="", weight=70, dod="")
    bo = BO(id="BO-1", objective="test", weight=100, status="FROZEN", phase="P1", tbos=[tbo])
    assert coverage_score(bo) == 70.0

def test_coverage_score_empty():
    bo = BO(id="BO-1", objective="test", weight=100, status="DRAFT", phase="P1")
    assert coverage_score(bo) == 0.0

def test_traceability_full():
    assert traceability_score(10, 10) == 100.0

def test_traceability_partial():
    assert traceability_score(10, 7) == 70.0

def test_traceability_zero_tasks():
    assert traceability_score(0, 0) == 100.0
