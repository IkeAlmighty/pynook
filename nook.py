import sys
import os

from runtime import Runtime
from nast.evaluator import Evaluator
from tokenizer import Tokenizer
from parser import Parser

if __name__ == "__main__":
    args = sys.argv

    if len(args) < 1:
        raise Exception("missing source file in command line arguments")

    if len(args) > 1:
        prog_args = args[2:]

    with open(args[1]) as file:
        source = file.read()
        tokenizer = Tokenizer(source)
        parser = Parser(tokenizer)


        runtime = Runtime()
        evaluator = Evaluator(runtime)

        filepath = os.path.basename(args[1])

        evaluator.name_hints.append(filepath)
        evaluator.dispatch(parser.file())
        evaluator.name_hints.pop()

