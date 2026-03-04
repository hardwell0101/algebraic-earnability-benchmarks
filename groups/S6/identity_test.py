"""S6 identity test via permutation composition."""

from typing import List, Union

N = 6
IDENTITY = [1, 2, 3, 4, 5, 6]
ALPHABET = ['s1', 's2', 's3', 's4', 's5']
VALID_INDICES = {1, 2, 3, 4, 5}


def parse_word(word_str: str) -> List[int]:
    """Parse string to indices."""
    if not word_str or not word_str.strip():
        return []

    tokens = word_str.strip().split()
    indices = []

    for token in tokens:
        if not token:
            continue
        # Parse "sN" format
        if token.startswith('s') and token[1:].isdigit():
            idx = int(token[1:])
            if idx in VALID_INDICES:
                indices.append(idx)
            else:
                raise ValueError(f"Invalid generator index: {token} (must be s1-s5)")
        else:
            raise ValueError(f"Invalid generator format: {token}")

    return indices


def word_to_string(indices: List[int]) -> str:
    """Convert indices to string."""
    return ' '.join(f's{i}' for i in indices)


def validate_word(word_str: str) -> bool:
    """Validate word format."""
    try:
        parse_word(word_str)
        return True
    except ValueError:
        return False


def apply_transposition(perm: List[int], i: int) -> None:
    """Apply transposition si."""
    perm[i-1], perm[i] = perm[i], perm[i-1]


def evaluate(word: Union[str, List[int]]) -> List[int]:
    """Evaluate word as permutation."""
    if isinstance(word, str):
        indices = parse_word(word)
    else:
        indices = word

    # Start with identity permutation
    perm = list(IDENTITY)

    # Apply each transposition left-to-right
    for i in indices:
        if i not in VALID_INDICES:
            raise ValueError(f"Invalid generator index: {i}")
        apply_transposition(perm, i)

    return perm


def test_identity(word_str: str) -> bool:
    """Test if word equals identity."""
    perm = evaluate(word_str)
    return perm == IDENTITY


def invert_word(indices: List[int]) -> List[int]:
    """Compute word inverse (reverse)."""
    return list(reversed(indices))


def free_reduce(indices: List[int]) -> List[int]:
    """Cancel adjacent duplicates."""
    if not indices:
        return []

    stack = []
    for idx in indices:
        if stack and stack[-1] == idx:
            stack.pop()
        else:
            stack.append(idx)

    return stack


def run_tests():
    """Run tests."""
    print("Running S6 identity test cases...")
    print("=" * 60)

    # Required test cases from specification
    required_tests = [
        ("s1 s1", True, "s1^2 = 1"),
        ("s2 s2", True, "s2^2 = 1"),
        ("s3 s3", True, "s3^2 = 1"),
        ("s4 s4", True, "s4^2 = 1"),
        ("s5 s5", True, "s5^2 = 1"),
        ("s1 s2 s1 s2 s1 s2", True, "Braid relation (s1 s2)^3 = 1"),
        ("s2 s3 s2 s3 s2 s3", True, "Braid relation (s2 s3)^3 = 1"),
        ("s3 s4 s3 s4 s3 s4", True, "Braid relation (s3 s4)^3 = 1"),
        ("s4 s5 s4 s5 s4 s5", True, "Braid relation (s4 s5)^3 = 1"),
        ("s1 s3 s1 s3", True, "Distant commutation s1 s3 s1 s3 = 1"),
        ("s1 s4 s1 s4", True, "Distant commutation s1 s4 s1 s4 = 1"),
        ("s1 s5 s1 s5", True, "Distant commutation s1 s5 s1 s5 = 1"),
        ("s2 s4 s2 s4", True, "Distant commutation s2 s4 s2 s4 = 1"),
        ("s2 s5 s2 s5", True, "Distant commutation s2 s5 s2 s5 = 1"),
        ("s3 s5 s3 s5", True, "Distant commutation s3 s5 s3 s5 = 1"),
        ("s1", False, "Single s1"),
        ("s5", False, "Single s5"),
        ("s1 s2", False, "s1 s2 != identity"),
        ("s1 s2 s3 s4 s5", False, "s1 s2 s3 s4 s5 != identity"),
    ]

    # Additional test cases
    additional_tests = [
        ("", True, "Empty word = identity"),
        ("s1 s2 s1", False, "s1 s2 s1 (transposition (1 3))"),
        ("s1 s2 s3 s4 s5", False, "Long cycle"),
        ("s5 s4 s3 s2 s1 s1 s2 s3 s4 s5", True, "w * w^-1 pattern"),
        ("s1 s5", False, "Product of distant transpositions"),
    ]

    all_passed = True

    print("\n--- Required Test Cases ---")
    for word, expected, description in required_tests:
        result = test_identity(word)
        status = "PASS" if result == expected else "FAIL"
        if result != expected:
            all_passed = False
        print(f"[{status}] test_identity(\"{word}\") == {expected}: {description}")
        if result != expected:
            perm = evaluate(word)
            print(f"       Got permutation: {perm}")

    print("\n--- Additional Test Cases ---")
    for word, expected, description in additional_tests:
        result = test_identity(word)
        status = "PASS" if result == expected else "FAIL"
        if result != expected:
            all_passed = False
        print(f"[{status}] test_identity(\"{word}\") == {expected}: {description}")
        if result != expected:
            perm = evaluate(word)
            print(f"       Got permutation: {perm}")

    print("\n" + "=" * 60)

    # Run the required assertions
    print("\nRunning required assertions...")
    try:
        assert test_identity("s5 s5") == True
        assert test_identity("s1 s4") == test_identity("s4 s1")  # Commute
        assert test_identity("s4 s5 s4 s5 s4 s5") == True  # Braid
        assert test_identity("s5") == False
        print("All required assertions PASSED!")
    except AssertionError as e:
        print(f"Assertion FAILED: {e}")
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("All tests PASSED!")
    else:
        print("Some tests FAILED!")

    return all_passed


def demo_permutations():
    """Show generators and relations."""
    print("\nGenerator Actions on [1,2,3,4,5,6]:")
    print("-" * 40)
    for gen in ALPHABET:
        perm = evaluate(gen)
        print(f"{gen}: {IDENTITY} -> {perm}")

    print("\nKey Relations:")
    print("-" * 40)

    # Self-inverse
    for gen in ALPHABET:
        word = f"{gen} {gen}"
        perm = evaluate(word)
        print(f"{gen}^2 = {perm}")

    # Braid relations
    braid_words = [
        "s1 s2 s1 s2 s1 s2",
        "s2 s3 s2 s3 s2 s3",
        "s3 s4 s3 s4 s3 s4",
        "s4 s5 s4 s5 s4 s5",
    ]
    for word in braid_words:
        perm = evaluate(word)
        print(f"({word.split()[0]} {word.split()[1]})^3 = {perm}")

    # Distant commutation
    print("\nDistant commutation (si sj = sj si when |i-j| >= 2):")
    pairs = [("s1", "s3"), ("s1", "s4"), ("s1", "s5"), ("s2", "s4"), ("s2", "s5"), ("s3", "s5")]
    for s1, s2 in pairs:
        perm1 = evaluate(f"{s1} {s2}")
        perm2 = evaluate(f"{s2} {s1}")
        equal = perm1 == perm2
        print(f"{s1} {s2} = {perm1}, {s2} {s1} = {perm2}, equal: {equal}")


if __name__ == "__main__":
    demo_permutations()
    print()
    run_tests()
