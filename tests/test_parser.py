from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook

from src.excel_parser import read_appointments


def test_read_appointments_extracts_day_assignments(tmp_path: Path) -> None:
    workbook_path = tmp_path / "example.xlsx"
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(["Codice", "Gruppo", "Referente Gruppo", "Regno", "Auto", "Ospiti", "26/10 (Lunedì)", "", "", "", "27/10 (Martedì)", "", "", ""])
    worksheet.append(["", "", "", "", "", "", "Mattina", "Pomeriggio", "NOTE", "Mattina", "Pomeriggio", "NOTE", "", ""])
    worksheet.append(["A-001", "Gruppo Uno", "Rossi, Mario", "Roma", "Auto 1", "Delegato 1", "Bianchi, Luca: 333111222", "Verdi, Anna: 444222333", "Prima nota", "Neri, Paolo: 555444333", "", "Seconda nota", "", ""])
    workbook.save(workbook_path)

    appointments = read_appointments(workbook_path)

    assert len(appointments) == 1
    appointment = appointments[0]
    assert appointment.code == "A-001"
    assert appointment.group == "Gruppo Uno"
    assert appointment.assignments[0].date_label == "26/10 (Lunedì)"
    assert "Bianchi" in appointment.assignments[0].morning
    assert "Verdi" in appointment.assignments[0].afternoon
    assert appointment.assignments[0].note == "Prima nota"
    assert appointment.assignments[1].date_label == "27/10 (Martedì)"
    assert "Neri" in appointment.assignments[1].morning
