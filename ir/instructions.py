from typing import Callable
from dataclasses import dataclass
from ir.definitions import ScopeDefinition, Constant

class Instruction: pass

@dataclass
class Load(Instruction):
    name: str

@dataclass
class LoadMember(Instruction): pass

@dataclass
class LoadSlice(Instruction): pass

@dataclass
class Store(Instruction):
    name: str

@dataclass
class StoreMember(Instruction): pass

@dataclass
class PushConst(Instruction):
    value: Constant

@dataclass 
class CreateScope(Instruction):
    definition: ScopeDefinition

@dataclass
class CreateFunction(Instruction):
    body_definition: ScopeDefinition
    parameter_definition: ScopeDefinition

@dataclass 
class CreateArgument(Instruction):
    bind_to: str | None

@dataclass
class CreateSpreadArgument(Instruction): pass

@dataclass
class SpreadTerm(Instruction): pass

@dataclass
class Call(Instruction): pass

@dataclass
class CallBuiltIn(Instruction):
    function: Callable
    parameter_names: list[str]

@dataclass 
class CreateList(Instruction):
    length: int

@dataclass
class CreateSet(Instruction):
    length: int

@dataclass 
class Jump(Instruction):
    target: int | None

@dataclass 
class JumpIfFalse(Instruction):
    target: int | None

@dataclass
class Collect(Instruction): pass 

@dataclass
class Return(Instruction): pass

@dataclass
class Leave(Instruction): pass

#####################################################
############### Binary Op Instructions ##############
#####################################################

@dataclass
class Subtract(Instruction): pass

@dataclass
class Add(Instruction): pass

@dataclass
class Divide(Instruction): pass

@dataclass
class Multiply(Instruction): pass

@dataclass
class Exponent(Instruction): pass

@dataclass
class Modulo(Instruction): pass

@dataclass
class Xor(Instruction): pass

@dataclass
class BwAnd(Instruction): pass

@dataclass
class BwOr(Instruction): pass

@dataclass
class And(Instruction): pass

@dataclass
class Or(Instruction): pass

@dataclass
class Equal(Instruction): pass

@dataclass
class NotEqual(Instruction): pass

@dataclass
class GreaterThanOrEqual(Instruction): pass

@dataclass
class LessThanOrEqual(Instruction): pass

@dataclass
class LessThan(Instruction): pass

@dataclass
class GreaterThan(Instruction): pass

