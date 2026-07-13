"""Render README.md from README.template.md with fresh GitHub activity.

Usage: python scripts/build_readme.py
Reads GITHUB_TOKEN from the environment (optional locally, required in CI to
avoid the low anonymous rate limit).
"""

import sys
from datetime import datetime, timezone

from activity import (
    fetch_recent_commits,
    fetch_recent_issues,
    fetch_recent_pull_requests,
    fetch_recent_repos,
    fetch_recent_stars,
)
from config import OUTPUT_PATH, TEMPLATE_PATH, TIMESTAMP_FORMAT
from github_api import GitHubApiError
from render import render_commits, render_issue_like, render_repos, render_stars


def _utc_now():
    return datetime.now(timezone.utc).strftime(TIMESTAMP_FORMAT)


def collect_sections():
    """Fetch every activity feed and render it to Markdown."""
    return {
        "RECENT_REPOS": render_repos(fetch_recent_repos()),
        "RECENT_COMMITS": render_commits(fetch_recent_commits()),
        "RECENT_STARS": render_stars(fetch_recent_stars()),
        "RECENT_PULL_REQUESTS": render_issue_like(fetch_recent_pull_requests()),
        "RECENT_ISSUES": render_issue_like(fetch_recent_issues()),
        "LAST_SYNC": _utc_now(),
    }


def fill(template, sections):
    """Replace every {{PLACEHOLDER}} in the template. Unknown ones are an error."""
    filled = template
    for key, value in sections.items():
        filled = filled.replace(f"{{{{{key}}}}}", value)

    if "{{" in filled:
        start = filled.index("{{")
        raise ValueError(f"模板里有未填充的占位符: {filled[start : start + 40]!r}")

    return filled


def main():
    if not TEMPLATE_PATH.exists():
        print(f"找不到模板文件: {TEMPLATE_PATH}", file=sys.stderr)
        return 1

    try:
        sections = collect_sections()
    except GitHubApiError as error:
        print(f"抓取 GitHub 数据失败: {error}", file=sys.stderr)
        return 1

    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    try:
        rendered = fill(template, sections)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 1

    OUTPUT_PATH.write_text(rendered, encoding="utf-8")
    print(f"已生成 {OUTPUT_PATH.name}，Last sync: {sections['LAST_SYNC']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
