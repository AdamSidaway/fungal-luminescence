# Fungal bioluminescence pathway — genome mining

Mining the hispidin bioluminescence pathway across fungal genome assemblies,
including the unannotated majority.

**This repository is self-contained.** It shares no sequences, panels, HMMs or
results with `Fungal-Barrel-Proteins` or `luciferase-sequence-mining`, and
nothing is to be moved between them in either direction.

## The pathway

Kotlobay et al. 2018, *PNAS* 115(50):12728 established the four-gene pathway:

| Gene | Reaction | Enzyme class |
|---|---|---|
| `HispS` | caffeic acid → hispidin | polyketide synthase (PKS) |
| `H3H`   | hispidin → 3-hydroxyhispidin (the luciferin) | FAD monooxygenase, NADPH-preferring |
| `Luz`   | 3-hydroxyhispidin → light | luciferase |
| `CPH`   | oxyluciferin → caffeic acid | caffeylpyruvate hydrolase (recycles substrate) |

Roughly 100 luminous species are described, out of ~100,000 described fungi,
all within the Agaricales.

## Two branches, deliberately kept apart

Both run off the same mining output. They do not share an output channel.

- **Branch A — Distribution.** Where the cluster sits across fungi, and whether
  it appears in species with no recorded luminescence. Intended for
  publication. Gated on Task 0 (prior art).
- **Branch B — Engineering.** Which natural sequences would help the pathway
  run at 37 °C in a mammalian cell. **Branch B outputs stay out of anything
  intended for publication until the IP position is checked.**

Branch B exists because the optimised pathway sits roughly 100× below firefly
in mammalian cells, against about 10× above it in plants — a thousand-fold
swing for identical enzymes.

### IP status gating Branch B

| Document | Subject | Status |
|---|---|---|
| US 2025/0075191 A1 | Light Bio family; mammalian and oncology claims recited | pending |
| WO 2025/049575 A1 | same family | pending |
| CN 116732084 A | ΔN20 truncation | — |

Ancestral and thermotolerant sequences are **novel sequences** and are treated
as such.

## Scale of the problem

Measured from NCBI GenBank `assembly_summary.txt` (fungi), 2026-09-30:

| | |
|---|---|
| Latest fungal assemblies | 26,465 |
| With protein annotation | 6,155 (23.3%) |
| **Unannotated** | **20,310 (76.7%)** |
| Total sequence | 936 Gbp |

A search against predicted proteomes sees 23% of what is there. A polyketide
synthase inside an unannotated assembly is exactly the kind of gene a caller
misses — which is why the sweep is six-frame `tblastn` against nucleotide
assemblies, with `exonerate protein2genome` behind it to recover exon structure
(the raw frame is wrong wherever an intron falls inside the alignment, and
these are spliced fungal genes).

The same point holds inside the positive control: **18 of 33 assemblies of
species with recorded bioluminescence (55%) carry no annotation.** A
proteome-only survey cannot see half of its own positive controls.

## Tiering — on cluster completeness, not single-gene identity

| Tier | Definition |
|---|---|
| 1 | all four genes within a 100 kb window, each with an intact ORF |
| 2 | three of four in the window, or all four with one broken ORF |
| 3 | two of four, or any single gene with no partner nearby |
| 4 | single-gene hits only |

`H3H` and `CPH` have non-luminescent relatives, so a lone hit to either means
nothing. `Luz` is the most diagnostic of the four.

**Tiers are never summed.** Tiers 3 and 4 are counted and located and never
pooled upward.

## Standing rules

1. Every sweep emits the sequences it called, not only the tables. A table
   without sequences cannot be checked or aligned by anyone later.
2. Any negative carries its coverage: how many assemblies, annotated or not,
   and what the detection floor was from the controls.
3. Tiers are never summed.
4. Controls run before any discovery number is read.

## Layout

```
data/
  assembly_summary_fungi.tsv         NCBI GenBank fungal assembly table
  manifest_control_positive.tsv      33 assemblies, recorded luminous species
  manifest_control_negative.tsv      87 assemblies, Ascomycota
  refseqs/                           query proteins (committed)
  assemblies/                        downloaded genomes (gitignored, streamed)
scripts/
results/
  controls/    branchA/    branchB/
docs/
```

## Status

See `docs/STATUS.md`.
