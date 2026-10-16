from __future__ import annotations
from dataclasses import dataclass

class Node: pass
class Statement(Node): pass
class Expr(Statement): pass
class Literal(Expr): pass

@dataclass 
class File(Node):
    block: Block

@dataclass
class Block(Node):
    statements: list[ Statement ]

@dataclass
class Scope(Literal):
    block: Block
    location: Location

@dataclass
class List(Literal):
    items: list[ Expr ]
    location: Location

@dataclass
class Set(Literal):
    items: list[ Expr ]
    location: Location

@dataclass
class Leave(Statement):
    location: Location

@dataclass
class Continue(Statement):
    location: Location

@dataclass
class Collect(Statement):
    child: Expr | Assignment | None
    location: Location

@dataclass
class Return(Statement):
    child: Expr | Assignment | None
    location: Location

@dataclass
class Ignore(Statement):
    child: Expr | Assignment
    location: Location

@dataclass
class Identifier(Expr):
    value: str
    location: Location

@dataclass
class Catch(Node):
    identifier: Identifier
    scope: Scope
    location: Location

@dataclass
class Throw(Statement):
    expr: Expr
    location: Location

@dataclass
class TryCatch(Statement):
    try_scope: Scope
    catches: list[ Catch ]
    finally_scope: Scope

@dataclass
class Parameters(Node):
    parameters: list[ RestParameter | Parameter ]

@dataclass 
class Parameter(Node):
    identifier: Identifier
    default: Expr | None

@dataclass
class RestParameter(Node):
    parameter: Parameter

@dataclass
class DefineFunction(Node):
    parameters: Parameters
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
    location: Location

@dataclass
class ForIn(Statement):
    identifier: Identifier
    enumerated: Expr
    scope: Scope
    location: Location

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
class Subscript(Expr):
    expr: Expr
    start: String | Integer | None
    end: Integer | None
    is_slice: bool

@dataclass
class Call(Expr):
    expr: Expr
    arguments: Arguments

@dataclass
class Arguments(Node):
    arguments: list[ Argument | SpreadArgument ]

@dataclass
class Argument(Node):
    expr: Expr
    bind_to: Identifier | None

@dataclass
class SpreadArgument(Node):
    expr: Expr

@dataclass
class Integer(Literal):
    value: str 
    location: Location

@dataclass
class Float(Literal):
    value: str
    location: Location

@dataclass
class String(Literal):
    value: str
    location: Location

@dataclass
class Boolean(Literal):
    value: str
    location: Location

@dataclass
class Hexadecimal(Literal):
    value: str
    location: Location

@dataclass
class BinaryNumber(Literal):
    value: str
    location: Location

@dataclass
class NullValue(Literal):
    value: None
    location: Location

@dataclass
class NoneValue(Literal):
    value: None
    location: Location

