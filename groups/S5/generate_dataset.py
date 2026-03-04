"""Dataset generator for S5 (Symmetric Group on 5 Elements) word problem."""

import csv
import os
import random
from typing import List, Tuple, Set

from identity_test import (
    test_identity,
    parse_word,
    word_to_string,
    evaluate,
    invert_word,
    free_reduce,
    ALPHABET,
    VALID_INDICES,
    N,
)

# Random seed
SEED = 42
random.seed(SEED)

# Base relations
BASE_RELATIONS = [
    # Self-inverse
    ("s1 s1", "self_cancel"), ("s2 s2", "self_cancel"),
    ("s3 s3", "self_cancel"), ("s4 s4", "self_cancel"),
    # Braid relations
    ("s1 s2 s1 s2 s1 s2", "braid_12"), ("s2 s3 s2 s3 s2 s3", "braid_23"),
    ("s3 s4 s3 s4 s3 s4", "braid_34"),
    ("s2 s1 s2 s1 s2 s1", "braid_21"), ("s3 s2 s3 s2 s3 s2", "braid_32"),
    ("s4 s3 s4 s3 s4 s3", "braid_43"),
    # Commutation
    ("s1 s3 s1 s3", "commute_13"), ("s3 s1 s3 s1", "commute_31"),
    ("s1 s4 s1 s4", "commute_14"), ("s4 s1 s4 s1", "commute_41"),
    ("s2 s4 s2 s4", "commute_24"), ("s4 s2 s4 s2", "commute_42"),
    # Combined
    ("s1 s1 s2 s2", "double_cancel"), ("s3 s3 s4 s4", "double_cancel"),
    ("s1 s2 s3 s4 s4 s3 s2 s1", "palindrome"),
]


def random_word(length: int) -> List[int]:
    """Generate random word."""
    return [random.choice(list(VALID_INDICES)) for _ in range(length)]


def random_reduced_word(target_length: int) -> List[int]:
    """Generate reduced word."""
    word = []
    attempts = 0
    max_attempts = target_length * 10

    while len(word) < target_length and attempts < max_attempts:
        attempts += 1
        gen = random.choice(list(VALID_INDICES))

        # Avoid creating adjacent duplicate
        if word and word[-1] == gen:
            continue

        word.append(gen)

    return word


def conjugate_identity(identity_indices: List[int], conjugator_length: int = None) -> Tuple[List[int], str]:
    """Conjugate word: g^-1 * word * g."""
    if conjugator_length is None:
        conjugator_length = random.randint(2, 8)

    # Generate random conjugator
    g = random_reduced_word(conjugator_length)
    g_inv = invert_word(g)  # Just reverse for self-inverse generators

    # g^-1 * identity * g
    result = g_inv + identity_indices + g

    # Light free reduction
    result = free_reduce(result)

    return result, "_conjugated"


def word_inverse_identity(length: int) -> Tuple[List[int], str]:
    """Generate w * w^-1 identity."""
    half_len = max(2, length // 2)
    w = random_reduced_word(half_len)
    w_inv = invert_word(w)

    # w * w^-1
    result = w + w_inv
    result = free_reduce(result)

    return result, "word_inverse"


def random_identity_from_relations(target_length: int, max_attempts: int = 20) -> Tuple[List[int], str]:
    """Generate identity from relations."""
    for _ in range(max_attempts):
        method = random.choices(
            ['single_relation', 'product', 'word_inverse', 'conjugate'],
            weights=[0.2, 0.3, 0.25, 0.25]
        )[0]

        if method == 'single_relation':
            # Use a single base relation
            relation, source = random.choice(BASE_RELATIONS)
            indices = parse_word(relation)

            # Maybe conjugate if too short
            if len(indices) < target_length // 2 and random.random() < 0.5:
                indices, suffix = conjugate_identity(indices, random.randint(2, 5))
                source += suffix

            if indices and test_identity(word_to_string(indices)):
                return indices, source

        elif method == 'product':
            # Concatenate multiple relations
            indices = []
            num_relations = random.randint(2, min(4, max(2, target_length // 4)))

            for _ in range(num_relations):
                relation, _ = random.choice(BASE_RELATIONS)
                indices.extend(parse_word(relation))

            indices = free_reduce(indices)

            if indices and test_identity(word_to_string(indices)):
                return indices, "relation_product"

        elif method == 'word_inverse':
            indices, source = word_inverse_identity(target_length)

            if indices and test_identity(word_to_string(indices)):
                return indices, source

        elif method == 'conjugate':
            # Conjugate a base relation
            relation, source = random.choice(BASE_RELATIONS)
            base_indices = parse_word(relation)
            conj_len = max(1, (target_length - len(base_indices)) // 2)
            indices, suffix = conjugate_identity(base_indices, min(conj_len, 10))
            source += suffix

            if indices and test_identity(word_to_string(indices)):
                return indices, source

    # Fallback: simple s1 s1
    return parse_word("s1 s1"), "self_cancel_fallback"


def random_identity_deep(target_length: int, max_attempts: int = 15) -> Tuple[List[int], str]:
    """Generate deep identity."""
    for _ in range(max_attempts):
        # Start with a base relation
        relation, base_source = random.choice(BASE_RELATIONS)
        indices = parse_word(relation)

        # Apply multiple conjugations
        depth = random.randint(2, 5)
        for _ in range(depth):
            conj_len = random.randint(2, 5)
            indices, _ = conjugate_identity(indices, conj_len)

            if not indices:
                # Restart if reduction collapsed
                relation, _ = random.choice(BASE_RELATIONS)
                indices = parse_word(relation)

        if indices and len(indices) >= 4 and test_identity(word_to_string(indices)):
            return indices, "deep_relation"

    # Fallback: word-inverse with conjugation
    indices, _ = word_inverse_identity(target_length)
    if indices and test_identity(word_to_string(indices)):
        return indices, "deep_fallback"

    return parse_word("s1 s1"), "deep_fallback_self"


def generate_non_identity(target_length: int, max_attempts: int = 30) -> Tuple[List[int], str]:
    """Generate random non-identity."""
    for _ in range(max_attempts):
        indices = random_reduced_word(target_length)

        if indices and not test_identity(word_to_string(indices)):
            return indices, "random_word"

    # Fallback: guaranteed non-identity patterns
    fallback_patterns = [
        [1],           # s1
        [2],           # s2
        [3],           # s3
        [4],           # s4
        [1, 2],        # s1 s2
        [2, 3],        # s2 s3
        [1, 2, 3],     # s1 s2 s3
        [1, 2, 3, 4],  # s1 s2 s3 s4
    ]

    pattern = random.choice(fallback_patterns)
    return pattern, "fallback_non_identity"


def perturb_identity(identity_indices: List[int]) -> Tuple[List[int], str]:
    """Perturb to non-identity."""
    if not identity_indices or len(identity_indices) < 2:
        return generate_non_identity(4)[0], "perturbed_fallback"

    indices = list(identity_indices)

    # Try a few random perturbations
    for _ in range(10):
        test_indices = list(indices)
        pos = random.randint(0, len(indices) - 1)
        original = test_indices[pos]

        # Choose perturbation type
        perturb_type = random.choices(
            ['replace', 'remove', 'insert'],
            weights=[0.5, 0.25, 0.25]
        )[0]

        if perturb_type == 'replace':
            # Replace with a different generator
            others = [g for g in VALID_INDICES if g != original]
            if others:
                test_indices[pos] = random.choice(others)

        elif perturb_type == 'remove':
            if len(test_indices) > 2:
                test_indices = test_indices[:pos] + test_indices[pos+1:]

        else:  # insert
            new_gen = random.choice(list(VALID_INDICES))
            test_indices = test_indices[:pos] + [new_gen] + test_indices[pos:]

        if test_indices and not test_identity(word_to_string(test_indices)):
            return test_indices, "perturbed"

    # Fallback
    return generate_non_identity(len(indices))[0], "perturbed_fallback"


def remove_duplicates(dataset: List[dict], seen: Set[str] = None) -> List[dict]:
    """Remove duplicates."""
    if seen is None:
        seen = set()

    unique = []
    for entry in dataset:
        word = entry['word']
        if word not in seen:
            seen.add(word)
            unique.append(entry)

    return unique


def generate_unique_identity(seen_words: Set[str], target_len: int, method: str = 'auto') -> Tuple[List[int], str]:
    """Generate unique identity."""
    # Try standard methods first
    for _ in range(10):
        if method == 'auto':
            choice = random.choice(['relation', 'inverse', 'deep', 'conjugate'])
        else:
            choice = method

        if choice == 'relation':
            indices, source = random_identity_from_relations(target_len)
        elif choice == 'inverse':
            indices, source = word_inverse_identity(target_len)
        elif choice == 'deep':
            indices, source = random_identity_deep(target_len)
        else:  # conjugate with random prefix
            relation, base_source = random.choice(BASE_RELATIONS)
            base_indices = parse_word(relation)
            # Add random length conjugator
            conj_len = random.randint(1, max(1, target_len // 2))
            indices, _ = conjugate_identity(base_indices, conj_len)
            source = "conjugation_unique"

        word = word_to_string(indices)
        if word and word not in seen_words and test_identity(word):
            return indices, source

    # Fallback: generate truly random identity using word-inverse pattern
    for _ in range(20):
        half_len = random.randint(2, max(3, target_len // 2))
        w = random_reduced_word(half_len)
        w_inv = invert_word(w)
        indices = w + w_inv
        indices = free_reduce(indices)

        word = word_to_string(indices)
        if word and word not in seen_words and test_identity(word):
            return indices, "word_inverse_unique"

    # Ultimate fallback: self-cancel with random conjugation
    base = parse_word("s1 s1")
    conj_len = random.randint(3, 15)
    indices, _ = conjugate_identity(base, conj_len)
    return indices, "fallback_unique"


def generate_synthetic_dataset(n: int = 1000) -> List[dict]:
    """Generate 50/50 dataset, lengths 4-20."""
    dataset = []
    seen_words: Set[str] = set()
    n_identities = n // 2
    n_non_identities = n - n_identities

    print(f"Generating {n_identities} identities...")
    identity_count = 0

    while identity_count < n_identities:
        target_len = random.randint(4, 20)
        indices, source = generate_unique_identity(seen_words, target_len)
        word = word_to_string(indices)

        if word and word not in seen_words and test_identity(word):
            seen_words.add(word)
            dataset.append({
                'word': word,
                'label': 1,
                'length': len(indices),
                'source': source,
            })
            identity_count += 1

            if identity_count % 100 == 0:
                print(f"  Generated {identity_count}/{n_identities} identities")

    print(f"  Generated {identity_count} identities")

    print(f"Generating {n_non_identities} non-identities...")
    non_identity_count = 0

    while non_identity_count < n_non_identities:
        target_len = random.randint(4, 20)
        indices, source = generate_non_identity(target_len)
        word = word_to_string(indices)

        if word and word not in seen_words and not test_identity(word):
            seen_words.add(word)
            dataset.append({
                'word': word,
                'label': 0,
                'length': len(indices),
                'source': source,
            })
            non_identity_count += 1

            if non_identity_count % 100 == 0:
                print(f"  Generated {non_identity_count}/{n_non_identities} non-identities")

    print(f"  Generated {non_identity_count} non-identities")

    random.shuffle(dataset)
    return dataset


def generate_augmented_dataset(n: int = 1000) -> List[dict]:
    """Generate conjugation dataset, lengths 8-30."""
    dataset = []
    seen_words: Set[str] = set()
    n_identities = n // 2
    n_non_identities = n - n_identities

    print(f"Generating {n_identities} identities (augmented)...")
    identity_count = 0

    while identity_count < n_identities:
        target_len = random.randint(8, 30)

        # Prefer conjugation methods with fallback to unique generation
        method = random.choices(['conjugate', 'deep', 'unique'], weights=[0.4, 0.3, 0.3])[0]

        if method == 'conjugate':
            relation, base_source = random.choice(BASE_RELATIONS)
            base_indices = parse_word(relation)
            conj_len = max(2, (target_len - len(base_indices)) // 2)
            indices, suffix = conjugate_identity(base_indices, min(conj_len, 12))
            source = "conjugation"
        elif method == 'deep':
            indices, source = random_identity_deep(target_len)
        else:
            indices, source = generate_unique_identity(seen_words, target_len)

        word = word_to_string(indices)

        if word and word not in seen_words and test_identity(word):
            seen_words.add(word)
            dataset.append({
                'word': word,
                'label': 1,
                'length': len(indices),
                'source': source,
            })
            identity_count += 1

            if identity_count % 100 == 0:
                print(f"  Generated {identity_count}/{n_identities} identities")

    print(f"  Generated {identity_count} identities")

    print(f"Generating {n_non_identities} non-identities (augmented)...")
    non_identity_count = 0

    while non_identity_count < n_non_identities:
        target_len = random.randint(8, 30)
        indices, source = generate_non_identity(target_len)
        word = word_to_string(indices)

        if word and word not in seen_words and not test_identity(word):
            seen_words.add(word)
            dataset.append({
                'word': word,
                'label': 0,
                'length': len(indices),
                'source': source,
            })
            non_identity_count += 1

            if non_identity_count % 100 == 0:
                print(f"  Generated {non_identity_count}/{n_non_identities} non-identities")

    print(f"  Generated {non_identity_count} non-identities")

    random.shuffle(dataset)
    return dataset


def generate_hard_dataset(n: int = 1000) -> List[dict]:
    """Generate adversarial dataset, lengths 10-40."""
    dataset = []
    seen_words: Set[str] = set()
    n_identities = n // 2
    n_non_identities = n - n_identities

    print(f"Generating {n_identities} identities (hard)...")
    identity_count = 0

    while identity_count < n_identities:
        target_len = random.randint(10, 40)

        # Mix of deep and unique generation
        if random.random() < 0.7:
            indices, source = random_identity_deep(target_len)
        else:
            indices, source = generate_unique_identity(seen_words, target_len)

        word = word_to_string(indices)

        if word and word not in seen_words and test_identity(word):
            seen_words.add(word)
            dataset.append({
                'word': word,
                'label': 1,
                'length': len(indices),
                'source': source,
            })
            identity_count += 1

            if identity_count % 100 == 0:
                print(f"  Generated {identity_count}/{n_identities} identities")

    print(f"  Generated {identity_count} identities")

    # Mix of adversarial (perturbed) and random non-identities
    print(f"Generating {n_non_identities} non-identities (hard/adversarial)...")
    n_adversarial = n_non_identities * 2 // 3
    adversarial_count = 0
    total_non_identity_count = 0

    # Adversarial examples (perturbed identities)
    while adversarial_count < n_adversarial:
        target_len = random.randint(10, 40)

        # Generate an identity then perturb it
        identity_indices, _ = random_identity_deep(target_len)
        indices, source = perturb_identity(identity_indices)
        word = word_to_string(indices)

        if word and word not in seen_words and not test_identity(word):
            seen_words.add(word)
            dataset.append({
                'word': word,
                'label': 0,
                'length': len(indices),
                'source': source,
            })
            adversarial_count += 1
            total_non_identity_count += 1

            if adversarial_count % 100 == 0:
                print(f"  Generated {adversarial_count}/{n_adversarial} adversarial")

    # Random non-identities to fill remaining
    while total_non_identity_count < n_non_identities:
        target_len = random.randint(10, 40)
        indices, source = generate_non_identity(target_len)
        word = word_to_string(indices)

        if word and word not in seen_words and not test_identity(word):
            seen_words.add(word)
            dataset.append({
                'word': word,
                'label': 0,
                'length': len(indices),
                'source': source,
            })
            total_non_identity_count += 1

    print(f"  Generated {total_non_identity_count} non-identities")

    random.shuffle(dataset)
    return dataset


def save_dataset(dataset: List[dict], filepath: str):
    """Save to CSV."""
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)

    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['word', 'label', 'length', 'source'])
        writer.writeheader()
        writer.writerows(dataset)

    print(f"Saved {len(dataset)} samples to {filepath}")


def verify_dataset(dataset: List[dict], name: str, sample_size: int = 100):
    """Verify and print stats."""
    print(f"\n{'='*60}")
    print(f"Verifying: {name}")
    print(f"{'='*60}")

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
    print(f"\nSource distribution:")
    for source, count in sorted(sources.items(), key=lambda x: -x[1]):
        print(f"  {source}: {count}")

    # Check for duplicates
    words = [d['word'] for d in dataset]
    unique_words = set(words)
    if len(unique_words) < len(words):
        print(f"\nWARNING: {len(words) - len(unique_words)} duplicate words found!")
    else:
        print(f"\nNo duplicates found.")

    # Verify random sample
    print(f"\nVerifying {min(sample_size, total)} random samples...")
    sample = random.sample(dataset, min(sample_size, total))
    correct = 0
    errors = []

    for d in sample:
        word = d['word']
        is_identity = test_identity(word)
        expected = d['label'] == 1

        if is_identity == expected:
            correct += 1
        else:
            errors.append({
                'word': word,
                'expected': expected,
                'got': is_identity,
                'source': d['source'],
            })

    print(f"Verification: {correct}/{len(sample)} correct ({100*correct/len(sample):.1f}%)")

    if errors:
        print(f"\nERRORS found ({len(errors)}):")
        for err in errors[:5]:
            word_preview = err['word'][:50] + "..." if len(err['word']) > 50 else err['word']
            print(f"  Word: {word_preview}")
            print(f"    Expected: {'identity' if err['expected'] else 'non-identity'}")
            print(f"    Got: {'identity' if err['got'] else 'non-identity'}")
            print(f"    Source: {err['source']}")

    # Show examples
    print(f"\nExample entries:")
    for i, d in enumerate(random.sample(dataset, min(5, len(dataset)))):
        label_str = "identity" if d['label'] == 1 else "non-identity"
        word_preview = d['word'][:50] + "..." if len(d['word']) > 50 else d['word']
        print(f"  {i+1}. [{label_str}] \"{word_preview}\"")
        print(f"     Length: {d['length']}, Source: {d['source']}")

    return len(errors) == 0


def main():
    """Generate all datasets."""
    print("S5 (Symmetric Group on 5 Elements) - Dataset Generator")
    print("=" * 60)
    print(f"Random seed: {SEED}")

    # Create data directory
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)

    all_valid = True

    # Generate synthetic dataset
    print("\n[1/3] Generating synthetic_1k.csv...")
    random.seed(SEED)
    synthetic = generate_synthetic_dataset(1000)
    save_dataset(synthetic, os.path.join(data_dir, "synthetic_1k.csv"))
    if not verify_dataset(synthetic, "synthetic_1k.csv"):
        all_valid = False

    # Generate augmented dataset
    print("\n[2/3] Generating augmented_1k.csv...")
    random.seed(SEED + 1)
    augmented = generate_augmented_dataset(1000)
    save_dataset(augmented, os.path.join(data_dir, "augmented_1k.csv"))
    if not verify_dataset(augmented, "augmented_1k.csv"):
        all_valid = False

    # Generate hard dataset
    print("\n[3/3] Generating hard_1k.csv...")
    random.seed(SEED + 2)
    hard = generate_hard_dataset(1000)
    save_dataset(hard, os.path.join(data_dir, "hard_1k.csv"))
    if not verify_dataset(hard, "hard_1k.csv"):
        all_valid = False

    print("\n" + "=" * 60)
    if all_valid:
        print("Dataset generation complete! All datasets valid.")
    else:
        print("Dataset generation complete with some issues.")
    print(f"Files saved in: {data_dir}/")
    print("  - synthetic_1k.csv")
    print("  - augmented_1k.csv")
    print("  - hard_1k.csv")


if __name__ == "__main__":
    main()
