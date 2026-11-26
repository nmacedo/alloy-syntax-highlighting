// Generated from grammar/alloy.tmLanguage.json by codemirror/build.py.
// Ordered scanners follow the grammar's repository groups. Shared streaming
// mechanics (context stack, lookbehind history, and captures) follow below.
import {StreamLanguage} from "@codemirror/language";
import {tags} from "@lezer/highlight";

const NO_MATCH = Symbol("no match");
const RESTART = Symbol("restart after context entry");
function scanNothing() { return NO_MATCH; }

// Grammar-derived scanners. Rule order is significant. Regex flags: `y`
// anchors a match at the current position; `d` supplies capture boundaries.
function scanComments(stream, state) {
  let result;
  if ((result = enterContext(stream, state, {
    id: "rule1",
    begin: /\/\//dy, end: /$/dy,
    scan: scanNothing,
    style: "comment",
  })) !== NO_MATCH) return result;
  if ((result = enterContext(stream, state, {
    id: "rule2",
    begin: /--/dy, end: /$/dy,
    scan: scanNothing,
    style: "comment",
  })) !== NO_MATCH) return result;
  if ((result = enterContext(stream, state, {
    id: "rule3",
    begin: /\/\*\*(?!\/)/dy, end: /\*\//dy,
    scan: scanNothing,
    style: "docComment",
    delimiterStyle: "comment",
  })) !== NO_MATCH) return result;
  if ((result = enterContext(stream, state, {
    id: "rule4",
    begin: /\/\*/dy, end: /\*\//dy,
    scan: scanNothing,
    style: "comment",
  })) !== NO_MATCH) return result;
  return NO_MATCH;
}

function scanMetaString(stream, state) {
  let match;
  if ((match = matchAt(/\\./dy, stream, state)))
    return emitMatch(stream, state, match, "string");
  return NO_MATCH;
}

function scanStrings(stream, state) {
  return enterContext(stream, state, {
    id: "rule5",
    begin: /"/dy, end: /"/dy,
    scan: scanMetaString,
    contentStyle: "string",
    delimiterStyle: "string",
  });
}

function scanDeclarationKeywords(stream, state) {
  let match;
  if ((match = matchAt(/(?:\b(pred|fun)\b)|(?:\b(enum)\b)|(?:\b(module)\b)|(?:\b(run|check)\b)|(?:\b(assert)\b)|(?:\b(fact)\b)/dy, stream, state)))
    return emitMatch(stream, state, match, "keyword");
  return NO_MATCH;
}

function scanTopLevelLetDeclarationsBody(stream, state) {
  let result;
  if ((result = scanComments(stream, state)) !== NO_MATCH) return result;
  if ((result = scanStrings(stream, state)) !== NO_MATCH) return result;
  if ((result = scanTopLevelLetHeader(stream, state)) !== NO_MATCH) return result;
  if ((result = scanTopLevelLetExpressionBody(stream, state)) !== NO_MATCH) return result;
  if ((result = scanTopLevelLetBlockBody(stream, state)) !== NO_MATCH) return result;
  return NO_MATCH;
}

function scanTopLevelLetDeclarations(stream, state) {
  return enterContext(stream, state, {
    id: "rule6",
    begin: /\blet\b/dy, end: /(?<=\})|(?=(?:[ \t]+|\/\*[\s\S]*?\*\/|\/\/[^\r\n]*|--[^\r\n]*)*(?:(?:private|abstract|one|lone|some|var)\b[ \t]+)*(?:module|open|sig|enum|pred|fun|fact|assert|run|check|let)\b)/dy,
    scan: scanTopLevelLetDeclarationsBody,
    beginStyle: "keyword",
  });
}

function scanTopLevelLetHeaderBody(stream, state) {
  let result;
  if ((result = scanComments(stream, state)) !== NO_MATCH) return result;
  if ((result = enterContext(stream, state, {
    id: "rule8",
    begin: /\[/dy, end: /\]/dy,
    scan: scanIdentifierListItems,
    delimiterStyle: "punctuation",
  })) !== NO_MATCH) return result;
  if ((result = scanIdentifiers(stream, state)) !== NO_MATCH) return result;
  return NO_MATCH;
}

function scanTopLevelLetHeader(stream, state) {
  return enterContext(stream, state, {
    id: "rule7",
    begin: /(?=[A-Za-z_])/dy, end: /(?=(?:\s|\/\/[^\r\n]*|--[^\r\n]*|\/\*[\s\S]*?\*\/)*(?:=|\{))/dy,
    scan: scanTopLevelLetHeaderBody,
  });
}

function scanMetaBindingMacro(stream, state) {
  let result;
  if ((result = scanComments(stream, state)) !== NO_MATCH) return result;
  if ((result = scanStrings(stream, state)) !== NO_MATCH) return result;
  if ((result = scanBlockExpressions(stream, state)) !== NO_MATCH) return result;
  return NO_MATCH;
}

function scanTopLevelLetExpressionBody(stream, state) {
  return enterContext(stream, state, {
    id: "rule9",
    begin: /=/dy, end: /(?=(?:[ \t]+|\/\*[\s\S]*?\*\/|\/\/[^\r\n]*|--[^\r\n]*)*(?:(?:private|abstract|one|lone|some|var)\b[ \t]+)*(?:module|open|sig|enum|pred|fun|fact|assert|run|check|let)\b)/dy,
    scan: scanMetaBindingMacro,
    beginStyle: "operator",
  });
}

function scanTopLevelLetBlockBody(stream, state) {
  return enterContext(stream, state, {
    id: "rule10",
    begin: /(?=\{)/dy, end: /(?<=\})/dy,
    scan: scanMetaBindingMacro10,
  });
}

function scanCallableDeclarationsBody(stream, state) {
  let result;
  if ((result = scanComments(stream, state)) !== NO_MATCH) return result;
  if ((result = scanCallableDeclarationParameters(stream, state)) !== NO_MATCH) return result;
  if ((result = scanIdentifiers(stream, state)) !== NO_MATCH) return result;
  return NO_MATCH;
}

function scanCallableDeclarations(stream, state) {
  return enterContext(stream, state, {
    id: "rule11",
    begin: /\b(fun|pred)\b/dy, end: /(?=[:{])/dy,
    scan: scanCallableDeclarationsBody,
    beginStyle: "keyword",
  });
}

function scanCallableDeclarationParametersBody(stream, state) {
  let match, result;
  if ((result = scanComments(stream, state)) !== NO_MATCH) return result;
  if ((result = scanStrings(stream, state)) !== NO_MATCH) return result;
  if ((result = scanCallableParameterValue(stream, state)) !== NO_MATCH) return result;
  if ((match = matchAt(/\b(disj|var)\b(?!\$)/dy, stream, state)))
    return emitMatch(stream, state, match, "keyword");
  if ((match = matchAt(/,/dy, stream, state)))
    return emitMatch(stream, state, match, "punctuation");
  if ((result = scanBlockExpressions(stream, state)) !== NO_MATCH) return result;
  return NO_MATCH;
}

function scanCallableDeclarationParameters(stream, state) {
  return enterContext(stream, state, {
    id: "rule12",
    begin: /\[/dy, end: /\]/dy,
    scan: scanCallableDeclarationParametersBody,
    delimiterStyle: "punctuation",
  });
}

function scanIdentifierListItems(stream, state) {
  let match, result;
  if ((result = scanComments(stream, state)) !== NO_MATCH) return result;
  if ((match = matchAt(/,/dy, stream, state)))
    return emitMatch(stream, state, match, "punctuation");
  if ((result = scanIdentifiers(stream, state)) !== NO_MATCH) return result;
  return NO_MATCH;
}

function scanModulePathArguments(stream, state) {
  return enterContext(stream, state, {
    id: "rule13",
    begin: /\[/dy, end: /\]/dy,
    scan: scanIdentifierListItems,
    delimiterStyle: "punctuation",
  });
}

function scanModulePathComponents(stream, state) {
  let match, result;
  if ((result = scanComments(stream, state)) !== NO_MATCH) return result;
  if ((result = scanModulePathArguments(stream, state)) !== NO_MATCH) return result;
  if ((match = matchAt(/\b[A-Za-z_][A-Za-z0-9_]*\b/dy, stream, state)))
    return emitMatch(stream, state, match, "variableName");
  if ((match = matchAt(/\//dy, stream, state)))
    return emitMatch(stream, state, match, "punctuation");
  return NO_MATCH;
}

function scanMetaPathOpen(stream, state) {
  let match, result;
  if ((result = scanComments(stream, state)) !== NO_MATCH) return result;
  if ((match = matchAt(/\bas\b/dy, stream, state)))
    return emitMatch(stream, state, match, "keyword");
  if ((result = scanModulePathComponents(stream, state)) !== NO_MATCH) return result;
  return NO_MATCH;
}

function scanModuleDeclarationsAndImports(stream, state) {
  let result;
  if ((result = enterContext(stream, state, {
    id: "rule14",
    begin: /\b(module)\b/dy, end: /(?=(?:\s|\/\/[^\r\n]*|--[^\r\n]*|\/\*[\s\S]*?\*\/)*(?:open|sig|enum|pred|fun|fact|assert|run|check|let|private|abstract|one|lone|some|var)\b)/dy,
    scan: scanModulePathComponents,
    beginStyle: "keyword",
  })) !== NO_MATCH) return result;
  if ((result = enterContext(stream, state, {
    id: "rule15",
    begin: /\b(open)\b/dy, end: /(?=(?:\s|\/\/[^\r\n]*|--[^\r\n]*|\/\*[\s\S]*?\*\/)*(?:open|sig|enum|pred|fun|fact|assert|run|check|let|private|abstract|one|lone|some|var)\b)/dy,
    scan: scanMetaPathOpen,
    beginStyle: "keyword",
  })) !== NO_MATCH) return result;
  return NO_MATCH;
}

function scanSignatureDeclarationsBody(stream, state) {
  let match, result;
  if ((match = matchAt(/\b(sig)\b(?!\$)/dy, stream, state)))
    return emitMatch(stream, state, match, "keyword");
  if ((result = scanSignatureHierarchy(stream, state)) !== NO_MATCH) return result;
  if ((result = scanSignatureFields(stream, state)) !== NO_MATCH) return result;
  return NO_MATCH;
}

function scanSignatureDeclarations(stream, state) {
  let match, result;
  if ((match = matchAt(/(?:\b(abstract|private|var)\b(?!\$))|(?:\b(one|lone|some)\b(?=(?:(?:\s+)|\/\*[\s\S]*?\*\/|\/\/[^\r\n]*|--[^\r\n]*|\b(?:abstract|private|var|one|lone|some)\b)*\bsig\b(?!\$)))/dy, stream, state)))
    return emitMatch(stream, state, match, "keyword");
  if ((result = enterContext(stream, state, {
    id: "rule16",
    begin: /(?=\bsig\b(?!\$))/dy, end: /(?<=\})/dy,
    scan: scanSignatureDeclarationsBody,
  })) !== NO_MATCH) return result;
  return NO_MATCH;
}

function scanMetaIdentifiers(stream, state) {
  let match;
  if ((match = matchAt(/(?:\b(sig|field)\$(?![A-Za-z0-9_]))|(?:\b(static|var)\$(?![A-Za-z0-9_]))/dy, stream, state)))
    return emitMatch(stream, state, match, "constant");
  if ((match = matchAt(/\$/dy, stream, state)))
    return emitMatch(stream, state, match, "punctuation");
  return NO_MATCH;
}

function scanKeywords(stream, state) {
  let match;
  if ((match = matchAt(/(?:\b(for|but|exactly|expect|with)\b)|(?:\b(enabled|event|invariant|modifies)\b)/dy, stream, state)))
    return emitMatch(stream, state, match, "keyword");
  if ((match = matchAt(/\b(Int|String|int|seq|steps)\b/dy, stream, state)))
    return emitMatch(stream, state, match, "typeName");
  if ((match = matchAt(/\b(this)\b/dy, stream, state)))
    return emitMatch(stream, state, match, "atom");
  return NO_MATCH;
}

function scanExpressionGroups(stream, state) {
  return enterContext(stream, state, {
    id: "rule17",
    begin: /\(/dy, end: /\)/dy,
    scan: scanBlockExpressions,
    delimiterStyle: "punctuation",
  });
}

function scanMetaBrackets(stream, state) {
  let match, result;
  if ((match = matchAt(/\b(disj)\b(?!\$)/dy, stream, state)))
    return emitMatch(stream, state, match, "keyword");
  if ((result = scanBlockExpressions(stream, state)) !== NO_MATCH) return result;
  return NO_MATCH;
}

function scanExpressionBrackets(stream, state) {
  return enterContext(stream, state, {
    id: "rule18",
    begin: /\[/dy, end: /\]/dy,
    scan: scanMetaBrackets,
    delimiterStyle: "punctuation",
  });
}

function scanExpressionBlocks(stream, state) {
  return enterContext(stream, state, {
    id: "rule19",
    begin: /\{/dy, end: /\}/dy,
    scan: scanBlockExpressions,
    delimiterStyle: "punctuation",
  });
}

function scanBlockExpressionsBody(stream, state) {
  let result;
  if ((result = scanComments(stream, state)) !== NO_MATCH) return result;
  if ((result = scanStrings(stream, state)) !== NO_MATCH) return result;
  return NO_MATCH;
}

function scanMetaBindingLet22Body(stream, state) {
  let result;
  if ((result = scanComments(stream, state)) !== NO_MATCH) return result;
  if ((result = scanStrings(stream, state)) !== NO_MATCH) return result;
  if ((result = scanIdentifiers(stream, state)) !== NO_MATCH) return result;
  return NO_MATCH;
}

function scanMetaBindingLet22(stream, state) {
  let result;
  if ((result = scanComments(stream, state)) !== NO_MATCH) return result;
  if ((result = scanStrings(stream, state)) !== NO_MATCH) return result;
  if ((result = enterContext(stream, state, {
    id: "rule23",
    begin: /,/dy, end: /(=)|(?=\S)(?![A-Za-z_]|\/\*|\/\/|--)/dy,
    scan: scanMetaBindingLet22Body,
    beginStyle: "punctuation",
    endCaptures: {"1": "operator"},
  })) !== NO_MATCH) return result;
  if ((result = scanBlockExpressions(stream, state)) !== NO_MATCH) return result;
  return NO_MATCH;
}

function scanMetaBindingLet(stream, state) {
  let result;
  if ((result = enterContext(stream, state, {
    id: "rule22",
    begin: /=/dy, end: /(?=\|(?!\|)|\{(?!\s*[A-Za-z_][A-Za-z0-9_]*\s*:))/dy,
    scan: scanMetaBindingLet22,
    beginStyle: "operator",
  })) !== NO_MATCH) return result;
  if ((result = scanBlockExpressions(stream, state)) !== NO_MATCH) return result;
  return NO_MATCH;
}

function scanBlockExpressions(stream, state) {
  let match, result;
  if ((result = scanComments(stream, state)) !== NO_MATCH) return result;
  if ((result = scanStrings(stream, state)) !== NO_MATCH) return result;
  if ((result = scanExpressionGroups(stream, state)) !== NO_MATCH) return result;
  if ((result = scanExpressionBrackets(stream, state)) !== NO_MATCH) return result;
  if ((result = scanExpressionBlocks(stream, state)) !== NO_MATCH) return result;
  if ((result = enterContext(stream, state, {
    id: "rule20",
    begin: /(:)(?!>)|(->)/dy, end: /((?:one|lone|some|set)\b)|(?=\S)(?!\/\*|\/\/|--)/dy,
    scan: scanBlockExpressionsBody,
    beginCaptures: {"1": "punctuation", "2": "operator"},
    endCaptures: {"1": "keyword"},
  })) !== NO_MATCH) return result;
  if ((match = matchAt(/(?:(?<=:\s*)(one|lone|some|set)\b)|(?:(?<=->\s*)(one|lone|some|set)\b)/dy, stream, state)))
    return emitMatch(stream, state, match, "keyword");
  if ((result = scanPunctuation(stream, state)) !== NO_MATCH) return result;
  if ((match = matchAt(/(?:\b(disj|var)\b(?!\$))|(?:\b(one|lone|some|set)\b(?=(?:(?:\s+)|\/\*[\s\S]*?\*\/|\/\/[^\r\n]*|--[^\r\n]*)*->))/dy, stream, state)))
    return emitMatch(stream, state, match, "keyword");
  if ((match = matchAt(/(?:\b(and|or|not|implies|iff|else)\b)|(?:\b(all|no|one|some|lone)\b)|(?:\b(always|eventually|after|before|until|releases|since|triggered|historically|once)\b)/dy, stream, state)))
    return emitMatch(stream, state, match, "operator");
  if ((result = enterContext(stream, state, {
    id: "rule21",
    begin: /\blet\b/dy, end: /(?=\|(?!\|)|\{(?!\s*[A-Za-z_][A-Za-z0-9_]*\s*:))/dy,
    scan: scanMetaBindingLet,
    beginStyle: "operator",
  })) !== NO_MATCH) return result;
  if ((match = matchAt(/(?:\b(in)\b)|(?:\b(sum|int)\b)/dy, stream, state)))
    return emitMatch(stream, state, match, "operator");
  if ((match = matchAt(/\b(seq)\b/dy, stream, state)))
    return emitMatch(stream, state, match, "keyword");
  if ((match = matchAt(/(?:<=>|=>|!|&&|\|\||;)|(?:>>>|>>|<<)|(?:\+\+|->|<:|:>|\+|-|&|\*|\^|~|\.|#|')|(?:=<|>=|=|<|>)/dy, stream, state)))
    return emitMatch(stream, state, match, "operator");
  if ((result = scanMetaIdentifiers(stream, state)) !== NO_MATCH) return result;
  if ((result = scanKeywords(stream, state)) !== NO_MATCH) return result;
  if ((result = scanConstants(stream, state)) !== NO_MATCH) return result;
  if ((result = scanIdentifiers(stream, state)) !== NO_MATCH) return result;
  return NO_MATCH;
}

function scanPunctuation(stream, state) {
  let match;
  if ((match = matchAt(/(?:\.\.)|(?:,|:(?!>)|(?<!\|)\|(?!\|))|(?:@)/dy, stream, state)))
    return emitMatch(stream, state, match, "punctuation");
  return NO_MATCH;
}

function scanConstants(stream, state) {
  let match;
  if ((match = matchAt(/(?:\b0x(?:_|[0-9A-Fa-f]{2})+\b)|(?:\b0b[01_]+\b)|(?:\b[0-9][0-9_]*\b)/dy, stream, state)))
    return emitMatch(stream, state, match, "number");
  if ((match = matchAt(/\b(univ|iden|none)\b/dy, stream, state)))
    return emitMatch(stream, state, match, "atom");
  return NO_MATCH;
}

function scanIdentifiers(stream, state) {
  let match;
  if ((match = matchAt(/\b[A-Za-z_][A-Za-z0-9_]*\b/dy, stream, state)))
    return emitMatch(stream, state, match, "variableName");
  return NO_MATCH;
}

function scanMetaSignatureHierarchy(stream, state) {
  let match, result;
  if ((result = scanComments(stream, state)) !== NO_MATCH) return result;
  if ((result = scanStrings(stream, state)) !== NO_MATCH) return result;
  if ((result = scanMetaIdentifiers(stream, state)) !== NO_MATCH) return result;
  if ((match = matchAt(/\b(extends|in)\b/dy, stream, state)))
    return emitMatch(stream, state, match, "keyword");
  if ((match = matchAt(/(?:\+)|(?:=)/dy, stream, state)))
    return emitMatch(stream, state, match, "operator");
  if ((result = scanKeywords(stream, state)) !== NO_MATCH) return result;
  if ((result = scanConstants(stream, state)) !== NO_MATCH) return result;
  if ((result = scanIdentifiers(stream, state)) !== NO_MATCH) return result;
  if ((result = scanPunctuation(stream, state)) !== NO_MATCH) return result;
  return NO_MATCH;
}

function scanSignatureHierarchy(stream, state) {
  return enterContext(stream, state, {
    id: "rule24",
    begin: /(?<=sig\s*)/dy, end: /(?=\{)/dy,
    scan: scanMetaSignatureHierarchy,
  });
}

function scanMetaBlockSignatureFields(stream, state) {
  let match, result;
  if ((result = scanComments(stream, state)) !== NO_MATCH) return result;
  if ((result = scanStrings(stream, state)) !== NO_MATCH) return result;
  if ((match = matchAt(/\b(private|var|disj)\b(?!\$)/dy, stream, state)))
    return emitMatch(stream, state, match, "keyword");
  if ((result = scanFieldDeclarationValue(stream, state)) !== NO_MATCH) return result;
  if ((result = scanBlockExpressions(stream, state)) !== NO_MATCH) return result;
  return NO_MATCH;
}

function scanSignatureFields(stream, state) {
  return enterContext(stream, state, {
    id: "rule25",
    begin: /\{/dy, end: /\}/dy,
    scan: scanMetaBlockSignatureFields,
    delimiterStyle: "punctuation",
  });
}

function scanFieldDeclarationValue(stream, state) {
  return enterContext(stream, state, {
    id: "rule26",
    begin: /(?=:(?!>))|(=)/dy, end: /(?=,|\})/dy,
    scan: scanBlockExpressions,
    beginCaptures: {"1": "operator"},
  });
}

function scanCallableParameterValue(stream, state) {
  return enterContext(stream, state, {
    id: "rule27",
    begin: /(?=:(?!>))|(=)/dy, end: /(?=,|\])/dy,
    scan: scanBlockExpressions,
    beginCaptures: {"1": "operator"},
  });
}

function scanRoot(stream, state) {
  let result;
  if ((result = scanComments(stream, state)) !== NO_MATCH) return result;
  if ((result = scanStrings(stream, state)) !== NO_MATCH) return result;
  if ((result = scanModuleDeclarationsAndImports(stream, state)) !== NO_MATCH) return result;
  if ((result = scanSignatureDeclarations(stream, state)) !== NO_MATCH) return result;
  if ((result = scanCallableDeclarations(stream, state)) !== NO_MATCH) return result;
  if ((result = scanTopLevelLetDeclarations(stream, state)) !== NO_MATCH) return result;
  if ((result = scanDeclarationKeywords(stream, state)) !== NO_MATCH) return result;
  if ((result = scanMetaIdentifiers(stream, state)) !== NO_MATCH) return result;
  if ((result = scanKeywords(stream, state)) !== NO_MATCH) return result;
  if ((result = scanBlockExpressions(stream, state)) !== NO_MATCH) return result;
  if ((result = scanExpressionBrackets(stream, state)) !== NO_MATCH) return result;
  if ((result = scanExpressionBlocks(stream, state)) !== NO_MATCH) return result;
  if ((result = scanPunctuation(stream, state)) !== NO_MATCH) return result;
  if ((result = scanConstants(stream, state)) !== NO_MATCH) return result;
  if ((result = scanIdentifiers(stream, state)) !== NO_MATCH) return result;
  return NO_MATCH;
}

const scanMetaBindingMacro10 = scanMetaBindingMacro;

// Streaming support. A frame stores its ending pattern and body scanner.
// NO_MATCH tries the next rule; RESTART rescans after a zero-width begin.
function startState() {
  return {
    contexts: [], pending: [], delimiterDepth: 0, history: "",
    zeroRule: null, zeroPosition: -1,
  };
}

function copyState(state) {
  // Frames and pending pieces are immutable; only the arrays need copying.
  return {...state, contexts: state.contexts.slice(), pending: state.pending.slice()};
}

function matchAt(expression, stream, state) {
  // Reset lastIndex on every call, including regexes shared by copied frames.
  // Recent text supplies lookbehind context across CodeMirror's line streams.
  if (!expression.source.includes("(?<=")) {
    expression.lastIndex = stream.pos;
    return expression.exec(stream.string);
  }
  const prefix = state.history;
  expression.lastIndex = prefix.length;
  const match = expression.exec(prefix + stream.string.slice(stream.pos));
  if (!match) return null;
  match.index = 0;
  match.indices = match.indices.map(span => span && [span[0] - prefix.length, span[1] - prefix.length]);
  return match;
}

function enterContext(stream, state, rule) {
  // A zero-width begin may be retried after its context ends without consuming
  // text. Suppress that one rule until the stream makes progress.
  if (state.zeroRule === rule.id && state.zeroPosition === stream.pos) return NO_MATCH;
  const match = matchAt(rule.begin, stream, state);
  if (!match) return NO_MATCH;
  if (!match[0].length) {
    state.zeroRule = rule.id;
    state.zeroPosition = stream.pos;
  }
  state.contexts.push({...rule, openingStream: stream, openingPosition: stream.pos});
  const style = rule.beginStyle ?? rule.delimiterStyle ?? rule.style ?? null;
  return match[0].length
    ? emitMatch(stream, state, match, style, rule.beginCaptures)
    : RESTART;
}

function emitMatch(stream, state, match, style = null, captures = null) {
  // Most rules style the entire match. Only mixed captures need a queue:
  // StreamLanguage can return just one style from each token() call.
  if (!captures) return consume(stream, state, match[0], style);
  const text = match[0];
  const ranges = [];
  const boundaries = new Set([0, text.length]);
  for (const [index, tag] of Object.entries(captures)) {
    const span = match.indices[Number(index)];
    if (!span) continue;
    const from = span[0] - match.index;
    const to = span[1] - match.index;
    ranges.push({from, to, tag});
    boundaries.add(from);
    boundaries.add(to);
  }
  const points = [...boundaries].sort((a, b) => a - b);
  for (let i = 0; i < points.length - 1; i++) {
    const from = points[i], to = points[i + 1];
    let tag = style;
    for (const range of ranges) {
      if (range.from <= from && range.to >= to) tag = range.tag;
    }
    state.pending.push({tag, text: text.slice(from, to)});
  }
  return state.pending.length ? emitPending(stream, state) : null;
}

function emitPending(stream, state) {
  const part = state.pending.shift();
  return consume(stream, state, part.text, part.tag);
}

function consume(stream, state, text, style) {
  stream.pos += text.length;
  state.history = (state.history + text).replace(/\s+/g, " ").slice(-64);
  state.zeroRule = null;
  state.zeroPosition = -1;
  if (style === "punctuation") {
    if (/^[([{]$/.test(text)) state.delimiterDepth++;
    else if (/^[)\]}]$/.test(text)) state.delimiterDepth = Math.max(0, state.delimiterDepth - 1);
  }
  return style;
}

function token(stream, state) {
  if (state.pending.length) return emitPending(stream, state);
  // Line comments must also end when CodeMirror skips a blank line.
  while (state.contexts.length && state.contexts.at(-1).end.source === "$" && stream !== state.contexts.at(-1).openingStream) {
    state.contexts.pop();
  }
  const spaceContext = state.contexts.at(-1);
  if (stream.eatSpace()) {
    state.history = (state.history + stream.current()).replace(/\s+/g, " ").slice(-64);
    return spaceContext?.contentStyle || spaceContext?.style || null;
  }

  while (state.contexts.length && state.contexts.at(-1).end.source === "(?<=\\})"
         && (stream !== state.contexts.at(-1).openingStream || stream.pos !== state.contexts.at(-1).openingPosition)
         && state.history.trimEnd().endsWith("}")) {
    state.contexts.pop();
  }
  const context = state.contexts.at(-1);
  if (context && (stream !== context.openingStream || stream.pos !== context.openingPosition)) {
    const ending = matchAt(context.end, stream, state);
    if (ending) {
      state.contexts.pop();
      if (ending[0].length) {
        const style = context.endStyle ?? context.delimiterStyle ?? context.style ?? null;
        return emitMatch(stream, state, ending, style, context.endCaptures);
      }
      return token(stream, state);
    }
  }

  const result = context ? context.scan(stream, state) : scanRoot(stream, state);
  if (result === RESTART) return token(stream, state);
  if (result !== NO_MATCH) return result;

  if (stream.eol()) return null;
  stream.next();
  state.history = (state.history + stream.current()).replace(/\s+/g, " ").slice(-64);
  return context?.contentStyle || context?.style || null;
}

function indent(state, textAfter, context) {
  const closes = /^[})\]]/.test(textAfter);
  return Math.max(0, state.delimiterDepth - (closes ? 1 : 0)) * context.unit;
}

const tokenTable = {
  comment: tags.comment,
  docComment: tags.docComment,
  string: tags.string,
  number: tags.number,
  constant: tags.constant(tags.variableName),
  typeName: tags.typeName,
  atom: tags.atom,
  variableName: tags.variableName,
  punctuation: tags.punctuation,
  operator: tags.operator,
  keyword: tags.keyword,
};

export const alloy = StreamLanguage.define({
  name: "alloy",
  startState,
  copyState,
  token,
  indent,
  languageData: {commentTokens: {line: "//", block: {open: "/*", close: "*/"}}},
  tokenTable,
});

export default alloy;
