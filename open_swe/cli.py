# import click
# import subprocess
# import asyncio
# import inspect
# from .agent_factory import get_agent
# from .settings import REPO_ROOT, DEFAULT_DRY_RUN, DEFAULT_TEST_CMD, DEFAULT_LINT_CMD, DEFAULT_BASE_BRANCH
# from .tools import create_worktree, commit_and_push, create_pr

# try:
#     from agents import Runner
# except ImportError:
#     Runner = None

# @click.group()
# def cli():
#     pass

# @cli.command()
# @click.argument("issue_text", nargs=-1)
# @click.option("--model", default=None, help="LLM model to use (e.g., groq/llama-3.1-8b-instant). Defaults to settings.DEFAULT_MODEL.")
# @click.option("--branch", "-b", default=None, help="Branch name to use. If omitted, generates one based on issue.")
# @click.option("--dry-run/--apply", default=DEFAULT_DRY_RUN, help="Dry-run or apply & commit.")
# @click.option("--base", default=DEFAULT_BASE_BRANCH, help="Base branch for PR (e.g., test_dev).")
# @click.option("--tests/--no-tests", default=True, help="Run tests after applying patch")
# @click.option("--pr/--no-pr", default=True, help="Create PR after pushing.")
# def solve_issue(issue_text, model, branch, dry_run, tests, base, pr):
#     issue_text = " ".join(issue_text).strip()
#     if not issue_text:
#         click.echo("Provide an issue description.")
#         return

#     repo_path = REPO_ROOT

#     try:
#         subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=repo_path, check=True, capture_output=True, text=True)
#         click.echo(f"[+] Valid Git repository at: {repo_path}")
#     except subprocess.CalledProcessError:
#         click.echo(f"[!] Error: {repo_path} is not a Git repository. Initialize or set SWE_REPO_ROOT.")
#         return

#     branch_name = branch or f"feature-{issue_text.lower().replace(' ', '-')[:20]}"
#     click.echo(f"[+] Using repo path: {repo_path}")
#     click.echo(f"[+] Using branch: {branch_name}")

#     test_cmd = DEFAULT_TEST_CMD if tests else None
#     lint_cmd = DEFAULT_LINT_CMD

#     instruction = f"""
# You are an SWE agent working on a code repository at PATH={repo_path}.
# Goal: Resolve the issue described below, create a new branch, commit, push, and create a PR.
# Issue: {issue_text}
# Dry-run mode: {dry_run}
# PR creation: {pr}
# """

#     click.echo("[+] Invoking agent...")

#     try:
#         agent = get_agent(instruction, model_name=model)
#         import inspect
#         if inspect.iscoroutinefunction(agent):
#             res = asyncio.run(agent())
#         else:
#             res = agent()
#     except Exception as e:
#         click.echo(f"[!] Agent invocation failed: {e}")
#         return

#     click.echo("[+] Agent finished. Output:")
#     click.echo(res)

#     # You can add your commit/push/PR logic here if dry_run == False

#     click.echo("[i] Done.")

import os
import click
from git import Repo
from dotenv import load_dotenv
from groq import Groq  # Groq Python client
from github import Github
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = os.getenv("REPO_OWNER")
REPO_NAME = os.getenv("REPO_NAME")
LOCAL_REPO_PATH = "./repo_clone"
BRANCH_PREFIX = "update-cli-"

gh = Github(GITHUB_TOKEN)
llm = Groq()

def clone_or_pull_repo():
    if not os.path.exists(LOCAL_REPO_PATH):
        print("Cloning repo...")
        Repo.clone_from(f"https://github.com/{REPO_OWNER}/{REPO_NAME}.git", LOCAL_REPO_PATH)
    else:
        print("Pulling latest...")
        repo = Repo(LOCAL_REPO_PATH)
        repo.remotes.origin.pull()

def create_branch(repo, branch_name):
    if branch_name in repo.heads:
        repo.git.checkout(branch_name)
    else:
        new_branch = repo.create_head(branch_name)
        new_branch.checkout()

def commit_and_push(repo, branch_name, message):
    repo.git.add(all=True)
    repo.index.commit(message)
    repo.remotes.origin.push(branch_name)

def generate_edit_plan(instruction):
    prompt = f"""
You are a helpful programming assistant.

The user says: "{instruction}"

Please ONLY output a single JSON object with this format, no explanation or extra text:

{{
  "files": {{
    "path/to/file1": "new content or diff here",
    "path/to/file2": "new content or diff here"
  }},
  "commit_message": "Commit message summarizing changes"
}}
"""
    response = llm.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=1000,
    )
    content = response.choices[0].message.content
    return content

@click.command()
@click.argument("instruction", nargs=-1)
def cli(instruction):
    instruction = " ".join(instruction)
    print(f"Received instruction: {instruction}")

    clone_or_pull_repo()
    repo = Repo(LOCAL_REPO_PATH)

    branch_name = BRANCH_PREFIX + instruction.lower().replace(" ", "-")[:50]
    create_branch(repo, branch_name)

    print("Generating edit plan via Groq LLM...")
    edit_plan_json = generate_edit_plan(instruction)
    print("LLM response:", edit_plan_json)

    import json

    try:
        plan = json.loads(edit_plan_json)
    except Exception as e:
        print("Failed to parse JSON from LLM response:", e)
        return

    files = plan.get("files", {})
    commit_message = plan.get("commit_message", "Update via CLI")

    for filepath, content in files.items():
        abs_path = os.path.join(LOCAL_REPO_PATH, filepath)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w") as f:
            f.write(content)
        print(f"Updated file: {filepath}")

    commit_and_push(repo, branch_name, commit_message)

    gh_repo = gh.get_repo(f"{REPO_OWNER}/{REPO_NAME}")
    pr = gh_repo.create_pull(
        title=commit_message,
        body=f"Automated PR generated by CLI for instruction: {instruction}",
        head=branch_name,
        base="main",
    )
    print(f"PR created: {pr.html_url}")

if __name__ == "__main__":
    cli()
