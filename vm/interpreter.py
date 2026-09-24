from ir.instructions import *
from runtime.values import NkScope

class VM:

    def __init__(self):
        self.stack = []
        self.scope = NkScope()
        self.ins_lookup = {
            Load: self.Load,
            Store: self.Store,
            PushConst: self.PushConst
            CreateScope: self.CreateScope
            CreateFunction: self.CreateFunction
        }

    def execute(self, definition):
        for instruction in definition.instructions:
            self.ins_lookup[type(instruction)](instruction)

    def PushConst(self, inst):
        self.stack.append(inst.value)

    def Store(self, inst):
        value = self.stack.pop()
        self.scope.assign(inst.value, value)

    def Load(self, inst):
        """
        Loads the instruction's value onto the stack. 
        """
        value = self.scope.resolve(inst.value)
        self.stack.append(value)

    def CreateScope(self, inst):
        """
        Creates a NkScope, immediately executes it, and pushes the 
        NkScope to the stack.
        """
        new_scope = NkScope(
            parent=self.scope
            definition=inst.definition
        )

        previous_scope = self.scope

        self.scope = new_scope

        try:
            self.execute(inst.definition)
        finally:
            self.scope = previous_scope

        self.stack.append(new_scope)
    
    def CreateFunction(self, inst):
        """
        Creates a NkScope, pushes it to the stack.
        """
        function = NkScope(
            parent=self.scope
            definition=inst.definition,
            parameters=inst.parameters
        )

        self.stack.append(function)
