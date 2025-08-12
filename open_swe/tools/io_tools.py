from typing import Optional, Dict
from pathlib import Path
import difflib
from agents import function_tool
MAX_READ_KB = 200

@function_tool(strict_mode=False)
def read_file(path: str) -> Optional[Dict]:
    """
    Read a file's content safely.

    If file size > MAX_READ_KB, return only the first 500 lines.

    Args:
        path (str): File path to read.

    Returns:
        Dict: {
            "ok": bool,
            "content": str (full content if not truncated),
            "truncated": bool,
            "head": str (if truncated),
            "size_kb": float,
            "reason": str (if error),
            "path": str (requested path)
        }
    """
    p = Path(path)
    if not p.exists():
        return {"ok": False, "reason": "not_found", "path": path}
    size_kb = p.stat().st_size / 1024
    if size_kb > MAX_READ_KB:
        with p.open("r", encoding="utf8", errors="ignore") as f:
            head = "".join([next(f) for _ in range(500)])
        return {"ok": True, "truncated": True, "head": head, "size_kb": size_kb}
    with p.open("r", encoding="utf8", errors="ignore") as f:
        content = f.read()
    return {"ok": True, "truncated": False, "content": content, "size_kb": size_kb}

@function_tool(strict_mode=False)
def write_file(path: str, content: str) -> Dict:
    """
    Write content to a file, creating directories if needed.

    Args:
        path (str): File path to write.
        content (str): Content to write to the file.

    Returns:
        Dict: { "ok": bool } or error info.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        with p.open("w", encoding="utf8") as f:
            f.write(content)
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@function_tool(strict_mode=False)
def list_files(dir_path: str, extension: Optional[str] = None) -> Dict:
    """
    List all files in a directory optionally filtered by extension.

    Args:
        dir_path (str): Directory to list files from.
        extension (str, optional): File extension to filter (e.g. '.py').

    Returns:
        Dict: { "ok": bool, "files": List[str] } or error info.
    """
    p = Path(dir_path)
    if not p.exists() or not p.is_dir():
        return {"ok": False, "reason": "not_found_or_not_dir", "path": dir_path}
    files = [str(f) for f in p.glob(f"*{extension}" if extension else "*") if f.is_file()]
    return {"ok": True, "files": files}

@function_tool(strict_mode=False)
def unified_diff(old_content: str, new_content: str, fromfile: str = "old", tofile: str = "new") -> Dict:
    """
    Generate unified diff between old_content and new_content.

    Args:
        old_content (str): Original text.
        new_content (str): Modified text.
        fromfile (str): Label for original file.
        tofile (str): Label for modified file.

    Returns:
        Dict: { "ok": bool, "diff": str }
    """
    diff = difflib.unified_diff(
        old_content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile=fromfile,
        tofile=tofile,
        lineterm=""
    )
    diff_text = "".join(diff)
    return {"ok": True, "diff": diff_text}
