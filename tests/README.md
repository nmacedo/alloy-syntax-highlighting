# Shared fixtures and validation

## Running the TextMate oracle

Run the scope assertions against the canonical TextMate grammar, which is the
scope oracle:

```sh
npm test -- --grammar grammar/alloy.tmLanguage.json
```

Then run the same assertions against each generated TextMate artifact:

```sh
npm test -- --grammar vscode/syntaxes/alloy.tmLanguage.json
npm test -- --grammar sublime/Alloy.tmLanguage
```

To run one fixture while updating or reviewing its expectations, pass its path
with `--file`:

```sh
npm test -- --grammar grammar/alloy.tmLanguage.json --file tests/fixtures/comments.als
```

For a terminal preview of a fixture using either generated grammar, run:

```sh
npm run preview:textmate -- --grammar vscode/syntaxes/alloy.tmLanguage.json --file tests/fixtures/modules.als
npm run preview:textmate -- --grammar sublime/Alloy.tmLanguage --file tests/fixtures/modules.als
```

The preview gives each distinct lexical scope in the selected fixture its own
ANSI color and prints a color-to-scope legend when stdout is a terminal. Use
the scope-inspection commands below to see complete nested scope stacks.

The Sublime `.tmLanguage` plist is decoded before tokenizing. To inspect the
token scope stack for an individual fixture from either artifact:

```sh
npm run inspect:textmate -- --grammar vscode/syntaxes/alloy.tmLanguage.json --file tests/fixtures/modules.als
npm run inspect:textmate -- --grammar sublime/Alloy.tmLanguage --file tests/fixtures/modules.als
```

These commands use `vscode-textmate` and Oniguruma locally. They test the
generated TextMate grammar data without launching an editor; they do not invoke
Sublime's own grammar runtime.

The fixture corpus is organized around eight files:

- `modules.als`: module and import paths, aliases, path comments and line breaks.
- `signatures.als`: signature hierarchies, fields, modifiers, multiplicities,
  `seq` field types, and enums.
- `declarations.als`: facts, predicates, functions, parameters, return types,
  empty declarations, assertions, and top-level `let` macros.
- `commands.als`: `run` and `check` forms, scopes, expectations, and multiline
  command syntax.
- `formulas.als`: quantified formulas, multiplicity roles, comprehensions,
  relational and propositional operators, ternaries, and temporal operators.
- `literals.als`: decimal, hexadecimal, and binary forms, plus strings and
  escapes.
- `comments.als`: line, block, documentation, and comments inside constructs.
- `meta.als`: Alloy meta-identifiers, integer operations, and field access.

Formulas and expressions remain together because Alloy comprehensions embed
formulas inside expressions, and their shared context is part of what the
fixture exercises. The previous edge-case fixture files have been merged into
these feature-oriented files; empty declarations are covered in
`declarations.als`.

The `seq` type-constructor form is in `signatures.als`; the `seq` command-scope
form is in `commands.als`. Their scopes intentionally differ:
`storage.modifier.alloy` for the declaration modifier and `support.type.alloy`
for the built-in command scope name. The expected scopes are recorded in
[`expected/scopes.json`](./expected/scopes.json).

Each fixture has entries in `expected/scopes.json`. The CodeMirror demo offers
the same eight fixtures in its picker.

Known generated-artifact differences are listed in
[`docs/limitations.md`](../docs/limitations.md).

## Feature coverage map

| Alloy construct | Fixture(s) |
|---|---|
| Modules, `open`, aliases, qualified paths, path comments and line breaks | `modules.als` |
| Signatures, hierarchy, fields, modifiers, multiplicities, `seq` field types, enums | `signatures.als` |
| Facts, predicates, functions, parameters, return types, empty declarations, top-level `let` macros | `declarations.als` |
| `run`/`check`, scopes, expectations, multiline commands | `commands.als` |
| Quantifiers, comprehensions, `let` expressions, ternary formulas | `formulas.als` |
| Relational operators, arrows, closures, built-in types and functions | `formulas.als` |
| Temporal operators and nested temporal formulas | `formulas.als` |
| Decimal, hexadecimal and binary numbers; string literals and escapes | `literals.als` |
| Line, block and documentation comments, including comments inside constructs | `comments.als`, `modules.als`, `declarations.als` |
| Meta-identifiers and field access | `meta.als` |

These are tokenizer fixtures, not Analyzer-validated models. Some use
undeclared names or combine constructs to exercise highlighting boundaries.

The most important distinction tested is the role of `one`, `lone`, and `some`:
- signature modifiers;
- field multiplicities;
- multiplicities on quantified-variable declarations;
- quantifier operators;
- multiplicity checks.

The original declaration cases, supplied declaration updates, macros, and
conditional-expression examples are kept together in `declarations.als`.


