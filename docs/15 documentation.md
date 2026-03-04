# New Groups Documentation

---

## Table of Contents

1. [SC - Small Cancellation Group](#sc---small-cancellation-group)
2. [TF - Thompson's Group F](#tf---thompsons-group-f)
3. [H3 - Heisenberg Group H₃(Z)](#h3---heisenberg-group-h₃z)
4. [BS12 - Baumslag-Solitar Group BS(1,2)](#bs12---baumslag-solitar-group-bs12)
5. [OR - One-Relator Group](#or---one-relator-group)
6. [GG - Grigorchuk Group](#gg---grigorchuk-group)
7. [MCG - Mapping Class Group](#mcg---mapping-class-group)
8. [LL - Lamplighter Group](#ll---lamplighter-group)
9. [KT - Knot Group (Trefoil)](#kt---knot-group-trefoil)
10. [SL2Z - Modular Group](#sl2z---modular-group)
11. [Summary Statistics](#summary-statistics)

---

## SC - Small Cancellation Group

### Mathematical Description
Groups with presentation ⟨a, b | r₁, r₂, ...⟩ satisfying the C'(1/6) small cancellation condition. This condition ensures that any common prefix between two distinct relators (or a relator and its cyclic conjugate) has length less than 1/6 of either relator. The word problem is solvable in O(n) time via Dehn's algorithm.

**Example Relator:** r = abababABABAB (length 12)

### Alphabet
| Symbol | Meaning |
|--------|---------|
| `a` | Generator a |
| `A` | Inverse a⁻¹ |
| `b` | Generator b |
| `B` | Inverse b⁻¹ |

### Identity Test
**Dehn's Algorithm:** Scan the word for any subword matching more than half of a cyclic conjugate of a relator. Replace with the shorter complement. Repeat until no replacements possible. Identity iff reduces to empty.

### Dataset Variants

#### Synthetic (sc_synthetic_100k.csv)
| Word | Label | Length |
|------|-------|--------|
| `aAbbBBaAbBAb` | 0 | 12 |
| `BabababABABABb` | 1 | 14 |
| `aAbBabababABABAB` | 1 | 16 |

#### Augmented (sc_augmented_100k.csv)
| Word | Label | Length |
|------|-------|--------|
| `AAbabaBBaabBAbabA` | 0 | 17 |
| `abababABABABaAbbBB` | 1 | 18 |
| `BAabababABABABAbbaAB` | 1 | 20 |

#### Hard (sc_hard_100k.csv)
| Word | Label | Length |
|------|-------|--------|
| `AAbaBAbabABaBAbaBAbabBAbaB` | 0 | 26 |
| `abababABABABBabababABABABbAaBB` | 1 | 30 |
| `AABBabababABABABaabbABababABABABba` | 1 | 34 |

---

## TF - Thompson's Group F

### Mathematical Description
Thompson's group F consists of piecewise-linear homeomorphisms of [0,1] with dyadic rational breakpoints and slopes that are powers of 2. Infinite presentation:

**⟨x₀, x₁, x₂, ... | xₖ⁻¹xₙxₖ = xₙ₊₁ for k < n⟩**

Using finite generators x₀, x₁, the key derived relation is X1 x0 x1 = x0 x0.

### Alphabet
| Symbol | Meaning |
|--------|---------|
| `x0` | Generator x₀ |
| `X0` | Inverse x₀⁻¹ |
| `x1` | Generator x₁ |
| `X1` | Inverse x₁⁻¹ |

### Identity Test
**Tree Pair Normalization:** Each element represented by binary tree pair. Identity iff normalized trees are identical.

### Dataset Variants

#### Synthetic (tf_synthetic_100k.csv)
| Word | Label | Length |
|------|-------|--------|
| `x0 x1 X0 x0 X1` | 0 | 5 |
| `x1 X1 x0 X0` | 1 | 4 |
| `X1 x0 x1 X0 X0` | 1 | 5 |

#### Augmented (tf_augmented_100k.csv)
| Word | Label | Length |
|------|-------|--------|
| `x0 x1 x0 X1 x1 X0 X0 x0 X1 x0 x1` | 0 | 11 |
| `x0 X1 x0 x1 X0 X0 X0 x1 X1 x0` | 1 | 10 |
| `x1 x0 X1 x0 x1 X0 X0 x0 X0 x1 X1` | 1 | 11 |

#### Hard (tf_hard_100k.csv)
| Word | Label | Length |
|------|-------|--------|
| `x0 x0 x1 X0 x1 x0 X1 X0 x0 x1 x0 X1 X0 x1 x0 X0 X1 x0 x1 X0 x0` | 0 | 21 |
| `X1 x0 x1 X0 X0 x1 X1 x0 x1 X0 X0 x0 X0 X1 x0 x1 X0 X0 x1 X1` | 1 | 20 |
| `x0 X1 x0 x1 X0 X0 x1 x1 X1 X1 x0 X0 X1 x0 x1 X0 X0 x0 x0 X0 X0` | 1 | 21 |

---

## H3 - Heisenberg Group H₃(Z)

### Mathematical Description
The discrete Heisenberg group of 3×3 upper triangular integer matrices:

```
[1 a c]
[0 1 b]
[0 0 1]
```

**Presentation:** ⟨a, b, c | [a,b] = c, [a,c] = 1, [b,c] = 1⟩

**Critical:** a b A B = c ≠ identity (the commutator equals c, not 1!)

### Alphabet
| Symbol | Meaning |
|--------|---------|
| `a` | Generator a |
| `A` | Inverse a⁻¹ |
| `b` | Generator b |
| `B` | Inverse b⁻¹ |
| `c` | Central element c = [a,b] |
| `C` | Inverse c⁻¹ |

### Identity Test
**Normal Form Collection:** Rewrite to aˣbʸcᶻ form. Identity iff x = y = z = 0.

### Dataset Variants

#### Synthetic (h3_synthetic_100k.csv)
| Word | Label | Length |
|------|-------|--------|
| `a b c A` | 0 | 4 |
| `a b A B C` | 1 | 5 |
| `b a B A c` | 1 | 5 |

#### Augmented (h3_augmented_100k.csv)
| Word | Label | Length |
|------|-------|--------|
| `a a b c c A B C A` | 0 | 10 |
| `c a b A B C c C b B` | 1 | 10 |
| `a b A B C b a B A c` | 1 | 10 |

#### Hard (h3_hard_100k.csv)
| Word | Label | Length |
|------|-------|--------|
| `a b a b c A A B B c c C C a b A B` | 0 | 18 |
| `a b A B C a b A B C b a B A c b a B A c` | 1 | 20 |
| `c c a b A B C C a a b b A A B B C C c c a b A B C C` | 1 | 26 |

---

## BS12 - Baumslag-Solitar Group BS(1,2)

### Mathematical Description
**BS(1,2) = ⟨a, t | t⁻¹at = a²⟩**

A fundamental **non-automatic group**. The relation states conjugating a by t doubles it: T a t = a a.

### Alphabet
| Symbol | Meaning |
|--------|---------|
| `a` | Generator a |
| `A` | Inverse a⁻¹ |
| `t` | Generator t |
| `T` | Inverse t⁻¹ |

### Identity Test
**Britton's Lemma:** Apply T a t → a a, reduce to normal form. Note: `t a T` does NOT reduce (would require a^(1/2)).

### Dataset Variants

#### Synthetic (bs12_synthetic_100k.csv)
| Word | Label | Length |
|------|-------|--------|
| `t a T a` | 0 | 4 |
| `T a t A A` | 1 | 5 |
| `a T a t A A A` | 1 | 7 |

#### Augmented (bs12_augmented_100k.csv)
| Word | Label | Length |
|------|-------|--------|
| `t t a a T T a a a` | 0 | 9 |
| `T a a t A A A A t T` | 1 | 10 |
| `a a T a t A A A A A` | 1 | 10 |

#### Hard (bs12_hard_100k.csv)
| Word | Label | Length |
|------|-------|--------|
| `t T a a t a T T a a a a T a t A A` | 0 | 17 |
| `T T a t t A A A A T a a t A A A A t T` | 1 | 19 |
| `a T a t A A A T a t A A A A A A a A t T` | 1 | 20 |

---

## OR - One-Relator Group

### Mathematical Description
Groups with a single defining relator. We use the classic example:

**⟨a, b | abab = baba⟩**

This is isomorphic to the trefoil knot group. The relation gives: a b a b B A B A = identity.

### Alphabet
| Symbol | Meaning |
|--------|---------|
| `a` | Generator a |
| `A` | Inverse a⁻¹ |
| `b` | Generator b |
| `B` | Inverse b⁻¹ |

### Identity Test
**Magnus Algorithm:** Apply the relator ababBABA = 1 and its cyclic conjugates. Word equals identity iff it reduces to empty via relator applications and free reductions.

### Dataset Variants

#### Synthetic (or_synthetic_100k.csv)
| Word | Label | Length |
|------|-------|--------|
| `a b a A b B` | 0 | 6 |
| `a b a b B A B A` | 1 | 8 |
| `B a b a b B A B A b` | 1 | 10 |

#### Augmented (or_augmented_100k.csv)
| Word | Label | Length |
|------|-------|--------|
| `a a b b a b A A B B` | 0 | 10 |
| `a A b B a b a b B A B A` | 1 | 12 |
| `A a b a b B A B A b B a A` | 1 | 13 |

#### Hard (or_hard_100k.csv)
| Word | Label | Length |
|------|-------|--------|
| `a b a b a b A B A B A a b a b B A B` | 0 | 18 |
| `a b a b B A B A B a b a b B A B A b a A` | 1 | 20 |
| `A a b a b B A B A b B b a b a b B A B A B a A` | 1 | 23 |

---

## GG - Grigorchuk Group

### Mathematical Description
The first Grigorchuk group is a self-similar group acting on the infinite binary tree. It is:
- Finitely generated but not finitely presented
- Has intermediate growth (between polynomial and exponential)
- A famous counterexample in geometric group theory

**Generators:** a, b, c, d where **ALL are self-inverse** (a² = b² = c² = d² = 1)

**Key Relation:** b c d = 1 (equivalently: d = bc, c = bd, b = cd)

### Alphabet
| Symbol | Meaning |
|--------|---------|
| `a` | Generator a (order 2) |
| `b` | Generator b (order 2) |
| `c` | Generator c (order 2) |
| `d` | Generator d (order 2) |

**Note:** No inverse symbols needed since each generator is its own inverse.

### Identity Test
**Recursive Automaton:** Elements represented by states of a finite automaton acting on binary tree. Identity verified by recursive decomposition.

**Simple Identities:** a a, b b, c c, d d, b c d, d c b, a a b c d, etc.

### Dataset Variants

#### Synthetic (gg_synthetic_100k.csv)
| Word | Label | Length |
|------|-------|--------|
| `a b c a` | 0 | 4 |
| `a a b b` | 1 | 4 |
| `b c d a a` | 1 | 5 |

#### Augmented (gg_augmented_100k.csv)
| Word | Label | Length |
|------|-------|--------|
| `a b c d a b c a` | 0 | 8 |
| `a b c d a a d c b a` | 1 | 10 |
| `b c d b c d a a c c` | 1 | 10 |

#### Hard (gg_hard_100k.csv)
| Word | Label | Length |
|------|-------|--------|
| `a b a c a d b c d a b c a d c b a` | 0 | 17 |
| `a b c d a a b c d a a b c d a a d c b a` | 1 | 20 |
| `b c d d c b a a b c d d c b c c b c d d c b` | 1 | 22 |

---

## MCG - Mapping Class Group

### Mathematical Description
The mapping class group MCG(Σ₂) of a genus-2 surface, generated by Dehn twists around essential curves.

**Generators:** Five Dehn twists τ₁, τ₂, τ₃, τ₄, τ₅

**Relations:**
- Braid relation: τᵢτⱼτᵢ = τⱼτᵢτⱼ when |i-j| = 1
- Commutation: τᵢτⱼ = τⱼτᵢ when |i-j| ≥ 2

### Alphabet
| Symbol | Meaning |
|--------|---------|
| `t1` | Dehn twist τ₁ |
| `T1` | Inverse τ₁⁻¹ |
| `t2` | Dehn twist τ₂ |
| `T2` | Inverse τ₂⁻¹ |
| `t3` | Dehn twist τ₃ |
| `T3` | Inverse τ₃⁻¹ |
| `t4` | Dehn twist τ₄ |
| `T4` | Inverse τ₄⁻¹ |
| `t5` | Dehn twist τ₅ |
| `T5` | Inverse τ₅⁻¹ |

### Identity Test
**Curve Action:** Verify element acts trivially on all curves, or reduce using braid/commutation relations to normal form.

### Dataset Variants

#### Synthetic (mcg_synthetic_100k.csv)
| Word | Label | Length |
|------|-------|--------|
| `t1 t2 t3 T1 T3` | 0 | 5 |
| `t1 t2 t1 T2 T1 T2` | 1 | 6 |
| `t1 T1 t3 t4 t3 T4 T3 T4` | 1 | 8 |

#### Augmented (mcg_augmented_100k.csv)
| Word | Label | Length |
|------|-------|--------|
| `t1 t2 t3 t4 t5 T1 T2 T3 T5 t4` | 0 | 10 |
| `t2 t3 t2 T3 T2 T3 t1 T1 t4 T4` | 1 | 10 |
| `t1 t3 t3 T3 T3 t2 t1 T2 T1 T2 t2 T1` | 1 | 12 |

#### Hard (mcg_hard_100k.csv)
| Word | Label | Length |
|------|-------|--------|
| `t1 t2 t1 t3 t4 t3 T2 T1 T4 T3 t5 t4 t5 T4 T5 T4 t2 t1 T3` | 0 | 19 |
| `t1 t2 t1 T2 T1 T2 t3 t4 t3 T4 T3 T4 t2 t3 t2 T3 T2 T3 t1 T1` | 1 | 20 |
| `t1 t2 t1 T2 T1 T2 t4 t5 t4 T5 T4 T5 t2 t1 t2 T1 T2 T1 t3 T3 t5 T5` | 1 | 22 |

---

## LL - Lamplighter Group

### Mathematical Description
The lamplighter group Z₂ ≀ Z (wreath product) models a lamplighter walking on an integer line with binary lamps.

**Presentation:** ⟨a, t | a² = 1, [a, tⁿat⁻ⁿ] = 1 for all n⟩

**Intuition:**
- t moves the lamplighter right, T moves left
- a toggles the lamp at current position
- a is self-inverse (a² = 1)

### Alphabet
| Symbol | Meaning |
|--------|---------|
| `a` | Toggle lamp (order 2, a = a⁻¹) |
| `t` | Move right |
| `T` | Move left (t⁻¹) |

### Identity Test
**Configuration Check:** Word equals identity iff:
1. Final position = 0 (equal t's and T's)
2. All lamps off (even toggles at each position)

**Examples:**
- `t a T a` = NOT identity (lamps at positions 0 and 1 are on)
- `t a t T a T` = identity (lamp 1 toggled twice, end at position 0)

### Dataset Variants

#### Synthetic (ll_synthetic_100k.csv)
| Word | Label | Length |
|------|-------|--------|
| `t a t T T a` | 0 | 6 |
| `a a t T` | 1 | 4 |
| `t a t T a T` | 1 | 6 |

#### Augmented (ll_augmented_100k.csv)
| Word | Label | Length |
|------|-------|--------|
| `t t a T a t T T a` | 0 | 9 |
| `t t a a T T a a t T` | 1 | 10 |
| `t a t a T a T a T t T` | 1 | 11 |

#### Hard (ll_hard_100k.csv)
| Word | Label | Length |
|------|-------|--------|
| `t t t a T T a t a T T t a t T a T a t T` | 0 | 20 |
| `t t a t T a t T T a a t a T a T T a T t t T` | 1 | 22 |
| `t a t a t a T T a T a t t T a T T a t a T a T t T` | 1 | 25 |

---

## KT - Knot Group (Trefoil)

### Mathematical Description
The fundamental group of the complement of the trefoil knot in S³.

**Wirtinger Presentation:** ⟨a, b | aba = bab⟩

This is equivalent to the braid group relation and the one-relator group with relator ababBABA.

### Alphabet
| Symbol | Meaning |
|--------|---------|
| `a` | Generator a |
| `A` | Inverse a⁻¹ |
| `b` | Generator b |
| `B` | Inverse b⁻¹ |

### Identity Test
**Relator Application:** From aba = bab, derive aba·B·A·B = 1. Apply relator and free reductions.

### Dataset Variants

#### Synthetic (kt_synthetic_100k.csv)
| Word | Label | Length |
|------|-------|--------|
| `a b a A B` | 0 | 5 |
| `a b a B A B` | 1 | 6 |
| `B a b a B A B b` | 1 | 8 |

#### Augmented (kt_augmented_100k.csv)
| Word | Label | Length |
|------|-------|--------|
| `a b a b A B A a B` | 0 | 9 |
| `a A b B a b a B A B` | 1 | 10 |
| `A a b a B A B b B a A` | 1 | 11 |

#### Hard (kt_hard_100k.csv)
| Word | Label | Length |
|------|-------|--------|
| `a b a b a B A B A a b a B A B b A B a A` | 0 | 20 |
| `a b a B A B B a b a B A B b a A b B a A` | 1 | 20 |
| `A a b a B A B b B a b a B A B b a b a B A B B A` | 1 | 24 |

---

## SL2Z - Modular Group

### Mathematical Description
The modular group PSL(2,Z) ≅ SL(2,Z)/{±I} is fundamental in number theory and hyperbolic geometry.

**Presentation:** ⟨S, T | S² = (ST)³ = 1⟩ for PSL(2,Z)

For SL(2,Z): ⟨S, T | S⁴ = 1, (ST)³ = S²⟩

**Matrix Representatives:**
- S = [[0,-1],[1,0]] (rotation by π/2)
- T = [[1,1],[0,1]] (shear)

### Alphabet
| Symbol | Meaning |
|--------|---------|
| `S` | Generator S (order 4) |
| `s` | Inverse S⁻¹ = S³ |
| `T` | Generator T |
| `t` | Inverse T⁻¹ |

### Identity Test
**Matrix Computation:** Multiply matrices, check if result is identity matrix I.

**Key Relations:**
- S S S S = I (S⁴ = 1)
- S T S T S T = S S (i.e., (ST)³ = S²)
- S T S T S T s s = I

### Dataset Variants

#### Synthetic (sl2z_synthetic_100k.csv)
| Word | Label | Length |
|------|-------|--------|
| `S T s T s` | 0 | 5 |
| `S S S S` | 1 | 4 |
| `S T S T S T s s` | 1 | 8 |

#### Augmented (sl2z_augmented_100k.csv)
| Word | Label | Length |
|------|-------|--------|
| `S T S T s T s T S s` | 0 | 10 |
| `S S S S T t S S S S` | 1 | 10 |
| `T S T S T S T s s t S S S S` | 1 | 14 |

#### Hard (sl2z_hard_100k.csv)
| Word | Label | Length |
|------|-------|--------|
| `S T S T S T s S T S T s T s T S s s T t S` | 0 | 21 |
| `S T S T S T s s S S S S T t S T S T S T s s` | 1 | 22 |
| `T S T S T S T s s t S S S S S T S T S T s s S S` | 1 | 24 |

---

## Summary Statistics

### Dataset Overview by Group

| Group | Variant | Rows | Identity % | Non-Identity % | Length Range | Mean Length |
|-------|---------|------|------------|----------------|--------------|-------------|
| SC | Synthetic | 100,000 | 50.0% | 50.0% | 4 - 50 | 27.3 |
| SC | Augmented | 100,000 | 50.0% | 50.0% | 10 - 50 | 29.8 |
| SC | Hard | 100,000 | 50.0% | 50.0% | 20 - 80 | 48.5 |
| TF | Synthetic | 100,000 | 50.0% | 50.0% | 4 - 50 | 26.1 |
| TF | Augmented | 100,000 | 50.0% | 50.0% | 10 - 50 | 28.9 |
| TF | Hard | 100,000 | 50.0% | 50.0% | 20 - 80 | 47.2 |
| H3 | Synthetic | 100,000 | 50.0% | 50.0% | 4 - 50 | 25.8 |
| H3 | Augmented | 100,000 | 50.0% | 50.0% | 10 - 50 | 29.2 |
| H3 | Hard | 100,000 | 50.0% | 50.0% | 20 - 80 | 46.3 |
| BS12 | Synthetic | 100,000 | 50.0% | 50.0% | 4 - 50 | 26.4 |
| BS12 | Augmented | 100,000 | 50.0% | 50.0% | 10 - 50 | 28.7 |
| BS12 | Hard | 100,000 | 50.0% | 50.0% | 20 - 80 | 48.1 |
| OR | Synthetic | 100,000 | 50.0% | 50.0% | 4 - 50 | 26.8 |
| OR | Augmented | 100,000 | 50.0% | 50.0% | 10 - 50 | 29.1 |
| OR | Hard | 100,000 | 50.0% | 50.0% | 20 - 80 | 47.6 |
| GG | Synthetic | 100,000 | 50.0% | 50.0% | 4 - 50 | 25.4 |
| GG | Augmented | 100,000 | 50.0% | 50.0% | 10 - 50 | 28.3 |
| GG | Hard | 100,000 | 50.0% | 50.0% | 20 - 80 | 46.8 |
| MCG | Synthetic | 100,000 | 50.0% | 50.0% | 4 - 50 | 27.1 |
| MCG | Augmented | 100,000 | 50.0% | 50.0% | 10 - 50 | 29.5 |
| MCG | Hard | 100,000 | 50.0% | 50.0% | 20 - 80 | 48.2 |
| LL | Synthetic | 100,000 | 50.0% | 50.0% | 4 - 50 | 24.9 |
| LL | Augmented | 100,000 | 50.0% | 50.0% | 10 - 50 | 28.1 |
| LL | Hard | 100,000 | 50.0% | 50.0% | 20 - 80 | 45.7 |
| KT | Synthetic | 100,000 | 50.0% | 50.0% | 4 - 50 | 26.2 |
| KT | Augmented | 100,000 | 50.0% | 50.0% | 10 - 50 | 28.8 |
| KT | Hard | 100,000 | 50.0% | 50.0% | 20 - 80 | 47.3 |
| SL2Z | Synthetic | 100,000 | 50.0% | 50.0% | 4 - 50 | 26.5 |
| SL2Z | Augmented | 100,000 | 50.0% | 50.0% | 10 - 50 | 29.0 |
| SL2Z | Hard | 100,000 | 50.0% | 50.0% | 20 - 80 | 47.9 |

### Grand Totals

| Group | Full Name | Total Examples | Files |
|-------|-----------|----------------|-------|
| SC | Small Cancellation | 300,000 | 3 |
| TF | Thompson's F | 300,000 | 3 |
| H3 | Heisenberg | 300,000 | 3 |
| BS12 | Baumslag-Solitar | 300,000 | 3 |
| OR | One-Relator | 300,000 | 3 |
| GG | Grigorchuk | 300,000 | 3 |
| MCG | Mapping Class | 300,000 | 3 |
| LL | Lamplighter | 300,000 | 3 |
| KT | Knot (Trefoil) | 300,000 | 3 |
| SL2Z | Modular | 300,000 | 3 |
| **TOTAL** | | **3,000,000** | **30** |

---

## Group Classification

### By Algorithmic Properties

| Property | Groups |
|----------|--------|
| O(n) word problem | SC, F2 |
| Polynomial word problem | TF, H3, OR, GG, MCG, LL, KT, SL2Z |
| Automatic | SC, TF, H3, OR, GG, MCG, LL, KT, SL2Z |
| **Non-automatic** | **BS12** |

### By Algebraic Structure

| Structure | Groups |
|-----------|--------|
| Free-like | SC (hyperbolic) |
| Nilpotent | H3 (2-step) |
| Solvable | LL (metabelian) |
| HNN extension | BS12 |
| Self-similar | GG |
| Surface group related | MCG, TF |
| Knot group | KT |
| Arithmetic | SL2Z |

### By Special Features

| Feature | Groups | Notes |
|---------|--------|-------|
| Self-inverse generators | GG, LL | a² = 1 for some generators |
| Central element | H3 | c commutes with all |
| Braid relations | MCG, KT | τᵢτⱼτᵢ = τⱼτᵢτⱼ |
| Torsion elements | SL2Z, GG | Finite order elements |
| Intermediate growth | GG | Between polynomial and exponential |

### Alphabet Comparison

| Group | Alphabet Size | Token Format | Generators | Inverses |
|-------|--------------|--------------|------------|----------|
| SC | 4 | chars | a, b | A, B |
| TF | 4 | space-sep | x0, x1 | X0, X1 |
| H3 | 6 | space-sep | a, b, c | A, B, C |
| BS12 | 4 | space-sep | a, t | A, T |
| OR | 4 | chars | a, b | A, B |
| GG | 4 | space-sep | a, b, c, d | (self-inverse) |
| MCG | 10 | space-sep | t1-t5 | T1-T5 |
| LL | 3 | space-sep | a, t | (a self-inv), T |
| KT | 4 | chars | a, b | A, B |
| SL2Z | 4 | space-sep | S, T | s, t |

---

## Critical Edge Cases for Neural Networks

### Common Pitfalls by Group

| Group | Trap Example | Equals | Why Tricky |
|-------|--------------|--------|------------|
| H3 | `a b A B` | c (not 1!) | Commutator relation |
| BS12 | `t a T` | undefined | Would need a^(1/2) |
| GG | `b c` | d | Self-inverse with bcd=1 |
| LL | `t a T a` | ≠ 1 | Lamps at different positions |
| SL2Z | `S S` | ≠ 1 | S has order 4, not 2 |

### Identity Patterns Summary

| Group | Key Identity Pattern | Explanation |
|-------|---------------------|-------------|
| SC | Relator insertion | abababABABAB = 1 |
| TF | Relation: X1 x0 x1 = x0 x0 | Tree pair normalization |
| H3 | `a b A B C` | Commutator times C |
| BS12 | `T a t A A` | t⁻¹at = a² applied |
| OR | `a b a b B A B A` | Single relator |
| GG | `b c d` or `a a` | Self-inverse + bcd=1 |
| MCG | `t1 t2 t1 T2 T1 T2` | Braid relation |
| LL | `t a t T a T` | Same lamp toggled twice |
| KT | `a b a B A B` | aba = bab applied |
| SL2Z | `S T S T S T s s` | (ST)³ = S² |
