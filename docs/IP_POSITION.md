# IP position — Task 0 patent strand

**Research triage, not legal advice and not a freedom-to-operate opinion.**
Produced from public sources for research planning. Espacenet, WIPO Patentscope
and the USPTO APIs were all inaccessible from this container, so there is no
verified live register status and no prosecution history here. Claim text is
from OCR of official published PDFs except where marked verified below. Obtain
a written opinion from a qualified patent attorney before any filing,
publication or commercial decision.

Search date: 2026-09-30.

## Headline: the brief's premise needs correcting

The project brief gates Branch B on **US 2025/0075191 A1 / WO 2025/049575 A1**,
described as "pending with mammalian and oncology claims recited".

That is not what those documents claim.

- **No mammalian cell is recited in any claim.** The claims say "transgenic
  organism capable of biosynthesizing 3-hydroxyhispidin", "a cell", "a cell or
  organism". Host-agnostic, and they would read on a mammalian cell — but the
  only dependent narrowing is to *plants* (cl. 7, 18). HEK293/HEK293T and cancer
  cells appear in the specification, not the claims.
- **No oncology or tumour-imaging claim exists** anywhere in this family.
- The claims are **narrow and sequence-anchored**: every independent requires
  either a literal SEQ ID, or >=90% identity to a named SEQ ID **plus** at least
  one enumerated substitution (Luz: T99P, T192S, A199P; H3H: D37E, V181I, A183P,
  S323M, M385K).

So the document the brief names as the gate is among the *less* threatening
items in the landscape. The actual exposure is elsewhere, in the same
assignee's portfolio.

## The item that matters: US 12,473,582 B2

**Verified directly from the official grant PDF** (front page and claim page
read in this session, not taken on trust from a summary):

| | |
|---|---|
| Number | US 12,473,582 B2 |
| Title | Method and agents for detecting luciferase activity |
| Assignee | **Light Bio, Inc.**, Mount Horeb, WI |
| Granted | **18 November 2025** — in force |
| Priority | RU 2015106305, **25 February 2015** |
| Chain | continuation of 16/773,304 (US 11,802,302) ← 15/553,411 (US 10,584,368), PCT/RU2016/000229 |
| Claims | 11; subject to a terminal disclaimer |

Claim 1, verbatim:

> **1.** A biological sample comprising at least one cell containing at least one
> of 3-hydroxyhispidin and 3-hydroxybisnoryangonin, wherein the biological
> sample is not obtained from a higher fungus.

Dependents: cl. 2 adds a fungal luciferase; cl. 3/4 set luciferin concentration
ranges (0.03-30 uM; 1-5 uM); cl. 6 the cell expresses hispidin-3-hydroxylase;
cl. 7/8 the cell is a plant cell; cl. 9 a method of producing the luciferin from
hispidin + NAD(P)H + H3H; cl. 11 a detection method.

**Why this is the load-bearing item.** It is a *composition* claim on a cell
containing the luciferin, carved out only for higher fungi. It is
**sequence-independent**: it does not matter which enzymes made the
3-hydroxyhispidin, nor whether they are natural, ancestral, thermotolerant or
engineered. No amount of sequence novelty designs around it. Any mammalian cell
in which this pathway is reconstituted is, on the face of the claim, within it.

That is precisely the Branch B objective. It is granted and in force, where the
documents the brief names are merely pending.

## The item that matters for Branch B's method: the L3 genus family

WO 2020/005120 / RU 2730038 C2 → US 2024/0117385 A1, EP 3816282 (both pending),
JP 7842813 B2 and AU 2019292668 B2 (granted). Planta LLC → Light Bio. Priority
2018-06-28. *Enzymes of luciferin biosynthesis and use thereof.*

Reported to claim hispidin synthases, hispidin hydroxylases and caffeylpyruvate
hydrolases by SEQ ID **plus identity-threshold genus language** — reportedly
**>=40% identity for hispidin synthases** and **>=60% over 350+ aa for the
hydroxylases and hydrolases** — extending to cells and to transgenic plant,
animal, bacterial and fungal organisms.

A >=40% floor on HispS is close to family-wide. Essentially any HispS orthologue
from any basidiomycete would clear it, and so would an ancestral reconstruction
at any node inside the fungal clade. **This lands directly on Branch B2
(naturally thermotolerant orthologues) and B3 (ASR).**

Two counterweights for the attorney, not for us to resolve:
- These thresholds are *as filed*. The US and EP members are still pending, and
  breadth of that kind is the first thing an examiner attacks on written
  description and enablement (*Amgen v. Sanofi*; EPC Art. 83/84). Granted claims
  may be far narrower.
- The **granted** JP and AU members already exist and their thresholds should be
  pulled, since they are settled where the US/EP are not.

## CN 116732084 A — the DeltaN20 truncation

Confirmed as the brief states, with detail the brief did not have:

- The enzyme is **Luz** (*N. nambi* nnLuz), not HispS/H3H/CPH.
- Applicant **Zhejiang University**; **assigned 2025-04-18 to Guangdong Sanjie
  Forage Biotechnology Co., Ltd.** Priority 2023-05-05. A-publication only, no
  grant found; no family outside China found.
- Claims are **Swiss-style use claims limited to fungi or plants**, with the gene
  integrated into the genome; dependents recite co-integration of HispS, CPH, H3H
  and **NPGA** at SEQ ID NO:3-6, and CRISPR/Cas9 delivery.
- Being limited to fungi and plants, **it would not reach mammalian-cell work.**

Note the truncation space is contested from two directions: the Light Bio claims
are framed on "positions 40-267" of their Luz SEQ ID NO:1, effectively a DeltaN39
construct, against this DeltaN20.

## Where our planned work lands

| Planned activity | Relevant claims | First-pass read |
|---|---|---|
| ASR of Luz | US 11,913,033 (>=95% to nnLuz); US 2025/0075191 cl. 11/19 (>=90% + P199) | Probably outside — ASR nodes normally fall well below 90-95% identity to any extant sequence. **Must be computed, not assumed**: pairwise identity against both SEQ IDs, and check the residue aligned to position 199. |
| **ASR of HispS / H3H / CPH** | **L3 genus claims** | **Highest risk.** An ASR node inside the fungal clade will almost certainly exceed >=40%/>=60%. |
| **Naturally thermotolerant HispS / H3H / CPH** | **L3 genus claims** | **Highest risk, same numbers.** |
| Thermotolerant Luz from Armillaria / Mycena / Omphalotus | US 11,913,033 (>=95%) | Likely outside the US claim; the granted CN/JP/KR/AU members may differ and must be pulled. |
| **Expressing the pathway in a mammalian cell at all** | **US 12,473,582 cl. 1** | **Sequence-proof exposure.** Not addressable by sequence choice. |
| Cognate PPTase co-expression (B1) | CN 116732084 only (China, fungi/plants) | **Low risk elsewhere.** Foundational Sfp/PPTase patents are long expired. |
| N-truncated Luz | US 2025/0075191 cl. 1/19; CN 116732084 | Contested from two directions; needs specific advice. |

Searched and **not** found, which is useful: no patent family claiming ancestral
sequence reconstruction applied to luciferases or polyketide synthases; no
fungal-pathway PPTase co-expression family outside the CN document; no oncology
claim set on the fungal pathway at all.

## Consequences for how this project runs

1. **Branch B's publication hold stands, and is now better justified.** Not
   because of the pending applications the brief named, but because of a granted,
   in-force, sequence-independent claim covering the end state Branch B aims at.
2. **B1 (cognate in-cluster PPTase) is the cleanest branch of the engineering
   work** on this evidence — it was already the highest-value question
   scientifically, and it is also the least encumbered.
3. **Branch A is unaffected.** Describing where the cluster occurs in nature is
   not an act any of these claims reach. Branch A's gate is the literature
   strand, not this one.
4. **The identity computation is now a required deliverable, not an optional
   one.** Every ASR output and every thermotolerant candidate must carry its
   percent identity to the relevant SEQ IDs so that the attorney has numbers
   rather than sequences to work from.

## For the attorney — priority order

1. Verify status and territorial reach of **US 12,473,582**; check for any
   EP/GB/CN/JP counterpart of that family. Assess validity of cl. 1 under
   §101/§112 and on anticipation.
2. Pull the **pending claims as currently amended** of US 2024/0117385 and
   EP 3816282, and the **granted** claims of JP 7842813 B2 and AU 2019292668 B2
   (L3). These thresholds decide whether B2 and B3 are viable.
3. Pull granted claims of CN 110234758 B, JP 7298907 B2, KR 102594240 B1,
   AU 2017395644 — the >=95% figure may not hold outside the US.
4. Confirm national-phase entries for WO 2025/049575 (30-month date ~2026-02-28,
   already past).
5. Confirm CN 116732084 status at CNIPA against the official Chinese text; §1
   above rests on machine translation.
6. Advise on **file-before-publish** sequencing, and on UK PA 1977 s.60(5)(b)
   experimental-use cover for the research-stage screening.
7. Run the searches this container could not: Espacenet, Patentscope, DWPI,
   CNIPA/KIPO native-language, INPADOC legal status, and **sequence-based (BLAST)
   patent searching against the GenBank patent division and EPO/WIPO sequence
   listings** — sequence searching is essential here and was not possible.

## Confidence

- **Verified in this session from the official PDF:** US 12,473,582 front-page
  bibliographic data and claims 1-11.
- **Agent OCR of official PDFs, not independently re-read:** US 2025/0075191 and
  WO 2025/049575 claim sets; US 11,802,302 and US 11,913,033 claim 1.
- **Secondary / machine translation, lowest confidence:** all L3 identity
  thresholds, the CN 116732084 claim wording, and every legal status line.
  The L3 thresholds drive the Branch B risk assessment and are the single most
  important thing to confirm from primary sources.
