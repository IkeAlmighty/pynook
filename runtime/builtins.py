import inspect
from tokenizer import Tokenizer
from parser import Parser
from ir.builder import IRBuilder
from ir.definitions import ScopeDefinition
from ir.instructions import *
from runtime.values import *

def inject_builtins(nk_scope):
    builtins = [
        (name[3:], fn)
        for name, fn in inspect.getmembers(BuiltIns)
        if name.startswith("nk_")
    ]

    for name, function in builtins:

        # TODO: add support for default parameters in builtins

        parameter_definition = ScopeDefinition()
        sig = inspect.signature(function)
        parameter_names = []
        for parameter in sig.parameters.values():
            if parameter.name == "vm": continue
            parameter_definition.instructions.append(
                PushConst(
                    Constant(
                        type_name="unbound",
                        value=None
                    )
                )
            )

            parameter_definition.instructions.append(
                Store(parameter.name)
            )

            parameter_names.append(parameter.name)

        body_definition = ScopeDefinition()

        body_definition.instructions.append(
            CallBuiltIn(function, parameter_names)
        )
        
        nk_scope.members[name] = NkScope(
            parent=nk_scope,
            body_definition=body_definition,
            parameter_definition=parameter_definition,
            name=name
        )

class BuiltIns:

    @staticmethod
    def nk_import(vm, filepath):
        # normalize the module name
        module_name = filepath.value

        if not module_name.endswith('.nk') and not module_name.endswith('.json'):
            module_name = module_name + ".nk"

        # open the file:
        source = ""
        with open(module_name) as f:
            source = f.read()

        # tokenize, parse, and create ir:
        tokenizer = Tokenizer(source)
        parser = Parser(tokenizer)
        ir_builder = IRBuilder()

        ast = parser._block()
        ir = ir_builder.build(ast)

        # create a scope to run file against:
        file_scope = NkScope(
            parent=vm.frame.scope,
            body_definition=ir,
            name=module_name
        )

        file_scope.set_as_file_scope()

        # execute ir on vm:
        vm.execute(file_scope, ir)

        # return the scope:
        return file_scope

    @staticmethod
    def nk_print(vm, obj):

        if isinstance(obj, NkScope):
            print(obj.members)

        else: 
            print(obj.value)

    @staticmethod
    def nk_open(vm, address, mode):
        raise NotImplementedError()

    @staticmethod
    def nk_connect(vm, address):
        raise NotImplementedError()

    @staticmethod
    def nk_listen(vm, address):
        raise NotImplementedError()

    @staticmethod
    def nk_accept(vm, listener):
        raise NotImplementedError()

    @staticmethod
    def nk_read(vm, stream):
        raise NotImplementedError()
   
    @staticmethod
    def nk_write(vm, stream, value):
        raise NotImplementedError()
    
    @staticmethod
    def nk_close(vm, stream):
        raise NotImplementedError()

    @staticmethod
    def nk_hash(vm, value):
        raise NotImplementedError()
