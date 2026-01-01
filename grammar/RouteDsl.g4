grammar RouteDsl;

// Entry point
file
  : routeDecl* EOF
  ;

routeDecl
  : ROUTE method path ARROW handler SEMI
  ;

method
  : GET
  | POST
  | PUT
  | DELETE
  ;

path
  : PATH
  ;

handler
  : IDENT (DOT IDENT)*
  ;

// ===== Lexer =====

ROUTE  : 'route' ;
GET    : 'GET' ;
POST   : 'POST' ;
PUT    : 'PUT' ;
DELETE : 'DELETE' ;

ARROW : '->' ;
SEMI  : ';' ;
DOT   : '.' ;

// Path tokens like: /users, /users/{id}, /v1/users/{id}/posts
PATH : '/' ~[ \t\r\n;]+ ;

IDENT : [a-zA-Z_] [a-zA-Z0-9_]* ;

WS : [ \t\r\n]+ -> skip ;


