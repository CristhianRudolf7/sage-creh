"""Synthetic, closed-world tasks and deterministic reference evaluators.

Only ``public`` is sent to a model. Reference answers and SQL fixtures remain
inside the evaluator. This is a coordination microbenchmark, not SWE-bench.
"""
from __future__ import annotations

import itertools
import json
import random
import sqlite3
from dataclasses import dataclass
from typing import Any


@dataclass
class Task:
    id: str
    family: str
    public: dict
    expected: Any = None
    sql_fixtures: list | None = None


SKILLS = {
    "ledger": {
        "description": "Deduplicate event ledgers and aggregate exact integer amounts.",
        "instructions": "First resolve repeated event ids using the greatest revision, even when the newer record cancels the old one. Then apply status and currency filters. Apply each eligible event once. Keep money in integer cents; never round or convert currencies without instructions. Negative amounts reduce the net total. Distinguish count of qualifying events from sum of their amounts. Produce every requested group, including zero groups. Reconcile the overall sum against the group sums and the overall count against the group counts. Preserve the task's exact output keys. Never invent missing records or use a discarded revision as an additional payment.",
    },
    "schedule": {
        "description": "Find a common calendar interval across fixed UTC offsets.",
        "instructions": "Normalize all participant intervals to UTC minutes, using UTC = local time minus the signed offset. Restrict the search to the organizer's stated local working window. Busy intervals are half-open: an event ending at the proposed start does not overlap it. Merge overlapping busy intervals across participants before finding gaps. Choose the earliest complete gap that fits the duration; check the end as well as the start. Return the requested organizer-local clock times with zero-padded hours and minutes. Do not infer daylight-saving rules: the task supplies the offsets. If no complete gap fits, return null as instructed.",
    },
    "dependencies": {
        "description": "Compute earliest starts and a critical path in an acyclic dependency graph.",
        "instructions": "Respect every predecessor edge. A task with no predecessor starts at zero. Otherwise its earliest start is the maximum finish among its predecessors, not their sum. Finish is earliest start plus duration. Compute in topological order with unlimited parallel workers unless the task states a different resource limit. Makespan is the maximum finish. A critical path follows predecessor choices attaining that maximum; retain the lexicographically smallest full id sequence among equal-duration critical paths. Return starts for all nodes, including independent branches. Do not confuse a topological ordering with the actual critical path.",
    },
    "selection": {
        "description": "Choose a finite bundle under budget, coverage and compatibility constraints.",
        "instructions": "Apply all hard constraints before comparing objective values. Respect exact cardinality, required capability coverage, forbidden pairs and prerequisite ids. Each item's cost and value count once even when it covers multiple capabilities. Maximize total value among feasible bundles; break equal-value ties by lower total cost and then the lexicographically smallest sorted id list. A high-scoring infeasible bundle is never a valid answer. Return sorted ids and exact integer totals. Use the complete candidate list rather than a greedy choice based only on individual value-to-cost ratio. Keep prerequisite implications directional.",
    },
    "memory": {
        "description": "Reduce scoped preference events into an auditable current snapshot.",
        "instructions": "Process events by ascending sequence number. A confirmed set writes exactly one key in its own scope. A delete removes that key only in the named scope and does not delete an inherited global value. A candidate does not change durable state. Build the effective project view by overlaying its current local keys on the current global keys after all events. Other projects cannot overwrite this project's values. Keep the sequence number that supplied each effective value. Do not promote repeated candidates unless the task explicitly defines such a rule. Explicit values outrank assumptions, and chronological order outranks textual presentation order.",
    },
    "sql": {
        "description": "Write read-only SQLite aggregates without multiplying joined rows.",
        "instructions": "Use only a SELECT statement or WITH followed by SELECT. Honor the requested output column order and deterministic row order. Pre-aggregate one-to-many child tables before joining them to another one-to-many relation, otherwise amounts and counts can multiply. Keep requested entities with zero qualifying rows using LEFT JOIN and COALESCE; filters on the optional side usually belong inside a subquery or ON condition. COUNT(*) after a left join can count a synthetic row; count a non-null child id instead. Choose latest attempts using the specified timestamp and tie-breaker before aggregating statuses. Preserve integer cents and do not assume hidden uniqueness constraints.",
    },
    "file_edits": {
        "description": "Plan precise edits to local text files.",
        "instructions": "Read the current file before proposing a replacement. Match the intended occurrence exactly, preserve unrelated text and line endings, and report ambiguity instead of applying a broad replacement. A successful write is an operating-system result, not proof of semantic correctness. Inspect the resulting difference when it helps establish the requested change. Treat generated and source files differently when the project documents the distinction. Keep file paths explicit, avoid moving unrelated files, and retain the original artifact identifier when reporting a modification. This skill does not grant permissions to execute commands or access credentials.",
    },
    "reminders": {
        "description": "Represent a reminder with an explicit time and delivery state.",
        "instructions": "Separate the reminder content, scheduled instant, time zone and delivery state. Resolve relative dates against the current supplied date, not a remembered date from another session. Ask when the intended time is materially ambiguous. A recurring schedule and a one-time reminder have different completion semantics. Mark delivery only after its channel confirms acceptance. Preserve a pending reminder after a delivery failure and distinguish rescheduling from duplication. Do not claim that a reminder has been created unless a scheduling tool actually returns its persisted identifier. Do not infer that an expired reminder was delivered.",
    },
    "conversation": {
        "description": "Produce a concise, sourced recap of a conversation.",
        "instructions": "Separate the objective, constraints, completed work, current work, blockers, decisions, relevant artifacts and next steps. Preserve unresolved assumptions as assumptions. Distinguish an action proposed in conversation from an action actually completed. Keep the source message or checkpoint identifier for a fact that may need later verification. Prefer explicit user corrections over earlier assistant suggestions. Exclude secrets from a recap. Avoid expanding a short exchange into an invented project history, and do not treat a missing mention as evidence that an event never happened.",
    },
    "incident_triage": {
        "description": "Record an operational incident and bounded diagnostic next steps.",
        "instructions": "Identify the observable symptom, affected component, time interval and available evidence. Separate a confirmed cause from a plausible hypothesis. Begin with read-only diagnostics when these can narrow the cause. Record the exact error class and last successful step rather than guessing that the entire workflow failed. A retry is appropriate only when the failure and action semantics allow it. Keep independent incidents and environments separate, preserve useful logs as references, and do not expose credentials in diagnostic output. A temporary recovery does not establish that the underlying cause is fixed.",
    },
}


def ledger(seed: int, task_id: str) -> Task:
    rng = random.Random(seed)
    rows = []
    for i in range(18):
        row = dict(id=f"E{i:02}", revision=1, project=rng.choice(["atlas", "boreal", "cedar"]),
                   amount_cents=rng.randint(-70, 180) * 25, currency="USD" if i % 4 else "PEN",
                   status="posted" if i % 5 else "pending")
        rows.append(row)
        if i % 3 == 0:
            rows.append(dict(row, revision=2, amount_cents=row["amount_cents"] + 375,
                             status="void" if i % 2 else "posted"))
    rng.shuffle(rows)
    latest = {}
    for row in rows:
        if row["id"] not in latest or row["revision"] > latest[row["id"]]["revision"]:
            latest[row["id"]] = row
    totals = {key: 0 for key in ["atlas", "boreal", "cedar"]}
    count = 0
    for row in latest.values():
        if row["status"] == "posted" and row["currency"] == "USD":
            totals[row["project"]] += row["amount_cents"]
            count += 1
    return Task(task_id, "ledger", {
        "request": "Keep only the greatest revision per id, then sum posted USD events. Include all three projects. Return {totals_cents:{atlas:int,boreal:int,cedar:int}, total_cents:int, event_count:int}.",
        "events": rows,
    }, dict(totals_cents=totals, total_cents=sum(totals.values()), event_count=count))


def clock(minutes: int) -> str:
    return f"{minutes // 60:02}:{minutes % 60:02}"


def schedule(seed: int, task_id: str) -> Task:
    rng = random.Random(seed)
    duration = 45 if seed % 2 else 60
    all_busy, participants = [], []
    for name, offset in [("Lima", -300), ("Lisbon", 60), ("New York", -240)]:
        intervals = []
        for _ in range(3):
            organizer_start = rng.randrange(540, 870, 15)
            organizer_end = organizer_start + rng.choice([30, 45, 60])
            all_busy.append((organizer_start, organizer_end))
            intervals.append([clock(organizer_start + offset + 300), clock(organizer_end + offset + 300)])
        participants.append(dict(name=name, utc_offset_minutes=offset, busy_local=intervals))
    start = next((s for s in range(540, 960 - duration + 1)
                  if all(s + duration <= a or s >= b for a, b in all_busy)), None)
    answer = None if start is None else dict(start_local=clock(start), end_local=clock(start + duration))
    return Task(task_id, "schedule", {
        "request": "Find the earliest common meeting on 2026-09-14 inside the organizer's 09:00–16:00 Lima window (UTC-05:00). Busy intervals are half-open. Use the fixed offsets supplied, no external calendar. Return {start_local:HH:MM,end_local:HH:MM}, or null if impossible.",
        "duration_minutes": duration, "participants": participants,
    }, answer)


def dependencies(seed: int, task_id: str) -> Task:
    rng = random.Random(seed)
    nodes, starts, finishes, paths = [], {}, {}, {}
    for i in range(11):
        name = chr(65 + i)
        parents = sorted(rng.sample(list(finishes), k=min(i, rng.choice([1, 2, 3])))) if i else []
        duration = rng.randint(2, 13)
        start = max((finishes[p] for p in parents), default=0)
        path = min((paths[p] for p in parents if finishes[p] == start), default=[]) + [name]
        starts[name], finishes[name], paths[name] = start, start + duration, path
        nodes.append(dict(id=name, duration=duration, predecessors=parents))
    makespan = max(finishes.values())
    critical = min(paths[n] for n in finishes if finishes[n] == makespan)
    rng.shuffle(nodes)
    return Task(task_id, "dependencies", {
        "request": "With unlimited workers and non-preemptive tasks, compute earliest starts and overall makespan from time zero. Return {earliest_start:{id:int,...},makespan:int,critical_path:[id,...]}. Break critical-path ties using the lexicographically smallest full id sequence.",
        "tasks": nodes,
    }, dict(earliest_start=starts, makespan=makespan, critical_path=critical))


def selection(seed: int, task_id: str) -> Task:
    rng = random.Random(seed)
    items = [dict(id=chr(65+i), cost=rng.randint(4, 14), value=rng.randint(8, 30),
                  capabilities=["storage", "compute", "network"][i % 3:i % 3 + 1]) for i in range(12)]
    items[4]["capabilities"].append("network")
    budget, forbidden, prerequisites = 34, [["B", "E"], ["H", "K"]], {"J": "A", "L": "D"}
    candidates = []
    for combo in itertools.combinations(items, 4):
        ids = sorted(i["id"] for i in combo)
        cost, value = sum(i["cost"] for i in combo), sum(i["value"] for i in combo)
        caps = set(c for item in combo for c in item["capabilities"])
        if (cost <= budget and len(caps) == 3 and not any(set(p) <= set(ids) for p in forbidden)
                and all(a not in ids or b in ids for a, b in prerequisites.items())):
            candidates.append((-value, cost, ids))
    negvalue, cost, ids = min(candidates)
    return Task(task_id, "selection", {
        "request": "Select exactly four items with total cost at most the budget, covering all three capabilities. Enforce forbidden pairs and directed prerequisites. Maximize total value, then minimize cost, then choose lexicographically smallest sorted ids. Return {ids:[...],total_cost:int,total_value:int}.",
        "budget": budget, "items": items, "forbidden_pairs": forbidden, "prerequisites": prerequisites,
    }, dict(ids=ids, total_cost=cost, total_value=-negvalue))


def memory(seed: int, task_id: str) -> Task:
    rng = random.Random(seed)
    events = []
    for seq in range(1, 25):
        events.append(dict(seq=seq, scope=rng.choice(["global", "atlas", "boreal"]),
                           op=rng.choices(["set", "delete", "candidate"], weights=[6, 2, 3])[0],
                           key=rng.choice(["language", "theme", "tone", "timezone"]),
                           value=rng.choice(["option_a", "option_b", "option_c"])))
    state = {scope: {} for scope in ["global", "atlas", "boreal"]}
    for event in events:
        if event["op"] == "set":
            state[event["scope"]][event["key"]] = dict(value=event["value"], source_seq=event["seq"])
        elif event["op"] == "delete":
            state[event["scope"]].pop(event["key"], None)
    effective = {**state["global"], **state["atlas"]}
    rng.shuffle(events)
    return Task(task_id, "memory", {
        "request": "Process events by ascending seq. set confirms a scoped value; delete removes only that scoped key; candidate never changes durable memory. Then overlay atlas on global. Return the effective atlas snapshot {key:{value:string,source_seq:int},...}, omitting absent keys. A project deletion reveals a surviving global value. Ignore boreal when constructing the atlas view.",
        "events": events,
    }, effective)


def sql_task(variant: int, task_id: str) -> Task:
    fixtures = []
    if variant == 1:
        schema = "CREATE TABLE customers(id INTEGER PRIMARY KEY, name TEXT); CREATE TABLE orders(id INTEGER PRIMARY KEY, customer_id INTEGER, status TEXT, amount_cents INTEGER); CREATE TABLE refunds(id INTEGER PRIMARY KEY, order_id INTEGER, amount_cents INTEGER);"
        request = "Write one read-only SQLite query. Include every customer ordered by id. Return columns customer_id, paid_order_count, net_cents. Count orders with status='paid' only. Net is paid order amounts minus all refunds attached to those paid orders; refunds on non-paid orders do not count. Include zero customers. Return {sql:string}."
        for seed in [51, 73, 97]:
            rng = random.Random(seed)
            customers = [(i, f"customer_{i}") for i in range(1, 7)]
            orders = [(i, rng.randint(1, 5), "paid" if i % 3 else "pending", rng.randint(1, 20)*100) for i in range(1, 17)]
            refunds = [(i, rng.randint(1, 16), rng.randint(1, 3)*50) for i in range(1, 15)]
            expected = []
            for customer, _ in customers:
                paid = [o for o in orders if o[1] == customer and o[2] == "paid"]
                net = sum(o[3] - sum(r[2] for r in refunds if r[1] == o[0]) for o in paid)
                expected.append([customer, len(paid), net])
            fixtures.append(dict(tables={"customers": customers, "orders": orders, "refunds": refunds}, expected=expected))
    else:
        schema = "CREATE TABLE projects(id INTEGER PRIMARY KEY); CREATE TABLE tasks(id INTEGER PRIMARY KEY, project_id INTEGER, archived INTEGER); CREATE TABLE attempts(id INTEGER PRIMARY KEY, task_id INTEGER, finished_at INTEGER, status TEXT);"
        request = "Write one read-only SQLite query. Include every project ordered by id. Output project_id, active_task_count, successful_latest_count. Active tasks have archived=0. For each active task choose its latest attempt by greatest finished_at, then greatest attempt id for ties; count it as successful only if that chosen status is 'success'. A task without attempts is not successful. Include empty projects. Return {sql:string}."
        for seed in [12, 22, 38]:
            rng = random.Random(seed)
            projects = [(i,) for i in range(1, 7)]
            tasks = [(i, rng.randint(1, 5), int(i % 4 == 0)) for i in range(1, 17)]
            attempts = [(i, rng.randint(1, 14), rng.randint(1, 4), rng.choice(["success", "failure"])) for i in range(1, 41)]
            expected = []
            for (project,) in projects:
                active = [t for t in tasks if t[1] == project and t[2] == 0]
                success = 0
                for task in active:
                    recent = max((a for a in attempts if a[1] == task[0]), key=lambda a: (a[2], a[0]), default=None)
                    success += int(recent is not None and recent[3] == "success")
                expected.append([project, len(active), success])
            fixtures.append(dict(tables={"projects": projects, "tasks": tasks, "attempts": attempts}, expected=expected))
    return Task(task_id, "sql", dict(request=request, schema=schema), sql_fixtures=fixtures)


def evaluation_tasks() -> list[Task]:
    tasks = []
    for index, factory in enumerate([ledger, schedule, dependencies, selection, memory]):
        for variant in range(2):
            tasks.append(factory(31 + 10*index + variant, f"T{len(tasks)+1:02}"))
    tasks.extend([sql_task(1, "T11"), sql_task(2, "T12")])
    return tasks


def json_equal(actual: Any, expected: Any) -> bool:
    if isinstance(expected, bool) or isinstance(actual, bool):
        return type(actual) is type(expected) and actual == expected
    if isinstance(expected, dict):
        return isinstance(actual, dict) and actual.keys() == expected.keys() and all(json_equal(actual[k], v) for k, v in expected.items())
    if isinstance(expected, list):
        return isinstance(actual, list) and len(actual) == len(expected) and all(json_equal(a, b) for a, b in zip(actual, expected))
    if isinstance(expected, (int, float)):
        return isinstance(actual, (int, float)) and abs(actual - expected) < 1e-9
    return type(actual) is type(expected) and actual == expected


def grade(task: Task, envelope: Any) -> dict:
    if not isinstance(envelope, dict) or set(envelope) != {"answer"}:
        return dict(success=False, score=0.0, reason="invalid_answer_envelope")
    answer = envelope["answer"]
    if task.family != "sql":
        match = json_equal(answer, task.expected)
        return dict(success=match, score=float(match), reason="exact_match" if match else "answer_mismatch")
    if not isinstance(answer, dict) or set(answer) != {"sql"} or not isinstance(answer["sql"], str):
        return dict(success=False, score=0.0, reason="invalid_sql_envelope")
    sql = answer["sql"].strip()
    if not sql.lower().startswith(("select", "with")):
        return dict(success=False, score=0.0, reason="read_only_query_required")
    checks = []
    for fixture in task.sql_fixtures or []:
        db = sqlite3.connect(":memory:")
        try:
            db.executescript(task.public["schema"])
            for table, rows in fixture["tables"].items():
                db.executemany(f"INSERT INTO {table} VALUES ({','.join('?' for _ in rows[0])})", rows)
            allowed = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION, sqlite3.SQLITE_RECURSIVE}
            db.set_authorizer(lambda action, *_: sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY)
            counter = [0]
            def limit():
                counter[0] += 1
                return int(counter[0] > 1000)
            db.set_progress_handler(limit, 1000)
            rows = [list(row) for row in db.execute(sql).fetchmany(100)]
            checks.append(json_equal(rows, fixture["expected"]))
        except sqlite3.Error:
            checks.append(False)
        finally:
            db.close()
    return dict(success=all(checks), score=sum(checks)/len(checks), reason="sql_fixtures", fixture_passes=checks)


if __name__ == "__main__":
    print(json.dumps([dict(id=t.id, family=t.family, public=t.public, expected=t.expected,
                           sql_fixtures=t.sql_fixtures) for t in evaluation_tasks()], indent=2))
