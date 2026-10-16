import re
from tokenizer.tokens import Token, TokenTypes

def scan_keyword(tokenizer, keyword):

    for i in range(0, len(keyword)):
        if tokenizer.state.curr_char != keyword[i]:
            return None

        tokenizer.state.advance()
    
    if tokenizer.state.curr_char and re.match(r'[a-zA-Z0-9_]', tokenizer.state.curr_char):
        return None

    t_type = getattr(TokenTypes, f"KW_{keyword.upper()}")
    return Token(t_type, keyword, tokenizer.state.location)

def scan_boolean(tokenizer):
    word = None
    if tokenizer.state.curr_char == 'f': word = str(False).lower()
    elif tokenizer.state.curr_char == 't': word = str(True).lower()
    else: return None

    for i in range(0, len(word)):
       if tokenizer.state.curr_char != word[i]:
           return None
       tokenizer.state.advance()

    return Token(TokenTypes.BOOLEAN, word, tokenizer.state.location)


