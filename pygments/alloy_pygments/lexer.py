"""Generated Pygments lexer for Alloy. Do not edit by hand.
Regenerate with: python pygments/build.py
Source: grammar/alloy.tmLanguage.json
"""
import re
from pygments.lexer import RegexLexer, bygroups, include
from pygments.token import Comment, Keyword, Name, Number, Operator, Punctuation, String, Text


class AlloyLexer(RegexLexer):
    """Alloy 6 lexer compiled from the canonical TextMate grammar."""
    name = "Alloy"
    aliases = ["alloy6"]
    filenames = ["*.als"]
    mimetypes = ["text/x-alloy"]
    flags = re.MULTILINE
    # Rules are ordered. Includes share rules; a third tuple item pushes
    # a body state, and '#pop' returns to the enclosing state.
    # Whitespace gaps in mixed captures are explicit Text groups.
    tokens = {
        'root': [
            include('comments'),
            (r'"', String.Delimiter, 'strings_body'),
            include('module_declarations_and_imports'),
            include('signature_declarations'),
            (r'\b(fun|pred)\b', Keyword.Declaration, 'callable_declarations_body'),
            (r'\blet\b', Keyword.Declaration, 'let'),
            include('declaration_keywords'),
            include('meta_identifiers'),
            include('keywords'),
            include('block_expressions'),
            (r'\[', Punctuation, 'expression_brackets_body'),
            (r'\{', Punctuation, 'expression_blocks_body'),
            include('punctuation'),
            include('constants'),
            (r'\b[A-Za-z_][A-Za-z0-9_]*\b', Name.Variable),
            (r'(?s:.)', Text),
        ],
        'comments': [
            (r'//', Comment.Single, 'comment_line_double_slash'),
            (r'--', Comment.Single, 'comment_line_double_dash'),
            (r'/\*\*(?!/)', Comment.Multiline, 'comment_block_documentation'),
            (r'/\*', Comment.Multiline, 'comment_block'),
        ],
        'comment_line_double_slash': [
            (r'$', Comment.Single, '#pop'),
            (r'[^\r\n]+', Comment.Single),
        ],
        'comment_line_double_dash': [
            (r'$', Comment.Single, '#pop'),
            (r'[^\r\n]+', Comment.Single),
        ],
        'comment_block_documentation': [
            (r'\*/', Comment.Multiline, '#pop'),
            (r'[^*]+', Comment.Multiline),
            (r'\*(?!/)', Comment.Multiline),
        ],
        'comment_block': [
            (r'\*/', Comment.Multiline, '#pop'),
            (r'[^*]+', Comment.Multiline),
            (r'\*(?!/)', Comment.Multiline),
        ],
        'strings_body': [
            (r'"', String.Delimiter, '#pop'),
            (r'\\.', String.Escape),
            (r'[^"\\]+', String.Double),
        ],
        'module_declarations_and_imports': [
            (r'\b(module)\b', Keyword.Namespace, 'path_module'),
            (r'\b(open)\b', Keyword.Namespace, 'path_open'),
        ],
        'path_module': [
            (r'(?=(?:\s|//[^\r\n]*|--[^\r\n]*|/\*[\s\S]*?\*/)*(?:open|sig|enum|pred|fun|fact|assert|run|check|let|private|abstract|one|lone|some|var)\b)', Text, '#pop'),
            include('module_path_components'),
            (r'(?s:.)', Text),
        ],
        'module_path_components': [
            include('comments'),
            (r'\[', Punctuation, 'module_path_arguments_body'),
            (r'\b[A-Za-z_][A-Za-z0-9_]*\b', Name.Variable),
            (r'/', Punctuation),
        ],
        'module_path_arguments_body': [
            (r'\]', Punctuation, '#pop'),
            include('identifier_list_items'),
            (r'(?s:.)', Text),
        ],
        'identifier_list_items': [
            include('comments'),
            (r',', Punctuation),
            (r'\b[A-Za-z_][A-Za-z0-9_]*\b', Name.Variable),
        ],
        'path_open': [
            (r'(?=(?:\s|//[^\r\n]*|--[^\r\n]*|/\*[\s\S]*?\*/)*(?:open|sig|enum|pred|fun|fact|assert|run|check|let|private|abstract|one|lone|some|var)\b)', Text, '#pop'),
            include('comments'),
            (r'\bas\b', Keyword.Namespace),
            include('module_path_components'),
            (r'(?s:.)', Text),
        ],
        'signature_declarations': [
            (r'\b(abstract|private|var)\b(?!\$)', Keyword.Reserved),
            (r'\b(one|lone|some)\b(?=(?:(?:\s+)|/\*[\s\S]*?\*/|//[^\r\n]*|--[^\r\n]*|\b(?:abstract|private|var|one|lone|some)\b)*\bsig\b(?!\$))', Keyword.Reserved),
            (r'(?=\bsig\b(?!\$))', Text, 'signature'),
        ],
        'signature': [
            (r'(?<=\})', Text, '#pop'),
            (r'\b(sig)\b(?!\$)', Keyword.Declaration),
            (r'(?<=sig)', Text, 'signature_hierarchy_body'),
            (r'\{', Punctuation, 'signature_fields_body'),
            (r'(?s:.)', Text),
        ],
        'signature_hierarchy_body': [
            (r'(?=\{)', Text, '#pop'),
            include('comments'),
            (r'"', String.Delimiter, 'strings_body'),
            include('meta_identifiers'),
            (r'\b(extends|in)\b', Keyword),
            (r'\+', Operator),
            (r'=', Operator),
            include('keywords'),
            include('constants'),
            (r'\b[A-Za-z_][A-Za-z0-9_]*\b', Name.Variable),
            include('punctuation'),
            (r'(?s:.)', Text),
        ],
        'meta_identifiers': [
            (r'\b(sig|field)\$(?![A-Za-z0-9_])', Name.Constant),
            (r'\b(static|var)\$(?![A-Za-z0-9_])', Name.Constant),
            (r'\$', Punctuation),
        ],
        'keywords': [
            (r'\b(for|but|exactly|expect|with)\b', Keyword),
            (r'\b(enabled|event|invariant|modifies)\b', Keyword),
            (r'\b(Int|String|int|seq|steps)\b', Keyword.Type),
            (r'\b(this)\b', Name.Builtin),
        ],
        'constants': [
            (r'\b0x(?:_|[0-9A-Fa-f]{2})+\b', Number.Hex),
            (r'\b0b[01_]+\b', Number.Bin),
            (r'\b[0-9][0-9_]*\b', Number.Integer),
            (r'\b(univ|iden|none)\b', Name.Builtin),
        ],
        'punctuation': [
            (r'\.\.', Punctuation),
            (r',|:(?!>)|(?<!\|)\|(?!\|)', Punctuation),
            (r'@', Punctuation),
        ],
        'signature_fields_body': [
            (r'\}', Punctuation, '#pop'),
            include('comments'),
            (r'"', String.Delimiter, 'strings_body'),
            (r'\b(private|var|disj)\b(?!\$)', Keyword.Reserved),
            (r'(?=:(?!>))|(=)', bygroups(Operator), 'field_declaration_value_body'),
            include('block_expressions'),
            (r'(?s:.)', Text),
        ],
        'field_declaration_value_body': [
            (r'(?=,|\})', Text, '#pop'),
            include('block_expressions'),
            (r'(?s:.)', Text),
        ],
        'block_expressions': [
            include('comments'),
            (r'"', String.Delimiter, 'strings_body'),
            (r'\(', Punctuation, 'expression_groups_body'),
            (r'\[', Punctuation, 'expression_brackets_body'),
            (r'\{', Punctuation, 'expression_blocks_body'),
            (r'(:)(?!>)|(->)', bygroups(Punctuation, Operator), 'multiplicity_after_separator'),
            (r'(?<=:)\s*(one|lone|some|set)\b', Keyword.Reserved),
            (r'(?<=->)\s*(one|lone|some|set)\b', Keyword.Reserved),
            include('punctuation'),
            (r'\b(disj|var)\b(?!\$)', Keyword.Reserved),
            (r'\b(one|lone|some|set)\b(?=(?:(?:\s+)|/\*[\s\S]*?\*/|//[^\r\n]*|--[^\r\n]*)*->)', Keyword.Reserved),
            (r'\b(and|or|not|implies|iff|else)\b', Operator.Word),
            (r'\b(all|no|one|some|lone)\b', Operator.Word),
            (r'\b(always|eventually|after|before|until|releases|since|triggered|historically|once)\b', Operator.Word),
            (r'\blet\b', Operator.Word, 'binding_let'),
            (r'\b(in)\b', Operator.Word),
            (r'\b(sum|int)\b', Operator.Word),
            (r'\b(seq)\b', Keyword.Reserved),
            (r'<=>|=>|!|&&|\|\||;', Operator),
            (r'>>>|>>|<<', Operator),
            (r"\+\+|->|<:|:>|\+|-|&|\*|\^|~|\.|#|'", Operator),
            (r'=<|>=|=|<|>', Operator),
            include('meta_identifiers'),
            include('keywords'),
            include('constants'),
            (r'\b[A-Za-z_][A-Za-z0-9_]*\b', Name.Variable),
        ],
        'expression_groups_body': [
            (r'\)', Punctuation, '#pop'),
            include('block_expressions'),
            (r'(?s:.)', Text),
        ],
        'expression_brackets_body': [
            (r'\]', Punctuation, '#pop'),
            (r'\b(disj)\b(?!\$)', Keyword.Reserved),
            include('block_expressions'),
            (r'(?s:.)', Text),
        ],
        'expression_blocks_body': [
            (r'\}', Punctuation, '#pop'),
            include('block_expressions'),
            (r'(?s:.)', Text),
        ],
        'multiplicity_after_separator': [
            (r'((?:one|lone|some|set)\b)|(?=\S)(?!/\*|//|--)', bygroups(Keyword.Reserved), '#pop'),
            include('comments'),
            (r'"', String.Delimiter, 'strings_body'),
            (r'(?s:.)', Text),
        ],
        'binding_let': [
            (r'(?=\|(?!\|)|\{(?!\s*[A-Za-z_][A-Za-z0-9_]*\s*:))', Text, '#pop'),
            (r'=', Operator, 'binding_let_2'),
            include('block_expressions'),
            (r'(?s:.)', Text),
        ],
        'binding_let_2': [
            (r'(?=\|(?!\|)|\{(?!\s*[A-Za-z_][A-Za-z0-9_]*\s*:))', Text, '#pop'),
            include('comments'),
            (r'"', String.Delimiter, 'strings_body'),
            (r',', Punctuation, 'additional_let_binding'),
            include('block_expressions'),
            (r'(?s:.)', Text),
        ],
        'additional_let_binding': [
            (r'(=)|(?=\S)(?![A-Za-z_]|/\*|//|--)', bygroups(Operator), '#pop'),
            include('comments'),
            (r'"', String.Delimiter, 'strings_body'),
            (r'\b[A-Za-z_][A-Za-z0-9_]*\b', Name.Variable),
            (r'(?s:.)', Text),
        ],
        'callable_declarations_body': [
            (r'(?=[:{])', Text, '#pop'),
            include('comments'),
            (r'\[', Punctuation, 'callable_declaration_parameters_body'),
            (r'\b[A-Za-z_][A-Za-z0-9_]*\b', Name.Variable),
            (r'(?s:.)', Text),
        ],
        'callable_declaration_parameters_body': [
            (r'\]', Punctuation, '#pop'),
            include('comments'),
            (r'"', String.Delimiter, 'strings_body'),
            (r'(?=:(?!>))|(=)', bygroups(Operator), 'callable_parameter_value_body'),
            (r'\b(disj|var)\b(?!\$)', Keyword.Reserved),
            (r',', Punctuation),
            include('block_expressions'),
            (r'(?s:.)', Text),
        ],
        'callable_parameter_value_body': [
            (r'(?=,|\])', Text, '#pop'),
            include('block_expressions'),
            (r'(?s:.)', Text),
        ],
        'let': [
            (r'(?<=\})|(?=(?:[ \t]+|/\*[\s\S]*?\*/|//[^\r\n]*|--[^\r\n]*)*(?:(?:private|abstract|one|lone|some|var)\b[ \t]+)*(?:module|open|sig|enum|pred|fun|fact|assert|run|check|let)\b)', Text, '#pop'),
            include('comments'),
            (r'"', String.Delimiter, 'strings_body'),
            (r'(?=[A-Za-z_])', Text, 'top_level_let_header_body'),
            (r'=', Operator, 'top_level_let_expression_body_content'),
            (r'(?=\{)', Text, 'top_level_let_block_body_content'),
            (r'(?s:.)', Text),
        ],
        'top_level_let_header_body': [
            (r'(?=(?:\s|//[^\r\n]*|--[^\r\n]*|/\*[\s\S]*?\*/)*(?:=|\{))', Text, '#pop'),
            include('comments'),
            (r'\[', Punctuation, 'brackets'),
            (r'\b[A-Za-z_][A-Za-z0-9_]*\b', Name.Variable),
            (r'(?s:.)', Text),
        ],
        'brackets': [
            (r'\]', Punctuation, '#pop'),
            include('identifier_list_items'),
            (r'(?s:.)', Text),
        ],
        'top_level_let_expression_body_content': [
            (r'(?=(?:[ \t]+|/\*[\s\S]*?\*/|//[^\r\n]*|--[^\r\n]*)*(?:(?:private|abstract|one|lone|some|var)\b[ \t]+)*(?:module|open|sig|enum|pred|fun|fact|assert|run|check|let)\b)', Text, '#pop'),
            include('comments'),
            (r'"', String.Delimiter, 'strings_body'),
            include('block_expressions'),
            (r'(?s:.)', Text),
        ],
        'top_level_let_block_body_content': [
            (r'(?<=\})', Text, '#pop'),
            include('comments'),
            (r'"', String.Delimiter, 'strings_body'),
            include('block_expressions'),
            (r'(?s:.)', Text),
        ],
        'declaration_keywords': [
            (r'\b(pred|fun)\b', Keyword.Declaration),
            (r'\b(enum)\b', Keyword.Declaration),
            (r'\b(module)\b', Keyword.Namespace),
            (r'\b(run|check)\b', Keyword.Declaration),
            (r'\b(assert)\b', Keyword.Declaration),
            (r'\b(fact)\b', Keyword.Declaration),
        ],
    }
