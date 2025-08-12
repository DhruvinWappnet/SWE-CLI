import subprocess
import shlex
from pathlib import Path
from typing import Dict, List
import json
from agents import function_tool

@function_tool(strict_mode=False)
def dry_run_patch(diff_text: str) -> Dict:
    """
    Return a summary of the unified diff: files touched and line counts.
    """
    files = []
    for line in diff_text.splitlines():
        if line.startswith("+++ ") or line.startswith("--- "):
            files.append(line[4:].strip())
    return {"ok": True, "files_touched": list(set(files)), "summary": f"{len(files)} files touched"}

@function_tool(strict_mode=False)
def validate_paths(paths: List[str], allowed_prefixes: List[str]) -> Dict:
    """
    Validate that every path is under allowed prefixes; returns boolean + invalid paths.
    """
    invalid = []
    for p in paths:
        ok = False
        for pref in allowed_prefixes:
            if p.startswith(pref) or p.startswith("a/" + pref) or p.startswith("b/" + pref):
                ok = True
                break
        if not ok:
            invalid.append(p)
    return {"ok": len(invalid) == 0, "invalid": invalid}

@function_tool(strict_mode=False)
def run_tests(cmd: str, cwd: str, timeout: int = 120) -> Dict:
    """
    Run tests (cmd) inside cwd. Returns code, stdout, stderr.
    """
    import subprocess
    try:
        proc = subprocess.run(shlex.split(cmd), cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return {"ok": proc.returncode == 0, "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}
    except subprocess.TimeoutExpired as e:
        return {"ok": False, "reason": "timeout", "error": str(e)}
    except Exception as e:
        return {"ok": False, "reason": "error", "error": str(e)}

@function_tool(strict_mode=False)
def run_linters(cmd: str, cwd: str, timeout: int = 60) -> Dict:
    return run_tests(cmd, cwd, timeout)
# Safety checks
