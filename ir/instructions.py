from dataclasses import dataclass
from ir.definitions import ScopeDefinition

class Instruction: pass

@dataclass
class Load(Instruction):
    name: str

@dataclass
class Store(Instruction):
    name: str

@dataclass
class PushConst(Instruction):
    value: NkValue

@dataclass 
class CreateScope(Instruction):
    definition: ScopeDefinition

@dataclass
class CreateFunction(Instruction):
    definition: ScopeDefinition
    parameters: dict
