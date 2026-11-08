"""Analyze authored commits and added lines in owned repositories."""

import re
import subprocess
import tempfile
from pathlib import Path
from typing import Sequence

from profile_stats.models import Repository

IGNORED_PATHS = re.compile(
    r"(package-lock\.json|yarn\.lock|pnpm-lock\.yaml|poetry\.lock|Cargo\.lock"
    r"|\.min\.(js|css)$|\.(glb|gltf|bin|png|jpe?g|gif|webp|ico|woff2?|ttf|otf|pdf|zip)$)",
    re.IGNORECASE,
)


def count_added_lines(numstat: str) -> int:
    added = 0
    for line in numstat.splitlines():
        parts = line.split("\t")
        if len(parts) != 3 or parts[0] == "-" or IGNORED_PATHS.search(parts[2]):
            continue
        added += int(parts[0])
    return added


class GitHistoryAnalyzer:
    def __init__(self, token: str | None, identities: Sequence[str]) -> None:
        self._token = token
        self._identities = tuple(identity for identity in identities if identity)
        if not self._identities:
            raise ValueError("At least one commit author identity is required")
        author_pattern = "|".join(re.escape(identity) for identity in self._identities)
        self._log_options = (
            "log",
            "--all",
            "--no-merges",
            "-E",
            f"--author=({author_pattern})",
        )

    def analyze(self, repositories: Sequence[Repository]) -> tuple[int, int]:
        commit_count = 0
        added_lines = 0

        with tempfile.TemporaryDirectory() as temporary_directory:
            for repository in repositories:
                destination = Path(temporary_directory) / repository.name
                if self._token:
                    remote = (
                        f"https://x-access-token:{self._token}@github.com/"
                        f"{repository.full_name}.git"
                    )
                else:
                    remote = f"https://github.com/{repository.full_name}.git"
                self._run_git(
                    ["clone", "--quiet", "--no-tags", remote, str(destination)],
                    repository,
                )
                hashes = self._run_git(
                    ["-C", str(destination), *self._log_options, "--format=%H"],
                    repository,
                )
                numstat = self._run_git(
                    ["-C", str(destination), *self._log_options, "--numstat", "--format="],
                    repository,
                )
                commit_count += len(hashes.splitlines())
                added_lines += count_added_lines(numstat)

        return commit_count, added_lines

    def _run_git(self, arguments: list[str], repository: Repository) -> str:
        try:
            result = subprocess.run(
                ["git", *arguments],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as error:
            details = (error.stderr or error.stdout or "unknown Git error").strip()
            if self._token:
                details = details.replace(self._token, "[REDACTED]")
            raise RuntimeError(f"Git failed for {repository.full_name}: {details}") from None
        return result.stdout
