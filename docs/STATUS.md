# Status

Updated: 2026-09-30

## Task 0 — prior art (GATES BRANCH A)
- [~] Europe PMC sweep, three queries, each run with and without `SRC:PPR` — running
- [~] bioRxiv direct search, last 18 months — running
- [~] Patent landscape: US 2025/0075191 A1, WO 2025/049575 A1, CN 116732084 A — running
- [ ] Verdict: is Branch A still open?

## Environment
- [x] Toolchain: BLAST+ 2.12, exonerate 2.4.0, MAFFT 7.505, HMMER 3.4, FastTree,
      seqkit, DIAMOND 2.1.9, MMseqs2 15-6f452, NCBI datasets 18.38.0
- [x] NCBI eutils, NCBI FTP-over-HTTP, Europe PMC all reachable
- Container limits: 4 cores, ~30 GB writable disk. The full 936 Gbp cannot be
  held at once; the sweep must stream download -> search -> delete.

## Task 1 — mining run
- [x] Assembly census: 26,465 latest fungal assemblies, 20,310 (76.7%) unannotated
- [ ] Query proteins from primary papers (blocked on Task 0 accession recovery)
- [ ] Six-frame sweep, controls first
- [ ] exonerate protein2genome refinement
- [ ] Tier assignment on cluster completeness

## Task 2 — controls (BEFORE any discovery number)
- [x] Positive manifest: 33 assemblies, 18 species with recorded luminescence, 2.35 Gbp
      (18/33 unannotated — 55%)
- [x] Negative manifest: 87 Ascomycete assemblies, 30 species, 2.79 Gbp, <=3/species
- [ ] Positive sweep -> detection floor
- [ ] Negative sweep -> false-positive floor

## Branch A — distribution
- [ ] blocked on Task 0 verdict and Task 2 controls

## Branch B — engineering (NOT FOR PUBLICATION until IP checked)
- [ ] B1 in-cluster PPTase scan (highest value; answerable from sequence alone)
- [ ] B2 naturally thermotolerant orthologues
- [ ] B3 ancestral sequence reconstruction (report posterior per site, not one sequence)
- [ ] B4 natural NADH-preferring H3H

## Compute scope — RESOLVED
Full 26,465-assembly sweep benchmarked at ~10-12 h wall clock. Affordable.
Branch A will NOT be restricted to the Agaricales. See docs/SCOPE.md.
