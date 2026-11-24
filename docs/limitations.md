# Known highlighting and translation limits

This page records limitations demonstrated by the current fixtures and
generated-artifact suites. It does not attempt to list every Alloy construct
that a regex-based highlighter might handle imperfectly. 

The suite keeps the expected scopes as the desired results. The current,
narrowly scoped mismatches are recorded in
[`known-failures.json`](../tests/expected/known-failures.json): runners report
them as `XFAIL`, fail on unlisted mismatches, and fail with `XPASS` when a known
case starts passing so its entry can be removed.

## Canonical TextMate grammar

### Top-level `let` macro bodies

Brace-bodied top-level macros end at their closing `}`. Within that body,
`let` is treated as an expression operator, including nested let-expressions.
The fixture [`declarations.als`](../tests/fixtures/declarations.als) checks
those nested scopes and checks that a following declaration resumes normally.

Expression-bodied macros introduced with `=` have no delimiter that reliably
marks the end of the right-hand side. The grammar ends the macro scope when it
encounters a declaration keyword, including on the same line and after
whitespace or comments. This recognizes adjacent declarations such as `pred`
and another top-level `let`, but it is intentionally conservative: a
let-expression inside an `=` macro RHS can look like a new top-level macro and
end the scope prematurely. The `mcr5`, `mcr6`, and `mcr7` cases in
[`declarations.als`](../tests/fixtures/declarations.als) retain the expected
expression scopes in the expected file, but the oracle currently scopes four
inner `let` tokens as top-level declarations instead. This produces eight
failed oracle assertions because both the operator and enclosing let-expression
scope are checked at each token.

### Multiplicity before an arrow after a line comment

A multiplicity immediately before `->` is not recognized when the arrow
crosses a line boundary. TextMate tokenizes one line at a time, so a lookahead cannot inspect
the later arrow. The token currently receives the ordinary multiplicity-word
operator scope instead of `storage.modifier.alloy`. The neighboring cases
verify that comments before a multiplicity and comments after an arrow are
handled.

### Full module paths across lines

The grammar cannot reliably scope an entire module path when it spans lines.
Alloy ignores newlines, and module paths have no explicit terminator, so a
TextMate pattern cannot always determine where the path ends without risking
scope bleed into a following declaration. 

## Pygments translation

Pygments uses a flat token stream, so TextMate context scopes such as `meta.*`
do not have direct Pygments token equivalents. The adapter checks representable
token categories against the shared fixture expectations. For example,
`some` in [`formulas.als`](../tests/fixtures/formulas.als) has both
`keyword.operator.word.alloy` and the enclosing `meta.block.alloy` scope; the
latter is intentionally skipped by the Pygments adapter.

The remaining four Pygments mismatches are the inner `let` tokens described
above: Pygments and the TextMate oracle both emit declaration-keyword scopes,
contrary to the expected operator scopes. They are existing oracle failures,
not Pygments-specific divergences. Import aliases in
[`modules.als`](../tests/fixtures/modules.als) are mapped to
`Keyword.Namespace` and pass their expected-category checks.

The `one` case before a line comment in [`formulas.als`](../tests/fixtures/formulas.als)
does not fail Pygments: its lexer emits `Keyword.Reserved`, matching the
expected modifier category. The TextMate oracle emits the word-operator scope
there, so this behavior differs between the canonical grammar and the Pygments
lexer.

## CodeMirror translation

CodeMirror uses a streaming `StreamLanguage` highlighter rather than an Alloy
parser. It provides token styles and delimiter-based indentation, but no Alloy
syntax tree for structural navigation or semantic analysis. Its standard
highlight tags flatten TextMate scopes: nested `meta.*` scopes are not exposed,
and punctuation subscopes share the same visual tag. The fixture tests can
therefore check mapped styles, but cannot distinguish every TextMate scope.

Identifiers use the variable style unless the TextMate grammar gives them a
more specific role. Function-like integer names are deliberately not styled as
functions because Alloy declarations can shadow them.

The shared fixtures retain the same known `let` and `one` exceptions as the
TextMate oracle. In CodeMirror's mapped-style test output, these appear as four
operator-style mismatches for nested `let` expressions inside expression-bodied
top-level macros, plus two diagnostics for the single `one` multiplicity before
an arrow on the next line. TextMate also reports four enclosing `meta.binding`
scope mismatches for those `let` tokens; CodeMirror cannot represent or test
those scopes. The duplicate `one` diagnostics come from its expected-style and
forbidden-style assertions for the same token.

## TextMate artifact validation boundary

The VS Code artifact is a direct JSON copy of the canonical grammar. The
Sublime artifact serializes the same grammar as an XML property list. Both are
tokenized by the repository's `vscode-textmate` test harness; this validates
their data and shared scopes, but does not execute Sublime Text's native
grammar runtime.

