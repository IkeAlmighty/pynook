from __future__ import annotations
from dataclasses import dataclass
from debug.location import Location

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
    location: Location

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
    location: Location = None

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
    catch: Catch | None
    finally_scope: Scope | None
    location: Location

@dataclass
class Parameters(Node):
    parameters: list[ RestParameter | Parameter ]
    location: Location

@dataclass 
class Parameter(Node):
    identifier: Identifier
    default: Expr | None
    location: Location

@dataclass
class RestParameter(Node):
    parameter: Parameter
    location: Location

@dataclass
class DefineFunction(Node):
    parameters: Parameters
    scope: Scope
    has_root: bool
    location: Location

@dataclass
class Assignment(Statement):
    target: Member | Subscript | Identifier 
    value: Expr | DefineFunction
    location: Location

@dataclass
class Member(Expr):
    target: Member | Identifier 
    name: Identifier
    location: Location

@dataclass
class AssignmentBatch(Node):
    assignments: list[ Assignment ]
    location: Location

@dataclass
class While(Statement):
    expr: Expr
    scope: Scope
    location: Location

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
    iterable: Expr
    scope: Scope
    location: Location = None

@dataclass
class If(Statement):
    condition: Expr
    then_scope: Scope
    elifs: list[ If ]
    else_scope: Scope | None
    location: Location

@dataclass
class Switch(Statement):
    expr: Expr
    scope: Scope
    location: Location

@dataclass
class Case(Node):
    literal: Literal
    scope: Scope
    location: Location

@dataclass
class Default(Node):
    scope: Scope
    location: Location

@dataclass
class SpreadTerm(Expr):
    expr: Literal | Identifier | Call | Subscript | Member
    location: Location

@dataclass
class BinaryOperation(Expr):
    left: Expr
    op_token: Token
    right: Expr
    location: Location

@dataclass
class Subscript(Expr):
    expr: Expr
    start: String | Integer | None
    end: Integer | None
    is_slice: bool
    location: Location

@dataclass
class Call(Expr):
    expr: Expr
    arguments: Arguments
    location: Location

@dataclass
class Arguments(Node):
    arguments: list[ Argument | SpreadArgument ]
    location: Location

@dataclass
class Argument(Node):
    expr: Expr
    bind_to: Identifier | None
    location: Location

@dataclass
class SpreadArgument(Node):
    expr: Expr
    location: Location

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

