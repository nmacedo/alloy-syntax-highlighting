# Alloy syntax highlighting

Syntax highlighting for Alloy 6 across VS Code, Sublime Text, Pygments, and
CodeMirror 6. The canonical, hand-maintained grammar is
[`grammar/alloy.tmLanguage.json`](./grammar/alloy.tmLanguage.json); platform
artifacts are generated from it.

## Targets

| Target | Generated artifact | Guide |
|---|---|---|
| VS Code | `vscode/syntaxes/alloy.tmLanguage.json` | [Overview and installation](./vscode/README.md) |
| Sublime Text | `sublime/Alloy.tmLanguage` | [Overview and installation](./sublime/README.md) |
| Pygments | `pygments/alloy_pygments/lexer.py` | [Install, use, and test](./pygments/README.md) |
| CodeMirror 6 | `codemirror/src/alloy.js` | [Use](./codemirror/README.md) |

Generated artifacts should not be edited by hand. Builders require Python 3.10
or later.

## Contributor quick start

Install the TextMate test dependencies and check that all generated artifacts
match the canonical grammar:

```sh
npm ci
python3 scripts/build.py --check
```

Run the shared scope assertions against the canonical oracle grammar:

```sh
npm test -- --grammar grammar/alloy.tmLanguage.json
```

Run those same scope assertions against the two generated TextMate grammars:

```sh
npm test -- --grammar vscode/syntaxes/alloy.tmLanguage.json
npm test -- --grammar sublime/Alloy.tmLanguage
```

Run the generated Pygments and CodeMirror suites against the shared fixture
expectations:

```sh
python3 -m pip install -e .
python3 -m unittest discover -s pygments/tests -p 'test_pygments.py' -v
npm --prefix codemirror ci
npm --prefix codemirror test
```

These are the validation entry points for all four generated artifacts. The
Pygments and CodeMirror suites adapt the shared TextMate expectations to their
own token models. Their known mismatches are recorded in
[`docs/limitations.md`](./docs/limitations.md).

The shared fixture corpus, scope expectations, target suite commands, and
terminal previews are documented in the [testing guide](./tests/README.md).

## Local previews

Each preview below uses a generated artifact. For the TextMate targets, the
preview prints each distinct lexical scope in its own terminal color and
includes a scope legend.

**VS Code TextMate grammar:**

```sh
npm run preview:textmate -- --grammar vscode/syntaxes/alloy.tmLanguage.json --file tests/fixtures/declarations.als
```

**Sublime Text TextMate grammar:**

```sh
npm run preview:textmate -- --grammar sublime/Alloy.tmLanguage --file tests/fixtures/declarations.als
```

**Pygments lexer:** after `python3 -m pip install -e .`:

```sh
pygmentize -l alloy6 -f terminal256 tests/fixtures/declarations.als
```

**CodeMirror 6:**

```sh
npm run demo:codemirror
```

Then open `http://localhost:8000/codemirror/demo/` and select a fixture. The
target guides and [testing guide](./tests/README.md) have further setup and
inspection details.

## Change workflow

Edit the canonical grammar, rebuild generated targets with
`python3 scripts/build.py`, then run the relevant suites. Platform-specific
build, installation, use, and smoke-test instructions live in each target
guide above. Publishing has not started. The manual GitHub Actions workflow
can prepare candidate payloads and, when explicitly enabled, update the
platform repositories.
