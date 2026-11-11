from dataclasses import dataclass
from runtime.values.core import NkValue, NkId
from runtime.operators import TypeFamily

class NkBool(NkValue):

    TYPE_ID = NkId("ac2e02cc-0b91-402b-aea2-f0e88c110a76")
    FAMILY = { TypeFamily.NUMERIC, TypeFamily.STRING }

    def __init__(self, value):
        super().__init__()
        if value == 'true': self.value = True
        elif value == 'false': self.value = False
        else: raise Exception(f"Invalid NkBool value {value}")

    def __repr__(self):
        return f"NkBool('{self.value}')"

    def eq(self, rhs):
        if rhs.value == lhs.value: 
            return NK_TRUE

        return NK_FALSE

    def add(self, rhs):
        if rhs.value == True or self.value == True:
            return NK_TRUE
        else:
            return NK_FALSE
            
NK_FALSE = NkBool('false')
NK_TRUE = NkBool('true')

