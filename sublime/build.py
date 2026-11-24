#!/usr/bin/env python3

import argparse
import json
import plistlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "grammar" / "alloy.tmLanguage.json"
DESTINATION = ROOT / "sublime" / "Alloy.tmLanguage"


def generated_bytes():
    if not SOURCE.is_file():
        raise SystemExit(f"Grammar not found: {SOURCE}")

    with SOURCE.open("r", encoding="utf-8") as source_file:
        grammar = json.load(source_file)

    return plistlib.dumps(grammar, fmt=plistlib.FMT_XML, sort_keys=False)


def main():
    parser = argparse.ArgumentParser(description="Build the Sublime Text grammar.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if the generated grammar is missing or out of date",
    )
    args = parser.parse_args()

    output = generated_bytes()
    if args.check:
        if not DESTINATION.is_file() or DESTINATION.read_bytes() != output:
            print(f"{DESTINATION.relative_to(ROOT)} is out of date; run python sublime/build.py", file=sys.stderr)
            return 1
        print(f"{DESTINATION.relative_to(ROOT)} is up to date")
        return 0

    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    DESTINATION.write_bytes(output)
    print(f"Generated {DESTINATION.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
