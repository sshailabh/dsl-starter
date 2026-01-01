/*
 * Configuration DSL Grammar (INI-style)
 * 
 * Inspired by grammars-v4/toml/TomlParser.g4 and TomlLexer.g4
 * 
 * This is a simplified INI-style config format. For complete TOML support:
 * See: https://github.com/antlr/grammars-v4/tree/master/toml
 * 
 * Features:
 * - Sections: [section_name]
 * - Key-value pairs: key = value
 * - Typed values: strings, numbers, booleans
 * - Comments: # or ;
 */

grammar ConfigDsl;

// Entry point
config
    : (NEWLINE | section)* EOF
    ;

section
    : sectionHeader (NEWLINE+ keyValue)* NEWLINE*
    ;

sectionHeader
    : '[' IDENTIFIER ']'
    ;

keyValue
    : key '=' value
    ;

key
    : IDENTIFIER
    | DOTTED_KEY
    ;

value
    : string
    | NUMBER
    | BOOLEAN
    | IDENTIFIER
    ;

string
    : BASIC_STRING
    | LITERAL_STRING
    ;

// Lexer rules (simplified from TOML lexer)
BOOLEAN
    : 'true'
    | 'false'
    | 'yes'
    | 'no'
    | 'on'
    | 'off'
    ;

DOTTED_KEY
    : IDENTIFIER ('.' IDENTIFIER)+
    ;

IDENTIFIER
    : [a-zA-Z_][a-zA-Z0-9_-]*
    ;

NUMBER
    : '-'? [0-9]+ ('.' [0-9]+)?
    ;

BASIC_STRING
    : '"' (ESC | ~["\\])* '"'
    ;

LITERAL_STRING
    : '\'' (~['\r\n])* '\''
    ;

fragment ESC
    : '\\' ["\\/bfnrt]
    ;

NEWLINE
    : '\r'? '\n'
    | '\r'
    ;

WS
    : [ \t]+ -> skip
    ;

COMMENT
    : ('#' | ';') ~[\r\n]* -> skip
    ;
