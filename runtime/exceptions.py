from runtime.values import NkScope, NkString

class NkRuntimeException(Exception):

    def create_nk_value(exc_type, message, parent=None):

        nkscope = NkScope(parent=parent)
        
        nkscope.assign("message", NkString(message))
        nkscope.assign("type", NkString(exc_type))

        return nkscope


    def __init__(self, exc_type, message=None):
        super().__init__(message)
        self.exc_type = exc_type
        self.message = message
    
