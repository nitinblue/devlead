"""Smoke tests — verify the package installs and CLI responds."""

import subprocess
import sys


def test_import():
    """devlead can be imported and has __version__."""
    import devlead

    assert hasattr(devlead, "__version__")
    assert devlead.__version__ == "0.1.0"


def test_cli_help():
    """python -m devlead --help exits 0."""
    result = subprocess.run(
        [sys.executable, "-m", "devlead", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Usage:" in result.stdout


def test_cli_version():
    """python -m devlead --version shows version string."""
    result = subprocess.run(
        [sys.executable, "-m", "devlead", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "0.1.0" in result.stdout
