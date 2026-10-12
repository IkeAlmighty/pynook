import unittest
from runtime.values import NkList, NkFloat
from nook import run_program

class TestRunProgram(unittest.TestCase):

    def test_args(self):
        scope = run_program("""
            a: 5
            b: {}
            c: (){}
            d: (root) {}
            e: args
        """, "arg1", "arg2")
        
        e = scope.resolve("e")
        self.assertEqual(e, NkList(["arg1", "arg2"]))

    def test_stdlib_compilation(self):

        scope = run_program("""
            a: "hello!"
        """)

        pi = scope.resolve("pi")

        self.assertEqual(pi, NkFloat(3.14159))
        




