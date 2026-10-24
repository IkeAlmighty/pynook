from runtime.values.nkprimitives import NkValue, NkId

class NkList(NkValue):

    def __init__(self, items):
        self.items = list(items)
        self.members = {
            "__id__": NkId("c0e0630b-6ef9-4e0b-b2be-2b96079a7cdb")
        }
   
    def __repr__(self):
        return f"NkList{self.items}"

    def collect_to(self, obj):
        for item in self.items:
            if isinstance(obj, NkList):
                obj.items.append(item)

            elif isinstance(obj, NkSet):
                obj.items.add(item)

            else: #NkScope:
                if isinstance(item, NkScope):
                    obj.assign(item.name, item)


