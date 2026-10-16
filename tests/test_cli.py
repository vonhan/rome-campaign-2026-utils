from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook

from src.cli import run_cli


def test_cli_generates_appointment_and_guide_pdf(tmp_path: Path) -> None:
    workbook_path = tmp_path / "input.xlsx"
    output_dir = tmp_path / "out"
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(["Codice", "Gruppo", "Referente Gruppo", "Regno", "Auto", "Ospiti", "26/10 (Lunedì)", "", "", "", "27/10 (Martedì)", "", "", ""])
    worksheet.append(["", "", "", "", "", "", "Mattina", "Pomeriggio", "NOTE", "Mattina", "Pomeriggio", "NOTE", "", ""])
    worksheet.append(["CLI-1", "Gruppo CLI", "Bianchi, Anna", "Roma", "Auto 9", "Delegati CLI", "Rossi, Luca: 333444555", "Verdi, Anna: 444333222", "Nota CLI", "Neri, Paolo: 111222333", "", "Seconda nota", "", ""])
    workbook.save(workbook_path)

    exit_code = run_cli(["--input", str(workbook_path), "--output", str(output_dir), "--logo", "assets/icon.png"])

    assert exit_code == 0
    assert (output_dir / "Gruppo CLI.pdf").exists()
    assert (output_dir / "Guida-uso.pdf").exists()
