#!/usr/bin/env python3

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = ROOT / "VERSION"
PACKAGE = ROOT / "vscode" / "package.json"
SOURCE = ROOT / "grammar" / "alloy.tmLanguage.json"
DESTINATION = ROOT / "vscode" / "syntaxes" / "alloy.tmLanguage.json"
LICENSE_SOURCE = ROOT / "LICENSE"
LICENSE_DESTINATION = ROOT / "vscode" / "LICENSE"


def main():
    parser = argparse.ArgumentParser(description="Build the VS Code TextMate grammar.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if the generated grammar is missing or out of date",
    )
    args = parser.parse_args()

    if not SOURCE.is_file():
        raise SystemExit(f"Grammar not found: {SOURCE}")

    version = VERSION.read_text(encoding="utf-8").strip()
    package = json.loads(PACKAGE.read_text(encoding="utf-8"))

    if args.check:
        if not DESTINATION.is_file() or DESTINATION.read_bytes() != SOURCE.read_bytes():
            print(f"{DESTINATION.relative_to(ROOT)} is out of date; run python vscode/build.py", file=sys.stderr)
            return 1
        if not LICENSE_DESTINATION.is_file() or LICENSE_DESTINATION.read_bytes() != LICENSE_SOURCE.read_bytes():
            print(f"{LICENSE_DESTINATION.relative_to(ROOT)} is out of date; run python vscode/build.py", file=sys.stderr)
            return 1
        if package.get("version") != version:
            print(f"{PACKAGE.relative_to(ROOT)} version does not match VERSION; run python vscode/build.py", file=sys.stderr)
            return 1
        print(f"{DESTINATION.relative_to(ROOT)} is up to date")
        return 0

    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE, DESTINATION)
    shutil.copy2(LICENSE_SOURCE, LICENSE_DESTINATION)
    if package.get("version") != version:
        package["version"] = version
        PACKAGE.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
    print(f"Copied grammar to {DESTINATION.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
