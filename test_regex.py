import unittest

from regex import Literal, Regex, fail_table


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


class TestFailTable(unittest.TestCase):
    def test_empty(self):
        self.assertEqual([], fail_table(""))

    def test_simple(self):
        self.assertEqual([None, None, 1], fail_table("aad"))

    def test_medium(self):
        self.assertEqual([None, 0, None, 0, 2], fail_table("ababc"))


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
