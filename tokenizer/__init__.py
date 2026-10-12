from enum import Enum, auto
import re

class InvalidNumber(Exception):
    def __init__(self, message):
        super().__init__(message)

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

class Tokenizer:

    keywords = sorted([
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

    operators = {
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

    operator_values = sorted(
        operators.keys(), 
        key=len, 
        reverse=True
    )

    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.row = 1
        self.col = 1

        if len(source) == 0: self.curr_char = None
        else: self.curr_char = self.source[self.pos]

        self.newline_flag = False

    def _advance(self):
        self.pos += 1
        self.col += 1
        if self.pos >= len(self.source):
            self.curr_char = None
            return

        if self.newline_flag:
            self.newline_flag = False
            self.col = 1
            self.row += 1

        self.curr_char = self.source[self.pos]
        if self.curr_char == '\n':
            self.newline_flag = True

    def _peek(self, offset: int):
        if self.pos + offset >= len(self.source):
            return None

        return self.source[self.pos + offset]

    def snapshot(self):
       """
         Takes a snapshot of the current tokenizer state.
       """
       snap = Tokenizer(self.source)
       snap.pos = self.pos
       snap.row = self.row
       snap.col = self.col
       snap.curr_char = self.curr_char

       return snap

    def _restore(self, tokenizer):
        """
        Sets the values of the tokenizer to match values of another
        """
        self.pos = tokenizer.pos
        self.col = tokenizer.col
        self.row = tokenizer.row
        self.curr_char = tokenizer.curr_char

    def _skip_comment(self):
        while self.curr_char and self.curr_char != '\n':
            self._advance()

    def _skip_whitespace(self):
        while self.curr_char and self.curr_char in (' ', '\n', '\t'):
            self._advance()

    def _skip_non_newline_whitespace(self):
        while self.curr_char and self.curr_char in (' ', '\t'):
            self._advance()
   
    def next(self):
        self._skip_non_newline_whitespace()

        if self.curr_char == '\n':
            row = self.row
            col = self.col
            self._advance()
            return Token(TokenTypes.NEWLINE, '\n', row, col)

        # ^^^^^^ don't skip whitespace until the first newline 
        # has been tokenized!
        self._skip_whitespace()

        if self.curr_char == None:
            return Token(TokenTypes.EOF, 'EOF', self.row, self.col) 

        if self.curr_char == '#':
            self._skip_comment()
            return self.next()
        
        if self.curr_char == ';':
            row = self.row
            col = self.col
            self._advance()
            return Token(TokenTypes.SEMICOLON, '\n', row, col)

        if self.curr_char == '.':
            row = self.row
            col = self.col
            if self._peek(1) == '.':
                self._advance()
                self._advance()
                return Token(TokenTypes.SPREAD, '..', row, col)
            else:
                self._advance()
                return Token(TokenTypes.DOT, '.', row, col)

        if self.curr_char == ':':
            row = self.row
            col = self.col
            self._advance()
            return Token(TokenTypes.COLON, ':', row, col)

        if self.curr_char == ',':
            row = self.row
            col = self.col
            self._advance()
            return Token(TokenTypes.COMMA, ',', row, col)
        
        if self.curr_char == '(':
            row = self.row
            col = self.col
            self._advance()
            return Token(TokenTypes.LPAREN, '(', row, col)

        if self.curr_char == ')':
            row = self.row
            col = self.col
            self._advance()
            return Token(TokenTypes.RPAREN, ')', row, col)
        
        if self.curr_char == '[':
            row = self.row
            col = self.col
            self._advance()
            return Token(TokenTypes.LBRACKET, '[', row, col)

        if self.curr_char == ']':
            row = self.row
            col = self.col
            self._advance()
            return Token(TokenTypes.RBRACKET, ']', row, col)

        if self.curr_char == '{':
            row = self.row
            col = self.col
            self._advance()
            return Token(TokenTypes.LBRACE, '{', row, col)

        if self.curr_char == '}':
            row = self.row
            col = self.col
            self._advance()
            return Token(TokenTypes.RBRACE, '}', row, col)

        if self.curr_char in ('"', "'"):
            return self._scan_string()
        
        # test for negative numbers:
        if self.curr_char == '-' and re.match(r'[0-9]', self._peek(1)):
            return self._scan_number()

        # non-negative numbers:
        if re.match(r'[0-9]', self.curr_char):
            return self._scan_number()

        # test for keywords:
        for word in Tokenizer.keywords:
            if self.curr_char == word[0]:
                snap = self.snapshot()
                token = self._scan_keyword(word)
                if not token: self._restore(snap)
                else: return token

        for op in Tokenizer.operator_values:
            if self.curr_char == op[0]:
                snap = self.snapshot()
                token = self._scan_operator(op)
                if not token: self._restore(snap)
                else: return token

        if self.curr_char == 'b':
            snap = self.snapshot()
            token = self._scan_binary()
            if not token: self._restore(snap)
            else: return token

        if self.curr_char == 'h':
            snap = self.snapshot()
            token = self._scan_hexadecimal()
            if not token: self._restore(snap)
            else: return token

        if self.curr_char in ('f', 't'):
            snap = self.snapshot()
            token = self._scan_boolean()
            if not token: self._restore(snap)
            else: return token
            
        if re.match(r'[a-zA-Z_]', self.curr_char):
            return self._scan_identifier()
        
        raise Exception("Unknown Token")

    ###############################################################
    ## scanner definitions:                                      ##
    ###############################################################

    def _scan_identifier(self):
        row = self.row
        col = self.col
        value = self.curr_char
        
        self._advance()
        while self.curr_char and re.match(r'[a-zA-Z0-9_]', self.curr_char):
            value += self.curr_char
            self._advance()

        return Token(TokenTypes.IDENTIFIER, value, row, col)

    def _scan_binary(self):
        row = self.row
        col = self.col
        self._advance()

        if not self.curr_char or self.curr_char not in "01":
            return None

        value = ''

        while self.curr_char and self.curr_char in "01":
            value += self.curr_char
            self._advance()
        
        if self.curr_char and re.match(r'[a-zA-Z0-9_]', self.curr_char):
            return None # return None if this is an identifier

        return Token(TokenTypes.BINARY, value, row, col)

    def _scan_hexadecimal(self):
        row = self.row
        col = self.col
        self._advance()

        if not self.curr_char:
            return None

        if not re.match(r'[0-9a-fA-F]', self.curr_char):
            return None

        value = ''

        while self.curr_char and re.match(r'[0-9a-fA-F]', self.curr_char):
            value += self.curr_char
            self._advance()
        
        if self.curr_char and re.match(r'[a-zA-Z0-9_]', self.curr_char):
            return None # return None if this is an identifier

        return Token(TokenTypes.HEXADECIMAL, value, row, col)

    def _scan_number(self):
        # disambiguiates between float and int
        row = self.row
        col = self.col
        value = ""

        if self.curr_char == '-':
            value += '-'
            self._advance()

        while self.curr_char and re.match(r'[0-9]', self.curr_char):
            value += self.curr_char
            self._advance()

        if self.curr_char == '.':
            return self._scan_float(value)

        # check for invalid beginning character of next token
        # (to avoid 456ffxx being counted as a number)
        valid_int_suffix = r'[\]\)\-\+\*\^%/\s;:,\}]'
        if self.curr_char and not re.match(valid_int_suffix, self.curr_char):
            raise InvalidNumber(f"{value + self.curr_char} is not a valid number {self.row} {self.col}")

        return Token(TokenTypes.INT, value, self.row, self.col)

    def _scan_float(self, int_value):
        value = int_value
        # add the '.'
        value += self.curr_char
        self._advance()
        while self.curr_char and re.match(r'[0-9]', self.curr_char):
            value += self.curr_char
            self._advance()

        # check for invalid beginning character of next token
        # (to avoid 456ffxx being counted as a number)
        valid_float_suffix = r'[\]\)\-\+\*\^%/\s;,\}]'
        if self.curr_char and not re.match(valid_float_suffix, self.curr_char):
            raise InvalidNumber(f"{value + self.curr_char} is not a valid number {self.row} {self.col}")

        return Token(TokenTypes.FLOAT, value, self.row, self.col)

    def _scan_string(self):
        row = self.row
        col = self.col
        ending = self.curr_char
        value = ''
        self._advance()

        while self.curr_char != ending:
            if not self.curr_char: raise Exception('Incomplete string at end of input')
            value += self.curr_char
            self._advance()

        self._advance()

        return Token(TokenTypes.STRING, value, row, col)
         
    def _scan_boolean(self):
        word = None
        if self.curr_char == 'f': word = str(False).lower()
        elif self.curr_char == 't': word = str(True).lower()
        else: return None

        for i in range(0, len(word)):
           if self.curr_char != word[i]:
               return None
           self._advance()

        return Token(TokenTypes.BOOLEAN, word, self.row, self.col)

    def _scan_keyword(self, keyword):
        row = self.row
        col = self.col

        for i in range(0, len(keyword)):
            if self.curr_char != keyword[i]:
                return None

            self._advance()
        
        if self.curr_char and re.match(r'[a-zA-Z0-9_]', self.curr_char):
            return None

        t_type = getattr(TokenTypes, f"KW_{keyword.upper()}")
        return Token(t_type, keyword, row, col)

    def _scan_operator(self, op):
        row = self.row
        col = self.col
        
        for i in range(0, len(op)):
            if self.curr_char != op[i]:
                return None

            self._advance()

        t_type = Tokenizer.operators[op]
        return Token(t_type, op, row, col)
