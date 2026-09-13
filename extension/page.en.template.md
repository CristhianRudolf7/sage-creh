---
title: "SAGE-CREH: adaptive subagent coordination and skills"
description: "A fifth architecture, the same twelve tasks and 216 new runs: comparing completion, tokens, time and skill distribution with code and data."
date: 2026-09-13
updated: 2026-09-13
tags:
  - "agents"
  - "subagents"
  - "benchmarks"
  - "skills"
draft: false
bilingual: true
kind: preprint
version: "2.0"
authors:
  - "Cristhian Egoavil"
pdf: "/investigacion/documentos/subagentes-arquitecturas-tokens-tiempo-2026-v2-en.pdf"
---

## How should subagents be organized?

This research compares **coordination architectures and skill distribution**, not different models. Who solves? Who checks? When does delegation add value? Which instructions does each worker actually need?

The previous version studied four patterns: sequential, parallel, hierarchical and reflexive. This update adds a fifth architecture implemented at CREH Labs, **SAGE-CREH**, and reruns the original controls on the same tasks with the same model. The article expands its review from nine to twelve arXiv papers.

@@CONCLUSION@@

## The fifth architecture: SAGE-CREH

SAGE-CREH combines skill selection with conditional delegation. A deterministic coordinator recognizes public task structure, loads relevant instructions and selects one of two paths:

1. **Direct path:** one solver proposes an answer. If it satisfies the output contract and reports no specific unresolved issues, execution ends. Otherwise a verifier reviews the proposal.
2. **Subagent path:** for predefined structural complexity, two independent solvers work concurrently. One solves the full problem; the other pays particular attention to constraints, dependencies and tie breakers. Matching valid candidates without unresolved issues avoid an integrator; disagreement triggers an adjudicator.

The policy activates two solvers for graphs with at least eight nodes and any node with two or more predecessors, and for selection with at least ten items, forbidden pairs and prerequisites. These rules were fixed before replication. **The gate validates format; it does not know the correct answer.** Agreement does not guarantee that both agents are right.

The adjudicator receives original data and proposals, never evaluator feedback. There is no access to reference answers, SQL execution against hidden databases, or retry-until-correct loop. The name identifies this local composition; it does not claim to invent adaptive routing.

## Five architectures, side by side

| Architecture | Implemented organization | Calls per task |
| --- | --- | ---: |
| Sequential | Extraction, solving and integration, one stage after another. | 3 |
| Parallel | Two simultaneous complementary specialists and a fixed integrator. | 3 |
| Hierarchical | Supervisor plans one or two assignments, workers execute, results are integrated. | 3–4 |
| Reflexive | Proposal, critique and revision upon objections; at most two rounds. | 2–5 |
| SAGE-CREH | Direct path or two independent solvers; adjudication only when triggered. | 1–3 |

A one-call single-agent reference is also retained. All use the same model; changing a role does not change its weights. SAGE's parallel path introduces selective redundancy, whereas the original parallel pattern uses a fixed complementary division of responsibilities.

## How skills are distributed

The catalog retains ten skills: six relevant to the problems and four distractors. SAGE identifies the interface from public task fields and supplies only the relevant instruction body. It does not resend the full description catalog on each call.

| Task family | Skill responsibility |
| --- | --- |
| Ledger | Revisions, status and monetary sums. |
| Calendar | Time zones and common availability. |
| Dependencies | Precedence, earliest starts and critical path. |
| Selection | Budget, coverage, incompatibilities and tie breakers. |
| Memory | Confirmations, deletions, scopes and inheritance. |
| SQL | Read-only queries, aggregation and edge cases. |

Agents on the same task can receive the same skill while taking different roles. All retain the complete public input. This evaluates a closed-world interface adapter, **not semantic skill retrieval for open-ended conversations**.

## Benchmark: same task, model and evaluator

@@METRICS@@

The twelve original tasks are repeated twice in nine conditions: four architectures, a single agent, SAGE and three ablation controls. Each condition has 24 runs. Ten problems use exact-match grading; each of the two SQL queries is tested against three databases hidden from agents.

GPT-5.6 Luna uses low reasoning effort and at most 1,536 output tokens per call, including reasoning. Controls retain their original prompts. Order is randomized by task and repetition, with one condition at a time and at most two simultaneous within-flow calls. The [model identifier and configuration](https://developers.openai.com/api/docs/models/gpt-5.6-luna) are preserved.

## Replication results

@@MAIN_TABLE@@

Tokens and seconds are per-task means; calls are condition totals. Time includes network and coordination, excluding the evaluator. Tokens sum every input and output: cache and reasoning are already included, never added twice.

![Five architectures and the single-agent reference: completion, tokens and time, with exploratory intervals.](/investigacion/datos/subagentes-arquitecturas-tokens-tiempo-2026-v2/comparison-en.png)

The strict column requires the original JSON envelope. Secondary **SQL norm.** only wraps a raw SQL string into the requested nested field and applies the same evaluator: it changes no query and repairs no solution. This sensitivity was identified in v1 and predefined as a secondary metric for v2. Better formatting must not be mistaken for better reasoning.

Paper intervals use 10,000 paired task-cluster draws, retaining both repetitions. There are twelve distinct tasks, not 216 independent problems. Intervals are exploratory, and ceilings do not establish perfect reliability.

## Is the difference coordination or instruction loading?

@@ABLATION_TABLE@@

**SAGE without delegation** uses the same proposer and instruction payload, but never calls another agent. **SAGE with ten skills** keeps the policy while supplying every instruction body. The original hierarchy pair also measures that loading cost.

Against the original patterns, SAGE changes topology, prompts and catalog exposure. These ablations help distinguish effects; attributing every difference exclusively to coordination would be incorrect.

@@ROUTING@@

## Development and policy selection

@@DEVELOPMENT@@

Every attempt is retained. Selection was recorded before replication, and the architecture remained frozen throughout the 216 runs. Offline tests validate contracts, routes and accounting; their outcomes are not counted as model successes.

The success separating candidates occurred on DEV22, a calendar task where both used the same direct path without review. That variation does not demonstrate a causal effect of parallelism; selection is retained under the prior rule.

## How the literature informed the design

Progressive instruction loading and the separation between skills and workers motivate context controls. The extension incorporates selective delegation from [Uno-Orchestra](https://arxiv.org/html/2605.05007v1), progress-conditioned decisions from [ProgRouter](https://arxiv.org/html/2608.25992v1), and continuation review from [TROVE](https://arxiv.org/html/2609.05019v1). These are conceptual foundations: their training is not reproduced and their scores are not presented as our results.

## Scope and materials

This is an exploratory preprint without peer review. Final tasks **were already known during design**: this is a development-informed paired replication, not a blind generalization test. It evaluates one model, short contexts and synthetic tasks, without terminal use, browsing, multi-file programming, persistent memory or RAM measurement.

Practical selection should consider completion, tokens and waiting time together. Traces show when a revision corrected something and when it only added cost. Both waves are retained separately; historical latency is not pooled with new measurements.

- [Full v2 paper in English](/investigacion/documentos/subagentes-arquitecturas-tokens-tiempo-2026-v2-en.pdf).
- [Paper v2 completo en español](/investigacion/documentos/subagentes-arquitecturas-tokens-tiempo-2026-v2-es.pdf).
- [Code, LaTeX sources, protocols and every trace](/investigacion/datos/subagentes-arquitecturas-tokens-tiempo-2026-v2/source-and-data.zip).
- [Workbook with all nine conditions](/investigacion/datos/subagentes-arquitecturas-tokens-tiempo-2026-v2/benchmark-data.xlsx).
- [Summary CSV](/investigacion/datos/subagentes-arquitecturas-tokens-tiempo-2026-v2/summary.csv), [per-run CSV](/investigacion/datos/subagentes-arquitecturas-tokens-tiempo-2026-v2/runs.csv) and [paired comparisons](/investigacion/datos/subagentes-arquitecturas-tokens-tiempo-2026-v2/paired-comparisons.csv).
- [Routes and corrections](/investigacion/datos/subagentes-arquitecturas-tokens-tiempo-2026-v2/routing.csv), [SQL sensitivity](/investigacion/datos/subagentes-arquitecturas-tokens-tiempo-2026-v2/format-sensitivity.csv) and [hashes](/investigacion/datos/subagentes-arquitecturas-tokens-tiempo-2026-v2/SHA256SUMS.txt).
- [Historical v1 paper in English](/investigacion/documentos/subagentes-arquitecturas-tokens-tiempo-2026-v1-en.pdf) and [preserved v1 data](/investigacion/datos/subagentes-arquitecturas-tokens-tiempo-2026-v1/source-and-data.zip).

The package contains only synthetic data, visible answers and research materials. It includes no credentials, private conversations or private deliberation.

## Sources and consulted versions

@@SOURCES@@
