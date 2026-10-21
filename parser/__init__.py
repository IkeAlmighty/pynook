from tokenizer.tokens import TokenTypes
from tokenizer import Tokenizer

import nast.nodes as Nodes

class ExpressionNeededException(Exception):
    pass

class UnexpectedTokenException(Exception):
    pass

class Parser:

    PRECEDENCE = {
        TokenTypes.OR: 10,
        TokenTypes.AND: 20,
        TokenTypes.EQ: 30,
        TokenTypes.NOT_EQ: 30,
        TokenTypes.GREATER_EQ: 40,
        TokenTypes.LESS_EQ: 40,
        TokenTypes.LESS: 40,
        TokenTypes.GREATER: 40,
        TokenTypes.BW_OR: 50,
        TokenTypes.XOR: 60,
        TokenTypes.BW_AND: 70,
        TokenTypes.SUB: 80,
        TokenTypes.ADD: 80,
        TokenTypes.DIV: 90,
        TokenTypes.MULT: 90,
        TokenTypes.MODULO: 90,
        TokenTypes.EXPONENT: 100,
    }

    RIGHT_ASSOC = { TokenTypes.EXPONENT }

    def __init__(self, tokenizer, initialize_token=True):
        self.tokenizer = tokenizer
        if initialize_token:
            self.curr_token = self.tokenizer.next()

    def _eat(self, token_type):
        if self.curr_token.type != token_type:
            raise UnexpectedTokenException(f"unexpected token {self.curr_token}, expected {token_type}")
        else:
            self.curr_token = self.tokenizer.next()

    def _snapshot(self):
        tokenizer_state = self.tokenizer.state.snapshot()

        snap = Parser(
            Tokenizer(state=tokenizer_state), 
            initialize_token=False
        )

        snap.curr_token = self.curr_token

        return snap

    def _restore(self, snapshot):
        self.tokenizer = snapshot.tokenizer 
        self.curr_token = snapshot.curr_token

    def _skip_newlines(self):
        while self.curr_token.type == TokenTypes.NEWLINE:
            self._eat(TokenTypes.NEWLINE)

################################################################################

    def file(self):
        block = self._block()
        return Nodes.File(block)

    def _block(self):
        statements = []
        while self.curr_token.type not in (
            TokenTypes.RBRACE,
            TokenTypes.RBRACKET,
            TokenTypes.EOF
        ):
            statements.append(self._statement())

            if self.curr_token.type in (
                TokenTypes.NEWLINE, 
                TokenTypes.SEMICOLON, 
                TokenTypes.COMMA
            ):
                self._eat(self.curr_token.type)

            self._skip_newlines()
            
        return Nodes.Block(statements)

    def _assignment_or_expr(self):
        # take a parser snapshot, and then try 
        # to parse an assignment. 
        # if it fails with a ExpressionNeededException, 
        # then rewind the parser to the snapshot 
        # and parse and expression instead:
        snapshot = self._snapshot()

        try:
            return self._assignment()

        except ExpressionNeededException: 
            self._restore(snapshot)
            return self._expr()

    def _statement(self):

        while self.curr_token.type == TokenTypes.NEWLINE:
            self._eat(TokenTypes.NEWLINE)

        if self.curr_token.type in (TokenTypes.IDENTIFIER, TokenTypes.STRING):
            return self._assignment_or_expr()

        elif self.curr_token.type == TokenTypes.SPREAD:
            return self._expr()

        elif self.curr_token.type == TokenTypes.LPAREN:
            return self._expr()
        
        elif self.curr_token.type in (TokenTypes.LBRACKET, TokenTypes.LBRACE):
            return self._destructure()

        elif self.curr_token.type == TokenTypes.KW_LEAVE:
            self._eat(TokenTypes.KW_LEAVE)
            return Nodes.Leave(self.curr_token.location)

        elif self.curr_token.type == TokenTypes.KW_CONTINUE:
            self._eat(TokenTypes.KW_CONTINUE)
            return Nodes.Continue()

        elif self.curr_token.type == TokenTypes.KW_RETURN:
            return self._return()

        elif self.curr_token.type == TokenTypes.KW_COLLECT:
            return self._collect()

        elif self.curr_token.type == TokenTypes.KW_IGNORE:
            return self._ignore()

        elif self.curr_token.type == TokenTypes.KW_DO:
            return self._dowhile()

        elif self.curr_token.type == TokenTypes.KW_WHILE:
            return self._while()

        elif self.curr_token.type == TokenTypes.KW_IF:
            return self._if()

        elif self.curr_token.type == TokenTypes.KW_SWITCH:
            return self._switch() 

        elif self.curr_token.type == TokenTypes.KW_CASE:
            return self._case()

        elif self.curr_token.type == TokenTypes.KW_DEFAULT:
            return self._default()

        elif self.curr_token.type == TokenTypes.KW_TRY:
            return self._trycatch()

        elif self.curr_token.type == TokenTypes.KW_FOR:
            # for disambiguates for forin
            return self._for()

        elif self.curr_token.type == TokenTypes.KW_THROW:
            return self._throw()

        else: 
            raise Exception(f"Unhandled token type for beginning of statement {self.curr_token}")

    def _scope(self):
        self._eat(TokenTypes.LBRACE)
        block = self._block()
        self._eat(TokenTypes.RBRACE)

        return Nodes.Scope(block, self.curr_token.location)

    def _list(self):
        self._eat(TokenTypes.LBRACKET)

        if self.curr_token.type != TokenTypes.RBRACKET:
            items = self._items()

        self._eat(TokenTypes.RBRACKET)

        return Nodes.List(items, self.curr_token.location)

    def _set(self):
        self._eat(TokenTypes.KW_SET)
        self._eat(TokenTypes.LBRACKET)

        if self.curr_token.type != TokenTypes.RBRACKET:
            items = self._items()

        self._eat(TokenTypes.RBRACKET)

        return Nodes.Set(items, self.curr_token.location)

    def _items(self):
        """
        returns a list of Expressions
        """
        items = [self._item()]
        while self.curr_token.type == TokenTypes.COMMA:
            self._eat(TokenTypes.COMMA)
            items.append(self._item())

        return items

    def _item(self, with_spread=False):
        """
        returns an expression, or if there is a spread operator
        returns a list of expressions
        """
        if self.curr_token.type == TokenTypes.SPREAD and with_spread:
            self._eat(TokenTypes.SPREAD)
            return Nodes.SpreadTerm(self._item(with_spread=True))

        else:
            return self._expr()

    def _throw(self):
        self._eat(TokenTypes.KW_THROW)
        expr = self._expr()

        return Nodes.Throw(expr, self.curr_token.location)

    def _trycatch(self):
        self._eat(TokenTypes.KW_TRY)
        self._skip_newlines()
        try_scope = self._scope()
        self._skip_newlines()
        catches = []
        node_finally = None
        while self.curr_token.type == TokenTypes.KW_CATCH:
            self._eat(TokenTypes.KW_CATCH)

            t = self.curr_token
            self._eat(TokenTypes.IDENTIFIER)
            self._skip_newlines()

            identifier = Nodes.Identifier(t.value, t.location)

            catch_scope = self._scope()
            self._skip_newlines()

            catches.append(Nodes.Catch(identifier, catch_scope, t.location))

        if self.curr_token.type == TokenTypes.KW_FINALLY:
            self._eat(TokenTypes.KW_FINALLY)
            self._skip_newlines()
            node_finally = self._scope()
            
        return Nodes.TryCatch(try_scope, catches, node_finally)

    def _assignment(self):

        try:
            target = None
            # check for string assignments first
            if self.curr_token.type == TokenTypes.STRING:
                target = Nodes.Identifier(
                    value=self.curr_token.value, 
                    location=self.curr_token.location, 
                )
                self._eat(TokenTypes.STRING)
            else:
                # otherwise assume it's a regular target
                target = self._target()

            self._eat(TokenTypes.COLON)

        except UnexpectedTokenException as err:
            raise ExpressionNeededException

        if self.curr_token.type == TokenTypes.LPAREN:
            self._eat(TokenTypes.LPAREN)
            function = None
            if self.curr_token.type == TokenTypes.IDENTIFIER and self.curr_token.value == 'root':
                function = self._def_root_func() 
            else:
                function = self._def_func()

            return Nodes.Assignment(target, function)

        else:
            expr = self._expr()
            return Nodes.Assignment(target, expr)
        
    def _target(self):
        t = self.curr_token
        self._eat(TokenTypes.IDENTIFIER)
        target = Nodes.Identifier(t.value, t.location)

        while self.curr_token.type in (TokenTypes.DOT, TokenTypes.LBRACKET):
            if self.curr_token.type == TokenTypes.DOT:
                self._eat(TokenTypes.DOT)
                t = self.curr_token
                self._eat(TokenTypes.IDENTIFIER)
                target = Nodes.Member(
                    target,
                    Nodes.Identifier(t.value, t.location)
                )
            else:
                target = self._subscript(target)

        return target

    def _destructure(self, ignore=False):
        patterns = None
        if self.curr_token.type == TokenTypes.LBRACE:
            patterns = self._destruct_scope()
        else:
            patterns = self._destruct_list()

        self._eat(TokenTypes.COLON)
        expr = self._expr()
        assignments = []

        for pattern in patterns:
            bindings = self._resolve_pattern(expr, pattern)

            for identifier, source_expr in bindings:
                assignment = Nodes.Assignment(
                    identifier,
                    source_expr
                )

                if ignore:
                    ignore_node = Nodes.Ignore(assignment)
                    assignments.append(ignore_node)

                else:
                    assignments.append(assignment)

        return Nodes.AssignmentBatch(assignments)


    def _resolve_pattern(self, source_expression, pattern):
        field_name, child_pattern = pattern

        # create the parent node of the current depth:
        member_expression = Nodes.Member(source_expression, field_name)
        
        # if there is no child, bubble the parent
        # up to the next call:
        # { a }
        if child_pattern is None:
            return [(field_name, member_expression)]

        # if the child_pattern is an Identifier, then 
        # return the member
        # { a : b }
        if isinstance(child_pattern, Nodes.Identifier):
            return [(child_pattern, member_expression)]

        # { a : { ... } }
        bindings = []

        # for field_name, child in child:
        for nested_pattern in child_pattern:
            bindings.extend(
                self._resolve_pattern(
                    member_expression, 
                    nested_pattern
                )
            )

        return bindings

    def _destruct_scope(self):
        self._eat(TokenTypes.LBRACE)
        sequence = self._pattern_sequence()
        self._eat(TokenTypes.RBRACE)

        return sequence
    
    def _destruct_list(self):
        self._eat(TokenTypes.LBRACKET)
        sequence = self._pattern_sequence()
        self._eat(TokenTypes.RBRACKET)

        return sequence

    def _pattern_sequence(self):
        sequence = [self._pattern()]

        while self.curr_token.type == TokenTypes.COMMA:
            self._eat(TokenTypes.COMMA)
            sequence.append(self._pattern()) 

        return sequence

    def _pattern(self):
        t = self.curr_token
        self._eat(TokenTypes.IDENTIFIER)
        identifier = Nodes.Identifier(t.value, t.location)

        if self.curr_token.type == TokenTypes.COLON:
            self._eat(TokenTypes.COLON)
            return (identifier, self._pattern_obj())

        return (identifier, None)

    def _pattern_obj(self):
        if self.curr_token.type == TokenTypes.IDENTIFIER:
            t = self.curr_token
            self._eat(TokenTypes.IDENTIFIER)
            return Nodes.Identifier(t.value, t.location)

        elif self.curr_token.type == TokenTypes.LBRACE:
            return self._destruct_scope()

        else: 
            return self._destruct_list()

    def _return(self):
        self._eat(TokenTypes.KW_RETURN)
        child = None 

        if self.curr_token.type in (
            TokenTypes.LBRACE,
            TokenTypes.LBRACKET,
            TokenTypes.KW_SET,
            TokenTypes.IDENTIFIER, 
            TokenTypes.SPREAD,
            TokenTypes.BOOLEAN, 
            TokenTypes.STRING,
            TokenTypes.INT, 
            TokenTypes.FLOAT,
            TokenTypes.BINARY,
            TokenTypes.KW_NONE,
            TokenTypes.KW_NULL,
            TokenTypes.BOOLEAN,
            TokenTypes.HEXADECIMAL,
            TokenTypes.BINARY
        ):
            child = self._expr()
        
        return Nodes.Return(child, self.curr_token.location)

    def _collect(self):
        self._eat(TokenTypes.KW_COLLECT)
        child = None 

        if self.curr_token.type in (TokenTypes.IDENTIFIER, TokenTypes.SPREAD):
            child = self._assignment_or_expr()

        return Nodes.Collect(child, self.curr_token.location)

    def _ignore(self):
        self._eat(TokenTypes.KW_IGNORE)
        if self.curr_token.type in (TokenTypes.LBRACE, TokenTypes.LBRACKET):
            return self._destructure(ignore=True)
        else:
            node = self.assignment_or_expr()
            return Nodes.Ignore(node)

    def _while(self):
        self._eat(TokenTypes.KW_WHILE)
        expr = self._expr()
        scope = self._scope()
        return Nodes.While(expr, scope)

    def _dowhile(self):
        self._eat(TokenTypes.KW_DO)
        scope = self._scope()
        self._eat(TokenTypes.KW_WHILE)
        expr = self._expr()

        return Nodes.While(expr, scope)

    def _for(self):
        self._eat(TokenTypes.KW_FOR)
        
        init = self._statement()

        if isinstance(init, Nodes.Identifier) and self.curr_token.type == TokenTypes.KW_IN:
            return self._forin(init)

        self._eat(TokenTypes.SEMICOLON)
        condition = self._expr()
        self._eat(TokenTypes.SEMICOLON)
        action = self._statement()

        scope = self._scope()

        return Nodes.For(init, condition, action, scope, self.curr_token.location)

    def _forin(self, identifier):
        """
        forin makes the assumption that FOR and the the identifier 
        has aleady been eaten, and that it being called from the 
        _for function:
        """
        self._eat(TokenTypes.KW_IN)

        collection = self._expr()
        scope = self._scope()

        return Nodes.ForIn(identifier, collection, scope, self.curr_token.location)

    def _if(self):
        self._eat(TokenTypes.KW_IF)

        expr = self._expr()
        scope = self._scope()

        # skip any newlines
        while self.curr_token.type == TokenTypes.NEWLINE:
            self._eat(TokenTypes.NEWLINE)

        elif_nodes = []
        while self.curr_token.type == TokenTypes.KW_ELIF:
            elif_nodes.append(self._elif())

        # skip any newlines
        while self.curr_token.type == TokenTypes.NEWLINE:
            self._eat(TokenTypes.NEWLINE)

        else_node = None
        if self.curr_token.type == TokenTypes.KW_ELSE:
            else_node = self._else()

        return Nodes.If(expr, scope, elif_nodes, else_node)
        
    def _elif(self):
        self._eat(TokenTypes.KW_ELIF)

        expr = self._expr()
        scope = self._scope()

        return Nodes.If(expr, scope)

    def _else(self):
        self._eat(TokenTypes.KW_ELSE) 
        return self._scope()

    def _switch(self):
        self._eat(TokenTypes.KW_SWITCH)
        expr = self._expr()
        scope = self._scope()
        return Nodes.Switch(expr, scope)

    def _default(self):
        self._eat(TokenTypes.KW_DEFAULT)
        scope = self._scope()
        return Nodes.Default(scope)

    def _case(self):
        self._eat(TokenTypes.KW_CASE)
        literal = self._literal()
        scope = self._scope()
        return Nodes.Case(literal, scope)

    def _def_func(self):
        """
        _def_func assumes that LPAREN has already been eaten.
        This lets us avoid having to take a snapshot from _assignment.
        """
        t = self.curr_token.type
        params = Nodes.Parameters([])

        if t == TokenTypes.SPREAD or t == TokenTypes.IDENTIFIER:
            params = self._params()
        
        self._eat(TokenTypes.RPAREN)

        scope = self._scope()

        return Nodes.DefineFunction(params, scope, has_root=False)

    def _def_root_func(self):
        """ 
        def_proto assumes that LPAREN has already been eaten.
        This lets us avoid having to take a snapshot from _assignment.
        """
        self._eat(TokenTypes.IDENTIFIER)

        t = self.curr_token.type
        params = Nodes.Parameters([])
        if t == TokenTypes.COMMA:
            self._eat(TokenTypes.COMMA)
            
            params = self._params()
        
        self._eat(TokenTypes.RPAREN)

        scope = self._scope()

        return Nodes.DefineFunction(params, scope, has_root=True)

    def _params(self):
        params = [self._param()]

        while self.curr_token.type == TokenTypes.COMMA:
            self._eat(TokenTypes.COMMA)
            params.append(self._param())

        if self.curr_token.type == TokenTypes.SPREAD:
            if len(params) == 0: 
                raise Exception(f"Unexepected spread token '..' {self.curr_token.location}")
            
            last_param = params.pop()

            if last_param.default:
                raise Exception(f"rest parameters cannot have default values")

            spread_param = Nodes.RestParameter(last_param)
            params.append(spread_param)
            self._eat(TokenTypes.SPREAD)

        return Nodes.Parameters(params)

    def _param(self):
        result = None
        
        t = self.curr_token
        self._eat(TokenTypes.IDENTIFIER)
        
        # handle default parameter values:
        default = None
        if self.curr_token.type == TokenTypes.COLON:
            self._eat(TokenTypes.COLON) 
            default = self._expr()

        identifier = Nodes.Identifier(t.value, t.location)
        result = Nodes.Parameter(identifier, default)

        return result
            
    def _expr(self):
        return self._infix()    

    def _infix(self, min_prec=0):
        # prat parser
        left = self._term()

        while True:
            op_token = self.curr_token

            # if the type is not an operator type, 
            # then break the parse loop and return:
            if op_token.type not in Parser.PRECEDENCE:
                break

            prec = Parser.PRECEDENCE[op_token.type]

            # if the precedence is less than the current
            # min precedence, then break and return:
            if prec < min_prec:
                break

            self._eat(op_token.type)
            if op_token.type in Parser.RIGHT_ASSOC:
                next_min_prec = prec
            else:
                next_min_prec = prec + 1

            # call the next infix with higher precedence,
            # which ensures left associativity:
            right = self._infix(next_min_prec)

            # reassign left to contain the original left,
            # the op token, and the right in a Binary node:
            left = Nodes.BinaryOperation(left, op_token, right)

        return left
        
    def _term(self):
        if self.curr_token.type == TokenTypes.SPREAD:
            self._eat(TokenTypes.SPREAD)
            return Nodes.SpreadTerm(self._postfix())

        return self._postfix()

    def _postfix(self):
        expr = self._primary()
        while True:
            if self.curr_token.type == TokenTypes.LPAREN:
                expr = self._call(expr)
            
            elif self.curr_token.type == TokenTypes.LBRACKET:
                expr = self._subscript(expr)

            elif self.curr_token.type == TokenTypes.DOT:
                self._eat(TokenTypes.DOT)

                t = self.curr_token
                self._eat(TokenTypes.IDENTIFIER)

                member = Nodes.Identifier(t.value, t.location)

                expr = Nodes.Member(expr, member)

            else:
                break

        return expr

    def _primary(self):
        if self.curr_token.type == TokenTypes.LPAREN:
            self._eat(TokenTypes.LPAREN)
            expr = self._expr()
            self._eat(TokenTypes.RPAREN)
            return expr
        elif self.curr_token.type == TokenTypes.IDENTIFIER:
            t = self.curr_token
            self._eat(TokenTypes.IDENTIFIER)
            return Nodes.Identifier(t.value, t.location)
        else:
            return self._literal()

    def _call(self, expr):
        self._eat(TokenTypes.LPAREN)

        args = Nodes.Arguments([])

        if self.curr_token.type != TokenTypes.RPAREN:
            args = self._args()

        self._eat(TokenTypes.RPAREN)

        return Nodes.Call(expr, args)

    def _subscript(self, expr):
        self._eat(TokenTypes.LBRACKET)
        start = None
        end = None
        is_slice = False

        if self.curr_token.type != TokenTypes.RBRACKET:
            if self.curr_token.type != TokenTypes.COLON:
                start = self._expr()
            
            if self.curr_token.type == TokenTypes.COLON:
                self._eat(TokenTypes.COLON)
                is_slice = True
                if self.curr_token.type != TokenTypes.RBRACKET:
                    end = self._expr()

        self._eat(TokenTypes.RBRACKET) 
        return Nodes.Subscript(expr, start, end, is_slice)

    def _args(self):
        args = [self._arg()]
        
        while self.curr_token.type == TokenTypes.COMMA:
            self._eat(TokenTypes.COMMA)
            args.append(self._arg()) 

        if self.curr_token.type == TokenTypes.SPREAD:
            if len(args) == 0:
                raise Exception("no target for spread")

            last_arg = args.pop()
            if last_arg.default:
                raise Exception("spread arguments cannot be specifically bound to a parameter")

            spread_arg = Node.SpreadArg(last_arg.expr)
            args.append(spread_arg)

        return Nodes.Arguments(args)
        
    def _arg(self):
        expr = self._expr()

        # named argument logic: 
        bind_to = None
        if self.curr_token.type == TokenTypes.COLON:
            if not isinstance(expr, Identifier):
                raise Exception(f"expressions cannot be used as argument identifier {self.curr_token.location}")

            self._eat(TokenTypes.COLON)

            bind_to = expr.value

            expr = self._expr()

        return Nodes.Argument(expr, bind_to)
    
    def _literal(self):
        node_lookup = {
            TokenTypes.INT : Nodes.Integer,
            TokenTypes.FLOAT : Nodes.Float,
            TokenTypes.STRING : Nodes.String,
            TokenTypes.BOOLEAN : Nodes.Boolean,
            TokenTypes.BINARY : Nodes.BinaryNumber,
            TokenTypes.HEXADECIMAL : Nodes.Hexadecimal,
            TokenTypes.KW_NULL : Nodes.NullValue,
            TokenTypes.KW_NONE : Nodes.NoneValue
        }

        t = self.curr_token
        if t.type in node_lookup.keys():
            self._eat(t.type)
            return node_lookup[t.type](t.value, t.location)
        
        elif t.type == TokenTypes.LBRACE:
            return self._scope()
        elif t.type == TokenTypes.LBRACKET:
            return self._list()
        elif t.type == TokenTypes.KW_SET:
            return self._set()

        raise Exception(f"Expected literal, got {t}")

