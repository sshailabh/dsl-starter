/*
 * API Schema DSL Grammar
 * 
 * A custom DSL for defining REST APIs with types, endpoints, and error definitions.
 * Inspired by OpenAPI/Swagger but with a more concise syntax.
 * 
 * Example:
 *   api UserService {
 *     base_url: "/api/v1"
 *     
 *     endpoint GET /users/{id:uuid} {
 *       response: User
 *       errors: 404 "User not found"
 *     }
 *     
 *     type User {
 *       id: uuid
 *       name: string
 *     }
 *   }
 * 
 * This demonstrates:
 * - Nested structures with braces
 * - Typed parameters in paths
 * - Custom type definitions
 */

grammar ApiSchema;

// Entry point
schema 
    : apiDef+ EOF 
    ;

apiDef 
    : 'api' IDENTIFIER '{' apiContent* '}'
    ;

apiContent
    : baseUrl
    | endpoint
    | typeDef
    ;

baseUrl
    : 'base_url' ':' STRING
    ;

endpoint
    : 'endpoint' method path '{' endpointContent* '}'
    ;

method 
    : 'GET' 
    | 'POST' 
    | 'PUT' 
    | 'DELETE' 
    | 'PATCH' 
    ;

path 
    : pathSegment+
    ;

pathSegment
    : '/' IDENTIFIER
    | '/' '{' IDENTIFIER (':' typeName)? '}'
    ;

endpointContent
    : queryParams
    | bodyDef
    | responseDef
    | errorsDef
    ;

queryParams
    : 'query' ':' paramList
    ;

bodyDef
    : 'body' ':' typeRef
    ;

responseDef
    : 'response' ':' typeRef
    ;

errorsDef
    : 'errors' ':' errorDef (',' errorDef)*
    ;

errorDef
    : NUMBER STRING
    ;

paramList
    : param (',' param)*
    ;

param
    : IDENTIFIER ':' typeName '?'?
    ;

typeDef
    : 'type' IDENTIFIER '{' field* '}'
    ;

field
    : IDENTIFIER ':' typeRef '?'?
    ;

typeRef
    : typeName ('[]')?
    | IDENTIFIER ('[]')?
    ;

typeName 
    : 'string' 
    | 'int' 
    | 'float' 
    | 'bool' 
    | 'uuid' 
    | 'timestamp'
    ;

// Lexer rules
IDENTIFIER 
    : [a-zA-Z_][a-zA-Z0-9_]* 
    ;

NUMBER 
    : [0-9]+ 
    ;

STRING 
    : '"' (~["])* '"' 
    ;

WS 
    : [ \t\r\n]+ -> skip 
    ;

LINE_COMMENT 
    : '//' ~[\r\n]* -> skip 
    ;
