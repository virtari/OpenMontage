"""Prove each new development boundary in disposable copies, never the checkout."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / 'scripts/quality_gate.py').read_text()
MUTATIONS = [
    ('stale-head', "record.get('head') != head", 'False', 'PolicyTests.test_merge_evidence_rejects_stale_head_wrong_reviewer_or_ci'),
    ('ci-head', "if record['jobs'][name].get('head') != head:", 'if False:', 'PolicyTests.test_merge_evidence_rejects_stale_head_wrong_reviewer_or_ci'),
    ('verdict', "lines[-1] != 'READY YES'", 'False', 'PolicyTests.test_ready_requires_current_full_head_and_exact_markers'),
    ('review-head-line', "lines[0] != f'Katselmoitu head: {head}'", 'False', 'PolicyTests.test_ready_requires_current_full_head_and_exact_markers'),
    ('required-check', "if result != 'success' and not (name not in selected and result == 'skipped'):", 'if False:', 'PolicyTests.test_aggregate_requires_every_selected_job'),
    ('unknown-path', "raise ValueError(f'Unclassified change: {name}')", "risks.add('docs')", 'PolicyTests.test_unknown_and_unsafe_paths_block_the_gate'),
    ('selection', "record.get('selected') != classify(paths)['jobs']", 'False', 'PolicyTests.test_merge_evidence_rejects_stale_head_wrong_reviewer_or_ci'),
    ('expected-session', 'not expected_session or ', '', 'PolicyTests.test_merge_evidence_rejects_stale_head_wrong_reviewer_or_ci'),
    ('reviewer', "or review.get('reviewer') != 'claude-cli'", 'or False', 'PolicyTests.test_merge_evidence_rejects_stale_head_wrong_reviewer_or_ci'),
    ('opus-model', "or not isinstance(model, str) or not model.startswith('claude-opus-')", 'or False', 'PolicyTests.test_merge_evidence_rejects_stale_head_wrong_reviewer_or_ci'),
    ('workflow-coverage', 'required.update(JOBS)', "required.add('cli')", 'PolicyTests.test_workflow_or_gate_policy_change_exercises_every_defined_job'),
    ('governance', "'PROJECT_CONTEXT.md', 'COPILOT.md', 'CURSOR.md', 'docs/DEVELOPMENT.md',", '', 'PolicyTests.test_all_shared_development_instructions_are_governance'),
    ('docs-scope', "risks.add('docs')", "required.add('cli')", 'PolicyTests.test_all_shared_development_instructions_are_governance'),
    ('classifier-result', "if needs['classify']['result'] != 'success':", 'if False:', 'GateCliTests.test_ci_gate_rejects_failed_classifier_even_when_test_jobs_are_green'),
    ('checkout-head', "if subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip() != head:", 'if False:', 'GateCliTests.test_ci_plan_binds_the_real_checkout_even_under_python_optimization'),
]


def main():
    results = []
    for name, before, after, test in MUTATIONS:
        if SOURCE.count(before) != 1:
            raise SystemExit(f'Mutation target changed: {name}')
        with tempfile.TemporaryDirectory(prefix='openmontage-gate-mutation-') as directory:
            work = Path(directory)
            (work / 'scripts').mkdir()
            (work / 'tests').mkdir()
            (work / 'tests/__init__.py').write_text('')
            (work / 'tests/test_quality_gate.py').write_bytes((ROOT / 'tests/test_quality_gate.py').read_bytes())
            (work / 'scripts/quality_gate.py').write_text(SOURCE.replace(before, after, 1))
            run = subprocess.run([sys.executable, '-B', '-m', 'unittest', f'tests.test_quality_gate.{test}', '-v'],
                                 cwd=work, capture_output=True, text=True, timeout=15)
            if run.returncode == 0 or 'FAIL:' not in run.stderr or 'ERROR:' in run.stderr:
                print(run.stdout + run.stderr, file=sys.stderr)
                raise SystemExit(f'Mutation survived or did not produce an assertion failure: {name}')
            results.append({'boundary': name, 'test': test, 'caught': True})
    if SOURCE != (ROOT / 'scripts/quality_gate.py').read_text():
        raise SystemExit('Live source changed')
    print(json.dumps({'sourceSha256': hashlib.sha256(SOURCE.encode()).hexdigest(), 'mutations': results}))


if __name__ == '__main__':
    main()
