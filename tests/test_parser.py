from __future__ import annotations

from pathlib import Path

import pytest
from openpyxl import Workbook

from src.excel_parser import parse_volunteer, read_appointments


def test_read_appointments_understands_real_header_shape(
    tmp_path: Path, synthetic_workbook
) -> None:
    workbook_path = synthetic_workbook(tmp_path / "synthetic.xlsx")

    appointments = read_appointments(workbook_path)

    assert len(appointments) == 1
    appointment = appointments[0]
    assert appointment.group_code == "RM-01"
    assert appointment.group_contact == "Referente Sintetico"
    assert appointment.kingdom_hall == "Sala Centro"
    assert appointment.guest_count == "4"
    assert appointment.guest_vehicle == "Auto blu"
    assert appointment.source_row_number == 3
    assert [item.date_label for item in appointment.assignments] == [
        "26/10 (Lunedì)",
        "27/10 (Martedì)",
    ]
    assert appointment.assignments[0].morning is not None
    assert appointment.assignments[0].morning.surname == "ROSSI"
    assert appointment.assignments[0].morning.name == "MARIO"
    assert appointment.assignments[0].morning.phone == "000 111 222"
    assert appointment.assignments[1].afternoon is None


def test_read_appointments_keeps_every_non_empty_data_row(
    tmp_path: Path, synthetic_workbook
) -> None:
    rows = [
        ["DUP", "Primo", "Sala A", 1, "", "", "", "", "", "", ""],
        [None] * 11,
        ["DUP", "Secondo", "Sala B", 2, "", "", "", "", "", "", ""],
    ]
    workbook_path = synthetic_workbook(tmp_path / "rows.xlsx", rows)

    appointments = read_appointments(workbook_path)

    assert [item.source_row_number for item in appointments] == [3, 5]
    assert len(appointments) == 2
    assert all(len(item.assignments) == 2 for item in appointments)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("  ROSSI, MARIO: 000 123 456  ", "ROSSI, MARIO: 000 123 456"),
        ("Dato non strutturato", "Dato non strutturato"),
    ],
)
def test_parse_volunteer_preserves_complete_or_partial_data(
    raw: str, expected: str
) -> None:
    volunteer = parse_volunteer(raw)

    assert volunteer is not None
    assert volunteer.display == expected


def test_parse_volunteer_returns_none_for_empty_value() -> None:
    assert parse_volunteer("  ") is None


def test_missing_required_header_is_reported(tmp_path: Path) -> None:
    path = tmp_path / "invalid.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["Codice Gruppo", "Referente Gruppo", "Sala del Regno"])
    sheet.append(["", "", ""])
    workbook.save(path)

    with pytest.raises(ValueError, match="Intestazioni obbligatorie mancanti"):
        read_appointments(path)


def test_incomplete_date_block_is_reported(tmp_path: Path) -> None:
    path = tmp_path / "invalid-block.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(
        [
            "Codice Gruppo",
            "Referente Gruppo",
            "Sala del Regno",
            "N. Ospiti",
            "Auto Ospiti",
            "26/10 (Lunedì)",
            "",
        ]
    )
    sheet.append(["", "", "", "", "", "Mattina", "Pomeriggio"])
    workbook.save(path)

    with pytest.raises(ValueError, match="Mattina, Pomeriggio e NOTE"):
        read_appointments(path)


def test_non_xlsx_file_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "appointments.csv"
    path.write_text("synthetic", encoding="utf-8")

    with pytest.raises(ValueError, match="estensione .xlsx"):
        read_appointments(path)


def test_corrupted_xlsx_is_reported_clearly(tmp_path: Path) -> None:
    path = tmp_path / "corrupted.xlsx"
    path.write_text("not an Excel archive", encoding="utf-8")

    with pytest.raises(ValueError, match="Impossibile leggere il file Excel"):
        read_appointments(path)
