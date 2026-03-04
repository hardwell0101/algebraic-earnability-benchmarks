"""Out(F2) = GL(2,Z) identity test via matrix multiplication."""

import numpy as np
from typing import List, Optional, Union

# Generator matrices
GENERATORS = {
    'S': np.array([[0, -1], [1, 0]], dtype=object),
    's': np.array([[0, 1], [-1, 0]], dtype=object),
    'T': np.array([[1, 1], [0, 1]], dtype=object),
    't': np.array([[1, -1], [0, 1]], dtype=object),
    'J': np.array([[-1, 0], [0, 1]], dtype=object),
}

IDENTITY = np.array([[1, 0], [0, 1]], dtype=object)
ALPHABET = ['S', 's', 'T', 't', 'J']
INVERSES = {'S': 's', 's': 'S', 'T': 't', 't': 'T', 'J': 'J'}


def parse_word(word_str: str) -> List[str]:
    """Parse string to symbol list."""
    if not word_str or not word_str.strip():
        return []
    return [token for token in word_str.strip().split() if token]


def word_to_string(tokens: List[str]) -> str:
    """Convert list to string."""
    return ' '.join(tokens)


def validate_word(word_str: str) -> bool:
    """Validate word symbols."""
    tokens = parse_word(word_str)
    return all(token in GENERATORS for token in tokens)


def evaluate(word: Union[str, List[str]]) -> np.ndarray:
    """Evaluate word as matrix product."""
    if isinstance(word, str):
        tokens = parse_word(word)
    else:
        tokens = word

    # Start with identity matrix
    result = IDENTITY.copy()

    # Multiply left-to-right
    for token in tokens:
        if token not in GENERATORS:
            raise ValueError(f"Unknown generator: {token}")
        result = result @ GENERATORS[token]

    return result


def test_identity(word_str: str) -> bool:
    """Test if word equals identity."""
    matrix = evaluate(word_str)
    return np.array_equal(matrix, IDENTITY)


def get_inverse(gen: str) -> str:
    """Get inverse symbol."""
    if gen not in INVERSES:
        raise ValueError(f"Unknown generator: {gen}")
    return INVERSES[gen]


def invert_word(tokens: List[str]) -> List[str]:
    """Compute word inverse."""
    return [get_inverse(g) for g in reversed(tokens)]


def free_reduce(tokens: List[str]) -> List[str]:
    """Cancel adjacent inverses."""
    if not tokens:
        return []

    stack = []
    for token in tokens:
        if stack and stack[-1] == get_inverse(token):
            stack.pop()
        else:
            stack.append(token)

    return stack


def run_tests():
    """Run tests."""
    print("Running Out(F₂) identity test cases...")
    print("=" * 60)

    # Required test cases from specification
    required_tests = [
        ("S S S S", True, "S⁴ = I"),
        ("S s", True, "Free cancellation S·s"),
        ("T t", True, "Free cancellation T·t"),
        ("S T S T S T S T S T S T", True, "(ST)⁶ = I"),
        ("S T S T S T s s", True, "(ST)³ = S² → (ST)³·S⁻² = I"),
        ("S", False, "Single S"),
        ("T", False, "Single T"),
        ("S T", False, "ST ≠ I"),
        ("T T", False, "T² = [[1,2],[0,1]] ≠ I"),
    ]

    # Additional test cases
    additional_tests = [
        ("", True, "Empty word = I"),
        ("J J", True, "J² = I"),
        ("s s s s", True, "s⁴ = (S⁻¹)⁴ = I"),
        ("t T", True, "Free cancellation t·T"),
        ("S S", False, "S² = -I ≠ I"),
        ("s s", False, "s² = -I ≠ I"),
        ("J", False, "Single J ≠ I"),
        ("T T T T T T", False, "T⁶ ≠ I"),
        # Conjugation: g⁻¹ · identity · g = identity
        ("s S S S S S", True, "s·S⁵ = s·S = I"),
        ("T S S S S t", True, "T·S⁴·t = T·I·t = T·t = I"),
        # Proper conjugation of S⁴
        ("J S S S S J", True, "J·S⁴·J = J·I·J = J² = I"),
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
            matrix = evaluate(word)
            print(f"       Got matrix: {matrix.tolist()}")

    print("\n--- Additional Test Cases ---")
    for word, expected, description in additional_tests:
        result = test_identity(word)
        status = "PASS" if result == expected else "FAIL"
        if result != expected:
            all_passed = False
        print(f"[{status}] test_identity(\"{word}\") == {expected}: {description}")
        if result != expected:
            matrix = evaluate(word)
            print(f"       Got matrix: {matrix.tolist()}")

    print("\n" + "=" * 60)

    # Run the required assertions
    print("\nRunning required assertions...")
    try:
        assert test_identity("S S S S") == True       # S⁴ = I
        assert test_identity("S s") == True           # Free cancellation
        assert test_identity("T t") == True           # Free cancellation
        assert test_identity("S T S T S T S T S T S T") == True  # (ST)⁶ = I
        assert test_identity("S T S T S T s s") == True  # (ST)³ = S²
        assert test_identity("S") == False
        assert test_identity("T") == False
        assert test_identity("S T") == False
        assert test_identity("T T") == False          # T² = [[1,2],[0,1]]
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


def demo_matrices():
    """Show generators and relations."""
    print("\nGenerator Matrices:")
    print("-" * 40)
    for name, matrix in GENERATORS.items():
        print(f"{name}: {matrix.tolist()}")

    print("\nKey Relations:")
    print("-" * 40)

    # S⁴ = I
    s4 = GENERATORS['S'] @ GENERATORS['S'] @ GENERATORS['S'] @ GENERATORS['S']
    print(f"S⁴ = {s4.tolist()}")

    # (ST)⁶ = I
    st = GENERATORS['S'] @ GENERATORS['T']
    st6 = st @ st @ st @ st @ st @ st
    print(f"(ST)⁶ = {st6.tolist()}")

    # (ST)³ = -I
    st3 = st @ st @ st
    print(f"(ST)³ = {st3.tolist()}")

    # S² = -I
    s2 = GENERATORS['S'] @ GENERATORS['S']
    print(f"S² = {s2.tolist()}")

    # J² = I
    j2 = GENERATORS['J'] @ GENERATORS['J']
    print(f"J² = {j2.tolist()}")


if __name__ == "__main__":
    demo_matrices()
    print()
    run_tests()
