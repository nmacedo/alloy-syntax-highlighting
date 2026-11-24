"""Generated Pygments lexer for Alloy. Do not edit by hand.
Regenerate with: python pygments/build.py
Source: grammar/alloy.tmLanguage.json
"""
import re
from pygments.lexer import RegexLexer, include
from pygments.token import Comment, Keyword, Name, Number, Operator, Punctuation, String, Text

def _capture_groups(base, overrides):
    """Apply this grammar's ordered captures, using base for gaps."""
    def callback(lexer, match, ctx=None):
        cursor = match.start()
        for group, token in sorted(overrides.items()):
            start, end = match.span(group)
            if start < 0 or end <= start:
                continue
            if start < cursor:
                raise ValueError("Overlapping captures are not supported")
            if start > cursor:
                yield cursor, base, match.string[cursor:start]
            yield start, token, match.string[start:end]
            cursor = end
        if cursor < match.end():
            yield cursor, base, match.string[cursor:match.end()]
        if ctx is not None:
            ctx.pos = match.end()
    return callback


class AlloyLexer(RegexLexer):
    """Alloy 6 lexer compiled from the canonical TextMate grammar."""
    name = "Alloy"
    aliases = ["alloy6"]
    filenames = ["*.als"]
    mimetypes = ["text/x-alloy"]
    flags = re.MULTILINE
    tokens = {
        'root': [
            include('repo_comments'),
            include('repo_strings'),
            include('repo_module_declarations_and_imports'),
            include('repo_signature_declarations'),
            include('repo_callable_declaration_parameters'),
            include('repo_top_level_let_declarations'),
            include('repo_declaration_keywords'),
            include('repo_meta_identifiers'),
            include('repo_keywords'),
            include('repo_block_expressions'),
            include('repo_expression_brackets'),
            include('repo_expression_blocks'),
            include('repo_punctuation'),
            include('repo_constants'),
            include('repo_identifiers'),
            (r'(?s:.)', Text),
        ],
        'repo_comments': [
            ('//', Comment.Single, 'context_comment_line_double_slash'),
            ('--', Comment.Single, 'context_comment_line_double_dash'),
            ('/\\*\\*(?!/)', Comment.Multiline, 'context_comment_block_documentation'),
            ('/\\*', Comment.Multiline, 'context_comment_block'),
        ],
        'context_comment_line_double_slash': [
            ('$', Comment.Single, '#pop'),
            (r'[^\r\n]+', Comment.Single),
        ],
        'context_comment_line_double_dash': [
            ('$', Comment.Single, '#pop'),
            (r'[^\r\n]+', Comment.Single),
        ],
        'context_comment_block_documentation': [
            ('\\*/', Comment.Multiline, '#pop'),
            (r'[^*]+', Comment.Multiline),
            (r'\*(?!/)', Comment.Multiline),
        ],
        'context_comment_block': [
            ('\\*/', Comment.Multiline, '#pop'),
            (r'[^*]+', Comment.Multiline),
            (r'\*(?!/)', Comment.Multiline),
        ],
        'repo_strings': [
            ('"', String.Delimiter, 'body_repo_strings'),
        ],
        'body_repo_strings': [
            ('"', String.Delimiter, '#pop'),
            ('\\\\.', String.Escape),
            (r'[^"\\]+', String.Double),
        ],
        'repo_module_declarations_and_imports': [
            ('\\b(module)\\b', Keyword.Namespace, 'context_path_module'),
            ('\\b(open)\\b', Keyword.Namespace, 'context_path_open'),
        ],
        'context_path_module': [
            ('(?=(?:\\s|//[^\\r\\n]*|--[^\\r\\n]*|/\\*[\\s\\S]*?\\*/)*(?:open|sig|enum|pred|fun|fact|assert|run|check|let|private|abstract|one|lone|some|var)\\b)', Text, '#pop'),
            include('repo_module_path_components'),
            (r'(?s:.)', Text),
        ],
        'repo_module_path_components': [
            include('repo_comments'),
            include('repo_module_path_arguments'),
            ('\\b[A-Za-z_][A-Za-z0-9_]*\\b', Name.Variable),
            ('/', Punctuation),
        ],
        'repo_module_path_arguments': [
            ('\\[', Punctuation, 'body_repo_module_path_arguments'),
        ],
        'body_repo_module_path_arguments': [
            ('\\]', Punctuation, '#pop'),
            include('repo_identifier_list_items'),
            (r'(?s:.)', Text),
        ],
        'repo_identifier_list_items': [
            include('repo_comments'),
            (',', Punctuation),
            include('repo_identifiers'),
        ],
        'repo_identifiers': [
            ('\\b[A-Za-z_][A-Za-z0-9_]*\\b', Name.Variable),
        ],
        'context_path_open': [
            ('(?=(?:\\s|//[^\\r\\n]*|--[^\\r\\n]*|/\\*[\\s\\S]*?\\*/)*(?:open|sig|enum|pred|fun|fact|assert|run|check|let|private|abstract|one|lone|some|var)\\b)', Text, '#pop'),
            include('repo_comments'),
            ('\\bas\\b', Keyword.Namespace),
            include('repo_module_path_components'),
            (r'(?s:.)', Text),
        ],
        'repo_signature_declarations': [
            ('\\b(abstract|private|var)\\b(?!\\$)', Keyword.Reserved),
            ('\\b(one|lone|some)\\b(?=(?:(?:\\s+)|/\\*[\\s\\S]*?\\*/|//[^\\r\\n]*|--[^\\r\\n]*|\\b(?:abstract|private|var|one|lone|some)\\b)*\\bsig\\b(?!\\$))', Keyword.Reserved),
            ('(?=\\bsig\\b(?!\\$))', Text, 'context_signature'),
        ],
        'context_signature': [
            ('(?<=\\})', Text, '#pop'),
            ('\\b(sig)\\b(?!\\$)', Keyword.Declaration),
            include('repo_signature_hierarchy'),
            include('repo_signature_fields'),
            (r'(?s:.)', Text),
        ],
        'repo_signature_hierarchy': [
            ('(?<=sig)', Text, 'body_repo_signature_hierarchy'),
        ],
        'body_repo_signature_hierarchy': [
            ('(?=\\{)', Text, '#pop'),
            include('repo_comments'),
            include('repo_strings'),
            include('repo_meta_identifiers'),
            ('\\b(extends|in)\\b', Keyword),
            ('\\+', Operator),
            ('=', Operator),
            include('repo_keywords'),
            include('repo_constants'),
            include('repo_identifiers'),
            include('repo_punctuation'),
            (r'(?s:.)', Text),
        ],
        'repo_meta_identifiers': [
            ('\\b(sig|field)\\$(?![A-Za-z0-9_])', Name.Constant),
            ('\\b(static|var)\\$(?![A-Za-z0-9_])', Name.Constant),
            ('\\$', Punctuation),
        ],
        'repo_keywords': [
            ('\\b(for|but|exactly|expect|with)\\b', Keyword),
            ('\\b(enabled|event|invariant|modifies)\\b', Keyword),
            ('\\b(Int|String|int|seq|steps)\\b', Keyword.Type),
            ('\\b(this)\\b', Name.Builtin),
        ],
        'repo_constants': [
            ('\\b0x(?:_|[0-9A-Fa-f]{2})+\\b', Number.Hex),
            ('\\b0b[01_]+\\b', Number.Bin),
            ('\\b[0-9][0-9_]*\\b', Number.Integer),
            ('\\b(univ|iden|none)\\b', Name.Builtin),
        ],
        'repo_punctuation': [
            ('\\.\\.', Punctuation),
            (',|:(?!>)|(?<!\\|)\\|(?!\\|)', Punctuation),
            ('@', Punctuation),
        ],
        'repo_signature_fields': [
            ('\\{', Punctuation, 'body_repo_signature_fields'),
        ],
        'body_repo_signature_fields': [
            ('\\}', Punctuation, '#pop'),
            include('repo_comments'),
            include('repo_strings'),
            ('\\b(private|var|disj)\\b(?!\\$)', Keyword.Reserved),
            include('repo_field_declaration_value'),
            include('repo_block_expressions'),
            (r'(?s:.)', Text),
        ],
        'repo_field_declaration_value': [
            ('(:)(?!>)|(=)', _capture_groups(Text, {1: Punctuation, 2: Operator}), 'body_repo_field_declaration_value'),
        ],
        'body_repo_field_declaration_value': [
            ('(?=,|\\})', Text, '#pop'),
            include('repo_block_expressions'),
            (r'(?s:.)', Text),
        ],
        'repo_block_expressions': [
            include('repo_comments'),
            include('repo_strings'),
            include('repo_expression_groups'),
            include('repo_expression_brackets'),
            include('repo_expression_blocks'),
            ('(:)(?!>)|(->)', _capture_groups(Text, {1: Punctuation, 2: Operator}), 'context_type_operator'),
            ('(?<=:)\\s*(one|lone|some|set)\\b', Keyword.Reserved),
            ('(?<=->)\\s*(one|lone|some|set)\\b', Keyword.Reserved),
            include('repo_punctuation'),
            ('\\b(disj|var)\\b(?!\\$)', Keyword.Reserved),
            ('\\b(one|lone|some|set)\\b(?=(?:(?:\\s+)|/\\*[\\s\\S]*?\\*/|//[^\\r\\n]*|--[^\\r\\n]*)*->)', Keyword.Reserved),
            ('\\b(and|or|not|implies|iff|else)\\b', Operator.Word),
            ('\\b(all|no|one|some|lone)\\b', Operator.Word),
            ('\\b(always|eventually|after|before|until|releases|since|triggered|historically|once)\\b', Operator.Word),
            ('\\blet\\b', Operator.Word, 'context_binding_let'),
            ('\\b(in)\\b', Operator.Word),
            ('\\b(sum|int)\\b', Operator.Word),
            ('\\b(seq)\\b', Keyword.Reserved),
            ('<=>|=>|!|&&|\\|\\||;', Operator),
            ('>>>|>>|<<', Operator),
            ("\\+\\+|->|<:|:>|\\+|-|&|\\*|\\^|~|\\.|#|'", Operator),
            ('=<|>=|=|<|>', Operator),
            include('repo_meta_identifiers'),
            include('repo_keywords'),
            include('repo_constants'),
            include('repo_identifiers'),
        ],
        'repo_expression_groups': [
            ('\\(', Punctuation, 'body_repo_expression_groups'),
        ],
        'body_repo_expression_groups': [
            ('\\)', Punctuation, '#pop'),
            include('repo_block_expressions'),
            (r'(?s:.)', Text),
        ],
        'repo_expression_brackets': [
            ('\\[', Punctuation, 'body_repo_expression_brackets'),
        ],
        'body_repo_expression_brackets': [
            ('\\]', Punctuation, '#pop'),
            ('\\b(disj)\\b(?!\\$)', Keyword.Reserved),
            include('repo_block_expressions'),
            (r'(?s:.)', Text),
        ],
        'repo_expression_blocks': [
            ('\\{', Punctuation, 'body_repo_expression_blocks'),
        ],
        'body_repo_expression_blocks': [
            ('\\}', Punctuation, '#pop'),
            include('repo_block_expressions'),
            (r'(?s:.)', Text),
        ],
        'context_type_operator': [
            ('((?:one|lone|some|set)\\b)|(?=\\S)(?!/\\*|//|--)', _capture_groups(Text, {1: Keyword.Reserved}), '#pop'),
            include('repo_comments'),
            include('repo_strings'),
            (r'(?s:.)', Text),
        ],
        'context_binding_let': [
            ('(?=\\|(?!\\|)|\\{(?!\\s*[A-Za-z_][A-Za-z0-9_]*\\s*:))', Text, '#pop'),
            ('=', Operator, 'context_binding_let_2'),
            include('repo_block_expressions'),
            (r'(?s:.)', Text),
        ],
        'context_binding_let_2': [
            ('(?=\\|(?!\\|)|\\{(?!\\s*[A-Za-z_][A-Za-z0-9_]*\\s*:))', Text, '#pop'),
            include('repo_comments'),
            include('repo_strings'),
            (',', Punctuation, 'context_comma'),
            include('repo_block_expressions'),
            (r'(?s:.)', Text),
        ],
        'context_comma': [
            ('(=)|(?=\\S)(?![A-Za-z_]|/\\*|//|--)', _capture_groups(Text, {1: Operator}), '#pop'),
            include('repo_comments'),
            include('repo_strings'),
            include('repo_identifiers'),
            (r'(?s:.)', Text),
        ],
        'repo_callable_declaration_parameters': [
            ('\\b(fun|pred)\\b\\s+([A-Za-z_][A-Za-z0-9_]*)\\s*(\\[)', _capture_groups(Text, {1: Keyword.Declaration, 2: Name.Variable, 3: Punctuation}), 'body_repo_callable_declaration_parameters'),
        ],
        'body_repo_callable_declaration_parameters': [
            ('\\]', Punctuation, '#pop'),
            include('repo_comments'),
            include('repo_strings'),
            include('repo_callable_parameter_value'),
            ('\\b(disj|var)\\b(?!\\$)', Keyword.Reserved),
            (',', Punctuation),
            include('repo_block_expressions'),
            (r'(?s:.)', Text),
        ],
        'repo_callable_parameter_value': [
            ('(:)(?!>)|(=)', _capture_groups(Text, {1: Punctuation, 2: Operator}), 'body_repo_callable_parameter_value'),
        ],
        'body_repo_callable_parameter_value': [
            ('(?=,|\\])', Text, '#pop'),
            include('repo_block_expressions'),
            (r'(?s:.)', Text),
        ],
        'repo_top_level_let_declarations': [
            ('\\blet\\b', Keyword.Declaration, 'context_let'),
        ],
        'context_let': [
            ('(?<=\\})|(?=(?:[ \\t]+|/\\*[\\s\\S]*?\\*/|//[^\\r\\n]*|--[^\\r\\n]*)*(?:(?:private|abstract|one|lone|some|var)\\b[ \\t]+)*(?:module|open|sig|enum|pred|fun|fact|assert|run|check|let)\\b)', Text, '#pop'),
            include('repo_comments'),
            include('repo_strings'),
            include('repo_top_level_let_header'),
            include('repo_top_level_let_expression_body'),
            include('repo_top_level_let_block_body'),
            (r'(?s:.)', Text),
        ],
        'repo_top_level_let_header': [
            ('(?=[A-Za-z_])', Text, 'body_repo_top_level_let_header'),
        ],
        'body_repo_top_level_let_header': [
            ('(?=(?:\\s|//[^\\r\\n]*|--[^\\r\\n]*|/\\*[\\s\\S]*?\\*/)*(?:=|\\{))', Text, '#pop'),
            include('repo_comments'),
            ('\\[', Punctuation, 'context_brackets'),
            include('repo_identifiers'),
            (r'(?s:.)', Text),
        ],
        'context_brackets': [
            ('\\]', Punctuation, '#pop'),
            include('repo_identifier_list_items'),
            (r'(?s:.)', Text),
        ],
        'repo_top_level_let_expression_body': [
            ('=', Operator, 'body_repo_top_level_let_expression_body'),
        ],
        'body_repo_top_level_let_expression_body': [
            ('(?=(?:[ \\t]+|/\\*[\\s\\S]*?\\*/|//[^\\r\\n]*|--[^\\r\\n]*)*(?:(?:private|abstract|one|lone|some|var)\\b[ \\t]+)*(?:module|open|sig|enum|pred|fun|fact|assert|run|check|let)\\b)', Text, '#pop'),
            include('repo_comments'),
            include('repo_strings'),
            include('repo_block_expressions'),
            (r'(?s:.)', Text),
        ],
        'repo_top_level_let_block_body': [
            ('(?=\\{)', Text, 'body_repo_top_level_let_block_body'),
        ],
        'body_repo_top_level_let_block_body': [
            ('(?<=\\})', Text, '#pop'),
            include('repo_comments'),
            include('repo_strings'),
            include('repo_block_expressions'),
            (r'(?s:.)', Text),
        ],
        'repo_declaration_keywords': [
            ('\\b(pred|fun)\\b', Keyword.Declaration),
            ('\\b(enum)\\b', Keyword.Declaration),
            ('\\b(module)\\b', Keyword.Namespace),
            ('\\b(run|check)\\b', Keyword.Declaration),
            ('\\b(assert)\\b', Keyword.Declaration),
            ('\\b(fact)\\b', Keyword.Declaration),
        ],
    }
