# Alloy syntax highlighting for VS Code

Syntax highlighting for Alloy 6 `.als` files using a TextMate grammar.
Release version: `1.0.0` (`v1.0.0`).

## Install and use

The release repository contains the extension source. Marketplace publication
and a downloadable VSIX are not configured. To run the extension locally,
open the repository in VS Code and start the Extension Development Host with
**Run → Start Debugging**.

The extension associates `.als` files with Alloy syntax highlighting.

## Build, test, and preview

Run these commands from the root of the canonical repository
([alloy-syntax-highlighting](https://github.com/nmacedo/alloy-syntax-highlighting)).

Build or check the extension grammar:

```sh
python3 vscode/build.py
python3 vscode/build.py --check
```

Run the shared scope tests and preview a fixture in the terminal:

```sh
npm test -- --grammar vscode/syntaxes/alloy.tmLanguage.json
npm run preview:textmate -- --grammar vscode/syntaxes/alloy.tmLanguage.json --file tests/fixtures/declarations.als
```

The preview uses the VS Code TextMate grammar without launching VS Code.

## Limitations and source

This extension provides syntax highlighting; it does not include Alloy Analyzer
or semantic language services. The canonical grammar and known highlighting limitations are in the
[Alloy syntax highlighting repository](https://github.com/nmacedo/alloy-syntax-highlighting)
and its [limitations guide](https://github.com/nmacedo/alloy-syntax-highlighting/blob/main/docs/limitations.md).
