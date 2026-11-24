# Alloy syntax highlighting for VS Code

Syntax highlighting for Alloy 6 `.als` files using a TextMate grammar.

## Install

When a VSIX package is available, install it with:

```sh
code --install-extension alloy-language-0.1.0.vsix
```

The extension source is in this repository; Marketplace publication is handled
separately.

## Use

Open an `.als` file. VS Code associates the file with Alloy syntax highlighting
automatically.

## Limitations and source

This provides syntax highlighting, not Alloy Analyzer or semantic language
services. The canonical grammar and known highlighting limitations are in the
[Alloy syntax highlighting repository](https://github.com/nmacedo/alloy-syntax-highlighting)
and its [limitations guide](https://github.com/nmacedo/alloy-syntax-highlighting/blob/main/docs/limitations.md).
