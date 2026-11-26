#!/usr/bin/env python3
"""Translate the canonical Alloy TextMate grammar to CodeMirror 6."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = ROOT / "VERSION"
PACKAGE = ROOT / "codemirror" / "package.json"
PACKAGE_LOCK = ROOT / "codemirror" / "package-lock.json"
GRAMMAR = ROOT / "grammar" / "alloy.tmLanguage.json"
OUTPUT = ROOT / "codemirror" / "src" / "alloy.js"
LICENSE_SOURCE = ROOT / "LICENSE"
LICENSE_OUTPUT = ROOT / "codemirror" / "LICENSE"

RUNTIME = r'''// Generated from grammar/alloy.tmLanguage.json by codemirror/build.py.
// Ordered scanners follow the grammar's repository groups. Shared streaming
// mechanics (context stack, lookbehind history, and captures) follow below.
import {StreamLanguage} from "@codemirror/language";
import {tags} from "@lezer/highlight";

const NO_MATCH = Symbol("no match");
const RESTART = Symbol("restart after context entry");
function scanNothing() { return NO_MATCH; }

// Grammar-derived scanners. Rule order is significant. Regex flags: `y`
// anchors a match at the current position; `d` supplies capture boundaries.
__SCANNERS__

// Streaming support. A frame stores its ending pattern and body scanner.
// NO_MATCH tries the next rule; RESTART rescans after a zero-width begin.
function startState() {
  return {
    contexts: [], pending: [], delimiterDepth: 0, history: "",
    zeroRule: null, zeroPosition: -1,
  };
}

function copyState(state) {
  // Frames and pending pieces are immutable; only the arrays need copying.
  return {...state, contexts: state.contexts.slice(), pending: state.pending.slice()};
}

function matchAt(expression, stream, state) {
  // Reset lastIndex on every call, including regexes shared by copied frames.
  // Recent text supplies lookbehind context across CodeMirror's line streams.
  if (!expression.source.includes("(?<=")) {
    expression.lastIndex = stream.pos;
    return expression.exec(stream.string);
  }
  const prefix = state.history;
  expression.lastIndex = prefix.length;
  const match = expression.exec(prefix + stream.string.slice(stream.pos));
  if (!match) return null;
  match.index = 0;
  match.indices = match.indices.map(span => span && [span[0] - prefix.length, span[1] - prefix.length]);
  return match;
}

function enterContext(stream, state, rule) {
  // A zero-width begin may be retried after its context ends without consuming
  // text. Suppress that one rule until the stream makes progress.
  if (state.zeroRule === rule.id && state.zeroPosition === stream.pos) return NO_MATCH;
  const match = matchAt(rule.begin, stream, state);
  if (!match) return NO_MATCH;
  if (!match[0].length) {
    state.zeroRule = rule.id;
    state.zeroPosition = stream.pos;
  }
  state.contexts.push({...rule, openingStream: stream, openingPosition: stream.pos});
  const style = rule.beginStyle ?? rule.delimiterStyle ?? rule.style ?? null;
  return match[0].length
    ? emitMatch(stream, state, match, style, rule.beginCaptures)
    : RESTART;
}

function emitMatch(stream, state, match, style = null, captures = null) {
  // Most rules style the entire match. Only mixed captures need a queue:
  // StreamLanguage can return just one style from each token() call.
  if (!captures) return consume(stream, state, match[0], style);
  const text = match[0];
  const ranges = [];
  const boundaries = new Set([0, text.length]);
  for (const [index, tag] of Object.entries(captures)) {
    const span = match.indices[Number(index)];
    if (!span) continue;
    const from = span[0] - match.index;
    const to = span[1] - match.index;
    ranges.push({from, to, tag});
    boundaries.add(from);
    boundaries.add(to);
  }
  const points = [...boundaries].sort((a, b) => a - b);
  for (let i = 0; i < points.length - 1; i++) {
    const from = points[i], to = points[i + 1];
    let tag = style;
    for (const range of ranges) {
      if (range.from <= from && range.to >= to) tag = range.tag;
    }
    state.pending.push({tag, text: text.slice(from, to)});
  }
  return state.pending.length ? emitPending(stream, state) : null;
}

function emitPending(stream, state) {
  const part = state.pending.shift();
  return consume(stream, state, part.text, part.tag);
}

function consume(stream, state, text, style) {
  stream.pos += text.length;
  state.history = (state.history + text).replace(/\s+/g, " ").slice(-64);
  state.zeroRule = null;
  state.zeroPosition = -1;
  if (style === "punctuation") {
    if (/^[([{]$/.test(text)) state.delimiterDepth++;
    else if (/^[)\]}]$/.test(text)) state.delimiterDepth = Math.max(0, state.delimiterDepth - 1);
  }
  return style;
}

function token(stream, state) {
  if (state.pending.length) return emitPending(stream, state);
  // Line comments must also end when CodeMirror skips a blank line.
  while (state.contexts.length && state.contexts.at(-1).end.source === "$" && stream !== state.contexts.at(-1).openingStream) {
    state.contexts.pop();
  }
  const spaceContext = state.contexts.at(-1);
  if (stream.eatSpace()) {
    state.history = (state.history + stream.current()).replace(/\s+/g, " ").slice(-64);
    return spaceContext?.contentStyle || spaceContext?.style || null;
  }

  while (state.contexts.length && state.contexts.at(-1).end.source === "(?<=\\})"
         && (stream !== state.contexts.at(-1).openingStream || stream.pos !== state.contexts.at(-1).openingPosition)
         && state.history.trimEnd().endsWith("}")) {
    state.contexts.pop();
  }
  const context = state.contexts.at(-1);
  if (context && (stream !== context.openingStream || stream.pos !== context.openingPosition)) {
    const ending = matchAt(context.end, stream, state);
    if (ending) {
      state.contexts.pop();
      if (ending[0].length) {
        const style = context.endStyle ?? context.delimiterStyle ?? context.style ?? null;
        return emitMatch(stream, state, ending, style, context.endCaptures);
      }
      return token(stream, state);
    }
  }

  const result = context ? context.scan(stream, state) : scanRoot(stream, state);
  if (result === RESTART) return token(stream, state);
  if (result !== NO_MATCH) return result;

  if (stream.eol()) return null;
  stream.next();
  state.history = (state.history + stream.current()).replace(/\s+/g, " ").slice(-64);
  return context?.contentStyle || context?.style || null;
}

function indent(state, textAfter, context) {
  const closes = /^[})\]]/.test(textAfter);
  return Math.max(0, state.delimiterDepth - (closes ? 1 : 0)) * context.unit;
}

const tokenTable = {
  comment: tags.comment,
  docComment: tags.docComment,
  string: tags.string,
  number: tags.number,
  constant: tags.constant(tags.variableName),
  typeName: tags.typeName,
  atom: tags.atom,
  variableName: tags.variableName,
  punctuation: tags.punctuation,
  operator: tags.operator,
  keyword: tags.keyword,
};

export const alloy = StreamLanguage.define({
  name: "alloy",
  startState,
  copyState,
  token,
  indent,
  languageData: {commentTokens: {line: "//", block: {open: "/*", close: "*/"}}},
  tokenTable,
});

export default alloy;
'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="check generated CodeMirror module freshness")
    args = parser.parse_args()
    version = VERSION.read_text(encoding="utf-8").strip()
    package = json.loads(PACKAGE.read_text(encoding="utf-8"))
    package_lock = json.loads(PACKAGE_LOCK.read_text(encoding="utf-8"))
    grammar = json.loads(GRAMMAR.read_text(encoding="utf-8"))
    repository = grammar["repository"]

    def scope_tag(scope: str | None) -> str | None:
        if not scope:
            return None
        names = [name for name in scope.split() if not name.startswith("meta.")]
        for name in names:
            if name.startswith("punctuation.definition.comment."): return "comment"
            if name.startswith("punctuation.definition.string."): return "string"
            if name.startswith("comment.block.documentation."): return "docComment"
            if name.startswith("comment."): return "comment"
            if name.startswith("string."): return "string"
            if name.startswith("constant.numeric."): return "number"
            if name.startswith("constant.character."): return "string"
            if name.startswith("support.constant."): return "constant"
            if name.startswith("support.type."): return "typeName"
            if name.startswith("variable.language."): return "atom"
            if name.startswith("variable.other."): return "variableName"
            if name.startswith("punctuation."): return "punctuation"
            if name.startswith("keyword.operator."): return "operator"
            if name.startswith("keyword.") or name.startswith("storage."): return "keyword"
        return None

    fields = ("match", "begin", "end", "include")

    def combine_adjacent_matches(patterns: list[dict]) -> list[dict]:
        """Join adjacent same-style leaf matches without changing rule order."""
        combined: list[dict] = []
        alternatives: list[str] = []
        for rule in patterns:
            if ("match" in rule and rule.get("style") and not rule.get("captures")
                    and combined and combined[-1].get("style") == rule["style"]
                    and "match" in combined[-1] and not combined[-1].get("captures")):
                previous = combined[-1]
                alternatives.append(rule["match"])
                previous["match"] = "|".join(f"(?:{pattern})" for pattern in alternatives)
            else:
                combined.append(rule)
                alternatives = [rule["match"]] if "match" in rule else []
        return combined

    def captures_for(captures: dict) -> dict:
        result = {}
        for key, capture in captures.items():
            if style := scope_tag(capture.get("name")):
                result[key] = style
        return result

    def compile_rule(rule: dict) -> dict:
        result = {key: rule[key] for key in fields if key in rule}
        if "begin" in result:
            # StreamLanguage consumes spaces before applying a lookbehind.
            result["begin"] = result["begin"].replace(r"(?<=sig)", r"(?<=sig\s*)")
        if "match" in result:
            # CodeMirror consumes inter-token spaces before matching. Move
            # these grammar lookbehinds across that skipped space.
            result["match"] = (result["match"]
                               .replace(r"(?<=:)\s*", r"(?<=:\s*)")
                               .replace(r"(?<=->)\s*", r"(?<=->\s*)"))
        if rule.get("name"):
            result["contextName"] = rule["name"].split()[0]
        if style := scope_tag(rule.get("name")):
            result["style"] = style
        if style := scope_tag(rule.get("contentName")):
            result["contentStyle"] = style
        for key in ("captures", "beginCaptures", "endCaptures"):
            if key in rule and (compiled := captures_for(rule[key])):
                result[key] = compiled
        if "patterns" in rule:
            children = [compile_rule(child) for child in rule["patterns"]]
            useful = [child for child in children
                      if child.get("style") or child.get("contentStyle")
                      or child.get("include") or child.get("patterns")
                      or child.get("begin")]
            result["patterns"] = combine_adjacent_matches(useful)
        if "match" in result and not result.get("style") and not result.get("captures"):
            return {}
        return result

    rules = [compiled for rule in grammar["patterns"] if (compiled := compile_rule(rule))]
    compiled_repository = {key: compiled for key, value in repository.items()
                           if (compiled := compile_rule(value))}
    def identifier(name: str) -> str:
        parts = re.findall(r"[A-Za-z0-9]+", name.replace("$", "self"))
        return "scan" + "".join(part.title() for part in parts)

    scanner_names = {key: identifier(key) for key in compiled_repository}
    scanner_names["$self"] = "scanRoot"
    generated_scanners: dict[str, str] = {}
    inline_scanners: dict[int, str] = {}
    rule_keys: dict[int, str] = {}
    rule_number = 0

    def scanner_for_context(rule: dict, owner: str) -> str:
        nonlocal rule_number
        key = id(rule)
        if key not in inline_scanners:
            rule_number += 1
            rule_keys[key] = f"rule{rule_number}"
            if not rule.get("patterns"):
                inline_scanners[key] = "scanNothing"
                return "scanNothing"
            patterns = rule["patterns"]
            if len(patterns) == 1 and "include" in patterns[0]:
                target = patterns[0]["include"].removeprefix("#")
                inline_scanners[key] = scanner_names[target]
                return inline_scanners[key]
            # Anonymous grammar contexts inherit their owner's name rather
            # than becoming anonymous scanContext7 / scanContext8 functions.
            label = rule.get("contextName")
            base = identifier(label.replace(".alloy", "")) if label else owner + "Body"
            used = set(inline_scanners.values()) | set(scanner_names.values())
            inline_scanners[key] = base if base not in used else f"{base}{rule_number}"
            generated_scanners[inline_scanners[key]] = emit_scanner(
                inline_scanners[key], rule.get("patterns", []))
        return inline_scanners[key]

    def regex_literal(pattern: str) -> str:
        """Keep regex syntax visible instead of escaping it as a JS string."""
        pattern = re.sub(r"(\\*)/", lambda m: m[1] + (r"\/" if len(m[1]) % 2 == 0 else "/"), pattern)
        for char, escaped in (("\n", r"\n"), ("\r", r"\r"), ("\u2028", r"\u2028"), ("\u2029", r"\u2029")):
            pattern = pattern.replace(char, escaped)
        return f"/{pattern}/dy"

    def match_styles(rule: dict, capture_key: str) -> tuple[str | None, dict]:
        captures = dict(rule.get(capture_key, {}))
        # A capture for group zero simply supplies the whole-match style.
        style = captures.pop("0", rule.get("style"))
        if all(value == style for value in captures.values()):
            captures = {}
        return style, captures

    def emit_rule(rule: dict, owner: str, terminal: bool = False) -> str:
        if "include" in rule:
            target = rule["include"][1:] if rule["include"] != "$self" else "$self"
            function = scanner_names.get(target)
            if not function:
                raise ValueError(f"Unsupported TextMate include: {rule['include']}")
            if terminal:
                return f"return {function}(stream, state);"
            return f"if ((result = {function}(stream, state)) !== NO_MATCH) return result;"
        if "match" in rule:
            style, captures = match_styles(rule, "captures")
            extra = f", {json.dumps(captures)}" if captures else ""
            return (f"if ((match = matchAt({regex_literal(rule['match'])}, stream, state)))\n"
                    f"  return emitMatch(stream, state, match, {json.dumps(style)}{extra});")
        if "begin" in rule:
            child = scanner_for_context(rule, owner)
            properties = [
                f"id: {json.dumps(rule_keys[id(rule)])}",
                f"begin: {regex_literal(rule['begin'])}, end: {regex_literal(rule['end'])}",
                f"scan: {child}",
            ]
            for key in ("style", "contentStyle"):
                if rule.get(key):
                    properties.append(f"{key}: {json.dumps(rule[key])}")
            begin_style, begin_captures = match_styles(rule, "beginCaptures")
            end_style, end_captures = match_styles(rule, "endCaptures")
            if begin_style == end_style and begin_style != rule.get("style"):
                properties.append(f"delimiterStyle: {json.dumps(begin_style)}")
            for prefix, style, captures in (("begin", begin_style, begin_captures),
                                            ("end", end_style, end_captures)):
                if begin_style != end_style and style != rule.get("style"):
                    properties.append(f"{prefix}Style: {json.dumps(style)}")
                if captures:
                    properties.append(f"{prefix}Captures: {json.dumps(captures)}")
            opening = "return enterContext(stream, state, {" if terminal else "if ((result = enterContext(stream, state, {"
            closing = "});" if terminal else "})) !== NO_MATCH) return result;"
            return (opening + "\n  "
                    + ",\n  ".join(properties)
                    + ",\n" + closing)
        return ""

    def emit_scanner(name: str, patterns: list[dict]) -> str:
        terminal = len(patterns) == 1 and bool(patterns[0].get("begin") or patterns[0].get("include"))
        body = []
        for rule in patterns:
            if rule.get("include") or rule.get("match") or rule.get("begin"):
                body.append(emit_rule(rule, name, terminal))
        variables = []
        if any("match = " in line for line in body):
            variables.append("match")
        if any("result = " in line for line in body):
            variables.append("result")
        declaration = f"  let {', '.join(variables)};\n" if variables else ""
        statements = "\n".join(body).splitlines()
        return (f"function {name}(stream, state) {{\n" + declaration
                + "\n".join("  " + line for line in statements)
                + ("\n}" if terminal else "\n  return NO_MATCH;\n}"))

    # Generate one readable function per TextMate repository group. Context
    # rules get their own child function and push that function on the stack.
    for key, rule in compiled_repository.items():
        generated_scanners[scanner_names[key]] = emit_scanner(
            scanner_names[key], [rule] if rule.get("begin") or rule.get("match") else rule.get("patterns", []))
    generated_scanners["scanRoot"] = emit_scanner("scanRoot", rules)

    # Several named TextMate groups have identical rule bodies. Keep their
    # names as aliases for readable call sites, but emit each scanner body once.
    scanner_bodies: dict[str, str] = {}
    scanner_functions: list[str] = []
    scanner_aliases: list[str] = []
    for name, source in generated_scanners.items():
        body = source.replace(f"function {name}(", "function __scanner(", 1)
        canonical = scanner_bodies.get(body)
        if canonical:
            scanner_aliases.append(f"const {name} = {canonical};")
        else:
            scanner_bodies[body] = name
            scanner_functions.append(source)
    scanner_source = "\n\n".join(scanner_functions)
    if scanner_aliases:
        scanner_source += "\n\n" + "\n".join(scanner_aliases)
    generated = RUNTIME.replace("__SCANNERS__", scanner_source)
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != generated:
            print("CodeMirror module is out of date; run python codemirror/build.py", file=sys.stderr)
            return 1
        if not LICENSE_OUTPUT.is_file() or LICENSE_OUTPUT.read_bytes() != LICENSE_SOURCE.read_bytes():
            print("CodeMirror LICENSE is out of date; run python codemirror/build.py", file=sys.stderr)
            return 1
        if package.get("version") != version or package_lock.get("version") != version or package_lock.get("packages", {}).get("", {}).get("version") != version:
            print("CodeMirror package versions do not match VERSION; run python codemirror/build.py", file=sys.stderr)
            return 1
        print("CodeMirror module is up to date.")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(generated, encoding="utf-8")
    LICENSE_OUTPUT.write_bytes(LICENSE_SOURCE.read_bytes())
    if package.get("version") != version:
        package["version"] = version
        PACKAGE.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
    if (package_lock.get("version") != version
            or package_lock.get("packages", {}).get("", {}).get("version") != version):
        package_lock["version"] = version
        package_lock["packages"][""]["version"] = version
        PACKAGE_LOCK.write_text(json.dumps(package_lock, indent=2) + "\n", encoding="utf-8")
    print(f"Built {OUTPUT.relative_to(ROOT)} from {GRAMMAR.relative_to(ROOT)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
