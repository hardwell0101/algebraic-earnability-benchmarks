"""Thompson's group F identity test via normal form algorithm."""

import re
from typing import List, Tuple, Union

# Word = list of (index, sign) tuples
Word = List[Tuple[int, int]]


def parse_word(word_string: str) -> Word:
    """Parse string to (index, sign) tuples."""
    if not word_string or not word_string.strip():
        return []

    result = []
    pattern = r'([xX])(\d+)'
    for match in re.finditer(pattern, word_string):
        letter, index = match.groups()
        sign = 1 if letter == 'x' else -1
        result.append((int(index), sign))
    return result


def word_to_string(word: Word) -> str:
    """Convert tuples to string."""
    if not word:
        return ''
    parts = []
    for idx, sign in word:
        letter = 'x' if sign == 1 else 'X'
        parts.append(f"{letter}{idx}")
    return ' '.join(parts)


def expand_higher_generators(word: Word) -> Word:
    """Expand x_n (n>=2) to x0,x1 basis."""
    result = []
    for idx, sign in word:
        if idx <= 1:
            # x0, x1, X0, X1 unchanged
            result.append((idx, sign))
        else:
            # x_n (n >= 2): X0^(n-1) x1 x0^(n-1)
            # X_n (n >= 2): X0^(n-1) X1 x0^(n-1)
            n = idx
            # Add X0^(n-1)
            for _ in range(n - 1):
                result.append((0, -1))
            # Add x1 or X1 (keeping the original sign)
            result.append((1, sign))
            # Add x0^(n-1)
            for _ in range(n - 1):
                result.append((0, 1))
    return result


def free_reduce(word: Word) -> Word:
    """Cancel adjacent inverses."""
    stack = []
    for gen in word:
        if stack and stack[-1][0] == gen[0] and stack[-1][1] == -gen[1]:
            # Adjacent inverses: cancel
            stack.pop()
        else:
            stack.append(gen)
    return stack


def apply_fold(word: Word) -> Tuple[Word, bool]:
    """Apply X0 x_n x0 -> x_{n+1} folding."""
    if len(word) < 3:
        return word, False

    for i in range(len(word) - 2):
        g1, g2, g3 = word[i], word[i+1], word[i+2]

        # Check for X0 ... x0 pattern
        if g1 == (0, -1) and g3 == (0, 1):
            idx, sign = g2
            if idx >= 1:  # x_n or X_n with n >= 1
                # Fold: replace three generators with one
                new_gen = (idx + 1, sign)
                new_word = word[:i] + [new_gen] + word[i+3:]
                return new_word, True

    return word, False


def apply_unfold(word: Word) -> Tuple[Word, bool]:
    """Unfold x_n -> X0 x_{n-1} x0 if beneficial."""
    if len(word) < 2:
        return word, False

    for i in range(len(word)):
        idx, sign = word[i]
        if idx >= 2:
            # Check if unfolding might help
            # Unfold if adjacent generator might cancel with X0 or x0
            should_unfold = False

            # Check left neighbor
            if i > 0:
                left_idx, left_sign = word[i-1]
                if left_idx == 0 and left_sign == 1:  # x0 on left
                    should_unfold = True

            # Check right neighbor
            if i < len(word) - 1:
                right_idx, right_sign = word[i+1]
                if right_idx == 0 and right_sign == -1:  # X0 on right
                    should_unfold = True

            if should_unfold:
                # x_n -> X0 x_{n-1} x0
                # X_n -> X0 X_{n-1} x0
                expansion = [(0, -1), (idx - 1, sign), (0, 1)]
                new_word = word[:i] + expansion + word[i+1:]
                return new_word, True

    return word, False


def reduce_word(word: Word) -> Word:
    """Fully reduce word."""
    word = expand_higher_generators(word)

    max_iterations = 1000
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        old_len = len(word)

        # Free reduction
        word = free_reduce(word)

        # Try folding
        word, fold_changed = apply_fold(word)
        if fold_changed:
            continue

        # Try unfolding if no folding occurred
        word, unfold_changed = apply_unfold(word)
        if unfold_changed:
            # After unfold, try to reduce again
            word = free_reduce(word)
            continue

        # No changes, we're done
        if len(word) == old_len:
            break

    return word


def to_normal_form(word: Word) -> Word:
    """Transform to normal form."""
    word = reduce_word(word)

    if not word:
        return []

    max_iterations = len(word) * len(word) * 10 + 100
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        changed = False

        # Free reduce first
        new_word = free_reduce(word)
        if len(new_word) != len(word):
            word = new_word
            changed = True
            continue

        # Scan for transformations
        for i in range(len(word) - 1):
            g1, g2 = word[i], word[i+1]
            idx1, sign1 = g1
            idx2, sign2 = g2

            # Case 1: Negative followed by positive -> move positive left
            if sign1 == -1 and sign2 == 1:
                if idx1 < idx2:
                    # X_m x_n -> x_{n+1} X_m when m < n
                    # Move positive left, increment its index
                    new_g1 = (idx2 + 1, 1)
                    new_g2 = (idx1, -1)
                    word = word[:i] + [new_g1, new_g2] + word[i+2:]
                    changed = True
                    break
                elif idx1 > idx2 and idx1 - idx2 >= 2:
                    # They commute (distance >= 2), swap to move positive left
                    word = word[:i] + [g2, g1] + word[i+2:]
                    changed = True
                    break
                elif idx1 == idx2:
                    # X_n x_n -> identity (will be caught by free_reduce)
                    pass

            # Case 2: Sort positive generators (ascending indices)
            elif sign1 == 1 and sign2 == 1:
                if idx1 > idx2 and idx1 - idx2 >= 2:
                    # Commute: swap to get smaller index first
                    word = word[:i] + [g2, g1] + word[i+2:]
                    changed = True
                    break

            # Case 3: Sort negative generators (descending indices)
            elif sign1 == -1 and sign2 == -1:
                if idx1 < idx2 and idx2 - idx1 >= 2:
                    # Commute: swap to get larger index first
                    word = word[:i] + [g2, g1] + word[i+2:]
                    changed = True
                    break

            # Case 4: Positive followed by negative (might need adjustment)
            elif sign1 == 1 and sign2 == -1:
                # x_m X_n: if they don't cancel and m > n with distance >= 2, commute
                if idx1 != idx2 and idx1 > idx2 and idx1 - idx2 >= 2:
                    word = word[:i] + [g2, g1] + word[i+2:]
                    changed = True
                    break

        if not changed:
            break

    return word


def test_identity(word_or_string: Union[str, Word]) -> bool:
    """Test if word equals identity."""
    if isinstance(word_or_string, str):
        word = parse_word(word_or_string)
    else:
        word = list(word_or_string)

    normal = to_normal_form(word)
    return len(normal) == 0


def validate_word(word_or_string: Union[str, Word]) -> bool:
    """Validate word format."""
    if isinstance(word_or_string, str):
        if not word_or_string.strip():
            return True  # Empty string is valid (identity)
        pattern = r'^([xX]\d+\s*)+$'
        return bool(re.match(pattern, word_or_string.strip()))
    else:
        return all(
            isinstance(g, tuple) and
            len(g) == 2 and
            isinstance(g[0], int) and
            g[0] >= 0 and
            g[1] in (1, -1)
            for g in word_or_string
        )


# Test suite
if __name__ == "__main__":
    print("Thompson's Group F - Identity Test Suite")
    print("=" * 50)

    # Test cases: (word_string, expected_is_identity)
    # Note: In Thompson's F, generators do NOT simply commute.
    # The relation x_j x_i = x_i x_{j+1} for i < j means moving changes indices.
    test_cases = [
        # Empty word = identity
        ("", True),

        # Simple cancellations
        ("x0 X0", True),
        ("X0 x0", True),
        ("x1 X1", True),
        ("X1 x1", True),
        ("x2 X2", True),
        ("X2 x2", True),

        # Nested cancellations
        ("x0 x1 X1 X0", True),
        ("x0 X0 x1 X1", True),
        ("X0 x0 X1 x1", True),

        # Conjugation relation: X0 x1 x0 = x2, so X0 x1 x0 X2 = identity
        ("X0 x1 x0 X2", True),
        ("x2 X0 X1 x0", True),  # x2 = X0 x1 x0, so x2 X0 X1 x0 = X0 x1 x0 X0 X1 x0 = X0 x1 X1 x0 = X0 x0 = 1

        # Higher conjugation: X0 x2 x0 = x3
        ("X0 x2 x0 X3", True),

        # This specific form reduces to identity via folding
        ("X0 X2 x0 x2", True),

        # X1 x2 x1 = x3, so X1 x2 x1 X3 = identity
        ("X1 x2 x1 X3", True),

        # Non-identities: single generators
        ("x0", False),
        ("x1", False),
        ("x2", False),
        ("X0", False),
        ("X1", False),

        # Non-identities: non-commuting pairs
        ("x0 x1", False),
        ("x1 x0", False),
        ("x0 X1", False),
        ("X0 x1", False),

        # Non-identities: products that don't cancel
        ("x0 x0", False),
        ("x1 x1", False),
        ("X0 X0", False),

        # Note: x0 x2 X0 X2 is NOT identity (x0 and x2 don't commute simply)
        ("x0 x2 X0 X2", False),

        # Note: X0 X3 x0 x3 is NOT identity
        ("X0 X3 x0 x3", False),

        # Complex non-identity
        ("x0 x1 x2", False),

        # More complex identities using conjugation
        # X0^2 x1 x0^2 = x3, so X0^2 x1 x0^2 X3 = identity
        ("X0 X0 x1 x0 x0 X3", True),

        # Double conjugation: X1 x2 x1 = x3, X0 x3 x0 = x4
        # So X0 X1 x2 x1 x0 X4 = identity
        ("X0 X1 x2 x1 x0 X4", True),
    ]

    passed = 0
    failed = 0

    for word_str, expected in test_cases:
        result = test_identity(word_str)
        status = "PASS" if result == expected else "FAIL"
        if result == expected:
            passed += 1
        else:
            failed += 1

        display_word = word_str if word_str else "(empty)"
        print(f"  {status}: test_identity(\"{display_word}\") = {result} (expected {expected})")

    print()
    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")

    # Additional function tests
    print()
    print("Function Tests:")
    print("-" * 50)

    # Test parse_word
    assert parse_word("x0 X1 x2") == [(0, 1), (1, -1), (2, 1)], "parse_word failed"
    assert parse_word("") == [], "parse_word empty failed"
    assert parse_word("x10 X25") == [(10, 1), (25, -1)], "parse_word multi-digit failed"
    print("  parse_word: OK")

    # Test word_to_string
    assert word_to_string([(0, 1), (1, -1), (2, 1)]) == "x0 X1 x2", "word_to_string failed"
    assert word_to_string([]) == "", "word_to_string empty failed"
    print("  word_to_string: OK")

    # Test expand_higher_generators
    assert expand_higher_generators([(2, 1)]) == [(0, -1), (1, 1), (0, 1)], "expand x2 failed"
    assert expand_higher_generators([(2, -1)]) == [(0, -1), (1, -1), (0, 1)], "expand X2 failed"
    assert expand_higher_generators([(3, 1)]) == [(0, -1), (0, -1), (1, 1), (0, 1), (0, 1)], "expand x3 failed"
    print("  expand_higher_generators: OK")

    # Test free_reduce
    assert free_reduce([(0, 1), (0, -1)]) == [], "free_reduce cancel failed"
    assert free_reduce([(0, 1), (1, 1), (1, -1), (0, -1)]) == [], "free_reduce nested failed"
    assert free_reduce([(0, 1), (1, 1)]) == [(0, 1), (1, 1)], "free_reduce no-op failed"
    print("  free_reduce: OK")

    # Test validate_word
    assert validate_word("x0 X1 x2") == True, "validate_word valid failed"
    assert validate_word("") == True, "validate_word empty failed"
    assert validate_word([(0, 1), (1, -1)]) == True, "validate_word list failed"
    print("  validate_word: OK")

    print()
    print("All function tests passed!")
