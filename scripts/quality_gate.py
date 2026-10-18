"""Deterministic development checks. Call from a trusted revision, not PR policy.

This validates data, not its provenance. The delivery controller must obtain
check results and the original reviewer output independently of the PR author.
"""
import json
import re
from pathlib import PurePosixPath
import sys

JOBS = ('gate-tests', 'cli', 'ui', 'runtime', 'composer')


def classify(paths):
    if not isinstance(paths, list) or not paths:
        raise ValueError('Empty or invalid diff')
    required = {'gate-tests'}
    risks = set()
    for name in paths:
        if not isinstance(name, str) or not name or '\\' in name:
            raise ValueError('Invalid path')
        path = PurePosixPath(name)
        if path.is_absolute() or any(p in ('', '.', '..') for p in name.split('/')):
            raise ValueError('Unsafe path')
        if name.startswith('.github/') or name == 'scripts/quality_gate.py' or name in (
            'AGENTS.md', 'CLAUDE.md', 'CODEX.md', 'AGENT_GUIDE.md',
            'tests/test_quality_gate.py', 'Makefile', '.gitignore',
        ):
            risks.add('governance')
            required.add('cli')
        elif name.startswith('tests/ui/') or name.startswith('docs/pilot/sau-4/') and path.suffix in ('.html', '.cjs'):
            risks.add('ui')
            required.add('ui')
        elif name in ('render_demo.py', 'render-demo.sh', 'tests/test_render_demo.py') or name.startswith('remotion-composer/public/demo-props/'):
            risks.add('cli')
            required.add('cli')
        elif name.startswith('remotion-composer/'):
            risks.add('build')
            required.add('composer')
        elif name.startswith(('lib/', 'tools/', 'schemas/', 'pipeline_defs/', 'styles/', 'tests/', 'skills/', '.agents/')) or name in (
            'config.yaml', 'setup.py', 'requirements.txt', 'requirements-dev.txt', 'requirements-gpu.txt',
        ):
            risks.add('runtime')
            required.add('runtime')
        elif path.suffix == '.md' or name == 'LICENSE' or name.startswith('docs/') and path.suffix in ('.png', '.svg'):
            risks.add('docs')
        else:
            raise ValueError(f'Unclassified change: {name}')
    return {'risks': sorted(risks), 'jobs': [j for j in JOBS if j in required]}


def aggregate(selected, results):
    if (not isinstance(selected, list) or not selected or 'gate-tests' not in selected
            or len(set(selected)) != len(selected) or not set(selected) <= set(JOBS)):
        raise ValueError('Invalid check selection')
    if not isinstance(results, dict) or set(results) != set(JOBS):
        raise ValueError('Missing or unexpected check results')
    for name in JOBS:
        result = results[name].get('result')
        if result != 'success' and not (name not in selected and result == 'skipped'):
            raise ValueError(f'Check not successful: {name}={result}')


def review_ready(text, head):
    if not isinstance(head, str) or not re.fullmatch('[0-9a-f]{40}', head):
        raise ValueError('Expected a full lowercase head SHA')
    if not isinstance(text, str):
        raise ValueError('Missing reviewer output')
    lines = text.splitlines()
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines or lines[0] != f'Katselmoitu head: {head}' or lines[-1] != 'READY YES':
        raise ValueError('Missing, stale or non-ready independent verdict')


def verify(record, head, paths, expected_session):
    # Provenance is supplied by the trusted controller, never asserted by a PR.
    if record.get('head') != head or record.get('selected') != classify(paths)['jobs']:
        raise ValueError('Head or classifier mismatch')
    aggregate(record['selected'], record['jobs'])
    for name in record['selected']:
        if record['jobs'][name].get('head') != head:
            raise ValueError('Stale CI head')
    review = record['review']
    model = review.get('model', '')
    if (not expected_session or review.get('session_id') != expected_session
            or review.get('reviewer') != 'claude-cli'
            or not (model == 'opus' or model.startswith('claude-opus-'))):
        raise ValueError('Reviewer identity, session or Opus model mismatch')
    review_ready(review.get('text'), head)


def main(argv):
    if argv == ['aggregate']:
        data = json.load(sys.stdin)
        aggregate(data['selected'], data['jobs'])
        print('QUALITY_GATE_PASS')
        return
    if argv != ['classify']:
        raise ValueError('Expected: classify or aggregate')
    raw = sys.stdin.buffer.read()
    if not raw.endswith(b'\0'):
        raise ValueError('Expected a nonempty NUL-terminated path list')
    print(json.dumps(classify(raw[:-1].decode('utf-8').split('\0'))))


if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except (ValueError, UnicodeError, KeyError, TypeError, AttributeError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
