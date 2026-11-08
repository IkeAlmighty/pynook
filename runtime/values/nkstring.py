from dataclasses import dataclass
from runtime.operators import TypeFamily
from runtime.values.core import NkValue, NkId
from runtime.values.nkbool import NK_FALSE, NK_TRUE

class NkString(NkValue):

    TYPE_ID = "3ef3cea1-608c-4487-8ceb-ebd362f6c4f3"
    RANK = 50
    FAMILY = { TypeFamily.STRING }

    def __init__(self, value):
        self.value = value


    def eq(self, rhs):
        if self.value == rhs.value:
            return NK_TRUE

        return NK_FALSE


    
