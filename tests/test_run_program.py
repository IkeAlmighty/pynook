
import unittest
from runtime.values import NkList
from nook import run_program

class TestRunProgram(unittest.TestCase):

    def test_run_program(self):
        scope = run_program("""
            a: 5
            b: {}
            c: (){}
            d: (root) {}
            e: args
        """, "arg1", "arg2")
        
        e = scope.resolve("e")
        self.assertEqual(e, NkList(["arg1", "arg2"]))

