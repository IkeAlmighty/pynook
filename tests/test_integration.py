import unittest
from ir.builder import IRBuilder
from vm.interpreter import VirtualMachine
from tokenizer import Tokenizer
from parser import Parser
from runtime.values import *

class TestIntegration(unittest.TestCase):

    def setUp(self): pass

    def load_source(self, source):
        source = source
        tokenizer = Tokenizer(source)
        parser = Parser(tokenizer)

        ir_builder = IRBuilder()

        ast = parser.file()

        ir = ir_builder.build(ast)

        vm = VirtualMachine()

        builtins_scope = NkScope(
            parent=None,
            body_definition=ir,
            parameter_definition=None,
            name='__builtins__'
        )

        vm.execute(builtins_scope, ir)

        file_scope = vm.stack.pop()
        file_scope.set_as_file_scope()
        file_scope.name = "test_filescope"
        file_scope.members['__name__'] = file_scope.name

        return file_scope

    def load_fixture(self, filepath):
        with open(filepath) as f:
            source = f.read()
            return self.load_source(source)

    def test_load_source(self):
        scope = self.load_source("a: 5")

        self.assertEqual(scope.resolve("a"), NkInt(5))
    
    def test_reserved_names(self):
        scope = self.load_source("a: 5")

        self.assertEqual(scope.resolve("__file__").name, scope.name)
        self.assertEqual(scope.resolve("__main__").name, scope.name)
        self.assertEqual(scope.resolve("__scope__").name, scope.name)
        self.assertEqual(scope.resolve("__parent__"), scope.parent)
        self.assertEqual(scope.resolve("__name__"), scope.name)


    def test_multiple_assignments(self):
        scope = self.load_source("""
            a: 1
            b: 2
            c: 3
        """)

        self.assertEqual(scope.resolve("a"), NkInt(1))
        self.assertEqual(scope.resolve("b"), NkInt(2))
        self.assertEqual(scope.resolve("c"), NkInt(3))



    def test_nested_scope(self):
        scope = self.load_source("""
            a: {
                b: 5
            }
        """)

        a = scope.resolve("a")

        self.assertEqual(
            a.resolve("b"),
            NkInt(5)
        )

    def test_file_scope_parent(self):
        scope = self.load_source("a: 5")

        self.assertEqual(
            scope.parent.name,
            "__builtins__"
        )

    def test_parent_scope_resolution(self):
        scope = self.load_source("""
            a: 5

            b: {
                c: a
            }
        """)

        b = scope.resolve("b")

        self.assertEqual(
            b.resolve("c"),
            NkInt(5)
        )

    def test_list_creation(self):
        scope = self.load_source("""
            a: [1, 2, 3]
        """)

        self.assertEqual(
            scope.resolve("a"),
            NkList([
                NkInt(1),
                NkInt(2),
                NkInt(3)
            ])
        )

    def test_set_creation(self):
        scope = self.load_source("""
            a: set[1, 2, 3, 3]
        """)

        self.assertEqual(
            scope.resolve("a"),
            NkSet([
                NkInt(1),
                NkInt(2),
                NkInt(3)
            ])
        )

        self.assertNotEqual(
            scope.resolve("a"),
            NkSet([
                NkInt(1),
                NkInt(2),
                NkInt(3),
                NkInt(4)
            ])
        )

    def test_string_assignment(self):
        scope = self.load_source("""
            "a-1": 6
        """)

        self.assertEqual(
            scope.resolve("a-1"),
            NkInt(6)
        )

    def test_if_statement(self):
        scope = self.load_source("""
            a: 2
            if a == 2 {
                a: 3
            }
        """)

        self.assertEqual(
            scope.resolve("a"),
            NkInt(3)
        )

        scope = self.load_source("""
            a: 1
            if a == 2 {
                a: 4
            }
        """)

        self.assertEqual(
            scope.resolve("a"),
            NkInt(1)
        )

        scope = self.load_source("""
            if true {
                helper: 5
            }
        """)

        with self.assertRaises(Exception):
            scope.resolve("helper")

    def test_while_statement(self):
        scope = self.load_source("""
            a: 0
            while a < 10 {
                a: a + 1
            }
        """)

        self.assertEqual(scope.resolve("a"), NkInt(10))
