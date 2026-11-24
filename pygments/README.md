# Alloy syntax highlighting for Pygments

A Pygments lexer for Alloy 6 source files.
Release version: `1.0.0` (`v1.0.0`).

## Install

```sh
python -m pip install git+https://github.com/nmacedo/alloy-pygments-highlighting.git@v1.0.0
```

## Use

```sh
pygmentize -l alloy6 -f terminal256 model.als
```

## Build, test, and preview

Run these commands from the root of the canonical repository
([alloy-syntax-highlighting](https://github.com/nmacedo/alloy-syntax-highlighting)).

Build or check the Pygments lexer, install the local package, and run its shared
fixture tests:

```sh
python3 pygments/build.py
python3 pygments/build.py --check
python3 -m pip install -e .
python3 -m unittest discover -s pygments/tests -p 'test_pygments.py' -v
```

Preview a fixture with Pygments in the terminal:

```sh
pygmentize -l alloy6 -f terminal256 tests/fixtures/declarations.als
```

## Limitations and source

This lexer provides syntax highlighting; it does not include Alloy Analyzer
or semantic language services. The canonical grammar and known highlighting limitations are in the
[Alloy syntax highlighting repository](https://github.com/nmacedo/alloy-syntax-highlighting)
and its [limitations guide](https://github.com/nmacedo/alloy-syntax-highlighting/blob/main/docs/limitations.md).
