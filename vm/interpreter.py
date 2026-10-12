from __future__ import annotations
from ir.instructions import *
from runtime.values import *
from ir.builder import RETURN_DEST, LEAVE_DEST, CONTINUE_DEST, COLLECT_DEST, COLLECT_RESOLVABLE_MEMBERS 

class VirtualMachine:

    def __init__(self):
        self.stack = []

        self.frames = []

        self.ins_lookup = {
            Load: self.Load,
            LoadMember: self.LoadMember,
            LoadSlice: self.LoadSlice,
            Store: self.Store,
            StoreMember: self.StoreMember,
            PushConst: self.PushConst,
            CreateScope: self.CreateScope,
            CreateFunction: self.CreateFunction,
            CreateArgument: self.CreateArgument,
            CreateList: self.CreateList,
            CreateSet: self.CreateSet,
            SpreadTerm: self.SpreadTerm,
            Call: self.Call,
            CallBuiltIn: self.CallBuiltIn,
            Collect: self.Collect,
            Leave: self.Leave,
            Return: self.Return,
            Equal: self.Equal,
            JumpIfFalse: self.JumpIfFalse,
            Jump: self.Jump,
            Add: self.Add,
            LessThan: self.LessThan
        }

        
    def materialize(self, constant):
        type_name = constant.type_name
        value = constant.value

        if type_name == "int": 
            return NkInt(int(value))
            
        elif type_name == "string": 
            return NkString(str(value))
            
        elif type_name == "float": 
            return NkFloat(float(value))
            
        elif type_name == "boolean": 
            return NkBool(value)
            
        elif type_name == "hexadecimal": 
            return NkInt(int(value))
            
        elif type_name == "binary": 
            return NkInt(int(value))
            
        elif type_name == "none": 
            return NK_NONE
            
        elif type_name == "null": 
            return NK_NULL
            
        elif type_name == "unbound": 
            return NK_UNBOUND

        elif type_name == "collectall":
            return NK_COLLECT_ALL

        else:
            raise Exception(f"no materialize branch for {type_name}")
            
    @property
    def frame(self):
        return self.frames[-1]

    def execute(self, scope, definition):
        frame = Frame(scope, definition)
        try:
            self.frames.append(frame)

            instructions = definition.instructions

            while frame.ip < len(instructions):
                instruction = instructions[frame.ip]
                frame.ip += 1
                self.ins_lookup[type(instruction)](instruction)

        finally:

            # first, promote any resolvable members in this
            # frame's scope to their owners:

            # TODO: right now, collect only works inside of scopes. 
            # the original idea was to allow it inside of nested lists and 
            # nested sets. This can be done by restructuring the parse tree
            # output and defining lists and sets as scopes with '[' ... ']' 
            # instead of '{' ... '}'

            # At that point, NkScope.collect_to should also be examined to 
            # see if it is a better fit here:
            if COLLECT_RESOLVABLE_MEMBERS in definition.control_types:
                for name in frame.scope.unreserved_members:
                    owner = frame.scope.parent.resolve_owner(name)
                    if owner:
                        owner.assign(name, frame.scope.resolve(name))

            # then, apply the completion type and pop the frame:
            completion = frame.completion 
            self.frames.pop() 

            if self.frames:
                completion.apply(self)

    ###################################################################################
    ##########                  Instruction Implementations                 ###########
    ###################################################################################

    def PushConst(self, inst):
        const = inst.value
        value = self.materialize(const)
        self.stack.append(value)

    def Store(self, inst):
        value = self.stack.pop()

        if isinstance(value, NkScope):
            # assign name if the scope doesn't have one
            if value.name is None:
                value.name = inst.name

            value.aliases.add(inst.name)

        self.frame.scope.assign(inst.name, value)

    def StoreMember(self, inst):
        name = inst.name
        owner = self.stack.pop()
        value = self.stack.pop()

        if isinstance(value, NkScope):
            # assign name if the value doesn't have one
            if value.name is None:
                value.name = inst.name

            value.aliases.add(inst.name)
        
        owner.assign(name, value)

    def Load(self, inst):
        """
        loads the instruction's value onto the stack. 
        """
        value = self.frame.scope.resolve(inst.name)
        self.stack.append(value)

    def LoadMember(self, inst):
        """
        loads the a member of the instruction's value onto the stack.
        """
        owner = self.stack.pop()
        key = inst.value
        member = None

        if key.isnumeric(): # for integers:
            if isinstance(owner, NkList):
                member = owner.items[int(key)]
            else: 
                raise Exception(f"{type(owner)} is not indexable")

        else: # for strings and identifiers:
            if isinstance(owner, NkScope):
                member = owner.resolve_local(key)
            else:
                raise Exception(f"{type(owner)} is not subscriptable")
        
        self.stack.append(member)

    def LoadSlice(self, inst):
        value = self.stack.pop()

        if not isinstance(value, NkList):
            raise Exception(f"{value} is not a list")
        
        start, end = 0, len(value.items)
        if inst.start: start = int(inst.start)
        if inst.end: end = int(inst.end)

        items = value.items[start:end]

        self.stack.append(NkList(items))

    def JumpIfFalse(self, inst):
        value = self.stack.pop()
        if value == NK_FALSE: self.frame.ip = inst.target

    def Jump(self, inst):
        self.frame.ip = inst.target

    def CreateScope(self, inst):
        """
        creates a nkscope, immediately executes it, and pushes the 
        nkscope to the stack.
        """
        scope = NkScope(
            parent=self.frame.scope, 
            body_definition=inst.definition,
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
            parameter_definition=inst.parameter_definition,
        )

        self.stack.append(function)

    def CreateList(self, inst):
        items = []
        for i in range(inst.length):
            items.append(self.stack.pop())

        items.reverse()

        nk_list = NkList(items)
        self.stack.append(nk_list)

    def CreateSet(self, inst):
        items = []
        for i in range(inst.length):
            items.append(self.stack.pop())

        items.reverse()

        nk_set = NkSet(items)
        self.stack.append(nk_set)

    def Call(self, inst):
        """
        pops a NkScope off the stack, and a list of NkArgument off the stack.
        executes NkScope.call with the NkArguments obj as the argument.
        """

        # pop NkScope off the stack
        scope = self.stack.pop()

        # pop the arguments off the stack
        arguments = self.stack.pop()

        # execute NkScope.call with arguments passed in
        scope.call(self, arguments)

    def CallBuiltIn(self, inst):
        function = inst.function

        # arguments are already bound to correct parameter names.
        arg_names = inst.parameter_names
        arguments = []
        for name in arg_names:
            arguments.append(self.frame.scope.resolve(name))
        
        result = function(self, *arguments)
        self.stack.append(result)

    def CreateArgument(self, inst):
        value = self.stack.pop()
        bind_to = (
            inst.bind_to
            if inst.bind_to is not None
            else NK_UNBOUND
        )

        argument = NkArgument(value, bind_to)
        self.stack.append(argument)

    def CreateSpreadArgument(self, inst):
        value = self.stack.pop()
        if not isinstance(value, NkList):
            raise Exception("spread argument requires a list")

        spread_argument = NkSpreadArgument(value)

        self.stack.append(spread_argument)

    def SpreadTerm(self, inst):
        obj = self.stack.pop()

        valid_types = (NkList, NkScope, NkSet)
        if not isinstance(obj, valid_types):
            raise Exception("invalid spread term, must be a list, scope, or set.")

        obj.collect_to(self.frame.scope)

    def Equal(self, inst):
        rhs = self.stack.pop()
        lhs = self.stack.pop()

        if rhs == lhs:
            self.stack.append(NK_TRUE)
        else:
            self.stack.append(NK_FALSE)

    def Return(self, inst):
        return_value = self.stack.pop()
        
        # set the completion status:
        self.frame.completion = ReturnCompletion(return_value)

        # jump to end of this stack's instruction list:
        self.frame.ip = len(
            self.frame.definition.instructions
        )

    def Collect(self, inst):
        collect_value = self.stack.pop()
        
        # set the completion status:
        self.frame.completion = CollectCompletion(collect_value, self.frame.scope)

        # jump to end of this stack's instruction list:
        self.frame.ip = len(
            self.frame.definition.instructions
        )

    def Leave(self, inst):

        # set the completion status:
        self.frame.completion = LeaveCompletion()

        # jump to end of this stack's instruction list:
        self.frame.ip = len(
            self.frame.definition.instructions
        )

    def Subtract(self, inst): 
        raise NotImplementedError()

    def Add(self, inst): 
        rhs = self.stack.pop()
        lhs = self.stack.pop()

        self.stack.append(
            lhs.add(rhs)
        )

    def Divide(self, inst): 
        raise NotImplementedError()

    def Multiply(self, inst): 
        raise NotImplementedError()

    def Exponent(self, inst): 
        raise NotImplementedError()

    def Modulo(self, inst): 
        raise NotImplementedError()

    def Xor(self, inst): 
        raise NotImplementedError()

    def BwAnd(self, inst): 
        raise NotImplementedError()

    def BwOr(self, inst): 
        raise NotImplementedError()

    def And(self, inst): 
        raise NotImplementedError()

    def Or(self, inst): 
        raise NotImplementedError()

    def GreaterThanOrEqual(self, inst): 
        raise NotImplementedError()

    def LessThanOrEqual(self, inst): 
        raise NotImplementedError()

    def LessThan(self, inst): 
        rhs = self.stack.pop()
        lhs = self.stack.pop()

        self.stack.append(lhs.less_than(rhs))

    def GreaterThan(self, inst): 
        raise NotImplementedError()


##########################################
############ Helper Classes ##############
##########################################

class Frame:

    def __init__(self, scope, definition):
        self.scope = scope
        self.definition = definition
        self.ip = 0

        self.completion = NormalCompletion()
        self.control_types = definition.control_types or []

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


