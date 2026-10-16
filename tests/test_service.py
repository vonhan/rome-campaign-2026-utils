from __future__ import annotations

from pathlib import Path

import pytest

from src import service


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


def test_generated_filename_contains_group_and_unique_volunteer_names(
    tmp_path: Path, synthetic_workbook
) -> None:
    workbook = synthetic_workbook(tmp_path / "input.xlsx")

    result = service.generate_documents(workbook, tmp_path / "out", "assets/icon.png")

    assert result.appointment_files[0].name == (
        "Appuntamento-RM-01-ROSSI-MARIO-VERDI-ANNA-BIANCHI-LUCA-riga-3.pdf"
    )
