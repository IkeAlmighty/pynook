from dataclasses import dataclass
from runtime.values.core import NkValue, NkId

class NkBool(NkValue):

    TYPE_ID = NkId("ac2e02cc-0b91-402b-aea2-f0e88c110a76")

    def __init__(self, value):
        super().__init__()
        if value == 'true': self.value = True
        elif value == 'false': self.value = False
        else: raise Exception(f"Invalid NkBool value {value}")

    def eq(self, rhs):
        if rhs.value == lhs.value: 
            return NK_TRUE

        return NK_FALSE
            
NK_FALSE = NkBool('false')
NK_TRUE = NkBool('true')

