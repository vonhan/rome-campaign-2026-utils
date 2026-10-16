from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_main_cli_runs_without_importing_graphical_toolkit(
    tmp_path: Path,
) -> None:
    guide = tmp_path / "Guida-uso.pdf"

    completed = subprocess.run(
        [
            sys.executable,
            "main.py",
            "--guide-only",
            str(guide),
            "--logo",
            "assets/icon.png",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert guide.is_file()
