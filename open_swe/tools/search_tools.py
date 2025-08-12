# Search utilities
import shutil, subprocess, re
from pathlib import Path
from typing import List, Dict
from agents import function_tool

def _ripgrep_available() -> bool:
    return shutil.which("rg") is not None

@function_tool(strict_mode=False)
def search_codebase(root: str, pattern: str, max_results: int = 200) -> Dict:
    """
    Search codebase for pattern. Returns list of matches.
    """
    results = []
    if _ripgrep_available():
        try:
            cmd = ["rg", "--no-heading", "--line-number", "--hidden", "--glob", "!.git", pattern, root]
            proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
            if proc.returncode in (0, 1):  # 1 means some matches but non-0 for rg semantics
                out = (proc.stdout or "").strip()
                if out:
                    lines = out.splitlines()[:max_results]
                    for line in lines:
                        # file:lineno:text
                        parts = line.split(":", 2)
                        if len(parts) == 3:
                            file_path, lineno, text = parts
                            results.append({"path": file_path, "line": int(lineno), "text": text.strip()})
            return {"ok": True, "matches": results}
        except Exception as e:
            return {"ok": False, "reason": "rg_failed", "error": str(e)}
    # fallback python search
    regex = re.compile(pattern)
    for p in Path(root).rglob("*.*"):
        if p.match("*.pyc") or ".git" in str(p):
            continue
        try:
            txt = p.read_text(errors="ignore")
        except Exception:
            continue
        for i, line in enumerate(txt.splitlines(), start=1):
            if regex.search(line):
                results.append({"path": str(p), "line": i, "text": line.strip()})
                if len(results) >= max_results:
                    return {"ok": True, "matches": results}
    return {"ok": True, "matches": results}
