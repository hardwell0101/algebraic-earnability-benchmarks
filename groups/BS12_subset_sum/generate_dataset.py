#!/usr/bin/env python3
"""
Dataset generation for BS(1,2) subset sum problem.

Given group elements w_1, ..., w_k in BS(1,2) and a target t,
does there exist a subset S such that prod_{i in S} w_i = t?

Generates verified positive and negative instances with brute-force checking.
"""

import random
import csv
import os
import sys
import time
from fractions import Fraction
from identity_test import (
    BS12Element, parse_word, element_to_word, normal_form_to_element
)


def random_word(min_len=2, max_len=6):
    """Generate a random word in BS(1,2) generators {a, A, b, B}."""
    length = random.randint(min_len, max_len)
    generators = ['a', 'A', 'b', 'B']
    tokens = [random.choice(generators) for _ in range(length)]
    return ' '.join(tokens)


def all_subset_products(elements):
    """
    Compute products for all 2^k subsets using dynamic programming.

    products[mask] = product of elements[i] for each bit i set in mask,
    multiplied in increasing index order.

    Uses only 2^k - 1 multiplications (vs k * 2^k for naive approach).
    """
    k = len(elements)
    products = [None] * (1 << k)
    products[0] = BS12Element.identity()
    for i in range(k):
        bit = 1 << i
        for mask in range(bit):
            products[mask | bit] = products[mask] * elements[i]
    return products


def mask_to_indices(mask, k):
    """Convert bitmask to sorted list of indices."""
    return [i for i in range(k) if mask & (1 << i)]


def generate_positive_instance(k, max_word_len):
    """
    Generate a positive instance of BS(1,2) subset sum.

    Returns (words, target_word, label=1, solution_mask).
    """
    words = [random_word(2, max_word_len) for _ in range(k)]
    elements = [parse_word(w) for w in words]

    # Choose a random non-empty subset
    subset_size = random.randint(1, k)
    indices = sorted(random.sample(range(k), subset_size))
    mask = sum(1 << i for i in indices)

    # Compute target as ordered product of subset
    target = BS12Element.identity()
    for i in indices:
        target = target * elements[i]

    target_word = element_to_word(target)
    return words, target_word, 1, mask


def generate_negative_instance(k, max_word_len, max_attempts=100):
    """
    Generate a verified negative instance of BS(1,2) subset sum.

    1. Generate k random words and precompute ALL 2^k subset products.
    2. Pick a random subset product as base, perturb its normal form.
    3. Verify perturbed target is NOT in the set of subset products.

    Returns (words, target_word, label=0, None).
    """
    for attempt in range(max_attempts):
        words = [random_word(2, max_word_len) for _ in range(k)]
        elements = [parse_word(w) for w in words]

        # Precompute all subset products and store in a set for O(1) lookup
        products = all_subset_products(elements)
        product_set = set()
        for mask in range(1, 1 << k):
            product_set.add(products[mask])

        # Pick a random subset and compute base target
        subset_size = random.randint(1, k)
        indices = sorted(random.sample(range(k), subset_size))
        mask = sum(1 << i for i in indices)
        base = products[mask]

        m, k_val, n = base.normal_form()

        # Try perturbations (change a-exponent or b-counts slightly)
        perturbations = [
            (m, k_val + 1, n),
            (m, k_val - 1, n),
            (m, k_val + 3, n),
            (m, k_val - 3, n),
            (m, k_val + 2, n),
            (m, k_val - 2, n),
            (m, k_val, n + 1),
            (m + 1, k_val, n),
        ]
        if n > 0:
            perturbations.append((m, k_val, n - 1))
        if m > 0:
            perturbations.append((m - 1, k_val, n))
            perturbations.append((m - 1, k_val + 1, n))
        perturbations.append((m + 1, k_val + 1, n + 1))

        random.shuffle(perturbations)

        for pm, pk, pn in perturbations:
            if pm < 0 or pn < 0:
                continue

            perturbed = normal_form_to_element(pm, pk, pn)

            if perturbed not in product_set:
                target_word = element_to_word(perturbed)
                return words, target_word, 0, None

    raise RuntimeError(
        f"Failed to generate negative instance after {max_attempts} attempts "
        f"(k={k}, max_word_len={max_word_len})"
    )


def format_instance(words, target_word):
    """Format as 'w1 | w2 | ... | wk || target'."""
    return ' | '.join(words) + ' || ' + target_word


def generate_dataset(num_samples, k_range, max_word_len, variant,
                     output_path=None, seed=42):
    """
    Generate a dataset of BS(1,2) subset sum instances.

    Args:
        num_samples: Total number of instances to generate.
        k_range: (min_k, max_k) range for number of group elements.
        max_word_len: Maximum word length in tokens.
        variant: Name string ("synthetic", "augmented", "hard").
        output_path: CSV file path (optional).
        seed: Random seed.

    Returns:
        Dictionary with stats, rows, and timing info.
    """
    random.seed(seed)

    num_pos = num_samples // 2
    num_neg = num_samples - num_pos

    rows = []
    seen_instances = set()
    dup_skipped = 0

    print(f"\n{'='*60}")
    print(f"Generating {variant} dataset")
    print(f"  samples={num_samples}, k={k_range}, max_word_len={max_word_len}")
    print(f"{'='*60}")

    # --- Positive instances ---
    print(f"\n  Generating {num_pos} positive instances...")
    pos_times = []
    pos_masks = []
    pos_count = 0
    while pos_count < num_pos:
        k = random.randint(*k_range)
        t0 = time.time()
        words, target_word, label, mask = generate_positive_instance(k, max_word_len)
        elapsed = time.time() - t0

        instance = format_instance(words, target_word)
        if instance in seen_instances:
            dup_skipped += 1
            continue
        seen_instances.add(instance)

        target_tokens = len(target_word.split()) if target_word != 'e' else 0
        rows.append({
            'instance': instance,
            'label': label,
            'num_elements': k,
            'target_length': target_tokens,
            '_mask': mask,
            '_words': words,
            '_target_word': target_word,
        })
        pos_times.append(elapsed)
        pos_masks.append(mask)
        pos_count += 1
        if pos_count % 5000 == 0 and pos_count > 0:
            print(f"    {pos_count}/{num_pos} positive")

    # --- Negative instances ---
    print(f"\n  Generating {num_neg} negative instances...")
    neg_times = []
    neg_count = 0
    while neg_count < num_neg:
        k = random.randint(*k_range)
        t0 = time.time()
        words, target_word, label, _ = generate_negative_instance(k, max_word_len)
        elapsed = time.time() - t0

        instance = format_instance(words, target_word)
        if instance in seen_instances:
            dup_skipped += 1
            continue
        seen_instances.add(instance)

        target_tokens = len(target_word.split()) if target_word != 'e' else 0
        rows.append({
            'instance': instance,
            'label': label,
            'num_elements': k,
            'target_length': target_tokens,
            '_mask': None,
            '_words': words,
            '_target_word': target_word,
        })
        neg_times.append(elapsed)
        neg_count += 1
        if neg_count % 5000 == 0 and neg_count > 0:
            print(f"    {neg_count}/{num_neg} negative")

    # Shuffle
    random.shuffle(rows)

    # Save to CSV (without internal fields)
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(
                f, fieldnames=['instance', 'label', 'num_elements', 'target_length']
            )
            writer.writeheader()
            for row in rows:
                writer.writerow({
                    'instance': row['instance'],
                    'label': row['label'],
                    'num_elements': row['num_elements'],
                    'target_length': row['target_length'],
                })
        print(f"\n  Saved to {output_path}")

    # Statistics
    avg_pos_time = sum(pos_times) / len(pos_times) if pos_times else 0
    avg_neg_time = sum(neg_times) / len(neg_times) if neg_times else 0

    print(f"\n  --- Statistics ---")
    print(f"  Positive: {num_pos}  |  Negative: {num_neg}")
    print(f"  Duplicates skipped: {dup_skipped}")
    print(f"  Avg positive gen time: {avg_pos_time*1000:.2f} ms")
    print(f"  Avg negative gen time: {avg_neg_time*1000:.2f} ms")

    return {
        'variant': variant,
        'rows': rows,
        'avg_pos_time': avg_pos_time,
        'avg_neg_time': avg_neg_time,
    }


def show_examples(rows, num_examples=3):
    """Display example positive and negative instances with verification."""
    pos = [r for r in rows if r['label'] == 1]
    neg = [r for r in rows if r['label'] == 0]

    print(f"\n  --- Positive Examples ---")
    for i, row in enumerate(pos[:num_examples]):
        words = row['_words']
        target_word = row['_target_word']
        mask = row['_mask']
        k = row['num_elements']
        indices = mask_to_indices(mask, k)

        # Verify: recompute product of subset
        elements = [parse_word(w) for w in words]
        target = parse_word(target_word)
        product = BS12Element.identity()
        for idx in indices:
            product = product * elements[idx]

        verified = product == target
        print(f"\n  POSITIVE #{i+1} (k={k}):")
        print(f"    Elements: {' | '.join(words)}")
        print(f"    Target:   {target_word}")
        print(f"    Solution: subset {{{', '.join(str(j) for j in indices)}}}")
        print(f"    Verified: {verified}")

    print(f"\n  --- Negative Examples ---")
    for i, row in enumerate(neg[:num_examples]):
        words = row['_words']
        target_word = row['_target_word']
        k = row['num_elements']

        # Full brute-force verification
        elements = [parse_word(w) for w in words]
        target = parse_word(target_word)
        products = all_subset_products(elements)
        found = None
        for m in range(1, 1 << k):
            if products[m] == target:
                found = m
                break

        print(f"\n  NEGATIVE #{i+1} (k={k}):")
        print(f"    Elements: {' | '.join(words)}")
        print(f"    Target:   {target_word}")
        print(f"    Brute-force checked {(1 << k) - 1} subsets: "
              f"{'NONE match' if found is None else f'FOUND match at mask={found} (BUG!)'}")


# ──────────────────────────────────────────────────────────
# Variant configurations
# ──────────────────────────────────────────────────────────
VARIANTS = {
    'synthetic':  {'k_range': (5, 8),   'max_word_len': 6},
    'augmented':  {'k_range': (8, 12),  'max_word_len': 10},
    'hard':       {'k_range': (12, 15), 'max_word_len': 14},
}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Generate BS(1,2) subset sum datasets'
    )
    parser.add_argument(
        '--count', type=int, default=100000,
        help='Number of samples per variant (default: 100000)',
    )
    parser.add_argument(
        '--seed', type=int, default=42,
        help='Base random seed (default: 42)',
    )
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, 'data')

    for variant_name, cfg in VARIANTS.items():
        output_path = os.path.join(
            data_dir, f'{variant_name}_{args.count}.csv'
        )
        generate_dataset(
            num_samples=args.count,
            k_range=cfg['k_range'],
            max_word_len=cfg['max_word_len'],
            variant=variant_name,
            output_path=output_path,
            seed=args.seed + hash(variant_name) % 1000,
        )

    print(f"\n{'='*60}")
    print("ALL DATASETS GENERATED SUCCESSFULLY")
    print(f"{'='*60}")
