/*
 * SQL Subset Grammar
 * 
 * Inspired by grammars-v4/sql/sqlite/SQLiteParser.g4
 * 
 * This is a simplified subset for learning. For complete SQL support:
 * - SQLite: https://github.com/antlr/grammars-v4/tree/master/sql/sqlite
 */

grammar SqlSubset;

// Entry point - supports multiple statements
sql_stmt_list
    : statement (';' statement)* ';'? EOF
    ;

statement
    : selectStmt
    | insertStmt
    | updateStmt
    | deleteStmt
    ;

// SELECT name, email FROM users WHERE age > 25
selectStmt
    : SELECT_ (STAR | columnList) FROM_ tableName whereClause? orderClause? limitClause?
    ;

// INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com')
insertStmt
    : INSERT_ INTO_ tableName '(' columnList ')' VALUES_ '(' valueList ')'
    ;

// UPDATE users SET email = 'new@email.com' WHERE id = 1
updateStmt
    : UPDATE_ tableName SET_ assignment (',' assignment)* whereClause?
    ;

// DELETE FROM users WHERE age < 18
deleteStmt
    : DELETE_ FROM_ tableName whereClause?
    ;

whereClause
    : WHERE_ condition (andOr condition)*
    ;

andOr
    : AND_ | OR_
    ;

condition
    : columnName comparator value
    | columnName IN_ '(' valueList ')'
    | columnName IS_ NULL_
    | columnName IS_ NOT_ NULL_
    ;

comparator
    : '=' | '!=' | '<>' | '<' | '>' | '<=' | '>='
    ;

orderClause
    : ORDER_ BY_ columnName (ASC_ | DESC_)?
    ;

limitClause
    : LIMIT_ NUMBER (OFFSET_ NUMBER)?
    ;

assignment
    : columnName '=' value
    ;

columnList
    : columnName (',' columnName)*
    ;

valueList
    : value (',' value)*
    ;

tableName
    : IDENTIFIER
    ;

columnName
    : IDENTIFIER
    ;

value
    : STRING
    | NUMBER
    | NULL_
    ;

// Keywords (case-insensitive in real SQL, but simplified here)
SELECT_ : 'SELECT' ;
FROM_   : 'FROM' ;
WHERE_  : 'WHERE' ;
INSERT_ : 'INSERT' ;
INTO_   : 'INTO' ;
VALUES_ : 'VALUES' ;
UPDATE_ : 'UPDATE' ;
SET_    : 'SET' ;
DELETE_ : 'DELETE' ;
AND_    : 'AND' ;
OR_     : 'OR' ;
ORDER_  : 'ORDER' ;
BY_     : 'BY' ;
ASC_    : 'ASC' ;
DESC_   : 'DESC' ;
LIMIT_  : 'LIMIT' ;
OFFSET_ : 'OFFSET' ;
IN_     : 'IN' ;
IS_     : 'IS' ;
NOT_    : 'NOT' ;
NULL_   : 'NULL' ;

STAR : '*' ;

IDENTIFIER
    : [a-zA-Z_][a-zA-Z0-9_]*
    ;

STRING
    : '\'' ( ~['\\] | '\\' . )* '\''
    ;

NUMBER
    : '-'? [0-9]+ ('.' [0-9]+)?
    ;

WS
    : [ \t\r\n]+ -> skip
    ;
