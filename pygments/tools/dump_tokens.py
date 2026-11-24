"""Print Pygments token types, source positions, and token values."""

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "pygments"))

from alloy_pygments.lexer import AlloyLexer


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("file", type=Path, help="Alloy source file to tokenize")
args = parser.parse_args()

source = args.file.read_text(encoding="utf-8")
lexer = AlloyLexer()

line = 1
column = 1

for token_type, value in lexer.get_tokens(source):
    print(f"{line:4}:{column:<4} {str(token_type):35} {value!r}")

    parts = value.split("\n")
    if len(parts) > 1:
        line += len(parts) - 1
        column = len(parts[-1]) + 1
    else:
        column += len(value)
