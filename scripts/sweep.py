#!/usr/bin/env python3
"""
Six-frame tblastn sweep of the hispidin bioluminescence cluster.

Stage 1 of the mining run. For each assembly in a manifest:
  1. build a throwaway nucleotide BLAST DB (2.5x faster than tblastn -subject,
     which is single-threaded; verified identical hit sets - see docs/SCOPE.md)
  2. tblastn the 43 query proteins against it
  3. merge HSPs into loci, one locus per (gene, contig, strand) neighbourhood
  4. group loci into clusters within a 100 kb window and assign a tier

Run PERMISSIVELY. The e-value cut here is deliberately loose: the negative
control is what sets the working threshold, and a threshold chosen before the
controls are read would make the false-positive floor unmeasurable. Every HSP is
recorded with bitscore and identity so the cut can be made from data afterwards.

Usage:
    python3 scripts/sweep.py <manifest.tsv> <assembly-dir> <out-dir> [--evalue 1e-3]
"""
import argparse
import csv
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

# Maximum genomic span of a single gene, used to decide whether two HSPs of the
# same query gene belong to one locus. Fungal genes are spliced and these are
# generous: HispS is a ~1,700 aa PKS whose genomic span with introns can exceed
# 8 kb, while Luz is ~270 aa. Set per gene rather than globally so that a long
# PKS does not force a span wide enough to merge genuinely separate small genes.
MAX_GENE_SPAN = {"HispS": 20000, "H3H": 8000, "CPH": 8000, "Luz": 6000}
DEFAULT_SPAN = 10000

# Tier 1 requires all four genes inside this window.
CLUSTER_WINDOW = 100000

GENES = ["HispS", "H3H", "Luz", "CPH"]

BLAST_FIELDS = [
    "qseqid", "sseqid", "pident", "length", "mismatch", "gapopen",
    "qstart", "qend", "sstart", "send", "evalue", "bitscore", "qlen", "slen",
]


def run_tblastn(genome_gz, query, threads, evalue, tmpdir):
    """Decompress, build a DB, tblastn, return parsed HSP dicts."""
    fna = Path(tmpdir) / "g.fna"
    with open(fna, "wb") as out:
        subprocess.run(["zcat", str(genome_gz)], stdout=out, check=True)

    db = Path(tmpdir) / "gdb"
    subprocess.run(
        ["makeblastdb", "-in", str(fna), "-dbtype", "nucl", "-out", str(db)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    proc = subprocess.run(
        ["tblastn", "-query", str(query), "-db", str(db),
         "-num_threads", str(threads), "-evalue", str(evalue),
         "-outfmt", "6 " + " ".join(BLAST_FIELDS),
         "-max_target_seqs", "10000", "-seg", "no"],
        check=True, capture_output=True, text=True,
    )

    hsps = []
    for line in proc.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) != len(BLAST_FIELDS):
            continue
        h = dict(zip(BLAST_FIELDS, parts))
        for k in ("pident", "evalue", "bitscore"):
            h[k] = float(h[k])
        for k in ("length", "qstart", "qend", "sstart", "send", "qlen", "slen"):
            h[k] = int(h[k])
        # tblastn reports sstart > send on the minus strand; normalise and keep
        # the strand explicitly so downstream merging is orientation-aware.
        h["strand"] = "+" if h["sstart"] <= h["send"] else "-"
        h["lo"], h["hi"] = sorted((h["sstart"], h["send"]))
        h["gene"] = h["qseqid"].split("|", 1)[0]
        hsps.append(h)
    return hsps, fna


def merge_loci(hsps):
    """Merge HSPs of the same gene on the same contig and strand into loci.

    A spliced gene produces several HSPs, one per exon block, so the raw HSP
    count is not a gene count. Merging is what turns alignment fragments into
    candidate gene calls.
    """
    by_key = defaultdict(list)
    for h in hsps:
        by_key[(h["gene"], h["sseqid"], h["strand"])].append(h)

    loci = []
    for (gene, contig, strand), group in by_key.items():
        group.sort(key=lambda x: x["lo"])
        span = MAX_GENE_SPAN.get(gene, DEFAULT_SPAN)
        cur = [group[0]]
        for h in group[1:]:
            if h["lo"] - cur[-1]["hi"] <= span:
                cur.append(h)
            else:
                loci.append(_locus(gene, contig, strand, cur))
                cur = [h]
        loci.append(_locus(gene, contig, strand, cur))
    return loci


def _locus(gene, contig, strand, group):
    best = max(group, key=lambda x: x["bitscore"])
    # Query coverage is computed over the union of query intervals, so that
    # overlapping HSPs are not double counted and a locus cannot appear to
    # cover more of the query than it does.
    ivs = sorted((h["qstart"], h["qend"]) for h in group)
    merged, cov = [], 0
    for s, e in ivs:
        if merged and s <= merged[-1][1] + 1:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    for s, e in merged:
        cov += e - s + 1
    return {
        "gene": gene, "contig": contig, "strand": strand,
        "start": min(h["lo"] for h in group),
        "end": max(h["hi"] for h in group),
        "n_hsp": len(group),
        "best_bitscore": best["bitscore"],
        "best_evalue": best["evalue"],
        "best_pident": best["pident"],
        "best_query": best["qseqid"],
        "qlen": best["qlen"],
        "qcov_aa": cov,
        "qcov_frac": round(cov / best["qlen"], 4),
        "sum_bitscore": round(sum(h["bitscore"] for h in group), 1),
    }


def cluster_loci(loci, window=CLUSTER_WINDOW):
    """Group loci on the same contig into clusters within `window` bp.

    Strand is deliberately ignored here: the four genes are not required to be
    co-oriented, and Ke 2020 reports cph sitting outside the cluster entirely in
    several Mycena, so an orientation requirement would discard real signal.
    """
    by_contig = defaultdict(list)
    for l in loci:
        by_contig[l["contig"]].append(l)

    clusters = []
    for contig, group in by_contig.items():
        group.sort(key=lambda x: x["start"])
        cur = [group[0]]
        for l in group[1:]:
            if l["start"] - max(x["end"] for x in cur) <= window:
                cur.append(l)
            else:
                clusters.append(cur)
                cur = [l]
        clusters.append(cur)
    return clusters


def tier_of(cluster):
    """Assign a tier on cluster completeness, per the project rules.

    ORF integrity is not known at this stage - it needs the exonerate pass - so
    tiers 1 and 2 are reported here as provisional on ORF status and are
    finalised downstream. Tiers are never summed.
    """
    genes = {l["gene"] for l in cluster}
    n = len(genes)
    if n == 4:
        return 1, "all four genes in window (ORF integrity pending)"
    if n == 3:
        return 2, "three of four in window"
    if n == 2:
        return 3, "two of four in window"
    # A single gene. Luz is the most diagnostic of the four; H3H and CPH have
    # non-luminescent relatives, so a lone hit to either means nothing.
    g = next(iter(genes))
    return 4, f"single gene only ({g})"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("assembly_dir")
    ap.add_argument("out_dir")
    ap.add_argument("--query", default="data/refseqs/query_all.faa")
    ap.add_argument("--evalue", default="1e-3",
                    help="permissive by design; controls set the working cut")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    adir = Path(args.assembly_dir)

    rows = list(csv.DictReader(open(args.manifest), delimiter="\t"))
    if args.limit:
        rows = rows[: args.limit]

    hsp_fh = open(out / "hits_raw.tsv", "w", newline="")
    hsp_w = csv.writer(hsp_fh, delimiter="\t")
    hsp_w.writerow(["assembly", "species"] + BLAST_FIELDS + ["strand", "gene"])

    loc_fh = open(out / "loci.tsv", "w", newline="")
    loc_w = csv.writer(loc_fh, delimiter="\t")
    LOCF = ["gene", "contig", "strand", "start", "end", "n_hsp", "best_bitscore",
            "best_evalue", "best_pident", "best_query", "qlen", "qcov_aa",
            "qcov_frac", "sum_bitscore"]
    loc_w.writerow(["assembly", "species", "has_annotation"] + LOCF)

    cl_fh = open(out / "clusters.tsv", "w", newline="")
    cl_w = csv.writer(cl_fh, delimiter="\t")
    cl_w.writerow(["assembly", "species", "has_annotation", "contig", "start",
                   "end", "span_bp", "n_genes", "genes", "tier", "tier_reason",
                   "max_bitscore"])

    summary = []
    for i, r in enumerate(rows, 1):
        acc = r["assembly_accession"]
        sp = r.get("matched_species", r.get("organism_name", ""))
        ann = r.get("has_annotation", "")
        gz = adir / f"{acc}.fna.gz"
        if not gz.exists():
            print(f"[{i}/{len(rows)}] {acc} MISSING FILE", flush=True)
            summary.append((acc, sp, ann, 0, 0, 0, ""))
            continue

        with tempfile.TemporaryDirectory() as td:
            try:
                hsps, _ = run_tblastn(gz, args.query, args.threads, args.evalue, td)
            except subprocess.CalledProcessError as e:
                print(f"[{i}/{len(rows)}] {acc} BLAST FAILED: {e}", flush=True)
                continue

        for h in hsps:
            hsp_w.writerow([acc, sp] + [h[f] for f in BLAST_FIELDS]
                           + [h["strand"], h["gene"]])

        loci = merge_loci(hsps)
        for l in loci:
            loc_w.writerow([acc, sp, ann] + [l[f] for f in LOCF])

        clusters = cluster_loci(loci)
        best_tier, tiers_here = 5, []
        for c in clusters:
            tier, reason = tier_of(c)
            genes = sorted({l["gene"] for l in c}, key=lambda g: GENES.index(g))
            lo, hi = min(l["start"] for l in c), max(l["end"] for l in c)
            cl_w.writerow([acc, sp, ann, c[0]["contig"], lo, hi, hi - lo,
                           len(genes), ",".join(genes), tier, reason,
                           max(l["best_bitscore"] for l in c)])
            best_tier = min(best_tier, tier)
            tiers_here.append(tier)

        genes_found = sorted({l["gene"] for l in loci}, key=lambda g: GENES.index(g))
        summary.append((acc, sp, ann, len(hsps), len(loci), len(clusters),
                        ",".join(genes_found), best_tier))
        print(f"[{i}/{len(rows)}] {acc:<18} {sp:<32} "
              f"hsp={len(hsps):<5} loci={len(loci):<3} clust={len(clusters):<3} "
              f"genes={','.join(genes_found) or '-':<20} best_tier="
              f"{best_tier if best_tier < 5 else '-'}", flush=True)

        hsp_fh.flush(); loc_fh.flush(); cl_fh.flush()

    hsp_fh.close(); loc_fh.close(); cl_fh.close()

    with open(out / "per_assembly.tsv", "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["assembly", "species", "has_annotation", "n_hsp", "n_loci",
                    "n_clusters", "genes_found", "best_tier"])
        for s in summary:
            w.writerow(list(s) if len(s) == 8 else list(s) + [""])

    print(f"\nwrote {out}/hits_raw.tsv, loci.tsv, clusters.tsv, per_assembly.tsv")


if __name__ == "__main__":
    main()
