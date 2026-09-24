from ir.definitions import ScopeDefinition
from ir.instructions import *
from runtime.values import NkInt

class IRBuilder:

    def __init__(self):
        self.definition_stack = [ScopeDefinition()]

    def build(self, ast):
        self.dispatch(ast)
        return self.definition_stack[0]

    @property
    def curr_scope(self):
        return self.definition_stack[-1]

    def emit(self, instruction):
        self.curr_scope.instructions.append(instruction)

    def dispatch(self, node):
        method_name = f"visit_{node.__class__.__name__}"
        method = getattr(self, method_name)
        return method(node)

    #####################################################
    ##                 VISITOR METHODS                 ##
    #####################################################

    def visit_Scope(self, node):
        definition = ScopeDefinition()

        self.definition_stack.append(definition)

        try:
            self.dispatch(node.block)
        finally:
            self.definition_stack.pop()

        self.emit(CreateScope(definition))

    def visit_Block(self, node):
        for statement in node.statements:
            self.dispatch(statement)
    
    def visit_List(self, node):
        raise NotImplementedError()

    def visit_Set(self, node):
        raise NotImplementedError()

    def visit_Leave(self, node):
        raise NotImplementedError()

    def visit_Continue(self, node):
        raise NotImplementedError()

    def visit_Collect(self, node):
        raise NotImplementedError()

    def visit_Return(self, node):
        raise NotImplementedError()

    def visit_Ignore(self, node):
        raise NotImplementedError()

    def visit_Identifier(self, node):
        self.emit(Load(node.value))

    def visit_Catch(self, node):
        raise NotImplementedError()

    def visit_Throw(self, node):
        raise NotImplementedError()

    def visit_TryCatch(self, node):
        raise NotImplementedError()

    def visit_Parameters(self, node):
        raise NotImplementedError()

    def visit_Parameter(self, node):
        raise NotImplementedError()

    def visit_RestParameter(self, node):
        raise NotImplementedError()

    def visit_DefineFunction(self, node):
        raise NotImplementedError()

    def visit_Assignment(self, node):
        self.dispatch(node.value)
        self.emit(
            Store(node.target.value)
        )

    def visit_Member(self, node):
        raise NotImplementedError()

    def visit_AssignmentBatch(self, node):
        raise NotImplementedError()

    def visit_While(self, node):
        raise NotImplementedError()

    def visit_For(self, node):
        raise NotImplementedError()

    def visit_ForIn(self, node):
        raise NotImplementedError()

    def visit_If(self, node):
        raise NotImplementedError()

    def visit_Switch(self, node):
        raise NotImplementedError()

    def visit_Case(self, node):
        raise NotImplementedError()

    def visit_Default(self, node):
        raise NotImplementedError()

    def visit_SpreadTerm(self, node):
        raise NotImplementedError()

    def visit_BinaryOperation(self, node):
        raise NotImplementedError()

    def visit_Arguments(self, node):
        raise NotImplementedError()

    def visit_Call(self, node):
        raise NotImplementedError()

    def visit_Subscript(self, node):
        raise NotImplementedError()

    def visit_SpreadArgs(self, node):
        raise NotImplementedError()

    def visit_Integer(self, node):
        self.emit(PushConst(NkInt(node.value)))

    def visit_Float(self, node):
        self.emit(PushConst(NkFloat(node.value)))

    def visit_String(self, node):
        self.emit(PushConst(NkString(node.value)))

    def visit_Boolean(self, node):
        self.emit(PushConst(NkBool(node.value)))

    def visit_Hexadecimal(self, node):
        raise NotImplementedError()

    def visit_BinaryNumber(self, node):
        raise NotImplementedError()

    def visit_NullValue(self, node):
        raise NotImplementedError()

    def visit_NoneValue(self, node):
        raise NotImplementedError()
