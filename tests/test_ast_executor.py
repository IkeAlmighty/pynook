import unittest
from unittest.mock import patch
from ast_nodes import *
from ast_executor import Executor
from runtime import Runtime, RtScope
from runtime_exceptions import *

class TestAstExecutor(unittest.TestCase):

    def setUp(self):
        runtime = Runtime()
        self.exec = Executor(runtime)
        self.main_scope = self.exec.runtime.main_scope

    def test_resolve_assignment_target(self):

        ast = Member(
            target=Member(
                target=Identifier("a", 0, 0), 
                name=Identifier("b", 0, 0)
            ),
            name=Identifier("c", 0, 0), 
        )
        
        # FAIL (no values have been assigned)
        with self.assertRaises(VariableUnresolvable) as err:
            owner, name = self.exec.resolve_assignment_target(ast)

        # PASS 
        # manually assign values, then try to resolve
        a_scope = RtScope(
            "a_scope", 
            parent=self.main_scope, 
            scope_type=RtScope.Types.FUNCTION_BODY, 
            main_scope=self.main_scope
        )
        self.main_scope.assign("a", a_scope)

        b_scope = RtScope(
            "b_scope", 
            parent=a_scope, 
            scope_type=RtScope.Types.FUNCTION_BODY, 
            main_scope=self.main_scope
        )

        a_scope.assign("b", b_scope)

        c_value = "hello"
        b_scope.assign("c", c_value)

        owner, name = self.exec.resolve_assignment_target(ast)

        self.assertEqual(name, "c")
        self.assertEqual(owner, b_scope)

    @patch('ast_nodes.Block')
    def test_visit_Scope(self, mock_block):
        fixture = Scope(
            Block([]), 0, 0
        )

        mock_block.return_value = True

        self.exec.scope_type_hints.append(RtScope.Types.FILE)
        self.exec.dispatch(fixture) 

    def test_visit_List(self):
        ast = List(
            items=[
                String("a", 0, 0),
                Identifier("b", 0, 0)
            ],
            row=0, col=0
        )

        self.main_scope.assign("b", "test")

        rt_list = self.exec.dispatch(ast)
        self.assertTrue(rt_list == ["a", "test"])

    def test_visit_Set(self):
        pass

    def test_visit_Block(self):
        pass

    def test_visit_Leave(self):
        pass

    def test_visit_Continue(self):
        pass

    def test_visit_Collect(self):
        pass

    def test_visit_Return(self):
        pass

    def test_visit_Ignore(self):
        pass

    def test_visit_Identifier(self):
        pass

    def test_visit_Catch(self):
        pass

    def test_visit_TryCatch(self):
        pass

    def test_visit_Parameters(self):
        pass

    def test_visit_RestParameter(self):
        pass

    def test_visit_DefineFunction(self):
        pass

    def test_visit_Assignment(self):
        identifier = Identifier(value = "a", row=0, col=0)
        string = String(value = "hello!", row=0, col=0)
        assignment = Assignment(target=identifier, value=string)

        self.exec.dispatch(assignment)

        self.assertEqual(self.main_scope.variables['a'], 'hello!')
 
    def test_visit_Member(self):
        pass

    def test_visit_AssignmentBatch(self):
        pass

    def test_visit_While(self):
        pass

    def test_visit_DoWhile(self):
        pass

    def test_visit_For(self):
        pass

    def test_visit_ForIn(self):
        pass

    def test_visit_If(self):
        pass

    def test_visit_Switch(self):
        pass

    def test_visit_Case(self):
        pass

    def test_visit_SpreadTerm(self):
        pass

    def test_visit_BinaryOperation(self):
        pass

    def test_visit_Arguments(self):
        pass

    def test_visit_Call(self):
        pass

    def test_visit_Subscript(self):
        pass

    def test_visit_SpreadArgs(self):
        pass

    def test_visit_Integer(self):
        pass

    def test_visit_Float(self):
        pass

    def test_visit_String(self):
        pass

    def test_visit_Boolean(self):
        pass

    def test_visit_Hexadecimal(self):
        pass

    def test_visit_BinaryNumber(self):
        pass

    def test_visit_NullValue(self):
        pass

    def test_visit_NoneValue(self):
        pass

