// Simple Hello World grammar - perfect for learning ANTLR4 basics
grammar Hello;

// Parser rules (lowercase)
greeting
    : 'hello' name
    | 'hi' name
    | 'hey' name
    ;

name
    : NAME+
    ;

// Lexer rules (UPPERCASE)
NAME : [a-zA-Z]+ ;
WS   : [ \t\r\n]+ -> skip ;
