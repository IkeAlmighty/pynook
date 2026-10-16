



class Databall:
    def __init__(self):
        self.file = None
        self.source = None


        self.tokens = []
        self.ast = None
        self.ir = None

        self.errors = []
        self.warning = []

        self.events = []

        # arbitrary metadata:
        self.data = {}

