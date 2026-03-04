import csv
import os
import random
from identity_test import test_identity, reduce_word, validate_word

# Random seed
SEED = 42
random.seed(SEED)

GENERATORS = ['a', 'b', 'c', 'd']

# Base relations
BASE_RELATIONS = [
    'aa', 'bb', 'cc', 'dd',           # Self-inverse
    'bcd', 'bdc', 'cbd', 'cdb', 'dbc', 'dcb',  # Klein four
    'adadadad', 'dadadada',            # (ad)^4 = 1
    'bcdbcd',                          # (bcd)^2 = 1
]


def random_word(length: int) -> str:
    return ''.join(random.choices(GENERATORS, k=length))


def random_identity_from_relations(target_length: int, max_attempts: int = 200) -> str:
    """Generate identity from relations."""
    # Long words strategy
    if target_length >= 20:
        for _ in range(max_attempts):
            # Build from (ad)^4 copies
            num_copies = random.randint(2, target_length // 8 + 1)
            base = random.choice(['adadadad', 'dadadada']) * num_copies
            base = reduce_word(base)

            # Conjugate
            g_len = random.randint(3, min(10, target_length // 4))
            g = random_word(g_len)
            word = reduce_word(g[::-1] + base + g)

            if word and len(word) >= target_length * 0.7:
                return word

        # Fallback
        base = 'adadadad' * (target_length // 8 + 1)
        g = random_word(5)
        return reduce_word(g[::-1] + base + g)

    # Short words
    for _ in range(max_attempts):
        # Build from relations
        word = ''
        while len(word) < target_length * 2:
            relation = random.choice(BASE_RELATIONS)
            word += relation

        # Reduce
        word = reduce_word(word)

        # Check length
        if word and len(word) >= target_length // 2:
            return word

    # Fallback
    num_copies = max(1, target_length // 8)
    return reduce_word('adadadad' * num_copies)


def conjugate_word(word: str, conjugator_length: int = None) -> str:
    """Conjugate word: g^-1 * word * g."""
    if conjugator_length is None:
        conjugator_length = random.randint(2, 10)

    g = random_word(conjugator_length)
    g_inv = g[::-1]  # Reverse = inverse
    return reduce_word(g_inv + word + g)


def generate_non_identity(length: int, max_attempts: int = 50) -> str:
    """Generate random non-identity."""
    for _ in range(max_attempts):
        word = random_word(length)
        word = reduce_word(word)
        if word and not test_identity(word):
            return word

    # Fallback
    return random_word(1) + random_word(length - 1)


def perturb_word(word: str) -> str:
    """Perturb to non-identity."""
    if not word:
        return random_word(1)

    word_list = list(word)
    idx = random.randint(0, len(word) - 1)
    original = word_list[idx]

    # Swap one character
    others = [g for g in GENERATORS if g != original]
    word_list[idx] = random.choice(others)

    return ''.join(word_list)


def generate_synthetic_dataset(n: int = 1000) -> list:
    """Generate 50/50 dataset, lengths 4-30."""
    samples = []
    target_identities = n // 2
    target_non_identities = n - target_identities

    # Identities
    attempts = 0
    while len([s for s in samples if s['label'] == 1]) < target_identities and attempts < target_identities * 3:
        attempts += 1
        length = random.randint(4, 30)
        word = random_identity_from_relations(length)
        if word and test_identity(word):
            samples.append({
                'word': word,
                'label': 1,
                'length': len(word),
                'source': 'random_relation'
            })

    # Non-identities
    attempts = 0
    while len([s for s in samples if s['label'] == 0]) < target_non_identities and attempts < target_non_identities * 3:
        attempts += 1
        length = random.randint(4, 30)
        word = generate_non_identity(length)
        if word and not test_identity(word):
            samples.append({
                'word': word,
                'label': 0,
                'length': len(word),
                'source': 'random_word'
            })

    random.shuffle(samples)
    return samples


def generate_augmented_dataset(n: int = 1000) -> list:
    """Generate conjugation dataset, lengths 8-40."""
    samples = []
    target_identities = n // 2
    target_non_identities = n - target_identities

    # Identities via conjugation
    attempts = 0
    while len([s for s in samples if s['label'] == 1]) < target_identities and attempts < target_identities * 3:
        attempts += 1
        base = random_identity_from_relations(random.randint(4, 20))
        word = conjugate_word(base, random.randint(2, 10))

        if word and len(word) >= 4 and test_identity(word):
            samples.append({
                'word': word,
                'label': 1,
                'length': len(word),
                'source': 'conjugation'
            })
        elif base and test_identity(base):
            samples.append({
                'word': base,
                'label': 1,
                'length': len(base),
                'source': 'random_relation'
            })

    # Non-identities
    attempts = 0
    while len([s for s in samples if s['label'] == 0]) < target_non_identities and attempts < target_non_identities * 3:
        attempts += 1
        length = random.randint(8, 40)
        word = generate_non_identity(length)
        if word and not test_identity(word):
            samples.append({
                'word': word,
                'label': 0,
                'length': len(word),
                'source': 'random_word'
            })

    random.shuffle(samples)
    return samples


def generate_hard_dataset(n: int = 1000) -> list:
    """Generate adversarial dataset, lengths 20-60."""
    samples = []
    target_identities = n // 2
    target_non_identities = n - target_identities

    # Deep identities
    attempts = 0
    max_attempts = target_identities * 5
    while len([s for s in samples if s['label'] == 1]) < target_identities and attempts < max_attempts:
        attempts += 1
        target_len = random.randint(20, 50)
        base = random_identity_from_relations(target_len)

        # Optional conjugation
        if random.random() < 0.5 and base:
            word = conjugate_word(base, random.randint(3, 10))
        else:
            word = base

        if word and len(word) >= 16:
            if test_identity(word):
                samples.append({
                    'word': word,
                    'label': 1,
                    'length': len(word),
                    'source': 'deep_relation'
                })

    # Adversarial non-identities
    attempts = 0
    max_attempts = target_non_identities * 3
    while len([s for s in samples if s['label'] == 0]) < target_non_identities and attempts < max_attempts:
        attempts += 1
        base = random_identity_from_relations(random.randint(20, 50))
        word = perturb_word(base)

        if word and not test_identity(word) and len(word) >= 16:
            samples.append({
                'word': word,
                'label': 0,
                'length': len(word),
                'source': 'perturbed'
            })
        elif word:
            word = generate_non_identity(random.randint(20, 50))
            if word and len(word) >= 16:
                samples.append({
                    'word': word,
                    'label': 0,
                    'length': len(word),
                    'source': 'random_word'
                })

    random.shuffle(samples)
    return samples


def save_dataset(samples: list, filepath: str):
    """Save to CSV."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['word', 'label', 'length', 'source'])
        writer.writeheader()
        writer.writerows(samples)


def verify_dataset(samples: list, name: str, num_examples: int = 5):
    """Verify and print stats."""
    print(f"\n{'='*60}")
    print(f"Dataset: {name}")
    print(f"{'='*60}")

    # Balance
    identities = sum(1 for s in samples if s['label'] == 1)
    non_identities = len(samples) - identities
    print(f"\nClass balance:")
    print(f"  Identities (label=1): {identities} ({100*identities/len(samples):.1f}%)")
    print(f"  Non-identities (label=0): {non_identities} ({100*non_identities/len(samples):.1f}%)")

    # Lengths
    lengths = [s['length'] for s in samples]
    print(f"\nLength statistics:")
    print(f"  Min: {min(lengths)}, Max: {max(lengths)}, Avg: {sum(lengths)/len(lengths):.1f}")

    # Sources
    sources = {}
    for s in samples:
        sources[s['source']] = sources.get(s['source'], 0) + 1
    print(f"\nSource distribution:")
    for source, count in sorted(sources.items()):
        print(f"  {source}: {count}")

    # Examples
    print(f"\nSample examples (with verification):")
    print("-" * 60)

    id_examples = [s for s in samples if s['label'] == 1][:num_examples]
    non_id_examples = [s for s in samples if s['label'] == 0][:num_examples]

    print("\nIdentity examples:")
    for s in id_examples:
        word = s['word']
        verified = test_identity(word)
        status = "OK" if verified else "MISMATCH!"
        display_word = word if len(word) <= 40 else word[:37] + "..."
        print(f"  [{status}] '{display_word}' (len={s['length']}, source={s['source']})")

    print("\nNon-identity examples:")
    for s in non_id_examples:
        word = s['word']
        verified = not test_identity(word)
        status = "OK" if verified else "MISMATCH!"
        display_word = word if len(word) <= 40 else word[:37] + "..."
        print(f"  [{status}] '{display_word}' (len={s['length']}, source={s['source']})")


def main():
    print("Grigorchuk Group Word Problem Dataset Generator")
    print("=" * 60)
    print(f"Random seed: {SEED}")

    # Create data directory
    data_dir = os.path.join(os.path.dirname(__file__), 'data')

    # Generate datasets
    print("\nGenerating synthetic_1k.csv...")
    synthetic = generate_synthetic_dataset(1000)
    save_dataset(synthetic, os.path.join(data_dir, 'synthetic_1k.csv'))
    verify_dataset(synthetic, "synthetic_1k.csv")

    print("\nGenerating augmented_1k.csv...")
    augmented = generate_augmented_dataset(1000)
    save_dataset(augmented, os.path.join(data_dir, 'augmented_1k.csv'))
    verify_dataset(augmented, "augmented_1k.csv")

    print("\nGenerating hard_1k.csv...")
    hard = generate_hard_dataset(1000)
    save_dataset(hard, os.path.join(data_dir, 'hard_1k.csv'))
    verify_dataset(hard, "hard_1k.csv")

    print("\n" + "=" * 60)
    print("Dataset generation complete!")
    print(f"Files saved to: {data_dir}/")
    print("  - synthetic_1k.csv")
    print("  - augmented_1k.csv")
    print("  - hard_1k.csv")


if __name__ == "__main__":
    main()
