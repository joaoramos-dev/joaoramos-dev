"""Load and validate runtime settings from the environment."""

import os
from dataclasses import dataclass
from datetime import date
from typing import Mapping


@dataclass(frozen=True)
class Settings:
    user: str
    token: str | None
    emails: tuple[str, ...]
    birth_date: date | None

    @property
    def identities(self) -> tuple[str, ...]:
        return (self.user, *self.emails)

    @classmethod
    def from_environment(cls, environ: Mapping[str, str] | None = None) -> "Settings":
        values = os.environ if environ is None else environ
        user = values.get("GH_USER", "joaoramos-dev").strip()
        if not user:
            raise ValueError("GH_USER must not be empty")

        token = values.get("GH_TOKEN", "").strip() or None
        emails = tuple(
            email.strip()
            for email in values.get("GH_EMAILS", "").split(",")
            if email.strip()
        )
        raw_birth_date = values.get("BIRTH_DATE", "").strip()
        try:
            birth_date = date.fromisoformat(raw_birth_date) if raw_birth_date else None
        except ValueError as error:
            raise ValueError("BIRTH_DATE must use YYYY-MM-DD format") from error

        return cls(user, token, emails, birth_date)
