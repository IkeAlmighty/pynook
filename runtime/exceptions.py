
class NkRuntimeException(Exception):

    def __init__(self, exc_type, message=None):
        super().__init__(message)
        self.exc_type = exc_type
        self.message = message
    
