from runtime.values.core import NkValue, NkId
from runtime.values.nkbool import NK_FALSE, NK_TRUE

class NkList(NkValue):

    def __init__(self, items):
        self.items = list(items)
        self.members = {
            "__typeid__": NkId("c0e0630b-6ef9-4e0b-b2be-2b96079a7cdb")
        }
   
    def __repr__(self):
        return f"NkList{self.items}"

    def contains(self, item):
        for a in self.items:
            if a.eq(item) == NK_TRUE:
                return NK_TRUE

        return NK_FALSE

    def eq(self, rhs):
        for a, b in zip(self.items, rhs.items):
            if a.eq(b) == NK_FALSE:
                return NK_FALSE

        return NK_TRUE

    def collect_to(self, obj):
        for item in self.items:
            if isinstance(obj, NkList):
                obj.items.append(item)

            elif isinstance(obj, NkSet):
                obj.items.add(item)

            else: #NkScope:
                if isinstance(item, NkScope):
                    obj.assign(item.name, item)


