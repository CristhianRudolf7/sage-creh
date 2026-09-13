"""Offline reporting-integrity tests, separate from the frozen live runtime."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from analyze import audit
from write_results import table

ROOT = Path(__file__).resolve().parents[1]


class ReportingTests(unittest.TestCase):
    def copied(self, callback):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)/'evidence'
            shutil.copytree(ROOT/'results/development-v2',destination)
            callback(destination)
            with self.assertRaises(AssertionError): audit(destination)

    def test_preserved_development_validates(self):
        rows,_,_,traces = audit(ROOT/'results/development-v2')
        self.assertEqual(len(rows),20)
        self.assertEqual(sum(len(calls) for calls in traces.values()),28)

    def test_changed_frozen_source_is_rejected(self):
        def mutate(destination):
            path = destination/'frozen-source/extension/architecture.py'
            path.write_text(path.read_text()+'\n# changed\n')
        self.copied(mutate)

    def test_changed_usage_is_rejected(self):
        def mutate(destination):
            path = next((destination/'traces').glob('*/*.json'))
            trace = json.loads(path.read_text())
            trace['response']['usage']['total_tokens'] += 1
            path.write_text(json.dumps(trace))
        self.copied(mutate)

    def test_changed_run_order_is_rejected(self):
        def mutate(destination):
            path = destination/'runs.jsonl'
            rows = path.read_text().splitlines()
            rows[0],rows[1] = rows[1],rows[0]
            path.write_text('\n'.join(rows)+'\n')
        self.copied(mutate)

    def test_credential_header_is_rejected(self):
        def mutate(destination):
            path = next((destination/'traces').glob('*/*.json'))
            trace = json.loads(path.read_text())
            trace['Authorization'] = 'synthetic-test-marker'
            path.write_text(json.dumps(trace))
        self.copied(mutate)

    def test_numeric_parity_in_table_rendering(self):
        # Synthetic reporting fixture, never exported as experimental evidence.
        rows = [dict(condition='sage',successes=17,normalized_successes=18,
                     mean_tokens=1234.25,mean_seconds=5.678,calls=41)]
        es,en = [table(rows,lang,False) for lang in ['es','en']]
        self.assertEqual(es.splitlines()[-1],en.splitlines()[-1])
        for lang in ['es','en']:
            latex = table(rows,lang)
            for token in ['17/24','18/24','1,234','5.68','41']: self.assertIn(token,latex)


if __name__=='__main__': unittest.main()
