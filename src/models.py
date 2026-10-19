from __future__ import annotations

import re
from dataclasses import dataclass, field


def _normalize_identity_part(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().casefold()


def _normalize_phone(value: str) -> str:
    digits = re.sub(r"\D", "", value)
    return digits or _normalize_identity_part(value)


@dataclass(frozen=True)
class Volunteer:
    raw: str
    full_name: str = ""
    phone: str = ""

    @property
    def display_name(self) -> str:
        return self.full_name or self.raw

    @property
    def display(self) -> str:
        if self.phone and self.full_name:
            return f"{self.display_name} {self.phone}"
        return self.raw

    @property
    def identity_key(self) -> tuple[str, str]:
        if self.full_name or self.phone:
            return (
                _normalize_identity_part(self.full_name),
                _normalize_phone(self.phone),
            )
        return (_normalize_identity_part(self.raw), "")


@dataclass(frozen=True)
class DayAssignment:
    date_label: str
    morning: tuple[Volunteer, ...] = ()
    afternoon: tuple[Volunteer, ...] = ()
    union_group_code: tuple[str, ...] = ()
    note: str = ""


@dataclass
class Appointment:
    group_code: str = ""
    group_contact: str = ""
    group_contact_phone: str = ""
    kingdom_hall: str = ""
    guest_count: str = ""
    guest_vehicle: str = ""
    assignments: list[DayAssignment] = field(default_factory=list)
    source_row_number: int = 0

    @property
    def title(self) -> str:
        return self.group_code or f"Riga {self.source_row_number}"


@dataclass(frozen=True)
class UnionGroupInfo:
    group_code: str = ""
    group_contact: str = ""
    group_contact_phone: str = ""


@dataclass(frozen=True)
class VolunteerScheduleEntry:
    volunteer: Volunteer
    group_code: str = ""
    union_group_code: tuple[str, ...] = ()
    union_group_details: tuple[UnionGroupInfo, ...] = ()
    date_label: str = ""
    slot: str = ""
    note: str = ""
    source_row_number: int = 0
    group_contact: str = ""
    group_contact_phone: str = ""
    kingdom_hall: str = ""
    guest_count: str = ""
    guest_vehicle: str = ""
    date_order: int = 0
    other_volunteers: tuple[Volunteer, ...] = ()


@dataclass(frozen=True)
class VolunteerSchedule:
    volunteer: Volunteer
    entries: list[VolunteerScheduleEntry] = field(default_factory=list)
