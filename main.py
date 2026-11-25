#!/usr/bin/env python3
"""worst-fix: write one commit message for a fix that made everything worse.

The line is a commit subject for a bug that only ever fired on leap day,
fixed by deleting February 29 from the calendar. The repair "works" only
by amputating a day: the fix broke more than the bug ever did. It reads
like something a tired engineer would actually type at the end of a bad
day — short, plain, no slogan, no explanation, the punchline in the
second clause.

Standard library only, no network. Deterministic: the same bytes on every run.
"""

import os
import sys

# The line is built from two clauses, one per beat, so each beat can be
# checked on its own: the bug's narrow trigger (leap day only), then the
# repair that deletes February 29 — the day the bug lived on.
CLAUSES = (
    "fix: the bug only happened on leap day,",
    "we deleted February 29",
)

LINE = " ".join(CLAUSES)

MIN_LEN = 1
MAX_LEN = 100


def problems(text: str) -> list:
    """Return every gate violation for the entry text (empty means valid)."""
    found = []
    if not (MIN_LEN <= len(text) <= MAX_LEN):
        found.append(f"entry is {len(text)} code points, must be {MIN_LEN}-{MAX_LEN}")
    stripped = text.strip()
    if not stripped:
        found.append("entry must not be only white space")
    if text != stripped:
        found.append("entry must not start or end with white space")
    if "\n" in text or "\r" in text:
        found.append("entry must be a single line")
    if "  " in text:
        found.append("entry must not contain a double space")
    if not stripped.startswith("fix:"):
        found.append("entry must read as a commit subject line")
    return found


def main() -> int:
    if len(CLAUSES) != 2:
        print("line must be built from exactly two clauses", file=sys.stderr)
        return 1
    text = LINE
    bad = problems(text)
    if bad:
        for item in bad:
            print(item, file=sys.stderr)
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    # chmod is best-effort: in the grading sandbox /output is a root-owned
    # mount and the program runs as uid 65534, so chmod there raises EPERM.
    # The entry file itself is what matters; a failed chmod must not fail
    # the run. (The output directory itself is never chmodded or removed.)
    try:
        os.chmod(path, 0o644)
    except OSError:
        pass
    # Read the file back as bytes and confirm they match the line exactly.
    with open(path, "rb") as f:
        if f.read() != text.encode("utf-8"):
            print("entry.txt does not match the commit message", file=sys.stderr)
            return 1
    print(f"wrote {len(text)} characters to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
