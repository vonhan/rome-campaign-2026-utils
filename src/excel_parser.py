from __future__ import annotations

import re
from zipfile import BadZipFile
from pathlib import Path
from typing import Sequence

from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

from src.models import Appointment, DayAssignment, Volunteer


_DATE_RE = re.compile(r"^\d{1,2}/\d{1,2}(?:\s|$)")
_VOLUNTEER_RE = re.compile(
    r"^\s*(?P<surname>[^,:]+?)\s*,\s*(?P<name>[^:]+?)\s*:\s*(?P<phone>.+?)\s*$"
)
_FIELD_ALIASES = {
    "group_code": ("codice gruppo", "codice", "gruppo", "code"),
    "group_contact": ("referente gruppo", "referente", "group contact"),
    "kingdom_hall": ("sala del regno", "sala", "regno", "kingdom hall"),
    "guest_count": ("n ospiti", "numero ospiti", "ospiti", "guests"),
    "guest_vehicle": ("auto ospiti", "auto", "veicolo ospiti", "car"),
}


def _clean(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def _normalize_header(value: object) -> str:
    text = _clean(value).lower().replace("_", " ")
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def parse_volunteer(value: object) -> Volunteer | None:
    raw = re.sub(r"\s+", " ", _clean(value))
    if not raw:
        return None
    match = _VOLUNTEER_RE.match(raw)
    if not match:
        return Volunteer(raw=raw)
    return Volunteer(
        raw=raw,
        surname=match.group("surname").strip(),
        name=match.group("name").strip(),
        phone=match.group("phone").strip(),
    )


def _find_date_columns(header_row: Sequence[object]) -> list[int]:
    return [
        index
        for index, value in enumerate(header_row)
        if _DATE_RE.match(_clean(value))
    ]


def _find_base_columns(header_row: Sequence[object]) -> dict[str, int]:
    normalized = [_normalize_header(value) for value in header_row]
    result: dict[str, int] = {}
    missing: list[str] = []
    for field, aliases in _FIELD_ALIASES.items():
        index = next(
            (position for position, value in enumerate(normalized) if value in aliases),
            None,
        )
        if index is None:
            missing.append(aliases[0])
        else:
            result[field] = index
    if missing:
        raise ValueError(
            "Intestazioni obbligatorie mancanti: " + ", ".join(missing) + "."
        )
    return result


def _find_assignment_columns(
    second_row: Sequence[object], start: int, end: int, date_label: str
) -> tuple[int, int, int]:
    block = {
        _normalize_header(second_row[index]): index
        for index in range(start, min(end, len(second_row)))
        if _normalize_header(second_row[index])
    }
    morning = block.get("mattina")
    afternoon = block.get("pomeriggio")
    note = block.get("note")
    if morning is None or afternoon is None or note is None:
        raise ValueError(
            f"Il blocco del {date_label} deve contenere Mattina, Pomeriggio e NOTE."
        )
    return morning, afternoon, note


def read_appointments(path: str | Path) -> list[Appointment]:
    workbook_path = Path(path)
    if workbook_path.suffix.lower() != ".xlsx":
        raise ValueError("Selezionare un file Excel con estensione .xlsx.")

    try:
        workbook = load_workbook(workbook_path, read_only=True, data_only=True)
    except (OSError, ValueError, BadZipFile, InvalidFileException) as exc:
        raise ValueError(f"Impossibile leggere il file Excel: {exc}") from exc

    try:
        worksheet = workbook.active
        rows = list(worksheet.iter_rows(values_only=True))
        if len(rows) < 2:
            raise ValueError("Il file Excel non contiene le due righe di intestazione.")

        header_row = rows[0]
        second_row = rows[1]
        base_columns = _find_base_columns(header_row)
        date_columns = _find_date_columns(header_row)
        if not date_columns:
            raise ValueError(
                "Nessun blocco data trovato nella prima riga di intestazione."
            )

        assignment_columns: list[tuple[str, int, int, int]] = []
        for position, date_column in enumerate(date_columns):
            block_end = (
                date_columns[position + 1]
                if position + 1 < len(date_columns)
                else len(header_row)
            )
            date_label = _clean(header_row[date_column])
            columns = _find_assignment_columns(
                second_row, date_column, block_end, date_label
            )
            assignment_columns.append((date_label, *columns))

        appointments: list[Appointment] = []
        for row_number, row in enumerate(rows[2:], start=3):
            base_values = {
                field: _clean(row[index]) if index < len(row) else ""
                for field, index in base_columns.items()
            }
            if not any(base_values.values()):
                continue

            assignments = [
                DayAssignment(
                    date_label=date_label,
                    morning=parse_volunteer(
                        row[morning] if morning < len(row) else None
                    ),
                    afternoon=parse_volunteer(
                        row[afternoon] if afternoon < len(row) else None
                    ),
                    note=_clean(row[note]) if note < len(row) else "",
                )
                for date_label, morning, afternoon, note in assignment_columns
            ]
            appointments.append(
                Appointment(
                    **base_values,
                    assignments=assignments,
                    source_row_number=row_number,
                )
            )
        return appointments
    finally:
        workbook.close()
