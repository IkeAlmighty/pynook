from runtime.exceptions import *
from runtime.objects import RtScope, RtConstants, RtCoreFunction, RtFunction 
import nast.nodes as Node

class Evaluator:

    def __init__(self, runtime):
        self.runtime = runtime
        self.name_hints = []
        self.scope_type_hints = [RtScope.Types.FILE]
        self.scope_stack = [self.runtime.main_scope]
        self.throw_stack = []
        self.switch_expr_stack = []

    @property
    def curr_scope(self):
        if len(self.scope_stack) == 0: return None
        return self.scope_stack[-1]

    @property
    def curr_name_hint(self):
        if len(self.name_hints) == 0: return "<anonymous>"
        return self.name_hints[-1]

    @property
    def curr_type_hint(self):
        if len(self.scope_type_hints) == 0: 
            raise Exception("Attempted to access empty scope_type_hints")

        return self.scope_type_hints[-1]

    @property
    def curr_switch_expr(self):
        if len(self.switch_expr_stack) == 0: raise Exception("case must be inside switch")
        return self.switch_expr_stack[-1]

    @property
    def nearest_collection_scope(self):

        index = -2 # grab the parent scope to the current scope first
        scope = self.scope_stack[index]

        while scope.scope_type not in RtScope.COLLECT_CATCHER_TYPES:
            index -= 1
            if len(self.scope_stack) + index < 1:
                raise Exception("cannot collect to main scope")

            scope = self.scope_stack[index]

        return scope

    def resolve_assignment_target(self, node):
        """
        helper for getting must the name value of 
        an identifier node, instead of the value 
        it points to
        """
        if isinstance(node, Node.Identifier):
            # do a walk up the scope tree to make
            # sure this identifier has not been declared
            # somewhere:
            scope = self.curr_scope
            while scope:class Instruction: pass

@dataclass
class Load(Instruction):
    value: str

@dataclass
class Store(Instruction):
    value: str

@dataclass
class PushConst(Instruction):
    value: NkValue
                if node.value in scope.variables:
                    return scope, node.value
                
                scope = scope.parent

            # if it has not been, then go ahead
            # and return the current scope:
            return self.curr_scope, node.value

        if isinstance(node, Node.Member):
            owner = self.dispatch(node.target)

            if not isinstance(owner, RtScope):
                raise InvalidMemberAccess(f"{owner} is not a RuntimeScope and cannot be accessed.")

            # for a = Member ( Member ( Identifier )))
            # resolve_assignment_target(a) resolves a String literal for value
            # and an RtScope for owner
            value = node.name.value 
            return owner, value

        raise InvalidNameTarget(f"{node}")

    def dispatch(self, node):
        if node is None: return None

        method_name = f"visit_{node.__class__.__name__}"
        visit_method = getattr(self, method_name)
        return visit_method(node)
    
    # helper method for handling signals:
    def get_nonarg_parent(self):
        parent = self.curr_scope.parent
        while parent and parent.scope_type in RtScope.ARG_TYPES:
            parent = parent.parent

        if parent: return parent
        else: raise Exception("Cannot find non-arg parent scope")

    def visit_Scope(self, node):
        name = self.curr_name_hint
        scope_type = self.curr_type_hint

        scope = RtScope(
            name=name, 
            parent=self.curr_scope, 
            scope_type=scope_type, 
            ast_node = node,
            main_scope=self.runtime.main_scope
        )

        try:
            self.scope_stack.append(scope)
            self.dispatch(node.block)

        except LeaveSignal as sig:
            parent = self.get_nonarg_parent()
            if parent.scope_type not in RtScope.CONTROL_CATCHER_TYPES:
                raise sig

        except ReturnSignal as sig:
            parent = self.get_nonarg_parent()
            if parent.scope_type not in RtScope.RETURN_CATCHER_TYPES:
                raise sig

            else: scope.return_value = sig.value

        except CollectSignal as sig:
            parent = self.get_nonarg_parent()
            if parent.scope_type not in RtScope.COLLECT_CATCHER_TYPES:
                raise sig

            else: scope.return_value = sig.value

        finally:
            self.scope_stack.pop()

        return scope

    def visit_List(self, node):
        rt_list = []
        for expr in node.items:
            if isinstance(expr, Node.SpreadTerm):
                items = self.dispatch(expr.expr)
                rt_list.extend(items)
            else:
                rt_list.append(self.dispatch(expr))

        return rt_list

    def visit_Set(self, node):
        #FIXME: badly optimized! (build set conditionally, instead or flattening at end)
        rt_set = []
        for expr in node.items:
            if isinstance(expr, Node.SpreadTerm):
                items = self.dispatch(expr.expr)
                rt_set.extend(items)
            else:
                rt_set.append(self.dispatch(expr))

        return set(rt_set)

    def visit_Block(self, node):
        for statement in node.statements:
            self.dispatch(statement)

    def visit_Leave(self, node):
        raise LeaveSignal() 

    def visit_Continue(self, node):
        raise ContinueSignal()

    def visit_Collect(self, node):

        if node.child:
            value = self.dispatch(node.child)
        else:
            value = self.curr_scope
                
        if isinstance(value, RtScope):
            value.collect_to(self.nearest_collection_scope)

        else:
            _, name = self.resolve_assignment_target(node.child)
            self.nearest_collection_scope.assign(name, value)

        raise CollectSignal(value)

    def visit_Return(self, node):
        value = None
        if node.expr:
            value = self.dispatch(node.expr)

        raise ReturnSignal(value)

    def visit_Ignore(self, node):
        value = self.dispatch(node.child)
        _, name = self.resolve_assignment_target(node.child)
        self.curr_scope.ignored_names.append(name)

        return value

    def visit_Identifier(self, node):
        """
        Resolves the identifier.
        """
        return self.curr_scope.resolve(node.value)

    def visit_Catch(self, node):
        name = node.identifier.value
        # TODO: rethink and possible refactor into
        # flag/pull model...
        value = self.throw_stack.pop()

        args_scope = RtScope(
            name="<anonymous>",
            parent=self.curr_scope,
            scope_type=RtScope.Types.CATCH_ARGS,
            main_scope=self.runtime.main_scope
        )

        args_scope.assign(name, value)

        self.scope_stack.append(args_scope)
        self.scope_type_hints.append(RtScope.Types.CATCH_BODY)
        self.dispatch(node.scope)
        self.scope_type_hints.pop()
        self.scope_stack.pop()

    def visit_Throw(self, node):
        value = self.dispatch(node.expr)
        if not isinstance(value, RtException):
            raise Exception(f"Invalid throw value {node.row} {node.col}")

        self.throw_stack.append(value)

    def visit_TryCatch(self, node):
        # execute the main scope:
        self.dispatch(node.try_scope)

        # dispatch each catch scope:
        for catch in node.catches:
            self.dispatch(catch)

        if node.finally_scope:
            self.dispatch(finally_scope)

    def visit_Parameters(self, node):
        # return dictionary of name, default for parameters
        params = {}
        for param in node.params:
            if isinstance(param, Node.RestParameter):
                return self.dispatch(node.parameter)

            else:
                name, value = self.dispatch(param)
                params[name] = value

        return params

    def visit_Parameter(self, node):
        name = node.identifier.value
        #FIXME: handling defaults probably is more in depth
        default = self.dispatch(node.default)
        return name, default

    def visit_RestParameter(self, node):
        # RtSpreadParam is a name that means 'rest' of arguments. 
        # If visit_Call encounters a RtSpreadParam at the end of
        # an arg list then it creates a list and append remaining
        # args to that list, and passed it in under the name of 
        # RtSpread parameter. 
        name, default = self.dispatch(node.parameter)
        return RtSpreadParam(name, default)

    def visit_DefineFunction(self, node):
        if node.has_root:
            scope_type = RtScope.Types.ROOT_FUNCTION_BODY
        else:
            scope_type = RtScope.Types.FUNCTION_BODY

        name = self.curr_name_hint
        params_dict = self.dispatch(node.params)
        closure_scope = self.curr_scope
        func = RtFunction(name, params_dict, scope_type, node.scope, closure_scope)

        return func

    def visit_Assignment(self, node):
        if isinstance(node, Node.SpreadTerm):
            raise RuntimeException("spread operator cannot be used in an assignment")

        owner, name = self.resolve_assignment_target(node.target)

        self.name_hints.append(name)
        value = self.dispatch(node.value)
        self.name_hints.pop()

        owner.assign(name, value)

        return value

    def visit_Member(self, node):
        """
        Resolves the Member. Assumes that the target
        resolves to a RtScope.
        """
        target = self.dispatch(node.target)
        member_name = node.name.value

        if not isinstance(target, RtScope):
            message = (
                f"Cannot access member '{member_name}' "
                f"on value of type {type(target).__name__}"
            )
            raise InvalidMemberAccess(message)

        return target.resolve(member_name)

    def visit_AssignmentBatch(self, node):
        for assignment in node.assignments:
            self.dispatch(assignment)

    def visit_While(self, node):

        condition = self.dispatch(node.expr)
        while condition:
            try:
                self.scope_type_hints.append(RtScope.Types.LOOP_BODY)
                self.dispatch(node.scope)

            except ContinueSignal: continue
            finally:
                self.scope_type_hints.pop()
                condition = self.dispatch(node.expr)

    def visit_For(self, node):

        for_args_scope = RtScope(
            name="<anonymous.for-args>",
            parent=self.curr_scope,
            scope_type=RtScope.Types.LOOP_ARGS,
            main_scope=self.runtime.main_scope
        )
        self.scope_stack.append(for_args_scope)

        try:
            init = self.dispatch(node.init)
            condition = self.dispatch(node.condition)

            if condition != False and condition != True and condition != RtConstants.NoneValue:
                raise Exception(f"for loop conditions must resolve to truthy values {node.row} {node.col}")

            while condition:
                try:
                    self.scope_type_hints.append(RtScope.Types.LOOP_BODY)
                    self.dispatch(node.scope)

                except ContinueSignal: continue
                finally:
                    self.scope_type_hints.pop()
                    self.dispatch(node.update)
                    condition = self.dispatch(node.condition)

        finally:
            self.scope_stack.pop()

    def visit_ForIn(self, node):

        _, name = self.resolve_assignment_target(node.identifier)
        enumerated = self.dispatch(node.enumerated)

        if isinstance(enumerated, RtScope):
            enumerated = enumerated.collection

        if not isinstance(enumerated, list) and not isinstance(enumerated, set):
            message = f"for..in loops must provide an iterable {node.row} {node.col}"
            raise TypeException(message)
        
        for_in_args_scope = RtScope(
            name="<anonymous.forin-args>",
            parent=self.curr_scope,
            scope_type=RtScope.Types.LOOP_ARGS,
            main_scope=self.runtime.main_scope
        )
        self.scope_stack.append(for_in_args_scope)

        try:
            for val in enumerated:
                try:
                    for_in_args_scope.assign(name, val)
                    self.scope_type_hints.append(RtScope.Types.LOOP_BODY)
                    self.dispatch(node.scope)

                except ContinueSignal: continue 
                finally:
                    self.scope_type_hints.pop()

        finally:
            self.scope_stack.pop()
            

    def visit_If(self, node):
        """
        Returns True if the then_scope was ran
        Returns False if the then_scope was not ran
        """

        condition = self.dispatch(self.condition) 
        if isinstance(condition, RtConstants.NoneValue):
            condition = False

        if not isinstance(condition, bool):
            raise RuntimeException("condition must None type or Bool")

        if condition:
            try:
                self.scope_type_hints.append(RtScope.Types.IF_BODY)
                self.dispatch(node.then_scope)
            finally:
                self.scope_type_hints.pop()

            return True
        
        else:
            for elif_node in node.elifs:
                try:
                    self.scope_type_hints.append(RtScope.Types.IF_BODY)
                    did_run = self.dispatch(elif_node)
                finally:
                    self.scope_type_hints.pop()

                # stop visiting if nodes if an elif node runs:
                # TODO: write tests and debug for elif
                if did_run: return False
            
            # run the else node if no other nodes run:
            if node.else_scope: 
                try:
                    self.scope_type_hints.append(RtScope.Types.ELSE_BODY)
                    self.dispatch(node.else_scope)
                finally:
                    self.scope_type_hints.pop()

    def visit_Switch(self, node):
        # create a switch scope that can be collected to:
        switch_scope = RtScope(
            name="<anonymous>",
            parent=self.curr_scope, 
            scope_type=RtScope.Types.SWITCH_ARGS, 
            main_scope=self.runtime.main_scope
        )

        _, name = self.resolve_assignment_target(node.expr)
        value = self.dispatch(node.expr)
        switch_scope.assign(name, value)

        self.scope_stack.append(switch_scope)
        self.switch_expr_stack.append(name)
        self.scope_type_hints.append(RtScope.Types.SWITCH_BODY)
        self.name_hints.append("<anonymous>")

        try:
            self.dispatch(node.scope)

        finally:
            self.name_hints.pop()
            self.switch_expr_stack.pop()
            self.scope_type_hints.pop()
            self.scope_stack.pop()

    def visit_Case(self, node):
        name = self.curr_switch_expr
        against = self.curr_scope.resolve(name)
        match = self.dispatch(node.literal)

        if match == against:

            self.scope_type_hints.append(RtScope.Types.CASE_BODY)
            self.name_hints.append(f"<case-{match}>")

            try:
                self.dispatch(node.scope)
            finally:
                self.name_hints.pop()
                self.scope_type_hints.pop()

    def visit_Default(self, node):
        if len(self.switch_expr_stack) == 0: raise Exception("default must be inside switch")

        self.scope_type_hints.append(RtScope.Types.DEFAULT_BODY)
        self.name_hints.append("<anonymous>")
        try:
            self.dispatch(node.scope)
        finally:
            self.name_hints.pop()
            self.scope_type_hints.pop()

    def visit_SpreadTerm(self, node):
        # lists use SpreadArgs instead
        # and parameters are defined by SpreadParam
        expr = self.dispatch(node.expr)
        expr.collect_to(self.curr_scope)

    def visit_BinaryOperation(self, node):
        op_type = node.op_token.type
        left_val = self.dispatch(node.left)
        right_val = self.dispatch(node.right)

        result = self.apply_op(op_type, left_val, right_val)
        return result

    def visit_Arguments(self, node):
        names = self.curr_scope.get_unbound_vars()

        for name, expr in zip(names, node.arguments):
            if isinstance(expr, Node.SpreadArgs):
                self.dispatch(expr)
            else:
                value = self.dispatch(expr)
                if self.curr_scope.variables[name] is not RtConstants.UnboundValue:
                    raise RuntimeError(f"{name} assigned to twice in argument scope")

                self.curr_scope.assign(name, value)

    def call_core_func(self, core_func):
        """
        Reconstructs the arg values, assuming that the arg scope
        is currently at the top of the stack, and then calls the
        core function with those arguments. 
        """
        args = [self.runtime]
        for name, default in core_func.params.items():
            value = self.curr_scope.resolve(name)
            if not value:
                #sig = inspect.signature(core_func.func)
                pass

            args.append(value)

        return core_func.func(*args)

    def visit_Call(self, node):
        rt_func = self.dispatch(node.expr)
        name = rt_func.name
        
        if isinstance(rt_func, RtFunction):
            parent = rt_func.closure_scope
        else:
            # for RtCoreFunctions:
            parent = self.curr_scope

        args_scope = RtScope(
            name = f"{self.curr_scope.name}.{name}.args",
            parent = parent,
            scope_type=RtScope.Types.FUNCTION_ARGS,
            main_scope=self.runtime.main_scope
        )

        # push the args_scope to the stack:
        self.scope_stack.append(args_scope)

        if rt_func.scope_type == RtScope.Types.ROOT_FUNCTION_BODY:
            args_scope.assign("root", args_scope)

        # initialize each parameter from rt func
        # as UnboundValue in the args_scope:
        for name in rt_func.params.keys():
            value = RtConstants.UnboundValue
            args_scope.assign(name, value)

        try:
            # dispatch the arguments node, which will
            # attempt to assign all uninitialized parameters
            self.dispatch(node.arguments)

            # iterate through unbound parameters, grabbing their defaults
            # and assigning them appropiately
            for missing_param in self.curr_scope.get_unbound_vars():
                
                # grab default value:
                default = rt_func.params[missing_param]

                # (NoDefaultValue is assigned to parameters that have no default)
                if default != RtConstants.NoDefaultValue: 
                    self.curr_scope.assign(missing_param, default)

                # if there is no default value for parameter at this point, throw and error:
                else: 
                    raise Exception(f"Missing parameter {missing_param} for function {rt_func.name}")

            # if the function is a core function, then run it directly,
            if isinstance(rt_func, RtCoreFunction):
                return self.call_core_func(rt_func)  

            # otherwise dispatch function ast and return it's return value:
            # (return value defaults to RtConstants.NoneValue
            self.scope_type_hints.append(rt_func.scope_type)
            try:
                return self.dispatch(rt_func.scope_node)
            finally:
                self.scope_type_hints.pop()

        finally:
            self.scope_stack.pop()

    def visit_Subscript(self, node):
        value = self.dispatch(node.expr) 
        start = self.dispatch(node.start)
        end = self.dispatch(node.end)

        if node.is_slice:
            if start and end:
                if isinstance(value, str) or isinstance(value, list):
                    return value[start:end]

                else:
                    raise InvalidSubscript()

            if not start and end:
                if isinstance(value, str) or isinstance(value, list):
                    return value[:end]

                else:
                    raise InvalidSubscript()

            if start and not end:
                if ininstance(value, str) or isinstance(value, list):
                    return value[start:]

                else:
                    raise InvalidSubscript()

            if not start and not end:
                return value

        else:
            if isinstance(value, str) or isinstance(value, list):
                return value[start]

            elif isinstance(value, RtScope) and isinstance(start, str):
                return value.variables[start]

            else:
                raise InvalidSubscript()
       

    def visit_SpreadArgs(self, node):
        result = self.dispatch(node.expr)
        names = self.curr_scope.get_unbound_vars()

        if isinstance(result, RtScope):
            for name in names:
                if name in result.variables:
                    self.curr_scope.assign(
                        name,
                        result.variables[name]
                    )

        elif isinstance(result, list):
            for name, value in zip(names, result):
                self.curr_scope.assign(
                    name, 
                    value
                )
                
    def visit_Integer(self, node):
        return int(node.value)

    def visit_Float(self, node):
        return float(node.value)

    def visit_String(self, node):
        return node.value

    def visit_Boolean(self, node):
        # TODO: use Runtime Constants instead
        if node.value == 'true': return True
        else: return False

    def visit_Hexadecimal(self, node):
        return node.value

    def visit_BinaryNumber(self, node):
        return node.value

    def visit_NullValue(self, node):
        node.value = RtConstants.NullValue
        return node 

    def visit_NoneValue(self, node):
        node.value = RtConstants.NoneValue
        return node

    ##### op logic #####
    # FIXME: more precise logic needed for each op based
    # on types of the operands

    def apply_op(self, optype, lhs, rhs=None):
        
        method_name = f"op_{optype.name.lower()}"
        if rhs:
            result = getattr(self, method_name)(lhs, rhs)
        else:
            # for unary operators:
            result = getattr(self, method_name)(lhs)

        return result

    def op_sub(self, lhs, rhs):
        return lhs - rhs

    def op_add(self, lhs, rhs):
        return lhs + rhs

    def op_div(self, lhs, rhs):
        return lhs / rhs

    def op_mult(self, lhs, rhs):
        return lhs * rhs

    def op_exponent(self, lhs, rhs):
        return lhs ** rhs

    def op_modulo(self, lhs, rhs):
        return lhs % rhs

    def op_xor(self, lhs, rhs):
        return lhs ^ rhs

    def op_bw_and(self, lhs, rhs):
        return lhs & rhs

    def op_bw_or(self, lhs, rhs):
        return lhs | rhs

    def op_and(self, lhs, rhs):
        return lhs and rhs

    def op_or(self, lhs, rhs):
        return lhs or rhs

    def op_negate(self, operand):
        return not operand

    def op_size(self, operand):
        return len(operand)

    def op_eq(self, lhs, rhs):
        return lhs == rhs

    def op_not_eq(self, lhs, rhs):
        return lhs != rhs

    def op_greater_eq(self, lhs, rhs):
        return lhs >= rhs

    def op_less_eq(self, lhs, rhs):
        return lhs <= rhs

    def op_less(self, lhs, rhs):
        return lhs < rhs

    def op_greater(self, lhs, rhs):
        return lhs > rhs

