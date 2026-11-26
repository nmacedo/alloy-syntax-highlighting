#!/usr/bin/env python3
"""Compile this repository's TextMate grammar into a native Pygments RegexLexer."""
from __future__ import annotations

import ast
import json
import re
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAMMAR = ROOT / "grammar" / "alloy.tmLanguage.json"
OUTPUT = ROOT / "pygments" / "alloy_pygments" / "lexer.py"

def scope_token(scope: str) -> str | None:
    """Map a TextMate scope to a Pygments token expression.

    Meta scopes describe context rather than the lexical class of a token and
    therefore intentionally do not produce a Pygments token of their own.
    """
    parts = scope.split()
    for part in reversed(parts):
        if "." not in part:
            continue
        if part.startswith("meta."):
            continue
        if part.startswith("comment.line."):
            return "Comment.Single"
        if part.startswith("comment.block.") or part.startswith("comment."):
            return "Comment.Multiline"
        if part.startswith("constant.numeric.integer.hexadecimal."):
            return "Number.Hex"
        if part.startswith("constant.numeric.integer.binary."):
            return "Number.Bin"
        if part.startswith("constant.numeric."):
            return "Number.Integer"
        if part.startswith("constant.character.escape."):
            return "String.Escape"
        if part.startswith("string."):
            return "String.Double"
        if part.startswith("keyword.declaration.namespace.") or part.startswith("storage.type.namespace."):
            return "Keyword.Namespace"
        if part.startswith("keyword.declaration.") or part.startswith("storage.type."):
            return "Keyword.Declaration"
        if part.startswith("keyword.control.import."):
            return "Keyword.Namespace"
        if part.startswith("keyword.control.") or part.startswith("keyword.other."):
            return "Keyword"
        if part.startswith("keyword.operator.word."):
            return "Operator.Word"
        if part.startswith("keyword.operator."):
            return "Operator"
        if part.startswith("storage.modifier."):
            return "Keyword.Reserved"
        if part.startswith("support.function."):
            return "Name.Builtin"
        if part.startswith("support.type."):
            return "Keyword.Type"
        if part.startswith("support.constant."):
            return "Name.Constant"
        if part.startswith("variable.language."):
            return "Name.Builtin"
        if part.startswith("variable.other.meta."):
            return "Name.Variable.Magic"
        if part.startswith("variable.other."):
            return "Name.Variable"
        if part.startswith("punctuation."):
            return "Punctuation"
        if part.startswith("meta."):
            return None
        raise ValueError(f"No Pygments token mapping for TextMate scope {part!r}")
    return None


class Compiler:
    def __init__(self, grammar: dict):
        self.grammar = grammar
        self.repository = grammar.get("repository", {})
        self.states: dict[str, list[str]] = {}
        self.pushed_states: set[str] = set()
        self.context_index = 0
        self.context_names: dict[str, int] = {}

    @staticmethod
    def q(value: str) -> str:
        return repr(value)

    @staticmethod
    def regex(value: str) -> str:
        """Prefer raw strings so the generated regexes can be read directly."""
        for quote in ("'", '"'):
            literal = f"r{quote}{value}{quote}"
            try:
                if ast.literal_eval(literal) == value:
                    return literal
            except (SyntaxError, ValueError):
                pass
        return repr(value)

    def token_expr(self, scope: str | None, default: str = "Text") -> str:
        if not scope:
            return default
        mapped = scope_token(scope)
        return mapped or default

    def capture_action(self, regex: str, captures: dict | None, base_scope: str | None) -> tuple[str, str]:
        """Use native bygroups, explicitly capturing this grammar's gaps."""
        captures = captures or {}
        try:
            group_count = re.compile(regex).groups
        except re.error as exc:
            raise ValueError(f"Invalid Python-compatible regex {regex!r}: {exc}") from exc

        base_scope_value = captures.get("0", {}).get("name") or base_scope
        base = self.token_expr(base_scope_value)
        overrides = {}
        for key, value in captures.items():
            if key == "0":
                continue
            index = int(key)
            if index > group_count:
                raise ValueError(f"Capture {index} exceeds {group_count} groups in {regex!r}")
            overrides[index] = self.token_expr(value.get("name"))

        if not group_count or not overrides:
            return regex, base
        return self.capture_groups(regex, overrides, base)

    @staticmethod
    def capture_groups(regex: str, overrides: dict[int, str], base: str) -> tuple[str, str]:
        """Lower disjoint captures, assertions, and whitespace to bygroups.

        These are the only mixed-capture forms in the Alloy grammar. Reject
        other consuming gaps or nested captures rather than silently losing
        source text through Pygments' bygroups callback.
        """
        parts, actions = [], []
        index, group = 0, 0
        while index < len(regex):
            if regex[index] == "(":
                end, depth, in_class = index + 1, 1, False
                while end < len(regex) and depth:
                    char = regex[end]
                    if char == "\\":
                        end += 2
                        continue
                    if char == "[":
                        in_class = True
                    elif char == "]":
                        in_class = False
                    elif not in_class:
                        if char == "(":
                            depth += 1
                        elif char == ")":
                            depth -= 1
                    end += 1
                part = regex[index:end]
                groups = re.compile(part).groups
                if not part.startswith("(?") and groups == 1:
                    group += 1
                    actions.append(overrides.get(group, base))
                elif part.startswith(("(?=", "(?!", "(?<=", "(?<!")) and groups == 0:
                    pass
                else:
                    raise ValueError(f"Unsupported mixed-capture group: {part!r}")
                parts.append(part)
                index = end
            elif regex.startswith(r"\s", index):
                gap = re.match(r"\\s[+*?]?\??", regex[index:])[0]
                parts.append(f"({gap})")
                actions.append(base)
                index += len(gap)
            elif regex.startswith((r"\b", r"\B"), index):
                parts.append(regex[index:index + 2])
                index += 2
            elif regex[index] in "^$|":
                parts.append(regex[index])
                index += 1
            else:
                raise ValueError(f"Uncaptured consuming text in mixed-capture regex: {regex!r}")
        return "".join(parts), f"bygroups({', '.join(actions)})"

    def context_state_name(self, pattern: dict) -> str:
        """Name a pushed state after its TextMate scope when one is available."""
        scopes = []
        for value in (pattern.get("contentName"), pattern.get("name")):
            if value:
                scopes.extend(value.split())

        labels = []
        for scope in scopes:
            parts = scope.split(".")
            parts = [part for part in parts if part not in {"meta", "alloy"}]
            if parts:
                labels.append("_".join(parts))

        if labels:
            label = labels[0]
        else:
            begin = pattern.get("begin", "")
            known_begins = {
                r"\blet\b": "let",
                r"\[": "brackets",
                r"\(": "group",
                r"\{": "block",
                "=": "assignment",
                ",": "additional_let_binding",
            }
            label = known_begins.get(begin, "")
            if not label and begin.startswith("(:)"):
                label = "multiplicity_after_separator"
            if not label and begin.startswith("(?="):
                if r"\bsig\b" in begin:
                    label = "signature"
                elif "A-Za-z_" in begin:
                    label = "identifier"
                elif r"\{" in begin:
                    label = "block_boundary"

        if not label:
            self.context_index += 1
            label = f"rule_{self.context_index}"

        base = re.sub(r'[^A-Za-z0-9_]', '_', label)
        count = self.context_names.get(base, 0) + 1
        self.context_names[base] = count
        return base if count == 1 else f"{base}_{count}"

    def add_context(self, pattern: dict, target_state: str | None = None) -> str:
        if "end" not in pattern:
            raise ValueError(f"begin rule has no end pattern: {pattern.get('begin')!r}")
        body = target_state or self.context_state_name(pattern)
        if body in self.states:
            raise ValueError(f"Duplicate generated state {body!r}")
        self.states[body] = []
        self.pushed_states.add(body)

        end = pattern["end"]
        context_name = pattern.get("name", "")
        context_token = self.token_expr(context_name) if context_name else "Text"
        content_token = self.token_expr(pattern.get("contentName")) if pattern.get("contentName") else None
        # Pygments conventionally keeps comment delimiters in the comment token;
        # string delimiters get their own string token subtype.
        if context_token.startswith("Comment."):
            end_action = context_token
        elif content_token and content_token.startswith("String."):
            end_action = "String.Delimiter"
        else:
            end, end_action = self.capture_action(end, pattern.get("endCaptures"), None)
        end_rule = f"({self.regex(end)}, {end_action}, '#pop')"
        body_rules = self.states[body]
        if not pattern.get("applyEndPatternLast"):
            body_rules.append(end_rule)

        for child in pattern.get("patterns", []):
            body_rules.extend(self.compile_pattern(child))

        if pattern.get("applyEndPatternLast"):
            body_rules.append(end_rule)

        fallback_scope = pattern.get("contentName")
        if not fallback_scope:
            name = pattern.get("name", "")
            if name and not all(s.startswith("meta.") for s in name.split()):
                fallback_scope = name
        fallback = self.token_expr(fallback_scope)
        if content_token == "String.Double":
            body_rules.append("(r'[^\"\\\\]+', String.Double)")
        elif context_token == "Comment.Single":
            body_rules.append("(r'[^\\r\\n]+', Comment.Single)")
        elif context_token == "Comment.Multiline":
            body_rules.append("(r'[^*]+', Comment.Multiline)")
            body_rules.append("(r'\\*(?!/)', Comment.Multiline)")
        else:
            body_rules.append(f"(r'(?s:.)', {fallback})")

        begin = pattern["begin"]
        if context_token.startswith("Comment."):
            begin_action = context_token
        elif content_token and content_token.startswith("String."):
            begin_action = "String.Delimiter"
        else:
            begin, begin_action = self.capture_action(begin, pattern.get("beginCaptures"), pattern.get("name"))
        return f"({self.regex(begin)}, {begin_action}, {self.q(body)})"

    def repo_state(self, key: str) -> str:
        if key not in self.repository:
            raise ValueError(f"Unknown TextMate repository reference #{key}")
        state = re.sub(r'[^A-Za-z0-9_]', '_', key)
        if state in self.states:
            return state
        self.states[state] = []
        value = self.repository[key]
        if "begin" in value:
            body = state + ("_content" if state.endswith("_body") else "_body")
            self.states[state].append(self.add_context(value, body))
        elif "match" in value:
            self.states[state].extend(self.compile_pattern(value))
        else:
            for pattern in value.get("patterns", []):
                self.states[state].extend(self.compile_pattern(pattern))
        return state

    def compile_pattern(self, pattern: dict) -> list[str]:
        if "include" in pattern:
            ref = pattern["include"]
            if not ref.startswith("#"):
                raise ValueError(f"External TextMate include is not supported: {ref!r}")
            key = ref[1:]
            state = self.repo_state(key)
            return [f"include({self.q(state)})"]
        if "begin" in pattern:
            return [self.add_context(pattern)]
        if "match" in pattern:
            regex = pattern["match"]
            regex, action = self.capture_action(regex, pattern.get("captures"), pattern.get("name"))
            return [f"({self.regex(regex)}, {action})"]
        unsupported = set(pattern) - {"name", "contentName", "patterns", "repository"}
        if unsupported:
            raise ValueError(f"Unsupported TextMate rule keys: {sorted(unsupported)}")
        raise ValueError(f"Unrecognized TextMate pattern: {pattern!r}")

    def compile(self) -> str:
        self.states["root"] = []
        for pattern in self.grammar.get("patterns", []):
            self.states["root"].extend(self.compile_pattern(pattern))
        self.states["root"].append("(r'(?s:.)', Text)")

        # Force all repository entries to be checked, even if currently unused.
        for key in self.repository:
            self.repo_state(key)

        # Pygments' include() expands states statically and rejects recursive
        # include graphs. Context recursion is represented with state pushes,
        # not recursive includes; verify the remaining include graph is acyclic.
        self.check_include_cycles()
        self.inline_wrappers()

        lines = [
            '"""Generated Pygments lexer for Alloy. Do not edit by hand.',
            'Regenerate with: python pygments/build.py',
            'Source: grammar/alloy.tmLanguage.json',
            '"""',
            "import re",
            "from pygments.lexer import RegexLexer, bygroups, include",
            "from pygments.token import Comment, Keyword, Name, Number, Operator, Punctuation, String, Text",
            "",
            "",
            "class AlloyLexer(RegexLexer):",
            '    """Alloy 6 lexer compiled from the canonical TextMate grammar."""',
            '    name = "Alloy"',
            '    aliases = ["alloy6"]',
            '    filenames = ["*.als"]',
            '    mimetypes = ["text/x-alloy"]',
            "    flags = re.MULTILINE",
            "    # Rules are ordered. Includes share rules; a third tuple item pushes",
            "    # a body state, and '#pop' returns to the enclosing state.",
            "    # Whitespace gaps in mixed captures are explicit Text groups.",
            "    tokens = {",
        ]
        for state, rules in self.states.items():
            lines.append(f"        {state!r}: [")
            lines.extend(f"            {rule}," for rule in rules)
            lines.append("        ],")
        lines.extend(["    }", ""])
        return "\n".join(lines)

    def inline_wrappers(self):
        """Remove one-rule include wrappers, retaining all pushed body states."""
        wrappers = {state: rules[0] for state, rules in self.states.items()
                    if state != "root" and state not in self.pushed_states and len(rules) == 1}

        def expand(rule):
            match = re.fullmatch(r"include\('([^']+)'\)", rule)
            if match and match[1] in wrappers:
                return expand(wrappers[match[1]])
            return rule

        self.states = {state: [expand(rule) for rule in rules]
                       for state, rules in self.states.items() if state not in wrappers}

    def check_include_cycles(self):
        graph: dict[str, set[str]] = {}
        for state, rules in self.states.items():
            graph[state] = set()
            for rule in rules:
                m = re.fullmatch(r"include\('([^']+)'\)", rule)
                if m:
                    graph[state].add(m.group(1))
        visiting, visited = set(), set()

        def visit(node):
            if node in visiting:
                raise ValueError(f"Recursive Pygments include cycle at state {node!r}")
            if node in visited:
                return
            visiting.add(node)
            for child in graph.get(node, ()):
                visit(child)
            visiting.remove(node)
            visited.add(node)

        for node in graph:
            visit(node)


def main():
    parser = argparse.ArgumentParser(description="Build the Pygments Alloy lexer.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if the generated lexer is missing or out of date",
    )
    args = parser.parse_args()

    if not GRAMMAR.is_file():
        raise SystemExit(f"Grammar not found: {GRAMMAR}")
    grammar = json.loads(GRAMMAR.read_text(encoding="utf-8"))
    compiler = Compiler(grammar)
    source = compiler.compile()
    compile(source, str(OUTPUT), "exec")
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != source:
            print(f"{OUTPUT.relative_to(ROOT)} is out of date; run python pygments/build.py", file=sys.stderr)
            return 1
        print(f"{OUTPUT.relative_to(ROOT)} is up to date ({len(compiler.states)} states)")
        return 0

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(source, encoding="utf-8")
    print(f"Generated {OUTPUT.relative_to(ROOT)} ({len(compiler.states)} states)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
