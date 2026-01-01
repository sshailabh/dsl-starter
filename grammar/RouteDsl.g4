/*
 * Route DSL Grammar
 * 
 * A custom DSL for defining HTTP routes, inspired by web frameworks
 * like Express.js, Flask, and Ruby on Rails.
 * 
 * Example:
 *   route GET /users -> Users.list;
 *   route POST /users -> Users.create;
 *   route GET /users/{id} -> Users.show;
 * 
 * This demonstrates:
 * - Custom language design
 * - Path parameters with {param} syntax
 * - Handler references as Controller.method
 */

grammar RouteDsl;

// Entry point
file
    : routeDecl* EOF
    ;

routeDecl
    : 'route' method path '->' handler ';'
    ;

method
    : 'GET'
    | 'POST'
    | 'PUT'
    | 'DELETE'
    | 'PATCH'
    | 'HEAD'
    | 'OPTIONS'
    ;

path
    : PATH
    ;

handler
    : IDENTIFIER ('.' IDENTIFIER)*
    ;

// Lexer rules
PATH 
    : '/' ~[ \t\r\n;]+ 
    ;

IDENTIFIER 
    : [a-zA-Z_][a-zA-Z0-9_]* 
    ;

WS 
    : [ \t\r\n]+ -> skip 
    ;

COMMENT 
    : '#' ~[\r\n]* -> skip 
    ;
