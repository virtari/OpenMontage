"""Trust-boundary tests for development gates; no provider calls or credentials."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'quality_gate.py'


class GateCliTests(unittest.TestCase):
    def test_cli_classifies_null_delimited_git_paths_without_evaluating_text(self):
        result = subprocess.run([sys.executable, '-B', str(SCRIPT), 'classify'],
                                input=b'docs/guide $(touch NEVER).md\0',
                                capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertEqual(json.loads(result.stdout)['jobs'], ['gate-tests'])
        self.assertFalse((ROOT / 'NEVER').exists())


class PolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('quality_gate', SCRIPT)
        cls.gate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.gate)

    def test_mixed_diff_keeps_all_required_checks(self):
        plan = self.gate.classify(['docs/readme.md', 'render_demo.py', 'docs/pilot/sau-4/prototype.html'])
        self.assertEqual(plan['jobs'], ['gate-tests', 'cli', 'ui'])

    def test_unknown_and_unsafe_paths_block_the_gate(self):
        for paths in ([], ['unknown.secret'], ['../README.md'], ['/README.md'], ['docs//x.md'], ['.env'], ['docs/./x.md']):
            with self.subTest(paths=paths), self.assertRaises(ValueError):
                self.gate.classify(paths)

    def test_runtime_and_build_changes_cannot_use_doc_checks_only(self):
        self.assertIn('runtime', self.gate.classify(['lib/checkpoint.py'])['jobs'])
        self.assertIn('composer', self.gate.classify(['remotion-composer/src/Root.tsx'])['jobs'])
        self.assertIn('ui', self.gate.classify(['tests/ui/package-lock.json'])['jobs'])

    def test_aggregate_requires_every_selected_job(self):
        selected = ['gate-tests', 'cli']
        passing = {j: {'result': 'success' if j in selected else 'skipped'} for j in self.gate.JOBS}
        self.gate.aggregate(selected, passing)
        for status in ('failure', 'cancelled', 'skipped', 'pending', 'unknown', None):
            data = copy.deepcopy(passing)
            data['cli']['result'] = status
            with self.subTest(status=status), self.assertRaises(ValueError):
                self.gate.aggregate(selected, data)
        del passing['cli']
        with self.assertRaises(ValueError):
            self.gate.aggregate(selected, passing)

    def test_aggregate_fails_for_missing_selection_or_classifier_disagreement(self):
        jobs = {j: {'result': 'success'} for j in self.gate.JOBS}
        for selected in ([], ['cli'], ['gate-tests', 'made-up-job'], ['gate-tests', 'gate-tests']):
            with self.subTest(selected=selected), self.assertRaises(ValueError):
                self.gate.aggregate(selected, jobs)

    def test_ready_requires_current_full_head_and_exact_markers(self):
        head = 'a' * 40
        valid = f'Katselmoitu head: {head}\nCritical 0; Important 0; Minor 0.\nREADY YES'
        self.gate.review_ready(valid, head)
        for raw in (valid.replace(head, 'b' * 40), valid.replace(head, 'aaaaaaa'),
                    '> ' + valid, '```\n' + valid + '\n```',
                    valid.replace('READY YES', '## READY YES'), valid + '\nLisäteksti',
                    valid.replace('READY YES', 'READY NO'), '',
                    'READY YES\n' + valid):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                self.gate.review_ready(raw, head)

    def test_merge_evidence_rejects_stale_head_wrong_reviewer_or_ci(self):
        head = 'a' * 40
        record = {
            'head': head, 'selected': ['gate-tests', 'cli'],
            'jobs': {j: {'head': head, 'result': 'success' if j in ('gate-tests', 'cli') else 'skipped'} for j in self.gate.JOBS},
            'review': {'session_id': 'independent-session', 'model': 'claude-opus-4-7', 'reviewer': 'claude-cli',
                       'text': f'Katselmoitu head: {head}\nCritical 0; Important 0; Minor 0.\nREADY YES'}
        }
        self.gate.verify(record, head, ['render_demo.py'], 'independent-session')
        for key, value in (('head', 'b' * 40), ('selected', ['gate-tests'])):
            bad = copy.deepcopy(record); bad[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.gate.verify(bad, head, ['render_demo.py'], 'independent-session')
        for key, value in (('session_id', 'implementer'), ('model', 'sonnet'), ('reviewer', 'codex')):
            bad = copy.deepcopy(record); bad['review'][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.gate.verify(bad, head, ['render_demo.py'], 'independent-session')
        bad = copy.deepcopy(record); bad['jobs']['cli']['head'] = 'b' * 40
        with self.assertRaises(ValueError):
            self.gate.verify(bad, head, ['render_demo.py'], 'independent-session')
        bad = copy.deepcopy(record); bad['jobs']['cli']['result'] = 'cancelled'
        with self.assertRaises(ValueError):
            self.gate.verify(bad, head, ['render_demo.py'], 'independent-session')


if __name__ == '__main__':
    unittest.main()
