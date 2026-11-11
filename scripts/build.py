#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

for script in ("build-vscode.py", "build-sublime.py"):
    print(f"\nBuilding {script}...")
    subprocess.run(
        [sys.executable, str(SCRIPTS / script)],
        check=True
    )

print("\nAll editor grammars built successfully.")