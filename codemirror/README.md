# Alloy syntax highlighting for CodeMirror 6

CodeMirror 6 `StreamLanguage` support for Alloy 6.
Release version: `1.0.0` (`v1.0.0`).

## Install

```sh
npm install github:nmacedo/alloy-codemirror-highlighting#v1.0.0
```

This installs the tagged source from the platform repository. npm registry
publication uses a separate process.

## Use

```js
import {alloy} from "alloy-codemirror";

const extensions = [alloy];
```

Add `alloy` to your editor's extensions. It provides syntax-aware token styles
and delimiter-based indentation.

## Build, test, and demo

Run these commands from the root of the canonical repository
([alloy-syntax-highlighting](https://github.com/nmacedo/alloy-syntax-highlighting)).

Build or check the CodeMirror language module, install its development
dependencies, and run the fixture tests:

```sh
python3 codemirror/build.py
python3 codemirror/build.py --check
npm --prefix codemirror ci
npm --prefix codemirror test
```

Start the browser demo:

```sh
npm run demo:codemirror
```

Open `http://localhost:8000/codemirror/demo/` and select a fixture.

## Limitations and source

This is a streaming highlighter, not an Alloy parser; it does not provide
semantic language services. The canonical grammar and known highlighting
limitations are in the
[Alloy syntax highlighting repository](https://github.com/nmacedo/alloy-syntax-highlighting)
and its [limitations guide](https://github.com/nmacedo/alloy-syntax-highlighting/blob/main/docs/limitations.md).
