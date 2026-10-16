from enum import Enum, auto

class Token:

    def __init__(self, type, value, row, col):
        self.type = type
        self.value = value
        self.row = row
        self.col = col

    def __str__(self):
        return f"{self.type} {self.value} ({self.row}:{self.col})"

    def __repr__(self):
        return self.__str__()

class TokenTypes(Enum):
    IDENTIFIER = auto()

    LPAREN = auto()
    RPAREN = auto()

    LBRACKET = auto()
    RBRACKET = auto()
    
    LBRACE = auto()
    RBRACE = auto()

    COLON = auto()
    COMMA = auto()
    NEWLINE = auto()
    SEMICOLON = auto()

    INT = auto()
    FLOAT = auto()
    STRING = auto()
    BINARY = auto()
    HEXADECIMAL = auto()
    BOOLEAN = auto()
    KW_NONE = auto()
    KW_NULL = auto()

    SPREAD = auto()
    DOT = auto()

    EOF = auto()

    KW_IGNORE = auto()
    KW_COLLECT = auto()
    KW_RETURN = auto()
    KW_SET = auto()
    KW_LEAVE = auto()
    KW_THROW = auto()
    KW_TRY = auto()
    KW_CATCH = auto()
    KW_FINALLY = auto()
    KW_FOR = auto()
    KW_IN = auto()
    KW_WHILE = auto()
    KW_DO = auto()
    KW_IF = auto()
    KW_ELIF = auto()
    KW_ELSE = auto()
    KW_SWITCH = auto()
    KW_CASE = auto()
    KW_DEFAULT = auto()
    KW_CONTINUE = auto()

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

