## Research question

When does delegating to other agents pay off? This CREH Labs study reviews nine arXiv papers first submitted in 2026 and compares four subagent-management patterns. A single-agent baseline and a complete-skill-library condition provide additional comparisons.

**The single agent had the lowest token consumption and mean time in this sample.** Among teams, the reflexive workflow used the fewest tokens and the parallel workflow had the lowest mean latency. These are short tasks with all information supplied; the findings do not establish a universally best architecture.

## The four architectures

| Architecture | Implemented workflow | Calls per task |
| --- | --- | ---: |
| Sequential | One worker extracts evidence, another solves, and a third integrates the answer. | 3 |
| Parallel | Two complementary specialists run concurrently and a merger combines their findings. | 3 |
| Hierarchical | A supervisor chooses one or two assignments, workers execute, and the supervisor integrates. | 3–4 |
| Reflexive | An agent proposes, another critiques, and objections trigger revision, with at most two rounds. | 2–5 |

These are simplified pattern implementations, not reproductions of the cited frameworks. A document-processing comparison of the four families supplies one starting point; the wider review considers authority, context and skills. [Kulkarni and Kulkarni, 2026](https://arxiv.org/html/2603.22651v1).

## Executed benchmark

The study ran **144 live evaluations, 416 model calls and 568,283 provider-reported tokens** using GPT-5.6 Luna with low reasoning effort on 13 September 2026. Model identity and supported effort were checked against the [official model documentation](https://developers.openai.com/api/docs/models/gpt-5.6-luna).

There are **12 distinct tasks**, two repetitions and six conditions, with 24 runs per condition. Families cover ledgers, calendars, dependencies, constrained selection, project-scoped memory and SQL generation. Ten tasks require exact answers; each SQL task must pass three database fixtures. A separate six-run development pilot is preserved and excluded from performance metrics.

Model, data access and maximum limits are shared. Each worker receives the complete original task and a relevant skill. Run order is randomized, with one evaluation at a time and up to two concurrent calls inside eligible workflows. Coordination, criticism, repeated inputs and failures all count. The comparison measures naturally consumed compute rather than an identical spent budget.

## Results

| Configuration | Strict successes | After SQL normalization | Mean tokens | Mean seconds |
| --- | ---: | ---: | ---: | ---: |
| Single agent | 20/24 | 23/24 | 1,143 | 4.72 |
| Sequential | 20/24 | 24/24 | 3,410 | 13.72 |
| Parallel | 19/24 | 23/24 | 3,520 | 8.14 |
| Hierarchical | 20/24 | 24/24 | 4,373 | 11.19 |
| Reflexive | 20/24 | 24/24 | 2,714 | 9.77 |
| Hierarchical + all skills | 21/24 | 24/24 | 8,518 | 11.93 |

Tokens are input plus output, including reasoning. Latency is elapsed time with network and orchestration, excluding final grading. Complete tables include medians, per-call usage and descriptive 95% task-cluster bootstrap intervals. Overlapping request durations are not added together to represent user waiting time.

![Strict task success, token consumption and mean elapsed time; whiskers show task-cluster 95% intervals.](/investigacion/datos/subagentes-arquitecturas-tokens-tiempo-2026-v1/comparison-en.png)

### A finding about SQL formatting

The primary evaluator required a specific JSON structure. In 22 outputs, the model supplied a SQL string inside `answer` instead of a nested object containing `sql`. **Original strict scores were retained.**

An explicitly post-hoc analysis normalized only that wrapper and executed the unchanged query: total completions increased from 120/144 to 142/144. No queries were edited, no other model repaired them and no unfavorable trial was rerun. The two remaining errors involved dependency propagation in T05: H and K started too early despite a correct overall makespan.

This shows why ranking only the strict column mixes formatting and solution quality. The normalized analysis also does not establish correctness beyond the tasks and database fixtures tested.

### Selected skills or the complete catalog

Under the same hierarchical workflow, loading all ten complete skills increased mean usage from **4,373 to 8,518 tokens: 94.8% more**. The paired interval for the increase is 87.9%–101.9%. Strict success changed from 20/24 to 21/24, while normalized success was 24/24 in both conditions. The mean time difference was 0.74 seconds, with an interval from −0.24 to 1.83 seconds.

Here the relevant skill is selected from the known task-family label. The experiment does not evaluate errors or cost from discovering that skill in a real conversation. Separating the catalog, selected instructions and supporting resources is consistent with [Xu and Yan's survey](https://arxiv.org/html/2602.12430v4); our experiment measures only this specific payload variation.

## Choosing a subagent architecture

The recommendation is a **master with optional delegation**: preserve direct execution and create workers when sufficiently separable work can repay planning and integration. The master discovers catalog metadata; each worker receives relevant skills and task references, with additional resources available on request.

One delegation level and two concurrent workers provide an initial implementation scope, not proven optimal values. The runtime should manage dependencies, cancellation, permissions and conflicting writes. Unresolved decisions are escalated to the coordinator.

This adaptive policy and reduced production context **are hypotheses not yet evaluated**. No universally best architecture is established: on these short tasks, the single agent was the most economical option; among the multi-agent patterns, reflexive coordination used the fewest tokens on average and parallel coordination had the lowest mean latency.

## Scope and materials

This is an exploratory preprint without peer review. The sample is small and synthetic, with one model and short contexts; it does not evaluate terminal use, browsing, multi-file coding, long-running autonomy or RAM. Latency depends on the provider and network. Further work requires held-out real tasks, more models and adaptive-delegation comparisons at matched budgets.

- [Full paper in English](/investigacion/documentos/subagentes-arquitecturas-tokens-tiempo-2026-v1-en.pdf).
- [Artículo completo en español](/investigacion/documentos/subagentes-arquitecturas-tokens-tiempo-2026-v1-es.pdf).
- [Code, LaTeX sources, tasks and every trace](/investigacion/datos/subagentes-arquitecturas-tokens-tiempo-2026-v1/source-and-data.zip).
- [Workbook with chart data](/investigacion/datos/subagentes-arquitecturas-tokens-tiempo-2026-v1/benchmark-data.xlsx).
- [Summary CSV](/investigacion/datos/subagentes-arquitecturas-tokens-tiempo-2026-v1/summary.csv) and [per-run results CSV](/investigacion/datos/subagentes-arquitecturas-tokens-tiempo-2026-v1/runs.csv).
- [SQL-format sensitivity](/investigacion/datos/subagentes-arquitecturas-tokens-tiempo-2026-v1/format-sensitivity.csv) and [download checksums](/investigacion/datos/subagentes-arquitecturas-tokens-tiempo-2026-v1/SHA256SUMS.txt).

The bundle preserves the frozen local protocol, code hashes, randomized order, visible responses, times and tokens. Credentials and private reasoning are excluded.

## Review sources

Dates below indicate first submission to arXiv; each link identifies the consulted version. Scores from different papers were not pooled, and simulators or qualitative proposals were not treated as equivalent executed experiments.

- [Agent Skills for Large Language Models: Architecture, Acquisition, Security, and the Path Forward](https://arxiv.org/html/2602.12430v4) — 2026-02-12.
- [Benchmarking Multi-Agent LLM Architectures for Financial Document Processing: A Comparative Study of Orchestration Patterns, Cost-Accuracy Tradeoffs and Production Scaling Strategies](https://arxiv.org/html/2603.22651v1) — 2026-03-24.
- [CRAFT: Grounded Multi-Agent Coordination Under Partial Information](https://arxiv.org/html/2603.25268v2) — 2026-03-26.
- [EvoAgent: An Evolvable Agent Framework with Skill Learning and Multi-Agent Delegation](https://arxiv.org/html/2604.20133v3) — 2026-04-22.
- [Swarm Skills: A Portable, Self-Evolving Multi-Agent System Specification for Coordination Engineering](https://arxiv.org/html/2605.10052v2) — 2026-05-11.
- [When Does Hierarchy Help? Benchmarking Agent Coordination in Event-Driven Industrial Scheduling](https://arxiv.org/html/2605.13172v1) — 2026-05-13.
- [Beyond Sequential Interaction: Benchmarking Parallel Execution and Coordination for GUI Agents](https://arxiv.org/html/2607.22689v1) — 2026-07-17.
- [OrchBench: Evaluating Multi-Agent Orchestration Plans in Isolation via Deterministic Simulation](https://arxiv.org/html/2607.25656v1) — 2026-07-28.
- [Subagents vs Agent Skills: Executing Reusable Knowledge for Long-Horizon Agentic Tasks](https://arxiv.org/html/2609.09233v1) — 2026-09-07.
