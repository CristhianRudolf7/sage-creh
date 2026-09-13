"""Evaluator tests: reject plausible-but-wrong results and unsafe SQL.

These tests validate the measurement harness; their outcomes are not model
performance and are never pooled with live experiment results.
"""
import copy
import json
import tempfile
import threading
import time
import unittest
from pathlib import Path

from runner import Run
from tasks import evaluation_tasks, grade, json_equal


class EvaluatorTests(unittest.TestCase):
    def test_reference_answers_and_missing_fields(self):
        for task in evaluation_tasks():
            if task.family == "sql":
                continue
            with self.subTest(task=task.id):
                self.assertTrue(grade(task, {"answer": task.expected})["success"])
                self.assertFalse(grade(task, {})["success"])
                wrong = copy.deepcopy(task.expected)
                if isinstance(wrong, dict) and wrong:
                    wrong.pop(next(iter(wrong)))
                else:
                    wrong = "wrong"
                self.assertFalse(grade(task, {"answer": wrong})["success"])

    def test_boolean_is_not_numeric_answer(self):
        self.assertFalse(json_equal(True, 1))
        self.assertTrue(json_equal(1.0, 1))

    def test_sql_reference_and_join_multiplication(self):
        task = evaluation_tasks()[-2]
        correct = """WITH r AS (SELECT order_id, SUM(amount_cents) cents FROM refunds GROUP BY order_id),
        p AS (SELECT o.customer_id, COUNT(*) n, SUM(o.amount_cents-COALESCE(r.cents,0)) net
        FROM orders o LEFT JOIN r ON r.order_id=o.id WHERE o.status='paid' GROUP BY o.customer_id)
        SELECT c.id, COALESCE(p.n,0), COALESCE(p.net,0) FROM customers c LEFT JOIN p ON p.customer_id=c.id ORDER BY c.id"""
        wrong = """SELECT c.id, COUNT(o.id), COALESCE(SUM(o.amount_cents-r.amount_cents),0)
        FROM customers c LEFT JOIN orders o ON o.customer_id=c.id AND o.status='paid'
        LEFT JOIN refunds r ON r.order_id=o.id GROUP BY c.id ORDER BY c.id"""
        self.assertTrue(grade(task, {"answer": {"sql": correct}})["success"])
        self.assertFalse(grade(task, {"answer": {"sql": wrong}})["success"])
        for statement in ["DELETE FROM customers", "SELECT 1; DROP TABLE orders", "WITH x AS (SELECT 1) DELETE FROM orders"]:
            self.assertFalse(grade(task, {"answer": {"sql": statement}})["success"])

    def test_latest_attempt_tie_breaker(self):
        task = evaluation_tasks()[-1]
        correct = """WITH ranked AS (SELECT task_id,status, ROW_NUMBER() OVER
        (PARTITION BY task_id ORDER BY finished_at DESC,id DESC) rn FROM attempts),
        agg AS (SELECT t.project_id, COUNT(*) n, SUM(CASE WHEN r.status='success' THEN 1 ELSE 0 END) successes
        FROM tasks t LEFT JOIN ranked r ON r.task_id=t.id AND r.rn=1 WHERE t.archived=0 GROUP BY t.project_id)
        SELECT p.id,COALESCE(a.n,0),COALESCE(a.successes,0) FROM projects p LEFT JOIN agg a ON a.project_id=p.id ORDER BY p.id"""
        self.assertTrue(grade(task, {"answer": {"sql": correct}})["success"])
        self.assertFalse(grade(task, {"answer": {"sql": correct.replace("finished_at DESC,id DESC", "finished_at ASC,id ASC")}})["success"])

    def test_accounting_includes_all_roles_without_counting_reasoning_twice(self):
        task = evaluation_tasks()[0]
        client = FakeClient(task.expected)
        with tempfile.TemporaryDirectory() as directory:
            result = Run(client, task, "hierarchical", 1, Path(directory)).finish()
        self.assertTrue(result["success"])
        self.assertEqual(result["calls"], 4)
        self.assertEqual(result["usage"]["total_tokens"], 60)
        self.assertEqual(result["usage"]["reasoning_tokens"], 12)
        self.assertEqual(client.peak, 2)

    def test_partial_generation_cannot_pass_even_with_correct_visible_answer(self):
        task = evaluation_tasks()[0]
        with tempfile.TemporaryDirectory() as directory:
            result = Run(FakeClient(task.expected, status="incomplete"), task, "single", 1, Path(directory)).finish()
        self.assertFalse(result["success"])
        self.assertTrue(result["accounting_complete"])
        self.assertEqual(result["usage"]["total_tokens"], 15)

    def test_missing_usage_is_not_silently_estimated(self):
        task = evaluation_tasks()[0]
        with tempfile.TemporaryDirectory() as directory:
            result = Run(FakeClient(task.expected, missing_usage=True), task, "single", 1, Path(directory)).finish()
        self.assertFalse(result["success"])
        self.assertFalse(result["accounting_complete"])


class FakeClient:
    model = "offline-harness-test-double"

    def __init__(self, expected, status="completed", missing_usage=False):
        self.expected, self.status, self.missing_usage = expected, status, missing_usage
        self.active, self.peak, self.lock = 0, 0, threading.Lock()

    def complete(self, body):
        with self.lock:
            self.active += 1
            self.peak = max(self.peak, self.active)
        time.sleep(0.01)
        if "Decompose the task" in body["input"][0]["content"]:
            output = {"jobs": [{"task": "extract"}, {"task": "constraints"}]}
        else:
            output = {"answer": self.expected}
        with self.lock:
            self.active -= 1
        response = dict(status=self.status, model=self.model,
                        output=[dict(type="message", content=[dict(type="output_text", text=json.dumps(output))])],
                        usage=dict(input_tokens=10, output_tokens=5, total_tokens=15,
                                   input_tokens_details={"cached_tokens": 2}, output_tokens_details={"reasoning_tokens": 3}))
        if self.missing_usage:
            response.pop("usage")
        return response, 0.01


if __name__ == "__main__":
    unittest.main()
