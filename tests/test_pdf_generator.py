from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from src.models import Appointment, DayAssignment, Volunteer, VolunteerScheduleEntry
from src.pdf_generator import (
    write_appointment_pdf,
    write_user_guide_pdf,
    write_volunteer_schedule_pdf,
)


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
                morning=(
                    Volunteer(
                        raw="ROSSI MARIO 000",
                        full_name="ROSSI MARIO",
                        phone="000",
                    ),
                ),
                note="Nota sintetica & verificabile",
            )
        ],
        source_row_number=3,
    )
    output = tmp_path / "appointment.pdf"

    write_appointment_pdf(appointment, output, Path("assets/icon.png"))

    reader = PdfReader(output)
    text = " ".join(_pdf_text(output).split())
    assert len(reader.pages) == 1
    assert "Campagna Speciale Roma 2026" in text
    assert "Appuntamento di servizio" in text
    assert "TEST-01" in text
    assert "Referente & Collaboratore" in text
    assert "Sala Città" in text
    assert "Auto <test>" in text
    assert "ROSSI MARIO 000" in text
    assert "Nota sintetica & verificabile" in text


def test_user_guide_pdf_contains_usage_and_privacy_instructions(
    tmp_path: Path,
) -> None:
    output = tmp_path / "guide.pdf"

    write_user_guide_pdf(output, Path("assets/icon.png"))

    text = " ".join(_pdf_text(output).split())
    assert "Campagna Speciale Roma 2026" in text
    assert "Guida rapida" in text
    assert "Scegli il file Excel" in text
    assert "Scegli il tipo di PDF" in text
    assert "capogruppo delegato" in text
    assert "capogruppo volontario" in text
    assert "Mattina" in text
    assert "Pomeriggio" in text
    assert "UNIONI" in text
    assert "NOME COMPLETO TELEFONO" in text
    assert "punto e virgola" in text
    assert "Codice Gruppo" in text
    assert "codice, referente e numero di telefono" in text
    assert "Auto Ospiti" in text
    assert "non vengono mostrati" in text
    assert "Log elaborazione" in text
    assert "Protezione dei dati" in text
    assert "senza allegare il file Excel" in text


def test_typical_seven_day_appointment_fits_on_one_page(
    tmp_path: Path,
) -> None:
    assignments = [
        DayAssignment(
            date_label=f"{26 + day}/10",
            morning=(Volunteer(raw="ROSSI MARIO 000111222"),),
            afternoon=(Volunteer(raw="VERDI ANNA 000333444"),),
            note="Nota sintetica",
        )
        for day in range(6)
    ]
    assignments.append(
        DayAssignment(
            date_label="01/11",
            morning=(Volunteer(raw="BIANCHI LUCA 000555666"),),
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


def test_appointment_pdf_renders_with_campaign_logo(tmp_path: Path) -> None:
    appointment = Appointment(
        group_code="LOGO-01",
        group_contact="Referente Sintetico",
        kingdom_hall="Sala Centro",
        guest_count="2",
        guest_vehicle="Auto blu",
        assignments=[
            DayAssignment(
                date_label="26/10 (Lunedì)",
                morning=(Volunteer(raw="ROSSI MARIO 000111222"),),
                note="Nota sintetica",
            )
        ],
        source_row_number=3,
    )
    output = tmp_path / "campaign-logo.pdf"

    write_appointment_pdf(
        appointment, output, Path("assets/Rome_campaign_2026_logo.png")
    )

    reader = PdfReader(output)
    assert len(reader.pages) == 1
    assert output.stat().st_size > 0
    assert "Campagna Speciale Roma 2026" in _pdf_text(output)


def test_documents_keep_their_own_titles(tmp_path: Path) -> None:
    appointment = Appointment(
        group_code="TITOLI-01",
        assignments=[DayAssignment(date_label="26/10")],
        source_row_number=3,
    )
    appointment_pdf = tmp_path / "appointment.pdf"
    guide_pdf = tmp_path / "guide.pdf"
    logo = Path("assets/icon.png")

    write_appointment_pdf(appointment, appointment_pdf, logo)
    write_user_guide_pdf(guide_pdf, logo)

    appointment_title = PdfReader(appointment_pdf).metadata.title
    guide_title = PdfReader(guide_pdf).metadata.title
    assert appointment_title == "Campagna Speciale Roma 2026 - Appuntamento TITOLI-01"
    assert guide_title == "Campagna Speciale Roma 2026 - Guida all'uso"


def test_volunteer_schedule_flows_across_pages_without_losing_entries(
    tmp_path: Path,
) -> None:
    volunteer = Volunteer(
        raw="ROSSI MARIO 000",
        full_name="ROSSI MARIO",
        phone="000",
    )
    entries = [
        VolunteerScheduleEntry(
            volunteer=volunteer,
            group_code=f"GRUPPO-{index:02d}",
            group_contact=f"Delegato {index}",
            kingdom_hall=f"Sala {index}",
            guest_count=str(index),
            guest_vehicle=f"Auto {index}",
            date_label=f"{index:02d}/11",
            slot="Mattina" if index % 2 else "Pomeriggio",
            note=(
                f"Nota appuntamento {index} con contenuto sintetico "
                "sufficientemente lungo per verificare l'impaginazione."
            ),
            source_row_number=index + 2,
            date_order=index,
        )
        for index in range(1, 13)
    ]
    output = tmp_path / "volunteer-many.pdf"

    write_volunteer_schedule_pdf(
        volunteer,
        entries,
        output,
        Path("assets/icon.png"),
    )

    reader = PdfReader(output)
    text = _pdf_text(output)
    assert len(reader.pages) > 1
    for index in range(1, 13):
        assert f"GRUPPO-{index:02d}" in text
        assert f"Delegato {index}" in text
        assert f"Sala {index}" in text
        assert f"Auto {index}" not in text
        assert f"Nota appuntamento {index}" not in text
