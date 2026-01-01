grammar ConfigDsl;

// Configuration file DSL (INI-like format)
config
    : section* EOF
    ;

section
    : '[' sectionName ']' keyValue*
    ;

keyValue
    : key '=' value NEWLINE
    ;

sectionName
    : IDENTIFIER
    ;

key
    : IDENTIFIER
    ;

value
    : STRING
    | NUMBER
    | BOOLEAN
    | IDENTIFIER
    ;

IDENTIFIER
    : [a-zA-Z_][a-zA-Z0-9_]*
    ;

STRING
    : '"' ( ESC | ~["\\] )* '"'
    | '\'' ( ESC | ~['\\] )* '\''
    ;

fragment ESC
    : '\\' ["'\\]
    ;

NUMBER
    : [0-9]+ ('.' [0-9]+)?
    ;

BOOLEAN
    : 'true'
    | 'false'
    | 'yes'
    | 'no'
    ;

NEWLINE
    : '\r'? '\n'
    | '\r'
    ;

WS
    : [ \t]+ -> skip
    ;

COMMENT
    : '#' ~[\r\n]* -> skip
    | ';' ~[\r\n]* -> skip
    ;
