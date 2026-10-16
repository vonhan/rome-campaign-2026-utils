from __future__ import annotations

import multiprocessing
import sys

from src.cli import run_cli


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args:
        return run_cli(args)
    from src.gui import launch_gui

    launch_gui()
    return 0


if __name__ == "__main__":
    multiprocessing.freeze_support()
    raise SystemExit(main())
