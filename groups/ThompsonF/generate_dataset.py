"""Dataset generator for Thompson's group F word problem."""

import csv
import os
import random
from typing import List, Tuple

from identity_test import (
    parse_word,
    word_to_string,
    test_identity,
    free_reduce,
    expand_higher_generators,
    Word,
)

# Random seed
SEED = 42
random.seed(SEED)

# Max generator index
MAX_INDEX = 5

# Base relations
BASE_RELATIONS = [
    # Free cancellations
    "x0 X0", "X0 x0", "x1 X1", "X1 x1", "x2 X2", "X2 x2", "x3 X3",
    # Conjugation relations
    "X0 x1 x0 X2", "X0 x2 x0 X3", "X0 x3 x0 X4", "X1 x2 x1 X3", "X1 x3 x1 X4",
    # Inverse conjugation
    "x0 X2 X0 x1", "x0 X3 X0 x2", "x1 X3 X1 x2",
    # Nested cancellations
    "x0 x1 X1 X0", "x1 x0 X0 X1", "X0 X1 x1 x0", "x0 x2 X2 X0",
]


def random_word(length: int, max_index: int = MAX_INDEX) -> Word:
    """Generate random word."""
    word = []
    for _ in range(length):
        idx = random.randint(0, max_index)
        sign = random.choice([1, -1])
        word.append((idx, sign))
    return word


def random_reduced_word(target_length: int, max_index: int = MAX_INDEX) -> Word:
    """Generate reduced word."""
    word = random_word(target_length * 2, max_index)
    word = expand_higher_generators(word)
    word = free_reduce(word)

    # Trim or extend
    if len(word) > target_length:
        word = word[:target_length]
    elif len(word) < target_length:
        while len(word) < target_length:
            idx = random.randint(0, 1)
            sign = random.choice([1, -1])
            if word and word[-1][0] == idx and word[-1][1] == -sign:
                continue
            word.append((idx, sign))

    return word


def invert_word(word: Word) -> Word:
    """Compute word inverse."""
    return [(idx, -sign) for idx, sign in reversed(word)]


def concatenate_words(words: List[Word]) -> Word:
    """Concatenate words."""
    result = []
    for w in words:
        result.extend(w)
    return result


def conjugate_word(word: Word, conjugator_length: int = None, reduce: bool = True) -> Word:
    """Conjugate word: g^-1 * word * g."""
    if conjugator_length is None:
        conjugator_length = random.randint(2, 8)

    g = random_word(conjugator_length, max_index=1)
    g_inv = invert_word(g)
    result = concatenate_words([g_inv, word, g])

    if reduce:
        expanded = expand_higher_generators(result)
        reduced = free_reduce(expanded)
        if len(reduced) < len(result) // 2:
            return free_reduce(result)
        return reduced

    return result


def random_identity_from_relations(target_length: int, max_attempts: int = 20) -> Tuple[Word, str]:
    """Generate identity from relations."""
    base_words = [parse_word(r) for r in BASE_RELATIONS]

    for attempt in range(max_attempts):
        method = random.choices(['product', 'conjugate', 'nested'], weights=[0.5, 0.3, 0.2])[0]

        if method == 'product':
            word = []
            num_relations = random.randint(2, min(4, target_length // 3 + 1))
            for _ in range(num_relations):
                base = random.choice(base_words)
                word.extend(base)
            word = free_reduce(word)

            if word and len(word) >= 2:
                if len(word) < target_length // 2:
                    word = conjugate_word(word, random.randint(1, 3), reduce=False)
                    word = free_reduce(word)
                if word and len(word) >= 2 and test_identity(word):
                    return word, "relation_product"

        elif method == 'conjugate':
            base = list(random.choice(base_words))
            conj_len = max(1, min(5, (target_length - len(base)) // 2))
            word = conjugate_word(base, conj_len, reduce=False)
            word = free_reduce(word)
            if word and len(word) >= 2 and test_identity(word):
                return word, "conjugation"

        else:  # nested
            base = list(random.choice(base_words))
            g1 = random_word(random.randint(1, 2), max_index=1)
            word = concatenate_words([invert_word(g1), base, g1])
            word = free_reduce(word)
            if word and len(word) >= 2 and test_identity(word):
                return word, "nested_conjugation"

    # Fallback
    base = list(random.choice(base_words[:6]))
    g = random_word(max(1, target_length // 3), max_index=1)
    word = concatenate_words([invert_word(g), base, g])
    word = free_reduce(word)
    if word and test_identity(word):
        return word, "fallback_conjugation"

    return parse_word("x0 x1 X1 X0"), "fallback_simple"


def random_identity_deep(target_length: int, max_attempts: int = 10) -> Tuple[Word, str]:
    """Generate deep identity."""
    base_words = [parse_word(r) for r in BASE_RELATIONS]

    for _ in range(max_attempts):
        word = list(random.choice(base_words))
        depth = random.randint(2, 4)
        for _ in range(depth):
            conj_len = random.randint(1, 3)
            g = random_word(conj_len, max_index=1)
            word = concatenate_words([invert_word(g), word, g])
            word = free_reduce(word)
            if not word:
                word = list(random.choice(base_words))

        if word and len(word) >= 4 and test_identity(word):
            return word, "deep_relation"

    word, _ = random_identity_from_relations(target_length)
    return word, "deep_fallback"


def generate_non_identity(target_length: int, max_attempts: int = 10) -> Tuple[Word, str]:
    """Generate random non-identity."""
    for _ in range(max_attempts):
        word = random_reduced_word(target_length)
        if word and not test_identity(word):
            return word, "random_word"

    # Fallback
    fallback_patterns = [
        [(0, 1)], [(1, 1)], [(0, 1), (1, 1)], [(1, 1), (0, 1)],
        [(0, 1), (0, 1)], [(1, 1), (1, 1)], [(0, 1), (1, -1)], [(0, -1), (1, 1)],
    ]
    return random.choice(fallback_patterns), "fallback_non_identity"


def perturb_identity(identity_word: Word) -> Tuple[Word, str]:
    """Perturb to non-identity."""
    if not identity_word or len(identity_word) < 2:
        return generate_non_identity(4)[0], "perturbed_fallback"

    word = list(identity_word)
    for _ in range(3):
        test_word = list(word)
        pos = random.randint(0, len(word) - 1)
        old_gen = test_word[pos]
        perturb_type = random.choice(['index', 'sign', 'remove'])

        if perturb_type == 'index':
            delta = random.choice([1, -1, 2, -2])
            new_idx = max(0, min(3, old_gen[0] + delta))
            if new_idx != old_gen[0]:
                test_word[pos] = (new_idx, old_gen[1])
        elif perturb_type == 'sign':
            test_word[pos] = (old_gen[0], -old_gen[1])
        else:
            if len(test_word) > 2:
                test_word = test_word[:pos] + test_word[pos+1:]

        if test_word and not test_identity(test_word):
            return test_word, "perturbed"

    return generate_non_identity(len(word))[0], "perturbed_fallback"


def generate_synthetic_dataset(n: int = 1000) -> List[dict]:
    """Generate 50/50 dataset, lengths 4-20."""
    dataset = []
    n_identities = n // 2
    n_non_identities = n - n_identities

    print(f"Generating {n_identities} identities...")
    for i in range(n_identities):
        target_len = random.randint(4, 20)
        word, source = random_identity_from_relations(target_len)

        dataset.append({
            'word': word_to_string(word),
            'label': 1,
            'length': len(word),
            'source': source,
        })

        if (i + 1) % 100 == 0:
            print(f"  Generated {i + 1}/{n_identities} identities")

    print(f"Generating {n_non_identities} non-identities...")
    for i in range(n_non_identities):
        target_len = random.randint(4, 20)
        word, source = generate_non_identity(target_len)

        dataset.append({
            'word': word_to_string(word),
            'label': 0,
            'length': len(word),
            'source': source,
        })

        if (i + 1) % 100 == 0:
            print(f"  Generated {i + 1}/{n_non_identities} non-identities")

    random.shuffle(dataset)
    return dataset


def generate_augmented_dataset(n: int = 1000) -> List[dict]:
    """Generate conjugation dataset, lengths 8-30."""
    dataset = []
    n_identities = n // 2
    n_non_identities = n - n_identities

    print(f"Generating {n_identities} identities (augmented)...")
    for i in range(n_identities):
        target_len = random.randint(8, 30)
        word, source = random_identity_from_relations(target_len)

        # Extra conjugation for longer words
        if len(word) < target_len and random.random() < 0.7:
            augmented_word = conjugate_word(list(word), random.randint(3, 6), reduce=False)
            augmented_word = free_reduce(augmented_word)
            # Verify the augmented word is still identity
            if augmented_word and test_identity(augmented_word):
                word = augmented_word
                source = "conjugation_augmented"

        if word and test_identity(word):
            dataset.append({
                'word': word_to_string(word),
                'label': 1,
                'length': len(word),
                'source': source,
            })
        else:
            # Retry with fresh generation
            word, source = random_identity_from_relations(target_len)
            dataset.append({
                'word': word_to_string(word),
                'label': 1,
                'length': len(word),
                'source': source,
            })

        if (i + 1) % 100 == 0:
            print(f"  Generated {i + 1}/{n_identities} identities")

    print(f"Generating {n_non_identities} non-identities (augmented)...")
    for i in range(n_non_identities):
        target_len = random.randint(8, 30)
        word, source = generate_non_identity(target_len)

        dataset.append({
            'word': word_to_string(word),
            'label': 0,
            'length': len(word),
            'source': source,
        })

        if (i + 1) % 100 == 0:
            print(f"  Generated {i + 1}/{n_non_identities} non-identities")

    random.shuffle(dataset)
    return dataset


def generate_hard_dataset(n: int = 1000) -> List[dict]:
    """Generate adversarial dataset, lengths 10-40."""
    dataset = []
    n_identities = n // 2
    n_non_identities = n - n_identities

    print(f"Generating {n_identities} identities (hard)...")
    for i in range(n_identities):
        target_len = random.randint(10, 40)
        word, source = random_identity_deep(target_len)

        dataset.append({
            'word': word_to_string(word),
            'label': 1,
            'length': len(word),
            'source': source,
        })

        if (i + 1) % 100 == 0:
            print(f"  Generated {i + 1}/{n_identities} identities")

    print(f"Generating {n_non_identities} non-identities (hard/adversarial)...")
    # Mix of adversarial (perturbed) and random
    n_adversarial = n_non_identities * 2 // 3
    n_random = n_non_identities - n_adversarial

    for i in range(n_adversarial):
        # Generate an identity then perturb it
        target_len = random.randint(10, 40)
        identity_word, _ = random_identity_deep(target_len)
        word, source = perturb_identity(identity_word)

        dataset.append({
            'word': word_to_string(word),
            'label': 0,
            'length': len(word),
            'source': source,
        })

        if (i + 1) % 100 == 0:
            print(f"  Generated {i + 1}/{n_adversarial} adversarial")

    for i in range(n_random):
        target_len = random.randint(10, 40)
        word, source = generate_non_identity(target_len)

        dataset.append({
            'word': word_to_string(word),
            'label': 0,
            'length': len(word),
            'source': source,
        })

    random.shuffle(dataset)
    return dataset


def save_dataset(dataset: List[dict], filename: str):
    """Save to CSV."""
    os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)

    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['word', 'label', 'length', 'source'])
        writer.writeheader()
        writer.writerows(dataset)

    print(f"Saved {len(dataset)} samples to {filename}")


def verify_dataset(dataset: List[dict], name: str, sample_size: int = 50):
    """Verify and print stats."""
    print(f"\n{'='*50}")
    print(f"Verifying {name}")
    print(f"{'='*50}")

    # Basic stats
    total = len(dataset)
    identities = sum(1 for d in dataset if d['label'] == 1)
    non_identities = total - identities

    print(f"Total samples: {total}")
    print(f"Identities: {identities} ({100*identities/total:.1f}%)")
    print(f"Non-identities: {non_identities} ({100*non_identities/total:.1f}%)")

    # Length stats
    lengths = [d['length'] for d in dataset]
    print(f"Length range: {min(lengths)} - {max(lengths)}")
    print(f"Average length: {sum(lengths)/len(lengths):.1f}")

    # Source distribution
    sources = {}
    for d in dataset:
        sources[d['source']] = sources.get(d['source'], 0) + 1
    print(f"Sources: {sources}")

    # Verify sample
    print(f"\nVerifying {sample_size} random samples...")
    sample = random.sample(dataset, min(sample_size, total))
    correct = 0
    errors = []

    for d in sample:
        word = parse_word(d['word'])
        is_identity = test_identity(word)
        expected = d['label'] == 1

        if is_identity == expected:
            correct += 1
        else:
            errors.append({
                'word': d['word'],
                'expected': expected,
                'got': is_identity,
            })

    print(f"Verification: {correct}/{len(sample)} correct ({100*correct/len(sample):.1f}%)")

    if errors:
        print(f"Errors found ({len(errors)}):")
        for err in errors[:5]:
            print(f"  Word: {err['word'][:50]}...")
            print(f"    Expected: {'identity' if err['expected'] else 'non-identity'}")
            print(f"    Got: {'identity' if err['got'] else 'non-identity'}")

    # Show examples
    print(f"\nExample entries:")
    for i, d in enumerate(random.sample(dataset, 5)):
        label_str = "identity" if d['label'] == 1 else "non-identity"
        word_preview = d['word'][:40] + "..." if len(d['word']) > 40 else d['word']
        print(f"  {i+1}. [{label_str}] {word_preview}")
        print(f"     Length: {d['length']}, Source: {d['source']}")


def main():
    """Generate all datasets."""
    print("Thompson's Group F - Dataset Generator")
    print("=" * 50)

    # Create data directory
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)

    # Generate synthetic dataset
    print("\n[1/3] Generating synthetic_1k.csv...")
    random.seed(SEED)
    synthetic = generate_synthetic_dataset(1000)
    save_dataset(synthetic, os.path.join(data_dir, "synthetic_1k.csv"))
    verify_dataset(synthetic, "synthetic_1k.csv")

    # Generate augmented dataset
    print("\n[2/3] Generating augmented_1k.csv...")
    random.seed(SEED + 1)
    augmented = generate_augmented_dataset(1000)
    save_dataset(augmented, os.path.join(data_dir, "augmented_1k.csv"))
    verify_dataset(augmented, "augmented_1k.csv")

    # Generate hard dataset
    print("\n[3/3] Generating hard_1k.csv...")
    random.seed(SEED + 2)
    hard = generate_hard_dataset(1000)
    save_dataset(hard, os.path.join(data_dir, "hard_1k.csv"))
    verify_dataset(hard, "hard_1k.csv")

    print("\n" + "=" * 50)
    print("Dataset generation complete!")
    print(f"Files saved in: {os.path.abspath(data_dir)}/")


if __name__ == "__main__":
    main()
