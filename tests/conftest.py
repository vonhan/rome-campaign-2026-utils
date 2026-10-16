from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest
from openpyxl import Workbook


@pytest.fixture
def synthetic_workbook() -> Callable[[Path, list[list[object]] | None], Path]:
    def create(
        path: Path,
        data_rows: list[list[object]] | None = None,
    ) -> Path:
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = "Appuntamenti"
        worksheet.append(
            [
                "Codice Gruppo",
                "Referente Gruppo",
                "Sala del Regno",
                "N. Ospiti",
                "Auto Ospiti",
                "26/10 (Lunedì)",
                "",
                "",
                "27/10 (Martedì)",
                "",
                "",
            ]
        )
        worksheet.append(
            [
                "",
                "",
                "",
                "",
                "",
                "Mattina",
                "Pomeriggio",
                "NOTE",
                "Mattina",
                "Pomeriggio",
                "NOTE",
            ]
        )
        worksheet.merge_cells("F1:H1")
        worksheet.merge_cells("I1:K1")
        rows = data_rows or [
            [
                "RM-01",
                "Referente Sintetico",
                "Sala Centro",
                4,
                "Auto blu",
                "ROSSI, MARIO: 000 111 222",
                "VERDI, ANNA: 000 333 444",
                "Portare il materiale",
                "BIANCHI, LUCA: 000 555 666",
                "",
                "Ingresso laterale",
            ]
        ]
        for row in rows:
            worksheet.append(row)
        workbook.save(path)
        return path

    return create
