# Git utilities
import subprocess
import os
from pathlib import Path
from typing import Dict
import shutil

try:
    from agents import function_tool
except Exception:
    def function_tool(func=None, **_):
        if func is None:
            def dec(f): return f
            return dec
        return func

def _run(cmd, cwd=None, capture=True, check=True):
    res = subprocess.run(cmd, cwd=cwd, text=True, capture_output=capture)
    if check and res.returncode != 0:
        raise RuntimeError(f"Command {cmd} failed: {res.stderr}")
    return res.stdout.strip()

def normalize_branch_name(s: str) -> str:
    import re
    s = s.lower()
    s = re.sub(r'[^a-z0-9\-]+', '-', s)
    s = re.sub(r'-{2,}', '-', s).strip('-')
    return s[:120]

@function_tool
def create_branch(branch_name: str, repo_path: str = ".") -> Dict:
    """
    Creates and checks out a branch in repo_path.
    """
    branch = normalize_branch_name(branch_name)
    _run(["git", "fetch"], cwd=repo_path)
    _run(["git", "checkout", "-b", branch], cwd=repo_path)
    return {"ok": True, "branch": branch}

@function_tool
def create_worktree(branch_name: str, repo_path: str = ".", worktrees_dir: str = "/tmp") -> Dict:
    """
    Create a git worktree for branch_name and return the worktree path.
    """
    branch = normalize_branch_name(branch_name)
    wt_base = Path(worktrees_dir)
    wt_base.mkdir(parents=True, exist_ok=True)
    worktree_path = wt_base / f"wt-{branch}"
    if worktree_path.exists():
        # remove and recreate to avoid stale state (user choice; can change)
        shutil.rmtree(worktree_path)
    # ensure branch exists locally
    try:
        _run(["git", "rev-parse", "--verify", branch], cwd=repo_path, check=False)
    except Exception:
        # create orphan branch from current HEAD if necessary
        _run(["git", "branch", branch], cwd=repo_path, check=False)
    _run(["git", "worktree", "add", str(worktree_path), branch], cwd=repo_path)
    return {"ok": True, "worktree_path": str(worktree_path)}

@function_tool
def apply_patch(patch_text: str, worktree_path: str) -> Dict:
    """
    Apply unified diff patch inside worktree. Returns ok or error message.
    """
    p = subprocess.Popen(["git", "apply", "--index", "--whitespace=nowarn", "-"], cwd=worktree_path,
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate(patch_text)
    if p.returncode != 0:
        return {"ok": False, "error": err}
    return {"ok": True, "stdout": out}

@function_tool
def commit_and_push(message: str, worktree_path: str, remote: str = "origin") -> Dict:
    _run(["git", "add", "-A"], cwd=worktree_path)
    # avoid failing if no changes
    try:
        _run(["git", "commit", "-m", message], cwd=worktree_path)
    except RuntimeError as e:
        return {"ok": False, "reason": "no_changes_or_commit_failed", "error": str(e)}
    branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=worktree_path)
    _run(["git", "push", "--set-upstream", remote, branch], cwd=worktree_path)
    sha = _run(["git", "rev-parse", "HEAD"], cwd=worktree_path)
    return {"ok": True, "branch": branch, "sha": sha}

@function_tool
def status(repo_path: str = ".") -> Dict:
    out = _run(["git", "status", "--porcelain"], cwd=repo_path, check=False)
    return {"ok": True, "status_porcelain": out}
