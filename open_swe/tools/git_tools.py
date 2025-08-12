# Git utilities
import re
import subprocess
import os
from pathlib import Path
from typing import Dict
import shutil
import json
from agents import function_tool

import subprocess
from typing import List, Optional

def _run(cmd: List[str], cwd: Optional[str] = None, capture: bool = True, check: bool = True) -> str:
    """
    Run a shell command safely, optionally capturing output.
    Raises RuntimeError if command fails and check=True.
    """
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=capture)
    if check and result.returncode != 0:
        raise RuntimeError(f"Command {cmd} failed: {result.stderr.strip()}")
    return result.stdout.strip() if capture else ""

def normalize_branch_name(name: str) -> str:
    """
    Normalize branch name to be lowercase, dash-separated, max 120 chars.
    """
    name = name.lower()
    name = re.sub(r"[^a-z0-9\-]+", "-", name)
    name = re.sub(r"-{2,}", "-", name).strip("-")
    return name[:120]



@function_tool(strict_mode=False)
def create_branch(branch_name: str, repo_path: str = ".") -> Dict:
    """
    Create and checkout a git branch in the given repo path.

    Args:
        branch_name (str): Desired branch name.
        repo_path (str): Path to local git repo (default: current directory).

    Returns:
        Dict: { "ok": bool, "branch": str } on success or error info.
    """
    branch = normalize_branch_name(branch_name)
    _run(["git", "fetch"], cwd=repo_path)
    # Check if branch exists locally
    branches = _run(["git", "branch"], cwd=repo_path).split("\n")
    if any(b.strip() == branch for b in branches):
        _run(["git", "checkout", branch], cwd=repo_path)
    else:
        _run(["git", "checkout", "-b", branch], cwd=repo_path)
    return {"ok": True, "branch": branch}

@function_tool(strict_mode=False)
def create_worktree(branch_name: str, repo_path: str = ".", worktrees_dir: str = "/tmp") -> Dict:
    """
    Create a git worktree for a branch and return its path.

    Args:
        branch_name (str): Branch to create worktree for.
        repo_path (str): Path to the git repo.
        worktrees_dir (str): Directory to create worktrees in.

    Returns:
        Dict: { "ok": bool, "worktree_path": str } or error info.
    """
    branch = normalize_branch_name(branch_name)
    base = Path(worktrees_dir)
    base.mkdir(parents=True, exist_ok=True)
    worktree_path = base / f"wt-{branch}"
    if worktree_path.exists():
        shutil.rmtree(worktree_path)
    # Create branch if missing locally (no error if exists)
    _run(["git", "rev-parse", "--verify", branch], cwd=repo_path, check=False)
    _run(["git", "worktree", "add", str(worktree_path), branch], cwd=repo_path)
    return {"ok": True, "worktree_path": str(worktree_path)}

@function_tool(strict_mode=False)
def commit_and_push(message: str, repo_path: str = ".", remote: str = "origin") -> Dict:
    """
    Commit all current changes and push to remote branch.

    Args:
        message (str): Commit message.
        repo_path (str): Path to repo or worktree.
        remote (str): Remote name (default 'origin').

    Returns:
        Dict: { "ok": bool, "branch": str, "sha": str } or error info.
    """
    _run(["git", "add", "-A"], cwd=repo_path)
    try:
        _run(["git", "commit", "-m", message], cwd=repo_path)
    except RuntimeError as e:
        return {"ok": False, "reason": "no_changes_or_commit_failed", "error": str(e)}
    branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_path)
    _run(["git", "push", "--set-upstream", remote, branch], cwd=repo_path)
    sha = _run(["git", "rev-parse", "HEAD"], cwd=repo_path)
    return {"ok": True, "branch": branch, "sha": sha}

@function_tool(strict_mode=False)
def status(repo_path: str = ".") -> Dict:
    """
    Get current git status in porcelain format.

    Args:
        repo_path (str): Path to the git repo.

    Returns:
        Dict: { "ok": True, "status_porcelain": str }
    """
    out = _run(["git", "status", "--porcelain"], cwd=repo_path, check=False)
    return {"ok": True, "status_porcelain": out}

@function_tool(strict_mode=False)
def create_pr(base_branch: str, head_branch: str, title: str, body: str, repo_path: str = ".") -> Dict:
    """
    Create a GitHub Pull Request from head_branch to base_branch with the given title and body.

    Requires `gh` CLI installed and authenticated.

    Args:
        base_branch (str): The branch you want to merge into.
        head_branch (str): The branch with your changes.
        title (str): Title for the PR.
        body (str): Body/description for the PR.
        repo_path (str): Path to the local repo.

    Returns:
        Dict: { "ok": bool } on success or error info.
    """
    try:
        _run([
            "gh", "pr", "create",
            "--base", base_branch,
            "--head", head_branch,
            "--title", title,
            "--body", body
        ], cwd=repo_path)
        return {"ok": True}
    except RuntimeError as e:
        return {"ok": False, "error": str(e)}
    except Exception as e:
        return {"ok": False, "reason": "unexpected_error", "error": str(e)}
