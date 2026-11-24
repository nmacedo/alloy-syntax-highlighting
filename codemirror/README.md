# Alloy syntax highlighting for CodeMirror 6

CodeMirror 6 `StreamLanguage` support for Alloy 6.

## Install

```sh
npm install github:nmacedo/alloy-codemirror-highlighting
```

This installs from the platform repository. npm registry publication is
handled separately.

## Use

```js
import {alloy} from "alloy-codemirror";

const extensions = [alloy];
```

Add `alloy` to your editor's extensions. It provides syntax-aware token styles
and delimiter-based indentation.

## Limitations and source

This is a streaming highlighter, not an Alloy parser, and does not provide
semantic language services. The canonical grammar and known highlighting
limitations are in the
[Alloy syntax highlighting repository](https://github.com/nmacedo/alloy-syntax-highlighting)
and its [limitations guide](https://github.com/nmacedo/alloy-syntax-highlighting/blob/main/docs/limitations.md).
