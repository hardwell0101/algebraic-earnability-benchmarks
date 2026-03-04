"""Grigorchuk group identity test via contracting recursion."""

# Projection map
PROJECTION_MAP = {
    'b': ('a', 'c'),
    'c': ('a', 'd'),
    'd': ('', 'b'),
}

# Klein four reductions
KLEIN_REDUCTIONS = {
    'bc': 'd', 'cb': 'd',
    'cd': 'b', 'dc': 'b',
    'bd': 'c', 'db': 'c',
}


def reduce_word(word: str) -> str:
    """Apply self-inverse and Klein four reductions."""
    if not word:
        return ""

    prev = None
    while prev != word:
        prev = word
        # Cancel duplicates
        i = 0
        result = []
        while i < len(word):
            if i + 1 < len(word) and word[i] == word[i + 1]:
                i += 2
            else:
                result.append(word[i])
                i += 1
        word = ''.join(result)
        # Klein four reductions
        for pair, replacement in KLEIN_REDUCTIONS.items():
            word = word.replace(pair, replacement)
    return word


def compute_projections(word: str) -> tuple:
    """Compute left/right projections via wreath recursion."""
    left_proj = []
    right_proj = []
    swap_parity = 0  # 0 = normal, 1 = swapped (odd number of 'a's seen)

    for char in word:
        if char == 'a':
            swap_parity = 1 - swap_parity
        elif char in PROJECTION_MAP:
            left_contrib, right_contrib = PROJECTION_MAP[char]
            if swap_parity == 0:
                left_proj.append(left_contrib)
                right_proj.append(right_contrib)
            else:
                left_proj.append(right_contrib)
                right_proj.append(left_contrib)
    return (reduce_word(''.join(left_proj)), reduce_word(''.join(right_proj)))


def test_identity(word: str, depth: int = 0, max_depth: int = 50) -> bool:
    """Test if word equals identity via contracting recursion."""
    word = reduce_word(word)
    if not word:
        return True
    if depth >= max_depth:
        raise RecursionError(f"Max depth {max_depth} exceeded")
    if word.count('a') % 2 == 1:
        return False
    left_proj, right_proj = compute_projections(word)
    return test_identity(left_proj, depth + 1, max_depth) and \
           test_identity(right_proj, depth + 1, max_depth)


def validate_word(word: str) -> bool:
    """Check if word uses only {a,b,c,d}."""
    return all(c in 'abcd' for c in word)


if __name__ == "__main__":
    # Test cases
    tests = [
        ("", True), ("aa", True), ("bb", True), ("bcd", True),
        ("adadadad", True), ("a", False), ("ab", False), ("adad", False),
    ]
    for word, expected in tests:
        result = test_identity(word)
        status = "PASS" if result == expected else "FAIL"
        print(f"[{status}] test_identity('{word}') = {result}")
