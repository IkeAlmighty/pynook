import unittest
from vm.interpreter import VM
from ir.instructions import *
from runtime.values import *
from ir.definitions import ScopeDefinition

class TestVM(unittest.TestCase):

    def setUp(self):
        self.vm = VM()

    def load(self, instructions):
        scope = ScopeDefinition()
        scope.instructions = instructions

        return scope

    def test_assign(self):
        scope_def = self.load([
            PushConst(NkInt(5)),
            Store("a"),
            Load("a"),
            Store("b")
        ])

        self.vm.execute(scope_def)
        self.assertEqual(self.vm.scope.members['a'], NkInt(5))
        self.assertEqual(self.vm.scope.members['b'], NkInt(5))

