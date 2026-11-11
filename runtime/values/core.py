from dataclasses import dataclass
from runtime.operators import BinaryEvaluator, OpTypes

class NkValue: 

    TYPE_ID = None
    FAMILY = {}
    RANK = -1

    members = {}
    
    def resolve_local(self, name):
        if name == "__typeid__":
            if self.TYPE_ID is None:
                raise Exception(
                    f"{type(self).__name__} missing TYPE_ID"
                )

            return self.TYPE_ID

        return self.members.get(name, NK_NONE)

    def __repr__(self):
        raise NotImplementedError(f"{type(self)} does not implement __repr__")
        
    ########### UNARY ###################
    ###################################

    def negate(self):
        raise NotImplementedError(f"{type(self).__name__} does not support NEGATE")

    def size(self):
        raise NotImplementedError(f"{type(self).__name__} does not support SIZE")

    ########## BINARY ################
    ####################################

    def sub(self, rhs):
        raise NotImplementedError(f"{type(self).__name__} does not support SUB")

    def add(self, rhs):
        raise NotImplementedError(f"{type(self).__name__} does not support ADD")

    def div(self, rhs):
        raise NotImplementedError(f"{type(self).__name__} does not support DIV")

    def mult(self, rhs):
        raise NotImplementedError(f"{type(self).__name__} does not support MULT")

    def exponent(self, rhs):
        raise NotImplementedError(f"{type(self).__name__} does not support EXPONENT")

    def modulo(self, rhs):
        raise NotImplementedError(f"{type(self).__name__} does not support MODULO")

    def xor(self, rhs):
        raise NotImplementedError(f"{type(self).__name__} does not support XOR")

    def bw_and(self, rhs):
        raise NotImplementedError(f"{type(self).__name__} does not support BW_AND")

    def bw_or(self, rhs):
        raise NotImplementedError(f"{type(self).__name__} does not support BW_OR")

    def logical_and(self, rhs):
        raise NotImplementedError(f"{type(self).__name__} does not support AND")

    def logical_or(self, rhs):
        raise NotImplementedError(f"{type(self).__name__} does not support OR")
    
    def eq(self, rhs):
        raise NotImplementedError(f"{type(self).__name__} does not support EQ")

    def not_eq(self, rhs):
        return self.eq(rhs).negate()

    def greater_eq(self, rhs):
        return self.less(rhs).negate()

    def less_eq(self, rhs):
        return self.greater(rhs).negate()

    def less(self, rhs):
        raise NotImplementedError(f"{type(self).__name__} does not support LESS")

    def greater(self, rhs):
        raise NotImplementedError(f"{type(self).__name__} does not support GREATER")

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
    
@dataclass
class NkNone(NkValue): 
    TYPE_ID = NkId("1e80e598-08fc-463e-961c-bfbadb11bb92")
    
@dataclass(frozen=True)
class NkNull(NkValue):
    TYPE_ID = NkId("357f25a5-18e8-4ce6-8a27-2fadd6f52055")

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
NK_UNRESOLVED = NkUnresolved()
NK_COLLECT_ALL = NkCollectAll()

