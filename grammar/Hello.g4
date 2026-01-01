/*
 * Hello World Grammar
 * 
 * This is the canonical ANTLR4 learning example from 
 * "The Definitive ANTLR 4 Reference" Book
 * 
 * Perfect for understanding the basics:
 * - Parser rules (lowercase): define structure
 * - Lexer rules (UPPERCASE): define tokens
 * - The -> skip action: discard matched text
 */

grammar Hello;

// Parser rules (lowercase)
greeting
    : 'hello' name      # HelloGreeting
    | 'hi' name         # HiGreeting
    | 'hey' name        # HeyGreeting
    ;

name
    : WORD+
    ;

// Lexer rules (UPPERCASE)
WORD 
    : [a-zA-Z]+ 
    ;

WS   
    : [ \t\r\n]+ -> skip 
    ;
