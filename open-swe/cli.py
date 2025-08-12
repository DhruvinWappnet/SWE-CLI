import click
import os
from .agent_factory import get_agent
from .settings import REPO_ROOT, WORKTREES_DIR, DEFAULT_DRY_RUN, DEFAULT_TEST_CMD, DEFAULT_LINT_CMD
from .tools import create_worktree, commit_and_push

@click.group()
def cli():
    pass

@cli.command()
@click.argument("issue_text", nargs=-1)
@click.option("--branch", "-b", default=None, help="Branch name to use. If omitted, branch derived from issue text.")
@click.option("--dry-run/--apply", default=DEFAULT_DRY_RUN, help="Dry-run (generate patches) or actually apply & commit.")
@click.option("--tests/--no-tests", default=True, help="Run tests after applying patch")
def solve_issue(issue_text, branch, dry_run, tests):
    """
    Solve an issue. Usage:
    swe solve-issue "Fix bug in login flow"
    """
    issue_text = " ".join(issue_text).strip()
    if not issue_text:
        click.echo("Provide an issue description.")
        return
    agent = get_agent()

    branch_name = branch or f"issue-{issue_text[:50].strip().replace(' ', '-')}"
    click.echo(f"[+] Creating worktree for branch: {branch_name}")
    wt = create_worktree(branch_name, repo_path=REPO_ROOT, worktrees_dir=WORKTREES_DIR)
    worktree_path = wt.get("worktree_path") if isinstance(wt, dict) else wt
    click.echo(f"[+] Worktree: {worktree_path}")

    # Build initial instruction (agent will plan -> produce patches -> call tools)
    instruction = f"""
You are an SWE agent working on a code repository at PATH={worktree_path}.
Goal: implement the feature/fix described below.
1) Start by replying with a short 3-step plan (analysis, steps).
2) Produce unified diffs for files to change (do NOT apply them yet if dry-run).
3) Call the provided tools to read/write files and to apply patches if instructed.
Issue: {issue_text}
When you are done, return: branch name, patches, test results (if run), and a short summary of changed files.
"""

    click.echo("[+] Invoking agent...")
    # context passed to agent (tools already registered)
    context = {"worktree": worktree_path, "dry_run": dry_run}
    try:
        res = agent.run(instruction, context=context, stream=True)
    except Exception as e:
        click.echo(f"[!] Agent invocation failed: {e}")
        return

    click.echo("[+] Agent finished. Output:")
    click.echo(res)

    # if agent successfully applied and not dry-run, commit & push
    if not dry_run:
        click.echo("[+] Attempting commit & push...")
        commit_msg = f"SWE agent: {issue_text[:120]}"
        try:
            cp = commit_and_push(commit_msg, worktree_path)
            click.echo(f"[+] Commit result: {cp}")
        except Exception as e:
            click.echo(f"[!] Commit/push failed: {e}")
    else:
        click.echo("[i] Dry-run mode: no commit made. Review patches in logs.")
