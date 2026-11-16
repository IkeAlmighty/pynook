import sys
import unittest
from ir.builder import IRBuilder
from tokenizer import Tokenizer
from parser import Parser

from exceptions.compiler import CompilerException

class TestCompilerException(unittest.TestCase):

    def load_source(self, source):
        tokenizer = Tokenizer(source=source)
        parser = Parser(tokenizer)

        ir_builder = IRBuilder()

        ast = parser.file()

        ir = ir_builder.build(ast)

        return ir

    def load_fixture(self, filepath):
        tokenizer = Tokenizer(filepath=filepath)
        parser = Parser(tokenizer)

        ir_builder = IRBuilder()

        ast = parser.file()

        ir = ir_builder.build(ast)

        return ir

    def test_print_location(self):

        source = None
        try:
            source = self.load_fixture("tests/fixtures/fail/print_location_fixt.nk")
        except CompilerException as e:
            msg = e.get_error_message()
            print(msg, file=sys.stderr)




