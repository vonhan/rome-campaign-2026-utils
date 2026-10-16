from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.service import generate_documents, generate_user_guide


def run_cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Genera PDF di appuntamenti per la campagna di Roma 2026."
    )
    parser.add_argument("--input", help="File Excel .xlsx da elaborare.")
    parser.add_argument("--output", help="Cartella di destinazione dei PDF.")
    parser.add_argument(
        "--guide-only",
        metavar="PDF",
        help="Genera soltanto la guida utente nel percorso indicato.",
    )
    parser.add_argument("--logo", help="Logo alternativo da usare nei PDF.")
    args = parser.parse_args(argv)

    try:
        if args.guide_only:
            if args.input or args.output:
                parser.error("--guide-only non può essere usato con --input o --output.")
            guide = generate_user_guide(Path(args.guide_only), args.logo)
            print(f"Guida utente generata: {guide}")
            return 0

        if not args.input or not args.output:
            parser.error("--input e --output sono obbligatori.")

        result = generate_documents(args.input, args.output, args.logo)
    except (OSError, ValueError) as exc:
        print(f"Errore: {exc}", file=sys.stderr)
        return 1

    print(
        f"Generati {len(result.appointment_files)} PDF di appuntamento "
        f"in {Path(args.output)}."
    )
    print(f"Guida utente: {result.guide_file}")
    return 0
