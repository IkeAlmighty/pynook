from tokenizer.tokens import TokenTypes

KEYWORDS = sorted([
    "ignore",
    "collect",
    "return",
    "set",
    "leave",
    "throw",
    "try",
    "catch",
    "finally",
    "for",
    "in",
    "while",
    "do",
    "if",
    "elif",
    "else",
    "switch",
    "case",
    "default",
    "none",
    "null"
], key=len, reverse=True)

OPERATORS = {
    "-": TokenTypes.SUB,
    "+": TokenTypes.ADD,
    "/": TokenTypes.DIV,
    "*": TokenTypes.MULT,
    "**":TokenTypes.EXPONENT,
    "%": TokenTypes.MODULO,
    "^": TokenTypes.XOR,
    "&": TokenTypes.BW_AND,
    "|": TokenTypes.BW_OR,
    "&&":TokenTypes.AND,
    "||":TokenTypes.OR,
    "!": TokenTypes.NEGATE,
    "#": TokenTypes.SIZE,
    "==": TokenTypes.EQ,
    "!=": TokenTypes.NOT_EQ,
    ">=": TokenTypes.GREATER_EQ,
    "<=": TokenTypes.LESS_EQ,
    "<": TokenTypes.LESS,
    ">": TokenTypes.GREATER
}

OPERATOR_VALUES = sorted(
    OPERATORS.keys(), 
    key=len, 
    reverse=True
)

