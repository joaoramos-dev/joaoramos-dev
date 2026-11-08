#!/usr/bin/env python3
"""Generate the profile SVG with live GitHub statistics."""

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Sequence

from profile_stats.git_history import GitHistoryAnalyzer
from profile_stats.github import GitHubClient
from profile_stats.models import ProfileStats
from profile_stats.render import render_profile
from profile_stats.service import ProfileStatsService
from profile_stats.settings import Settings

PROFILE_FILE = Path(__file__).resolve().parents[1] / "assets" / "profile.svg"


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--placeholder",
        action="store_true",
        help="render the profile with placeholder statistics without using the GitHub API",
    )
    args = parser.parse_args(argv)
    settings = Settings.from_environment()

    if args.placeholder:
        stats = ProfileStats(age=None, repositories=None, commits=None, stars=None, lines_added=None)
    else:
        github = GitHubClient(settings.user, settings.token)
        history = GitHistoryAnalyzer(settings.token, settings.identities)
        stats = ProfileStatsService(github, history).collect(settings.birth_date)

    PROFILE_FILE.write_text(render_profile(stats, settings.user), encoding="utf-8")
    if args.placeholder:
        print(f"Profile SVG written to {PROFILE_FILE}")
    else:
        print(json.dumps(asdict(stats), indent=2))


if __name__ == "__main__":
    main()
