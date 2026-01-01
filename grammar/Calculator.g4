/*
 * Calculator Grammar
 * 
 * Derived from grammars-v4/arithmetic/arithmetic.g4
 * 
 * This is a simplified version for learning ANTLR4 basics.
 * For the full version with functions (sin, cos, log, etc.), 
 * see: https://github.com/antlr/grammars-v4/tree/master/arithmetic
 */

grammar Calculator;

// Entry point - an expression followed by EOF
expr
    : expr POW expr                     # Power
    | expr (TIMES | DIV) expr           # MulDiv
    | expr (PLUS | MINUS) expr          # AddSub
    | (PLUS | MINUS)? atom              # Signed
    ;

atom
    : NUMBER
    | LPAREN expr RPAREN
    | VARIABLE
    ;

// Lexer rules
NUMBER
    : DIGIT+ ('.' DIGIT+)?
    ;

VARIABLE
    : [a-zA-Z_][a-zA-Z0-9_]*
    ;

fragment DIGIT
    : [0-9]
    ;

LPAREN : '(' ;
RPAREN : ')' ;
PLUS   : '+' ;
MINUS  : '-' ;
TIMES  : '*' ;
DIV    : '/' ;
POW    : '^' ;

WS : [ \t\r\n]+ -> skip ;
