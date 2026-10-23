import unittest
from fractions import Fraction

from rational_interval_arithmetic_utils import RInterval, rinterval


class TestConstruction(unittest.TestCase):
    def test_int_endpoints(self):
        a = RInterval(1, 3)
        self.assertEqual(a.low, Fraction(1))
        self.assertEqual(a.high, Fraction(3))

    def test_str_endpoints(self):
        a = RInterval("1/3", "2/3")
        self.assertEqual(a.low, Fraction(1, 3))
        self.assertEqual(a.high, Fraction(2, 3))

    def test_fraction_endpoints(self):
        a = RInterval(Fraction(1, 10), Fraction(2, 10))
        self.assertEqual(a.low, Fraction(1, 10))
        self.assertEqual(a.high, Fraction(1, 5))

    def test_alias(self):
        self.assertEqual(rinterval(1, 2), RInterval(1, 2))

    def test_inverted_raises(self):
        with self.assertRaises(ValueError):
            RInterval(5, 1)

    def test_degenerate_allowed(self):
        a = RInterval(3, 3)
        self.assertEqual(a.low, a.high)
        self.assertEqual(a.width(), 0)

    def test_float_rejected(self):
        with self.assertRaises(TypeError):
            RInterval(0.1, 0.2)


class TestArithmetic(unittest.TestCase):
    def test_add(self):
        a = RInterval(1, 2)
        b = RInterval(3, 4)
        self.assertEqual(a + b, RInterval(4, 6))

    def test_sub(self):
        a = RInterval(1, 5)
        b = RInterval(2, 3)
        self.assertEqual(a - b, RInterval(-2, 3))

    def test_mul_positive(self):
        self.assertEqual(RInterval(1, 2) * RInterval(3, 4), RInterval(3, 8))

    def test_mul_straddle_zero(self):
        a = RInterval(-2, 3)
        b = RInterval(-1, 4)
        # corners: 2, -8, -3, 12  -> min -8, max 12
        self.assertEqual(a * b, RInterval(-8, 12))

    def test_mul_both_negative(self):
        a = RInterval(-5, -2)
        b = RInterval(-3, -1)
        # corners: 15, 5, 6, 2 -> min 2, max 15
        self.assertEqual(a * b, RInterval(2, 15))

    def test_neg(self):
        self.assertEqual(-RInterval(1, 3), RInterval(-3, -1))

    def test_abs_positive(self):
        self.assertEqual(abs(RInterval(2, 5)), RInterval(2, 5))

    def test_abs_negative(self):
        self.assertEqual(abs(RInterval(-5, -2)), RInterval(2, 5))

    def test_abs_straddle(self):
        self.assertEqual(abs(RInterval(-3, 7)), RInterval(0, 7))

    def test_div_positive(self):
        a = RInterval(1, 2)
        b = RInterval(3, 4)
        # recip(b) = [1/4, 1/3]; a * recip in [1/4, 2/3]
        self.assertEqual(a / b, RInterval(Fraction(1, 4), Fraction(2, 3)))

    def test_div_negative_denominator(self):
        a = RInterval(1, 2)
        b = RInterval(-4, -3)
        # recip = [1/-3, 1/-4] = [-1/3, -1/4]
        # a * recip: corners 1*(-1/3), 1*(-1/4), 2*(-1/3), 2*(-1/4)
        # = -1/3, -1/4, -2/3, -1/2 -> min -2/3, max -1/4
        self.assertEqual(a / b, RInterval(Fraction(-2, 3), Fraction(-1, 4)))

    def test_div_straddle_zero_raises(self):
        with self.assertRaises(ZeroDivisionError):
            RInterval(1, 2) / RInterval(-1, 1)

    def test_div_contains_zero_raises(self):
        with self.assertRaises(ZeroDivisionError):
            RInterval(1, 2) / RInterval(0, 1)

    def test_div_degenerate_zero_raises(self):
        with self.assertRaises(ZeroDivisionError):
            RInterval(1, 2) / RInterval(0, 0)


class TestProperties(unittest.TestCase):
    def test_contains_true(self):
        self.assertTrue(RInterval(1, 3).contains(2))

    def test_contains_endpoint(self):
        self.assertTrue(RInterval(1, 3).contains(1))
        self.assertTrue(RInterval(1, 3).contains(3))

    def test_contains_false(self):
        self.assertFalse(RInterval(1, 3).contains(4))

    def test_contains_fraction(self):
        self.assertTrue(RInterval(1, 2).contains(Fraction(3, 2)))

    def test_intersects_yes(self):
        self.assertTrue(RInterval(1, 3).intersects(RInterval(2, 5)))

    def test_intersects_touching(self):
        self.assertTrue(RInterval(1, 3).intersects(RInterval(3, 5)))

    def test_intersects_no(self):
        self.assertFalse(RInterval(1, 2).intersects(RInterval(3, 4)))

    def test_intersect(self):
        self.assertEqual(
            RInterval(1, 4).intersect(RInterval(3, 6)),
            RInterval(3, 4),
        )

    def test_intersect_disjoint_raises(self):
        with self.assertRaises(ValueError):
            RInterval(1, 2).intersect(RInterval(3, 4))

    def test_hull(self):
        self.assertEqual(
            RInterval(1, 2).hull(RInterval(5, 7)),
            RInterval(1, 7),
        )

    def test_midpoint(self):
        self.assertEqual(RInterval(1, 3).midpoint(), Fraction(2))

    def test_midpoint_fraction(self):
        self.assertEqual(RInterval(1, 2).midpoint(), Fraction(3, 2))

    def test_width(self):
        self.assertEqual(RInterval(1, 4).width(), Fraction(3))


class TestEquality(unittest.TestCase):
    def test_eq(self):
        self.assertEqual(RInterval(1, 2), RInterval(1, 2))

    def test_neq(self):
        self.assertNotEqual(RInterval(1, 2), RInterval(1, 3))

    def test_eq_wrong_type(self):
        self.assertNotEqual(RInterval(1, 2), "x")

    def test_hash(self):
        s = {RInterval(1, 2), RInterval(1, 2), RInterval(3, 4)}
        self.assertEqual(len(s), 2)


class TestRepr(unittest.TestCase):
    def test_repr(self):
        self.assertEqual(repr(RInterval(1, 2)), "RInterval(Fraction(1, 1), Fraction(2, 1))")

    def test_str(self):
        self.assertEqual(str(RInterval(1, 2)), "[1, 2]")


if __name__ == "__main__":
    unittest.main()
