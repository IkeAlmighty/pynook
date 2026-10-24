from dataclasses import dataclass
from runtime.operators import InfixEvaluator, OpTypes

class NkValue: 
    
    def resolve_local(self, name):
        if name in self.members:
            return self.members[name]

    def __eq__(self, rhs):
        return InfixEvaluator.evaluate(OpTypes.EQ, self, rhs)

    def __ne__(self, rhs):
        return InfixEvaluator.evaluate(OpTypes.NOT_EQ, self, rhs)


class NkBool(NkValue):

    def __init__(self, value):
        if value == 'true': self.value = True
        elif value == 'false': self.value = False
        else: raise Exception(f"Invalid NkBool value {value}")
        self.members = {
            "__id__": NkId("ac2e02cc-0b91-402b-aea2-f0e88c110a76")
        }
    
    def __repr__(self):
        return "NkBool(true)" if self.value else "NkBool(false)"

@dataclass(frozen=True)
class NkId(NkValue): 
    value: str

@dataclass
class NkArgument:
    value: NkValue
    bind_to: str | NkUnbound

@dataclass
class NkSpreadArgument:
    values: NkList
    
@dataclass(frozen=True)
class NkInt(NkValue): 
    value: int
    members = {
        "__id__": NkId("882b5545-cb21-4875-94ac-134ab8e055e5")
    }

@dataclass(frozen=True)
class NkFloat(NkValue):
    value: float
    members = {
        "__id__": NkId("1ce035b4-21e2-45ba-a1a6-13b9696f87de")
    }

@dataclass(frozen=True)
class NkString(NkValue):
    value: str
    members = {
        "__id__": NkId("4693a742-bf91-49a8-9301-93900432a18e")
    }
    
@dataclass
class NkNone(NkValue): 
    members = {
        "__id__": NkId("1e80e598-08fc-463e-961c-bfbadb11bb92")
    }

    
@dataclass(frozen=True)
class NkNull(NkValue):
    members = {
        "__id__": NkId("357f25a5-18e8-4ce6-8a27-2fadd6f52055")
    }


# used for argument binding:
@dataclass
class NkUnbound(NkValue): pass

# used for operator traps:
@dataclass
class NkUnresolved(NkValue): pass

@dataclass
class NkCollectAll(NkValue): pass


NK_NONE = NkNone()
NK_NULL = NkNull()
NK_UNBOUND = NkUnbound()
NK_FALSE = NkBool('false')
NK_TRUE = NkBool('true')
NK_UNRESOLVED = NkUnresolved()
NK_COLLECT_ALL = NkCollectAll()

