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

Why this entry: it reads as a complete three-act arc in one line — a
couple ("divorce"), a contested asset ("WiFi"), and an underdog winner
("the dog") — with no filler word to trim and no abbreviation to decode.
It fits the 32-character gate with 5 characters to spare, so the whole
story survives intact on any network list.
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


class WriteEntryError(Exception):
    """Raised by write_entry() when the write or its verification fails.

    Carries the exact stderr prefix the CLI prints ("INVALID" or
    "INVALID after read-back") so main() can report it unchanged.
    """

    def __init__(self, prefix, messages):
        super().__init__(messages[0] if messages else prefix)
        self.prefix = prefix
        self.messages = messages


def write_entry(text, output_path):
    """Write ``text`` as UTF-8 bytes to ``output_path`` and verify it.

    Returns ``(on_disk_bytes, read_back_text)``. The read-back check
    guarantees what is on disk is byte-identical to what was intended
    and still passes the competition gate; any failure raises
    WriteEntryError instead of returning partial output.
    """
    data = text.encode("utf-8")
    with open(output_path, "wb") as fh:
        fh.write(data)

    # Read-back verification: what is on disk must be byte-identical to
    # what we intended to write, and must still pass the gate.
    with open(output_path, "rb") as fh:
        on_disk = fh.read()
    if on_disk != data:
        raise WriteEntryError("INVALID", ["read-back mismatch"])
    read_back = on_disk.decode("utf-8")
    read_back_problems = validate_entry(read_back)
    if read_back_problems:
        raise WriteEntryError("INVALID after read-back", read_back_problems)
    return on_disk, read_back


def main():
    problems = validate_entry(ENTRY_TEXT)
    if problems:
        for problem in problems:
            print("INVALID: %s" % problem, file=sys.stderr)
        return 1

    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "entry.txt")

    try:
        on_disk, read_back = write_entry(ENTRY_TEXT, output_path)
    except WriteEntryError as exc:
        for message in exc.messages:
            print("%s: %s" % (exc.prefix, message), file=sys.stderr)
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
