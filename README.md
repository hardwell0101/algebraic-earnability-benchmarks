# Algebraic Learnability Benchmarks

**Do neural networks learn algorithms or just patterns?**

This repository contains benchmark datasets, training notebooks, and results for an empirical study on whether neural networks can learn algebraic word problems across 11 mathematical groups. The work investigates the *tractability-learnability gap*: whether computationally tractable problems (solvable in polynomial time) are necessarily learnable by neural networks.

Submitted to the **FLANN Workshop @ Yale 2026** (Formal Languages and Neural Networks).

---

## What's the Word Problem?

Given a sequence of group generators and their inverses (e.g. `a b a⁻¹ b⁻¹`), does the word reduce to the identity element? Each group's word problem induces a formal language with a different computational complexity profile — making them ideal probes for neural network expressivity.

---

## Groups Studied

| Group | Type | Complexity | Dataset Size |
|---|---|---|---|
| F₂ | Free group (rank 2) | Linear (stack) | 300k |
| Z² | Free abelian | Counter / CFL | 300k |
| B₃, B₄ | Braid groups | Matrix arithmetic | 300k each |
| S₄, S₅, S₆ | Symmetric groups | Permutation (regular) | 300k / 30k / 30k |
| Grigorchuk | Intermediate growth | Tree recursion | 30k |
| Thompson's F | Infinite, torsion-free | Tree recursion | 30k |
| Out(F₂) | Outer automorphisms | Matrix arithmetic | 30k |
| BS(1,2) | Baumslag-Solitar | LOGSPACE word problem + **NP-complete** subset sum | 30k |

**Total: ~1.5 million labeled examples**

---

## Key Findings

- **LSTM consistently outperforms Transformer** across nearly all groups, with gaps widening on harder datasets
- Largest hard-set gaps: **F₂ (+19.5 pp)**, **S₆ (+19.1 pp)**, **Z² (+12.0 pp)**
- LSTM generalizes to **unseen word lengths**; Transformer accuracy drops with length
- **BS(1,2) subset sum**: both architectures score at chance (~50–55%) — first neural network test on an NP-complete group-theoretic problem
- Computational tractability does **not** guarantee neural learnability

---

## Dataset Structure

Each group folder follows this structure:

```
groups/<GroupName>/
├── data/
│   ├── *_synthetic_*.csv     # Random words, balanced classes
│   ├── *_augmented_*.csv     # Longer words, greater generator variety  
│   └── *_hard_*.csv          # Words near the decision boundary
├── notebook.ipynb             # Training + evaluation (LSTM & Transformer)
├── generate_dataset.py        # Dataset generation script
├── identity_test.py           # Mathematical verification of labels
└── results/                   # Accuracy CSVs and figures
```

Each CSV row contains a `word` (string of generators) and a binary `label` (1 = identity, 0 = non-identity), mathematically verified.

---

## Models

Two architectures evaluated on binary classification:

- **Bidirectional LSTM** — 2 layers, hidden size 128, ~627K parameters
- **Encoder-only Transformer** — 2 layers, 4 attention heads, FF dim 256, ~117K parameters

Both use mean-pooled representations over the input sequence.

---

## Reproducing Results

Each `notebook.ipynb` is self-contained and runs on Google Colab (tested on T4/A100/L4 GPUs).

```python
# Example: load a dataset
import pandas as pd
df = pd.read_csv("groups/F2/data/f2_hard_100k.csv")
print(df.head())
# word                          label
# a b A b a B                   1
# a b a b A B A B               0
```

---

## Citation

If you use these benchmarks, please cite:

```bibtex
@inproceedings{hakimi2026algebraic,
  title     = {Group Word Problems as Formal Language Benchmarks for Neural Networks},
  author    = {Hakimi},
  booktitle = {FLANN Workshop, Yale University},
  year      = {2026}
}
```

---

## License

MIT License — free to use, modify, and build upon.

---

