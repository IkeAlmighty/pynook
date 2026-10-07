from ir.definitions import ScopeDefinition, Constant
from ir.contexts import SwitchContext
from ir.instructions import *
from nast.nodes import *

RETURN_DEST = "return_dest"
LEAVE_DEST = "leave_dest"
CONTINUE_DEST = "continue_dest"
COLLECT_DEST = "collect_dest"
COLLECT_RESOLVABLE_MEMBERS = "collect_resolvable_members"

class IRBuilder:

    def __init__(self):
        # ends build flattened with a length of 1, used 
        # to simplify instruction length math per scope 
        # definition:
        self.definition_stack = [ScopeDefinition()]

        # some helpful stacks:
        self.switch_stack = []

        # scope types annotations:
        self.control_types_stack = [[]]

    def build(self, ast):
        self.dispatch(ast)
        return self.definition_stack[0]

    @property
    def curr_definition(self):
        return self.definition_stack[-1]

    @property
    def curr_switch(self):
        if len(self.switch_stack) == 0:
            raise Exception("switch context stack is empty")

        return self.switch_stack[-1]

    @property
    def curr_inst_length(self):
        return len(self.curr_definition.instructions)

    @property
    def control_types(self):
        if len(self.control_types_stack) == 0:
            raise Exception("scope types stack is empty, cannot access")

        return self.control_types_stack[-1] 

    def emit(self, instruction):
        self.curr_definition.instructions.append(instruction)

    def dispatch(self, node):
        method_name = f"visit_{node.__class__.__name__}"
        method = getattr(self, method_name)
        return method(node)

    ######################################################
    ##                 VISITOR HELPERS                  ##
    ######################################################

    def __emit_load(self, node): 
        if isinstance(node, Identifier):
            self.emit(
                Load(node.value)
            )

        elif isinstance(node, Member):
            self.__emit_load(node.target)

            self.emit(
                LoadMember(node.name.value)
            )

        elif isinstance(node, Subscript):
            raise NotImplementedError()

        else:
            raise Exception(f"Invalid Load target {node}")

    def __emit_store(self, node):
        if isinstance(node, Identifier):
            self.emit(
                Store(node.value)
            )

        elif isinstance(node, Member):
            self.__emit_load(node.target)

            self.emit(
                StoreMember(node.name.value)
            )

        elif isinstance(node, Subscript):
            raise NotImplementedError()

        else: 
            raise Exception(f"Invalid Store target {node}")

    #####################################################
    ##                 VISITOR METHODS                 ##
    #####################################################

    def visit_Scope(self, node):
        definition = ScopeDefinition(
            control_types=self.control_types
        )

        self.definition_stack.append(definition)
        self.dispatch(node.block)
        self.definition_stack.pop()

        self.emit(
            CreateScope(definition)
        )

    def visit_Block(self, node):
        for statement in node.statements:
            self.dispatch(statement)
    
    def visit_List(self, node):
        for item in node.items:
            self.dispatch(item)

        self.emit(CreateList(len(node.items)))

    def visit_Set(self, node):
        for item in node.items:
            self.dispatch(item)

        self.emit(CreateSet(len(node.items)))

    def visit_Leave(self, node):
        self.emit(Leave())

    def visit_Continue(self, node):
        self.emit(Continue())

    def visit_Collect(self, node):
        if node.child:
            self.dispatch(node.child)

        self.emit(Collect())

    def visit_Return(self, node):
        if node.child:
            self.dispatch(node.child)
        else:
            self.emit(
                PushConst(
                    Constant("none", None)
                )
            )

        self.emit(Return())

    def visit_Ignore(self, node):
        raise NotImplementedError()

    def visit_Identifier(self, node):
        self.__emit_load(node)

    def visit_Catch(self, node):
        raise NotImplementedError()

    def visit_Throw(self, node):
        raise NotImplementedError()

    def visit_TryCatch(self, node):
        raise NotImplementedError()

    def visit_Parameters(self, node):
        parameter_definition = ScopeDefinition()
        
        self.definition_stack.append(parameter_definition)

        try: 
            for parameter in node.parameters:
                self.dispatch(parameter)
        finally:
            self.definition_stack.pop()

        return parameter_definition

    def visit_Parameter(self, node):
        if node.default:
            self.dispatch(node.default)
        else:
            self.emit(
                PushConst(
                    Constant(
                        type_name="unbound",
                        value=None
                    )
                )
            )

        self.emit(Store(node.identifier.value))

    def visit_RestParameter(self, node):
        raise NotImplementedError()

    def visit_DefineFunction(self, node):
        body_definition = ScopeDefinition()

        self.definition_stack.append(body_definition)

        self.dispatch(node.scope.block)
        self.definition_stack.pop()

        parameter_definition = self.dispatch(node.parameters)

        self.emit(
            CreateFunction(
                body_definition,
                parameter_definition, 
                control_types=[RETURN_DEST, LEAVE_DEST, COLLECT_DEST]
            ),
        )
        
    def visit_Assignment(self, node):
        self.dispatch(node.value)
        self.__emit_store(node.target)
        
    def visit_Member(self, node):
        self.__emit_load(node)

    def visit_AssignmentBatch(self, node):
        for assignment in node.assignments:
            self.dispatch(assignment)

    def visit_While(self, node):

        start_jump = Jump(
            target = self.curr_inst_length
        )

        end_jump = JumpIfFalse(target=None)

        self.dispatch(node.expr)
        self.emit(end_jump)

        self.control_types_stack.append([CONTINUE_DEST, LEAVE_DEST, COLLECT_RESOLVABLE_MEMBERS])
        self.dispatch(node.scope)
        self.control_types_stack.pop()

        self.emit(start_jump)
        
        end_jump.target = self.curr_inst_length

    def visit_For(self, node):

        self.dispatch(node.init)

        loop_start = self.curr_inst_length

        self.dispatch(node.condition)

        end_jump = JumpIfFalse(target=None)
        self.emit(end_jump)

        self.control_types_stack.append([CONTINUE_DEST, LEAVE_DEST])

        self.dispatch(node.scope)
        self.dispatch(node.update)

        self.emit(Jump(target=loop_start))

        end_jump.target = self.curr_inst_length

        self.control_types_stack.pop()

    def visit_ForIn(self, node):
        raise NotImplementedError()
        
    def visit_If(self, node):
        branches = [(node.condition, node.then_scope)]

        # mark control types for all following if, else, and elif scopes: 
        self.control_types_stack.append([LEAVE_DEST, RETURN_DEST, COLLECT_RESOLVABLE_MEMBERS])

        for elif_node in node.elifs:
            branches.append((elif_node.condition, elif_node.then_scope))

        end_jumps = []
        for condition, scope in branches:
            self.dispatch(condition)

            skip_branch = JumpIfFalse(target=None)
            self.emit(skip_branch)

            self.dispatch(scope)

            end_jump = Jump(None)
            self.emit(end_jump)
            end_jumps.append(end_jump)

            skip_branch.target = self.curr_inst_length

        if node.else_scope:
            self.dispatch(node.else_scope)

        # pop the control types used for previously processed scopes:
        self.control_types_stack.pop()

        for jump in end_jumps:
            jump.target = self.curr_inst_length

    def visit_Switch(self, node):

        switch_context = SwitchContext()
        self.switch_stack.append(switch_context)

        self.__emit_load(node.expr)
        self.emit(Store(switch_context.expr_id))
        
        self.control_types_stack.append([COLLECT_DEST])

        self.dispatch(node.scope)

        self.control_types_stack.pop()

        self.switch_stack.pop()

        for jump in switch_context.end_jumps:
            jump.target = self.curr_inst_length
        
    def visit_Case(self, node):
        self.dispatch(node.literal)

        switch_expr_id = self.curr_switch.expr_id
        self.emit(Load(switch_expr_id))

        self.emit(Equal())
        
        jump = JumpIfFalse(target=None)
        self.emit(jump)

        # all child scopes can return control flow to a case scope:
        self.control_types_stack.append([LEAVE_DEST, COLLECT_DEST, RETURN_DEST])

        self.dispatch(node.scope)

        self.control_types_stack.pop()

        jump.target = self.curr_inst_length

        # skip the rest of the switch (this can be avoided 
        # with a collect ending the case scope)
        end_jump = Jump(target=None)
        self.curr_switch.end_jumps.append(end_jump)
        self.emit(end_jump)

    def visit_Default(self, node):
        self.control_types_stack.append([LEAVE_DEST, COLLECT_DEST, RETURN_DEST])
        self.dispatch(node.scope)
        self.control_types_stack.pop()

    def visit_SpreadTerm(self, node):
        self.dispatch(node.expr)
        self.emit(SpreadTerm())

    def visit_BinaryOperation(self, node):
        self.dispatch(node.left)
        self.dispatch(node.right)
        token_type_str = node.op_token.type.name
        op_inst_lookup = {
            "SUB": Subtract,
            "ADD": Add,
            "DIV": Divide,
            "MULT": Multiply,
            "EXPONENT": Exponent,
            "MODULO": Modulo,
            "XOR": Xor,
            "BW_AND": BwAnd,
            "BW_OR": BwOr,
            "AND": And,
            "OR": Or,
            "EQ": Equal,
            "NOT_EQ": NotEqual,
            "GREATER_EQ": GreaterThanOrEqual,
            "LESS_EQ": LessThanOrEqual,
            "LESS": LessThan,
            "GREATER": GreaterThan,
        }
        self.emit(op_inst_lookup[token_type_str]())

    def visit_Call(self, node):
        self.dispatch(node.arguments)
        self.__emit_load(node.expr)
        self.emit(Call())

    def visit_Arguments(self, node):
        for argument in node.arguments:
            self.dispatch(argument)

        self.emit(CreateList(len(node.arguments)))

    def visit_Argument(self, node):
        self.dispatch(node.expr)
        self.emit(
            CreateArgument(
                node.bind_to.value
                if node.bind_to
                else None
            )
        )

    def visit_SpreadArgument(self, node):
        self.dispatch(node.expr)
        self.emit(CreateSpreadArgument())

    def visit_Subscript(self, node):
        self.__emit_load(node)

    def visit_Integer(self, node):
        self.emit(
            PushConst(
                Constant(
                    type_name="int",
                    value=node.value
                )
            )
        )

    def visit_Float(self, node):
        self.emit(
            PushConst(
                Constant(
                    type_name="float",
                    value=node.value
                )
            )
        )

    def visit_String(self, node):
        self.emit(
            PushConst(
                Constant(
                    type_name="string",
                    value=node.value
                )
            )
        )

    def visit_Boolean(self, node):
        self.emit(
            PushConst(
                Constant(
                    type_name="boolean",
                    value=node.value
                )
            )
        )

    def visit_Hexadecimal(self, node):
        self.emit(
            PushConst(
                Constant(
                    type_name="hexadecimal",
                    value=int(node.value, 16)
                )
            )
        )

    def visit_BinaryNumber(self, node):
        self.emit(
            PushConst(
                Constant(
                    type_name="binary",
                    value=int(node.value, 2)
                )
            )
        )

    def visit_NullValue(self, node):
        self.emit(
            PushConst(
                Constant(
                    type_name="null",
                    value=None
                )
            )
        )

    def visit_NoneValue(self, node):
        self.emit(
            PushConst(
                Constant(
                    type_name="none",
                    value=None
                )
            )
        )
