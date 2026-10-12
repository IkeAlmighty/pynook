import sys
import os
from tokenizer import Tokenizer
from parser import Parser
from ir.builder import IRBuilder
from vm.interpreter import VirtualMachine
from runtime.values import NkScope, NkList
from runtime.builtins import inject_builtins

def run_program(source, *program_args):
    tokenizer = Tokenizer(source)
    parser = Parser(tokenizer)

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

    # inject program arguments:
    arguments = NkList(program_args)

    builtins_scope.members["args"] = arguments

    vm.execute(builtins_scope, ir)
    return vm.stack.pop()

if __name__ == "__main__":
    args = sys.argv

    if len(args) < 1:
        raise Exception("missing source file in command line arguments")

    if len(args) > 1:
        prog_args = args[2:]

    path = args[1]

    with open(path) as file:
        source = file.read()
        run_program(source, *args)
        
