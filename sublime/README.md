# Alloy syntax highlighting for Sublime Text

Syntax highlighting for Alloy 6 `.als` files using a TextMate grammar.
Release version: `1.1.0` (`v1.1.0`).

## Install

Place `Alloy.tmLanguage` in a Sublime Text package directory. In Sublime Text,
open **Preferences → Browse Packages**, create an `Alloy` directory, and copy
the grammar file there.

## Use

Open an `.als` file and select **View → Syntax → Alloy**.

## Build, test, and preview

Run these commands from the root of the canonical repository
([alloy-syntax-highlighting](https://github.com/nmacedo/alloy-syntax-highlighting)).

Build or check the Sublime grammar:

```sh
python3 sublime/build.py
python3 sublime/build.py --check
```

Run the shared scope tests and preview a fixture in the terminal:

```sh
npm test -- --grammar sublime/Alloy.tmLanguage
npm run preview:textmate -- --grammar sublime/Alloy.tmLanguage --file tests/fixtures/declarations.als
```

The preview uses the Sublime Text grammar without launching Sublime Text.

## Limitations and source

This package provides syntax highlighting; it does not include Alloy Analyzer
or semantic language services. The canonical grammar and known highlighting limitations are in the
[Alloy syntax highlighting repository](https://github.com/nmacedo/alloy-syntax-highlighting)
and its [limitations guide](https://github.com/nmacedo/alloy-syntax-highlighting/blob/main/docs/limitations.md).
