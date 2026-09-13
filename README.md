# Subagent orchestration research

[Español](README.es.md)

## Current version: 2.0 — SAGE-CREH

The study now includes a fifth architecture focused on selective subagent
coordination and skill distribution. See [extension/README.md](extension/README.md)
for the implementation, protocols and reproduction commands, and `paper-v2/`
for both updated language editions.

The new paired replication comprises 216 runs, 510 calls and 707,090 observed
tokens on the exact original twelve tasks. Separate development adds 20 runs,
28 calls and 32,351 tokens, excluded from replication means. All four original
architectures, the single agent and original skill-loading control were rerun;
SAGE, SAGE without delegation and SAGE with all ten skills were added.

SAGE reached 23/24 strict successes with 1,765 mean tokens and 7.34 mean seconds.
It used 30.2%–61.1% fewer tokens than the four original teams, but is not best
under every metric: normalized SQL yields 24/24 for sequential/reflexive and
23/24 for SAGE/single, while the single agent consumes less. The task set was
known during design, not a blind holdout. All attempts and failure cases are
retained. Three new arXiv references bring the corpus to twelve.

The version-1 scientific inputs, runtime and recorded outcomes remain unchanged.
This README's v2 introduction is an editorial update. The older `ARTIFACTS.sha256`
describes the historical v1 snapshot (including its original README), available
in the preserved v1 public ZIP, not the extended working tree. The v2 release
provides `ARTIFACTS-v2.sha256` covering the updated package.

## Historical version-1 documentation

An exploratory CREH Labs study of subagent coordination architectures. It compares four bounded multi-agent patterns, a single-agent baseline, and a skill-loading ablation using live `gpt-5.6-luna` responses with low reasoning effort. The literature corpus contains nine arXiv papers first submitted in 2026.

This folder contains an independent research harness and its recorded evidence. The benchmark has 12 distinct synthetic tasks, two repetitions and six conditions: 144 evaluation runs plus a separate six-run development pilot. It is not a SWE-bench, Terminal-Bench or production-autonomy result.

## Contents

- `benchmark/`: task generators, procedural skills, objective evaluators, role prompts and live runner.
- `protocol.en.md` / `protocol.es.md`: experimental settings frozen before evaluation, with documented editorial amendments.
- `results/pilot/`: development evidence, excluded from reported performance.
- `results/evaluation/`: ordered manifest, hashes, task definitions, per-call traces and run outcomes.
- `analysis/`: offline audit, aggregation, bootstrap, workbook and plot generation.
- `results/analysis/`: JSON/CSV/XLSX tables and figures after analysis.
- `sources.json`: source dates, versions, exact links and scope notes.
- `paper/es/` / `paper/en/`: complete editable LaTeX sources and compiled PDFs.

## Reproduce

Use Python 3.13 or a compatible version and install `requirements.txt` in an isolated environment. Run from this directory:

```bash
python3 -m unittest discover -s benchmark -v
python3 benchmark/runner.py --pilot --output results/new-pilot
python3 benchmark/runner.py --output results/new-evaluation
```

Supply your authorized key through `OPENAI_API_KEY`; alternatively pass `--env-file /path/to/authorized.env`. The runner reads only that key. API execution is billable. It never prints the credential or stores authorization headers. Output destinations must be new. The recorded model alias can change over time; a new run is a replication attempt, not a promise of identical answers or latency.

To regenerate the published analysis from its preserved evaluation:

```bash
python3 analysis/analyze.py
```

The analysis validates benchmark source hashes, documented protocol amendments, run order, complete blocks and per-call token totals. `editorial-amendments.json` records the original and current hashes of the two protocol documents after a framing-only edit; historical manifests remain unchanged. The results must be complete; it never silently drops an unfavorable run. New evaluation folders require changing only the analysis input path in a separate replication copy, preserving the original evidence.

Build each PDF with pdfLaTeX twice from its language directory, or use the CREH Labs `build_article.py` helper when installed. The source uses the original CREH Labs mark and style, A4 layout, bilingual bodies, and the exact required author footer. Generated figures require running the analysis first.

## Interpretation

The main performance metric is exact whole-task success. All model calls count, including supervision, criticism, repeated inputs and failed generations with reported usage. Cached input and reasoning are subsets already included in total tokens. Intervals use paired task-cluster bootstrap with both repetitions retained. Latency is elapsed run time, not the sum of overlapping request durations. Successes per minute describe accumulated serial-run efficiency, not loaded-server throughput.

Original benchmark material, data and paper are provided for public research review. Referenced papers remain their authors' work; their full text is not redistributed. Public traces contain synthetic inputs and visible answers, never private reasoning or personal conversation history. This preprint has not undergone peer review.
