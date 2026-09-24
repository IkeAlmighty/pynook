import unittest
from runtime import Runtime

class TestRuntime(unittest.TestCase):

    def test_assign_core_functions(self):
        runtime = Runtime()
        
        expected_names = [
            'import',
            'print'
        ]

        for name in expected_names:
            self.assertIsNotNone(runtime.main_scope.variables[name])


