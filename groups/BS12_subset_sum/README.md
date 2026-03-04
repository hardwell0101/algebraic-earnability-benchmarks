# BS(1,2) Subset Sum Problem

## The Group BS(1,2)

The Baumslag-Solitar group BS(1,2) is defined by the presentation:

> **BS(1,2) = \<a, b | b a b^{-1} = a^2\>**

This is a two-generator group with generators `a` and `b` (and their inverses `A = a^{-1}`, `B = b^{-1}`). The single defining relation states that conjugating `a` by `b` squares it. Equivalently:

- `b a = a^2 b` (moving `b` left past `a` doubles the `a`-exponent)
- `b a^k b^{-1} = a^{2k}` (generalised conjugation)

Every element has a **normal form** `B^m a^k b^n` where `m, n >= 0` and `k` is an integer.

### Matrix Representation

BS(1,2) embeds faithfully into 2x2 upper-triangular matrices over the dyadic rationals:

```
a -> [[1, 1], [0, 1]]       A -> [[1, -1], [0, 1]]
b -> [[2, 0], [0, 1]]       B -> [[1/2, 0], [0, 1]]
```

Each element corresponds to a matrix `[[2^s, r], [0, 1]]` where `s` is an integer and `r` is a dyadic rational (`p/2^q`). This representation makes arithmetic exact and equality testing trivial.

## The Subset Sum Problem

**Input:** Group elements `w_1, w_2, ..., w_k` in BS(1,2) and a target element `t`.

**Question:** Does there exist a non-empty subset `S` of `{1, ..., k}` such that the ordered product `w_{i_1} * w_{i_2} * ... * w_{i_r} = t` (where `i_1 < i_2 < ... < i_r` are the elements of `S`)?

**Output:** `1` (YES) or `0` (NO).

### Complexity

- **Word problem** (are two words equal?): solvable in **LOGSPACE** — just compute normal forms via the matrix representation and compare.
- **Subset sum problem**: **NP-complete**.

The NP-completeness was proven by Myasnikov, Nikolaev, and Ushakov (2015). The key insight is that the exponential compression from the relation `b a^k b^{-1} = a^{2k}` allows encoding instances of classical (integer) subset sum into BS(1,2) subset sum. Short words in BS(1,2) can represent exponentially large integers, making the subset sum problem hard despite the word problem being easy.

**Reference:**
> A. Myasnikov, A. Nikolaev, A. Ushakov. *The subset sum problem in the group of circulant matrices and in the Baumslag-Solitar group BS(1,2)*. Mathematics of Computation, 84(295):2469-2490, 2015.

## Dataset Generation

### Positive Instances (label = 1)

1. Generate `k` random words in generators `{a, A, b, B}` of length 2 to `max_word_len`.
2. Randomly select a non-empty subset.
3. Compute the ordered product of the subset elements.
4. The product becomes the target.

### Negative Instances (label = 0)

1. Generate `k` random words.
2. Precompute all `2^k` subset products using dynamic programming.
3. Pick a random subset product as a base target.
4. Perturb the base target's normal form slightly (change `a`-exponent by +/-1, +/-2, +/-3, or adjust `b`-counts).
5. Verify the perturbed target does **not** match any of the `2^k` subset products (hash set lookup).
6. If verification fails, try another perturbation. If all fail, regenerate words.

Every negative label is **brute-force verified** — no subset of the given elements produces the target.

### Dataset Variants

| Variant    | k range | max word length | Subsets checked (max) |
|------------|---------|-----------------|----------------------|
| synthetic  | 5 - 8   | 6               | 255                  |
| augmented  | 8 - 12  | 10              | 4,095                |
| hard       | 12 - 15 | 14              | 32,767               |

### Typical Generation Times (100 samples, Apple Silicon)

| Variant    | Avg positive (ms) | Avg negative (ms) |
|------------|-------------------|--------------------|
| synthetic  | ~0.1              | ~0.3               |
| augmented  | ~0.2              | ~5                 |
| hard       | ~1                | ~50                |

## Input Format

Each instance is encoded as a single string:

```
w1 | w2 | ... | wk || target
```

- Words are space-separated generator tokens: `a`, `A`, `b`, `B`.
- `|` separates group elements.
- `||` separates the element list from the target.

Example:
```
a b A | b a | A A b | a b b || b a a b
```

This encodes 4 elements (`a b A`, `b a`, `A A b`, `a b b`) and target `b a a b`.

## CSV Columns

| Column          | Description                                   |
|-----------------|-----------------------------------------------|
| `instance`      | Encoded instance string (see format above)     |
| `label`         | `1` (positive) or `0` (negative)               |
| `num_elements`  | Number of group elements `k`                   |
| `target_length` | Number of tokens in the target word            |

## Files

```
identity_test.py     - BS(1,2) arithmetic, normal forms, and correctness tests
generate_dataset.py  - Dataset generation with brute-force verification
data/
  synthetic_test_100.csv
  augmented_test_100.csv
  hard_test_100.csv
```

## Usage

```bash
# Run arithmetic tests
python3 identity_test.py

# Generate test datasets (100 samples each)
python3 generate_dataset.py
```
