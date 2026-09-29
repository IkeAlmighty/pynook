from ir.instructions import *
from runtime.values import NkScope

class Frame:

    def __init__(self, scope, definition):
        self.scope = scope
        self.definition = definition
        self.ip = 0

class vm:

    def __init__(self):
        self.stack = []

        self.frames = []

        self.ins_lookup = {
            Load: self.Load,
            Store: self.Store,
            PushConst: self.PushConst,
            CreateScope: self.CreateScope,
            CreateFunction: self.CreateFunction
        }

    @property
    def frame(self):
        return self.frames[-1]

    def execute(self, scope, definition):
        try:
            frame = Frame(scope, definition)
            self.frames.append(frame)

            instructions = definition.instructions

            while frame.ip < len(instructions):
                instruction = instructions[frame.ip]
                self.ins_lookup[type(instruction)](instruction)
                frame.ip += 1

        finally:
            self.frames.pop() 

    def PushConst(self, inst):
        self.stack.append(inst.value)

    def Store(self, inst):
        value = self.stack.pop()

        if isinstance(value, NkScope):
            # assign name if the scope doesn't have one
            if value.name is None:
                value.name = inst.name

            value.aliases.add(inst.name)

        self.frame.scope.assign(inst.name, value)

    def Load(self, inst):
        """
        loads the instruction's value onto the stack. 
        """
        value = self.frame.scope.resolve(inst.name)
        self.stack.append(value)

    def CreateScope(self, inst):
        """
        creates a nkscope, immediately executes it, and pushes the 
        nkscope to the stack.
        """
        scope = NkScope(
            parent=self.frame.scope, 
            body_definition=inst.definition
        )
        
        self.execute(scope, inst.definition)

        self.stack.append(scope)
    
    def CreateFunction(self, inst):
        """
        creates a NkScope, pushes it to the stack.
        """
        function = NkScope(
            parent=self.frame.scope,
            body_definition=inst.body_definition,
            parameter_definition=inst.parameter_definition
        )

        self.stack.append(function)
