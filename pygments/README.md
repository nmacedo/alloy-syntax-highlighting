# Alloy syntax highlighting for Pygments

A Pygments lexer for Alloy 6 source files.

## Install

```sh
python -m pip install git+https://github.com/nmacedo/alloy-pygments-highlighting.git
```

## Use

```sh
pygmentize -l alloy6 -f terminal256 model.als
```

## Limitations and source

This provides syntax highlighting, not Alloy Analyzer or semantic language
services. The canonical grammar and known highlighting limitations are in the
[Alloy syntax highlighting repository](https://github.com/nmacedo/alloy-syntax-highlighting)
and its [limitations guide](https://github.com/nmacedo/alloy-syntax-highlighting/blob/main/docs/limitations.md).
