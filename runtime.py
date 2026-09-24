from runtime_exceptions import *
from tokenizer import Tokenizer
from parser import Parser
from ast_executor import Executor
from runtime_objects import *
import os
import inspect

class Runtime:

    def __init__(self):
        self.working_dir = os.getcwd()
        self.filescope_registry = {}
        self.main_scope = RtScope(
            name="__main__", 
            parent=None, 
            scope_type=RtScope.Types.MAIN
        )

        self.assign_core_functions()
        
    def assign_core_functions(self):
        core_functions = {
            name[5:]: value
            for name, value in vars(Runtime).items()
            if name.startswith('nook_')
        }

        for name, func in core_functions.items():
            sig = inspect.signature(func)
            params = {}

            for param_name, param in sig.parameters.items():
                if param_name == 'self': continue

                # NoDefaultValue is used here so that python Nones can be preserved
                # in CoreFunction method signatures
                value = RtConstants.NoDefaultValue
                if param.default is not inspect.Parameter.empty:
                    value = param.default

                params[param_name] = value


            core_func = RtCoreFunction(
                name,
                params=params,
                func=func,
            )

            self.main_scope.assign(name, core_func)

    def resolve_filescope(self, fullpath):
        with open(fullpath) as f:
            source = f.read()

        tokenizer = Tokenizer(source)
        parser = Parser(tokenizer)
        ast = parser.file()

        module_name = os.path.basename(fullpath)

        executor = Executor(self)

        executor.name_hints.append("module." + module_name)

        try:
            scope = executor.dispatch(ast)
            return scope
        
        finally:
            executor.name_hints.pop()
            executor.scope_stack.pop()


    ##########################################################
    ##### CORE FUNCTIONS LIVE HERE AND START WITH nook_ ######
    ##########################################################

    def nook_import(self, relative_path, dest_scope=None):

        # normalize relative path:
        if not (relative_path.endswith(".nk") or relative_path.endswith(".json")):
            relative_path += ".nk"

        fullpath = os.path.abspath(
            os.path.join(self.working_dir, relative_path)
        )

        # check that filescope has not been imported before!
        if fullpath not in self.filescope_registry:
            self.filescope_registry[fullpath] = 1 # FIXME this is fragile! 
            scope = self.resolve_filescope(fullpath)
            self.filescope_registry[fullpath] = scope

        module_scope = self.filescope_registry[fullpath]

        if dest_scope:
            module_scope.collect_to(dest_scope)

        return module_scope


    def nook_print(self, message):
        print(message)

    def nook_open(self, filepath):
        pass
