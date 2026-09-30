#!/usr/bin/env bash
# Fetch genomic FASTA for every assembly in a manifest built by
# build_control_manifests.py.
#
# Downloads are kept gzipped: the sweep reads them through zcat, so there is no
# reason to pay ~3x the disk to store them expanded. The container has a fixed
# writable allowance and the full fungal set is ~281 GB gzipped, so the
# genome-scale sweep streams (fetch -> search -> delete) rather than
# accumulating. For the controls (5.1 Gbp) we can afford to keep them.
#
# Usage: scripts/fetch_assemblies.sh <manifest.tsv> <outdir> [parallel]
set -uo pipefail

MANIFEST="${1:?usage: fetch_assemblies.sh <manifest.tsv> <outdir> [parallel]}"
OUTDIR="${2:?usage: fetch_assemblies.sh <manifest.tsv> <outdir> [parallel]}"
PAR="${3:-4}"

mkdir -p "$OUTDIR"

# Column order is fixed by build_control_manifests.py FIELDS:
# 1 accession ... 10 ftp_path, 11 matched_species, 12 has_annotation
fetch_one() {
    local acc="$1" ftp="$2"
    local base out
    base="$(basename "$ftp")"
    out="$OUTDIR/${acc}.fna.gz"

    [[ -s "$out" ]] && { echo "SKIP  $acc (already present)"; return 0; }
    [[ -z "$ftp" || "$ftp" == "na" ]] && { echo "NOFTP $acc"; return 1; }

    # assembly_summary gives an ftp:// URL; the container reaches NCBI over
    # HTTPS through the agent proxy, so rewrite the scheme.
    local url="${ftp/ftp:\/\//https://}/${base}_genomic.fna.gz"

    for attempt in 1 2 3 4; do
        if curl -sSfL --retry 2 --max-time 900 -o "$out.part" "$url"; then
            mv "$out.part" "$out"
            echo "OK    $acc  $(du -h "$out" | cut -f1)"
            return 0
        fi
        rm -f "$out.part"
        sleep $((2 ** attempt))
    done
    echo "FAIL  $acc  $url"
    return 1
}
export -f fetch_one
export OUTDIR

tail -n +2 "$MANIFEST" \
  | awk -F'\t' '{print $1"\t"$10}' \
  | xargs -P "$PAR" -I{} bash -c 'IFS=$'"'"'\t'"'"' read -r acc ftp <<< "{}"; fetch_one "$acc" "$ftp"'

echo "--- summary ---"
echo "manifest rows : $(( $(wc -l < "$MANIFEST") - 1 ))"
echo "files present : $(ls -1 "$OUTDIR"/*.fna.gz 2>/dev/null | wc -l)"
echo "disk used     : $(du -sh "$OUTDIR" 2>/dev/null | cut -f1)"
