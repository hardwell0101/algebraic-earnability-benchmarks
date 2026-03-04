#!/usr/bin/env python3
"""
BS(1,2) group arithmetic and identity testing.

BS(1,2) = <a, b | bab^{-1} = a^2>

Uses the faithful matrix representation:
    a -> [[1, 1], [0, 1]]
    b -> [[2, 0], [0, 1]]

Each element is represented as (s, r) corresponding to matrix [[2^s, r], [0, 1]]
where s is an integer and r is a dyadic rational (Python Fraction).

Multiplication: (s1, r1) * (s2, r2) = (s1 + s2, 2^s1 * r2 + r1)
Identity: (0, 0)
Inverse of (s, r): (-s, -r * 2^(-s))
"""

from fractions import Fraction


class BS12Element:
    """Element of BS(1,2) via faithful 2x2 matrix representation."""

    __slots__ = ('s', 'r')

    def __init__(self, s=0, r=None):
        self.s = s
        self.r = Fraction(r) if r is not None else Fraction(0)

    @staticmethod
    def identity():
        return BS12Element(0, Fraction(0))

    @staticmethod
    def generator(name):
        if name == 'a':
            return BS12Element(0, Fraction(1))
        elif name == 'A':
            return BS12Element(0, Fraction(-1))
        elif name == 'b':
            return BS12Element(1, Fraction(0))
        elif name == 'B':
            return BS12Element(-1, Fraction(0))
        else:
            raise ValueError(f"Unknown generator: {name}")

    def __mul__(self, other):
        # [[2^s1, r1],[0,1]] * [[2^s2, r2],[0,1]] = [[2^(s1+s2), 2^s1*r2 + r1],[0,1]]
        new_s = self.s + other.s
        if self.s >= 0:
            scale = Fraction(1 << self.s)          # 2^s as integer
        else:
            scale = Fraction(1, 1 << (-self.s))    # 1 / 2^|s|
        new_r = scale * other.r + self.r
        return BS12Element(new_s, new_r)

    def inverse(self):
        neg_s = -self.s
        if neg_s >= 0:
            scale = Fraction(1 << neg_s)
        else:
            scale = Fraction(1, 1 << (-neg_s))
        return BS12Element(neg_s, -self.r * scale)

    def __eq__(self, other):
        if not isinstance(other, BS12Element):
            return NotImplemented
        return self.s == other.s and self.r == other.r

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.s, self.r))

    def __repr__(self):
        m, k, n = self.normal_form()
        if m == 0 and k == 0 and n == 0:
            return "BS12(identity)"
        parts = []
        if m > 0:
            parts.append(f"B^{m}")
        if k != 0:
            parts.append(f"a^{k}")
        if n > 0:
            parts.append(f"b^{n}")
        return f"BS12({' '.join(parts)})"

    def is_identity(self):
        return self.s == 0 and self.r == 0

    def normal_form(self):
        """
        Returns (m, k, n) with m, n >= 0 such that element = B^m * a^k * b^n.

        Uses minimal m (and consequently minimal n) for uniqueness.
        The matrix is [[2^(n-m), k/2^m], [0, 1]], so:
            s = n - m
            r = k / 2^m
        """
        if self.r == 0:
            if self.s >= 0:
                return (0, 0, self.s)
            else:
                return (-self.s, 0, 0)

        num = self.r.numerator    # odd integer (Fraction auto-reduces)
        den = self.r.denominator  # power of 2

        # Find q such that den = 2^q
        q = 0
        d = den
        while d > 1:
            d >>= 1
            q += 1

        # m = max(q, -s) ensures k is integer and n >= 0
        m = max(q, -self.s)
        k = num * (1 << (m - q))
        n = m + self.s

        return (m, k, n)


def parse_word(word_string):
    """Parse a space-separated word string into a BS12Element."""
    word_string = word_string.strip()
    if not word_string or word_string == 'e':
        return BS12Element.identity()
    tokens = word_string.split()
    result = BS12Element.identity()
    for token in tokens:
        result = result * BS12Element.generator(token)
    return result


def bs12_normal_form(word_string):
    """Compute normal form (m, k, n) of a word in BS(1,2)."""
    return parse_word(word_string).normal_form()


def elements_equal(word1, word2):
    """Check if two words represent the same BS(1,2) element."""
    return parse_word(word1) == parse_word(word2)


def multiply_words(word1, word2):
    """Normal form of the product (concatenation) of two words."""
    return (parse_word(word1) * parse_word(word2)).normal_form()


def element_to_word(element):
    """Convert a BS12Element to a word string in normal form."""
    m, k, n = element.normal_form()
    tokens = []
    tokens.extend(['B'] * m)
    if k > 0:
        tokens.extend(['a'] * k)
    elif k < 0:
        tokens.extend(['A'] * (-k))
    tokens.extend(['b'] * n)
    return ' '.join(tokens) if tokens else 'e'


def normal_form_to_element(m, k, n):
    """Construct a BS12Element from normal form (m, k, n)."""
    s = n - m
    r = Fraction(k, 1 << m) if m > 0 else Fraction(k)
    return BS12Element(s, r)


if __name__ == '__main__':
    print("=" * 60)
    print("BS(1,2) IDENTITY TESTS")
    print("=" * 60)

    # Test 1: a * A = identity
    nf = bs12_normal_form("a A")
    print(f"\n1. 'a A' normal form: {nf}")
    assert nf == (0, 0, 0), f"Expected (0,0,0), got {nf}"
    print("   PASS: a * a^-1 = identity")

    # Test 2: b * B = identity
    nf = bs12_normal_form("b B")
    print(f"\n2. 'b B' normal form: {nf}")
    assert nf == (0, 0, 0), f"Expected (0,0,0), got {nf}"
    print("   PASS: b * b^-1 = identity")

    # Test 3: b a B = a^2
    nf = bs12_normal_form("b a B")
    print(f"\n3. 'b a B' normal form: {nf}")
    assert nf == (0, 2, 0), f"Expected (0,2,0), got {nf}"
    eq = elements_equal("b a B", "a a")
    print(f"   'b a B' == 'a a': {eq}")
    assert eq, "Expected bab^-1 = a^2"
    print("   PASS: bab^-1 = a^2")

    # Test 4: b b a B B = a^4
    nf = bs12_normal_form("b b a B B")
    print(f"\n4. 'b b a B B' normal form: {nf}")
    assert nf == (0, 4, 0), f"Expected (0,4,0), got {nf}"
    eq = elements_equal("b b a B B", "a a a a")
    print(f"   'b b a B B' == 'a a a a': {eq}")
    assert eq, "Expected b^2 a b^-2 = a^4"
    print("   PASS: b^2 a b^-2 = a^4")

    print(f"\n{'=' * 60}")
    print("ADDITIONAL TESTS")
    print("=" * 60)

    # Test 5: Associativity
    e1 = parse_word("a b")
    e2 = parse_word("B a")
    e3 = parse_word("b b")
    lhs = (e1 * e2) * e3
    rhs = e1 * (e2 * e3)
    print(f"\n5. Associativity: ((ab)(Ba))(bb) vs (ab)((Ba)(bb))")
    print(f"   LHS: {lhs}")
    print(f"   RHS: {rhs}")
    assert lhs == rhs, "Associativity failed"
    print("   PASS")

    # Test 6: Element * inverse = identity
    e = parse_word("a b B a A")
    e_inv = e.inverse()
    product = e * e_inv
    print(f"\n6. Element * inverse = identity")
    print(f"   Element: {e}")
    print(f"   Inverse: {e_inv}")
    print(f"   Product: {product}")
    assert product.is_identity(), "Inverse test failed"
    print("   PASS")

    # Test 7: Inverse * element = identity (right inverse)
    product2 = e_inv * e
    print(f"\n7. Inverse * element = identity")
    print(f"   Product: {product2}")
    assert product2.is_identity(), "Right inverse test failed"
    print("   PASS")

    # Test 8: Relation ba^n B = a^(2n) for n=1..5
    print(f"\n8. Relation verification: b a^n B = a^(2n)")
    for n_val in range(1, 6):
        word = "b " + " ".join(["a"] * n_val) + " B"
        target = " ".join(["a"] * (2 * n_val))
        eq = elements_equal(word, target)
        print(f"   b a^{n_val} B = a^{2*n_val}: {eq}")
        assert eq, f"Relation failed for n={n_val}"
    print("   PASS")

    # Test 9: multiply_words
    nf = multiply_words("a b", "B a")
    manual = parse_word("a b B a")
    print(f"\n9. multiply_words('a b', 'B a') = {nf}")
    print(f"   Direct parse of 'a b B a' = {manual.normal_form()}")
    assert nf == manual.normal_form()
    print("   PASS")

    # Test 10: element_to_word roundtrip
    print(f"\n10. element_to_word roundtrip tests:")
    test_words = ["a a b", "B B a a a", "b b b", "B a a b b", "A A A"]
    for w in test_words:
        elem = parse_word(w)
        word_out = element_to_word(elem)
        elem2 = parse_word(word_out)
        print(f"    '{w}' -> {elem} -> '{word_out}' -> {elem2}: eq={elem == elem2}")
        assert elem == elem2, f"Roundtrip failed for '{w}'"
    print("   PASS")

    # Test 11: normal_form_to_element roundtrip
    print(f"\n11. normal_form_to_element roundtrip tests:")
    test_nfs = [(0, 0, 0), (0, 5, 0), (2, 3, 1), (0, -4, 3), (3, 4, 0)]
    for m, k, n in test_nfs:
        elem = normal_form_to_element(m, k, n)
        nf = elem.normal_form()
        # The roundtripped normal form should give the same element
        elem2 = normal_form_to_element(*nf)
        print(f"    ({m},{k},{n}) -> {elem} -> nf={nf} -> eq={elem == elem2}")
        assert elem == elem2, f"Roundtrip failed for ({m},{k},{n})"
    print("   PASS")

    # Test 12: b^3 a B^3 = a^8
    nf = bs12_normal_form("b b b a B B B")
    print(f"\n12. 'b b b a B B B' normal form: {nf}")
    assert nf == (0, 8, 0), f"Expected (0,8,0), got {nf}"
    eq = elements_equal("b b b a B B B", " ".join(["a"] * 8))
    assert eq
    print("    PASS: b^3 a b^-3 = a^8")

    print(f"\n{'=' * 60}")
    print("ALL TESTS PASSED")
    print("=" * 60)
