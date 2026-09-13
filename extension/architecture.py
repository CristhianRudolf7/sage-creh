"""SAGE-CREH: skill-aware gated execution; no ground truth or grading access.

Routing uses public input structure. Validators check the declared interface,
never solve tasks, execute SQL, inspect fixtures, or choose by reference score.
"""
from __future__ import annotations

import concurrent.futures
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / 'benchmark'))
from runner import Run, ROLES
from tasks import SKILLS

ROLES.update({
    'sage_propose': (
        'Solve the complete task, checking every requested output field. This is an internal proposal, '
        'not the final response: return exactly {"candidate":{"answer":<requested value>},'
        '"uncertainties":["specific unresolved issue",...]}. Use an empty uncertainties list when '
        'no concrete issue remains; the absence of an external evaluator is not an uncertainty. '
        'The requested value must retain its exact nested structure; for SQL it is {"sql":"query"}. '
        'Return no explanations beyond brief unresolved issues. Do not output private deliberation.'
    ),
    'sage_independent': (
        'Independently solve the full task with special attention to constraints, every dependency, '
        'scope and tie breakers. You do not see another agent response. This is an internal proposal: '
        'return exactly {"candidate":{"answer":<requested value>},"uncertainties":['
        '"specific unresolved issue",...]}. Use [] if no concrete issue remains. Preserve all nested '
        'fields; SQL must have answer:{sql:string}. Return concise results, not private deliberation.'
    ),
    'sage_review': (
        'Act as the final verifier and adjudicator. Independently check the candidate or candidates '
        'against the ORIGINAL task, not against agent confidence or majority vote. Recompute any '
        'disputed quantities and inspect all requested fields and tie breakers. Keep correct content '
        'and correct only demonstrated problems. You have no external grading feedback. Return '
        'exactly {"answer":<requested value>}, preserving its full requested nested structure; '
        'for SQL return {"answer":{"sql":"query"}}. Do not output private deliberation.'
    ),
})


def discover_skill(public: dict) -> str:
    """A fixed closed-world adapter, not an oracle using task ids or family labels."""
    if 'schema' in public:
        return 'sql'
    if 'participants' in public:
        return 'schedule'
    if 'items' in public:
        return 'selection'
    if 'tasks' in public:
        return 'dependencies'
    if 'events' in public:
        events = public['events']
        if events and all('revision' in event for event in events):
            return 'ledger'
        if events and all('seq' in event and 'scope' in event for event in events):
            return 'memory'
    raise ValueError('Unsupported public task interface')


def risk_reasons(public: dict) -> list[str]:
    reasons = []
    nodes = public.get('tasks', [])
    if len(nodes) >= 8 and any(len(node.get('predecessors', [])) >= 2 for node in nodes):
        reasons.append('multi_predecessor_graph_with_at_least_8_nodes')
    if len(public.get('items', [])) >= 10 and public.get('forbidden_pairs') and public.get('prerequisites'):
        reasons.append('constrained_selection_with_at_least_10_items')
    return reasons


def contract_errors(public: dict, envelope) -> list[str]:
    """Only schema/type/key checks derived from the public task interface."""
    if not isinstance(envelope, dict) or set(envelope) != {'answer'}:
        return ['Return an object with exactly the answer key.']
    answer = envelope['answer']
    family = discover_skill(public)
    integer = lambda value: type(value) is int  # JSON booleans are not numbers.
    if family == 'schedule' and answer is None:
        return []
    if not isinstance(answer, dict):
        return ['The requested answer value must be a structured object.']
    keys = {
        'ledger': {'totals_cents', 'total_cents', 'event_count'},
        'schedule': {'start_local', 'end_local'},
        'dependencies': {'earliest_start', 'makespan', 'critical_path'},
        'selection': {'ids', 'total_cost', 'total_value'},
        'sql': {'sql'},
    }
    if family in keys and set(answer) != keys[family]:
        return ['Requested field set mismatch: ' + ', '.join(sorted(keys[family]))]
    valid = True
    if family == 'ledger':
        valid = (isinstance(answer['totals_cents'], dict)
                 and set(answer['totals_cents']) == {'atlas', 'boreal', 'cedar'}
                 and all(integer(value) for value in answer['totals_cents'].values())
                 and integer(answer['total_cents']) and integer(answer['event_count']))
    elif family == 'schedule':
        import re
        valid = all(isinstance(value, str) and re.fullmatch(r'\d{2}:\d{2}', value) for value in answer.values())
    elif family == 'dependencies':
        valid = (isinstance(answer['earliest_start'], dict)
                 and set(answer['earliest_start']) == {node['id'] for node in public['tasks']}
                 and all(integer(value) for value in answer['earliest_start'].values())
                 and integer(answer['makespan']) and isinstance(answer['critical_path'], list)
                 and all(isinstance(value, str) for value in answer['critical_path']))
    elif family == 'selection':
        valid = (isinstance(answer['ids'], list) and all(isinstance(value, str) for value in answer['ids'])
                 and integer(answer['total_cost']) and integer(answer['total_value']))
    elif family == 'memory':
        valid = all(isinstance(value, dict) and set(value) == {'value', 'source_seq'}
                    and isinstance(value['value'], str) and integer(value['source_seq']) for value in answer.values())
    elif family == 'sql':
        valid = isinstance(answer['sql'], str) and bool(answer['sql'].strip())
    return [] if valid else ['One or more requested field types or key sets are invalid.']


class SkillClient:
    """Change only skill payload; forward identical model, task data, API options."""
    def __init__(self, client, all_skills=False):
        self.client, self.model, self.all_skills = client, client.model, all_skills

    def complete(self, body):
        # Run.call records this exact request object after its execution.
        packet = json.loads(body['input'][1]['content'])
        skill = discover_skill(packet['task'])
        packet.pop('skill_catalog', None)
        selected = SKILLS if self.all_skills else {skill: SKILLS[skill]}
        packet['loaded_skills'] = {name: entry['instructions'] for name, entry in selected.items()}
        body['input'][1]['content'] = json.dumps(packet, ensure_ascii=False, separators=(',', ':'))
        return self.client.complete(body)


class SageRun(Run):
    def __init__(self, client, task, condition, trial, output, policy='parallel'):
        self.policy = policy
        self.routing = {'policy': policy, 'selected_skill': discover_skill(task.public),
                        'risk_reasons': risk_reasons(task.public), 'review_triggered': False}
        super().__init__(SkillClient(client, all_skills=condition == 'sage_all_skills'), task, condition, trial, output)

    def inspect(self, proposal):
        if not isinstance(proposal, dict):
            return None, ['Malformed internal proposal.']
        candidate = proposal.get('candidate')
        reasons = contract_errors(self.task.public, candidate)
        uncertainty = proposal.get('uncertainties')
        if not isinstance(uncertainty, list) or any(not isinstance(item, str) for item in uncertainty):
            reasons.append('Malformed uncertainty list.')
        elif uncertainty:
            reasons.append('Solver reported unresolved issues.')
        return candidate, reasons

    def execute(self):
        risks = self.routing['risk_reasons']
        if self.condition != 'sage_single' and self.policy == 'parallel' and risks:
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                futures = [pool.submit(self.call, role) for role in ['sage_propose', 'sage_independent']]
                proposals = [future.result() for future in futures]
            checked = [self.inspect(proposal) for proposal in proposals]
            candidates = [entry[0] for entry in checked]
            matching = (not any(entry[1] for entry in checked)
                        and json.dumps(candidates[0], sort_keys=True) == json.dumps(candidates[1], sort_keys=True))
            self.routing.update(path='parallel_agreement' if matching else 'parallel_adjudication',
                                gate_errors=[entry[1] for entry in checked], agreement=matching)
            if matching:
                return candidates[0]
        else:
            proposals = [self.call('sage_propose')]
            candidate, errors = self.inspect(proposals[0])
            self.routing.update(path='direct', gate_errors=[errors])
            if self.condition == 'sage_single':
                return candidate
            if not errors and not (self.policy == 'serial' and risks):
                return candidate
            self.routing['path'] = 'selective_review'
        self.routing['review_triggered'] = True
        return self.call('sage_review', {'proposals': proposals, 'routing': self.routing})

    def finish(self):
        result = super().finish()
        result['routing'] = self.routing
        return result
