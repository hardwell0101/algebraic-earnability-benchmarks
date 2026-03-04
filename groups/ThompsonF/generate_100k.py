"""Generate 100k datasets for Thompson's group F."""

import csv
import os
import random
import time
from identity_test import (
    parse_word, word_to_string, test_identity,
    free_reduce, expand_higher_generators, Word,
)

SEED = 42
MAX_INDEX = 5

BASE_RELATIONS = [
    "x0 X0", "X0 x0", "x1 X1", "X1 x1", "x2 X2", "X2 x2", "x3 X3",
    "X0 x1 x0 X2", "X0 x2 x0 X3", "X0 x3 x0 X4", "X1 x2 x1 X3", "X1 x3 x1 X4",
    "x0 X2 X0 x1", "x0 X3 X0 x2", "x1 X3 X1 x2",
    "x0 x1 X1 X0", "x1 x0 X0 X1", "X0 X1 x1 x0", "x0 x2 X2 X0",
]


def random_word(length, max_index=MAX_INDEX):
    word = []
    for _ in range(length):
        idx = random.randint(0, max_index)
        sign = random.choice([1, -1])
        word.append((idx, sign))
    return word


def random_reduced_word(target_length, max_index=MAX_INDEX):
    word = random_word(target_length * 2, max_index)
    word = expand_higher_generators(word)
    word = free_reduce(word)
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


def invert_word(word):
    return [(idx, -sign) for idx, sign in reversed(word)]


def concatenate_words(words):
    result = []
    for w in words:
        result.extend(w)
    return result


def conjugate_word(word, conjugator_length=None, reduce=True):
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


def random_identity_from_relations(target_length, max_attempts=20):
    base_words = [parse_word(r) for r in BASE_RELATIONS]
    for _ in range(max_attempts):
        method = random.choices(['product', 'conjugate', 'nested'], weights=[0.5, 0.3, 0.2])[0]
        if method == 'product':
            word = []
            num_relations = random.randint(2, min(4, target_length // 3 + 1))
            for _ in range(num_relations):
                word.extend(random.choice(base_words))
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
        else:
            base = list(random.choice(base_words))
            g1 = random_word(random.randint(1, 2), max_index=1)
            word = concatenate_words([invert_word(g1), base, g1])
            word = free_reduce(word)
            if word and len(word) >= 2 and test_identity(word):
                return word, "nested_conjugation"
    base = list(random.choice(base_words[:6]))
    g = random_word(max(1, target_length // 3), max_index=1)
    word = concatenate_words([invert_word(g), base, g])
    word = free_reduce(word)
    if word and test_identity(word):
        return word, "fallback_conjugation"
    return parse_word("x0 x1 X1 X0"), "fallback_simple"


def random_identity_deep(target_length, max_attempts=10):
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


def generate_non_identity(target_length, max_attempts=10):
    for _ in range(max_attempts):
        word = random_reduced_word(target_length)
        if word and not test_identity(word):
            return word, "random_word"
    fallback = [(0, 1), (1, 1)]
    return fallback, "fallback_non_identity"


def perturb_identity(identity_word):
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
            word, source = random_identity_deep(target_len)
        elif variant == 'augmented':
            word, source = random_identity_from_relations(target_len)
            if len(word) < target_len and random.random() < 0.7:
                aug = conjugate_word(list(word), random.randint(3, 6), reduce=False)
                aug = free_reduce(aug)
                if aug and test_identity(aug):
                    word = aug
                    source = "conjugation_augmented"
        else:
            word, source = random_identity_from_relations(target_len)

        if not word:
            continue
        w_str = word_to_string(word)
        if not w_str or w_str in seen:
            continue
        if not test_identity(word):
            continue
        if len(word) < len_min:
            continue

        seen.add(w_str)
        dataset.append({'word': w_str, 'label': 1, 'length': len(word), 'source': source})
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
            identity_word, _ = random_identity_deep(target_len)
            word, source = perturb_identity(identity_word)
            adv_count += 1
        else:
            word, source = generate_non_identity(target_len)

        if not word:
            continue
        w_str = word_to_string(word)
        if not w_str or w_str in seen:
            continue
        if test_identity(word):
            continue
        if len(word) < len_min:
            continue

        seen.add(w_str)
        dataset.append({'word': w_str, 'label': 0, 'length': len(word), 'source': source})
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
        word = parse_word(d['word'])
        result = test_identity(word)
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

    print(f"Thompson's Group F - {N} sample Dataset Generator")
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
