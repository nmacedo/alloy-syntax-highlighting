import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import {fileURLToPath} from "node:url";
import {EditorState} from "@codemirror/state";
import {ensureSyntaxTree, getIndentation, syntaxTree} from "@codemirror/language";
import {alloy} from "../src/alloy.js";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "../..");
const FIXTURES = path.join(ROOT, "tests", "fixtures");
const EXPECTED = path.join(ROOT, "tests", "expected", "scopes.json");
const KNOWN_FAILURES = path.join(ROOT, "tests", "expected", "known-failures.json");

function failureKey(item) {
  return JSON.stringify([
    item.fixture,
    item.line,
    item.token,
    item.occurrence || 0,
    item.kind,
    item.scope
  ]);
}

function styleForScope(scope) {
  if (!scope) return null;
  if (scope.startsWith("punctuation.definition.comment")) return "comment";
  if (scope.startsWith("punctuation.definition.string")) return "string";
  if (scope.startsWith("comment.block.documentation.")) return "docComment";
  if (scope.startsWith("comment.")) return "comment";
  if (scope.startsWith("string.")) return "string";
  if (scope.startsWith("constant.numeric.")) return "number";
  if (scope.startsWith("constant.character.")) return "string";
  if (scope.startsWith("support.constant.")) return "constant";
  if (scope.startsWith("support.type.")) return "typeName";
  if (scope.startsWith("variable.language.")) return "atom";
  if (scope.startsWith("variable.other.")) return "variableName";
  if (scope.startsWith("punctuation.")) return "punctuation";
  if (scope.startsWith("keyword.operator.")) return "operator";
  if (scope.startsWith("keyword.") || scope.startsWith("storage.")) return "keyword";
  return null;
}

function findOccurrence(line, needle, occurrence = 0) {
  if (/^[A-Za-z_][A-Za-z0-9_]*$/.test(needle)) {
    const matches = [...line.matchAll(new RegExp(`(?<![A-Za-z0-9_])${needle}(?![A-Za-z0-9_])`, "g"))];
    assert.ok(matches[occurrence], `${needle} occurrence ${occurrence} missing in ${line}`);
    return matches[occurrence].index;
  }
  let position = -1;
  for (let i = 0; i <= occurrence; i++) {
    position = line.indexOf(needle, position + 1);
    assert.notEqual(position, -1, `${needle} occurrence ${occurrence} missing in ${line}`);
  }
  if (needle.startsWith('"') && needle.endsWith('"')) return position + 1;
  if (needle.startsWith("/*") && needle.endsWith("*/")) return position + 2;
  return position;
}

function tokensForState(state) {
  const tokens = [];
  const tree = ensureSyntaxTree(state, state.doc.length, 1000) || syntaxTree(state);
  tree.iterate({
    enter(node) {
      if (!node.type.isTop) tokens.push({from: node.from, to: node.to, style: node.type.name});
    },
  });
  return tokens;
}

function tokenize(source) {
  const state = EditorState.create({doc: source, extensions: [alloy]});
  return {state, tokens: tokensForState(state)};
}

test("all fixture scope assertions map to CodeMirror tags", () => {
  const expected = JSON.parse(fs.readFileSync(EXPECTED, "utf8"));
  const known = JSON.parse(fs.readFileSync(KNOWN_FAILURES, "utf8")).codemirror;
  const knownByKey = new Map(known.map(item => [failureKey(item), item]));
  const seenKnown = new Set();
  let checked = 0;
  let intentionallyUnstyled = 0;
  let xfailed = 0;
  const failures = [];

  function recordResult(filename, assertion, kind, scope, passed, observed) {
    const entry = {
      fixture: filename,
      line: assertion.line,
      token: assertion.token,
      occurrence: assertion.occurrence || 0,
      kind,
      scope
    };
    const key = failureKey(entry);
    const knownFailure = knownByKey.get(key);
    const label = `${filename}:${entry.line} ${JSON.stringify(entry.token)} ${kind} ${scope}`;
    if (knownFailure) {
      seenKnown.add(key);
      if (passed) {
        failures.push(`XPASS ${label}: remove the stale known-failure entry`);
      } else if (observed !== knownFailure.observed) {
        failures.push(
          `Known failure changed for ${label}: expected observed ${knownFailure.observed}, got ${observed}`
        );
      } else {
        xfailed += 1;
        console.log(`XFAIL ${label} [${knownFailure.reason}]`);
      }
    } else if (!passed) {
      failures.push(`${label}: got ${observed}`);
    }
  }

  for (const [filename, assertions] of Object.entries(expected)) {
    const fixturePath = path.join(FIXTURES, filename);
    assert.ok(fs.existsSync(fixturePath), `Missing fixture: ${filename}`);
    const source = fs.readFileSync(fixturePath, "utf8");
    const lines = source.split(/(?<=\n)/);
    const offsets = [];
    let offset = 0;
    for (const line of lines) { offsets.push(offset); offset += line.length; }
    const {tokens} = tokenize(source);

    for (const assertion of assertions) {
      const lineNumber = assertion.line;
      const line = (lines[lineNumber - 1] || "").replace(/[\r\n]+$/, "");
      const local = findOccurrence(line, assertion.token, assertion.occurrence || 0);
      const absolute = offsets[lineNumber - 1] + local;
      let length = assertion.token.length;
      if (assertion.token.startsWith('"') && assertion.token.endsWith('"')) length -= 2;
      else if (assertion.token.startsWith("/*") && assertion.token.endsWith("*/")) length -= 4;
      const end = absolute + length;
      const overlapping = tokens.filter(token => token.from < end && token.to > absolute);
      if (!overlapping.length) {
        failures.push(`${filename}:${lineNumber}: no syntax token overlaps ${JSON.stringify(assertion.token)}`);
        continue;
      }
      const wanted = styleForScope(assertion.scope);
      if (assertion.scope && wanted == null) intentionallyUnstyled++;
      if (wanted != null) {
        checked++;
        const passed = overlapping.every(token => token.style === wanted);
        const observed = [...new Set(overlapping.map(token => token.style || "(unstyled)"))].join(", ");
        recordResult(filename, assertion, "scope", assertion.scope, passed, observed);
      }
      for (const forbiddenScope of assertion.notScopes || []) {
        const forbidden = styleForScope(forbiddenScope);
        // StreamLanguage uses one shared punctuation tag for all TextMate
        // delimiter sub-scopes, so those negative distinctions are not testable.
        if (forbidden && forbidden !== "punctuation" && overlapping.some(token => token.style === forbidden)) {
          const observed = [...new Set(overlapping.map(token => token.style || "(unstyled)"))].join(", ");
          recordResult(filename, assertion, "notScope", forbiddenScope, false, observed);
        } else if (forbidden && forbidden !== "punctuation") {
          const observed = [...new Set(overlapping.map(token => token.style || "(unstyled)"))].join(", ");
          recordResult(filename, assertion, "notScope", forbiddenScope, true, observed);
        }
      }
    }
  }

  for (const knownFailure of known) {
    if (!seenKnown.has(failureKey(knownFailure))) {
      failures.push(
        `Stale known-failure entry: ${knownFailure.fixture}:${knownFailure.line} ` +
        `${JSON.stringify(knownFailure.token)} ${knownFailure.kind} ${knownFailure.scope}`
      );
    }
  }

  assert.deepEqual(failures, [], failures.join("\n"));
  console.log(`Checked ${checked} mapped scope assertions; ${intentionallyUnstyled} meta-scope assertions intentionally have no visual tag; observed ${xfailed} known failures.`);
});

test("indentation follows Alloy block and grouping delimiters", () => {
  const source = "sig A {\nfield: A\n}\n";
  const state = EditorState.create({doc: source, extensions: [alloy]});
  assert.equal(getIndentation(state, state.doc.line(2).from), 2);
  assert.equal(getIndentation(state, state.doc.line(3).from), 0);
});

test("incremental edits produce the same tokens as a fresh parse", () => {
  for (const filename of fs.readdirSync(FIXTURES).filter(name => name.endsWith(".als"))) {
    const source = fs.readFileSync(path.join(FIXTURES, filename), "utf8");
    let {state} = tokenize(source);
    const position = source.indexOf("\n", Math.floor(source.length / 2)) + 1;
    const comment = "// incremental edit\n";
    const edits = [
      {from: position, insert: comment},
      {from: position, to: position + comment.length, insert: ""},
      {from: 0, insert: "/*\n"},
      {from: 0, to: 3, insert: ""},
    ];
    for (const changes of edits) {
      state = state.update({changes}).state;
      const actual = tokensForState(state);
      const fresh = tokenize(state.doc.toString()).tokens;
      assert.deepEqual(actual, fresh, `${filename}: ${JSON.stringify(changes)}`);
    }
  }
});

test("meta-identifiers use the standard constant tag", () => {
  const {tokens} = tokenize("static$ field$ sig$ var$\n");
  const source = "static$ field$ sig$ var$\n";
  for (const value of ["static$", "field$", "sig$", "var$"]) {
    const start = source.indexOf(value);
    assert.ok(tokens.some(token => token.from < start + value.length && token.to > start && token.style === "constant"),
      `missing constant tag for ${value}`);
  }
});

test("documentation comments retain a distinct tag", () => {
  const {tokens} = tokenize("/** documentation */\n/* ordinary */\n");
  assert.ok(tokens.some(token => token.style === "docComment"));
  assert.ok(tokens.some(token => token.style === "comment"));
});
