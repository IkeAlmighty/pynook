import sys
import os
from tokenizer import Tokenizer
from parser import Parser
from ir.builder import IRBuilder
from vm.interpreter import VirtualMachine, ThrowCompletion
from runtime.values import NkScope, NkList, NkString
from runtime.builtins import inject_builtins, BuiltIns

def compile_stdlib():
    curr_path = os.path.dirname(__file__)
    module_name = os.path.join(curr_path, "nk_stdlib/core.nk")

    source = ""
    with open(module_name) as f:
        source = f.read()

    tokenizer = Tokenizer(source)
    parser = Parser(tokenizer)
    ir_builder = IRBuilder()

    ast = parser._block()
    ir = ir_builder.build(ast)

    return ir

def handle_uncaught_exception(completion):
    # handle uncaught exceptions:
    if isinstance(completion, ThrowCompletion):
        value = completion.value

        if isinstance(value, NkScope):
            message = value.resolve_local("message")

            if message is not NK_NONE:
                print(message, file=sys.stderr)

            else: 
                print(value, file=sys.stderr)

        else: 
            print(value)

        exit(-1)

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

    # inject builtin functions:
    inject_builtins(builtins_scope)

    # inject program arguments:
    arguments = NkList(program_args)
    builtins_scope.members["args"] = arguments

    # compile and inject the standard library:
    stdlib_ir = compile_stdlib()

    # execute the standard lib:
    completion = vm.execute(builtins_scope, stdlib_ir)
    handle_uncaught_exception(completion)

    # execute the program:
    completion = vm.execute(builtins_scope, ir)
    handle_uncaught_exception(completion)
    
    # grab the top level scope:
    scope = vm.stack.pop()

    return scope

if __name__ == "__main__":
    args = sys.argv

    if len(args) < 2:
        raise Exception("missing source file in command line arguments")

    if len(args) > 1:
        prog_args = args[2:]

    path = args[1]

    with open(path) as file:
        source = file.read()
        run_program(source, *args)
        
