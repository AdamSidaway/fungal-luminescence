#!/usr/bin/env python3
"""
Build the tblastn query protein set from Kotlobay et al. 2018 SI Datasets S1-S4.

Why this script exists rather than a list of accessions
-------------------------------------------------------
The brief says to take accessions from the primary papers. There are none.
Kotlobay et al. 2018 (PNAS 115:12728) deposits genomes and transcriptomes under
BioProject PRJNA476325, but the four pathway enzymes themselves are distributed
ONLY as FASTA inside SI Datasets S1-S4, keyed by species name, with no GenBank
accession for any individual gene. The same is true of Shakhova et al. 2024
(Addgene plasmids + figshare) and of Palkina et al. 2023, whose Data Availability
statement reads "Not applicable".

So the query set is reconstructed from the SI files and checksummed here, since
there is no accession anyone can cite to check it.

The SI datasets are CODING NUCLEOTIDE, not protein, despite the headers naming
the enzyme. They are translated here.

Usage:
    python3 scripts/build_query_set.py <dir-with-sd01..sd04> data/refseqs
"""
import hashlib
import re
import sys
from pathlib import Path

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

# SI dataset -> gene symbol used throughout this project.
DATASETS = {
    "sd01": ("HispS", "hispidin synthase (PKS)"),
    "sd02": ("H3H", "hispidin-3-hydroxylase (FAD monooxygenase)"),
    "sd03": ("CPH", "caffeoyl-pyruvate hydrolase"),
    "sd04": ("Luz", "luciferase"),
}

# Facts stated in the text of Kotlobay et al. 2018, used as translation checks.
# nnLuz is reported as 267 aa / ~28.5 kDa.
EXPECTED = {("Luz", "Neonothopanus nambi"): 267}


def slug(s):
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")


def species_of(header):
    """'Luciferase from Neonothopanus nambi' -> 'Neonothopanus nambi'."""
    m = re.search(r"\bfrom\s+(.+)$", header)
    return m.group(1).strip() if m else header.strip()


def translate_cds(seq):
    """Translate a CDS, trimming a trailing partial codon and one stop codon.

    Returns (protein, notes). Notes record anything irregular so that a query
    with a problem is visible rather than silently used.
    """
    notes = []
    n = len(seq)
    if n % 3:
        notes.append(f"length {n} not a multiple of 3; trimmed {n % 3} nt")
        seq = seq[: n - (n % 3)]
    prot = str(Seq(seq).translate())
    if prot.endswith("*"):
        prot = prot[:-1]
    # A missing terminal stop is not flagged: every one of the 43 SI entries
    # lacks one, so it is the deposit convention of these datasets rather than
    # a defect in any individual sequence. Internal stops and a non-M start are
    # flagged, because those would mean a wrong frame or a partial CDS.
    if "*" in prot:
        notes.append(f"{prot.count('*')} INTERNAL stop codon(s)")
    if not prot.startswith("M"):
        notes.append("does not start with M")
    return prot, notes


def main():
    src = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    out = Path(sys.argv[2] if len(sys.argv) > 2 else "data/refseqs")
    out.mkdir(parents=True, exist_ok=True)

    all_prot, manifest, problems = [], [], []

    for tag, (gene, desc) in DATASETS.items():
        hits = list(src.glob(f"*{tag}*"))
        if not hits:
            print(f"!! missing dataset {tag} ({gene})")
            continue
        path = hits[0]
        prots = []
        for rec in SeqIO.parse(path, "fasta"):
            header = rec.description
            sp = species_of(header)
            prot, notes = translate_cds(str(rec.seq).upper())
            rid = f"{gene}|{slug(sp)}"
            # Disambiguate the paper's repeated species (e.g. P. stipticus #1-#3)
            existing = sum(1 for p in prots if p.id.startswith(rid))
            if existing:
                rid = f"{rid}_{existing + 1}"
            pr = SeqRecord(Seq(prot), id=rid, description=f"{desc} | {sp}")
            prots.append(pr)

            exp = EXPECTED.get((gene, sp))
            check = ""
            if exp is not None:
                ok = len(prot) == exp
                check = f"  [paper says {exp} aa: {'MATCH' if ok else 'MISMATCH'}]"
                if not ok:
                    problems.append(f"{rid}: expected {exp} aa, got {len(prot)}")
            if notes:
                problems.append(f"{rid}: " + "; ".join(notes))
            manifest.append((gene, sp, len(prot), "; ".join(notes) or "-"))
            print(f"  {rid:<52} {len(prot):>5} aa{check}"
                  + (f"   <- {'; '.join(notes)}" if notes else ""))

        SeqIO.write(prots, out / f"{gene}.faa", "fasta")
        all_prot.extend(prots)
        print(f"== {gene}: {len(prots)} sequences -> {out / f'{gene}.faa'}\n")

    SeqIO.write(all_prot, out / "query_all.faa", "fasta")

    combined = (out / "query_all.faa").read_bytes()
    digest = hashlib.sha256(combined).hexdigest()

    with open(out / "PROVENANCE.md", "w") as fh:
        fh.write(
            "# Query set provenance\n\n"
            "Source: Kotlobay et al. 2018, PNAS 115(50):12728, "
            "doi:10.1073/pnas.1803615115, SI Datasets S1-S4.\n\n"
            "**There are no GenBank accessions for these four enzymes.** The paper\n"
            "deposits genomes and transcriptomes under BioProject PRJNA476325, but the\n"
            "individual pathway genes appear only as FASTA in the SI, keyed by species\n"
            "name. Shakhova et al. 2024 likewise gives Addgene plasmids and a figshare\n"
            "DOI rather than sequence accessions, and Palkina et al. 2023 states\n"
            "'Not applicable' for data availability. The query set therefore cannot be\n"
            "cited by accession and is checksummed instead.\n\n"
            "The SI datasets are coding nucleotide, not protein, and are translated here.\n\n"
            f"`query_all.faa` SHA-256: `{digest}`\n\n"
            f"| gene | species | length (aa) | notes |\n|---|---|---|---|\n"
        )
        for gene, sp, ln, nt in manifest:
            fh.write(f"| {gene} | {sp} | {ln} | {nt} |\n")

    print(f"TOTAL {len(all_prot)} query proteins -> {out / 'query_all.faa'}")
    print(f"sha256 {digest}")
    if problems:
        print("\n!! ISSUES REQUIRING ATTENTION:")
        for p in problems:
            print("   " + p)
    else:
        print("\nno translation issues")


if __name__ == "__main__":
    main()
