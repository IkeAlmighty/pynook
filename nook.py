import sys
import os
from tokenizer import Tokenizer
from parser import Parser
from ir.builder import IRBuilder
from vm.interpreter import VirtualMachine
from runtime.values import NkScope
from runtime.builtins import inject_builtins

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

        filepath = os.path.basename(args[1])

        ir_builder = IRBuilder()

        ir = ir_builder.build(parser.file())

        vm = VirtualMachine()

        builtins_scope = NkScope(
            parent=None,
            body_definition=ir,
            parameter_definition=None,
            name="__builtins__"
        )

        inject_builtins(builtins_scope)

        vm.execute(builtins_scope, ir)
