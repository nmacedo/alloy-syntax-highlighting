# Known highlighting and translation limits

The shared scope expectations describe the desired highlighting.
[`known-failures.json`](../tests/expected/known-failures.json) records exact
mismatches: runners report `XFAIL`, reject unlisted failures, and report `XPASS`
when an entry starts passing and needs removal.

## Canonical TextMate grammar

### Top-level `let` macros

Brace-bodied macros handle nested let-expressions. Expression-bodied macros
(`let m = ...`) have no reliable end delimiter: the grammar ends their context
at a declaration keyword, which can mistake an inner `let` for another macro.
[`declarations.als`](../tests/fixtures/declarations.als) demonstrates both forms.

### Multiplicities across lines

A `one`/`lone`/`some` modifier is scoped as an operator when the following `sig`
or arrow appears on a later line. [TextMate matches one line at a time](https://macromates.com/manual/en/language_grammars#language_rules),
so lookahead cannot inspect the later token. Assuming a modifier at a line
boundary would misclassify multiplicity tests.
See [`signatures.als`](../tests/fixtures/signatures.als) and
[`formulas.als`](../tests/fixtures/formulas.als).

Multiplicities after a field or parameter's `:` are handled across comments
and line breaks; those cases are not expected failures.

### Comprehensions in let bindings

A newline or comment between a comprehension's `{` and its first declaration
can prematurely end the enclosing let-binding context. A subsequent binding's
`=` receives a comparison scope instead of assignment and loses its binding
scope. The `boundaryLetComprehensions` cases in
[`formulas.als`](../tests/fixtures/formulas.als) demonstrate this gap.

### Full module paths across lines

An entire module path cannot be scoped reliably when it spans lines: paths
have no explicit terminator, and lookahead cannot inspect a later line.

## Pygments

Pygments exposes flat token categories, so enclosing `meta.*` scopes are
omitted and some distinct TextMate scopes map to the same category.

The nested macro `let` failures remain. Split signature modifiers and
multiplicities before arrows on later lines pass because Pygments regexes can
inspect the whole input. The comprehension binding checks also pass, but
assignment and comparison both map to `Operator`; those checks cannot establish
that the original contexts are preserved.

## CodeMirror

The `StreamLanguage` highlighter provides token styles and delimiter-based
indentation, without an Alloy syntax tree. Its flat tags omit enclosing
`meta.*` scopes and merge punctuation categories.

Nested macro `let`, split signature modifier, and arrow lookahead failures
remain. Assignment and comparison share the operator style, so mapped checks
cannot expose the comprehension binding issue. Multiplicity failures have two
assertions per token: the expected modifier and the forbidden operator style.

## TextMate artifact validation

The VS Code artifact copies the canonical JSON grammar; Sublime serializes it
as an XML property list. Both use the repository's `vscode-textmate` harness
for validation. These tests do not execute Sublime Text's native runtime.
