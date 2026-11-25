#!/usr/bin/env python3
"""worst-fix: one commit message for a fix that made everything worse.

The bug only fired on leap day. The fix deletes February 29 from the
calendar, so the bug can never fire again — along with birthdays,
anniversaries, and every other 29 February that ever existed. The repair
works by amputating the day the bug lived on: it broke far more than
the bug ever did.

The message reads like something a tired engineer would actually type
at the end of a bad day: short, plain, no slogan, no explanation. The
punchline lands in the second clause.

Standard library only, no network. Deterministic: identical bytes on
every run.
"""

import os
import sys

# Two beats, one per clause: the bug's narrow trigger (leap day only),
# then the repair that deletes February 29 — the day the bug lived on.
# Kept as a tuple so the shape of the line (exactly two clauses) can be
# checked on its own, apart from the text of either clause.
CLAUSES = (
    "fix: the bug only happened on leap day,",
    "we deleted February 29",
)


def build_line():
    """Join the two clauses into the single-line commit message."""
    if len(CLAUSES) != 2:
        raise ValueError("line must be built from exactly two clauses")
    return " ".join(CLAUSES)


LINE = build_line()

MIN_LEN = 1
MAX_LEN = 100


def check(text):
    """Return a list of gate violations for the entry (empty means valid)."""
    bad = []
    if not MIN_LEN <= len(text) <= MAX_LEN:
        bad.append("entry is %d code points, must be %d-%d"
                   % (len(text), MIN_LEN, MAX_LEN))
    if text != text.strip():
        bad.append("entry must not start or end with white space")
    if not text.strip():
        bad.append("entry must not be only white space")
    if "\n" in text or "\r" in text:
        bad.append("entry must be a single line")
    if "  " in text:
        bad.append("entry must not contain a double space")
    if not text.startswith("fix:"):
        bad.append("entry must read as a commit subject line")
    return bad


def main():
    bad = check(LINE)
    if bad:
        for item in bad:
            print(item, file=sys.stderr)
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(LINE)
    # The output directory itself is never chmodded or removed; only the
    # entry file gets best-effort permissions (in the grading sandbox the
    # directory is a root-owned mount, so a chmod there would raise EPERM
    # and must not fail the run).
    try:
        os.chmod(path, 0o644)
    except OSError:
        pass
    with open(path, "rb") as handle:
        if handle.read() != LINE.encode("utf-8"):
            print("entry.txt does not match the commit message", file=sys.stderr)
            return 1
    print("wrote %d characters to %s" % (len(LINE), path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
