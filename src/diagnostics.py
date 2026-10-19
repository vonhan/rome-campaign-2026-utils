from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationIssue:
    sheet: str
    cell: str
    row_number: int
    field: str
    reason: str
    date_label: str = ""

    def format(self) -> str:
        context = [
            f"Foglio '{self.sheet}'",
            f"cella {self.cell}",
            f"riga {self.row_number}",
        ]
        if self.date_label:
            context.append(self.date_label)
        context.append(self.field)
        return f"{' - '.join(context)}: {self.reason}"


class WorkbookValidationError(ValueError):
    def __init__(self, issues: list[ValidationIssue]) -> None:
        if not issues:
            raise ValueError("WorkbookValidationError richiede almeno un errore.")
        self.issues = tuple(issues)
        super().__init__(self._message())

    def _message(self) -> str:
        count = len(self.issues)
        heading = (
            "È stato rilevato 1 errore nel file Excel."
            if count == 1
            else f"Sono stati rilevati {count} errori nel file Excel."
        )
        return "\n".join(
            [heading, *(f"- {issue.format()}" for issue in self.issues)]
        )
