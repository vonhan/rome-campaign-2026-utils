from __future__ import annotations

import argparse
from pathlib import Path

from src.excel_parser import read_appointments
from src.pdf_generator import write_appointment_pdf, write_user_guide_pdf


def run_cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Genera PDF di appuntamenti per la campagna di Roma 2026.")
    parser.add_argument("--input", required=True, help="Percorso del file Excel .xlsx da elaborare.")
    parser.add_argument("--output", required=True, help="Cartella di destinazione dei PDF di appuntamento.")
    parser.add_argument("--guide-output", default=None, help="Cartella di destinazione del PDF guida all'uso.")
    parser.add_argument("--logo", default="assets/icon.png", help="Percorso del file logo usato nei PDF.")
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"File Excel non trovato: {input_path}")

    appointments = read_appointments(input_path)
    if not appointments:
        raise ValueError("Nessun appuntamento trovato nel file Excel.")

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    guide_dir = Path(args.guide_output) if args.guide_output else output_dir
    guide_dir.mkdir(parents=True, exist_ok=True)

    generated = []
    for appointment in appointments:
        file_name = f"{appointment.group or appointment.code or appointment.source_row_number}.pdf"
        safe_name = "".join(ch if ch.isalnum() or ch in (" ", "_", "-", ".") else "_" for ch in file_name).strip()
        generated.append(write_appointment_pdf(appointment, output_dir / safe_name, args.logo))

    guide_file = write_user_guide_pdf(guide_dir / "Guida-uso.pdf", args.logo)
    print(f"Generati {len(generated)} PDF di appuntamento in {output_dir}.")
    print(f"Guida utente: {guide_file}")
    return 0
