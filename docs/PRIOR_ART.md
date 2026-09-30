# Task 0 — prior art, literature strand

Search date 2026-09-30. Gates Branch A.

## Verdict: Branch A is OPEN

**No published or preprinted work has searched for HispS, H3H, Luz or CPH in
unannotated genome assemblies by any six-frame or nucleotide-level method.**

Three at-scale surveys exist. All three search predicted proteomes of a small,
taxonomically pre-filtered set:

| Study | Set searched | n | Method | Genes |
|---|---|---|---|---|
| Kotlobay 2018 PNAS 115:12728 | complete proteomes, Agaricales (JGI MycoCosm / NCBI / UniProt; 5 predicted by the authors with Augustus) | **57** | **blastp against predicted proteins**, + narrow `exonerate` rescue of expected-but-missing proteins within the same 57 | all four + CYP450 |
| Ke 2020 PNAS 117:31267 | annotated Basidiomycota proteomes | **42** | **OrthoFinder orthogroup inference** over proteomes | all four + CYP450 |
| Kim 2022 Genomics 114:110514 | 17 luminescent + 23 non-luminescent Agaricales | **40** | annotation-based protein comparison (**not verified — paywalled**) | cluster genes |

Kotlobay's `exonerate` step is the one that looks closest to a genome-level
search, and it is not one: it rescues proteins already expected to be present,
inside an already-selected, already-assembled, already-Agaricales set of 57. It
is an annotation-miss rescue, not a de novo scan.

Targeted queries pairing the cluster with `tblastn`, `"six-frame"`, `HMMER`,
`"hidden Markov"` or `"genome mining"` return 7 records; the only genuine
cluster papers among them are Ke 2020 and Palkina 2023, neither of which uses
those methods.

### What is left unexamined

| | |
|---|---|
| Agaricales assemblies at NCBI | **926** |
| of which annotated | **231 (25%)** |
| Agaricomycetes assemblies | 2,057 |
| Largest prior survey | 57 |

About three quarters of even the Agaricales assembly space has never been
looked at by any method, and none of it by a method that works on unannotated
sequence.

**The 25 new *Mycena* genomes in Harder et al. 2024 (Cell Genomics 4:100586) —
the largest single addition of mycenoid genomes ever made — have never been
examined for the cluster by anyone.** That paper is about genome expansion,
transposable elements and secretomes; it does not analyse the luciferase cluster
at all.

### Why the existing negatives are weak negatives

1. **Prior work predicts hits outside the annotated luminous set.** Ke 2020
   places the luciferase orthogroup in the LCA of the mycenoid + marasmioid clade
   **and Schizophyllaceae** — outside the luminous clade, and contradicting
   Kotlobay's "base of Agaricales". Kotlobay documents retained-but-diverged
   `hisps`/`h3h`/`luz` duplicates in non-luminescent fungi, a **partial `hisps` in
   *Armillaria mellea*** and a **truncated `luz` in *Guyanagaster necrorhiza***
   (scored non-luminous).
2. **Truncated, pseudogenised and frameshifted copies are exactly what gene
   predictors drop** and exactly what a translated-nucleotide search recovers. The
   existing non-luminous negatives were produced by the method least able to see
   them.
3. **Phenotype labels are assertions, not measurements.** Heinzelmann et al. 2024
   (*Mycoscience* 65:173) argue luminescence in many *Mycena* is simply
   overlooked, and new luminous lineages keep appearing (*Eoscyphella* 2023; two
   new Mycenaceae 2025). Every prior survey's "non-luminous" column inherits this.

Point 3 matters for how Branch A's central finding must be read. A complete
cluster in a species with no recorded luminescence has three readings — the
species is luminous and nobody looked; the cluster is present and silent; or it
does something else with the same chemistry — and the literature says the first
is not merely plausible but actively expected in *Mycena*.

### Qualification

Branch A is open as a **completeness and detection-sensitivity** question, not as
an origins question. The evolutionary narrative (single origin at the
mycenoid/marasmioid ancestor, ~160 Myr, repeated independent losses, cluster in
TE-rich fast-evolving regions in mycenoids) is well established and a broader
search will not overturn it.

One unresolved gap: Kim 2022 is paywalled and could not be read. Its abstract
indicates annotation-based comparison and its scale (40) is below the other two,
but if the novelty case is stated as "no survey used tblastn", that paper should
be obtained and its Methods checked before publication.

## A correction to the brief: the HispS truncation runs the other way

The brief says Markina 2023 "reports truncated HispS orthologues in non-luminous
fungi that do not make hispidin".

Two corrections.

**The citation.** The paper is **Palkina et al. 2023, *IJMS* 24(2):1317**,
"Domain Truncation in Hispidin Synthase Orthologs from Non-Bioluminescent Fungi
Does Not Lead to Hispidin Biosynthesis". Markina N.M. is fifth author.

**The direction.** The non-luminous orthologues are not the truncated ones — they
are the **longer** ones. Luminous HispS *lacks* a ketoreductase (KR) and a
dehydratase (DH) domain that the non-luminous orthologues carry. Palkina's
experiment was to **truncate the non-luminous enzymes artificially**, deleting
DH+KR (+/- the C-terminal ACP), to test whether removing those domains would
confer hispidin synthesis. It did not: every truncated variant was dark.

| Construct | Species (non-bioluminescent Agaricales) | Result |
|---|---|---|
| cgPKS | *Cortinarius glaucopus* | full length: no luminescence, no hispidin by LC-MS |
| hsPKS | *Hypholoma sublateritium* | full length: **dim luminescence**, ~2 orders below nnHispS; hispidin below detection |
| gcPKS | *Gymnopilus chrysopellus* | full length: no luminescence |
| all three, 2Δ and 2Δ_C | DH+KR(+ACP) deleted | **all dark** |

Architecture: nnHispS = AMP-binding, ACP, KS(N+C), AT, C-terminal ACP. The
non-luminous orthologues carry KR and DH in addition.

**This changes the mining design, and is the most useful thing the literature
strand produced.** Domain architecture, not sequence identity, is the diagnostic
for a *functional* HispS:

- luminous HispS measured from Kotlobay's SI: **1,504–1,774 aa** (n=11)
- Palkina's non-luminous gcPKS: **2,484 aa**

A ~700–980 aa difference, consistent with two extra domains. So HispS hit length
is a cheap first-pass discriminator, and an HMM scan for KR and DH domains within
each HispS locus separates the two classes directly. A tier-1 call that relies on
sequence similarity alone would score a non-luminous full-length PKS as a
pathway gene. **Branch A's question "how far does that pattern extend" is
answerable, but only if the sweep records domain architecture per HispS locus.**

## Query sequences: there are no accessions

Verified against the papers themselves.

- **Kotlobay 2018** deposits genomes and transcriptomes under BioProject
  **PRJNA476325** and figshare 6738953, but the four enzymes appear **only** as
  FASTA in SI Datasets S1–S4, keyed by species name. No per-gene accession.
  The datasets are **coding nucleotide, not protein**, despite headers naming the
  enzyme.
- **Shakhova 2024** gives Addgene plasmids (input plasmid pX037/FBP1 = Addgene
  #167156) and figshare 10.6084/m9.figshare.24623817. No sequence accessions.
- **Palkina 2023** Data Availability reads **"Not applicable"**. Sequences are
  recoverable only from a Jalview alignment in SI and ten Benchling construct
  links.
- **Ke 2020 is the exception** and has clean accessions: BioProject
  **PRJNA623720**; *M. chlorophos* JACAZE000000000, *M. indigotica*
  JACAZF000000000, *M. kentingensis* JACAZG000000000, *M. sanguinolenta*
  JACAZH000000000, *M. venus* JACAZI000000000.

The query set is therefore reconstructed from Kotlobay's SI and checksummed —
see `data/refseqs/PROVENANCE.md`. It cannot be cited by accession, which is
itself worth stating in any methods section.

Validation: nnLuz translates to **267 aa**, matching the length stated in
Kotlobay's text, and no sequence carries an internal stop codon. One CPH
(*A. fuscipes*) lacks a start methionine and is a partial CDS.

## Shakhova 2024 variants (Branch B reference, not for publication)

Defined as mutations on *N. nambi* wild type:

| Variant | Composition |
|---|---|
| nnLuz_v3 | nnLuz + T99P, T192S, A199P |
| nnLuz_v4 | nnLuz_v3 + I3S, N4T, F11L, I63T |
| nnH3H_v2 | nnH3H + D37E, V181I, S323M, M385K |
| HispS | **no improved variant found**; replaced by the *M. citricolor* orthologue mcitHispS |
| FBP2 | nnHispS + nnH3H_v2 + nnLuz_v4 + nnCPH + NpgA |
| FBP3 | mcitHispS + nnH3H_v2 + nnLuz_v4 + nnCPH + NpgA — 1–2 orders brighter than FBP1 |

Note the overlap with the patent position: these are exactly the substitutions
enumerated in the Light Bio claims (see `docs/IP_POSITION.md`).

Two observations that bear on Branch B:
- **No improved HispS variant was obtainable by engineering**; the gain came from
  swapping in a *natural orthologue* from another species. That is direct support
  for B2's premise that natural sequence space is worth mining before engineering.
- **NpgA was confirmed necessary in most plant hosts.** The cognate-PPTase
  question (B1) is therefore not speculative — a borrowed PPTase is already known
  to be load-bearing.

## Preprint picture

| Query | Europe PMC | + SRC:PPR |
|---|---|---|
| Q1 bioluminescence × fungi × evolution/distribution | 12,208 | 97 (0.8%) |
| Q2 hispidin/CPH/H3H/luz × genome/cluster | 170,092 | 2,970 (1.7%) |
| Q3 ASR × luciferase/PKS/monooxygenase × thermostab* | **64** | **0** |

Q2 is contaminated: `luz` tokenises as a free term matching Spanish and
Portuguese text and author names. A cleaned form returns **275** hits, which is
the real size of this literature. Do not quote the 170k figure.

The with/without difference is small throughout. This field is
published-journal-dominated; nothing is hiding in preprints.

**Q3 returning zero preprints and nothing at all connecting ASR to the fungal
pathway means B3 is unoccupied.** The adjacent ASR work is on Renilla-type
luciferase (Schenkmayerova 2021), fungal azaphilone PKSs (Chiang 2024) and FAD
monooxygenase stereoselectivity (Chiang 2023 — H3H's own family), none on HispS,
H3H, Luz or CPH.

## Cheapest strong first test

Rabara & Xie 2025 (*J Fungi* 11:774) report **all four genes absent** from a
non-luminous *Panellus stipticus* strain (KUC8834) whose genome is otherwise
near-identically syntenic with the luminous strain — on the basis of a generic
BLAST against a draft assembly. They also report `cph` absent from the *luminous*
assembly, which is itself a likely detection failure given the cluster is known
to contain it.

Two genomes is not a survey, and that is exactly the class of negative a
six-frame search exists to re-test. A partial or frameshifted remnant in KUC8834
would be a cheap, strong result and a direct demonstration of the method's added
sensitivity over the published approach.
