from __future__ import annotations

import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path

from src.excel_parser import read_appointments
from src.pdf_generator import (
    write_appointment_pdf,
    write_user_guide_pdf,
    write_volunteer_schedule_pdf,
)
from src.models import Appointment, Volunteer, VolunteerSchedule, VolunteerScheduleEntry
from src.resources import resource_path


@dataclass(frozen=True)
class GenerationResult:
    appointment_files: tuple[Path, ...]
    guide_file: Path


def _safe_filename(value: str, fallback: str = "senza-codice") -> str:
    cleaned = re.sub(r"[^\w -]", "_", value, flags=re.UNICODE)
    cleaned = re.sub(r"[\s_-]+", "-", cleaned).strip("-")
    return cleaned or fallback


def _normalize_generation_mode(mode: str) -> str:
    value = str(mode).strip().lower()
    mapping = {
        "delegato": "delegato",
        "delegate": "delegato",
        "volontario": "volontario",
        "volunteer": "volontario",
    }
    if value not in mapping:
        raise ValueError(
            "Modalità non valida. Scegliere 'delegato' o 'volontario'."
        )
    return mapping[value]


def _appointment_filename(appointment: Appointment) -> str:
    group = _safe_filename(appointment.group_code)
    group_contact = _safe_filename(
        appointment.group_contact,
        fallback="referente-non-specificato",
    )
    prefix = f"Appuntamento-{group_contact}-{group}"
    suffix = f"-riga-{appointment.source_row_number}.pdf"
    max_stem_length = 180 - len(suffix)
    return f"{prefix[:max_stem_length].rstrip('-')}{suffix}"


def _volunteer_schedule_filename(schedule: VolunteerSchedule) -> str:
    name_part = _safe_filename(schedule.volunteer.display_name)
    codes = sorted(
        {entry.group_code for entry in schedule.entries if entry.group_code}
    )
    suffix = ""
    if codes:
        group_part = "-".join(_safe_filename(code) for code in codes[:2])
        suffix = f"-{group_part}"
    stem = f"Volontario-{name_part}{suffix}"
    return f"{stem[:176].rstrip('-')}.pdf"


def _volunteer_schedule_filenames(
    schedules: list[VolunteerSchedule],
) -> list[str]:
    used: dict[str, int] = {}
    filenames: list[str] = []
    for schedule in schedules:
        candidate = _volunteer_schedule_filename(schedule)
        filename_key = candidate.casefold()
        occurrence = used.get(filename_key, 0) + 1
        used[filename_key] = occurrence
        if occurrence > 1:
            suffix = f"-{occurrence}.pdf"
            stem = candidate[:-4]
            candidate = f"{stem[:180 - len(suffix)].rstrip('-')}{suffix}"
        filenames.append(candidate)
    return filenames


def _build_volunteer_schedules(
    appointments: list[Appointment],
) -> list[VolunteerSchedule]:
    schedules: dict[
        tuple[str, str, str],
        tuple[Volunteer, list[VolunteerScheduleEntry]],
    ] = {}

    for appointment in appointments:
        for date_order, assignment in enumerate(appointment.assignments):
            for slot, volunteers in (
                ("Mattina", assignment.morning),
                ("Pomeriggio", assignment.afternoon),
            ):
                seen_in_slot: set[tuple[str, str, str]] = set()
                unique_volunteers: list[Volunteer] = []
                for volunteer in volunteers:
                    if volunteer.identity_key not in seen_in_slot:
                        seen_in_slot.add(volunteer.identity_key)
                        unique_volunteers.append(volunteer)
                for volunteer in unique_volunteers:
                    entry = VolunteerScheduleEntry(
                        volunteer=volunteer,
                        group_code=appointment.group_code,
                        date_label=assignment.date_label,
                        slot=slot,
                        note=assignment.note,
                        source_row_number=appointment.source_row_number,
                        group_contact=appointment.group_contact,
                        kingdom_hall=appointment.kingdom_hall,
                        guest_count=appointment.guest_count,
                        guest_vehicle=appointment.guest_vehicle,
                        date_order=date_order,
                        other_volunteers=tuple(
                            other
                            for other in unique_volunteers
                            if other.identity_key != volunteer.identity_key
                        ),
                    )
                    _, entries = schedules.setdefault(
                        volunteer.identity_key,
                        (volunteer, []),
                    )
                    entries.append(entry)

    ordered: list[VolunteerSchedule] = []
    for volunteer, entries in sorted(
        schedules.values(),
        key=lambda item: (
            item[0].display_name.casefold(),
            item[0].phone.casefold(),
        ),
    ):
        sorted_entries = sorted(
            entries,
            key=lambda entry: (
                entry.date_order,
                entry.source_row_number,
                0 if entry.slot == "Mattina" else 1,
            ),
        )
        ordered.append(
            VolunteerSchedule(volunteer=volunteer, entries=sorted_entries)
        )
    return ordered


def default_logo_path() -> Path:
    campaign_logo = resource_path("assets/Rome_campaign_2026_logo.png")
    if campaign_logo.is_file():
        return campaign_logo
    return resource_path("assets/icon.png")


def generate_documents(
    input_path: str | Path,
    output_dir: str | Path,
    logo_path: str | Path | None = None,
    mode: str = "delegato",
) -> GenerationResult:
    source = Path(input_path)
    destination = Path(output_dir)
    logo = Path(logo_path) if logo_path else default_logo_path()
    generation_mode = _normalize_generation_mode(mode)

    if not source.is_file():
        raise FileNotFoundError(f"File Excel non trovato: {source}")
    if not logo.is_file():
        raise FileNotFoundError(f"Logo non trovato: {logo}")

    appointments = read_appointments(source)
    if not appointments:
        raise ValueError("Nessun appuntamento trovato nel file Excel.")

    destination.mkdir(parents=True, exist_ok=True)
    if not destination.is_dir():
        raise NotADirectoryError(
            f"La destinazione non è una cartella: {destination}"
        )

    guide_name = "Guida-uso.pdf"

    if generation_mode == "delegato":
        final_names = [
            _appointment_filename(appointment) for appointment in appointments
        ]
        schedules: list[VolunteerSchedule] = []
    else:
        schedules = _build_volunteer_schedules(appointments)
        if not schedules:
            raise ValueError(
                "Nessun volontario trovato nelle celle Mattina o Pomeriggio."
            )
        final_names = _volunteer_schedule_filenames(schedules)

    with tempfile.TemporaryDirectory(prefix=".generazione-", dir=destination) as temp:
        temp_dir = Path(temp)
        if generation_mode == "delegato":
            for appointment, file_name in zip(
                appointments, final_names, strict=True
            ):
                write_appointment_pdf(
                    appointment,
                    temp_dir / file_name,
                    logo,
                )
        else:
            for schedule, file_name in zip(schedules, final_names, strict=True):
                write_volunteer_schedule_pdf(
                    schedule.volunteer,
                    schedule.entries,
                    temp_dir / file_name,
                    logo,
                )
        write_user_guide_pdf(temp_dir / guide_name, logo)

        appointment_files: list[Path] = []
        for file_name in final_names:
            target = destination / file_name
            os.replace(temp_dir / file_name, target)
            appointment_files.append(target)
        guide_file = destination / guide_name
        os.replace(temp_dir / guide_name, guide_file)

    return GenerationResult(tuple(appointment_files), guide_file)


def generate_user_guide(
    output_path: str | Path, logo_path: str | Path | None = None
) -> Path:
    logo = Path(logo_path) if logo_path else default_logo_path()
    if not logo.is_file():
        raise FileNotFoundError(f"Logo non trovato: {logo}")
    return write_user_guide_pdf(output_path, logo)
