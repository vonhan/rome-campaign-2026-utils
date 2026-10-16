from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class DayAssignment:
    date_label: str
    morning: str = ""
    afternoon: str = ""
    note: str = ""


@dataclass
class Appointment:
    code: str = ""
    group: str = ""
    referente_gruppo: str = ""
    regno: str = ""
    auto: str = ""
    ospiti: str = ""
    assignments: List[DayAssignment] = field(default_factory=list)
    source_row_number: int = 0

    @property
    def title(self) -> str:
        if self.group:
            return self.group
        return self.code or "Appuntamento"
