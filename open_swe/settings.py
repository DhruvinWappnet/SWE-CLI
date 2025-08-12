import os

# model choice (can be "gpt-5", "o4-mini", "groq/..." depending on your infra)
DEFAULT_MODEL = os.getenv("SWE_MODEL", "openai/gpt-oss-20b")
DEFAULT_BASE_BRANCH = os.getenv("SWE_BASE_BRANCH", "test_dev")

# repo root
REPO_ROOT = os.getenv("SWE_REPO_ROOT", ".")

# tests / linter commands (run inside worktree)
DEFAULT_TEST_CMD = os.getenv("SWE_TEST_CMD", "pytest -q")
DEFAULT_LINT_CMD = os.getenv("SWE_LINT_CMD", "flake8 --max-line-length=120")

# safe whitelist for modifications (relative paths)
ALLOWED_PATH_PREFIXES = [
    "src/",
    "app/",
    "swe-cli/",
    "requirements.txt",
    "pyproject.toml",
    "package.json",
]

# worktrees parent dir
WORKTREES_DIR = os.getenv("SWE_WORKTREES_DIR", "/tmp/swe-worktrees")

# dry-run default
DEFAULT_DRY_RUN = True