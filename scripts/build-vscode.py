#!/usr/bin/env python3

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SOURCE = ROOT / "grammar" / "alloy.tmLanguage.json"
DESTINATION = (
    ROOT / "editors" / "vscode" / "syntaxes" / "alloy.tmLanguage.json"
)


def main():
    if not SOURCE.is_file():
        raise SystemExit(f"Grammar not found: {SOURCE}")

    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE, DESTINATION)

    print(f"Copied grammar to {DESTINATION.relative_to(ROOT)}")


if __name__ == "__main__":
    main()