"""Generate 100k datasets for Out(F2) = GL(2,Z)."""

import csv
import os
import random
import time
from identity_test import (
    test_identity, parse_word, word_to_string,
    evaluate, invert_word, free_reduce, get_inverse,
    ALPHABET, GENERATORS,
)

SEED = 42

BASE_RELATIONS = [
    ("S S S S", "relation_S4"),
    ("S T S T S T S T S T S T", "relation_ST6"),
    ("S T S T S T s s", "relation_ST3_S2"),
    ("S s", "free_cancel"), ("s S", "free_cancel"),
    ("T t", "free_cancel"), ("t T", "free_cancel"),
    ("J J", "relation_J2"),
    ("s s s s", "relation_s4"),
    ("T S S T s s", "relation_TST"),
    ("T S T S T S T S T S T S", "relation_TS6"),
    ("S S S S S S S S", "relation_S8"),
]

CORE_ALPHABET = ['S', 's', 'T', 't']


def random_reduced_word(target_length, alphabet=None):
    if alphabet is None:
        alphabet = CORE_ALPHABET
    word = []
    attempts = 0
    max_attempts = target_length * 10
    while len(word) < target_length and attempts < max_attempts:
        attempts += 1
        gen = random.choice(alphabet)
        if word and word[-1] == get_inverse(gen):
            continue
        word.append(gen)
    return word


def conjugate_identity(identity_tokens, conjugator_length=None):
    if conjugator_length is None:
        conjugator_length = random.randint(2, 8)
    g = random_reduced_word(conjugator_length)
    g_inv = invert_word(g)
    result = g_inv + identity_tokens + g
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
            tokens = parse_word(relation)
            if len(tokens) < target_length // 2 and random.random() < 0.5:
                tokens, suffix = conjugate_identity(tokens, random.randint(2, 5))
                source += suffix
            if tokens and test_identity(word_to_string(tokens)):
                return tokens, source

        elif method == 'product':
            tokens = []
            num = random.randint(2, min(4, max(2, target_length // 4)))
            for _ in range(num):
                relation, _ = random.choice(BASE_RELATIONS)
                tokens.extend(parse_word(relation))
            tokens = free_reduce(tokens)
            if tokens and test_identity(word_to_string(tokens)):
                return tokens, "relation_product"

        elif method == 'word_inverse':
            tokens, source = word_inverse_identity(target_length)
            if tokens and test_identity(word_to_string(tokens)):
                return tokens, source

        elif method == 'conjugate':
            relation, source = random.choice(BASE_RELATIONS)
            base_tokens = parse_word(relation)
            conj_len = max(1, (target_length - len(base_tokens)) // 2)
            tokens, suffix = conjugate_identity(base_tokens, min(conj_len, 10))
            source += suffix
            if tokens and test_identity(word_to_string(tokens)):
                return tokens, source

    return parse_word("S S S S"), "relation_S4_fallback"


def random_identity_deep(target_length, max_attempts=15):
    for _ in range(max_attempts):
        relation, _ = random.choice(BASE_RELATIONS)
        tokens = parse_word(relation)
        depth = random.randint(2, 5)
        for _ in range(depth):
            conj_len = random.randint(2, 5)
            tokens, _ = conjugate_identity(tokens, conj_len)
            if not tokens:
                relation, _ = random.choice(BASE_RELATIONS)
                tokens = parse_word(relation)
        if tokens and len(tokens) >= 4 and test_identity(word_to_string(tokens)):
            return tokens, "deep_relation"
    tokens, _ = word_inverse_identity(target_length)
    if tokens and test_identity(word_to_string(tokens)):
        return tokens, "deep_fallback"
    return parse_word("S S S S"), "deep_fallback_S4"


def generate_non_identity(target_length, max_attempts=30):
    for _ in range(max_attempts):
        tokens = random_reduced_word(target_length)
        if tokens and not test_identity(word_to_string(tokens)):
            return tokens, "random_word"
    return ['S'], "fallback_non_identity"


def perturb_identity(identity_tokens):
    if not identity_tokens or len(identity_tokens) < 2:
        return generate_non_identity(4)[0], "perturbed_fallback"
    tokens = list(identity_tokens)
    for _ in range(5):
        test_tokens = list(tokens)
        pos = random.randint(0, len(tokens) - 1)
        original = test_tokens[pos]
        perturb_type = random.choices(['replace', 'flip_case', 'remove'], weights=[0.5, 0.3, 0.2])[0]
        if perturb_type == 'replace':
            others = [g for g in CORE_ALPHABET if g != original]
            if others:
                test_tokens[pos] = random.choice(others)
        elif perturb_type == 'flip_case':
            test_tokens[pos] = get_inverse(original)
        else:
            if len(test_tokens) > 2:
                test_tokens = test_tokens[:pos] + test_tokens[pos+1:]
        if test_tokens and not test_identity(word_to_string(test_tokens)):
            return test_tokens, "perturbed"
    return generate_non_identity(len(tokens))[0], "perturbed_fallback"


def generate_unique_identity(seen_words, target_len):
    for _ in range(10):
        choice = random.choice(['relation', 'inverse', 'deep', 'conjugate'])
        if choice == 'relation':
            tokens, source = random_identity_from_relations(target_len)
        elif choice == 'inverse':
            tokens, source = word_inverse_identity(target_len)
        elif choice == 'deep':
            tokens, source = random_identity_deep(target_len)
        else:
            relation, _ = random.choice(BASE_RELATIONS)
            base_tokens = parse_word(relation)
            conj_len = random.randint(1, max(1, target_len // 2))
            tokens, _ = conjugate_identity(base_tokens, conj_len)
            source = "conjugation_unique"
        word = word_to_string(tokens)
        if word and word not in seen_words and test_identity(word):
            return tokens, source
    for _ in range(20):
        half_len = random.randint(2, max(3, target_len // 2))
        w = random_reduced_word(half_len)
        w_inv = invert_word(w)
        tokens = w + w_inv
        tokens = free_reduce(tokens)
        word = word_to_string(tokens)
        if word and word not in seen_words and test_identity(word):
            return tokens, "word_inverse_unique"
    base = parse_word("S S S S")
    conj_len = random.randint(3, 15)
    tokens, _ = conjugate_identity(base, conj_len)
    return tokens, "fallback_unique"


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
                tokens, source = random_identity_deep(target_len)
            else:
                tokens, source = generate_unique_identity(seen, target_len)
        elif variant == 'augmented':
            method = random.choices(['conjugate', 'deep', 'unique'], weights=[0.4, 0.3, 0.3])[0]
            if method == 'conjugate':
                relation, _ = random.choice(BASE_RELATIONS)
                base_tokens = parse_word(relation)
                conj_len = max(2, (target_len - len(base_tokens)) // 2)
                tokens, _ = conjugate_identity(base_tokens, min(conj_len, 12))
                source = "conjugation"
            elif method == 'deep':
                tokens, source = random_identity_deep(target_len)
            else:
                tokens, source = generate_unique_identity(seen, target_len)
        else:
            tokens, source = generate_unique_identity(seen, target_len)

        if not tokens:
            continue
        word = word_to_string(tokens)
        if not word or word in seen:
            continue
        if not test_identity(word):
            continue
        if len(tokens) < len_min:
            continue

        seen.add(word)
        dataset.append({'word': word, 'label': 1, 'length': len(tokens), 'source': source})
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
            identity_tokens, _ = random_identity_deep(target_len)
            tokens, source = perturb_identity(identity_tokens)
            adv_count += 1
        else:
            tokens, source = generate_non_identity(target_len)

        if not tokens:
            continue
        word = word_to_string(tokens)
        if not word or word in seen:
            continue
        if test_identity(word):
            continue
        if len(tokens) < len_min:
            continue

        seen.add(word)
        dataset.append({'word': word, 'label': 0, 'length': len(tokens), 'source': source})
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

    print(f"Out(F2) = GL(2,Z) - {N} sample Dataset Generator")
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
