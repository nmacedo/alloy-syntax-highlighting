#!/usr/bin/env python3

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDERS = (
    ROOT / "vscode" / "build.py",
    ROOT / "sublime" / "build.py",
    ROOT / "pygments" / "build.py",
    ROOT / "codemirror" / "build.py",
)

parser = argparse.ArgumentParser(
    description="Build or check every generated Alloy syntax highlighter."
)
parser.add_argument(
    "--check",
    action="store_true",
    help="check that all generated artifacts are current without rewriting them",
)
args = parser.parse_args()

for builder in BUILDERS:
    action = "Checking" if args.check else "Building"
    print(f"\n{action} {builder.relative_to(ROOT)}...", flush=True)
    command = [sys.executable, str(builder)]
    if args.check:
        command.append("--check")
    subprocess.run(
        command,
        check=True
    )

result = "are up to date" if args.check else "built successfully"
print(f"\nAll configured syntax highlighters {result}.")
