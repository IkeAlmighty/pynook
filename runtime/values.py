from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto

class NkValue: pass

class NkScope(NkValue):

    reserved_names = {
        "__name__",
        "__main__",
        "__scope__",
        "__file__"
    }

    def __init__(self, parent=None, body_definition=None, parameter_definition=None, name=None):
        self.parent = parent
        self.members = {}
        self.parameter_definition = parameter_definition
        self.body_definition = body_definition
        self.name = name
        self.aliases = set()

    @property
    def unreserved_members(self):
        result = {}
        for name, value in self.members.items():
            if name not in NkScope.reserved_names:
                if not name.startswith('___'):
                    result[name] = value

        return result

    def resolve(self, name):
        curr = self

        while curr:
            if name in curr.members:
                return curr.members[name]
            
            curr = curr.parent

        raise Exception(f"{name} cannot be resolved")

    def assign(self, name, value):
        if name in NkScope.reserved_names:
            raise Exception(f"{name} is a reserved name, cannot assign {value} to it")

        self.members[name] = value

    def call(self, vm, arguments: list[NkArgument | NkSpreadArgument]):
        # create the execution scope, which is a copy of this scope,
        # minus the current member state (the new execution scope
        # can also be thought of as a new instance of the definition)

        execution_scope = NkScope(
            parent=self.parent, 
            body_definition=self.body_definition,
            parameter_definition=self.parameter_definition,
            name=self.name
        )
    
        # run the parameter definition:
        vm.execute(
            execution_scope,
            self.parameter_definition
        )

        parameters = execution_scope.unreserved_members
        
        # bind the arguments based on this scope's parameters
        bindings = self.__gather_argument_bindings(arguments, parameters)

        # overwrite all parameters with arguments:
        for name, value in bindings.items():
            execution_scope.assign(name, value)

        # validate that all parameters have been assigned:
        for name, value in execution_scope.unreserved_members.items():
            if value is NK_UNBOUND:
                raise Exception(f"name {name} is unbound for scope call {execution_scope.name}")

        # execute on the vm:
        vm.execute(
            execution_scope,
            self.body_definition
        )

    def __gather_argument_bindings(self, arguments, parameters):
        bindings = {}

        # find partition boundary for named vs unnamed arguments:
        boundary = self.__find_argument_partition(arguments)
        
        # validate that all arguments after partition have bind_to:
        self.__validate_bindto_arguments(arguments[boundary:])

        # validate spread argument position is the last element before boundary:
        self.__validate_spread_position(arguments[:boundary])

        # expand the last argument before the boundary if it is a RestArgument:
        arguments, boundary = self.__expand_spread_argument(arguments, boundary)

        # validate that the correct number of arguments was given:
        if boundary > len(parameters):
            # TODO: needs fixed to account for spread parameters
            raise Exception(f"too many arguments for call to {self.name}")

        # map unbound arguments onto parameters in order:
        parameter_names = list(parameters.keys())
        for argument, parameter_name in zip(arguments[:boundary], parameter_names):
            bindings[parameter_name] = argument.value

        # map bind_to arguments to their correct binding:
        for argument in arguments[boundary:]:
            if argument.bind_to in bindings:
                raise Exception(f"parameter {argument.bind_to} supplied twice.")

            if argument.bind_to not in parameters:
                raise Exception(f"{self.name} has no parameter named {argument.bind_to}")

            bindings[argument.bind_to] = argument.value
        
        return bindings

    def __find_argument_partition(self, arguments):
        for i, arg in enumerate(arguments):
            # skips over NkSpreadArgument as they cannot be bound:
            if isinstance(arg, NkArgument):

                # return i as boundary once the boundary is found:
                if arg.bind_to is not NK_UNBOUND: 
                    return i

        return len(arguments)

    def __validate_bindto_arguments(self, named_partition):
        for arg in named_partition:

            if isinstance(arg, NkSpreadArgument):
                raise Exception("Argument spreads must be the last element before named arguments")

            if arg.bind_to is NK_UNBOUND:
                raise Exception("unnamed arguments must come before named arguments")

    def __validate_spread_position(self, arguments):
        for arg in arguments[:-1]:
            if isinstance(arg, NkSpreadArgument):
                raise Exception("Argument spreads must be the last element before named arguments")

    def __expand_spread_argument(self, arguments, boundary):
        if boundary == 0: return arguments, boundary

        expanded_arguments = arguments[:boundary - 1]
        spread_candidate = arguments[boundary - 1]

        if isinstance(spread_candidate, NkSpreadArgument):
            new_boundary = len(expanded_arguments)

            for value in spread_candidate.values:
                expanded_arguments.append(
                    NkArgument(value, NK_UNBOUND)
                )
                new_boundary += 1

            expanded_arguments.extend(arguments[boundary:])
            return expanded_arguments, new_boundary

        return arguments, boundary
        
class NkSet(NkValue):

    def __init__(self, value):
        self.value = set(value)
    
    def __repr__(self):
        return f"NkSet{self.value}"

    def __eq__(self, rhs):
        return self.value == rhs.value

class NkList(NkValue):

    def __init__(self, value):
        self.value = list(value)
    
    def __repr__(self):
        return f"NkList{self.value}"

    def __eq__(self, rhs):
        return self.value == rhs.value

class NkBool(NkValue):

    def __init__(self, value):
        if value == 'true': self.value = True
        elif value == 'false': self.value = False
        else: raise Exception(f"Invalid NkBool value {value}")
    
    def __repr__(self):
        return "NkBool(true)" if self.value else "NkBool(false)"

    def __eq__(self, rhs):
        return self.value == rhs.value

@dataclass
class NkArgument:
    value: NkValue
    bind_to: str | NkUnbound

@dataclass
class NkSpreadArgument:
    values: list[NkValue]

@dataclass
class NkInt(NkValue): 
    value: int

@dataclass
class NkFloat(NkValue):
    value: float

@dataclass
class NkString(NkValue):
    value: str

@dataclass
class NkNone(NkValue): pass
    
@dataclass
class NkNull(NkValue): pass

@dataclass
class NkUnbound(NkValue): pass

NK_NONE = NkNone()
NK_NULL = NkNull()
NK_UNBOUND = NkUnbound()
