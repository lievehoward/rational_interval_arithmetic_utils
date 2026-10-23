# rational_interval_arithmetic_utils

Guaranteed-enclosure arithmetic for closed intervals whose endpoints are exact rationals (`fractions.Fraction`).

```python
from fractions import Fraction
from rational_interval_arithmetic_utils import RInterval, rinterval

a = RInterval(1, 2)
b = rinterval("1/3", "1/2")
print(a + b)        # [4/3, 5/2]
print(a * b)        # [1/3, 1]
print(a / b)        # [2, 6]
print(a.contains(Fraction(3, 2)))   # True
print(RInterval(-2, 3).hull(RInterval(5, 7)))   # [-2, 7]
```

## Why this exists

Floating-point interval arithmetic gives bounds that are themselves rounded, so a "guaranteed" enclosure can silently exclude the true value. By using `fractions.Fraction` for every endpoint and every intermediate result, the bounds here are exact: no rounding occurs at any step.

The trade-off is speed and memory. Rational arithmetic is slower than float arithmetic and can produce large numerators/denominators under repeated operations. This library is intended for correctness-critical code (certified computation, test oracles, constraint checking) where that cost is acceptable.

## The awkward edge: division by intervals containing zero

`a / b` raises `ZeroDivisionError` whenever `b` contains zero (including when an endpoint is exactly zero). The reciprocal of an interval straddling zero is the union of two disjoint rays, not a single interval, so returning one `RInterval` would misrepresent the mathematics. If you need an enclosure in that situation, split the denominator into sign-pure sub-intervals yourself, divide by each, and take the union of the results.

## Exported names

- `RInterval` — the interval class. Constructor: `RInterval(low, high)` where each endpoint is an `int`, `Fraction`, or `str` (passed to `Fraction`).
- `rinterval(low, high)` — alias constructor.

`RInterval` supports `+`, `-`, `*`, `/`, unary `-`, `abs()`, plus `contains(value)`, `intersects(other)`, `intersect(other)`, `hull(other)`, `midpoint()`, and `width()`. Equality and hashing are by endpoint value.
