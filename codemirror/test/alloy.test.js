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

function tokenize(source) {
  const state = EditorState.create({doc: source, extensions: [alloy]});
  const tokens = [];
  const tree = ensureSyntaxTree(state, source.length, 1000) || syntaxTree(state);
  tree.iterate({
    enter(node) {
      if (!node.type.isTop) tokens.push({from: node.from, to: node.to, style: node.type.name});
    },
  });
  return {state, tokens};
}

test("all fixture scope assertions map to CodeMirror tags", () => {
  const expected = JSON.parse(fs.readFileSync(EXPECTED, "utf8"));
  let checked = 0;
  let intentionallyUnstyled = 0;
  const failures = [];

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
        if (overlapping.some(token => token.style !== wanted)) {
          failures.push(`${filename}:${lineNumber}: ${JSON.stringify(assertion.token)} expected ${wanted}, got ${JSON.stringify(overlapping)}`);
        }
      }
      for (const forbiddenScope of assertion.notScopes || []) {
        const forbidden = styleForScope(forbiddenScope);
        // StreamLanguage uses one shared punctuation tag for all TextMate
        // delimiter sub-scopes, so those negative distinctions are not testable.
        if (forbidden && forbidden !== "punctuation" && overlapping.some(token => token.style === forbidden)) {
          failures.push(`${filename}:${lineNumber}: ${JSON.stringify(assertion.token)} unexpectedly styled ${forbidden} (${forbiddenScope})`);
        }
      }
    }
  }

  assert.deepEqual(failures, [], failures.join("\n"));
  console.log(`Checked ${checked} mapped scope assertions; ${intentionallyUnstyled} meta-scope assertions intentionally have no visual tag.`);
});

test("indentation follows Alloy block and grouping delimiters", () => {
  const source = "sig A {\nfield: A\n}\n";
  const state = EditorState.create({doc: source, extensions: [alloy]});
  assert.equal(getIndentation(state, state.doc.line(2).from), 2);
  assert.equal(getIndentation(state, state.doc.line(3).from), 0);
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
