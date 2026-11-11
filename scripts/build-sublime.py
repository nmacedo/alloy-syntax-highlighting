#!/usr/bin/env python3

import json
import plistlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SOURCE = ROOT / "grammar" / "alloy.tmLanguage.json"
DESTINATION = ROOT / "editors" / "sublime" / "Alloy.tmLanguage"


def main():
    if not SOURCE.is_file():
        raise SystemExit(f"Grammar not found: {SOURCE}")

    with SOURCE.open("r", encoding="utf-8") as file:
        grammar = json.load(file)

    DESTINATION.parent.mkdir(parents=True, exist_ok=True)

    with DESTINATION.open("wb") as file:
        plistlib.dump(
            grammar,
            file,
            fmt=plistlib.FMT_XML,
            sort_keys=False
        )

    print(f"Generated {DESTINATION.relative_to(ROOT)}")


if __name__ == "__main__":
    main()