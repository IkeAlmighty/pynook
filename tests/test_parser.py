from nast.nodes import *
from parser import Parser
from tokenizer import Tokenizer

from functools import wraps
import unittest
from unittest.mock import patch

class TestParser(unittest.TestCase):
    
    def load_fixture(self, fixture_path):
        with open(fixture_path) as f:
            self.source = f.read()

        self.tokenizer = Tokenizer(self.source)
        self.parser = Parser(self.tokenizer)

    def load_source(self, source):
        self.source = source
        self.tokenizer = Tokenizer(self.source)
        self.parser = Parser(self.tokenizer)
        
    def test_file(self):
        pass

    def test_block(self):
        self.load_fixture("tests/fixtures/pass/test_block.nk")
        block = self.parser._block()

        self.assertTrue(len(block.statements) == 4)
        self.assertTrue(isinstance(block.statements[0], Statement))

    def test_statement(self):
        pass

    def test_scope(self):
        self.load_source("{ a: 5 }")
        scope = self.parser._scope()

        self.assertTrue(isinstance(scope, Scope))

    def test_list(self):
        pass

    def test_set(self):
        pass

    def test_trycatch(self):
        pass

    def test_assignment(self):
        self.load_source("a: 65")
        assignment = self.parser._assignment()
        self.assertTrue(isinstance(assignment, Assignment))
        
        self.load_source("a.b.c: 8 + 3")
        assignment = self.parser._assignment()
        self.assertTrue(isinstance(assignment, Assignment))

        self.load_source("text64: 'hello world';")
        assignment = self.parser._assignment()
        self.assertTrue(isinstance(assignment, Assignment))

        self.load_source("b: a + 2,")
        assignment = self.parser._assignment()
        self.assertTrue(isinstance(assignment, Assignment))

    def test_target(self):
        self.load_source("a.b")
        target = self.parser._target()
        self.assertTrue(isinstance(target, Member))

        self.load_source("a['hello']")
        target = self.parser._target()
        self.assertTrue(isinstance(target, Subscript))

        self.load_source("c[8 + 3]")
        target = self.parser._target()
        self.assertTrue(isinstance(target, Subscript))

        self.load_source("a")
        target = self.parser._target()
        self.assertTrue(isinstance(target, Identifier))

        self.load_source("5 + 6")
        try:
            target = self.parser._target()
        except Exception as e:
            self.assertTrue(isinstance(e, Exception))

    def test_destructure(self):
        pass

    def test_resolve_pattern(self):
        pass

    def test_destruct_scope(self):
        pass

    def test_destruct_list(self):
        pass

    def test_pattern_sequence(self):
        pass

    def test_pattern(self):
        pass

    def test_pattern_obj(self):
        pass

    def test_return(self):
        pass

    def test_collect(self):
        pass

    def test_ignore(self):
        pass

    def test_while(self):
        pass

    def test_dowhile(self):
        pass

    def test_for(self):
        pass

    def test_forin(self):
        pass

    def test_if(self):
        pass

    def test_elif(self):
        pass

    def test_else(self):
        pass

    def test_switch(self):
        pass

    def test_case(self):
        pass

    def test_def_func(self):
        pass

    def test_def_proto(self):
        pass

    def test_params(self):
        pass

    def test_param(self):
        pass

    def test_expr(self):
        pass

    def test_infix(self):
        pass

    def test_term(self):
        pass

    def test_postfix(self):
        pass

    def test_primary(self):
        pass

    def test_call(self):
        pass

    def test_subscript(self):
        pass

    def test_args(self):
        pass

    def test_arg(self):
        pass

    def test_literal(self):
        pass

if __name__ == "__main__":
    unittest.main()

