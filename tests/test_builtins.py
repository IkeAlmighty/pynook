import unittest
from ir.builder import IRBuilder
from vm.interpreter import VirtualMachine
from tokenizer import Tokenizer
from parser import Parser
from runtime.values import *
from runtime.builtins import inject_builtins

class TestBuiltins(unittest.TestCase):

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

        inject_builtins(builtins_scope)

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
    
    def test_nkimport(self):
        scope = self.load_fixture('tests/fixtures/pass/test_import.nk')

        pass

