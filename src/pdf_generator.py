from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from src.models import Appointment, DayAssignment


def _safe_text(value: str) -> str:
    return value.strip() if value else "—"


def _logo_image(logo_path: str | Path | None):
    if not logo_path or not os.path.exists(str(logo_path)):
        return None
    try:
        return Image(str(logo_path), width=26 * mm, height=26 * mm)
    except Exception:
        return None


def write_appointment_pdf(appointment: Appointment, output_path: str | Path, logo_path: str | Path | None = None) -> Path:
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_file),
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleBold", parent=styles["Title"], fontSize=20, leading=24, spaceAfter=8)
    label_style = ParagraphStyle("Label", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=9, leading=12, spaceAfter=2)
    body_style = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=9, leading=12)

    story = []
    logo = _logo_image(logo_path)
    if logo is not None:
        story.append(logo)
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph("Appuntamento di servizio", title_style))
    story.append(Paragraph(f"Gruppo: {_safe_text(appointment.group)}", body_style))
    story.append(Paragraph(f"Referente: {_safe_text(appointment.referente_gruppo)}", body_style))
    story.append(Paragraph(f"Regno: {_safe_text(appointment.regno)}", body_style))
    story.append(Paragraph(f"Auto: {_safe_text(appointment.auto)}", body_style))
    story.append(Paragraph(f"Ospiti/delegati: {_safe_text(appointment.ospiti)}", body_style))
    story.append(Paragraph(f"Codice: {_safe_text(appointment.code)}", body_style))
    story.append(Spacer(1, 5 * mm))

    table_data = [[Paragraph("Data", label_style), Paragraph("Mattina", label_style), Paragraph("Pomeriggio", label_style), Paragraph("Note", label_style)]]
    for assignment in appointment.assignments:
        table_data.append([
            Paragraph(_safe_text(assignment.date_label), body_style),
            Paragraph(_safe_text(assignment.morning), body_style),
            Paragraph(_safe_text(assignment.afternoon), body_style),
            Paragraph(_safe_text(assignment.note), body_style),
        ])

    if len(table_data) == 1:
        table_data.append([Paragraph("Nessuna assegnazione trovata", body_style), "", "", ""])

    table = Table(table_data, colWidths=[32 * mm, 46 * mm, 46 * mm, 58 * mm])
    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9EAF7")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F9FC")]),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ])
    )
    story.append(table)
    doc.build(story)
    return output_file


def write_user_guide_pdf(output_path: str | Path, logo_path: str | Path | None = None) -> Path:
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_file),
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("GuideTitle", parent=styles["Title"], fontSize=20, leading=24, spaceAfter=10)
    heading_style = ParagraphStyle("GuideHeading", parent=styles["Heading2"], fontSize=12, leading=16, spaceBefore=12, spaceAfter=6)
    body_style = ParagraphStyle("GuideBody", parent=styles["BodyText"], fontSize=10, leading=14)
    story = []
    logo = _logo_image(logo_path)
    if logo is not None:
        story.append(logo)
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph("Guida rapida all'uso", title_style))
    story.append(Paragraph("1. Aprire il programma e selezionare il file Excel di input.", body_style))
    story.append(Paragraph("2. Scegliere la cartella dove salvare i PDF generati.", body_style))
    story.append(Paragraph("3. Premere Genera PDF e attendere il completamento.", body_style))
    story.append(Paragraph("4. Verificare la cartella di output e aprire il file PDF desiderato.", body_style))
    story.append(Paragraph("5. Se il file Excel non ha il formato atteso, controllare intestazioni e colonne date.", body_style))
    story.append(Paragraph("Tip: il file di lavoro Excel non viene salvato nel repository e i dati reali non devono essere condivisi fuori dal contesto richiesto.", body_style))
    doc.build(story)
    return output_file
