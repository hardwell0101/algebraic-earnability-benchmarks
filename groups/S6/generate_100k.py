"""Generate 100k datasets for S6."""

import csv
import os
import random
import time
from identity_test import (
    test_identity, parse_word, word_to_string,
    evaluate, invert_word, free_reduce,
    ALPHABET, VALID_INDICES, N,
)

SEED = 42

BASE_RELATIONS = [
    ("s1 s1", "self_cancel"), ("s2 s2", "self_cancel"),
    ("s3 s3", "self_cancel"), ("s4 s4", "self_cancel"), ("s5 s5", "self_cancel"),
    ("s1 s2 s1 s2 s1 s2", "braid_12"), ("s2 s3 s2 s3 s2 s3", "braid_23"),
    ("s3 s4 s3 s4 s3 s4", "braid_34"), ("s4 s5 s4 s5 s4 s5", "braid_45"),
    ("s2 s1 s2 s1 s2 s1", "braid_21"), ("s3 s2 s3 s2 s3 s2", "braid_32"),
    ("s4 s3 s4 s3 s4 s3", "braid_43"), ("s5 s4 s5 s4 s5 s4", "braid_54"),
    ("s1 s3 s1 s3", "commute_13"), ("s3 s1 s3 s1", "commute_31"),
    ("s1 s4 s1 s4", "commute_14"), ("s4 s1 s4 s1", "commute_41"),
    ("s1 s5 s1 s5", "commute_15"), ("s5 s1 s5 s1", "commute_51"),
    ("s2 s4 s2 s4", "commute_24"), ("s4 s2 s4 s2", "commute_42"),
    ("s2 s5 s2 s5", "commute_25"), ("s5 s2 s5 s2", "commute_52"),
    ("s3 s5 s3 s5", "commute_35"), ("s5 s3 s5 s3", "commute_53"),
    ("s1 s1 s2 s2", "double_cancel"), ("s3 s3 s4 s4", "double_cancel"),
    ("s4 s4 s5 s5", "double_cancel"),
    ("s1 s2 s3 s4 s5 s5 s4 s3 s2 s1", "palindrome"),
]


def random_reduced_word(target_length):
    word = []
    attempts = 0
    while len(word) < target_length and attempts < target_length * 10:
        attempts += 1
        gen = random.choice(list(VALID_INDICES))
        if word and word[-1] == gen:
            continue
        word.append(gen)
    return word


def conjugate_identity(identity_indices, conjugator_length=None):
    if conjugator_length is None:
        conjugator_length = random.randint(2, 8)
    g = random_reduced_word(conjugator_length)
    g_inv = invert_word(g)
    result = g_inv + identity_indices + g
    result = free_reduce(result)
    return result, "_conjugated"


def word_inverse_identity(length):
    half_len = max(2, length // 2)
    w = random_reduced_word(half_len)
    w_inv = invert_word(w)
    result = w + w_inv
    result = free_reduce(result)
    return result, "word_inverse"


def random_identity_from_relations(target_length, max_attempts=20):
    for _ in range(max_attempts):
        method = random.choices(
            ['single_relation', 'product', 'word_inverse', 'conjugate'],
            weights=[0.2, 0.3, 0.25, 0.25]
        )[0]
        if method == 'single_relation':
            relation, source = random.choice(BASE_RELATIONS)
            indices = parse_word(relation)
            if len(indices) < target_length // 2 and random.random() < 0.5:
                indices, suffix = conjugate_identity(indices, random.randint(2, 5))
                source += suffix
            if indices and test_identity(word_to_string(indices)):
                return indices, source
        elif method == 'product':
            indices = []
            num = random.randint(2, min(4, max(2, target_length // 4)))
            for _ in range(num):
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
            relation, source = random.choice(BASE_RELATIONS)
            base_indices = parse_word(relation)
            conj_len = max(1, (target_length - len(base_indices)) // 2)
            indices, suffix = conjugate_identity(base_indices, min(conj_len, 10))
            source += suffix
            if indices and test_identity(word_to_string(indices)):
                return indices, source
    return parse_word("s1 s1"), "self_cancel_fallback"


def random_identity_deep(target_length, max_attempts=15):
    for _ in range(max_attempts):
        relation, _ = random.choice(BASE_RELATIONS)
        indices = parse_word(relation)
        depth = random.randint(2, 5)
        for _ in range(depth):
            conj_len = random.randint(2, 5)
            indices, _ = conjugate_identity(indices, conj_len)
            if not indices:
                relation, _ = random.choice(BASE_RELATIONS)
                indices = parse_word(relation)
        if indices and len(indices) >= 4 and test_identity(word_to_string(indices)):
            return indices, "deep_relation"
    indices, _ = word_inverse_identity(target_length)
    if indices and test_identity(word_to_string(indices)):
        return indices, "deep_fallback"
    return parse_word("s1 s1"), "deep_fallback_self"


def generate_non_identity(target_length, max_attempts=30):
    for _ in range(max_attempts):
        indices = random_reduced_word(target_length)
        if indices and not test_identity(word_to_string(indices)):
            return indices, "random_word"
    return [1], "fallback_non_identity"


def perturb_identity(identity_indices):
    if not identity_indices or len(identity_indices) < 2:
        return generate_non_identity(4)[0], "perturbed_fallback"
    indices = list(identity_indices)
    for _ in range(10):
        test_indices = list(indices)
        pos = random.randint(0, len(indices) - 1)
        original = test_indices[pos]
        perturb_type = random.choices(['replace', 'remove', 'insert'], weights=[0.5, 0.25, 0.25])[0]
        if perturb_type == 'replace':
            others = [g for g in VALID_INDICES if g != original]
            if others:
                test_indices[pos] = random.choice(others)
        elif perturb_type == 'remove':
            if len(test_indices) > 2:
                test_indices = test_indices[:pos] + test_indices[pos+1:]
        else:
            new_gen = random.choice(list(VALID_INDICES))
            test_indices = test_indices[:pos] + [new_gen] + test_indices[pos:]
        if test_indices and not test_identity(word_to_string(test_indices)):
            return test_indices, "perturbed"
    return generate_non_identity(len(indices))[0], "perturbed_fallback"


def generate_unique_identity(seen_words, target_len):
    for _ in range(10):
        choice = random.choice(['relation', 'inverse', 'deep', 'conjugate'])
        if choice == 'relation':
            indices, source = random_identity_from_relations(target_len)
        elif choice == 'inverse':
            indices, source = word_inverse_identity(target_len)
        elif choice == 'deep':
            indices, source = random_identity_deep(target_len)
        else:
            relation, _ = random.choice(BASE_RELATIONS)
            base_indices = parse_word(relation)
            conj_len = random.randint(1, max(1, target_len // 2))
            indices, _ = conjugate_identity(base_indices, conj_len)
            source = "conjugation_unique"
        word = word_to_string(indices)
        if word and word not in seen_words and test_identity(word):
            return indices, source
    for _ in range(20):
        half_len = random.randint(2, max(3, target_len // 2))
        w = random_reduced_word(half_len)
        w_inv = invert_word(w)
        indices = w + w_inv
        indices = free_reduce(indices)
        word = word_to_string(indices)
        if word and word not in seen_words and test_identity(word):
            return indices, "word_inverse_unique"
    base = parse_word("s1 s1")
    conj_len = random.randint(3, 15)
    indices, _ = conjugate_identity(base, conj_len)
    return indices, "fallback_unique"


def save_dataset(dataset, filepath):
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['word', 'label', 'length', 'source'])
        writer.writeheader()
        writer.writerows(dataset)


def generate_dataset(n, variant, seed=42):
    random.seed(seed)

    if variant == 'synthetic':
        len_min, len_max = 4, 50
    elif variant == 'augmented':
        len_min, len_max = 10, 50
    else:
        len_min, len_max = 20, 80

    target_ids = n // 2
    target_nonids = n - target_ids
    dataset = []
    seen = set()

    # Identities
    id_count = 0
    t0 = time.time()
    while id_count < target_ids:
        target_len = random.randint(len_min, len_max)
        if variant == 'hard':
            if random.random() < 0.7:
                indices, source = random_identity_deep(target_len)
            else:
                indices, source = generate_unique_identity(seen, target_len)
        elif variant == 'augmented':
            method = random.choices(['conjugate', 'deep', 'unique'], weights=[0.4, 0.3, 0.3])[0]
            if method == 'conjugate':
                relation, _ = random.choice(BASE_RELATIONS)
                base_indices = parse_word(relation)
                conj_len = max(2, (target_len - len(base_indices)) // 2)
                indices, _ = conjugate_identity(base_indices, min(conj_len, 12))
                source = "conjugation"
            elif method == 'deep':
                indices, source = random_identity_deep(target_len)
            else:
                indices, source = generate_unique_identity(seen, target_len)
        else:
            indices, source = generate_unique_identity(seen, target_len)

        if not indices:
            continue
        word = word_to_string(indices)
        if not word or word in seen:
            continue
        if not test_identity(word):
            continue
        if len(indices) < len_min:
            continue

        seen.add(word)
        dataset.append({'word': word, 'label': 1, 'length': len(indices), 'source': source})
        id_count += 1
        if id_count % 5000 == 0:
            print(f"  Identities: {id_count}/{target_ids} ({time.time()-t0:.1f}s)")

    print(f"  Identities done: {id_count} in {time.time()-t0:.1f}s")

    # Non-identities
    nonid_count = 0
    t1 = time.time()
    n_adversarial = target_nonids * 2 // 3 if variant == 'hard' else 0
    adv_count = 0

    while nonid_count < target_nonids:
        target_len = random.randint(len_min, len_max)
        if variant == 'hard' and adv_count < n_adversarial:
            identity_indices, _ = random_identity_deep(target_len)
            indices, source = perturb_identity(identity_indices)
            adv_count += 1
        else:
            indices, source = generate_non_identity(target_len)

        if not indices:
            continue
        word = word_to_string(indices)
        if not word or word in seen:
            continue
        if test_identity(word):
            continue
        if len(indices) < len_min:
            continue

        seen.add(word)
        dataset.append({'word': word, 'label': 0, 'length': len(indices), 'source': source})
        nonid_count += 1
        if nonid_count % 5000 == 0:
            print(f"  Non-identities: {nonid_count}/{target_nonids} ({time.time()-t1:.1f}s)")

    print(f"  Non-identities done: {nonid_count} in {time.time()-t1:.1f}s")

    random.shuffle(dataset)
    return dataset


def verify_sample(dataset, n_check=500):
    check = random.sample(dataset, min(n_check, len(dataset)))
    errors = 0
    for d in check:
        result = test_identity(d['word'])
        expected = d['label'] == 1
        if result != expected:
            errors += 1
    return errors


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', type=int, default=100_000)
    args = parser.parse_args()
    N = args.count

    suffix = '100k' if N == 100_000 else f'test_{N // 1000}k' if N >= 1000 else f'test_{N}'

    print(f"S6 - {N} sample Dataset Generator")
    print("=" * 60)

    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

    for variant, seed in [('synthetic', SEED), ('augmented', SEED+1), ('hard', SEED+2)]:
        fname = f'{variant}_{suffix}.csv'
        print(f"\n--- Generating {fname} ---")
        t0 = time.time()
        dataset = generate_dataset(N, variant, seed=seed)

        errors = verify_sample(dataset, n_check=min(500, N))
        ids = sum(1 for d in dataset if d['label'] == 1)
        lengths = [d['length'] for d in dataset]

        print(f"  Total: {len(dataset)}, Identities: {ids}, Non-identities: {len(dataset)-ids}")
        print(f"  Lengths: min={min(lengths)}, max={max(lengths)}, avg={sum(lengths)/len(lengths):.1f}")
        print(f"  Unique words: {len(set(d['word'] for d in dataset))}")
        print(f"  Verification errors: {errors}/{min(500, N)}")
        print(f"  Time: {time.time()-t0:.1f}s")

        filepath = os.path.join(data_dir, fname)
        save_dataset(dataset, filepath)
        print(f"  Saved to {filepath}")


if __name__ == "__main__":
    main()
