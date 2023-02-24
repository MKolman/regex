import unittest

from reparser import Parser, TokenKind, lexer


class TestBasic(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(Parser(lexer("ab")).parse())
