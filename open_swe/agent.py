from agents import Agent, ModelSettings
import os
from tools.git_tools import create_branch,create_worktree,commit_and_push,status,create_pr
from tools.io_tools import read_file,write_file,list_files,unified_diff
def generate_plan(instruction):
    agent_to_test = Agent(
        name="Restaurant Assistant",
        instructions=instruction,
        model=os.getenv("SWE_MODEL"),
        tools=[
            create_branch,
            create_worktree,
            commit_and_push,
            status,
            create_pr,
            read_file,
            write_file,
            list_files,
            unified_diff
        ],
    )
    return agent_to_test