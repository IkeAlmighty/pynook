from runtime.values.nkprimitives import NkValue

class NkStream(NkValue):

    def __init__(self, kind, handle):
        self.kind = kind
        self.handle = handle

