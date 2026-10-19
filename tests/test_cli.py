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
        "Appuntamento-Primo-DUP-riga-3.pdf",
        "Appuntamento-Secondo-DUP-riga-4.pdf",
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


def test_cli_can_generate_volunteer_schedules(
    tmp_path: Path, synthetic_workbook, capsys
) -> None:
    workbook_path = synthetic_workbook(
        tmp_path / "input.xlsx",
        [
            [
                "RM-01",
                "Referente Uno",
                "Sala A",
                1,
                "Auto A",
                "ROSSI MARIO 111",
                "",
                "Messaggio 1",
                "ROSSI MARIO 111",
                "",
                "Messaggio 2",
            ],
            [
                "RM-02",
                "Referente Due",
                "Sala B",
                2,
                "Auto B",
                "VERDI ANNA 222",
                "",
                "Messaggio 3",
                "",
                "ROSSI MARIO 111",
                "Messaggio 4",
            ],
        ],
    )
    output_dir = tmp_path / "out"

    exit_code = run_cli(
        [
            "--input",
            str(workbook_path),
            "--output",
            str(output_dir),
            "--mode",
            "volontario",
            "--logo",
            "assets/icon.png",
        ]
    )

    volunteer_files = sorted(output_dir.glob("Volontario-*.pdf"))
    assert exit_code == 0
    assert {path.name for path in volunteer_files} == {
        "Volontario-ROSSI-MARIO-RM-01-RM-02.pdf",
        "Volontario-VERDI-ANNA-RM-02.pdf",
    }
    assert (output_dir / "Guida-uso.pdf").is_file()
    assert "Generati 2 PDF per capogruppo volontario" in capsys.readouterr().out


def test_cli_reports_all_cell_errors_without_sensitive_values(
    tmp_path: Path, synthetic_workbook_v2, capsys
) -> None:
    sensitive_value = "NOMINATIVO RISERVATO"
    workbook_path = synthetic_workbook_v2(
        tmp_path / "invalid.xlsx",
        [
            [
                "PRIMARY001",
                "Referente Sintetico",
                "3334445555",
                "Sala",
                1,
                "",
                f"{sensitive_value} ERRATO",
                "ALTRO ERRATO",
                "(include BAD CODE)",
                "",
                "",
                "",
            ]
        ],
    )
    output_dir = tmp_path / "out"

    exit_code = run_cli(
        [
            "--input",
            str(workbook_path),
            "--output",
            str(output_dir),
            "--mode",
            "volontario",
            "--logo",
            "assets/icon.png",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "3 errori" in captured.err
    assert "cella G3" in captured.err
    assert "cella H3" in captured.err
    assert "cella I3" in captured.err
    assert sensitive_value not in captured.err
    assert "Generati" not in captured.out
    assert not output_dir.exists()
