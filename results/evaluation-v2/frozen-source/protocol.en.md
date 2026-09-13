# Subagent orchestration microbenchmark: frozen experimental settings

Version 1.0, 13 September 2026. This local protocol is written before the held-out evaluation; it is not an externally registered preregistration. Literature inclusion: arXiv v1 submitted during 2026 and no later than 13 September 2026. Results from other papers are context, never pooled with this experiment.

## Question and scope

Measure whether four bounded multi-agent coordination patterns improve exact task completion enough to justify their tokens and elapsed time. A single-agent baseline and a separate skill-loading ablation are included. These are live API executions of synthetic, closed-world reasoning tasks. They do not measure terminal actions, long-running autonomy, web browsing, production reliability or local RAM per agent. Python is used for an independent research harness.

## Conditions

| ID | Workflow | Model calls | Parallel workers |
| --- | --- | --- | --- |
| single | One complete solver | 1 | 1 |
| sequential | Evidence extraction → solver → finalizer; each stage receives the original task and immediately preceding handoff | 3 | 1 |
| parallel | Two fixed complementary specialists → merger | 3 | 2 |
| hierarchical | Supervisor creates 1–2 assignments → workers → supervisor integration | 3–4 | 2 |
| reflexive | Proposal → critique; if rejected, revision; at most two critique/revision rounds | 2–5 | 1 |
| hierarchical_all_skills | Same hierarchical workflow, with all ten full skills loaded at every node | 3–4 | 2 |

Each node is a distinct stateless model invocation with a role prompt. The shared underlying model is identical across all roles. Every call receives the complete original task, the same ten-entry skill metadata catalog, and the relevant procedural skill. The ablation alone loads all ten skill bodies. Skill selection uses the known task-family label without a model or retrieval call; this deliberately isolates payload overhead and does not evaluate real-world skill routing. No conversation history or hidden state is inherited. These are simplified pattern implementations, not reproductions of the cited systems.

## Tasks and controls

Twelve fixed evaluation instances: two each for event-ledger deduplication/aggregation, calendar intersection with fixed UTC offsets, DAG scheduling/critical paths, constrained bundle optimization, scoped memory reduction, and SQLite query generation. All inputs and constraints are supplied. Ten tasks require an exact structured answer; the two SQL tasks must pass three distinct database fixtures each, including empty entities and join/tie edge cases. Ground truth comes from deterministic reducers, exhaustive enumeration or fixture-level calculations. It is never placed in a request or used as agent feedback. Output must be a JSON object containing only `answer`.

Run each task twice for every condition: 12 × 2 × 6 = 144 evaluation runs, with 24 per condition. The four multi-agent patterns plus baseline form the primary 120-run comparison; the all-skills variant contributes 24 ablation runs. Randomize task/trial blocks and condition order within blocks with seed 20260913. Run only one evaluation at a time, with up to two concurrent API requests inside eligible workflows. Repeat on identical task inputs; these are 12 distinct instances, not 144 independent tasks.

Use `gpt-5.6-luna`, reasoning `low`, Responses API, JSON-object mode, `store:false`, non-streaming, maximum 1,536 output tokens per call including reasoning. Do not set temperature or a model seed. API output reports the resolved model. No automatic HTTP retries. Maximum five calls per run; a new call cannot start after 240 seconds. HTTP connect/read timeouts are 10/60 seconds; the start deadline is not a strict wall-clock kill. No application response cache. Provider input caching is recorded, not disabled. Finalization and coordinator calls count against the same limits.

Before evaluation, run a six-condition development pilot on separate ledger instance DEV01, seed 901. Do not pool pilot data. Fix only harness/protocol issues identified before the evaluation; retain pilot evidence. Freeze source hashes in the evaluation manifest and compare them after completion. Do not tune prompts, task selection, output caps or graders after viewing evaluation performance. Malformed plans, incomplete generation, missing usage and transport failures remain recorded failures; no favorable reruns or condition-specific repairs.

## Measurement and analysis

Primary success is exact whole-task completion; SQL partial fixture scores are secondary. Measure wall time from run construction to final answer/error, including orchestration, API/network waiting and trace writes, excluding grading. Also record the sum of API-call durations; it is not elapsed latency when calls overlap.

Sum provider-reported input and output tokens across every call, including coordinators, critics, failed attempts with usage, and repeated handoffs. Total tokens already include reasoning output and cached input; do not add those subcategories again. Record cached input, reasoning tokens and maximum single-call input separately. Missing usage stays explicitly incomplete; observed totals are lower bounds and cannot establish a token-efficiency winner. No token estimates replace missing reports.

Publish successes/24, success percentage, mean and median latency, total/mean tokens, call count, successes per 100,000 total tokens, and successes per minute of accumulated run wall time. The latter is a serial-workload efficiency measure, not saturated server throughput. Compare all attempts, not only successes. Report per-task results and failures. A Pareto comparison uses success (higher), average total tokens and average wall time (lower); equal success does not establish equivalent general capability.

Use a paired cluster bootstrap with 10,000 draws and seed 20260913: sample the twelve task ids with replacement and retain both repetitions and all compared conditions for each sampled id. Report descriptive 95% percentile intervals on success, mean tokens and mean latency, and paired ablation differences. Do not treat the 24 repeated runs as 24 unrelated tasks. With this small synthetic sample, intervals are exploratory and no universal superiority or production SLA is established.

## Reproducibility and limits

Release public task definitions, evaluator, all role/skill prompts, source hashes, randomized run order, per-call request text, visible model output, usage, timestamps, answer and grading record. Credentials, authorization headers and private reasoning are excluded. The manifest records Python, HTTP-client, platform, requested model and effort; traces record returned model and service tier. Provide CSV/XLSX chart data and both language papers.

Principal threats: small author-designed task set; one low-effort model; short contexts; shared full input at every node; fixed prompts; unequal naturally consumed compute within a common cap; predetermined correct skill family; same-day provider caching/latency; no external actions or multi-file coding; only two stochastic repetitions. A broader production decision requires held-out real tasks and additional models. Recommendations must distinguish measured findings from untested system design.

Editorial note (2026-09-13): the title and scope framing were revised after evaluation. Experimental settings are unchanged. Original and amended document hashes are recorded in `editorial-amendments.json`; historical run manifests retain their original hashes.
