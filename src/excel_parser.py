from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, List, Sequence

from openpyxl import load_workbook

from src.models import Appointment, DayAssignment


_DATE_RE = re.compile(r"^\d{1,2}/\d{1,2}")


def _clean(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _normalize_header(value: str) -> str:
    return re.sub(r"\s+", " ", _clean(value)).lower().replace(".", "").replace("_", " ")


def _detect_date_columns(header_row: Sequence[object], second_row: Sequence[object] | None = None) -> list[int]:
    columns: list[int] = []
    for idx, value in enumerate(header_row):
        text = _clean(value)
        if not text:
            continue
        if _DATE_RE.match(text):
            columns.append(idx)
    return columns


def _resolve_assigned_columns(date_col: int, second_row: Sequence[object]) -> tuple[int, int, int]:
    window_start = max(0, date_col - 1)
    window_end = min(len(second_row), date_col + 4)
    candidates = list(enumerate(second_row[window_start:window_end], start=window_start))
    morning_col = next((idx for idx, value in candidates if _normalize_header(_clean(value)).startswith("mattina")), date_col)
    afternoon_col = next((idx for idx, value in candidates if _normalize_header(_clean(value)).startswith("pomeriggio") and idx > morning_col), date_col + 1)
    note_col = next((idx for idx, value in candidates if _normalize_header(_clean(value)).startswith("note") and idx > afternoon_col), date_col + 2)
    return morning_col, afternoon_col, note_col


def _field_index(header_row: Sequence[object]) -> dict[str, int]:
    index: dict[str, int] = {}
    for pos, value in enumerate(header_row):
        key = _normalize_header(value)
        if key:
            index[key] = pos
    return index


def _extract_field(row: Sequence[object], header_index: dict[str, int], *names: str) -> str:
    for name in names:
        pos = header_index.get(name)
        if pos is not None and pos < len(row):
            text = _clean(row[pos])
            if text:
                return text
    return ""


def _parse_volunteer(value: str) -> str:
    render = _clean(value)
    if not render:
        return ""
    return render.replace("\n", " ")


def read_appointments(path: str | Path) -> list[Appointment]:
    workbook = load_workbook(path, read_only=True, data_only=True)
    worksheet = workbook.active
    rows = list(worksheet.iter_rows(values_only=True))
    if not rows:
        raise ValueError("The workbook is empty.")

    header_row = rows[0]
    second_row = rows[1] if len(rows) > 1 else []
    date_columns = _detect_date_columns(header_row, second_row)
    if not date_columns:
        raise ValueError("No date column blocks detected. Check the workbook layout.")

    header_index = _field_index(header_row)
    appointments: list[Appointment] = []

    for row_number, row in enumerate(rows[2:], start=3):
        if not row or all(_clean(cell) == "" for cell in row):
            continue

        if any(_normalize_header(_clean(cell)).startswith("mattina") or _normalize_header(_clean(cell)).startswith("pomeriggio") or _normalize_header(_clean(cell)).startswith("note") for cell in row):
            continue

        record = Appointment(
            code=_extract_field(row, header_index, "codice", "code", "n", "n.", "id"),
            group=_extract_field(row, header_index, "gruppo", "group"),
            referente_gruppo=_extract_field(row, header_index, "referente gruppo", "referente", "referentegruppo"),
            regno=_extract_field(row, header_index, "regno", "regione", "territorio"),
            auto=_extract_field(row, header_index, "auto", "car"),
            ospiti=_extract_field(row, header_index, "ospiti", "guests", "delegati"),
            source_row_number=row_number,
        )

        for date_col in date_columns:
            morning_col, afternoon_col, note_col = _resolve_assigned_columns(date_col, second_row)
            if morning_col >= len(row) or afternoon_col >= len(row) or note_col >= len(row):
                continue

            morning = _parse_volunteer(_clean(row[morning_col]))
            afternoon = _parse_volunteer(_clean(row[afternoon_col]))
            note = _clean(row[note_col])
            date_label = _clean(header_row[date_col])

            if not date_label and not morning and not afternoon and not note:
                continue

            record.assignments.append(
                DayAssignment(
                    date_label=date_label,
                    morning=morning,
                    afternoon=afternoon,
                    note=note,
                )
            )

        if record.assignments or record.code or record.group or record.referente_gruppo:
            appointments.append(record)

    workbook.close()
    return appointments
