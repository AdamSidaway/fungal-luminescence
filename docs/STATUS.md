# Status

Updated: 2026-09-30

## Task 0 — prior art (GATES BRANCH A)
- [x] Europe PMC sweep, three queries, with and without `SRC:PPR`
- [x] bioRxiv direct search, last 18 months
- [x] Patent landscape complete — see docs/IP_POSITION.md
      Brief's premise corrected: the named Light Bio applications recite NO
      mammalian and NO oncology claims, and are narrow (>=90% identity + named
      substitutions). The real exposure is US 12,473,582 B2, GRANTED 2025-11-18,
      whose claim 1 is sequence-independent and covers any non-higher-fungus cell
      containing 3-hydroxyhispidin. Verified in-session from the official PDF.
      Branch B risk concentrates in the L3 genus family (>=40% HispS, >=60% H3H/CPH).
- [x] **VERDICT: BRANCH A IS OPEN.** No published or preprinted work has searched
      for the four genes in unannotated assemblies by any six-frame or
      nucleotide-level method. All three at-scale surveys are proteome-only on
      pre-filtered Agaricales: Kotlobay 2018 n=57 (blastp), Ke 2020 n=42
      (OrthoFinder), Kim 2022 n=40. Of 926 Agaricales assemblies at NCBI only
      231 (25%) are annotated. See docs/PRIOR_ART.md.

## Environment
- [x] Toolchain: BLAST+ 2.12, exonerate 2.4.0, MAFFT 7.505, HMMER 3.4, FastTree,
      seqkit, DIAMOND 2.1.9, MMseqs2 15-6f452, NCBI datasets 18.38.0
- [x] NCBI eutils, NCBI FTP-over-HTTP, Europe PMC all reachable
- Container limits: 4 cores, ~30 GB writable disk. The full 936 Gbp cannot be
  held at once; the sweep must stream download -> search -> delete.

## Task 1 — mining run
- [x] Assembly census: 26,465 latest fungal assemblies, 20,310 (76.7%) unannotated
- [x] Query proteins built: 43 sequences (HispS 11, H3H 14, CPH 6, Luz 12) from
      Kotlobay 2018 SI Datasets S1-S4. THERE ARE NO ACCESSIONS for these genes in
      any of the three primary papers; the SI datasets are coding nucleotide and
      are translated here. Validated: nnLuz = 267 aa, matching the paper's text;
      no internal stops. Checksummed in data/refseqs/PROVENANCE.md.
- [ ] Six-frame sweep, controls first
- [ ] exonerate protein2genome refinement
- [ ] Tier assignment on cluster completeness
- [ ] **HispS domain architecture must be recorded per locus** (KR/DH present or
      absent). The brief has the truncation backwards: non-luminous orthologues
      are the LONGER ones, carrying extra ketoreductase and dehydratase domains;
      luminous HispS lacks them (1,504-1,774 aa vs 2,484 aa). Sequence identity
      alone would mis-score a non-luminous full-length PKS as a pathway gene.

## Task 2 — controls (BEFORE any discovery number)
- [x] Positive manifest: 33 assemblies, 18 species with recorded luminescence, 2.35 Gbp
      (18/33 unannotated — 55%)
- [x] Negative manifest: 87 Ascomycete assemblies, 30 species, 2.79 Gbp, <=3/species
- [ ] Positive sweep -> detection floor
- [ ] Negative sweep -> false-positive floor

## Branch A — distribution
- [ ] blocked on Task 0 verdict and Task 2 controls

## Branch B — engineering (NOT FOR PUBLICATION until IP checked)
Hold stands and is now better justified — see docs/IP_POSITION.md.
Every ASR output and thermotolerant candidate must carry its percent identity
to the relevant patent SEQ IDs as a required deliverable.
- [ ] B1 in-cluster PPTase scan (highest value scientifically AND least
      encumbered on the patent evidence; answerable from sequence alone)
- [ ] B2 naturally thermotolerant orthologues
- [ ] B3 ancestral sequence reconstruction (report posterior per site, not one sequence)
- [ ] B4 natural NADH-preferring H3H

## Compute scope — RESOLVED
Full 26,465-assembly sweep benchmarked at ~10-12 h wall clock. Affordable.
Branch A will NOT be restricted to the Agaricales. See docs/SCOPE.md.
