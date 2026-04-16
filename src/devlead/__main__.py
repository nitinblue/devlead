"""Entry point for `python -m devlead`. Delegates to cli.main."""
import sys

from devlead.cli import main


if __name__ == "__main__":
    sys.exit(main())
