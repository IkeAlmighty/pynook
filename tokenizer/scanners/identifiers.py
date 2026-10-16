import re
from tokenizer.tokens import Token, TokenTypes

def scan_identifier(tokenizer):
    value = tokenizer.state.curr_char
    
    tokenizer.state.advance()
    while tokenizer.state.curr_char and re.match(r'[a-zA-Z0-9_]', tokenizer.state.curr_char):
        value += tokenizer.state.curr_char
        tokenizer.state.advance()

    return Token(TokenTypes.IDENTIFIER, value, tokenizer.state.location)
