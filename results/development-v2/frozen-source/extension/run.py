"""Version-2 experiments. Preserve the v1 harness and its historical evidence."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import platform
import random
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'benchmark'))
from runner import Client, Run, MODEL, MAX_OUTPUT, load_key, now, dumps, CONDITIONS as ORIGINALS
from tasks import evaluation_tasks, ledger, schedule, dependencies, selection, memory
from architecture import SageRun

CONDITIONS = ORIGINALS + ['sage', 'sage_single', 'sage_all_skills']
SEED = 20260914


def hashes():
    paths = list((ROOT / 'benchmark').glob('*.py')) + list(ROOT.glob('protocol*.md'))
    paths += [ROOT / 'extension' / name for name in ['architecture.py', 'run.py', 'test_extension.py', 'protocol.en.md', 'protocol.es.md']]
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(paths)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--env-file', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--development', action='store_true')
    parser.add_argument('--policy', choices=['serial', 'parallel'], default='parallel')
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Use a NEW output directory; evidence is never overwritten.')
    key = load_key(args.env_file)
    if args.development:
        tasks = [factory(1501 + i*100 + j, f'DEV{i+1}{j+1}')
                 for i, factory in enumerate([ledger, schedule, dependencies, selection, memory]) for j in range(2)]
        conditions, repeats = ['sage_serial', 'sage_parallel'], 1
    else:
        tasks, conditions, repeats = evaluation_tasks(), CONDITIONS, 2
    task_data = [dict(id=task.id, family=task.family, public=task.public, expected=task.expected, sql_fixtures=task.sql_fixtures) for task in tasks]
    if not args.development:
        original_tasks = json.loads((ROOT / 'results/evaluation/tasks.json').read_text())
        if task_data != original_tasks:
            raise RuntimeError('Evaluation tasks/answers/fixtures differ from v1.')
    rng = random.Random(SEED)
    blocks = [(task, repeat) for repeat in range(1, repeats+1) for task in tasks]
    rng.shuffle(blocks)
    order = []
    for task, repeat in blocks:
        arms = conditions.copy()
        rng.shuffle(arms)
        order.extend((task, repeat, arm) for arm in arms)
    args.output.mkdir(parents=True)
    source_hashes = hashes()
    for name in source_hashes:
        target = args.output / 'frozen-source' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)
    manifest = dict(version='2.0', created_at=now(), development=args.development,
                    requested_model=MODEL, model=MODEL, reasoning_effort='low', max_output_tokens=MAX_OUTPUT,
                    max_calls=5, max_parallel_workers=2, http_timeout_seconds=[10,60], transport_retries=0,
                    run_start_deadline_seconds=240, seed=SEED, repetitions=repeats, conditions=conditions,
                    task_count=len(tasks), run_count=len(order), sage_policy=args.policy,
                    python=platform.python_version(), source_sha256=source_hashes,
                    same_tasks_as_v1=not args.development,
                    order=[dict(task_id=t.id, trial=r, condition=c) for t,r,c in order])
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    (args.output / 'tasks.json').write_text(json.dumps(task_data, ensure_ascii=False, indent=2))
    client = Client(key)
    for index, (task, repeat, condition) in enumerate(order, 1):
        if condition.startswith('sage'):
            policy = condition.split('_')[1] if args.development else args.policy
            run = SageRun(client, task, condition, repeat, args.output, policy)
        else:
            run = Run(client, task, condition, repeat, args.output)
        result = run.finish()
        with (args.output / 'runs.jsonl').open('a') as handle:
            handle.write(dumps(result)+'\n'); handle.flush(); os.fsync(handle.fileno())
        print(dumps(dict(completed=index, total=len(order), task=task.id, condition=condition,
                         success=result['success'], tokens=result['usage']['total_tokens'],
                         seconds=round(result['wall_seconds'],2), error=result['error'])), flush=True)
        if result['error'] and any(code in result['error'] for code in ['provider_http_401','provider_http_403','provider_http_429']):
            raise RuntimeError('Provider access/quota failure; stopped without retries. Preserve partial evidence.')
    final_hashes = hashes()
    if final_hashes != source_hashes:
        raise RuntimeError('Runtime source changed during execution; no completed marker written.')
    (args.output / 'completed.json').write_text(json.dumps(dict(finished_at=now(), source_sha256=final_hashes), indent=2))


if __name__ == '__main__':
    main()
