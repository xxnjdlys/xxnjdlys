"""Turn activity records into the Markdown fragments injected into the README."""

from config import EMPTY_PLACEHOLDER

STATE_ICONS = {"open": "🟢", "closed": "🟣"}


def _as_list(lines):
    if not lines:
        return EMPTY_PLACEHOLDER
    return "\n".join(lines)


def _suffix(parts):
    """Join the optional trailing bits of a bullet, e.g. ' — Python · 2026-07-11'."""
    kept = [part for part in parts if part]
    if not kept:
        return ""
    return f" — {' · '.join(kept)}"


def render_repos(repos):
    return _as_list(
        [
            f"- [**{repo['name']}**]({repo['url']})"
            + _suffix([repo["description"], repo["language"], repo["date"]])
            for repo in repos
        ]
    )


def render_commits(commits):
    return _as_list(
        [
            f"- [`{commit['sha']}`]({commit['url']}) {commit['message']}"
            + _suffix([f"`{commit['repo']}`", commit["date"]])
            for commit in commits
        ]
    )


def render_stars(stars):
    return _as_list(
        [
            f"- ⭐ [**{star['repo']}**]({star['url']})"
            + _suffix([star["description"], star["date"]])
            for star in stars
        ]
    )


def render_issue_like(items):
    return _as_list(
        [
            f"- {STATE_ICONS.get(item['state'], '⚪')} [{item['title']}]({item['url']})"
            + _suffix([f"`{item['repo']}`", item["date"]])
            for item in items
        ]
    )
