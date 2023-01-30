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


class TestBuilder(unittest.TestCase):
    def test_match(self):
        re = Regex._builder("ab")
        self.assertTrue(re.match("ab", 0))

    def test_builder(self):
        re = Regex._builder("asdf")
        self.assertTrue(re.match("asdf", 0))
        self.assertFalse(re.match("asf", 0))


class TestWildcard(unittest.TestCase):
    def test_match(self):
        re = Regex("..")
        self.assertTrue(re.match("abc"))
        self.assertFalse(re.match(""))
        self.assertFalse(re.match("a"))

        re = Regex("a.")
        self.assertTrue(re.match("abc"))
        self.assertTrue(re.match("baba"))
        self.assertFalse(re.match("a"))
        self.assertFalse(re.match("ca"))

    def test_wildcard_backtrace(self):
        re = Regex("a.b")
        self.assertTrue(re.match("aaab"))
        self.assertFalse(re.match("accb"))

        re = Regex("a.a.c")
        self.assertTrue(re.match("aaaaac"))
        self.assertTrue(re.match("aaaaabc"))
        self.assertTrue(re.match("abcabacc"))


class TestOptional(unittest.TestCase):
    def test_simple(self):
        re = Regex("ba?b")
        self.assertTrue(re.match("bb"))
        self.assertTrue(re.match("bab"))
        self.assertFalse(re.match("baab"))
        self.assertFalse(re.match("b"))

    def test_wtf(self):
        re = Regex("ba?a")
        self.assertTrue(re.match("ba"))
        self.assertTrue(re.match("baa"))
        self.assertFalse(re.match("b"))
        self.assertFalse(re.match("aa"))
