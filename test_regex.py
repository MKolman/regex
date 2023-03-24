import unittest

from regex import Regex


class TestBasic(unittest.TestCase):
    def test_has_match(self):
        re = Regex("")
        self.assertTrue(re.match(""))

    def test_trailing_backslash(self):
        re = Regex("a\\\\")
        self.assertTrue(re.match("a\\"))
        self.assertRaisesRegex(
            ValueError,
            "Regex cannot end with a single backslash",
            lambda: Regex("\\"),
        )

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


class TestClojure(unittest.TestCase):
    def test_simple(self):
        re = Regex("pa*b")
        self.assertTrue(re.match("pb"))
        self.assertTrue(re.match("paab"))
        self.assertTrue(re.match("pabb"))
        self.assertFalse(re.match("paxb"))

        re = Regex("aa*")
        self.assertFalse(re.full_match(""))
        self.assertTrue(re.full_match("a"))
        self.assertTrue(re.full_match("aaaaa"))

    def test_grouped(self):
        re = Regex("(aab)*")
        self.assertTrue(re.full_match(""))
        self.assertTrue(re.full_match("aab"))
        self.assertTrue(re.full_match("aabaab"))
        self.assertTrue(re.full_match("aabaabaab"))
        self.assertFalse(re.full_match("aabab"))
        self.assertFalse(re.full_match("aabb"))


class TestOr(unittest.TestCase):
    def test_simpler(self):
        re = Regex("(a|)")
        self.assertTrue(re.full_match("a"))
        self.assertTrue(re.full_match(""))

        re = Regex("(a|b)")
        self.assertTrue(re.full_match("b"))

        re = Regex("(a|bc)")
        self.assertTrue(re.full_match("bc"))

    def test_simple(self):
        re = Regex("(aa*|b|xyz)")
        self.assertTrue(re.full_match("a"))
        self.assertTrue(re.full_match("aaa"))
        self.assertTrue(re.full_match("b"))
        self.assertTrue(re.full_match("xyz"))
        self.assertFalse(re.full_match("xyza"))

    def test_advanced(self):
        re = Regex("((a|b)*|xyz)(p|l)")
        self.assertTrue(re.full_match("al"))
        self.assertTrue(re.full_match("babbabaababp"))
        self.assertTrue(re.full_match("p"))
        self.assertTrue(re.full_match("xyzp"))


class TestOptional(unittest.TestCase):
    def test_simple(self):
        re = Regex("ba?b")
        self.assertTrue(re.full_match("bb"))
        self.assertTrue(re.full_match("bab"))
        self.assertFalse(re.full_match("baab"))
        self.assertFalse(re.full_match("b"))

    def test_bigger(self):
        re = Regex("b?a?b?")
        self.assertTrue(re.full_match("bb"))
        self.assertTrue(re.full_match("bab"))
        self.assertTrue(re.full_match("b"))
        self.assertTrue(re.full_match(""))
        self.assertFalse(re.full_match("baab"))

    def test_debug(self):
        re = Regex("a?")
        self.assertFalse(re.full_match("aa"))


class TestOneOrMore(unittest.TestCase):
    def test_simple(self):
        re = Regex("a+")
        self.assertFalse(re.full_match(""))
        self.assertTrue(re.full_match("a"))
        self.assertTrue(re.full_match("aaaaaa"))


class TestRange(unittest.TestCase):
    def test_simplest(self):
        re = Regex("a{1}")
        self.assertFalse(re.full_match(""))
        self.assertTrue(re.full_match("a"))
        self.assertFalse(re.full_match("aa"))
        self.assertFalse(re.full_match("aaa"))

    def test_simpler(self):
        re = Regex("a{2}")
        self.assertFalse(re.full_match(""))
        self.assertFalse(re.full_match("a"))
        self.assertTrue(re.full_match("aa"))
        self.assertFalse(re.full_match("aaa"))
        self.assertFalse(re.full_match("aaaa"))

    def test_simple(self):
        re = Regex("a{3}")
        self.assertFalse(re.full_match(""))
        self.assertFalse(re.full_match("a"))
        self.assertTrue(re.full_match("aaa"))
        self.assertFalse(re.full_match("aaaa"))

    def test_range(self):
        re = Regex("a{3,5}")
        "aaa(|a|aa) = aaa(|a(|a))"
        "aaa(aa?)?"
        self.assertFalse(re.full_match(""))
        self.assertFalse(re.full_match("a"))
        self.assertTrue(re.full_match("aaa"))
        self.assertTrue(re.full_match("aaaa"))
        self.assertFalse(re.full_match("aaaaaaa"))

    def test_complex(self):
        re = Regex("(ab|xy|p{4}|o+){1,3}")
        self.assertFalse(re.full_match(""))
        self.assertTrue(re.full_match("ab"))
        self.assertTrue(re.full_match("aboooo"))
        self.assertTrue(re.full_match("abppppxy"))
        self.assertFalse(re.full_match("abpppxy"))
        self.assertTrue(re.full_match("xy"))
        self.assertTrue(re.full_match("xyxy"))
        self.assertTrue(re.full_match("xypppp"))
        self.assertTrue(re.full_match("xyppppooooooooooo"))
        self.assertTrue(re.full_match("ooo"))
        self.assertTrue(re.full_match("o"))
        self.assertFalse(re.full_match("abababab"))
        self.assertFalse(re.full_match("ababxyxyxy"))
        self.assertFalse(re.full_match("aboooooaboooxyab"))

    def test_zero_range(self):
        re = Regex("a{0}")
        self.assertTrue(re.full_match(""))
        self.assertFalse(re.full_match("a"))
        self.assertFalse(re.full_match("aa"))
        self.assertFalse(re.full_match("aaa"))
        re = Regex("a{0,3}")
        self.assertTrue(re.full_match(""))
        self.assertTrue(re.full_match("a"))
        self.assertTrue(re.full_match("aa"))
        self.assertTrue(re.full_match("aaa"))
        self.assertFalse(re.full_match("aaaa"))


class TestOneOf(unittest.TestCase):
    def test_simplest(self):
        re = Regex("[a]")
        self.assertTrue(re.full_match("a"))
        self.assertFalse(re.full_match("b"))
        self.assertFalse(re.full_match("c"))

    def test_simpler(self):
        re = Regex("[abc]")
        self.assertTrue(re.full_match("a"))
        self.assertTrue(re.full_match("b"))
        self.assertTrue(re.full_match("c"))
        self.assertFalse(re.full_match("d"))

    def test_star(self):
        re = Regex("[a*bc]")
        self.assertTrue(re.full_match("a"))
        self.assertTrue(re.full_match("*"))
        self.assertTrue(re.full_match("b"))

    def test_complex(self):
        re = Regex("[a-f]")
        self.assertTrue(re.full_match("a"))
        self.assertTrue(re.full_match("b"))
        self.assertTrue(re.full_match("f"))
        self.assertFalse(re.full_match("g"))

    def test_empty(self):
        self.assertRaises(AssertionError, lambda: Regex("[]"))

    def test_advanced(self):
        re = Regex("[A-Fc-z0-5]{0,3}")
        self.assertTrue(re.full_match(""))
        self.assertTrue(re.full_match("ABC"))
        self.assertTrue(re.full_match("ABc"))
        self.assertTrue(re.full_match("3eC"))
        self.assertFalse(re.full_match("F6d"))

    def test_not(self):
        re = Regex("[^X]")
        self.assertTrue(re.full_match("a"))
        self.assertTrue(re.full_match("p"))
        self.assertFalse(re.full_match("X"))
        self.assertFalse(re.full_match("aa"))
        self.assertFalse(re.full_match(""))

    def test_not_complex(self):
        re = Regex("[^ABC]")
        self.assertTrue(re.full_match("D"))
        self.assertTrue(re.full_match("E"))
        self.assertFalse(re.full_match("A"))
        self.assertFalse(re.full_match("B"))
        self.assertFalse(re.full_match("CC"))

    def test_digit(self):
        re = Regex("a\db")
        self.assertTrue(re.full_match("a1b"))
        self.assertTrue(re.full_match("a2b"))
        self.assertFalse(re.full_match("ab3"))

    def test_word(self):
        re = Regex("a\wb")
        self.assertTrue(re.full_match("aab"))
        self.assertTrue(re.full_match("a_b"))
        self.assertTrue(re.full_match("aGb"))
        self.assertTrue(re.full_match("a0b"))
        self.assertFalse(re.full_match("a.b"))
        self.assertFalse(re.full_match("a?b"))
        self.assertFalse(re.full_match("ab"))

    def test_space(self):
        re = Regex(r"a\s\sb")
        self.assertTrue(re.full_match("a  b"))
        self.assertTrue(re.full_match("a\t b"))
        self.assertTrue(re.full_match("a\r\nb"))
        self.assertTrue(re.full_match("a\n\nb"))
        self.assertTrue(re.full_match("a\f b"))
        self.assertFalse(re.full_match("a b"))
        self.assertFalse(re.full_match("a bb"))


class TestBoundary(unittest.TestCase):
    def test_start(self):
        re = Regex("^a")
        self.assertTrue(re.match("a"))
        self.assertTrue(re.match("aa"))
        self.assertFalse(re.match("ba"))
        self.assertFalse(re.match(""))

    def test_end(self):
        re = Regex("a$")
        self.assertTrue(re.match("a"))
        self.assertTrue(re.match("ba"))
        self.assertFalse(re.match("ab"))
        self.assertFalse(re.match(""))


class TestVariables(unittest.TestCase):
    def test_definition(self):
        env = Regex()
        env.vars(
            eightbit="(\d|[1-9]\d|1\d\d|2([0-4]\d|5[0-5]))",
            ip="{eightbit}(\.{eightbit}){3}",
        )
        re = env.compile("\w+@{ip}")
        self.assertTrue(re.full_match("a@1.1.1.1"))


"""
b(?![^@]+@[^@]+).
([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|"([]!#-[^-~ \t]|(\\[\t -~]))+")@([0-9A-Za-z]([0-9A-Za-z-]{0,61}[0-9A-Za-z])?(\.[0-9A-Za-z]([0-9A-Za-z-]{0,61}[0-9A-Za-z])?)*|\[((25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])){3}|IPv6:((((0|[1-9A-Fa-f][0-9A-Fa-f]{0,3}):){6}|::((0|[1-9A-Fa-f][0-9A-Fa-f]{0,3}):){5}|[0-9A-Fa-f]{0,4}::((0|[1-9A-Fa-f][0-9A-Fa-f]{0,3}):){4}|(((0|[1-9A-Fa-f][0-9A-Fa-f]{0,3}):)?(0|[1-9A-Fa-f][0-9A-Fa-f]{0,3}))?::((0|[1-9A-Fa-f][0-9A-Fa-f]{0,3}):){3}|(((0|[1-9A-Fa-f][0-9A-Fa-f]{0,3}):){0,2}(0|[1-9A-Fa-f][0-9A-Fa-f]{0,3}))?::((0|[1-9A-Fa-f][0-9A-Fa-f]{0,3}):){2}|(((0|[1-9A-Fa-f][0-9A-Fa-f]{0,3}):){0,3}(0|[1-9A-Fa-f][0-9A-Fa-f]{0,3}))?::(0|[1-9A-Fa-f][0-9A-Fa-f]{0,3}):|(((0|[1-9A-Fa-f][0-9A-Fa-f]{0,3}):){0,4}(0|[1-9A-Fa-f][0-9A-Fa-f]{0,3}))?::)((0|[1-9A-Fa-f][0-9A-Fa-f]{0,3}):(0|[1-9A-Fa-f][0-9A-Fa-f]{0,3})|(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])){3})|(((0|[1-9A-Fa-f][0-9A-Fa-f]{0,3}):){0,5}(0|[1-9A-Fa-f][0-9A-Fa-f]{0,3}))?::(0|[1-9A-Fa-f][0-9A-Fa-f]{0,3})|(((0|[1-9A-Fa-f][0-9A-Fa-f]{0,3}):){0,6}(0|[1-9A-Fa-f][0-9A-Fa-f]{0,3}))?::)|(?!IPv6:)[0-9A-Za-z-]*[0-9A-Za-z]:[!-Z^-~]+)])

Variables save and insert
Name suggestion: RegExt (extended regex XD)
"""
