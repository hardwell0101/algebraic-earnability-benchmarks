"""Generate datasets for Grigorchuk group — optimized for speed."""

import csv
import os
import random
import time

SEED = 42
random.seed(SEED)

GENERATORS = ['a', 'b', 'c', 'd']

IDENTITY_SEEDS = [
    'aa', 'bb', 'cc', 'dd',
    'bcd', 'bdc', 'cbd', 'cdb', 'dbc', 'dcb',
    'adadadad', 'dadadada', 'bcdbcd',
]


def random_word(length):
    return ''.join(random.choices(GENERATORS, k=length))


def reduce_word(word):
    from identity_test import reduce_word as rw
    return rw(word)


def test_identity_safe(word):
    from identity_test import test_identity as ti
    try:
        return ti(word)
    except (RecursionError, Exception):
        return None  # unknown — skip


def make_identity(target_len):
    """Build an identity word using conjugation for variety."""
    base = random.choice(IDENTITY_SEEDS)
    if target_len > 10:
        n_copies = random.randint(1, max(1, target_len // 8))
        base = base * n_copies
        base = reduce_word(base)
    conj_len = random.randint(1, max(1, target_len // 2))
    g = random_word(conj_len)
    g_inv = g[::-1]  # all generators are self-inverse
    word = reduce_word(g_inv + base + g)
    return word


def make_non_identity(target_len):
    """Generate a non-identity word."""
    word = random_word(target_len)
    word = reduce_word(word)
    return word


def perturb_identity(target_len):
    """Make an identity then flip one char — almost certainly non-identity."""
    word = make_identity(target_len)
    if not word or len(word) < 2:
        return random_word(target_len)
    word_list = list(word)
    idx = random.randint(0, len(word_list) - 1)
    original = word_list[idx]
    others = [g for g in GENERATORS if g != original]
    word_list[idx] = random.choice(others)
    return reduce_word(''.join(word_list))


def save_dataset(samples, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['word', 'label', 'length'])
        writer.writeheader()
        writer.writerows(samples)


def generate_dataset(n, variant, seed=42):
    random.seed(seed)

    if variant == 'synthetic':
        len_min, len_max = 4, 30
    elif variant == 'augmented':
        len_min, len_max = 10, 35
    else:  # hard
        len_min, len_max = 20, 40

    target_pos = n // 2
    target_neg = n - target_pos
    samples = []

    # === IDENTITIES ===
    count = 0
    skipped = 0
    t0 = time.time()
    while count < target_pos:
        target_len = random.randint(len_min, len_max)
        word = make_identity(target_len)

        if not word or len(word) < len_min or len(word) > 50:
            skipped += 1
            continue

        result = test_identity_safe(word)
        if result is None or not result:
            skipped += 1
            continue

        samples.append({'word': word, 'label': 1, 'length': len(word)})
        count += 1

        if count % 50 == 0:
            elapsed = time.time() - t0
            rate = count / elapsed if elapsed > 0 else 0
            print(f"  Identities: {count}/{target_pos} ({elapsed:.1f}s, {rate:.0f}/s, {skipped} skipped)")

    print(f"  ✅ Identities done: {count} in {time.time()-t0:.1f}s ({skipped} skipped)")

    # === NON-IDENTITIES ===
    count = 0
    skipped = 0
    t1 = time.time()
    while count < target_neg:
        target_len = random.randint(len_min, len_max)

        if variant == 'hard' and random.random() < 0.6:
            word = perturb_identity(target_len)
        else:
            word = make_non_identity(target_len)

        if not word or len(word) < len_min or len(word) > 50:
            skipped += 1
            continue

        result = test_identity_safe(word)
        if result is None or result:
            skipped += 1
            continue

        samples.append({'word': word, 'label': 0, 'length': len(word)})
        count += 1

        if count % 50 == 0:
            elapsed = time.time() - t1
            rate = count / elapsed if elapsed > 0 else 0
            print(f"  Non-identities: {count}/{target_neg} ({elapsed:.1f}s, {rate:.0f}/s, {skipped} skipped)")

    print(f"  ✅ Non-identities done: {count} in {time.time()-t1:.1f}s ({skipped} skipped)")

    random.shuffle(samples)
    return samples


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', type=int, default=100_000)
    args = parser.parse_args()
    N = args.count

    suffix = '100k' if N == 100_000 else f'test_{N // 1000}k' if N >= 1000 else f'test_{N}'
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

    print(f"Grigorchuk Group - {N} sample Dataset Generator")
    print("=" * 60)

    for variant, seed in [('synthetic', SEED), ('augmented', SEED+1), ('hard', SEED+2)]:
        fname = f'{variant}_{suffix}.csv'
        print(f"\n--- Generating {fname} ---")
        t0 = time.time()
        samples = generate_dataset(N, variant, seed=seed)

        ids = sum(1 for s in samples if s['label'] == 1)
        lengths = [s['length'] for s in samples]
        dupes = len(samples) - len(set(s['word'] for s in samples))

        print(f"  Total: {len(samples)} | Pos: {ids} | Neg: {len(samples)-ids}")
        print(f"  Lengths: min={min(lengths)}, max={max(lengths)}, avg={sum(lengths)/len(lengths):.1f}")
        print(f"  Duplicates: {dupes}")
        print(f"  Time: {time.time()-t0:.1f}s")

        filepath = os.path.join(data_dir, fname)
        save_dataset(samples, filepath)
        print(f"  Saved to {filepath}")

    print("\n✅ All done!")


if __name__ == "__main__":
    main()
