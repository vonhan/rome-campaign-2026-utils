from __future__ import annotations

from pathlib import Path

from src.models import Appointment, DayAssignment
from src.pdf_generator import write_appointment_pdf, write_user_guide_pdf


def test_write_appointment_pdf_creates_file(tmp_path: Path) -> None:
    appointment = Appointment(
        code="A-999",
        group="Gruppo Test",
        referente_gruppo="Rossi, Marco",
        regno="Roma",
        auto="Auto 5",
        ospiti="Delegati vari",
        assignments=[
            DayAssignment(date_label="26/10 (Lunedì)", morning="Neri, Carlo: 333444555", afternoon="Rossi, Luca: 444555666", note="Note generiche")
        ],
    )
    output_path = tmp_path / "appointment.pdf"
    created = write_appointment_pdf(appointment, output_path, Path("assets/icon.png"))

    assert created.exists()
    assert created.stat().st_size > 0


def test_write_user_guide_pdf_creates_file(tmp_path: Path) -> None:
    output_path = tmp_path / "guide.pdf"
    created = write_user_guide_pdf(output_path, Path("assets/icon.png"))

    assert created.exists()
    assert created.stat().st_size > 0
