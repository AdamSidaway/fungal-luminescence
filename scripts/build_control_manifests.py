#!/usr/bin/env python3
"""
Build the positive and negative control genome manifests (Task 2).

Positives: assemblies of species with published, recorded bioluminescence.
           Every one of these should return a complete hispidin cluster.
           This measures the detection floor (sensitivity).

Negatives: Ascomycete assemblies, where the cluster should be absent.
           Anything returned here is the false-positive rate measured in a
           genome that has none. A positives-only control cannot measure this.

Both manifests must be built and both sweeps run BEFORE any discovery number
is read. Usage:
    python3 scripts/build_control_manifests.py data/assembly_summary_fungi.tsv
"""
import csv
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Species with recorded bioluminescence. Restricted to names for which
# luminescence is reported in the primary literature, not whole genera:
# Armillaria and Mycena both contain non-luminous members, so listing the
# genus would contaminate the positive control and inflate the detection floor.
# Sources: Desjardin et al. 2008 Photochem Photobiol Sci 7:170 (survey of
# luminous fungi); Kotlobay et al. 2018 PNAS 115:12728; Ke & Tsai 2022.
# ---------------------------------------------------------------------------
LUMINOUS_SPECIES = [
    # Omphalotaceae / Marasmiaceae
    "Neonothopanus nambi",
    "Neonothopanus gardneri",
    "Omphalotus olearius",
    "Omphalotus nidiformis",
    "Omphalotus japonicus",
    "Omphalotus illudens",
    # Physalacriaceae (Armillaria clade) - luminous members
    "Armillaria mellea",
    "Armillaria gallica",
    "Armillaria ostoyae",
    "Armillaria borealis",
    "Armillaria cepistipes",
    "Armillaria solidipes",
    "Armillaria novae-zelandiae",
    "Guyanagaster necrorhizus",
    # Mycenaceae - luminous members
    "Mycena chlorophos",
    "Mycena lux-coeli",
    "Mycena luxaeterna",
    "Mycena haematopus",
    "Mycena sanguinolenta",
    "Mycena citricolor",
    "Mycena polygramma",
    "Panellus stipticus",
    "Panellus pusillus",
    "Roridomyces roridus",
    "Filoboletus manipularis",
]

# ---------------------------------------------------------------------------
# Negative control: Ascomycota. Well-assembled, well-studied, phylogenetically
# spread across the phylum. The hispidin bioluminescence cluster is a
# Basidiomycete (Agaricales) trait and should be wholly absent here.
#
# NOTE: Aspergillus nidulans is deliberately included. It is the source of
# NpgA, the phosphopantetheinyl transferase Kotlobay used to activate HispS.
# It therefore CARRIES a PPTase but must carry NO hispidin cluster - which
# makes it a useful specificity check for Branch B1 as well as a negative here.
# ---------------------------------------------------------------------------
NEGATIVE_SPECIES = [
    "Saccharomyces cerevisiae",
    "Schizosaccharomyces pombe",
    "Candida albicans",
    "Aspergillus nidulans",
    "Aspergillus fumigatus",
    "Aspergillus niger",
    "Aspergillus oryzae",
    "Neurospora crassa",
    "Fusarium graminearum",
    "Fusarium oxysporum",
    # Magnaporthe oryzae was renamed; NCBI carries it under Pyricularia.
    "Pyricularia oryzae",
    "Botrytis cinerea",
    "Sclerotinia sclerotiorum",
    "Trichoderma reesei",
    "Penicillium chrysogenum",
    "Penicillium rubens",
    "Colletotrichum graminicola",
    "Verticillium dahliae",
    "Zymoseptoria tritici",
    "Chaetomium globosum",
    "Podospora anserina",
    "Thermothelomyces thermophilus",
    "Thermoascus aurantiacus",
    "Talaromyces marneffei",
    "Histoplasma capsulatum",
    "Coccidioides immitis",
    "Blastomyces dermatitidis",
    "Trichophyton rubrum",
    "Pneumocystis jirovecii",
    "Yarrowia lipolytica",
]

FIELDS = [
    "assembly_accession", "organism_name", "infraspecific_name",
    "assembly_level", "genome_size", "scaffold_count", "contig_count",
    "total_gene_count", "annotation_provider", "ftp_path",
]


def load_latest(summary_path):
    """Read assembly_summary.txt, keeping only version_status == 'latest'."""
    rows = []
    with open(summary_path) as fh:
        header = None
        for line in fh:
            if line.startswith("##"):
                continue
            if line.startswith("#"):
                header = line.lstrip("#").rstrip("\n").split("\t")
                continue
            if header is None:
                continue
            vals = line.rstrip("\n").split("\t")
            if len(vals) != len(header):
                continue
            rec = dict(zip(header, vals))
            if rec.get("version_status") == "latest":
                rows.append(rec)
    return rows


def drop_non_genomes(rows, label):
    keep = [r for r in rows if is_genome(r)]
    dropped = [r for r in rows if not is_genome(r)]
    if dropped:
        print(f"  {label}: dropped {len(dropped)} entr(ies) below "
              f"{MIN_GENOME_BP/1e6:.0f} Mbp as not-a-genome:")
        for r in dropped:
            gs = r.get("genome_size", "?")
            gs = f"{int(gs)/1e6:.2f} Mbp" if gs.isdigit() else gs
            print(f"    {r.get('assembly_accession', r.get('#assembly_accession', '?'))}  {r['organism_name']}  {gs}")
    return keep


def match(rows, species_list):
    """Match assemblies whose organism_name starts with a listed binomial.

    Prefix match (not exact) so that strain/subspecies suffixes are kept,
    e.g. 'Armillaria mellea DSM 3731' matches 'Armillaria mellea'.
    """
    out, found = [], {}
    for rec in rows:
        org = rec.get("organism_name", "")
        for sp in species_list:
            if org == sp or org.startswith(sp + " "):
                rec = dict(rec)
                rec["_matched_species"] = sp
                out.append(rec)
                found.setdefault(sp, 0)
                found[sp] += 1
                break
    return out, found


LEVEL_RANK = {
    "Complete Genome": 0, "Chromosome": 1, "Scaffold": 2, "Contig": 3,
}


def cap_per_species(rows, n):
    """Keep at most n assemblies per matched species.

    Needed for the negative control: species like Saccharomyces cerevisiae and
    Candida albicans carry thousands of near-identical strain assemblies, which
    would make the measured false-positive rate a statement about how many
    times one genome was resequenced rather than about the Ascomycota. Ranking
    prefers the most contiguous assembly, then an annotated one, then the
    least fragmented.
    """
    by_sp = {}
    for r in rows:
        by_sp.setdefault(r["_matched_species"], []).append(r)

    def key(r):
        contigs = r.get("contig_count", "")
        return (
            LEVEL_RANK.get(r.get("assembly_level", ""), 9),
            0 if annotated(r) else 1,
            int(contigs) if contigs.isdigit() else 10**9,
        )

    out = []
    for sp in sorted(by_sp):
        out.extend(sorted(by_sp[sp], key=key)[:n])
    return out


# Minimum assembly size to count as a genome. Fungal genomes run from ~8 Mbp
# (microsporidia) to >200 Mbp (some Mycena); Agaricales sit at 30-150 Mbp.
# NCBI carries entries under a species name that are not genomes at all: the
# positive control initially pulled in GCA_055690705.1, filed as
# "Omphalotus olearius" but consisting of 426 contigs totalling 221 kb with a
# mean length of 520 bp - a marker or amplicon set, 0.8% of a real genome.
# It returned zero hits, and left in place would have been recorded as a
# detection failure, degrading the measured detection floor for a reason that
# has nothing to do with detection. Sensitivity must be measured on genomes.
MIN_GENOME_BP = 5_000_000

# Assemblies quarantined out of the POSITIVE control, with the reason.
#
# Luminescence is not always a property of a species. Panellus stipticus is the
# classic case: it carries both luminescent and non-luminescent lineages, and
# Rabara & Xie 2025 (J Fungi 11:774) report the cluster absent from a
# non-luminous strain whose genome is otherwise near-identically syntenic with
# the luminous one. A positive control assembled from species names therefore
# cannot be assumed to consist of luminous specimens.
#
# The two entries below are two assemblies of a SINGLE Sanger BioSample
# (SAMEA9873913), so they are not independent observations either. In the
# control sweep both returned HispS, H3H and Luz at or below the identity
# ceiling measured in Ascomycete genomes that carry no pathway at all
# (Luz 28.3% against a 37.5% Ascomycete ceiling and a 73.2% floor among true
# positives). They do not carry the cluster. Left in the positive control they
# would be scored as a three-gene detection failure and would put the measured
# detection floor at 28.3% identity for Luz, which is a statement about a
# specimen that has no Luz rather than about the sensitivity of the search.
QUARANTINE_POSITIVE = {
    "GCA_965154615.1": "P. stipticus, Sanger SAMEA9873913; no cluster detected "
                       "(Luz 28.3% id, below Ascomycete ceiling); likely the "
                       "non-luminous lineage; same BioSample as GCA_965154625.1",
    "GCA_965154625.1": "P. stipticus, Sanger SAMEA9873913; no cluster detected "
                       "(Luz 28.7% id, below Ascomycete ceiling); likely the "
                       "non-luminous lineage; same BioSample as GCA_965154615.1",
}


def is_genome(rec):
    gs = rec.get("genome_size", "")
    return gs.isdigit() and int(gs) >= MIN_GENOME_BP


def annotated(rec):
    g = rec.get("total_gene_count", "")
    return bool(g) and g != "na" and g.isdigit() and int(g) > 0


def write_manifest(rows, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(FIELDS + ["matched_species", "has_annotation"])
        for r in rows:
            w.writerow(
                [r.get(f, "") for f in FIELDS]
                + [r["_matched_species"], "yes" if annotated(r) else "no"]
            )


def report(label, rows, found, species_list):
    ann = sum(1 for r in rows if annotated(r))
    bases = sum(int(r["genome_size"]) for r in rows if r.get("genome_size", "").isdigit())
    print(f"\n=== {label} ===")
    print(f"  assemblies matched : {len(rows)}")
    print(f"    annotated        : {ann}")
    print(f"    unannotated      : {len(rows) - ann}")
    print(f"  total sequence     : {bases / 1e9:.2f} Gbp")
    missing = [s for s in species_list if s not in found]
    print(f"  species represented: {len(found)}/{len(species_list)}")
    if missing:
        print("  NO ASSEMBLY for    : " + "; ".join(missing))


def main():
    summary = sys.argv[1] if len(sys.argv) > 1 else "data/assembly_summary_fungi.tsv"
    rows = load_latest(summary)
    print(f"latest fungal assemblies parsed: {len(rows)}")

    pos, pos_found = match(rows, LUMINOUS_SPECIES)
    neg_all, neg_found = match(rows, NEGATIVE_SPECIES)

    print("\nsize filter:")
    pos = drop_non_genomes(pos, "positive")

    quar = [r for r in pos if r.get("assembly_accession") in QUARANTINE_POSITIVE]
    pos = [r for r in pos if r.get("assembly_accession") not in QUARANTINE_POSITIVE]
    if quar:
        print("\nquarantined from the positive control:")
        for r in quar:
            print(f"  {r['assembly_accession']}  {r['organism_name']}")
            print(f"    reason: {QUARANTINE_POSITIVE[r['assembly_accession']]}")
        write_manifest(quar, "data/manifest_control_quarantined.tsv")
        print("  -> data/manifest_control_quarantined.tsv (kept, not deleted:"
              " these are a Branch A observation in their own right)")
    neg_all = drop_non_genomes(neg_all, "negative")

    # Positives are kept in full: there are few of them and every one is a
    # separate chance to miss a cluster, which is exactly what the detection
    # floor is measuring. Negatives are capped per species (see cap_per_species).
    neg = cap_per_species(neg_all, 3)
    print(f"negative control capped: {len(neg_all)} -> {len(neg)} assemblies (<=3/species)")

    write_manifest(pos, "data/manifest_control_positive.tsv")
    write_manifest(neg, "data/manifest_control_negative.tsv")

    report("POSITIVE CONTROL (recorded luminous)", pos, pos_found, LUMINOUS_SPECIES)
    report("NEGATIVE CONTROL (Ascomycota)", neg, neg_found, NEGATIVE_SPECIES)

    print("\nmanifests written to data/manifest_control_{positive,negative}.tsv")


if __name__ == "__main__":
    main()
