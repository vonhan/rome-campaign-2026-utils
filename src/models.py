from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Volunteer:
    raw: str
    surname: str = ""
    name: str = ""
    phone: str = ""

    @property
    def display_name(self) -> str:
        if self.surname and self.name:
            return f"{self.surname}, {self.name}"
        return self.surname or self.name or self.raw

    @property
    def display(self) -> str:
        if self.phone and (self.surname or self.name):
            return f"{self.display_name}: {self.phone}"
        return self.raw


@dataclass(frozen=True)
class DayAssignment:
    date_label: str
    morning: Volunteer | None = None
    afternoon: Volunteer | None = None
    note: str = ""


@dataclass
class Appointment:
    group_code: str = ""
    group_contact: str = ""
    kingdom_hall: str = ""
    guest_count: str = ""
    guest_vehicle: str = ""
    assignments: list[DayAssignment] = field(default_factory=list)
    source_row_number: int = 0

    @property
    def title(self) -> str:
        return self.group_code or f"Riga {self.source_row_number}"
