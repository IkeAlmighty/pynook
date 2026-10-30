from enum import Enum, auto

class OpTypes(Enum):
    # mirrors operators in tokenizer.tokens.TokenTypes
    SUB = auto()
    ADD = auto()
    DIV = auto()
    MULT = auto()
    EXPONENT = auto()
    MODULO = auto()
    XOR = auto()
    BW_AND = auto()
    BW_OR = auto()
    LOGICAL_AND = auto()
    LOGICAL_OR = auto()
    NEGATE = auto()
    SIZE = auto() 
    EQ = auto()
    NOT_EQ = auto()
    GREATER_EQ = auto()
    LESS_EQ = auto()
    LESS = auto()
    GREATER = auto()

def cast(value, target):

    if isinstance(value, target):
        return value

    elif target is NkInt:
        return NkInt(int(value))

    elif target is NkFloat:
        return NkFloat(float(value))

    elif target is NkString:
        return NkString(str(value))

    elif target is NkBool:
        return NkBool(bool(value))

    elif target is NkSet:
        # TODO
        raise NotImplementedError()

    elif target is NkList:
        # TODO
        raise NotImplementedError()

    elif target is NkNone:
        return NK_NONE

    elif target is NkNull:
        return NK_NULL

def promote(lhs, rhs): 

    if lhs.FAMILY != rhs.FAMILY:
        raise Exception(f"invalid promote with types ({lhs}, {rhs}).")

    target = max(
        lhs.__class__,
        rhs.__class__,
        key=lambda t: t.RANK
    )

    return cast(lhs, target), cast(rhs, target)

class BinaryEvaluator:

    def evaluate(optype, lhs, rhs):

        try:
            lhs, rhs = promote(lhs, rhs)

        except TypeError:
            return # TODO

        method = getattr(lhs, optype.name.lower())

        return method(rhs)
        
