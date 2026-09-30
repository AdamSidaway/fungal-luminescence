# Sweep scope and compute budget

Measured 2026-09-30 in this container (4 cores, ~28 GB writable disk free).

## Question

Can the six-frame sweep cover all 26,465 fungal assemblies, or must Branch A be
restricted to the Agaricales?

## Benchmark

Query: 4 proteins, 3,223 aa total — chosen to match the real query set's size
profile (`HispS` is a ~1,400–2,000 aa PKS; `H3H`, `Luz`, `CPH` are 270–500 aa).

Subject: `GCA_014462675.1`, 167 Mbp, 155 contigs — an Armillaria-scale genome,
i.e. near the large end of the fungal range.

| Route | Wall time | Hits |
|---|---|---|
| `makeblastdb` + `tblastn -num_threads 4` | 1.6 s + 4.4 s = **6.0 s** | 70 |
| `tblastn -subject` (no DB build) | 14.8 s | 70 |

`-subject` mode is single-threaded, so building a throwaway BLAST DB per genome
is 2.5x faster for an identical hit set. The DB route is what the sweep uses.

Throughput: **0.036 s per Mbp on 4 threads.**

## Extrapolation to the full set

| | |
|---|---|
| Assemblies | 26,465 |
| Total sequence | 936 Gbp |
| Mean genome | 35 Mbp (~1.3 s each) |
| **Search** | **~9.5 h** |
| Download, 281 GB gzipped at observed ~1 GB/min (4 parallel) | ~4.7 h |
| Peak disk, streaming | < 5 GB |

Download and search pipeline concurrently, so wall clock is bounded by search:
**~10–12 h as a background run.**

`exonerate protein2genome` refinement runs only on hit-bearing loci, which are a
small fraction of the total, and is not a material addition to this budget.

## Conclusion

**The full-set sweep is affordable. Branch A is not compute-limited and will not
be restricted to the Agaricales.**

This matters for the science, not just the budget: Branch A's central question is
whether the cluster appears in species with no recorded luminescence. Restricting
the search to the clade where luminescence is already known would assume the
answer. The negative — "the cluster is confined to the luminous Agaricales" — is
only publishable if the search actually looked outside them, across a stated
number of assemblies, with a detection floor measured from the controls.

## Disk strategy

The 281 GB gzipped total cannot be held at once against a ~28 GB allowance. The
sweep streams: fetch a batch, build DB, search, record hits **and called
sequences**, delete the genome, advance. Only assemblies carrying hits are
retained, for the `exonerate` pass.

Note on this container: writable disk is a fixed allowance, so `df` reporting
"Avail" near zero with low "Used" means the allowance is spent rather than the
machine being broken. Deletes still succeed when writes fail.
