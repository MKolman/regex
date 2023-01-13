import unittest

from regex import Literal, Regex


class TestBasic(unittest.TestCase):
    def test_has_match(self):
        re = Regex("")
        self.assertTrue(re.match(""))

    def test_no_match(self):
        re = Regex("a")
        self.assertFalse(re.match(""))

    def test_literal(self):
        re = Regex("asdf")
        self.assertFalse(re.match(""))
        self.assertFalse(re.match("jsadkhfg"))
        self.assertTrue(re.match("asdf"))
        self.assertTrue(re.match("jsdhfgasdf"))
        self.assertTrue(re.match("asdfsdjkh"))
        self.assertTrue(re.match("mdsbasdfsdjkh"))
    
    def test_self_similar(self):
        re = Regex("ab")
        self.assertTrue(re.match("aab"))


class TestLiteral(unittest.TestCase):

    def test_match(self):
        l = Literal({"a": Literal({"b": Literal({}, True)})})
        self.assertTrue(l.match("ab", 0))

    def test_match_final(self):
        self.assertTrue(Literal({}, True))

    def test_builder(self):
        re = Literal.builder("asdf")
        self.assertTrue(re.match("asdf", 0))
