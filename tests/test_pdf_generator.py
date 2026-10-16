from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from src.models import Appointment, DayAssignment, Volunteer
from src.pdf_generator import write_appointment_pdf, write_user_guide_pdf


def _pdf_text(path: Path) -> str:
    return "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)


def test_appointment_pdf_contains_all_sections_and_escaped_text(
    tmp_path: Path,
) -> None:
    appointment = Appointment(
        group_code="TEST-01",
        group_contact="Referente & Collaboratore",
        kingdom_hall="Sala Città",
        guest_count="3",
        guest_vehicle="Auto <test>",
        assignments=[
            DayAssignment(
                date_label="26/10 (Lunedì)",
                morning=Volunteer(
                    raw="ROSSI, MARIO: 000",
                    surname="ROSSI",
                    name="MARIO",
                    phone="000",
                ),
                afternoon=None,
                note="Nota sintetica & verificabile",
            )
        ],
        source_row_number=3,
    )
    output = tmp_path / "appointment.pdf"

    write_appointment_pdf(appointment, output, Path("assets/icon.png"))

    reader = PdfReader(output)
    text = _pdf_text(output)
    assert len(reader.pages) == 1
    assert "Appuntamento di servizio" in text
    assert "TEST-01" in text
    assert "Referente & Collaboratore" in text
    assert "Sala Città" in text
    assert "Auto <test>" in text
    assert "ROSSI, MARIO: 000" in text
    assert "Nota sintetica & verificabile" in text


def test_user_guide_pdf_contains_usage_and_privacy_instructions(
    tmp_path: Path,
) -> None:
    output = tmp_path / "guide.pdf"

    write_user_guide_pdf(output, Path("assets/icon.png"))

    text = _pdf_text(output)
    assert "Guida rapida" in text
    assert "Scegli il file Excel" in text
    assert "Protezione dei dati" in text
    assert "senza allegare il file Excel" in text


def test_typical_seven_day_appointment_fits_on_one_page(
    tmp_path: Path,
) -> None:
    assignments = [
        DayAssignment(
            date_label=f"{26 + day}/10",
            morning=Volunteer(raw="ROSSI, MARIO: 000 111 222"),
            afternoon=Volunteer(raw="VERDI, ANNA: 000 333 444"),
            note="Nota sintetica",
        )
        for day in range(6)
    ]
    assignments.append(
        DayAssignment(
            date_label="01/11",
            morning=Volunteer(raw="BIANCHI, LUCA: 000 555 666"),
            note="Nota sintetica",
        )
    )
    appointment = Appointment(
        group_code="SETTE-GIORNI",
        group_contact="Referente Sintetico",
        kingdom_hall="Sala Centro",
        guest_count="4",
        guest_vehicle="Auto blu",
        assignments=assignments,
        source_row_number=3,
    )
    output = tmp_path / "seven-days.pdf"

    write_appointment_pdf(appointment, output, Path("assets/icon.png"))

    assert len(PdfReader(output).pages) == 1
