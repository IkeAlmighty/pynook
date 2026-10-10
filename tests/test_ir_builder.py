
import unittest
from pprint import pprint
from ir.builder import IRBuilder
from ir.instructions import *
from ir.serializer import IRSerializer
from nast.nodes import *

class TestIRBuilder(unittest.TestCase):

    def setUp(self):
        self.builder = IRBuilder()

    def test___emit_load(self):
        # test on single identifier node
        ast = Identifier("test", 0, 0)
        definition = self.builder.build(ast)
        self.assertEqual(definition.instructions, [ Load("test") ])


        # test on a member chain:
        self.builder = IRBuilder()
        ast = Member(
            target=Identifier("test", 0, 0),
            name=Identifier("member_test", 0, 0)
        )

        definition = self.builder.build(ast)
        self.assertEqual(
            definition.instructions,
            [ Load("test"), LoadMember("member_test") ]
        )

    def test___emit_store(self):
        # test on single identifier node
        ast = Assignment(
            target=Member(
                target=Identifier("member_name", 0, 0),
                name=Identifier("owner_name", 0, 0)
            ),
            value=Identifier("test_value", 0, 0)
        )

        definition = self.builder.build(ast)
        self.assertEqual(
            definition.instructions,
            [ Load("test_value"), Load("member_name"), StoreMember("owner_name") ]
        )

    def test_visit_Scope(self):
        ast = Scope(
            Block(
                [
                    String("hello", 0, 0),
                    String("world", 0, 0),
                    String("!!!!", 0, 0),
                ]
            ), 0, 0
        )

        # TODO:


    def test_visit_Block(self):
        pass
        
    def test_visit_Set(self):
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

    def test_visit_Throw(self):
        pass

    def test_visit_TryCatch(self):
        pass

    def test_visit_Parameters(self):
        pass

    def test_visit_Parameter(self):
        pass

    def test_visit_RestParameter(self):
        pass

    def test_visit_DefineFunction(self):
        pass

    def test_visit_Assignment(self):
        pass
        
    def test_visit_Member(self):
        pass

    def test_visit_AssignmentBatch(self):
        pass

    def test_visit_While(self):
        pass

    def test_visit_For(self):
        pass

    def test_visit_ForIn(self):
        pass

    def test_visit_If(self):
        node = If(
            condition=Boolean(False, 0, 0),
            then_scope=Scope(Block([String("hello", 0, 0)]), 0, 0),
            elifs=[
                If(Boolean(False, 0, 0), Scope(Block([String("a", 0, 0)]), 0, 0), [], None), 
                If(Boolean(False, 0, 0), Scope(Block([String("b", 0, 0)]), 0, 0), [], None), 
                If(Boolean(False, 0, 0), Scope(Block([String("c", 0, 0)]), 0, 0), [], None)
            ],
            else_scope=None
        )

        result = self.builder.build(node)

    def test_visit_Switch(self):
        pass

    def test_visit_Case(self):
        pass

    def test_visit_Default(self):
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
