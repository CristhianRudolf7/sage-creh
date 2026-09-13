"""Offline contract, isolation and routing tests; not model-performance data."""
import copy
import json
import tempfile
import threading
import time
import unittest
from pathlib import Path

from architecture import SageRun, contract_errors, discover_skill, risk_reasons
from tasks import evaluation_tasks


class ClientDouble:
    model = 'offline-test-double'

    def __init__(self, answer, other=None, uncertainty=False, malformed=False):
        self.answer, self.other = answer, other
        self.uncertainty, self.malformed = uncertainty, malformed
        self.requests, self.active, self.peak, self.lock = [], 0, 0, threading.Lock()

    def complete(self, body):
        with self.lock:
            self.active += 1
            self.peak = max(self.peak, self.active)
            self.requests.append(copy.deepcopy(body))
        time.sleep(.015)
        role = body['input'][0]['content']
        candidate = {'answer': self.answer}
        if 'Independently solve' in role and self.other is not None:
            candidate = {'answer': self.other}
        if 'Act as the final verifier' in role:
            output = {'answer': self.answer}
        else:
            output = dict(candidate={'wrong': 1} if self.malformed else candidate,
                          uncertainties=['check one issue'] if self.uncertainty else [])
        with self.lock:
            self.active -= 1
        return dict(status='completed', model=self.model,
                    output=[dict(type='message', content=[dict(type='output_text', text=json.dumps(output))])],
                    usage=dict(input_tokens=10, output_tokens=5, total_tokens=15,
                               input_tokens_details={'cached_tokens': 2}, output_tokens_details={'reasoning_tokens': 3})), .015


class ArchitectureTests(unittest.TestCase):
    def test_serialized_tasks_match_historical_evaluation(self):
        tasks = [dict(id=t.id, family=t.family, public=t.public, expected=t.expected, sql_fixtures=t.sql_fixtures) for t in evaluation_tasks()]
        historical = Path(__file__).resolve().parents[1] / 'results/evaluation/tasks.json'
        self.assertEqual(json.loads(json.dumps(tasks)), json.loads(historical.read_text()))

    def run_case(self, index=0, condition='sage', policy='parallel', **options):
        task = evaluation_tasks()[index]
        client = ClientDouble(task.expected, **options)
        with tempfile.TemporaryDirectory() as directory:
            result = SageRun(client, task, condition, 1, Path(directory), policy).finish()
            traces = [json.loads(p.read_text()) for p in Path(directory).glob('traces/*/*.json')]
        return result, client, traces

    def test_public_skill_discovery_and_risk(self):
        for task in evaluation_tasks():
            self.assertEqual(discover_skill(task.public), task.family)
            self.assertEqual(bool(risk_reasons(task.public)), task.family in ['dependencies', 'selection'])
            if task.family != 'sql':
                self.assertEqual(contract_errors(task.public, {'answer': task.expected}), [])

    def test_easy_direct_and_exact_recorded_payload(self):
        result, client, traces = self.run_case()
        self.assertTrue(result['success'])
        self.assertEqual(result['calls'], 1)
        self.assertEqual(traces[0]['request'], client.requests[0])
        packet = json.loads(client.requests[0]['input'][1]['content'])
        self.assertNotIn('skill_catalog', packet)
        self.assertEqual(list(packet['loaded_skills']), ['ledger'])
        self.assertEqual(packet['task'], evaluation_tasks()[0].public)
        self.assertNotIn('expected', packet)
        self.assertNotIn('sql_fixtures', packet)

    def test_parallel_agreement_no_merge_and_accounting(self):
        result, client, _ = self.run_case(index=4)
        self.assertTrue(result['success'])
        self.assertEqual(result['routing']['path'], 'parallel_agreement')
        self.assertEqual(result['calls'], 2)
        self.assertEqual(client.peak, 2)
        self.assertEqual(result['usage']['total_tokens'], 30)
        self.assertEqual(result['usage']['reasoning_tokens'], 6)
        self.assertTrue(all('handoff' not in json.loads(r['input'][1]['content']) for r in client.requests))

    def test_disagreement_gets_third_call(self):
        other = copy.deepcopy(evaluation_tasks()[4].expected)
        other['makespan'] += 1
        result, client, _ = self.run_case(index=4, other=other)
        self.assertTrue(result['success'])
        self.assertEqual(result['calls'], 3)
        self.assertEqual(result['routing']['path'], 'parallel_adjudication')
        self.assertEqual(len(json.loads(client.requests[-1]['input'][1]['content'])['handoff']['proposals']), 2)

    def test_serial_risk_uncertainty_and_shape_gates(self):
        for options in [dict(index=4, policy='serial'), dict(uncertainty=True), dict(malformed=True)]:
            result, _, _ = self.run_case(**options)
            self.assertTrue(result['success'])
            self.assertEqual(result['calls'], 2)
            self.assertTrue(result['routing']['review_triggered'])

    def test_ablations(self):
        result, _, _ = self.run_case(index=4, condition='sage_single')
        self.assertEqual(result['calls'], 1)
        result, client, _ = self.run_case(condition='sage_all_skills')
        self.assertEqual(len(json.loads(client.requests[0]['input'][1]['content'])['loaded_skills']), 10)

    def test_no_semantic_oracle_in_gate(self):
        task = evaluation_tasks()[4]
        wrong = copy.deepcopy(task.expected)
        wrong['makespan'] += 1000
        self.assertEqual(contract_errors(task.public, {'answer': wrong}), [])
        client = ClientDouble(wrong)
        # Execution sees neither reference answers nor SQL fixtures. Scoring is a later separate step.
        from types import SimpleNamespace
        public_only = SimpleNamespace(id='unknown-id', family=task.family, public=task.public)
        with tempfile.TemporaryDirectory() as directory:
            run = SageRun(client, public_only, 'sage', 1, Path(directory))
            self.assertEqual(run.execute(), {'answer': wrong})
            self.assertEqual(len(run.calls), 2)

    def test_sql_shape_only_no_execution(self):
        task = evaluation_tasks()[-1]
        self.assertTrue(contract_errors(task.public, {'answer': 'SELECT 1'}))
        self.assertEqual(contract_errors(task.public, {'answer': {'sql': 'SELECT definitely_wrong'}}), [])
        self.assertTrue(contract_errors(task.public, {'answer': {'sql': ''}}))


if __name__ == '__main__':
    unittest.main()
