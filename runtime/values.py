from enum import Enum, auto

class NkValue: pass

class NkScope(NkValue):

    def __init__(self, parent=None, definition=None, parameters=None):
        self.parent = parent
        self.members = {}
        self.parameters = parameters
        self.definition = definition

    def resolve(self, name):
        curr = self

        while curr:
            if name in curr.members:
                return curr.members[name]
            
            curr = curr.parent

        raise Exception(f"{name} cannot be resolve")

    def assign(self, name, value):
        self.members[name] = value

    def call(self): pass

class NkInt(NkValue): 

    def __init__(self, value):
        self.value = int(value)
    
    def __repr__(self):
        return f"NkInt{self.value}"

class NkFloat(NkValue):

    def __init__(self, value):
        self.value = float(value)
    
    def __repr__(self):
        return f"NkFloat{self.value}"

class NkString(NkValue):

    def __init__(self, value):
        self.value = str(value)
    
    def __repr__(self):
        return f"NkString{self.value}"

class NkSet(NkValue):

    def __init__(self, value):
        self.value = set(value)
    
    def __repr__(self):
        return f"NkSet{self.value}"

class NkList(NkValue):

    def __init__(self, value):
        self.value = list(value)
    
    def __repr__(self):
        return f"NkList{self.value}"

class NkBool(NkValue):

    def __init__(self, value):
        if value == 'true': self.value = True
        elif value == 'false': self.value = False
        else: raise Exception(f"Invalid NkBool value {value}")
    
    def __repr__(self):
        return f"NkBool{self.value[0].upper()}{self.value[1:]}"

class NkNone(NkValue):
    def __repr__(self):
        return "NkNone"

class NkNull(NkValue):
    def __repr__(self):
        return "NkNull"
