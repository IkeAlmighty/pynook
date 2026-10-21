import inspect
import socket
import hashlib

from tokenizer import Tokenizer
from parser import Parser
from ir.builder import IRBuilder
from ir.definitions import ScopeDefinition
from ir.instructions import *
from runtime.values import *

from project_paths import rootpath

def _create_const_instruction(param):
    type_to_string_lookup = {
        str: "string",
        int: "int",
        bool: "bool", 
        float: "float",
        type(NK_NONE): "none",
    }

    default_type = type(param.default)
    if default_type not in type_to_string_lookup:
        raise Exception(f"python type {default_type} is not supported for default parameter values")

    type_name = type_to_string_lookup[default_type]

    return Constant(
        type_name=type_name, 
        value=param.default
    )

def create_builtin(name, function, parent):
    parameter_definition = ScopeDefinition()
    sig = inspect.signature(function)
    parameter_names = []

    for param_name, param in sig.parameters.items():
        if param_name == "vm": continue

        default_value_instruction = Constant(
            type_name="unbound",
            value=None
        )

        # replace the ir.Constant value with appropriate
        # value if there is a default value for the parameter:
        if param.default  is not inspect.Parameter.empty:
            default_value_instruction = _create_const_instruction(param)

        # create parameter definition:
        parameter_definition.instructions.append(
            PushConst(
                default_value_instruction    
            )
        )

        parameter_definition.instructions.append(
            Store(param_name)
        )
        ###################################

        # save parameter names so that CallBuiltIn can
        # be called correctly:
        parameter_names.append(param_name)

    body_definition = ScopeDefinition()

    body_definition.instructions.append(
        CallBuiltIn(function, parameter_names)
    )

    return NkScope(
        parent=parent,
        body_definition=body_definition,
        parameter_definition=parameter_definition,
        name=name, 
        is_builtin=True
    )
    
def get_builtins():
    builtins = [
        (name[len("nk_"):], fn)
        for name, fn in inspect.getmembers(BuiltIns)
        if name.startswith("nk_")
    ]

    return builtins

def inject_builtins(nk_scope):
    builtins = get_builtins()    

    for name, function in builtins:
        # create the builtin definitions:
        builtin = create_builtin(name, function, nk_scope)

        # finally, inject the builtin deferred scope:
        nk_scope.members[name] = builtin
        
class BuiltIns:

    stdlib_lookup = {
        "math.nk": rootpath + "/nk_stdlib/math.nk",
        "utest.nk": rootpath + "/nk_stdlib/utest.nk",
        "types.nk": rootpath + "/nk_stdlib/types.nk"
    }

    @staticmethod
    def nk_import(vm, filepath):
        # normalize the module name
        module_name = filepath.value

        if not module_name.endswith('.nk') and not module_name.endswith('.json'):
            module_name = module_name + ".nk"

        # allow standard library functions without fullpath:
        if module_name in BuiltIns.stdlib_lookup:
            module_name = BuiltIns.stdlib_lookup[module_name]

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
    def nk_open(vm, address, mode="r"):
        return NkStream(
            kind="file", 
            handle=open(address.value, mode.value)
        )

    @staticmethod
    def nk_connect(vm, address):
        host, port = address.value.split(":")
        s = socket.socket()
        s.connect((host, int(port)))

        return NkStream(
            kind="socket",
            handle=s
        )

    @staticmethod
    def nk_listen(vm, address):
        host, port = address.value.split(":")
        s = socket.socket()

        s.bind((host, int(port)))
        s.listen()

        return NkStream(
            kind="listenter",
            handle=s
        )

    @staticmethod
    def nk_accept(vm, listener):
        conn, _ = listener.handle.accept()

        return NkStream(
            kind="socket",
            handle=conn
        )

    @staticmethod
    def nk_read(vm, stream):
        if stream.kind == "file":
            return NkString(stream.handle.read())
        
        if stream.kind == "socket":
            return NkString(
                stream.handle.recv(4096).decode()
            )

        raise Exception(f"cannot read from {stream.kind}")
   
    @staticmethod
    def nk_write(vm, stream, value):
        if stream.kind == "file": 
            stream.handl.write(str(value.value))

            return
        
        if stream.kind == "socket":
            stream.handle.send(str(value.value).encode())

            return

        raise Exception(f"cannot write to {stream.kind}")

    @staticmethod
    def nk_close(vm, stream):
        stream.handle.close()

    @staticmethod
    def nk_hash(vm, value):
        data= repr(value).encode()

        return NkString(
            hashlib.sha256(data).hexdigest()
        )
