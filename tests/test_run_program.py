import unittest
from runtime.values import *
from nook import run_program

class TestRunProgram(unittest.TestCase):

    # override
    def assertEqual(self, lhs, rhs):
        if lhs in (NkBool, NkInt, NkString, NkScope, NkSet, NkList):
            super().assertTrue(lhs.eq(rhs))

    def test_args(self):
        scope = run_program("""
            a: 5
            b: {}
            c: (){}
            d: (root) {}
            e: args
        """, "arg1", "arg2")
        
        e = scope.resolve("e")
        self.assertEqual(e, NkList([NkString("arg1"), NkString("arg2")]))

    def test_stdlib_compilation(self):

        scope = run_program("""
            a: "hello!"
        """)

        pi = scope.resolve("pi")

        self.assertEqual(pi, NkFloat(3.14159))
        




