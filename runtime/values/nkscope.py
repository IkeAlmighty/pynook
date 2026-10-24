from runtime.values.nkprimitives import NkValue, NkString, NkSpreadArgument, NkArgument, NK_NONE, NK_UNBOUND
from runtime.values.nkset import NkSet
from runtime.values.nklist import NkList
import ir.instructions as ir

class NkScope(NkValue):
    
    def __init__(
        self, 
        parent=None, 
        body_definition=None, 
        parameter_definition=None, 
        name=None, 
        is_file_scope=False,
        is_builtin=False
    ):
        self.parent = parent
        self.members = {}
        self.parameter_definition = parameter_definition
        self.body_definition = body_definition
        self.name = name
        self.aliases = set()
        self.is_file_scope = is_file_scope
        self.is_builtin = is_builtin

        self.reserved_names = {
            "__name__",
            "__main__",
            "__scope__",
            "__file__", 
            "__parent__"
        }

        if self.name: self.reserved_names.add(self.name)

        self.__initialize_default_members()

    def __initialize_default_members(self):
        # initialize reserved members:
        self.members["__scope__"] = self
        self.members["__parent__"] = self.parent
        if self.name:
            self.members["__name__"] = NkString(self.name)
            self.members[self.name] = self
        else:
            self.members["__name__"] = NK_NONE
        
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
            if name not in self.reserved_names:
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
        if name in self.members:
            return self.members[name]

        # TODO: once Exception System is fleshed out, there should
        # probably be an Exception here (using none for __access__ overload):
        return NK_NONE

    def resolve_owner(self, name):
        curr = self
        
        while curr:
            if name in curr.members:
                return curr
            
            curr = curr.parent

        return None

    def assign(self, name, value):
        if name in self.reserved_names:
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
            new_scope.parameter_definition
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

        # the end of a body definition should include a push of 
        # NK_NONE to the stack,
        # as a default return value. Control Flow Instructions will 
        # short circuit this by 
        # moving the instruction pointer past the end of the 
        # body_definition instructions:

        # TODO: replace the use of ir.instructions 
        # with completion analysis and direct vm calls:

        if not self.is_builtin:
            new_scope.body_definition.instructions.append(
                ir.PushConst(
                    ir.Constant(
                        type_name="none",
                        value=None
                    )
                )
            )

        # execute on the vm:
        vm.execute(
            new_scope,
            new_scope.body_definition
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
 
