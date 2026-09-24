class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value

class CollectSignal(Exception):
    def __init__(self, value):
        self.value = value

class LeaveSignal(Exception): pass

class ContinueSignal(Exception): pass

class InvalidNameTarget(Exception): pass

class VariableUnresolvable(Exception): 
    def __init__(self, message):
        super().__init__(message)

class InvalidMemberAccess(Exception):
    def __init__(self, message):
        super().__init__(message)


