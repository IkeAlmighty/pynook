from debug.location import Location

class TokenizerState:

    def __init__(self, source, file=None):
        self.file = file
        self.source = source

        self.pos = 0
        self.col = 1
        self.row = 1

        self.curr_char = (
            source[0]
            if source
            else None
        )

        self.newline_flag = False

    def advance(self):
        self.pos += 1
        self.col += 1
        if self.pos >= len(self.source):
            self.curr_char = None
            return

        if self.newline_flag:
            self.newline_flag = False
            self.col = 1
            self.row += 1

        self.curr_char = self.source[self.pos]
        if self.curr_char == '\n':
            self.newline_flag = True

    def peek(self, offset: int):
        if self.pos + offset >= len(self.source):
            return None

        return self.source[self.pos + offset]

    def snapshot(self):
       """
         Takes a snapshot of the current tokenizer state.
       """
       snap = TokenizerState(self.source)
       snap.pos = self.pos
       snap.row = self.row
       snap.col = self.col
       snap.curr_char = self.curr_char

       return snap

    def restore(self, tokenizer_state):
        """
        Sets the values of the tokenizer to match values of another
        """
        self.pos = tokenizer_state.pos
        self.col = tokenizer_state.col
        self.row = tokenizer_state.row
        self.curr_char = tokenizer_state.curr_char

    @property
    def location(self):
        return Location(
            row=self.row,
            col=self.col,
            file=self.file,
            pos=self.pos
        )
