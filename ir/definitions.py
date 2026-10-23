from dataclasses import dataclass

class ScopeDefinition:

    indent_depth = -1

    def __init__(self, control_types = []):
        self.instructions = []
        self.control_types = control_types

    def __repr__(self):
        result = ""
        ScopeDefinition.indent_depth += 1
        indent = "\t" * ScopeDefinition.indent_depth

        for i, instruction in enumerate(self.instructions):
            result += f"\n{indent}{i}: {instruction}"

        ScopeDefinition.indent_depth -= 1
        return result + "\n"

@dataclass
class Constant:
    type_name: str
    value: object
