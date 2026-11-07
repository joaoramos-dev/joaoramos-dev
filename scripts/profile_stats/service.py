"""Application service that combines GitHub and Git history data."""

from datetime import date, datetime, timezone
from typing import Protocol, Sequence

from profile_stats.models import ProfileStats, Repository, calculate_age


class RepositorySource(Protocol):
    def owned_repositories(self) -> list[Repository]: ...


class HistoryAnalyzer(Protocol):
    def analyze(self, repositories: Sequence[Repository]) -> tuple[int, int]: ...


class ProfileStatsService:
    def __init__(self, github: RepositorySource, history: HistoryAnalyzer) -> None:
        self._repositories = github
        self._history = history

    def collect(self, birth_date: date | None, today: date | None = None) -> ProfileStats:
        repositories = self._repositories.owned_repositories()
        commits, lines_added = self._history.analyze(repositories)
        current_date = today or datetime.now(timezone.utc).date()
        stars = sum(repository.stars for repository in repositories)
        age = calculate_age(birth_date, current_date) if birth_date else None

        return ProfileStats(
            age=age,
            repositories=len(repositories),
            commits=commits,
            stars=stars,
            lines_added=lines_added,
        )
