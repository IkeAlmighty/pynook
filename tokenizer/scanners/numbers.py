import re
from tokenizer.exceptions import InvalidNumber
from tokenizer.tokens import Token, TokenTypes

def scan_binary(tokenizer):
    tokenizer.state.advance()

    if not tokenizer.state.curr_char or tokenizer.state.curr_char not in "01":
        return None

    value = ''

    while tokenizer.state.curr_char and tokenizer.state.curr_char in "01":
        value += tokenizer.state.curr_char
        tokenizer.state.advance()
    
    if tokenizer.state.curr_char and re.match(r'[a-zA-Z0-9_]', tokenizer.state.curr_char):
        return None # return None if this is an identifier

    return Token(TokenTypes.BINARY, value, tokenizer.state.location)

def scan_hexadecimal(tokenizer):
    tokenizer.state.advance()

    if not tokenizer.state.curr_char:
        return None

    if not re.match(r'[0-9a-fA-F]', tokenizer.state.curr_char):
        return None

    value = ''

    while tokenizer.state.curr_char and re.match(r'[0-9a-fA-F]', tokenizer.state.curr_char):
        value += tokenizer.state.curr_char
        tokenizer.state.advance()
    
    if tokenizer.state.curr_char and re.match(r'[a-zA-Z0-9_]', tokenizer.state.curr_char):
        return None # return None if this is an identifier

    return Token(TokenTypes.HEXADECIMAL, value, tokenizer.state.location)

def scan_number(tokenizer):
    # disambiguiates between float and int
    value = ""

    if tokenizer.state.curr_char == '-':
        value += '-'
        tokenizer.state.advance()

    while tokenizer.state.curr_char and re.match(r'[0-9]', tokenizer.state.curr_char):
        value += tokenizer.state.curr_char
        tokenizer.state.advance()

    if tokenizer.state.curr_char == '.':
        return scan_float(tokenizer, value)

    # check for invalid beginning character of next token
    # (to avoid 456ffxx being counted as a number)
    valid_int_suffix = r'[\]\)\-\+\*\^%/\s;:,\}]'
    if tokenizer.state.curr_char and not re.match(valid_int_suffix, tokenizer.state.curr_char):
        raise InvalidNumber(f"{value + tokenizer.state.curr_char} is not a valid number {tokenizer.state.row} {tokenizer.state.col}")

    return Token(TokenTypes.INT, value, tokenizer.state.location)

def scan_float(tokenizer, int_value):
    value = int_value
    # add the '.'
    value += tokenizer.state.curr_char
    tokenizer.state.advance()
    while tokenizer.state.curr_char and re.match(r'[0-9]', tokenizer.state.curr_char):
        value += tokenizer.state.curr_char
        tokenizer.state.advance()

    # check for invalid beginning character of next token
    # (to avoid 456ffxx being counted as a number)
    valid_float_suffix = r'[\]\)\-\+\*\^%/\s;,\}]'
    if tokenizer.state.curr_char and not re.match(valid_float_suffix, tokenizer.state.curr_char):
        raise InvalidNumber(f"{value + tokenizer.state.curr_char} is not a valid number {tokenizer.state.row} {tokenizer.state.col}")

    return Token(TokenTypes.FLOAT, value, tokenizer.state.location)

