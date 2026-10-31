from runtime.values.core import NkValue, NkId
from runtime.operators import TypeFamily
from runtime.values.nkbool import NK_TRUE, NK_FALSE

class NkInt(NkValue): 
    TYPE_ID = "882b5545-cb21-4875-94ac-134ab8e055e5"
    FAMILY = TypeFamily.NUMERIC

    def __init__(self, value):
        super().__init__()
        self.value = value

    def eq(self, rhs):
        if self.value == rhs.value:
            return NK_TRUE
        else:
            return NK_FALSE

    def add(self, rhs):
        return NkInt(self.value + rhs.value)

    
