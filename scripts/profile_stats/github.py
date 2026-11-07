"""GitHub API client for owned repository metadata."""

import json
import re
from typing import Any, Callable
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from profile_stats.models import Repository

API_URL = "https://api.github.com"
REPOSITORIES_PATH = "/user/repos?affiliation=owner&visibility=all&per_page=100"


class GitHubClient:
    def __init__(self, token: str, opener: Callable[..., Any] = urlopen) -> None:
        self._token = token
        self._opener = opener

    def owned_repositories(self) -> list[Repository]:
        repositories = self._paginate(REPOSITORIES_PATH)
        return [
            Repository(
                name=str(repository["name"]),
                full_name=str(repository["full_name"]),
                stars=int(repository["stargazers_count"]),
            )
            for repository in repositories
            if not repository["fork"]
        ]

    def _paginate(self, path: str) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        url: str | None = urljoin(API_URL, path)

        while url is not None:
            payload, link_header = self._get(url)
            if not isinstance(payload, list) or any(
                not isinstance(repository, dict) for repository in payload
            ):
                raise ValueError("GitHub repository response must be a list of objects")
            items.extend(payload)
            url = self._next_page(link_header)

        return items

    def _get(self, url: str) -> tuple[Any, str]:
        request = Request(
            url,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "profile-stats",
            },
        )
        with self._opener(request, timeout=30) as response:
            return json.load(response), response.headers.get("Link", "")

    @staticmethod
    def _next_page(link_header: str) -> str | None:
        for link in link_header.split(","):
            match = re.match(r'\s*<([^>]+)>;\s*rel="next"', link)
            if match:
                return match.group(1)
        return None
