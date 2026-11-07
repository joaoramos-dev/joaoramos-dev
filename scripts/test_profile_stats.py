"""Tests for profile statistics collection and rendering."""

import json
import unittest
from datetime import date
from typing import Any
from urllib.request import Request
from xml.etree import ElementTree

from profile_stats.github import GitHubClient
from profile_stats.git_history import count_added_lines
from profile_stats.models import ProfileStats, Repository, calculate_age
from profile_stats.render import render_profile
from profile_stats.service import ProfileStatsService
from profile_stats.settings import Settings


class FakeResponse:
    def __init__(self, payload: Any, link: str = "") -> None:
        self._body = json.dumps(payload).encode("utf-8")
        self.headers = {"Link": link}

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self._body


class GitHubClientTests(unittest.TestCase):
    def test_paginates_and_excludes_forks(self) -> None:
        requests: list[Request] = []
        responses = [
            FakeResponse(
                [
                    {"name": "first", "full_name": "joao/first", "fork": False, "stargazers_count": 3},
                    {"name": "fork", "full_name": "joao/fork", "fork": True, "stargazers_count": 20},
                ],
                '<https://api.github.com/user/repos?page=2>; rel="next"',
            ),
            FakeResponse([
                {"name": "second", "full_name": "joao/second", "fork": False, "stargazers_count": 4},
            ]),
        ]

        def opener(request: Request, timeout: int) -> FakeResponse:
            requests.append(request)
            return responses.pop(0)

        repositories = GitHubClient("test-token", opener).owned_repositories()

        self.assertEqual(
            repositories,
            [
                Repository("first", "joao/first", 3),
                Repository("second", "joao/second", 4),
            ],
        )
        self.assertEqual(len(requests), 2)
        self.assertEqual(requests[0].get_header("Authorization"), "Bearer test-token")


class ProfileStatsTests(unittest.TestCase):
    def test_calculates_age_before_and_on_birthday(self) -> None:
        birth_date = date(2000, 7, 10)
        self.assertEqual(calculate_age(birth_date, date(2026, 7, 9)), 25)
        self.assertEqual(calculate_age(birth_date, date(2026, 7, 10)), 26)

    def test_settings_normalize_environment_values(self) -> None:
        settings = Settings.from_environment({
            "GH_USER": " joao ",
            "GH_TOKEN": " token ",
            "GH_EMAILS": " one@example.com, ,two@example.com ",
            "BIRTH_DATE": "2000-07-10",
        })
        self.assertEqual(settings.user, "joao")
        self.assertEqual(settings.token, "token")
        self.assertEqual(settings.identities, ("joao", "one@example.com", "two@example.com"))
        self.assertEqual(settings.birth_date, date(2000, 7, 10))

    def test_counts_only_numeric_non_generated_additions(self) -> None:
        numstat = (
            "4\t0\tsrc/app.py\n"
            "12\t1\tassets/app.min.js\n"
            "-\t-\tassets/logo.png\n"
            "3\t0\tCargo.lock\n"
        )
        self.assertEqual(count_added_lines(numstat), 4)

    def test_service_aggregates_repository_and_history_stats(self) -> None:
        class FakeGitHub:
            def owned_repositories(self) -> list[Repository]:
                return [Repository("one", "joao/one", 3), Repository("two", "joao/two", 4)]

        class FakeHistory:
            def analyze(self, repositories: list[Repository]) -> tuple[int, int]:
                self.repositories = repositories
                return 12, 340

        service = ProfileStatsService(FakeGitHub(), FakeHistory())
        stats = service.collect(date(2000, 7, 10), date(2026, 7, 10))

        self.assertEqual(stats, ProfileStats(26, 2, 12, 7, 340))

    def test_renderer_outputs_valid_svg_with_metric_icons_and_links(self) -> None:
        stats = ProfileStats(26, 2, 12, 7, 340)
        svg = render_profile(stats, "joao<&")
        root = ElementTree.fromstring(svg)
        namespace = {"svg": "http://www.w3.org/2000/svg"}
        visible_text = "".join(node.text or "" for node in root.iter())

        self.assertIn("stats --user joao&lt;&amp;", svg)
        self.assertIn("STARS", visible_text)
        self.assertEqual(len(root.findall(".//svg:a", namespace)), 2)
        self.assertEqual(
            len([
                group for group in root.findall(".//svg:g", namespace)
                if group.attrib.get("transform", "").startswith("translate(")
            ]),
            5,
        )
        self.assertEqual(len(root.findall(".//svg:animate", namespace)), 2)


if __name__ == "__main__":
    unittest.main()
