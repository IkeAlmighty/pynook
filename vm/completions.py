from ir.builder import RETURN_DEST, LEAVE_DEST, CONTINUE_DEST, COLLECT_DEST, THROW_DEST 
from runtime.values import NK_COLLECT_ALL, NK_NONE

class ThrowCompletion:
    
    def __init__(self, value):
        self.value = value

    def apply(self, vm):
        if THROW_DEST in vm.frame.control_types:
            # skip over the catch jump instruction:
            # (has to skip the Pop for the try as well as the Jump)
            vm.frame.ip = vm.frame.ip + 2 # skipping the original Pop, Jump
            vm.stack.append(self.value) # append Throw value to stack

        else: 
            vm.frame.completion = self
            vm.frame.ip = len(
                vm.frame.definition.instructions
            )

class ReturnCompletion:

    def __init__(self, value):
        self.value = value

    def apply(self, vm):
        if RETURN_DEST not in vm.frame.control_types:
            vm.frame.completion = self

            vm.frame.ip = len(
                vm.frame.definition.instructions
            )

        else:
            vm.stack.append(self.value)

class CollectCompletion:

    def __init__(self, value, scope):
        self.value = value
        self.scope = scope

    def apply(self, vm):

        if COLLECT_DEST not in vm.frame.control_types:
            vm.frame.completion = self

            vm.frame.ip = len(
                vm.frame.definition.instructions
            )

        else:
            if self.value == NK_COLLECT_ALL:
                vm.stack.append(NK_NONE)

                # promote all members:
                for name in self.scope.unreserved_members:
                    owner = vm.frame.scope.resolve_owner(name)
                    if owner:
                        owner.assign(name, self.scope.resolve(name))
            else:
                vm.stack.append(self.value)


class LeaveCompletion:

    def apply(self, vm):
        if LEAVE_DEST not in vm.frame.control_types:
            vm.frame.completion = self

            vm.frame.ip = len(
                vm.frame.definition.instructions
            )

class ContinueCompletion: 

    def apply(self, vm):
        if CONTINUE_DEST not in vm.frame.control_types:
            vm.frame.completion = self

            vm.frame.ip = len(
                vm.frame.definition.instructions
            )

class NormalCompletion: 
    def apply(self, vm): pass


