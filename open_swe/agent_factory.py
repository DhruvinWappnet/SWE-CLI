import os

from .tools.io_tools import list_files
from .settings import DEFAULT_MODEL, REPO_ROOT
from .tools import read_file, write_file, unified_diff, search_codebase, create_worktree, apply_patch, commit_and_push, dry_run_patch, validate_paths, run_tests, run_linters, create_branch, status, create_pr

try:
    from agents import Agent, ModelSettings
except Exception:
    Agent = None
    ModelSettings = None

def get_agent(instruction, model_name: str = None):
    model_name = model_name or DEFAULT_MODEL
    print("Model Name: ", model_name)
    tools = [
        read_file, write_file, unified_diff, search_codebase,list_files, create_pr,
        create_worktree, apply_patch, commit_and_push, create_branch, status,
        dry_run_patch, validate_paths, run_tests, run_linters
    ]

    if Agent is None or ModelSettings is None:
        raise RuntimeError("agents.Agent or ModelSettings not available. Ensure open-swe (agents) package is installed and importable.")

    model_settings = ModelSettings(model=model_name, reasoning={"effort": "medium"}, summary="detailed")
    agent = Agent(name="open_swe_agent", instructions=instruction, tools=tools, model_settings=model_settings)
    print("Agent methods:", dir(agent))
    return agent