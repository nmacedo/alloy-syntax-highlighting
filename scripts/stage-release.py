#!/usr/bin/env python3
"""Stage a standalone source tree for one or all Alloy highlighting targets."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def copy_files(destination: Path, *sources: str) -> None:
    for source in sources:
        path = ROOT / source
        target = destination / path.name
        if path.is_dir():
            shutil.copytree(path, target, ignore=shutil.ignore_patterns(
                "__pycache__", "*.pyc", "*.egg-info", "node_modules", ".DS_Store"
            ))
        else:
            shutil.copy2(path, target)


def stage(target: str, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)
    if target == "sublime":
        copy_files(destination, "sublime/Alloy.tmLanguage", "sublime/README.md", "LICENSE")
    elif target == "vscode":
        copy_files(destination, "vscode/package.json", "vscode/README.md",
                   "vscode/LICENSE", "vscode/.vscodeignore", "vscode/syntaxes")
    elif target == "pygments":
        copy_files(destination, "pygments/alloy_pygments", "pygments/README.md", "LICENSE")
        (destination / "pyproject.toml").write_text(
            "[build-system]\nrequires = [\"setuptools>=77\"]\n"
            "build-backend = \"setuptools.build_meta\"\n\n"
            "[project]\nname = \"alloy-pygments\"\nversion = \"0.1.0\"\n"
            "description = \"Pygments lexer for Alloy 6\"\nreadme = \"README.md\"\n"
            "license = \"MIT\"\nlicense-files = [\"LICENSE\"]\n"
            "requires-python = \">=3.9\"\ndependencies = [\"Pygments>=2.17\"]\n"
            "keywords = [\"alloy\", \"syntax-highlighting\", \"pygments\"]\n\n"
            "[project.entry-points.\"pygments.lexers\"]\n"
            "alloy6 = \"alloy_pygments.lexer:AlloyLexer\"\n\n"
            "[tool.setuptools.packages.find]\nwhere = [\".\"]\n"
            "include = [\"alloy_pygments*\"]\nnamespaces = false\n",
            encoding="utf-8",
        )
    elif target == "codemirror":
        copy_files(destination, "codemirror/package.json", "codemirror/README.md",
                   "codemirror/LICENSE", "codemirror/src")
    else:
        raise ValueError(f"Unknown target: {target}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=("all", "sublime", "vscode", "pygments", "codemirror"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    targets = ("sublime", "vscode", "pygments", "codemirror") if args.target == "all" else (args.target,)
    for target in targets:
        stage(target, args.output / target)
        print(f"Staged {target}: {args.output / target}")


if __name__ == "__main__":
    main()
