
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
        scope = self.load([
            PushConst(NkInt(5)),
            Store("a"),
            Load("a"),
            Store("b")
        ])

        self.vm.execute(scope)

        print(self.vm.scope.members)
