import difflib

def unified_diff(a: str, b: str, fromfile="before", tofile="after") -> str:
    a_lines = a.splitlines(keepends=True)
    b_lines = b.splitlines(keepends=True)
    return "".join(difflib.unified_diff(a_lines, b_lines, fromfile, tofile))
