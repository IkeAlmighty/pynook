from enum import Enum, auto

class OpTypes:
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
    AND = auto()
    OR = auto()
    NEGATE = auto()
    SIZE = auto() 
    EQ = auto()
    NOT_EQ = auto()
    GREATER_EQ = auto()
    LESS_EQ = auto()
    LESS = auto()
    GREATER = auto()


class InfixEvaluator:

    def evaluate(optype, *args):
        # dynamically create the operator function based on the args
        breakpoint()
        print(optype.type.name)
        method_name = optype.name

        for value in args:
            method_name += f"_{type(value).__class__.__name__}"

        breakpoint()

        method = getattr(InfixEvaluator, method_name)
        return method(*args)


    # TODO: add all the evaluator functions:


