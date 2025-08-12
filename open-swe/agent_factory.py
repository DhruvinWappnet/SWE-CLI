# Agent factory logic
import os
from .settings import DEFAULT_MODEL, REPO_ROOT
from .tools import read_file, write_file, unified_diff, search_codebase, create_worktree, apply_patch, commit_and_push, dry_run_patch, validate_paths, run_tests, run_linters, create_branch, status

# import Agent and ModelSettings from open-swe (agents)
try:
    from agents import Agent, ModelSettings
except Exception:
    Agent = None
    ModelSettings = None

class AgentWrapper:
    def __init__(self, agent_obj):
        self.agent = agent_obj

    def run(self, instruction: str, context: dict = None, stream: bool = False):
        """
        Generic wrapper: try .run(), .execute(), .predict() in order.
        """
        if hasattr(self.agent, "run"):
            return self.agent.run(instruction, context=context, stream=stream)
        if hasattr(self.agent, "execute"):
            return self.agent.execute(instruction, context=context, stream=stream)
        if hasattr(self.agent, "predict"):
            return self.agent.predict(instruction, context=context)
        raise RuntimeError("Agent object does not expose run/execute/predict methods. Adapt agent_factory.get_agent()")

def get_agent(model_name: str = None):
    """
    Construct an Agent from open-swe 'agents' package and register our function tools.
    If the real Agent or ModelSettings is not available, raise an informative error.
    """
    model_name = model_name or DEFAULT_MODEL
    tools = [
        # functions registered as tools — these are the function objects (decorated)
        read_file, write_file, unified_diff, search_codebase,
        create_worktree, apply_patch, commit_and_push, create_branch, status,
        dry_run_patch, validate_paths, run_tests, run_linters
    ]

    if Agent is None or ModelSettings is None:
        raise RuntimeError("agents.Agent or ModelSettings not available. Ensure open-swe (agents) package is installed and importable.")

    model_settings = ModelSettings(model=model_name, reasoning={"effort":"medium"}, summary="detailed", stream=True)
    agent = Agent(tools=tools, model_settings=model_settings)
    return AgentWrapper(agent)
