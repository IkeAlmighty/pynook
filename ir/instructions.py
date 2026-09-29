from dataclasses import dataclass
from ir.definitions import ScopeDefinition, Constant

class Instruction: pass

@dataclass
class Load(Instruction):
    name: str

@dataclass
class LoadMember(Instruction):
    value: str

@dataclass
class Store(Instruction):
    name: str

@dataclass
class StoreMember(Instruction):
    name: str

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
class CreateArguments(Instruction):
    length: int

@dataclass
class Call(Instruction): pass

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
class Collect(Instruction): 
    value: Constant

@dataclass
class Return(Instruction):
    value: Constant

@dataclass
class Equals(Instruction): pass

@dataclass 
class NotEquals(Instruction): pass

@dataclass
class LessThan(Instruction): pass

@dataclass
class LessThanOrEqual(Instruction): pass

@dataclass 
class GreaterThan(Instruction): pass

@dataclass
class GreaterThanOrEqual(Instruction): pass


