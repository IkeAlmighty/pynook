
class ScopeDefinition:

    def __init__(self):
        self.instructions = []

    def __repr__(self):
        return "\n".join(
            f"{i}: {instruction}" 
            for i, instruction in enumerate(
                self.instructions
            )
        )
