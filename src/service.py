from __future__ import annotations

import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path

from src.excel_parser import read_appointments
from src.pdf_generator import write_appointment_pdf, write_user_guide_pdf
from src.resources import resource_path


@dataclass(frozen=True)
class GenerationResult:
    appointment_files: tuple[Path, ...]
    guide_file: Path


def _safe_filename(value: str) -> str:
    cleaned = re.sub(r"[^\w -]", "_", value, flags=re.UNICODE)
    cleaned = re.sub(r"[\s_-]+", "-", cleaned).strip("-")
    return cleaned or "senza-codice"


def default_logo_path() -> Path:
    return resource_path("assets/icon.png")


def generate_documents(
    input_path: str | Path,
    output_dir: str | Path,
    logo_path: str | Path | None = None,
) -> GenerationResult:
    source = Path(input_path)
    destination = Path(output_dir)
    logo = Path(logo_path) if logo_path else default_logo_path()

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

    final_names = [
        f"Appuntamento-{_safe_filename(appointment.group_code)}"
        f"-riga-{appointment.source_row_number}.pdf"
        for appointment in appointments
    ]
    guide_name = "Guida-uso.pdf"

    with tempfile.TemporaryDirectory(prefix=".generazione-", dir=destination) as temp:
        temp_dir = Path(temp)
        for appointment, file_name in zip(appointments, final_names, strict=True):
            write_appointment_pdf(appointment, temp_dir / file_name, logo)
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
