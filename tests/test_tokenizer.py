from tokenizer import *

from functools import wraps
import unittest
from unittest.mock import patch

class TestTokenizer(unittest.TestCase):

    def load_fixture(self, fixture_path):
        with open(fixture_path) as f:
            self.source = f.read()

        self.tokenizer = Tokenizer(self.source)

    def load_source(self, source):
        self.source = source
        self.tokenizer = Tokenizer(self.source)

    def test_identifier(self):
        self.load_source("a: 1")

        token_types = []
        for i in range(3):
            token_types.append(self.tokenizer.next().type)

        self.assertEqual(token_types, [
            TokenTypes.IDENTIFIER,
            TokenTypes.COLON,
            TokenTypes.INT
        ])

        
    def test_lparen(self):
        self.load_source("((( \t(( (( ((")
        tokentype = self.tokenizer.next().type
        while tokentype != TokenTypes.EOF:
            self.assertEqual(tokentype, TokenTypes.LPAREN)
            tokentype = self.tokenizer.next().type

        self.load_source("))       ))))))")
        tokentype = self.tokenizer.next().type
        while tokentype != TokenTypes.EOF:
            self.assertNotEqual(tokentype, TokenTypes.LPAREN)
            tokentype = self.tokenizer.next().type


    def test_rparen(self):
        self.load_source("))       ))\t))))")
        tokentype = self.tokenizer.next().type
        while tokentype != TokenTypes.EOF:
            self.assertEqual(tokentype, TokenTypes.RPAREN)
            tokentype = self.tokenizer.next().type

        # test that leading space is parsed correctly
        self.load_source("    ))       ))))))")
        tokentype = self.tokenizer.next().type
        while tokentype != TokenTypes.EOF:
            self.assertEqual(tokentype, TokenTypes.RPAREN)
            tokentype = self.tokenizer.next().type

        self.load_source("(((")
        tokentype = self.tokenizer.next().type
        while tokentype != TokenTypes.EOF:
            self.assertNotEqual(tokentype, TokenTypes.RPAREN)
            tokentype = self.tokenizer.next().type

    def test_lbracket(self):
        self.load_source("[[[[[ [[\t[[[[")
        tokentype = self.tokenizer.next().type
        while tokentype != TokenTypes.EOF:
            self.assertEqual(tokentype, TokenTypes.LBRACKET)
            tokentype = self.tokenizer.next().type


    def test_rbracket(self):
        pass
    
    def test_lbrace(self):
        pass

    def test_rbrace(self):
        pass

    def test_colon(self):
        self.load_source("a: b()")
        tokentypes = [
            self.tokenizer.next().type, 
            self.tokenizer.next().type, 
            self.tokenizer.next().type,
            self.tokenizer.next().type,
            self.tokenizer.next().type
        ]
        
        self.assertEqual(tokentypes, [
            TokenTypes.IDENTIFIER,
            TokenTypes.COLON,
            TokenTypes.IDENTIFIER,
            TokenTypes.LPAREN,
            TokenTypes.RPAREN
        ])

    def test_comma(self):
        pass

    def test_nospace(self):
        pass

    def test_newline(self):
        pass

    def test_semicolon(self):
        pass

    def test_int(self):
        fail_cases = [
            "01sdf: 1",
            "01(33)",
            "22264[456", 
            "4564.4564.444"
        ]

        for case in fail_cases:
            self.load_source(case)

            with self.assertRaises(InvalidNumber):
                self.tokenizer.next()

        pass_cases = [
            "4567545",
            "6600004",
            "0004"
        ]

        for case in pass_cases:
            self.load_source(case)
            token = self.tokenizer.next()

            self.assertEqual(int(token.value), int(case))

    def test_float(self):
        fail_cases = [
            "777.555.5",
            "77.55[ss", 
        ]

        for case in fail_cases:
            self.load_source(case)

            with self.assertRaises(InvalidNumber):
                self.tokenizer.next()

        pass_cases = [
            "456.55", 
            "000.45",
            "4040.00000001"
        ]
        for case in pass_cases:
            self.load_source(case)
            token = self.tokenizer.next()

            self.assertEqual(float(token.value), float(case))

    def test_string(self):
        pass

    def test_binary(self):
        pass

    def test_hexadecimal(self):
        pass

    def test_none(self):
        pass

    def test_null(self):
        pass

    def test_spread(self):
        pass

    def test_dot(self):
        pass

    def test_eof(self):
        pass

    def test_kw_ignore(self):
        pass

    def test_kw_collect(self):
        pass

    def test_kw_return(self):
        pass

    def test_kw_set(self):
        pass

    def test_kw_self(self):
        pass

    def test_kw_leave(self):
        pass

    def test_kw_try(self):
        pass

    def test_kw_catch(self):
        pass

    def test_kw_finally(self):
        pass

    def test_kw_for(self):
        pass

    def test_kw_in(self):
        pass

    def test_kw_while(self):
        pass

    def test_kw_do(self):
        pass
    
    def test_kw_if(self):
        pass

    def test_kw_else(self):
        pass

    def test_kw_switch(self):
        pass

    def test_kw_case(self):
        pass

    def test_kw_default(self):
        pass

    def test_kw_continue(self):
        pass

    def test_sub(self):
        pass

    def test_add(self):
        pass

    def test_div(self):
        pass

    def test_mult(self):
        pass

    def test_exponent(self):
        pass
    
    def test_modulo(self):
        pass

    def test_xor(self):
        pass

    def test_bw_and(self):
        pass

    def test_bw_or(self):
        pass

    def test_and(self):
        pass

    def test_or(self):
        pass

    def test_negate(self):
        pass

    def test_size(self):
        pass

    def test_eq(self):
        pass

    def test_not_eq(self):
        pass

    def test_greater_eq(self):
        pass

    def test_less_eq(self):
        pass

    def test_less(self):
        pass

    def test_greater(self):
        pass

    def test_scope_fixture_tokenization(self):
        self.load_fixture("tests/fixtures/pass/test_scope.nk")
        token = self.tokenizer.next()
        while token.type != TokenTypes.EOF:
            token = self.tokenizer.next()
        

