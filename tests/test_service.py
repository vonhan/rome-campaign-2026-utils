from __future__ import annotations

from pathlib import Path

import pytest
from pypdf import PdfReader

from src import service


def _pdf_text(path: Path) -> str:
    return "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)


def test_generation_is_not_published_partially_after_render_error(
    tmp_path: Path, synthetic_workbook, monkeypatch
) -> None:
    rows = [
        ["ONE", "Primo", "Sala A", 1, "", "", "", "", "", "", ""],
        ["TWO", "Secondo", "Sala B", 2, "", "", "", "", "", "", ""],
    ]
    workbook = synthetic_workbook(tmp_path / "input.xlsx", rows)
    destination = tmp_path / "out"
    original = service.write_appointment_pdf
    calls = 0

    def fail_on_second(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("errore sintetico")
        return original(*args, **kwargs)

    monkeypatch.setattr(service, "write_appointment_pdf", fail_on_second)

    with pytest.raises(OSError, match="errore sintetico"):
        service.generate_documents(workbook, destination, "assets/icon.png")

    assert list(destination.glob("*.pdf")) == []


def test_missing_logo_is_reported(
    tmp_path: Path, synthetic_workbook
) -> None:
    workbook = synthetic_workbook(tmp_path / "input.xlsx")

    with pytest.raises(FileNotFoundError, match="Logo non trovato"):
        service.generate_documents(
            workbook,
            tmp_path / "out",
            tmp_path / "missing.png",
        )


def test_delegato_filename_contains_group_contact_and_not_volunteer_names(
    tmp_path: Path, synthetic_workbook
) -> None:
    workbook = synthetic_workbook(tmp_path / "input.xlsx")

    result = service.generate_documents(workbook, tmp_path / "out", "assets/icon.png")

    assert result.appointment_files[0].name == (
        "Appuntamento-Referente-Sintetico-RM-01-riga-3.pdf"
    )
    assert "ROSSI" not in result.appointment_files[0].name
    assert "VERDI" not in result.appointment_files[0].name


def test_campaign_logo_is_preferred_when_available(monkeypatch, tmp_path: Path) -> None:
    campaign_logo = tmp_path / "assets" / "Rome_campaign_2026_logo.png"
    campaign_logo.parent.mkdir(parents=True)
    campaign_logo.write_bytes(Path("assets/icon.png").read_bytes())
    monkeypatch.setattr(service, "resource_path", lambda relative: tmp_path / relative)

    assert service.default_logo_path() == campaign_logo


def test_default_logo_falls_back_when_campaign_logo_missing(
    monkeypatch, tmp_path: Path
) -> None:
    fallback = tmp_path / "assets" / "icon.png"
    fallback.parent.mkdir(parents=True)
    fallback.write_bytes(Path("assets/icon.png").read_bytes())
    monkeypatch.setattr(service, "resource_path", lambda relative: tmp_path / relative)

    assert service.default_logo_path() == fallback


def test_generate_documents_can_group_by_volunteer(
    tmp_path: Path, synthetic_workbook
) -> None:
    workbook = synthetic_workbook(
        tmp_path / "input.xlsx",
        [
            [
                "RM-01",
                "Referente Uno",
                "Sala A",
                4,
                "Auto A",
                "ROSSI, MARIO: 111",
                "",
                "Note primo appuntamento",
                "ROSSI, MARIO: 111",
                "VERDI, ANNA: 222",
                "Note secondo appuntamento",
            ],
            [
                "RM-02",
                "Referente Due",
                "Sala B",
                3,
                "Auto B",
                "VERDI, ANNA: 222",
                "",
                "Note terzo appuntamento",
                "",
                "ROSSI, MARIO: 111",
                "Note quarto appuntamento",
            ],
        ],
    )

    result = service.generate_documents(
        workbook,
        tmp_path / "out",
        "assets/icon.png",
        mode="volontario",
    )

    names = sorted(path.name for path in result.appointment_files)
    assert names == [
        "Volontario-ROSSI-MARIO-RM-01-RM-02.pdf",
        "Volontario-VERDI-ANNA-RM-01-RM-02.pdf",
    ]
    assert all(path.is_file() for path in result.appointment_files)


def test_volunteer_pdf_contains_complete_appointment_without_counterpart(
    tmp_path: Path, synthetic_workbook
) -> None:
    workbook = synthetic_workbook(
        tmp_path / "input.xlsx",
        [
            [
                "RM-COMPLETE",
                "Delegato Completo",
                "Sala Test Completa",
                7,
                "Auto Ospiti Completa",
                "ROSSI, MARIO: 111",
                "VERDI, ANNA: 222",
                "Nota completa mattina",
                "",
                "",
                "",
            ]
        ],
    )

    result = service.generate_documents(
        workbook,
        tmp_path / "out",
        "assets/icon.png",
        mode="volontario",
    )

    mario_pdf = next(
        path for path in result.appointment_files if "ROSSI-MARIO" in path.name
    )
    text = _pdf_text(mario_pdf)
    assert "RM-COMPLETE" in text
    assert "Delegato Completo" in text
    assert "Sala Test Completa" in text
    assert "7" in text
    assert "Auto Ospiti Completa" in text
    assert "26/10 (Lunedì)" in text
    assert "Mattina" in text
    assert "Nota completa mattina" in text
    assert "VERDI, ANNA" not in text
    assert "222" not in text


def test_volunteer_identity_normalizes_case_and_spaces_but_not_phone(
    tmp_path: Path, synthetic_workbook
) -> None:
    workbook = synthetic_workbook(
        tmp_path / "input.xlsx",
        [
            [
                "RM-01",
                "Delegato Uno",
                "Sala A",
                1,
                "Auto A",
                "ROSSI, MARIO: 111",
                "",
                "Prima occorrenza",
                "",
                "",
                "",
            ],
            [
                "RM-01",
                "Delegato Due",
                "Sala B",
                2,
                "Auto B",
                "  rossi,   mario: 1 11  ",
                "",
                "Seconda occorrenza",
                "",
                "",
                "",
            ],
            [
                "RM-01",
                "Delegato Tre",
                "Sala C",
                3,
                "Auto C",
                "ROSSI, MARIO: 222",
                "",
                "Omonimo differente",
                "",
                "",
                "",
            ],
        ],
    )

    result = service.generate_documents(
        workbook,
        tmp_path / "out",
        "assets/icon.png",
        mode="volontario",
    )

    assert [path.name for path in result.appointment_files] == [
        "Volontario-ROSSI-MARIO-RM-01.pdf",
        "Volontario-ROSSI-MARIO-RM-01-2.pdf",
    ]
    first_text = _pdf_text(result.appointment_files[0])
    second_text = _pdf_text(result.appointment_files[1])
    assert "Prima occorrenza" in first_text
    assert "Seconda occorrenza" in first_text
    assert "Omonimo differente" not in first_text
    assert "Omonimo differente" in second_text


def test_volunteer_generation_is_not_published_after_render_error(
    tmp_path: Path, synthetic_workbook, monkeypatch
) -> None:
    workbook = synthetic_workbook(tmp_path / "input.xlsx")
    destination = tmp_path / "out"

    def fail_render(*args, **kwargs):
        raise OSError("errore volontario sintetico")

    monkeypatch.setattr(service, "write_volunteer_schedule_pdf", fail_render)

    with pytest.raises(OSError, match="errore volontario sintetico"):
        service.generate_documents(
            workbook,
            destination,
            "assets/icon.png",
            mode="volontario",
        )

    assert list(destination.glob("*.pdf")) == []


def test_multiple_volunteers_in_one_slot_receive_separate_pdfs(
    tmp_path: Path, synthetic_workbook
) -> None:
    workbook = synthetic_workbook(
        tmp_path / "input.xlsx",
        [
            [
                "RM-SHARED",
                "Delegato Condiviso",
                "Sala Condivisa",
                5,
                "Auto Condivisa",
                (
                    "Rossi, Mario: 0000000001 e "
                    "Verdi, Paolo: 0000000002 e "
                    "Bianchi, Luca: 0000000003"
                ),
                "",
                "Appuntamento condiviso",
                "",
                "",
                "",
            ]
        ],
    )

    result = service.generate_documents(
        workbook,
        tmp_path / "out",
        "assets/icon.png",
        mode="volontario",
    )

    assert [path.name for path in result.appointment_files] == [
        "Volontario-Bianchi-Luca-RM-SHARED.pdf",
        "Volontario-Rossi-Mario-RM-SHARED.pdf",
        "Volontario-Verdi-Paolo-RM-SHARED.pdf",
    ]
    for path in result.appointment_files:
        text = _pdf_text(path)
        assert "RM-SHARED" in text
        assert "Delegato Condiviso" in text
        assert "Sala Condivisa" in text
        assert "Appuntamento condiviso" in text
    rossi_text = _pdf_text(
        next(path for path in result.appointment_files if "Rossi-Mario" in path.name)
    )
    verdi_text = _pdf_text(
        next(path for path in result.appointment_files if "Verdi-Paolo" in path.name)
    )
    bianchi_text = _pdf_text(
        next(path for path in result.appointment_files if "Bianchi-Luca" in path.name)
    )
    assert "Verdi, Paolo: 0000000002" in rossi_text
    assert "Bianchi, Luca: 0000000003" in rossi_text
    assert "Rossi, Mario: 0000000001" in verdi_text
    assert "Bianchi, Luca: 0000000003" in verdi_text
    assert "Rossi, Mario: 0000000001" in bianchi_text
    assert "Verdi, Paolo: 0000000002" in bianchi_text

    delegate_result = service.generate_documents(
        workbook,
        tmp_path / "out-delegato",
        "assets/icon.png",
        mode="delegato",
    )
    delegate_text = " ".join(
        _pdf_text(delegate_result.appointment_files[0]).split()
    )
    assert "Rossi, Mario: 0000000001" in delegate_text
    assert "Verdi, Paolo: 0000000002" in delegate_text


def test_volunteer_mode_reports_when_no_volunteers_exist(
    tmp_path: Path, synthetic_workbook
) -> None:
    workbook = synthetic_workbook(
        tmp_path / "input.xlsx",
        [
            [
                "RM-EMPTY",
                "Delegato Senza Volontari",
                "Sala Vuota",
                1,
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ]
        ],
    )

    with pytest.raises(ValueError, match="Nessun volontario trovato"):
        service.generate_documents(
            workbook,
            tmp_path / "out",
            "assets/icon.png",
            mode="volontario",
        )
