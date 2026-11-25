#!/usr/bin/env python3
"""Tell a Whole Story in 32 Characters — make.fun entry.

Writes a single Wi-Fi network name (at most 32 characters) to
/output/entry.txt. Pure Python 3 standard library, no network, fully
deterministic: the same input always produces the same bytes.

The name: "The Dog Got WiFi In Divorce" (27 characters).
A divorce where the dog walks away with the Wi-Fi — a joke that lands on
the first read and implies a whole story (a marriage, a split, a custody
fight, and the dog coming out ahead) in the few words a phone shows in
its network list.
"""

import hashlib
import os
import sys

ENTRY_TEXT = "The Dog Got WiFi In Divorce"

MIN_LENGTH = 1
MAX_LENGTH = 32


def validate_entry(text):
    """Check the competition gate: UTF-8 text, 1-32 characters, not only
    whitespace. Returns a list of problems (empty means valid)."""
    problems = []
    if not isinstance(text, str):
        problems.append("entry is not a string")
        return problems
    if len(text) < MIN_LENGTH:
        problems.append("entry is empty (must be at least 1 character)")
    if len(text) > MAX_LENGTH:
        problems.append(
            "entry is %d characters (must be at most %d)"
            % (len(text), MAX_LENGTH)
        )
    if text.strip() == "":
        problems.append("entry is only whitespace")
    try:
        text.encode("utf-8")
    except UnicodeEncodeError as exc:
        problems.append("entry is not valid UTF-8: %s" % exc)
    return problems


def main():
    problems = validate_entry(ENTRY_TEXT)
    if problems:
        for problem in problems:
            print("INVALID: %s" % problem, file=sys.stderr)
        return 1

    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "entry.txt")

    data = ENTRY_TEXT.encode("utf-8")
    with open(output_path, "wb") as fh:
        fh.write(data)

    # Read-back verification: what is on disk must be byte-identical to
    # what we intended to write, and must still pass the gate.
    with open(output_path, "rb") as fh:
        on_disk = fh.read()
    if on_disk != data:
        print("INVALID: read-back mismatch", file=sys.stderr)
        return 1
    read_back = on_disk.decode("utf-8")
    read_back_problems = validate_entry(read_back)
    if read_back_problems:
        for problem in read_back_problems:
            print("INVALID after read-back: %s" % problem, file=sys.stderr)
        return 1

    digest = hashlib.sha256(on_disk).hexdigest()
    print("entry: %r" % read_back)
    print("characters: %d" % len(read_back))
    print("bytes: %d" % len(on_disk))
    print("sha256: %s" % digest)
    print("wrote: %s" % output_path)
    print("valid: gate passed (1-32 characters, not only whitespace)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
