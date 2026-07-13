"""Minimal GitHub REST client built on the standard library only."""

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

from config import (
    API_ROOT,
    API_VERSION,
    DEFAULT_ACCEPT,
    MAX_RETRIES,
    REQUEST_TIMEOUT_SECONDS,
    RETRY_BACKOFF_SECONDS,
    RETRYABLE_STATUS_CODES,
    USERNAME,
)


class GitHubApiError(RuntimeError):
    """Raised when the GitHub API cannot be reached or returns an error."""


def _build_request(path, params, accept):
    url = f"{API_ROOT}{path}"
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"

    headers = {
        "Accept": accept,
        "X-GitHub-Api-Version": API_VERSION,
        "User-Agent": f"{USERNAME}-profile-readme",
    }
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    return urllib.request.Request(url, headers=headers)


def _should_retry(status_code, attempt):
    return status_code in RETRYABLE_STATUS_CODES and attempt < MAX_RETRIES


def get(path, params=None, accept=DEFAULT_ACCEPT):
    """GET a JSON resource, retrying transient failures with a linear backoff."""
    for attempt in range(1, MAX_RETRIES + 1):
        request = _build_request(path, params, accept)
        try:
            with urllib.request.urlopen(
                request, timeout=REQUEST_TIMEOUT_SECONDS
            ) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            if _should_retry(error.code, attempt):
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
                continue
            raise GitHubApiError(
                f"GET {path} failed: HTTP {error.code} {error.reason}"
            ) from error
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
                continue
            raise GitHubApiError(f"GET {path} failed: {error}") from error

    raise GitHubApiError(f"GET {path} failed after {MAX_RETRIES} attempts")
