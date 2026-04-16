"""Sample plugin KPI for testing."""

from pathlib import Path


def compute(vars: dict, docs_dir: Path) -> dict:
    """Return a trivial KPI result."""
    return {
        "value": vars.get("tasks_done", 0) * 10,
        "format": "score",
        "detail": f"{vars.get('tasks_done', 0)} tasks completed",
        "warning": vars.get("tasks_done", 0) < 2,
    }
