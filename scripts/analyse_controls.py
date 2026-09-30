#!/usr/bin/env python3
"""
Task 2 analysis: the detection floor and the false-positive floor.

Both controls must be read before any discovery number. This script reports,
per gene:
  - positive control: what fraction of genomes of recorded-luminous species
    return the gene, and with what scores -> sensitivity, the detection floor
  - negative control: what the same search returns in Ascomycete genomes that
    should not carry the cluster -> the false-positive floor
  - the score separation between the two, which is what sets the working
    threshold

Per gene, not pooled. HispS is a polyketide synthase, H3H an FAD monooxygenase
and CPH a hydrolase; all three have large paralogous families in Ascomycetes, so
a hit to any of them in a negative genome is expected and is not by itself a
false positive for the CLUSTER. Luz is the diagnostic gene. Pooling the four
would hide exactly the distinction the controls exist to measure.

Usage:
    python3 scripts/analyse_controls.py results/controls/positive results/controls/negative
"""
import csv
import sys
from collections import defaultdict
from pathlib import Path
from statistics import median

GENES = ["HispS", "H3H", "Luz", "CPH"]


def read_tsv(path):
    with open(path) as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def load(dirpath):
    d = Path(dirpath)
    return {
        "loci": read_tsv(d / "loci.tsv"),
        "clusters": read_tsv(d / "clusters.tsv"),
        "per_assembly": read_tsv(d / "per_assembly.tsv"),
    }


def best_per_assembly_gene(loci):
    """Highest-scoring locus per (assembly, gene)."""
    best = {}
    for l in loci:
        k = (l["assembly"], l["gene"])
        b = float(l["best_bitscore"])
        if k not in best or b > float(best[k]["best_bitscore"]):
            best[k] = l
    return best


def describe(vals):
    if not vals:
        return "none"
    vals = sorted(vals)
    return (f"n={len(vals):<4} min={vals[0]:>7.1f} med={median(vals):>7.1f} "
            f"max={vals[-1]:>8.1f}")


def gene_report(pos, neg, pos_asm, neg_asm):
    print("\n" + "=" * 78)
    print("PER-GENE DETECTION AND FALSE-POSITIVE FLOOR")
    print("=" * 78)
    print(f"{'gene':<7} {'pos genomes w/ hit':>19} {'neg genomes w/ hit':>19}")
    print("-" * 78)

    pb = best_per_assembly_gene(pos["loci"])
    nb = best_per_assembly_gene(neg["loci"])
    sep = {}

    for g in GENES:
        pg = [pb[k] for k in pb if k[1] == g]
        ng = [nb[k] for k in nb if k[1] == g]
        print(f"{g:<7} {len(pg):>6}/{pos_asm} ({100*len(pg)/pos_asm:>5.1f}%) "
              f"{len(ng):>6}/{neg_asm} ({100*len(ng)/neg_asm:>5.1f}%)")
        sep[g] = (pg, ng)

    for g in GENES:
        pg, ng = sep[g]
        print(f"\n--- {g} ---")
        for label, rows in (("positive", pg), ("negative", ng)):
            print(f"  {label:<9} bitscore  {describe([float(r['best_bitscore']) for r in rows])}")
            print(f"  {' ':<9} identity  {describe([float(r['best_pident']) for r in rows])}")
            print(f"  {' ':<9} qcov      {describe([100*float(r['qcov_frac']) for r in rows])}")

        pvals = sorted(float(r["best_bitscore"]) for r in pg)
        nvals = sorted(float(r["best_bitscore"]) for r in ng)
        if pvals and nvals:
            pmin, nmax = pvals[0], nvals[-1]
            if pmin > nmax:
                print(f"  ** CLEAN SEPARATION: lowest positive {pmin:.1f} > "
                      f"highest negative {nmax:.1f}")
            else:
                overlap = [v for v in nvals if v >= pmin]
                print(f"  ** OVERLAP: {len(overlap)}/{len(nvals)} negative hits "
                      f"score at or above the weakest positive ({pmin:.1f}); "
                      f"highest negative {nmax:.1f}")
                # A threshold that admits every positive is what matters: the
                # detection floor is set by the weakest true locus, so the cost
                # of full sensitivity is however many negatives sit above it.
                print(f"     at a threshold of {pmin:.1f} (100% sensitivity), "
                      f"{len(overlap)} of {neg_asm} negative genomes carry a "
                      f"{g} hit")
        elif pvals and not nvals:
            print(f"  ** CLEAN: no {g} hit in any negative genome at all")


def cluster_report(pos, neg, pos_asm, neg_asm):
    print("\n" + "=" * 78)
    print("CLUSTER-LEVEL RESULT (tiers are never summed)")
    print("=" * 78)
    for label, data, n in (("POSITIVE", pos, pos_asm), ("NEGATIVE", neg, neg_asm)):
        counts = defaultdict(set)
        for c in data["clusters"]:
            counts[int(c["tier"])].add(c["assembly"])
        print(f"\n{label} control ({n} genomes) - genomes whose BEST cluster is:")
        seen = set()
        for t in (1, 2, 3, 4):
            # Assign each genome to its best (lowest) tier only, so that the
            # rows are disjoint and cannot be added together by accident.
            g = counts[t] - seen
            seen |= counts[t]
            print(f"  tier {t}: {len(g):>3}/{n} ({100*len(g)/n:>5.1f}%)")
        print(f"  none : {n - len(seen):>3}/{n}")

    print("\nNote: a genome is counted once, at its best tier. Rows are disjoint\n"
          "by construction and must still never be summed across tiers.")


def four_gene_report(pos, neg, pos_asm, neg_asm):
    print("\n" + "=" * 78)
    print("ALL FOUR GENES PRESENT SOMEWHERE IN THE GENOME")
    print("=" * 78)
    print("(distinct from tier 1, which additionally requires a 100 kb window)")
    for label, data, n in (("positive", pos, pos_asm), ("negative", neg, neg_asm)):
        got = defaultdict(set)
        for l in data["loci"]:
            got[l["assembly"]].add(l["gene"])
        full = [a for a, gs in got.items() if len(gs & set(GENES)) == 4]
        print(f"  {label:<9} {len(full):>3}/{n} ({100*len(full)/n:>5.1f}%)")


def main():
    posd = sys.argv[1] if len(sys.argv) > 1 else "results/controls/positive"
    negd = sys.argv[2] if len(sys.argv) > 2 else "results/controls/negative"
    pos, neg = load(posd), load(negd)

    pos_asm = len(pos["per_assembly"])
    neg_asm = len(neg["per_assembly"])
    print(f"positive control: {pos_asm} genomes")
    print(f"negative control: {neg_asm} genomes")

    gene_report(pos, neg, pos_asm, neg_asm)
    four_gene_report(pos, neg, pos_asm, neg_asm)
    cluster_report(pos, neg, pos_asm, neg_asm)


if __name__ == "__main__":
    main()
