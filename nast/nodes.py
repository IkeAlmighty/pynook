from __future__ import annotations
from dataclasses import dataclass

class Node: pass
class Statement(Node): pass
class Expr(Statement): pass
class Literal(Expr): pass

@dataclass
class Block(Node):
    statements: list[ Statement ]

@dataclass
class Scope(Literal):
    block: Block
    row: int
    col: int

@dataclass
class List(Literal):
    items: list[ Expr ]
    row: int
    col: int

@dataclass
class Set(Literal):
    items: list[ Expr ]
    row: int
    col: int

@dataclass
class Leave(Statement):
    row: int
    col: int

@dataclass
class Continue(Statement):
    row: int
    col: int

@dataclass
class Collect(Statement):
    child: Expr | Assignment | None
    row: int
    col: int

@dataclass
class Return(Statement):
    child: Expr | Assignment | None
    row: int
    col: int

@dataclass
class Ignore(Statement):
    child: Expr | Assignment
    row: int
    col: int

@dataclass
class Identifier(Expr):
    value: str
    row: int
    col: int

@dataclass
class Catch(Node):
    identifier: Identifier
    scope: Scope
    row: int
    col: int

@dataclass
class Throw(Statement):
    expr: Expr
    row: int
    col: int

@dataclass
class TryCatch(Statement):
    try_scope: Scope
    catches: list[ Catch ]
    finally_scope: Scope

@dataclass
class Parameters(Node):
    params: list[ RestParameter | Parameter ]

@dataclass 
class Parameter(Node):
    identifier: Identifier
    default: Expr

@dataclass
class RestParameter(Node):
    parameter: Parameter

@dataclass
class DefineFunction(Node):
    params: Parameters
    scope: Scope
    has_root: bool

@dataclass
class Assignment(Statement):
    target: Member | Subscript | Identifier 
    value: Expr | DefineFunction

@dataclass
class Member(Expr):
    target: Member | Identifier 
    name: Identifier

@dataclass
class AssignmentBatch(Node):
    assignments: list[ Assignment ]

@dataclass
class While(Statement):
    expr: Expr
    scope: Scope

@dataclass
class For(Statement):
    init: Statement
    condition: Expr
    update: Statement
    scope: Scope
    row: int
    col: int

@dataclass
class ForIn(Statement):
    identifier: Identifier
    enumerated: Expr
    scope: Scope
    row: int
    col: int

@dataclass
class If(Statement):
    condition: Expr
    then_scope: Scope
    elifs: list[ If ]
    else_scope: Scope | None

@dataclass
class Switch(Statement):
    expr: Expr
    scope: Scope

@dataclass
class Case(Node):
    literal: Literal
    scope: Scope

@dataclass
class Default(Node):
    scope: Scope

@dataclass
class SpreadTerm(Expr):
    expr: Literal | Identifier | Call | Subscript | Member

@dataclass
class BinaryOperation(Expr):
    left: Expr
    op_token: Token
    right: Expr

@dataclass
class Arguments(Node):
    arguments: list[ Expr ]

@dataclass
class Call(Expr):
    expr: Expr
    arguments: Arguments

@dataclass
class Subscript(Expr):
    expr: Expr
    start: String | Integer | None
    end: Integer | None
    is_slice: bool

@dataclass
class SpreadArgs(Expr):
    expr: Expr
    row: int
    col: int

@dataclass
class Integer(Literal):
    value: int 
    row: int
    col: int

@dataclass
class Float(Literal):
    value: float
    row: int
    col: int

@dataclass
class String(Literal):
    value: str
    row: int
    col: int

@dataclass
class Boolean(Literal):
    value: bool
    row: int
    col: int

@dataclass
class Hexadecimal(Literal):
    value: int
    row: int
    col: int

@dataclass
class BinaryNumber(Literal):
    value: int
    row: int
    col: int

@dataclass
class NullValue(Literal):
    value: None
    row: int
    col: int

@dataclass
class NoneValue(Literal):
    value: None
    row: int
    col: int

