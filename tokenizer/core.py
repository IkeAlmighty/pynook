import re

from tokenizer.constants import OPERATOR_VALUES, OPERATORS, KEYWORDS
from tokenizer.exceptions import InvalidNumber
from tokenizer.tokens import TokenTypes, Token
from tokenizer.state import TokenizerState

from tokenizer.scanners.strings import scan_string
from tokenizer.scanners.numbers import scan_number, scan_float, scan_hexadecimal, scan_binary
from tokenizer.scanners.keywords import scan_keyword, scan_boolean
from tokenizer.scanners.operators import scan_operator
from tokenizer.scanners.identifiers import scan_identifier

class Tokenizer:

    def __init__(self, source=None, state=None):
        if state == None:
            self.state = TokenizerState(source)
        else:
            self.state = state
    
    def _skip_comment(self):
        while self.state.curr_char and self.state.curr_char != '\n':
            self.state.advance()

    def _skip_whitespace(self):
        while self.state.curr_char and self.state.curr_char in (' ', '\n', '\t'):
            self.state.advance()

    def _skip_non_newline_whitespace(self):
        while self.state.curr_char and self.state.curr_char in (' ', '\t'):
            self.state.advance()
   
    def next(self):
        self._skip_non_newline_whitespace()

        if self.state.curr_char == '\n':
            self.state.advance()
            return Token(TokenTypes.NEWLINE, '\n', self.state.location)

        # ^^^^^^ don't skip whitespace until the first newline 
        # has been tokenized!
        self._skip_whitespace()

        if self.state.curr_char == None:
            return Token(TokenTypes.EOF, 'EOF', self.state.location) 

        if self.state.curr_char == '#':
            self._skip_comment()
            return self.next()
        
        if self.state.curr_char == ';':
            self.state.advance()
            return Token(TokenTypes.SEMICOLON, '\n', self.state.location)

        if self.state.curr_char == '.':
            if self.state.peek(1) == '.':
                self.state.advance()
                self.state.advance()
                return Token(TokenTypes.SPREAD, '..', self.state.location)
            else:
                self.state.advance()
                return Token(TokenTypes.DOT, '.', self.state.location)

        if self.state.curr_char == ':':
            self.state.advance()
            return Token(TokenTypes.COLON, ':', self.state.location)

        if self.state.curr_char == ',':
            self.state.advance()
            return Token(TokenTypes.COMMA, ',', self.state.location)
        
        if self.state.curr_char == '(':
            self.state.advance()
            return Token(TokenTypes.LPAREN, '(', self.state.location)

        if self.state.curr_char == ')':
            self.state.advance()
            return Token(TokenTypes.RPAREN, ')', self.state.location)
        
        if self.state.curr_char == '[':
            self.state.advance()
            return Token(TokenTypes.LBRACKET, '[', self.state.location)

        if self.state.curr_char == ']':
            self.state.advance()
            return Token(TokenTypes.RBRACKET, ']', self.state.location)

        if self.state.curr_char == '{':
            self.state.advance()
            return Token(TokenTypes.LBRACE, '{', self.state.location)

        if self.state.curr_char == '}':
            self.state.advance()
            return Token(TokenTypes.RBRACE, '}', self.state.location)

        if self.state.curr_char in ('"', "'"):
            return scan_string(self)
        
        # test for negative numbers:
        if self.state.curr_char == '-' and re.match(r'[0-9]', self.state.peek(1)):
            return scan_number(self)

        # non-negative numbers:
        if re.match(r'[0-9]', self.state.curr_char):
            return scan_number(self)

        # test for keywords:
        for word in KEYWORDS:
            if self.state.curr_char == word[0]:
                snap = self.state.snapshot()
                token = scan_keyword(self, word)
                if not token: self.state.restore(snap)
                else: return token

        for op in OPERATOR_VALUES:
            if self.state.curr_char == op[0]:
                snap = self.state.snapshot()
                token = scan_operator(self, op)
                if not token: self.state.restore(snap)
                else: return token

        if self.state.curr_char == 'b':
            snap = self.state.snapshot()
            token = scan_binary(self)
            if not token: self.state.restore(snap)
            else: return token

        if self.state.curr_char == 'h':
            snap = self.state.snapshot()
            token = scan_hexadecimal(self)
            if not token: self.state.restore(snap)
            else: return token

        if self.state.curr_char in ('f', 't'):
            snap = self.state.snapshot()
            token = scan_boolean(self)
            if not token: self.state.restore(snap)
            else: return token
            
        if re.match(r'[a-zA-Z_]', self.state.curr_char):
            return scan_identifier(self)
        
        raise Exception("Unknown Token")
