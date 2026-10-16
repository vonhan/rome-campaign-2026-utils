from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from src.cli import run_cli


def test_cli_generates_one_unique_pdf_per_row_and_guide(
    tmp_path: Path, synthetic_workbook, capsys
) -> None:
    rows = [
        ["DUP", "Primo", "Sala A", 1, "", "", "", "", "", "", ""],
        ["DUP", "Secondo", "Sala B", 2, "", "", "", "", "", "", ""],
    ]
    workbook_path = synthetic_workbook(tmp_path / "input.xlsx", rows)
    output_dir = tmp_path / "out"

    exit_code = run_cli(
        [
            "--input",
            str(workbook_path),
            "--output",
            str(output_dir),
            "--logo",
            "assets/icon.png",
        ]
    )

    appointment_files = sorted(output_dir.glob("Appuntamento-*.pdf"))
    assert exit_code == 0
    assert [path.name for path in appointment_files] == [
        "Appuntamento-DUP-riga-3.pdf",
        "Appuntamento-DUP-riga-4.pdf",
    ]
    assert (output_dir / "Guida-uso.pdf").is_file()
    assert all(len(PdfReader(path).pages) >= 1 for path in appointment_files)
    assert "Generati 2 PDF" in capsys.readouterr().out


def test_cli_reports_missing_input_without_success_message(
    tmp_path: Path, capsys
) -> None:
    exit_code = run_cli(
        [
            "--input",
            str(tmp_path / "missing.xlsx"),
            "--output",
            str(tmp_path / "out"),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "File Excel non trovato" in captured.err
    assert "Generati" not in captured.out


def test_cli_can_generate_standalone_guide(tmp_path: Path) -> None:
    guide = tmp_path / "Guida-uso.pdf"

    exit_code = run_cli(
        [
            "--guide-only",
            str(guide),
            "--logo",
            "assets/icon.png",
        ]
    )

    assert exit_code == 0
    assert guide.is_file()
