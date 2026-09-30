# Results

Outputs of the mining run. Written by `scripts/sweep.py`, analysed by
`scripts/analyse_controls.py`.

```
controls/positive/   32 genomes, species with recorded bioluminescence
controls/negative/   87 Ascomycete genomes
sweep/               the full-set run
branchA/             distribution
branchB/             engineering (NOT for publication until IP is checked)
```

Per directory:

| file | contents | committed |
|---|---|---|
| `hits_raw.tsv` | every tblastn HSP, with bitscore, identity, coordinates | no — large, regenerable |
| `loci.tsv` | HSPs merged into candidate gene calls, one row per locus | yes |
| `clusters.tsv` | loci grouped into 100 kb windows, with tier | yes |
| `per_assembly.tsv` | one row per genome | yes |

## Standing rules that apply to everything here

1. **Every sweep emits the sequences it called, not only the tables.** A table
   without sequences cannot be checked or aligned by anyone later. Sequence
   output comes from the `exonerate protein2genome` pass and is committed
   alongside the tables.
2. **Any negative carries its coverage** — how many assemblies, annotated or
   not, and what the detection floor was from the controls.
3. **Tiers are never summed.** Genomes are counted once at their best tier, so
   the rows are disjoint by construction, and they must still not be added.
4. **Controls are read before any discovery number.**

## A note on reading these tables

The sweep runs at a deliberately permissive e-value (1e-3). These tables are
therefore *candidate* calls, not filtered results. The working threshold is set
from the negative control per gene, because HispS (a polyketide synthase), H3H
(an FAD monooxygenase) and CPH (a hydrolase) all have large paralogous families
in fungi that carry no bioluminescence pathway. Luz is the diagnostic gene.
Do not read a raw row count here as a finding.
