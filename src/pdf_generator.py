from __future__ import annotations

from html import escape
from io import BytesIO
from pathlib import Path

from reportlab.graphics.shapes import Circle, Drawing, Line, Polygon, Rect
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from src.models import Appointment, Volunteer, VolunteerScheduleEntry


_BLUE = colors.HexColor("#1E4E79")
_LIGHT_BLUE = colors.HexColor("#EAF3F8")
_GOLD = colors.HexColor("#D7A928")
_TEXT = colors.HexColor("#243746")
_MUTED = colors.HexColor("#5F6F7B")

CAMPAIGN_TITLE = "Campagna Speciale Roma 2026"


def _paragraph_text(value: object, empty: str = "—") -> str:
    text = str(value).strip() if value is not None else ""
    return escape(text or empty).replace("\n", "<br/>")


def _volunteer_text(volunteers: tuple[Volunteer, ...]) -> str:
    return _paragraph_text(
        " e ".join(volunteer.display for volunteer in volunteers)
    )


def _logo_image(logo_path: str | Path) -> Image:
    path = Path(logo_path)
    width, height = ImageReader(str(path)).getSize()
    max_width = 34 * mm
    max_height = 22 * mm
    scale = min(max_width / width, max_height / height)
    return Image(str(path), width=width * scale, height=height * scale)


def _icon(kind: str, color: colors.Color = _BLUE) -> Drawing:
    drawing = Drawing(16, 16)
    stroke = color
    if kind == "group":
        drawing.add(Circle(5, 11, 2.2, fillColor=stroke, strokeColor=None))
        drawing.add(Circle(11, 11, 2.2, fillColor=stroke, strokeColor=None))
        drawing.add(Rect(2, 3, 6, 5, rx=2, fillColor=stroke, strokeColor=None))
        drawing.add(Rect(8, 3, 6, 5, rx=2, fillColor=stroke, strokeColor=None))
    elif kind == "location":
        drawing.add(Circle(8, 10, 4, fillColor=None, strokeColor=stroke, strokeWidth=1.5))
        drawing.add(Polygon([5, 8, 8, 2, 11, 8], fillColor=stroke, strokeColor=stroke))
        drawing.add(Circle(8, 10, 1.2, fillColor=stroke, strokeColor=None))
    elif kind == "car":
        drawing.add(Rect(2, 5, 12, 5, rx=1.5, fillColor=None, strokeColor=stroke, strokeWidth=1.5))
        drawing.add(Polygon([4, 10, 6, 13, 11, 13, 13, 10], fillColor=None, strokeColor=stroke, strokeWidth=1.5))
        drawing.add(Circle(5, 4, 1.5, fillColor=stroke, strokeColor=None))
        drawing.add(Circle(12, 4, 1.5, fillColor=stroke, strokeColor=None))
    elif kind == "sun":
        drawing.add(Circle(8, 8, 3.2, fillColor=_GOLD, strokeColor=None))
        for x1, y1, x2, y2 in (
            (8, 1, 8, 3),
            (8, 13, 8, 15),
            (1, 8, 3, 8),
            (13, 8, 15, 8),
            (3, 3, 4.5, 4.5),
            (11.5, 11.5, 13, 13),
            (3, 13, 4.5, 11.5),
            (11.5, 4.5, 13, 3),
        ):
            drawing.add(Line(x1, y1, x2, y2, strokeColor=_GOLD, strokeWidth=1.2))
    else:
        drawing.add(Circle(8, 8, 5, fillColor=None, strokeColor=stroke, strokeWidth=1.5))
        drawing.add(Circle(8, 8, 1.8, fillColor=stroke, strokeColor=None))
    return drawing


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "campaign": ParagraphStyle(
            "CampaignTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=25,
            textColor=_BLUE,
            alignment=0,
            spaceAfter=1,
        ),
        "title": ParagraphStyle(
            "AppointmentTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=17,
            textColor=_GOLD,
            alignment=0,
            spaceAfter=2,
        ),
        "subtitle": ParagraphStyle(
            "AppointmentSubtitle",
            parent=base["BodyText"],
            fontSize=10,
            leading=13,
            textColor=_MUTED,
        ),
        "label": ParagraphStyle(
            "InfoLabel",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=_MUTED,
        ),
        "body": ParagraphStyle(
            "InfoBody",
            parent=base["BodyText"],
            fontSize=10,
            leading=13,
            textColor=_TEXT,
        ),
        "slot": ParagraphStyle(
            "SlotLabel",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=11,
            textColor=_BLUE,
        ),
        "day": ParagraphStyle(
            "DayLabel",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=13,
            textColor=colors.white,
        ),
        "table_header": ParagraphStyle(
            "TableHeader",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=colors.white,
            alignment=1,
        ),
        "compact": ParagraphStyle(
            "CompactBody",
            parent=base["BodyText"],
            fontSize=8,
            leading=10,
            textColor=_TEXT,
        ),
        "guide_heading": ParagraphStyle(
            "GuideHeading",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=_BLUE,
            spaceBefore=9,
            spaceAfter=4,
        ),
    }


def _page_footer(canvas: Canvas, document: SimpleDocTemplate) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(_MUTED)
    canvas.drawString(15 * mm, 8 * mm, CAMPAIGN_TITLE)
    canvas.drawRightString(A4[0] - 15 * mm, 8 * mm, f"Pagina {document.page}")
    canvas.restoreState()


def write_appointment_pdf(
    appointment: Appointment,
    output_path: str | Path,
    logo_path: str | Path,
) -> Path:
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    styles = _styles()
    pdf_buffer = BytesIO()
    document = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=14 * mm,
        leftMargin=14 * mm,
        topMargin=11 * mm,
        bottomMargin=14 * mm,
        title=f"{CAMPAIGN_TITLE} - Appuntamento {appointment.title}",
        author="Rome Campaign 2026 Utils",
    )

    heading = Table(
        [[
            _logo_image(logo_path),
            [
                Paragraph(CAMPAIGN_TITLE, styles["campaign"]),
                Paragraph("Appuntamento di servizio", styles["title"]),
                Paragraph(
                    f"Gruppo {_paragraph_text(appointment.group_code)}",
                    styles["subtitle"],
                ),
            ],
        ]],
        colWidths=[38 * mm, 140 * mm],
    )
    heading.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LINEBELOW", (0, 0), (-1, -1), 1.5, _GOLD),
            ]
        )
    )

    info_rows = [
        (_icon("group"), "REFERENTE GRUPPO", appointment.group_contact),
    ]
    if appointment.group_contact_phone:
        info_rows.append(
            (_icon("group"), "TELEFONO REFERENTE", appointment.group_contact_phone)
        )
    info_rows.extend(
        [
            (_icon("location"), "SALA DEL REGNO", appointment.kingdom_hall),
            (_icon("group"), "NUMERO OSPITI", appointment.guest_count),
            (_icon("car"), "AUTO OSPITI", appointment.guest_vehicle),
        ]
    )
    info_table = Table(
        [
            [
                icon,
                Paragraph(label, styles["label"]),
                Paragraph(_paragraph_text(value), styles["body"]),
            ]
            for icon, label, value in info_rows
        ],
        colWidths=[8 * mm, 38 * mm, 132 * mm],
    )
    info_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), _LIGHT_BLUE),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#BFD5E3")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D7E5ED")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )

    story: list[object] = [
        heading,
        Spacer(1, 4 * mm),
        info_table,
        Spacer(1, 4 * mm),
    ]
    assignment_rows: list[list[object]] = [
        [
            Paragraph("DATA", styles["table_header"]),
            Table(
                [[_icon("sun", colors.white), Paragraph("MATTINA", styles["table_header"])]],
                colWidths=[7 * mm, 41 * mm],
            ),
            Table(
                [[_icon("time", colors.white), Paragraph("POMERIGGIO", styles["table_header"])]],
                colWidths=[7 * mm, 41 * mm],
            ),
            Paragraph("NOTE", styles["table_header"]),
        ]
    ]
    for assignment in appointment.assignments:
        assignment_rows.append(
            [
                Paragraph(_paragraph_text(assignment.date_label), styles["compact"]),
                Paragraph(_volunteer_text(assignment.morning), styles["compact"]),
                Paragraph(_volunteer_text(assignment.afternoon), styles["compact"]),
                Paragraph(_paragraph_text(assignment.note), styles["compact"]),
            ]
        )
    assignments_table = Table(
        assignment_rows,
        colWidths=[28 * mm, 50 * mm, 50 * mm, 50 * mm],
        repeatRows=1,
    )
    assignments_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), _BLUE),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, _LIGHT_BLUE]),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B8CBD7")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(assignments_table)

    document.build(story, onFirstPage=_page_footer, onLaterPages=_page_footer)
    output_file.write_bytes(pdf_buffer.getvalue())
    return output_file


def write_volunteer_schedule_pdf(
    volunteer: Volunteer,
    entries: list[VolunteerScheduleEntry],
    output_path: str | Path,
    logo_path: str | Path,
) -> Path:
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    styles = _styles()
    pdf_buffer = BytesIO()
    document = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=14 * mm,
        leftMargin=14 * mm,
        topMargin=11 * mm,
        bottomMargin=14 * mm,
        title=f"{CAMPAIGN_TITLE} - Volontario {volunteer.display_name}",
        author="Rome Campaign 2026 Utils",
    )

    heading = Table(
        [[
            _logo_image(logo_path),
            [
                Paragraph(CAMPAIGN_TITLE, styles["campaign"]),
                Paragraph("Appuntamenti del volontario", styles["title"]),
                Paragraph(_paragraph_text(volunteer.display), styles["subtitle"]),
            ],
        ]],
        colWidths=[38 * mm, 140 * mm],
    )
    heading.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LINEBELOW", (0, 0), (-1, -1), 1.5, _GOLD),
            ]
        )
    )

    info_rows = [
        (_icon("group"), "TELEFONO", volunteer.phone or "—"),
        (_icon("sun"), "NUMERO APPUNTAMENTI", str(len(entries))),
    ]
    info_table = Table(
        [
            [
                icon,
                Paragraph(label, styles["label"]),
                Paragraph(_paragraph_text(value), styles["body"]),
            ]
            for icon, label, value in info_rows
        ],
        colWidths=[8 * mm, 45 * mm, 120 * mm],
    )
    info_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), _LIGHT_BLUE),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#BFD5E3")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D7E5ED")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )

    story: list[object] = [
        heading,
        Spacer(1, 4 * mm),
        info_table,
        Spacer(1, 4 * mm),
        Paragraph("Elenco degli appuntamenti", styles["guide_heading"]),
    ]
    for entry in entries:
        entry_table = Table(
            [
                [
                    Paragraph(
                        f"<b>{_paragraph_text(entry.date_label)}</b> · "
                        f"{_paragraph_text(entry.slot)}",
                        styles["day"],
                    ),
                    Paragraph(
                        f"GRUPPO {_paragraph_text(entry.group_code)}",
                        styles["day"],
                    ),
                ],
                [
                    Paragraph("CAPOGRUPPO DELEGATO", styles["label"]),
                    Paragraph(
                        _paragraph_text(entry.group_contact),
                        styles["body"],
                    ),
                ],
                [
                    Paragraph("TELEFONO REFERENTE", styles["label"]),
                    Paragraph(
                        _paragraph_text(entry.group_contact_phone or "—"),
                        styles["body"],
                    ),
                ],
                [
                    Paragraph("SALA DEL REGNO", styles["label"]),
                    Paragraph(
                        _paragraph_text(entry.kingdom_hall),
                        styles["body"],
                    ),
                ],
                [
                    Paragraph("NUMERO OSPITI", styles["label"]),
                    Paragraph(
                        _paragraph_text(entry.guest_count),
                        styles["body"],
                    ),
                ],
                [
                    Paragraph("AUTO OSPITI", styles["label"]),
                    Paragraph(
                        _paragraph_text(entry.guest_vehicle),
                        styles["body"],
                    ),
                ],
                [
                    Paragraph("ALTRI VOLONTARI", styles["label"]),
                    Paragraph(
                        _paragraph_text(
                            " e ".join(
                                other.display
                                for other in entry.other_volunteers
                            )
                        ),
                        styles["body"],
                    ),
                ],
                [
                    Paragraph("NOTE", styles["label"]),
                    Paragraph(_paragraph_text(entry.note), styles["body"]),
                ],
            ],
            colWidths=[48 * mm, 126 * mm],
            splitByRow=1,
            splitInRow=1,
        )
        entry_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), _BLUE),
                    ("BACKGROUND", (0, 1), (0, -1), _LIGHT_BLUE),
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B8CBD7")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.extend([entry_table, Spacer(1, 3 * mm)])

    document.build(story, onFirstPage=_page_footer, onLaterPages=_page_footer)
    output_file.write_bytes(pdf_buffer.getvalue())
    return output_file


def write_user_guide_pdf(
    output_path: str | Path, logo_path: str | Path
) -> Path:
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    styles = _styles()
    pdf_buffer = BytesIO()
    document = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=14 * mm,
        bottomMargin=15 * mm,
        title=f"{CAMPAIGN_TITLE} - Guida all'uso",
        author="Rome Campaign 2026 Utils",
    )

    steps = [
        ("1", "Apri il programma", "Fai doppio clic su RomeCampaignPDF.exe."),
        (
            "2",
            "Scegli il file Excel",
            "Premi “Sfoglia” accanto al file Excel e seleziona il file degli appuntamenti.",
        ),
        (
            "3",
            "Scegli la destinazione",
            "Seleziona una cartella in cui salvare i PDF. Puoi crearne una nuova.",
        ),
        (
            "4",
            "Scegli il tipo di PDF",
            "Seleziona gli appuntamenti per capogruppo delegato oppure per capogruppo volontario.",
        ),
        (
            "5",
            "Genera i documenti",
            "Premi “Genera PDF” e attendi il messaggio di completamento.",
        ),
        (
            "6",
            "Apri i risultati",
            "Nella cartella scelta troverai un PDF per ogni delegato o volontario, in base alla modalità scelta, e questa guida.",
        ),
    ]
    step_table = Table(
        [
            [
                Paragraph(
                    f'<font color="#FFFFFF"><b>{number}</b></font>',
                    styles["body"],
                ),
                [
                    Paragraph(f"<b>{escape(title)}</b>", styles["body"]),
                    Paragraph(escape(text), styles["body"]),
                ],
            ]
            for number, title, text in steps
        ],
        colWidths=[12 * mm, 148 * mm],
    )
    step_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), _BLUE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#C9D6DE")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D7E5ED")),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    story: list[object] = [
        Table(
            [[
                _logo_image(logo_path),
                [
                    Paragraph(CAMPAIGN_TITLE, styles["campaign"]),
                    Paragraph("Guida rapida", styles["title"]),
                    Paragraph(
                        "Generatore PDF appuntamenti",
                        styles["subtitle"],
                    ),
                ],
            ]],
            colWidths=[38 * mm, 122 * mm],
        ),
        Spacer(1, 6 * mm),
        Paragraph("Come generare i PDF", styles["guide_heading"]),
        step_table,
        Paragraph("Se compare un errore", styles["guide_heading"]),
        Paragraph(
            "Controlla di aver scelto un file <b>.xlsx</b> con le intestazioni previste "
            "e una cartella in cui puoi salvare file. Il messaggio mostrato indica cosa "
            "correggere; nessun risultato viene dichiarato completato se la generazione fallisce.",
            styles["body"],
        ),
        Paragraph("Protezione dei dati", styles["guide_heading"]),
        Paragraph(
            "I dati degli appuntamenti restano sul computer. Non inviare il file Excel "
            "o i PDF a servizi esterni e non condividerli con persone non autorizzate.",
            styles["body"],
        ),
        Paragraph("Assistenza", styles["guide_heading"]),
        Paragraph(
            "Se il problema continua, comunica al referente tecnico il testo dell'errore, "
            "senza allegare il file Excel né copiare nominativi o numeri di telefono.",
            styles["body"],
        ),
    ]
    document.build(story, onFirstPage=_page_footer, onLaterPages=_page_footer)
    output_file.write_bytes(pdf_buffer.getvalue())
    return output_file
