"""Domain models and calculations for profile statistics."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Repository:
    name: str
    full_name: str
    stars: int


@dataclass(frozen=True)
class ProfileStats:
    age: int | None
    repositories: int | None
    commits: int | None
    stars: int | None
    lines_added: int | None


def calculate_age(birth_date: date, today: date) -> int:
    """Return the age in whole years on the given date."""
    return today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )
