#!/usr/bin/env node
"use strict";

const assert = require("node:assert/strict");
const { execFileSync } = require("node:child_process");
const fs = require("node:fs");
const path = require("node:path");
const vscodeTextmate = require("vscode-textmate");
const vscodeOniguruma = require("vscode-oniguruma");

const ROOT = path.resolve(__dirname, "..");
const FIXTURES = path.join(__dirname, "fixtures");
const EXPECTED = path.join(__dirname, "expected", "scopes.json");
const GRAMMAR_CANDIDATES = [
  path.join(ROOT, "vscode", "syntaxes", "alloy.tmLanguage.json"),
  path.join(ROOT, "grammar", "alloy.tmLanguage.json")
];
const GRAMMAR_PATH = GRAMMAR_CANDIDATES.find(candidate => fs.existsSync(candidate)) || GRAMMAR_CANDIDATES[0];

function parseArguments(argv) {
  const options = { grammar: GRAMMAR_PATH, file: null, printScopes: false, preview: false };
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === "--grammar" || argument === "--file") {
      const value = argv[index + 1];
      assert.ok(value, `Missing value after ${argument}`);
      options[argument === "--grammar" ? "grammar" : "file"] = path.resolve(value);
      index += 1;
    } else if (argument === "--print-scopes") {
      options.printScopes = true;
    } else if (argument === "--preview") {
      options.preview = true;
    } else {
      assert.fail(`Unknown argument: ${argument}`);
    }
  }
  assert.ok(!options.printScopes || options.file,
    "--print-scopes requires --file <fixture>");
  assert.ok(!options.preview || options.file,
    "--preview requires --file <fixture>");
  assert.ok(!(options.preview && options.printScopes),
    "--preview and --print-scopes cannot be used together");
  return options;
}

function readGrammar(grammarPath) {
  assert.ok(fs.existsSync(grammarPath),
    `Grammar not found: ${grammarPath}\nRun python scripts/build.py first.`);
  if (grammarPath.endsWith(".tmLanguage")) {
    const converted = execFileSync(process.env.PYTHON || "python3", [
      "-c",
      "import json, plistlib, sys; json.dump(plistlib.load(open(sys.argv[1], 'rb')), sys.stdout)",
      grammarPath
    ], { encoding: "utf8" });
    return JSON.parse(converted);
  }
  return JSON.parse(fs.readFileSync(grammarPath, "utf8"));
}

async function loadGrammar(grammarPath) {
  const buffer = fs.readFileSync(require.resolve("vscode-oniguruma/release/onig.wasm"));
  const wasm = buffer.buffer.slice(buffer.byteOffset, buffer.byteOffset + buffer.byteLength);
  await vscodeOniguruma.loadWASM(wasm);

  const rawGrammar = readGrammar(grammarPath);
  const registry = new vscodeTextmate.Registry({
    onigLib: Promise.resolve({
      createOnigScanner: patterns => new vscodeOniguruma.OnigScanner(patterns),
      createOnigString: value => new vscodeOniguruma.OnigString(value)
    }),
    loadGrammar: async scopeName => scopeName === "source.alloy" ? rawGrammar : null
  });
  const grammar = await registry.loadGrammar("source.alloy");
  assert.ok(grammar, "Could not load source.alloy grammar");
  return grammar;
}

function tokenizeFile(grammar, filePath) {
  const source = fs.readFileSync(filePath, "utf8").replace(/\r\n/g, "\n");
  let ruleStack = vscodeTextmate.INITIAL;
  return source.split("\n").map(text => {
    const result = grammar.tokenizeLine(text, ruleStack);
    ruleStack = result.ruleStack;
    return { text, tokens: result.tokens };
  });
}

function locate(line, text, occurrence = 0) {
  let index = -1;

  // Identifier expectations must match complete identifiers. Otherwise a
  // declaration name such as "p" can accidentally match the "p" in "pred".
  if (/^[A-Za-z_][A-Za-z0-9_]*$/.test(text)) {
    const escaped = text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const pattern = new RegExp(`(?<![A-Za-z0-9_])${escaped}(?![A-Za-z0-9_])`, "g");
    let match;
    for (let i = 0; i <= occurrence; i += 1) {
      match = pattern.exec(line);
      assert.ok(match,
        `Cannot find whole-identifier occurrence ${occurrence} of ${JSON.stringify(text)} in ${JSON.stringify(line)}`);
    }
    return match.index;
  }

  let from = 0;
  for (let i = 0; i <= occurrence; i += 1) {
    index = line.indexOf(text, from);
    assert.notEqual(index, -1,
      `Cannot find occurrence ${occurrence} of ${JSON.stringify(text)} in ${JSON.stringify(line)}`);
    from = index + text.length;
  }

  // A quoted string's opening quote has the delimiter scope, while its
  // contents carry string.quoted.double. Probe inside the quotes so the same
  // fixture location can assert both meta.string and string-content scopes.
  if (text.length >= 2 && text.startsWith('"') && text.endsWith('"')) {
    return index + 1;
  }
  return index;
}

function scopesAt(line, column) {
  const token = line.tokens.find(t => t.startIndex <= column && column < t.endIndex);
  return token ? token.scopes : [];
}

function hasScope(scopes, expected) {
  return scopes.some(scope => scope === expected || scope.startsWith(`${expected}.`));
}

function printScopes(grammar, grammarPath, filePath) {
  const lines = tokenizeFile(grammar, filePath);
  console.log(`Grammar: ${path.relative(ROOT, grammarPath)}`);
  console.log(`File: ${path.relative(ROOT, filePath)}`);
  for (let lineIndex = 0; lineIndex < lines.length; lineIndex += 1) {
    const line = lines[lineIndex];
    for (const token of line.tokens) {
      const value = line.text.slice(token.startIndex, token.endIndex);
      if (!value) continue;
      console.log(
        `${String(lineIndex + 1).padStart(4)}:${String(token.startIndex + 1).padEnd(4)} ` +
        `${JSON.stringify(value).padEnd(24)} ${token.scopes.join(" > ")}`
      );
    }
  }
}

function lexicalScope(scopes) {
  return [...scopes].reverse().find(scope =>
    !scope.startsWith("meta.") && !scope.startsWith("source.")
  ) || "(unscoped)";
}

function scopeColorMap(lines) {
  const scopes = [...new Set(lines.flatMap(line =>
    line.tokens.map(token => lexicalScope(token.scopes))
  ))].sort();
  const levels = [135, 175, 215, 255];
  const palette = [];
  for (const red of levels) {
    for (const green of levels) {
      for (const blue of levels) {
        palette.push(16 + 36 * levels.indexOf(red) + 6 * levels.indexOf(green) + levels.indexOf(blue));
      }
    }
  }
  if (scopes.length > palette.length) {
    throw new Error(`Preview has ${scopes.length} distinct token scopes, exceeding the ${palette.length}-color palette`);
  }
  return new Map(scopes.map((scope, index) => [scope, palette[index]]));
}

function printPreview(grammar, grammarPath, filePath) {
  const lines = tokenizeFile(grammar, filePath);
  const colors = scopeColorMap(lines);
  console.log(`TextMate preview: ${path.relative(ROOT, grammarPath)}`);
  console.log(`Fixture: ${path.relative(ROOT, filePath)}\n`);
  const colorEnabled = Boolean(process.stdout.isTTY && !process.env.NO_COLOR);
  for (const line of lines) {
    let rendered = "";
    for (const token of line.tokens) {
      const value = line.text.slice(token.startIndex, token.endIndex);
      const scope = lexicalScope(token.scopes);
      const color = colors.get(scope);
      rendered += colorEnabled ? `\u001b[38;5;${color}m${value}\u001b[0m` : value;
    }
    console.log(rendered);
  }
  if (colorEnabled) {
    console.log("\nToken scope colors:");
    for (const [scope, color] of colors) {
      console.log(`\u001b[38;5;${color}m■\u001b[0m ${scope}`);
    }
  }
}

async function main() {
  const options = parseArguments(process.argv.slice(2));
  const grammar = await loadGrammar(options.grammar);
  if (options.preview) {
    printPreview(grammar, options.grammar, options.file);
    return;
  }
  if (options.printScopes) {
    printScopes(grammar, options.grammar, options.file);
    return;
  }

  const expectations = JSON.parse(fs.readFileSync(EXPECTED, "utf8"));
  let fixtureExpectations = Object.entries(expectations);
  if (options.file) {
    const fixtureName = path.relative(FIXTURES, options.file);
    assert.ok(fixtureName && fixtureName !== ".." && !fixtureName.startsWith(`..${path.sep}`) && !path.isAbsolute(fixtureName),
      `Fixture must be inside ${FIXTURES}: ${options.file}`);
    assert.ok(expectations[fixtureName], `No scope expectations for fixture: ${fixtureName}`);
    fixtureExpectations = [[fixtureName, expectations[fixtureName]]];
  }
  let passed = 0;
  const failures = [];

  for (const [fixtureName, assertions] of fixtureExpectations) {
    const fixturePath = path.join(FIXTURES, fixtureName);
    assert.ok(fs.existsSync(fixturePath), `Missing fixture: ${fixtureName}`);
    const lines = tokenizeFile(grammar, fixturePath);

    for (const check of assertions) {
      const line = lines[check.line - 1];
      assert.ok(line, `${fixtureName}: missing line ${check.line}`);
      const column = locate(line.text, check.token, check.occurrence || 0);
      const actual = scopesAt(line, column);

      if (check.scope) {
        if (hasScope(actual, check.scope)) {
          passed += 1;
        } else {
          failures.push(`${fixtureName}:${check.line} ${JSON.stringify(check.token)} — expected ${check.scope}; got ${actual.join(" ") || "(none)"}`);
        }
      }

      for (const unwanted of check.notScopes || []) {
        if (!hasScope(actual, unwanted)) {
          passed += 1;
        } else {
          failures.push(`${fixtureName}:${check.line} ${JSON.stringify(check.token)} — unexpectedly had ${unwanted}; got ${actual.join(" ")}`);
        }
      }
    }
  }

  if (failures.length) {
    console.error(`${failures.length} assertion(s) failed:\n${failures.map(x => `  ✗ ${x}`).join("\n")}`);
    console.error(`\n${passed} assertion(s) passed.`);
    process.exitCode = 1;
  } else {
    console.log(`Alloy grammar tests: ${passed} scope assertions passed.`);
  }
}

main().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
