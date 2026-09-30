# Task 2 — controls

Run before any discovery number is read. Reproduce with:

```
python3 scripts/sweep.py data/manifest_control_positive.tsv \
    data/assemblies/control_positive results/controls/positive --evalue 1e-3
python3 scripts/sweep.py data/manifest_control_negative.tsv \
    data/assemblies/control_negative results/controls/negative --evalue 1e-3
python3 scripts/analyse_controls.py results/controls/positive results/controls/negative
```

Query set: 43 proteins, SHA-256 in `data/refseqs/PROVENANCE.md`.
Search: six-frame `tblastn`, e-value 1e-3 — permissive by design, so that the
negative control sets the working threshold rather than a threshold being chosen
in advance and making the false-positive floor unmeasurable.

## Detection floor — positive control

30 genomes, 18 species with recorded bioluminescence, 2.25 Gbp.
15 of 30 (50%) carry no annotation.

| | |
|---|---|
| All four genes recovered somewhere in the genome | **30/30 (100%)** |
| Best cluster at tier 1 (four genes in 100 kb, ORF pending) | 19/30 (63.3%) |
| tier 2 | 10/30 (33.3%) |
| tier 3 | 1/30 (3.3%) |
| tier 4 / nothing | 0/30 |

Sensitivity for gene recovery is 100%. **Tier 1 is not 100%, and should not be**:
Ke 2020 reports `cph` sitting outside the cluster on separate scaffolds in four
of five *Mycena*, so a *Mycena* genome landing at tier 2 is the published cluster
architecture reproducing, not a detection failure. The tier-1 fraction is a
statement about genome architecture and assembly contiguity, not about
sensitivity. That is why the two rows above are reported separately and why
tiers are never summed.

## False-positive floor — negative control

87 Ascomycete genomes, 30 species, 2.89 Gbp. 34 of 87 carry no annotation.

| | |
|---|---|
| **Best cluster at tier 1** | **0/87 (0.0%)** |
| tier 2 | 21/87 (24.1%) |
| tier 3 | 51/87 (58.6%) |
| tier 4 | 15/87 (17.2%) |
| All four genes somewhere in the genome | **69/87 (79.3%)** |

**Both numbers matter and they say opposite-looking things.**

At the permissive cut, **79.3% of Ascomycete genomes return all four genes**.
That is not a defect in the search; it is what the pathway's enzyme families
look like. HispS is a polyketide synthase, H3H an FAD monooxygenase and CPH a
hydrolase, and Ascomycetes carry large paralogous families of all three. A
positives-only control could never have measured this, and a four-gene
presence/absence criterion would have produced a ~79% false-positive rate.

**Zero of 87 reach tier 1.** The 100 kb co-localisation requirement is what
carries the specificity, not the gene hits.

## Operating point, set from the controls

Identity of the highest-scoring locus per gene:

| gene | positive min | negative max | margin | verdict |
|---|---|---|---|---|
| HispS | 43.2% | 35.3% | **+7.8** | clean |
| H3H | 40.6% | 36.4% | **+4.3** | clean |
| **Luz** | **73.2%** | **37.5%** | **+35.7** | **clean, wide** |
| CPH | 31.8% | 52.6% | −20.8 | **overlap — 78/87 negatives admitted** |

Two conclusions, both anticipated by the brief and now measured rather than
assumed:

1. **Luz is the diagnostic gene**, by a very large margin. Nothing else comes
   close.
2. **CPH cannot be used as evidence on its own.** At any threshold that retains
   all true CPH loci, 78 of 87 Ascomycete genomes are admitted. H3H separates,
   but by only 4.3 points, so it is weak evidence alone.

### A metric caveat worth stating

"The negative ceiling" can be computed two ways and they disagree substantially:

| gene | identity of top-scoring locus | max identity over any locus |
|---|---|---|
| HispS | 35.3% | 54.3% |
| H3H | 36.4% | 61.4% |
| Luz | 37.5% | 57.7% |
| CPH | 52.6% | 56.8% |

The first is used, because the top-scoring locus is what a caller would take as
the gene. The second is recorded so that the gap is visible rather than hidden
by a choice of statistic. An earlier reading of these controls used a mixture of
the two and reported a cleaner separation than the data supports; the table above
is the corrected one.

## Two control-design faults the run exposed

Both would have corrupted the detection floor silently.

### 1. NCBI files non-genomes under species names

`GCA_055690705.1`, filed as *Omphalotus olearius*, is 426 contigs totalling
221 kb at a mean length of 520 bp — 0.8% of a real fungal genome, and a marker or
amplicon set rather than an assembly. It returned zero hits. Left in, it would
have been recorded as a **detection failure**, putting the measured floor at
32/33 for a reason with nothing to do with detection. A 5 Mbp size floor now
excludes it, and removed nine further entries from the negative control, several
of them 0.00 Mbp.

### 2. Luminescence is not always a property of a species

Two assemblies filed as *Panellus stipticus* — `GCA_965154615.1` and
`GCA_965154625.1`, **both from the single Sanger BioSample SAMEA9873913**, so not
independent observations either — returned:

| gene | identity | Ascomycete ceiling | true-positive floor |
|---|---|---|---|
| HispS | 35.6% | 35.3% | 43.2% |
| H3H | 33.8% | 36.4% | 40.6% |
| **Luz** | **28.3% / 28.7%** | 37.5% | **73.2%** |
| CPH | 59.0% | 52.6% | 31.8% |

Their HispS, H3H and Luz hits sit **at or below the identity ceiling measured in
Ascomycete genomes that carry no pathway at all**. The query set contains three
*P. stipticus* Luz sequences from Kotlobay's SI; a genome of that species would
be expected near 100%, and every other positive is at or above 73.2%. **These
genomes do not carry the cluster.**

*P. stipticus* is the textbook case of population-dependent luminescence,
carrying both luminescent and non-luminescent lineages; Rabara & Xie 2025
(*J Fungi* 11:774) report the cluster absent from a non-luminous strain whose
genome is otherwise near-identically syntenic with the luminous one. The Sanger
material is almost certainly that non-luminous lineage.

Left in the positive control these two would have been scored as a three-gene
detection failure and would have set the measured detection floor at 28.3%
identity for Luz — a statement about a specimen that has no Luz, not about the
sensitivity of the search. They are quarantined to
`data/manifest_control_quarantined.tsv` with the reason recorded, not deleted.

**The general lesson: a positive control assembled from species names is unsound
wherever luminescence is strain-dependent.** Any species-level positive control
in this project inherits this, and every unexpected negative in a nominally
luminous species has to be checked against it before being called a detection
failure.

**This is also a Branch A observation in its own right.** A six-frame search
over the raw assembly — the method the published surveys did not use — finds no
cluster remnant in this genome. That is an independent confirmation of Rabara &
Xie's result by a more sensitive method, and it is a stronger negative than
theirs because a degraded or frameshifted remnant is exactly what six-frame
search recovers and annotation-based search does not. Carried forward to
Branch A.

## What the controls license

- A **tier 1** call is trustworthy: 0/87 in genomes that should have none.
- A **tier 2** call is not, on its own: 21/87 negatives reach it.
- **Luz identity above ~40%** is strong evidence; below it, nothing is.
- **CPH is not evidence**; H3H alone is weak evidence.
- Any negative reported from the full sweep must carry these numbers and the
  assembly count it was measured over.
