"""Configuration for the profile README builder."""

from pathlib import Path

USERNAME = "xxnjdlys"

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = REPO_ROOT / "README.template.md"
OUTPUT_PATH = REPO_ROOT / "README.md"

API_ROOT = "https://api.github.com"
API_VERSION = "2022-11-28"
DEFAULT_ACCEPT = "application/vnd.github+json"
STARRED_ACCEPT = "application/vnd.github.star+json"

REQUEST_TIMEOUT_SECONDS = 20
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2
RETRYABLE_STATUS_CODES = frozenset({403, 429, 500, 502, 503, 504})

MAX_RECENT_REPOS = 5
MAX_RECENT_COMMITS = 5
MAX_RECENT_STARS = 5
MAX_RECENT_PULL_REQUESTS = 5
MAX_RECENT_ISSUES = 5

COMMIT_MESSAGE_MAX_LENGTH = 72
DESCRIPTION_MAX_LENGTH = 80
SHORT_SHA_LENGTH = 7

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S UTC"
DATE_FORMAT = "%Y-%m-%d"
EMPTY_PLACEHOLDER = "_暂无数据_"
