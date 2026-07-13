"""Fetch the GitHub activity that feeds the profile README."""

from datetime import datetime, timezone

from config import (
    COMMIT_MESSAGE_MAX_LENGTH,
    DATE_FORMAT,
    DESCRIPTION_MAX_LENGTH,
    MAX_RECENT_COMMITS,
    MAX_RECENT_ISSUES,
    MAX_RECENT_PULL_REQUESTS,
    MAX_RECENT_REPOS,
    MAX_RECENT_STARS,
    SHORT_SHA_LENGTH,
    STARRED_ACCEPT,
    USERNAME,
)
from github_api import get


def _truncate(text, max_length):
    collapsed = " ".join((text or "").split())
    if len(collapsed) <= max_length:
        return collapsed
    return f"{collapsed[: max_length - 1]}…"


def _first_line(text):
    lines = (text or "").splitlines()
    return lines[0] if lines else ""


def _format_date(timestamp):
    """Accept both '...Z' and '...+08:00' timestamps; report the UTC date."""
    if not timestamp:
        return ""
    parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    return parsed.astimezone(timezone.utc).strftime(DATE_FORMAT)


def _repo_name_from_url(repository_url):
    """Turn https://api.github.com/repos/owner/name into owner/name."""
    marker = "/repos/"
    _, separator, tail = repository_url.partition(marker)
    return tail if separator else repository_url


def fetch_recent_repos():
    """Owned repositories, most recently pushed first."""
    payload = get(
        f"/users/{USERNAME}/repos",
        {
            "sort": "pushed",
            "direction": "desc",
            "type": "owner",
            "per_page": MAX_RECENT_REPOS,
        },
    )
    return [
        {
            "name": repo["name"],
            "url": repo["html_url"],
            "description": _truncate(repo.get("description"), DESCRIPTION_MAX_LENGTH),
            "language": repo.get("language") or "",
            "date": _format_date(repo.get("pushed_at")),
        }
        for repo in payload
    ]


def fetch_recent_commits():
    """Commits authored by the user, newest first.

    The public events API no longer returns a `commits` array (its PushEvent
    payload only carries the head sha), so the commit search endpoint is the
    only source that still yields messages across every repository.
    """
    payload = get(
        "/search/commits",
        {
            "q": f"author:{USERNAME}",
            "sort": "author-date",
            "order": "desc",
            "per_page": MAX_RECENT_COMMITS,
        },
    )
    return [
        {
            "repo": item["repository"]["full_name"],
            "sha": item["sha"][:SHORT_SHA_LENGTH],
            "url": item["html_url"],
            "message": _truncate(
                _first_line(item["commit"]["message"]), COMMIT_MESSAGE_MAX_LENGTH
            ),
            "date": _format_date(item["commit"]["author"]["date"]),
        }
        for item in payload.get("items", [])
    ]


def fetch_recent_stars():
    """Repositories the user starred most recently."""
    payload = get(
        f"/users/{USERNAME}/starred",
        {"per_page": MAX_RECENT_STARS},
        accept=STARRED_ACCEPT,
    )
    return [
        {
            "repo": item["repo"]["full_name"],
            "url": item["repo"]["html_url"],
            "description": _truncate(
                item["repo"].get("description"), DESCRIPTION_MAX_LENGTH
            ),
            "date": _format_date(item.get("starred_at")),
        }
        for item in payload
    ]


def _fetch_authored(kind, limit):
    payload = get(
        "/search/issues",
        {
            "q": f"author:{USERNAME} type:{kind}",
            "sort": "created",
            "order": "desc",
            "per_page": limit,
        },
    )
    return [
        {
            "title": _truncate(item["title"], DESCRIPTION_MAX_LENGTH),
            "url": item["html_url"],
            "repo": _repo_name_from_url(item["repository_url"]),
            "state": item["state"],
            "date": _format_date(item.get("created_at")),
        }
        for item in payload.get("items", [])
    ]


def fetch_recent_pull_requests():
    return _fetch_authored("pr", MAX_RECENT_PULL_REQUESTS)


def fetch_recent_issues():
    return _fetch_authored("issue", MAX_RECENT_ISSUES)
