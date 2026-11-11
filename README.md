# Alloy Language Support

Syntax highlighting for the Alloy 6 modeling language.

This repository provides editor support for:

- Visual Studio Code
- Sublime Text

The canonical grammar is a TextMate JSON grammar. Editor-specific
files are generated from that source.

## Repository structure

    grammar/
      alloy.tmLanguage.json

    editors/
      vscode/
        package.json
        syntaxes/
          alloy.tmLanguage.json

      sublime/
        Alloy.tmLanguage

    scripts/
      build.py
      build-vscode.py
      build-sublime.py

## Building

Requirements: Python 3.8 or later.

From the repository root, run:

    python scripts/build.py

This generates:

- `editors/vscode/syntaxes/alloy.tmLanguage.json`
- `editors/sublime/Alloy.tmLanguage`

Do not edit these generated files directly. Make changes to
`grammar/alloy.tmLanguage.json` and rebuild.

## Visual Studio Code

Build the grammar first:

    python scripts/build.py

Then package the extension:

    cd editors/vscode
    npx @vscode/vsce package

This produces a `.vsix` file that can be installed in VS Code.

To install it from the command line:

    code --install-extension alloy-language-0.1.0.vsix

## Sublime Text

Build the grammar first:

    python scripts/build.py

To try it locally, copy `editors/sublime/Alloy.tmLanguage` into
your Sublime Text Packages directory.

You can find that directory through:

    Preferences → Browse Packages...

For distribution, the Sublime grammar can be packaged separately
as a Sublime Text package.

## Contributing

Please make grammar changes in:

    grammar/alloy.tmLanguage.json

After changing the grammar, run:

    python scripts/build.py

Check that the generated files are up to date before submitting
a pull request.