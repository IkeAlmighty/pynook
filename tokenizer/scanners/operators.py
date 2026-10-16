from tokenizer.constants import OPERATORS
from tokenizer.tokens import Token

def scan_operator(tokenizer, op):
    
    for i in range(0, len(op)):
        if tokenizer.state.curr_char != op[i]:
            return None

        tokenizer.state.advance()

    t_type = OPERATORS[op]
    return Token(t_type, op, tokenizer.state.location)
