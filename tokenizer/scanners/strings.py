from tokenizer.tokens import Token, TokenTypes

def scan_string(tokenizer):
    ending = tokenizer.state.curr_char
    value = ''
    tokenizer.state.advance()

    while tokenizer.state.curr_char != ending:
        if not tokenizer.state.curr_char: raise Exception('Incomplete string at end of input')
        value += tokenizer.state.curr_char
        tokenizer.state.advance()

    tokenizer.state.advance()

    return Token(TokenTypes.STRING, value, tokenizer.state.location)

