from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto

class NkValue: 

    def add(self, rhs):
        raise Exception(f"{type(self)} does not support add")

    def less_than(self, rhs):
        raise Exception(f"{type(self)} does not support less than")

class NkScope(NkValue):

    reserved_names = {
        "__name__",
        "__main__",
        "__scope__",
        "__file__", 
        "__parent__"
    }

    def __init__(
        self, 
        parent=None, 
        body_definition=None, 
        parameter_definition=None, 
        name=None, 
        is_file_scope=False, 
    ):
        self.parent = parent
        self.members = {}
        self.parameter_definition = parameter_definition
        self.body_definition = body_definition
        self.name = name
        self.aliases = set()

        self.return_value = NK_NONE

        self.is_file_scope = is_file_scope

        self.__initialize_default_members()

    def __initialize_default_members(self):
        # initialize reserved members:
        self.members["__scope__"] = self
        self.members["__name__"] = self.name
        self.members["__parent__"] = self.parent
        
        # the root filescope is the main scope (child of the builtins scope)
        if self.parent is not None and self.parent.parent is None:
            self.members["__main__"] = self

        if self.is_file_scope: 
            self.set_as_file_scope()

    def set_as_file_scope(self):
        self.members["__file__"] = self

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

    def resolve_local(self, name):
        if name in curr.members:
            return curr.members[name]

        raise Exception(f"{name} is not a member of {self.name}")

    def resolve_owner(self, name):
        curr = self
        
        while curr:
            if name in curr.members:
                return curr
            
            curr = curr.parent

        return None

    def assign(self, name, value):
        if name in NkScope.reserved_names:
            raise Exception(f"{name} is a reserved name, cannot assign {value} to it")

        self.members[name] = value

    def call(self, vm, arguments: NkList):
        # create the execution scope, which is a copy of this scope,
        # minus the current member state (the new execution scope
        # can also be thought of as a new instance of the definition)

        new_scope = NkScope(
            parent=self.parent, 
            body_definition=self.body_definition,
            parameter_definition=self.parameter_definition,
            name=self.name
        )
    
        # run the parameter definition:
        vm.execute(
            new_scope,
            self.parameter_definition
        )

        parameters = new_scope.unreserved_members
        
        # bind the arguments based on this scope's parameters
        bindings = self.__gather_argument_bindings(arguments.items, parameters)

        # overwrite all parameters with arguments:
        for name, value in bindings.items():
            new_scope.assign(name, value)

        # validate that all parameters have been assigned:
        for name, value in new_scope.unreserved_members.items():
            if value is NK_UNBOUND:
                raise Exception(f"name {name} is unbound for scope call {new_scope.name}")

        # execute on the vm:
        vm.execute(
            new_scope,
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

            for value in spread_candidate.items:
                expanded_arguments.append(
                    NkArgument(value, NK_UNBOUND)
                )
                new_boundary += 1

            expanded_arguments.extend(arguments[boundary:])
            return expanded_arguments, new_boundary

        return arguments, boundary

    def collect_to(self, obj):
        for name, value in self.unreserved_members.items():
            if isinstance(obj, NkList):
                obj.items.append(value)

            elif isinstance(obj, NkSet):
                obj.items.add(value)

            else: #NkScope:
                obj.assign(name, value)

            
        
class NkSet(NkValue):

    def __init__(self, items):
        self.items = []
        for item in items:
            self.add(item)

    def add(self, item):
        for existing_item in self.items:
            if existing_item == item:
                return

        self.items.append(item)

    def __repr__(self):
        return f"NkSet{self.items}"

    def __eq__(self, rhs):
        return (
            isinstance(rhs, (NkList, NkSet))
            and self.items == rhs.items
        )
        
    def collect_to(self, obj):
        for item in self.items:
            if isinstance(obj, NkList):
                obj.items.append(item)

            elif isinstance(obj, NkSet):
                obj.items.add(item)

            else: #NkScope:
                if isinstance(item, NkScope):
                    obj.assign(item.name, item)

class NkList(NkValue):

    def __init__(self, items):
        self.items = list(items)
    
    def __repr__(self):
        return f"NkList{self.items}"

    def __eq__(self, rhs):
        return (
            isinstance(rhs, (NkSet, NkList))
            and self.items == rhs.items
        )

    def collect_to(self, obj):
        for item in self.items:
            if isinstance(obj, NkList):
                obj.items.append(item)

            elif isinstance(obj, NkSet):
                obj.items.add(item)

            else: #NkScope:
                if isinstance(item, NkScope):
                    obj.assign(item.name, item)

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
    values: NkList

@dataclass(frozen=True)
class NkInt(NkValue): 
    value: int

    def add(self, rhs):
        if isinstance(rhs, NkInt):
            return NkInt(
                self.value + rhs.value
            )
        if isinstance(rhs, NkFloat):
            return NkFloat(
                self.value + rhs.value
            )

    def less_than(self, rhs):
        if isinstance(rhs, NkInt):
            if self.value < rhs.value: return NK_TRUE
            else: return NK_FALSE

@dataclass(frozen=True)
class NkFloat(NkValue):
    value: float

@dataclass(frozen=True)
class NkString(NkValue):
    value: str

@dataclass
class NkNone(NkValue): pass
    
@dataclass(frozen=True)
class NkNull(NkValue): pass

# used for argument binding:
@dataclass
class NkUnbound(NkValue): pass

# used for operator traps:
@dataclass
class NkUnresolved(NkValue): pass

@dataclass
class NkCollectAll(NkValue): pass

NK_NONE = NkNone()
NK_NULL = NkNull()
NK_UNBOUND = NkUnbound()
NK_FALSE = NkBool('false')
NK_TRUE = NkBool('true')
NK_UNRESOLVED = NkUnresolved()
NK_COLLECT_ALL = NkCollectAll()

