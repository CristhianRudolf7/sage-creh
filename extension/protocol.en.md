# Extension v2: SAGE-CREH and skill-aware subagent coordination

Written before the live development and replication runs. This is a local
pre-execution protocol, not an independently timestamped preregistration.

## Research question and scope

Can selective delegation retain task completion while reducing aggregate tokens
and end-to-end time versus sequential, parallel, hierarchical and reflexive
coordination? SAGE-CREH means skill-aware gated execution. It is a newly composed
local implementation, not a claim to have invented adaptive routing or consensus.
No universal winner is assumed. The target is a quality/token/time Pareto tradeoff.

## Proposed architecture

A deterministic adapter identifies one of six closed-world task interfaces from
PUBLIC JSON structure and supplies the relevant unchanged skill instructions to
each worker, omitting the ten-description catalog. It never reads task IDs,
reference answers or SQL fixtures to route or decide. This is not learned semantic
skill retrieval. All workers receive the same complete original public data.

Two policies are developed. Serial: one proposer, followed by a verifier only for
public structural risk, unresolved issues, or an invalid output contract.
Parallel: for structural risk, run two independent full solvers simultaneously;
accept identical valid candidates without a merger, otherwise call an adjudicator.
Low-risk cases use one proposer, adding a verifier only for issues or invalid shape.
Risk is fixed as a graph with at least eight nodes and any node with two or more
predecessors, or selection with at least ten items, forbidden pairs and prerequisites.
The gate checks key sets and types only, not correctness or constraint satisfaction.
The proposal wrapper includes candidate and unresolved issues. The final answer
retains the original answer envelope. SQL nesting is explicit in the new prompts.
No external solver, tools, grading feedback, private deliberation or cached answer
is supplied. Serial uses at most two calls; parallel at most three, two concurrent.

## Development and selection (not evaluation data)

Ten fresh instances: two each of ledger, schedule, dependency, selection and memory,
with seeds 1501 + 100*family_index + variant. One repetition per policy = 20 runs.
SQL contracts are checked offline; there is no new live SQL development set.
Choose the policy with most strict successes, then lowest mean aggregate tokens,
then lowest mean wall time. Save all attempts, totals and policy decision before
starting the final replication. Do not report these developer-selected results
as held-out evidence. Any further development must be explicitly logged, use a
new output directory and finish before freezing the final runtime.

## Paired replication and controls

Repeat the EXACT twelve original tasks, answers and SQL fixtures twice, nine arms:
single; sequential; parallel; hierarchical; reflexive; hierarchical_all_skills;
sage; sage_single; sage_all_skills. Thus 216 runs, 24 per arm, random seed 20260914.
Blocks are task x repetition, shuffled, then arms randomized inside each block.
Runs are serial across arms, with at most two within-run calls concurrent.
All original arms use the original unmodified implementation and prompts.
All use gpt-5.6-luna, low effort, 1536 maximum output tokens per call, JSON-object,
non-streaming, store=false, the same transport timeouts and no retries.
No change to runtime, prompts, tasks or grading is permitted after final execution
starts. Freeze source copies/hashes before each phase and verify after completion.
Provider authorization/quota failure stops the phase and preserves partial data.

The original hierarchy/all-skills pair isolates catalog-body loading in that
architecture. sage_single uses the same new proposer and skill payload but never
delegates: compare it with sage to isolate the added routing/verification.
sage_all_skills uses the same selected policy and new prompts but loads all ten
unchanged bodies: compare with sage to measure selective instruction loading.
SAGE versus the original architectures changes prompts and catalog exposure as
well as topology; it must not be interpreted as a pure topology effect. Unequal
actual call counts are an outcome, not hidden unequal per-call model budgets.

## Outcomes, uncertainty and limits

Primary: strict all-or-nothing completion, aggregate observed input+output tokens,
and monotonic wall time from run initialization through the final model response
(including local coordination/tracing, excluding grading). Secondary: calls,
input/output/cache/reasoning subdivisions, path frequencies and family results.
Cache is part of input and reasoning is part of output: never add either twice.
Report errors and incomplete accounting; missing usage is not estimated.

Predefine a secondary normalized-SQL score: if and only if the final answer value
is a raw string, wrap that same string in {sql:...} and rerun the SAME evaluator.
Never edit queries, recompute non-SQL answers or repair the primary score. This
isolates the known v1 formatting sensitivity and avoids calling it reasoning gain.
Use 10000 paired bootstrap draws over twelve task clusters, preserving both trials
and every arm within a task, for differences and token ratios. Report intervals
as exploratory; with twelve tasks and ceilings, lack of observed errors does not
establish equality, significance, reliability or broad superiority.

All v1 evaluation data were visible during design. Reusing those exact tasks is a
development-informed paired replication, NOT a blind holdout or generalization
test. Fresh development seeds reduce direct tuning but do not remove task-family
or benchmark awareness. Preserve v1 results separately; do not pool waves for
latency or substitute old measurements for rerun baselines. Publish development
costs separately, raw visible I/O, code, manifest, both strict and normalized
results, and all ablations. No private API key or private reasoning is published.
