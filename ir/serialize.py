
class IRSerializer:

    def serialize(self, obj):
        method_name = f"serialize_{obj.__class__.__name__}"
        serializer = getattr(self, method_name)
        return serializer(obj)

    #####################################################
    ##             Serializer Methods                  ##
    #####################################################


    def serialize_ScopeDefinition(self, definition):
        result = []
        for instruction in definition.instructions:
            serialization = self.serialize(instruction)
            serialization["op_code"] = instruction.__class__.__name__
            result.append(serialization)

        return result

    def serialize_Constant(self, const):
        return {
            "type": const.type_name,
            "value": const.value
        }

    def serialize_Load(self, instruction):
        return {
            "name": instruction.name
        }

    def serialize_LoadMember(self, instruction):
        return {
            "name": instruction.name
        }

    def serialize_Store(self, instruction):
        return {
            "name": instruction.name
        }

    def serialize_StoreMember(self, instruction):
        return {
            "name": instruction.name
        }

    def serialize_PushConst(self, instruction):
        return {
            "value": self.serialize(instruction.value)
        }

    def serialize_CreateScope(self, instruction):
        return {
            "definition": self.serialize(instruction.definition)
        }

    def serialize_CreateFunction(self, instruction):
        return {
            "body_definition": self.serialize(
                instruction.body_definition
            ),
            "parameter_definition": self.serialize(
                instruction.parameter_definition
            )
        }

    def serialize_CreateList(self, instruction):
        return {
            "length": instruction.length
        }

    def serialize_CreateSet(self, instruction):
        return {
            "length": instruction.length
        }

    def serialize_Jump(self, instruction):
        return {
            "target": instruction.target
        }

    def serialize_JumpIfFalse(self, instruction):
        return {
            "target": instruction.target
        }

