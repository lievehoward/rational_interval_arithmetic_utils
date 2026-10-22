"""Exact rational interval arithmetic.

Every endpoint is a :class:`fractions.Fraction`, so every bound computed
here is a *guaranteed* enclosure of the true mathematical result -- there
is no floating-point rounding involved at any stage.

The only design decision that deserves comment is how division is handled.
Division by an interval that straddles zero has no single interval
enclosure: the reciprocal set is the union of two disjoint rays, not an
interval.  Returning a single ``RInterval`` would therefore misrepresent
the mathematics.  Instead :meth:`RInterval.__truediv__` *raises*
``ZeroDivisionError`` when the denominator interval contains zero, even
on one end only.  Callers who need split enclosures should divide the
denominator into sign-pure sub-intervals themselves and take the union of
the results.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Union

Number = Union[int, Fraction, str]


def _to_fraction(x: Number) -> Fraction:
    """Coerce *x* to :class:`~fractions.Fraction`.

    Accepting ``int``, ``Fraction`` and decimal/integer ``str`` lets users
    write ``RInterval(1, 2)`` or ``RInterval('1/3', '0.4')`` without
    thinking about constructor noise.  Anything else is a type error:
    silently converting ``float`` would re-introduce the very rounding
    this library exists to avoid.
    """
    if isinstance(x, Fraction):
        return x
    if isinstance(x, int):
        return Fraction(x)
    if isinstance(x, str):
        return Fraction(x)
    raise TypeError(
        f"endpoint must be int, Fraction, or str, not {type(x).__name__}"
    )


class RInterval:
    """A closed interval ``[lo, hi]`` with exact rational endpoints."""

    __slots__ = ("_lo", "_hi")

    def __init__(self, low: Number, high: Number) -> None:
        lo = _to_fraction(low)
        hi = _to_fraction(high)
        # Ordering is an invariant of the type; enforce it once on entry
        # rather than letting downstream operations produce nonsensical
        # "intervals" with lo > hi.
        if lo > hi:
            raise ValueError(
                f"interval low ({lo}) must not exceed high ({hi})"
            )
        self._lo = lo
        self._hi = hi

    # ------------------------------------------------------------------
    # accessors
    # ------------------------------------------------------------------
    @property
    def low(self) -> Fraction:
        return self._lo

    @property
    def high(self) -> Fraction:
        return self._hi

    # ------------------------------------------------------------------
    # equality / repr
    # ------------------------------------------------------------------
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RInterval):
            return NotImplemented
        return self._lo == other._lo and self._hi == other._hi

    def __hash__(self) -> int:
        return hash((self._lo, self._hi))

    def __repr__(self) -> str:
        return f"RInterval({self._lo!r}, {self._hi!r})"

    def __str__(self) -> str:
        return f"[{self._lo}, {self._hi}]"

    # ------------------------------------------------------------------
    # arithmetic -- binary
    # ------------------------------------------------------------------
    def __add__(self, other: RInterval) -> RInterval:
        if not isinstance(other, RInterval):
            return NotImplemented
        return RInterval(self._lo + other._lo, self._hi + other._hi)

    def __sub__(self, other: RInterval) -> RInterval:
        if not isinstance(other, RInterval):
            return NotImplemented
        # [a,b] - [c,d] = [a-d, b-c]
        return RInterval(self._lo - other._hi, self._hi - other._lo)

    def __mul__(self, other: RInterval) -> RInterval:
        if not isinstance(other, RInterval):
            return NotImplemented
        # Four corner products; the tightest enclosure is simply the min
        # and max of those four values.  This is always correct for exact
        # rationals regardless of sign.
        products = (
            self._lo * other._lo,
            self._lo * other._hi,
            self._hi * other._lo,
            self._hi * other._hi,
        )
        return RInterval(min(products), max(products))

    def __truediv__(self, other: RInterval) -> RInterval:
        if not isinstance(other, RInterval):
            return NotImplemented
        # Division is multiplication by the reciprocal interval.  The
        # reciprocal of [c, d] is [1/d, 1/c] -- *but only when* c and d
        # share the same strict sign.  If zero lies in [c, d] the
        # reciprocal set is not an interval, and we refuse to pretend
        # otherwise.  See the module docstring for the rationale.
        c, d = other._lo, other._hi
        if c <= 0 <= d:
            raise ZeroDivisionError(
                "divisor interval contains zero; "
                "true enclosure is not a single interval"
            )
        recip_lo = Fraction(1) / d
        recip_hi = Fraction(1) / c
        return self * RInterval(recip_lo, recip_hi)

    def __neg__(self) -> RInterval:
        return RInterval(-self._hi, -self._lo)

    def __abs__(self) -> RInterval:
        # abs([a,b]) = [0, max(|a|,|b|)] when the interval straddles 0,
        # otherwise it is [|near end|, |far end|].
        if self._lo >= 0:
            return RInterval(self._lo, self._hi)
        if self._hi <= 0:
            return RInterval(-self._hi, -self._lo)
        return RInterval(Fraction(0), max(-self._lo, self._hi))

    # ------------------------------------------------------------------
    # set-ish operations
    # ------------------------------------------------------------------
    def contains(self, value: Number) -> bool:
        v = _to_fraction(value)
        return self._lo <= v <= self._hi

    def intersects(self, other: RInterval) -> bool:
        return self._lo <= other._hi and other._lo <= self._hi

    def intersect(self, other: RInterval) -> RInterval:
        if not self.intersects(other):
            raise ValueError("intervals do not overlap")
        return RInterval(max(self._lo, other._lo), min(self._hi, other._hi))

    def hull(self, other: RInterval) -> RInterval:
        """Smallest interval containing both *self* and *other*."""
        return RInterval(min(self._lo, other._lo), max(self._hi, other._hi))

    def midpoint(self) -> Fraction:
        return (self._lo + self._hi) / 2

    def width(self) -> Fraction:
        return self._hi - self._lo


def rinterval(low: Number, high: Number) -> RInterval:
    """Concise constructor alias for :class:`RInterval`."""
    return RInterval(low, high)
