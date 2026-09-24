from runtime_exceptions import *
from enum import Enum, auto

class RtConstants(Enum):
    NoneValue = auto()
    NullValue = auto()
    UnboundValue = auto()
    NoDefaultValue = auto()

class RtFunction:

    def __init__(self, name, params, scope_type, scope_node, closure_scope):
        self.name = name
        self.params = params
        self.scope_type = scope_type
        self.scope_node = scope_node
        self.closure_scope = closure_scope

class RtCoreFunction:

    def __init__(self, name, params, func):
        self.name = name 
        self.params = params
        self.func = func
        self.scope_type = RtScope.Types.FUNCTION_BODY

class RtSpreadParam:

    def __init__(self, name):
        self.name = name

class RtScope:

    class Types(Enum):

        MAIN = auto()
        FILE = auto()
        OBJECT = auto()

        FUNCTION_BODY = auto()
        ROOT_FUNCTION_BODY = auto()

        FUNCTION_ARGS = auto()

        SWITCH_ARGS = auto()
        SWITCH_BODY = auto()

        LOOP_ARGS = auto()
        LOOP_BODY = auto()

        IF_BODY = auto()
        ELSE_BODY = auto()

        CASE_BODY = auto()
        DEFAULT_BODY = auto()

        TRY_BODY = auto()

        CATCH_ARGS = auto()
        CATCH_BODY = auto()

        FINALLY_BODY = auto()

    COLLECT_CATCHER_TYPES = (
        Types.FILE,
        Types.OBJECT,
        Types.FUNCTION_BODY, 
        Types.ROOT_FUNCTION_BODY, 
        Types.SWITCH_BODY
    )

    # control refers to leave and continue catchers
    CONTROL_CATCHER_TYPES = (
        Types.LOOP_BODY,
        Types.SWITCH_BODY,
    )

    RETURN_CATCHER_TYPES = (
        Types.FILE,
        Types.OBJECT,
        Types.FUNCTION_BODY,
        Types.ROOT_FUNCTION_BODY
    )

    ARG_TYPES = (
        Types.FUNCTION_ARGS,
        Types.SWITCH_ARGS,
        Types.LOOP_ARGS,
        Types.CATCH_ARGS
    )

    RESERVED_NAMES = (
        "__scope__",
        "__name__",
        "__main__", 
        "__file__"
    )

    def __init__(self, name, parent, scope_type, ast_node=None, main_scope=None):
        self.name = f"{name}"
        self.fullname = f"{name}-{str(scope_type.name)}"
        self.parent = parent
        self.scope_type = scope_type
        self.ast_node = ast_node
        self.variables = {}
        self.main_scope = main_scope
        self.return_value = RtConstants.NoneValue

        if scope_type != RtScope.Types.MAIN and main_scope is None:
            raise Exception("main_scope must be defined for non-main scopes")

        if scope_type == RtScope.Types.MAIN:
            if main_scope is not None:
                raise Exception("main_scope should not be initialized for scopes of type MAIN")

            self.main_scope = self

        if scope_type == RtScope.Types.FILE:
            self.variables["__file__"] = self

        self.variables["__scope__"] = self
        self.variables["__name__"] = self.name
        self.variables["__main__"] = main_scope

    def assign(self, name, value):
        if name in RtScope.RESERVED_NAMES:
            message = f"'{name}' is a reserved member that cannot be assigned to"
            raise RuntimeException(message)

        self.variables[name] = value 

    def collect_to(self, dest_scope, target=None):
        # if collecting just a single value, collect it
        # an then return:
        if target and target not in RtScope.RESERVED_NAMES:
            value = self.variables[target]
            dest_scope.assign(target, value)
            return

        # collect all variables from this scope to the destination 
        # scope:
        for name, value in self.variables.items():
                
            if name in RtScope.RESERVED_NAMES:
                continue

            dest_scope.assign(name, value) 

    def resolve(self, name):
        curr = self

        while name not in curr.variables:
            curr = curr.parent
            if curr is None:
                message = f"'{name}' cannot be resolved"
                raise VariableUnresolvable(message)

        return curr.variables[name]

    def get_unbound_vars(self):
        unbound_vars = []
        for name, value in self.variables.items():
            if value == RtConstants.UnboundValue:
                unbound_vars.append(name)

        return unbound_vars

class RtException(RtScope):

    def __init__(self, name, parent, main_scope):
        super().__init__(
            name, 
            parent, 
            RtScope.Types.EXCEPTION, 
            main_scope
        )

