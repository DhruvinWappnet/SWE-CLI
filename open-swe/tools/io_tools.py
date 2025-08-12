# File I/O utilities
from pathlib import Path
import difflib
import json
from typing import Optional, Dict

# decorator (will be replaced by real function_tool from agents if present)
try:
    from agents import function_tool
except Exception:
    def function_tool(func=None, **_):
        if func is None:
            def dec(f): return f
            return dec
        return func

MAX_READ_KB = 200

@function_tool
def read_file(path: str) -> Optional[Dict]:
    """
    Read file safely. Returns None if not found, or dict with content/truncated flag.
    """
    p = Path(path)
    if not p.exists():
        return {"ok": False, "reason": "not_found", "path": path}
    size_kb = p.stat().st_size / 1024
    if size_kb > MAX_READ_KB:
        # return head only
        with p.open("r", encoding="utf8", errors="ignore") as f:
            head = "".join([next(f) for _ in range(500)])
        return {"ok": True, "truncated": True, "head": head, "size_kb": size_kb}
    with p.open("r", encoding="utf8", errors="ignore") as f:
        content = f.read()
    return {"ok": True, "truncated": False, "content": content, "size_kb": size_kb}

@function_tool
def unified_diff(filename: str, old: str, new: str) -> Dict:
    """
    Return unified diff string between old and new. Tool returns dict.
    """
    old_lines = old.splitlines(keepends=True)
    new_lines = new.splitlines(keepends=True)
    diff = difflib.unified_diff(old_lines, new_lines, fromfile=f"a/{filename}", tofile=f"b/{filename}")
    return {"ok": True, "diff": "".join(diff)}

@function_tool
def write_file(path: str, content: str, backup: bool = True) -> Dict:
    """
    Write content to path. If backup True, create .bak file when overwriting.
    """
    p = Path(path)
    if backup and p.exists():
        bak = p.with_suffix(p.suffix + ".bak")
        p.replace(bak)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf8")
    return {"ok": True, "path": str(p)}
