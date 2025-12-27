"""Transitional entry point dispatching to CLI or MCP server."""

import os
import sys

from skillport.interfaces.cli.app import app
from skillport.interfaces.mcp.server import run_server
from skillport.shared.config import Config


def main():
    try:
        os.environ.setdefault("PYTHONIOENCODING", "utf-8")
        os.environ.setdefault("PYTHONUTF8", "1")
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    args = sys.argv[1:]
    # Legacy: no args → run MCP server (backward compat)
    # Note: `skillport --reindex` is NOT supported; use `skillport serve --reindex`
    if not args:
        config = Config()
        run_server(config=config)
    else:
        app()


if __name__ == "__main__":
    main()
