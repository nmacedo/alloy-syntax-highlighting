from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

from pygments.token import Token

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "pygments"))
from alloy_pygments.lexer import AlloyLexer  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures"
EXPECTED = ROOT / "tests" / "expected" / "scopes.json"


def scope_token(scope: str):
    """Normalize a TextMate scope to the Pygments category tested here."""
    for part in reversed(scope.split()):
        if part.startswith("comment.line."):
            return Token.Comment.Single
        if part.startswith(("comment.block.", "comment.")):
            return Token.Comment.Multiline
        if part.startswith("constant.numeric.integer.hexadecimal."):
            return Token.Literal.Number.Hex
        if part.startswith("constant.numeric.integer.binary."):
            return Token.Literal.Number.Bin
        if part.startswith("constant.numeric."):
            return Token.Literal.Number.Integer
        if part.startswith("constant.character.escape."):
            return Token.Literal.String.Escape
        if part.startswith("string."):
            return Token.Literal.String.Double
        if part.startswith(("keyword.declaration.namespace.", "storage.type.namespace.")):
            return Token.Keyword.Namespace
        if part.startswith(("keyword.declaration.", "storage.type.")):
            return Token.Keyword.Declaration
        if part.startswith("keyword.control.import."):
            return Token.Keyword.Namespace
        if part.startswith(("keyword.control.", "keyword.other.")):
            return Token.Keyword
        if part.startswith("keyword.operator.word."):
            return Token.Operator.Word
        if part.startswith("keyword.operator."):
            return Token.Operator
        if part.startswith("storage.modifier."):
            return Token.Keyword.Reserved
        if part.startswith("support.function.") or part.startswith("variable.language."):
            return Token.Name.Builtin
        if part.startswith("support.type."):
            return Token.Keyword.Type
        if part.startswith("support.constant."):
            return Token.Name.Constant
        if part.startswith("variable.other.meta."):
            return Token.Name.Variable.Magic
        if part.startswith("variable.other."):
            return Token.Name.Variable
        if part.startswith("punctuation."):
            return Token.Punctuation
    return None


def find_occurrence(line: str, needle: str, occurrence: int) -> int:
    import re
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", needle):
        pattern = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(needle)}(?![A-Za-z0-9_])")
        matches = list(pattern.finditer(line))
        if occurrence >= len(matches):
            raise AssertionError(f"{needle!r} occurrence {occurrence} not found in {line!r}")
        return matches[occurrence].start()
    pos = -1
    for _ in range(occurrence + 1):
        pos = line.find(needle, pos + 1)
        if pos < 0:
            raise AssertionError(f"{needle!r} occurrence {occurrence} not found in {line!r}")
    if len(needle) >= 2 and needle.startswith('"') and needle.endswith('"'):
        return pos + 1
    if needle.startswith("/*") and needle.endswith("*/"):
        return pos + 2
    return pos


class PygmentsFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
        cls.lexer = AlloyLexer()

    def test_fixtures_against_normalized_scope_expectations(self):
        failures = []
        checked = 0
        negative_checked = 0
        intentionally_unrepresentable = 0
        for filename, assertions in self.expected.items():
            source = (FIXTURES / filename).read_text(encoding="utf-8")
            lines = source.splitlines(keepends=True)
            tokens = list(self.lexer.get_tokens_unprocessed(source))
            errors = [(start, value) for start, token, value in tokens if token in Token.Error]
            if errors:
                failures.append(f"{filename}: lexer emitted Error tokens: {errors[:5]}")
            for assertion in assertions:
                line_number = assertion["line"]
                line = lines[line_number - 1].rstrip("\r\n")
                occurrence = assertion.get("occurrence", 0)
                local = find_occurrence(line, assertion["token"], occurrence)
                absolute = sum(len(part) for part in lines[:line_number - 1]) + local
                probe_length = len(assertion["token"])
                if assertion["token"].startswith('"') and assertion["token"].endswith('"'):
                    probe_length -= 2
                elif assertion["token"].startswith("/*") and assertion["token"].endswith("*/"):
                    probe_length -= 4
                end = absolute + probe_length
                overlapping = [
                    (start, start + len(value), token, value)
                    for start, token, value in tokens
                    if value and start < end and start + len(value) > absolute
                ]
                if not overlapping:
                    failures.append(f"{filename}:{line_number}: no Pygments token for {assertion['token']!r}")
                    continue

                expected_scope = assertion.get("scope")
                if expected_scope:
                    wanted = scope_token(expected_scope)
                    if wanted is None:
                        intentionally_unrepresentable += 1
                    else:
                        checked += 1
                        allowed = (wanted,)
                        if expected_scope == "string.quoted.double.alloy":
                            # TextMate's string scope encloses escape scopes;
                            # Pygments exposes the escape as a separate token.
                            allowed += (Token.Literal.String.Escape,)
                        if any(not any(token in category for category in allowed)
                               for _, _, token, _ in overlapping):
                            got = [(str(token), value) for _, _, token, value in overlapping]
                            failures.append(
                                f"{filename}:{line_number}: {assertion['token']!r}: "
                                f"expected {wanted}, got {got} (source scope {expected_scope})"
                            )

                for forbidden_scope in assertion.get("notScopes", []):
                    forbidden = scope_token(forbidden_scope)
                    # Pygments intentionally collapses delimiter sub-scopes
                    # such as group-open vs block-open into Punctuation.
                    if forbidden is not None and forbidden not in (Token.Punctuation,):
                        negative_checked += 1
                        if any(token in forbidden for _, _, token, _ in overlapping):
                            failures.append(
                                f"{filename}:{line_number}: {assertion['token']!r}: unexpectedly mapped to "
                                f"{forbidden} (forbidden source scope {forbidden_scope})"
                            )

        self.assertFalse("\n".join(failures), "Pygments fixture mismatches:\n" + "\n".join(failures))
        print(
            f"\nPygments checked {checked} representable positive assertions and "
            f"{negative_checked} representable negative assertions; "
            f"skipped {intentionally_unrepresentable} positive meta-scope assertions "
            "and unrepresentable negative scopes."
        )


if __name__ == "__main__":
    unittest.main()
