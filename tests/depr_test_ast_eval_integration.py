import os
import io
import unittest
from contextlib import redirect_stdout

from tokenizer import Tokenizer
from parser import Parser
from nast.evaluator import Evaluator
from runtime import Runtime
from runtime.objects import RtFunction, RtScope
from runtime.exceptions import VariableUnresolvable


class TestIntegration(unittest.TestCase):

    def setUp(self):
        self.runtime = Runtime()
        self.evaluator = Evaluator(self.runtime)

    def load_fixture(self, fixture_path):
        with open(fixture_path) as f:
            self.source = f.read()

        self.tokenizer = Tokenizer(self.source)
        self.parser = Parser(self.tokenizer)

    def load_source(self, source):
        self.source = source
        self.tokenizer = Tokenizer(self.source)
        self.parser = Parser(self.tokenizer)

    def test_print(self):
        self.load_source("print('testing the print function')")
        with io.StringIO() as buf, redirect_stdout(buf):
            self.evaluator.dispatch(self.parser.file())

            result = buf.getvalue()
            self.assertEqual(result, 'testing the print function\n')

    def test_import(self):
        filepath="tests/fixtures/pass/test_import.nk"
        self.load_fixture(filepath)

        self.evaluator.name_hints.append(os.path.basename(filepath))
        try:
            with io.StringIO() as buf, redirect_stdout(buf):
                self.evaluator.dispatch(self.parser.file())
                result = buf.getvalue()

            self.assertEqual(result, "goodbye!\nhello from import_a.nk!!\n4564\n")

        finally:
            self.evaluator.name_hints.pop()

    def test_scope(self): 
        self.load_source("a: { b: { c: 'hello!' } }, d: a.b.c")
        #self.load_fixture("tests/fixtures/pass/test_scope.nk")
        scope = self.evaluator.dispatch(self.parser.file())

        self.assertEqual(scope.resolve("d"), 'hello!')

    def test_function(self): 
        self.load_source(
            """
            func: (arg, another_arg) {
                print(arg)
                print(another_arg)
            }

            func("hello", "world")
            """
        )

        with io.StringIO() as buf, redirect_stdout(buf):
            scope = self.evaluator.dispatch(self.parser.file())
            result = buf.getvalue()
            self.assertTrue(isinstance(scope.resolve("func"), RtFunction))
            self.assertEqual(result, 'hello\nworld\n')

    def test_root(self):
        self.load_source(
            """
            test_root: (root) {
                root.a: "123"
                
                method: () {
                    root.a: "567"
                }
            }

            rt: test_root().method()
            a_test: rt.a
            """
        )

        scope = self.evaluator.dispatch(self.parser.file())
        self.assertEqual(scope.resolve("a_test"), "567")

    def test_list(self):
        self.load_source("a: [1, 2, 'hello']")

        scope = self.evaluator.dispatch(self.parser.file())

        self.assertEqual(scope.resolve("a"), [1, 2, 'hello'])

    def test_set(self):
        self.load_source("a_set: set[1, 2, 2, 2]")

        scope = self.evaluator.dispatch(self.parser.file())

        self.assertTrue(len(scope.resolve("a_set")) == 2)
    
    def test_destructure(self):
        self.load_source(
            """
            a: { b: { c: 65, d: 55 }, f: 32 }
            { b: { c, d }, f }: a
            """
        )

        scope = self.evaluator.dispatch(self.parser.file())

        self.assertEqual(scope.resolve("c"), 65)
        self.assertEqual(scope.resolve("d"), 55)
        self.assertEqual(scope.resolve("f"), 32)
        self.assertIsInstance(scope.resolve("a"), RtScope)

        with self.assertRaises(VariableUnresolvable):
            scope.resolve("b")

    def test_while(self):

        self.load_source(
            """
            c: 0
            b: 3
            a: 0
            while (a < b) {
                a: a + 1
                c: c + a
            }
            """
        )

        scope = self.evaluator.dispatch(self.parser.file())
        self.assertEqual(scope.resolve("c"), 6)

    def test_forin(self):

        self.load_source(
            """
            a: [1, 3, 6]
            acc: 0
            for item in a { acc: acc + item } 
            """
        )

        scope = self.evaluator.dispatch(self.parser.file())
        self.assertEqual(scope.resolve("acc"), 10)

    def test_for(self):

        self.load_source(
            """
            a: [1, 3, 6, 5]
            acc: 0
            for i: 0; i < 4; i: i+1 {
                acc: acc + a[i]
            }
            """
        )
        
        scope = self.evaluator.dispatch(self.parser.file())
        self.assertEqual(scope.resolve("acc"), 15)

    def test_switch(self):
        self.load_source(
            """
            a: 'hello'
            c: null

            switch a {
                case 'hello' {
                    a: true
                    b: 55
                    collect
                }

                case true {
                    c: true
                    leave
                }

                collect
            }
            """
        )

        scope = self.evaluator.dispatch(self.parser.file())

        self.assertEqual(scope.resolve("b"), 55)
        self.assertEqual(scope.resolve("c"), True)
        self.assertEqual(scope.resolve("a"), 'hello')
            

