import json

class Deserializer:

    def __init__(self, source):
        self.source = json.loads(source)
    
    def deserialize(self, obj):
        method_name = f"deserialize_{obj.op_code}"
        deserializer = getattr(self, method_name)
        return deserializer(obj)

#########################################################
################### Deserialize Methods #################
#########################################################

    def deserialize_ScopeDefinition(self, definition):
        raise NotImplementedError()
        
    def deserialize_Constant(self, const):
        raise NotImplementedError()
        
    def deserialize_Load(self, instruction):
        raise NotImplementedError()

    def deserialize_LoadMember(self, instruction):
        raise NotImplementedError()

    def deserialize_Store(self, instruction):
        raise NotImplementedError()

    def deserialize_StoreMember(self, instruction):
        raise NotImplementedError()

    def deserialize_PushConst(self, instruction):
        raise NotImplementedError()

    def deserialize_CreateScope(self, instruction):
        raise NotImplementedError()

    def deserialize_CreateFunction(self, instruction):
        raise NotImplementedError()

    def deserialize_CreateList(self, instruction):
        raise NotImplementedError()

    def deserialize_CreateSet(self, instruction):
        raise NotImplementedError()

    def deserialize_Jump(self, instruction):
        raise NotImplementedError()

    def deserialize_JumpIfFalse(self, instruction):
        raise NotImplementedError()

