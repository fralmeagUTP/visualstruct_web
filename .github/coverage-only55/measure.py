"""Bounded coverage-only orchestration for the frozen c395f5f selection."""
from __future__ import annotations
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from typing import Any, Iterable, Sequence

TARGET = "c395f5f70072d211fb0654af9b321294305e64b4"
CAPTURE = r"""
import json, os
from pathlib import Path
import coverage
OUT = Path(os.environ['COV55_OUT'])
PHASE = os.environ['COV55_PHASE']
REPORTS = []
def pytest_collection_finish(session):
    active = coverage.Coverage.current()
    config = None if active is None else {
        'source': active.get_option('run:source'),
        'branch': active.get_option('run:branch'),
        'run_omit': active.get_option('run:omit') or [],
        'report_omit': active.get_option('report:omit') or [],
        'exclude_lines': active.get_option('report:exclude_lines'),
    }
    (OUT / (PHASE + '-selection.json')).write_text(json.dumps({
        'ids': [item.nodeid for item in session.items], 'measurement_config': config,
    }, indent=2), encoding='utf-8')
    if PHASE == 'test':
        expected = json.loads((OUT / 'frozen-plan.json').read_text(encoding='utf-8'))['partition_ids']
        ids = [item.nodeid for item in session.items]
        assert len(ids) == len(set(ids)) == len(expected) and set(ids) == set(expected), 'Measured collection scope changed before tests'
        assert config and config['source'] == ['app'] and config['branch'] is False, 'Measurement settings changed before tests'
        assert config['run_omit'] == config['report_omit'] == [], 'Coverage omissions changed before tests'
def pytest_runtest_protocol(item, nextitem):
    if PHASE == 'collect':
        raise AssertionError('Collection must never execute tests')
def pytest_runtest_logreport(report):
    REPORTS.append({'id': report.nodeid, 'phase': report.when,
                    'outcome': report.outcome, 'xfail': bool(getattr(report, 'wasxfail', False))})
def pytest_sessionfinish(session, exitstatus):
    (OUT / (PHASE + '-execution.json')).write_text(json.dumps({
        'exit_status': int(exitstatus), 'reports': REPORTS,
    }, indent=2), encoding='utf-8')
"""

def read(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding='utf-8'))

def write(path: str | Path, value: Any) -> None:
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')

def sha(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def ids_digest(ids: Iterable[str]) -> str:
    return hashlib.sha256(json.dumps(sorted(ids), ensure_ascii=True,
                         separators=(',', ':')).encode()).hexdigest()

def run(args: Sequence[str], **kwargs: Any) -> subprocess.CompletedProcess[Any]:
    return subprocess.run(args, check=True, **kwargs)

def validate_source(manifest: dict[str, Any], root: Path) -> dict[str, str]:
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    assert head == TARGET == manifest['target_sha'], 'Wrong audited SHA'
    assert os.environ['GITHUB_EVENT_NAME'] == 'workflow_dispatch', 'Manual campaign only'
    assert os.environ['GITHUB_REF_NAME'].startswith('audit/coverage-only55-'), 'Temporary branch only'
    assert int(os.environ['GITHUB_RUN_ATTEMPT']) == 1, 'No retries authorized'
    actual = {}
    for name, expected in manifest['source_hashes'].items():
        file = (root / name).resolve()
        assert file.is_relative_to(root), 'Source outside audited checkout'
        actual[name] = sha(file)
        assert actual[name] == expected, 'Audited source changed: ' + name
    return actual

def validate_environment(manifest: dict[str, Any]) -> None:
    assert sys.version_info[:3] == (3, 10, 22)
    for distribution in ('pytest', 'coverage', 'pytest-cov'):
        assert importlib.metadata.version(distribution) == manifest['environment'][distribution]

def complete_execution(value: dict[str, Any], expected: list[str]) -> None:
    assert value['exit_status'] == 0, 'Pytest did not finish successfully'
    reports = value['reports']
    assert reports and all(r['outcome'] == 'passed' and not r['xfail'] for r in reports), 'Failed/skipped/xfail case'
    for phase in ('setup', 'call', 'teardown'):
        ids = [r['id'] for r in reports if r['phase'] == phase]
        assert len(ids) == len(set(ids)) == len(expected), 'Duplicate or missing execution phase'
        assert set(ids) == set(expected), 'Execution scope changed'

def raw_paths(file: Path, manifest: dict[str, Any], root: Path) -> dict[str, str]:
    from coverage import CoverageData
    data = CoverageData(basename=str(file))
    data.read()
    assert not data.has_arcs(), 'Measurement mode changed'
    result = {}
    for name in data.measured_files():
        actual = Path(name)
        if not actual.is_absolute():
            actual = root / actual
        actual = actual.resolve()
        assert actual.is_relative_to(root / 'app'), 'Measured source outside app: ' + name
        relative = actual.relative_to(root).as_posix()
        assert relative in manifest['app_files'], 'Unknown measured source'
        assert sha(actual) == manifest['source_hashes'][relative], 'Measured source hash changed'
        assert relative not in result, 'Duplicate source aliases'
        result[relative] = name
    assert result, 'Empty raw coverage data'
    return result

def partition(args: argparse.Namespace, manifest: dict[str, Any], root: Path, output: Path) -> None:
    part = manifest['partitions'][args.partition]
    write(output / 'source-before.json', validate_source(manifest, root))
    validate_environment(manifest)
    plugin_dir = Path(tempfile.mkdtemp(prefix='cov55-', dir=os.environ['RUNNER_TEMP']))
    (plugin_dir / 'cov55_capture.py').write_text(CAPTURE, encoding='utf-8')
    env = dict(os.environ, COV55_OUT=str(output), COV55_PHASE='collect', PYTEST_ADDOPTS='',
               PYTHONPATH=str(plugin_dir) + os.pathsep + os.environ.get('PYTHONPATH', ''),
               PYTHONDONTWRITEBYTECODE='1', PYTHONUNBUFFERED='1')
    with (output / 'collection.log').open('wb') as log:
        run([sys.executable, '-m', 'pytest', 'tests', '--collect-only', '-q', '-m', manifest['selector'],
             '-p', 'cov55_capture'], env=env, stdout=log, stderr=subprocess.STDOUT, timeout=60)
    full = read(output / 'collect-selection.json')['ids']
    assert len(full) == len(set(full)) == manifest['count'] == 1556
    assert ids_digest(full) == manifest['ids_sha256'], 'Full selector scope differs from frozen manifest'
    assert set(full) == set(manifest['ids'])
    assert set(part['ids']) == {i for i in full if i.split('::', 1)[0] in part['modules']}
    write(output / 'frozen-plan.json', {'target_sha': TARGET, 'partition': args.partition,
          'full_ids_sha256': ids_digest(full), 'partition_ids': part['ids'],
          'manifest_sha256': sha(args.manifest), 'run_id': os.environ['GITHUB_RUN_ID']})
    raw = output / ('.coverage.' + args.partition)
    env.update(COV55_PHASE='test', COVERAGE_FILE=str(raw))
    command = [sys.executable, '-m', 'pytest', '-m', manifest['selector'], '--cov=app', '--cov-report=',
               '--junitxml=' + str(output / 'pytest.xml'), '-p', 'cov55_capture'] + part['modules']
    write(output / 'test-command.json', {'argv': command, 'measurement': manifest['measurement'],
          'timeout_seconds': manifest['budgets']['test_command_seconds'], 'attempt': 1})
    print('Starting coverage-only partition', args.partition, 'cases', part['count'], 'test cap', manifest['budgets']['test_command_seconds'], 'seconds', flush=True)
    started = time.monotonic()
    timed_out = False
    with (output / 'pytest.stdout.log').open('wb') as stdout, (output / 'pytest.stderr.log').open('wb') as stderr:
        process = subprocess.Popen(command, env=env, stdout=stdout, stderr=stderr, start_new_session=True)
        try:
            status = process.wait(timeout=manifest['budgets']['test_command_seconds'])
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGINT)
            try:
                status = process.wait(timeout=manifest['budgets']['interrupt_grace_seconds'])
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                status = process.wait(timeout=manifest['budgets']['kill_grace_seconds'])
    write(output / 'timing.json', {'seconds': time.monotonic() - started, 'timeout': timed_out,
                                  'pytest_exit': status, 'attempt': 1})
    assert not timed_out and status == 0, 'No retry; preserve partial artifacts'
    actual = read(output / 'test-selection.json')
    assert set(actual['ids']) == set(part['ids']) and len(actual['ids']) == part['count']
    config = actual['measurement_config']
    assert config and config['source'] == ['app'] and config['branch'] is False
    assert config['run_omit'] == config['report_omit'] == [], 'Coverage exclusions changed'
    complete_execution(read(output / 'test-execution.json'), part['ids'])
    paths = raw_paths(raw, manifest, root)
    after = validate_source(manifest, root)
    write(output / 'source-after.json', after)
    write(output / 'partition-result.json', {'schema': manifest['schema'], 'target_sha': TARGET,
          'partition': args.partition, 'status': 'passed', 'test_count': part['count'],
          'manifest_sha256': sha(args.manifest), 'raw_file': raw.name, 'raw_sha256': sha(raw),
          'paths': paths, 'measurement_config': config, 'run_id': os.environ['GITHUB_RUN_ID']})
    print('Coverage partition', args.partition, 'PASS:', part['count'], 'cases; raw data retained', flush=True)

def combine(args: argparse.Namespace, manifest: dict[str, Any], root: Path, output: Path) -> None:
    validate_source(manifest, root)
    validate_environment(manifest)
    results = list(Path(args.inputs).rglob('partition-result.json'))
    assert len(results) == 2, 'Both required partitions must complete'
    values = {read(p)['partition']: (p.parent, read(p)) for p in results}
    assert set(values) == {'a', 'b'}, 'Duplicate or unexpected partitions'
    raw_dir = output / 'raw-preserved'
    raw_dir.mkdir()
    covered_ids = set()
    raw_names = {}
    config = None
    for name in ('a', 'b'):
        directory, value = values[name]
        part = manifest['partitions'][name]
        assert value['status'] == 'passed' and value['target_sha'] == TARGET
        assert value['manifest_sha256'] == sha(args.manifest)
        assert value['run_id'] == os.environ['GITHUB_RUN_ID'], 'Cross-run artifact reuse forbidden'
        assert value['test_count'] == part['count']
        complete_execution(read(directory / 'test-execution.json'), part['ids'])
        assert not (covered_ids & set(part['ids'])), 'Overlapping shards'
        covered_ids.update(part['ids'])
        raw = directory / value['raw_file']
        assert sha(raw) == value['raw_sha256']
        paths = raw_paths(raw, manifest, root)
        assert paths == value['paths'], 'Source path metadata changed'
        for relative, original in paths.items():
            assert relative not in raw_names or raw_names[relative] == original, 'Path aliases require explicit review'
            raw_names[relative] = original
        assert config is None or config == value['measurement_config'], 'Measurement config differs'
        config = value['measurement_config']
        shutil.copyfile(raw, raw_dir / raw.name)
    assert covered_ids == set(manifest['ids']) and len(covered_ids) == 1556
    from coverage import Coverage
    cov = Coverage(data_file=str(output / '.coverage'), source=['app'])
    assert cov.get_option('run:branch') == config['branch']
    assert cov.get_option('report:exclude_lines') == config['exclude_lines']
    cov.combine(data_paths=[str(raw_dir)], strict=True, keep=True)
    cov.save()
    report = output / 'coverage.json'
    cov.json_report(outfile=str(report), pretty_print=True)
    value = read(report)
    assert value['totals']['num_statements'] == manifest['expected_statements'], 'Coverage denominator changed'
    report_paths = {}
    for name in value['files']:
        path = Path(name)
        if not path.is_absolute():
            path = root / path
        path = path.resolve()
        assert path.is_relative_to(root / 'app')
        relative = path.relative_to(root).as_posix()
        assert relative in manifest['app_files'] and sha(path) == manifest['source_hashes'][relative]
        assert relative not in report_paths, 'Duplicate report source aliases'
        report_paths[relative] = name
    assert set(report_paths) == set(manifest['app_files']), 'Missing or extra measured app sources'
    assert set(value['files']) == set(manifest['app_files']), 'Gate report source paths must be canonical app-relative names'
    with (output / 'gates.log').open('wb') as log:
        result = subprocess.run([sys.executable, 'scripts/check_coverage_gates.py', '--report', str(report)],
                                stdout=log, stderr=subprocess.STDOUT, timeout=60)
    write(output / 'final-result.json', {'target_sha': TARGET, 'selection_count': 1556,
          'ids_sha256': ids_digest(covered_ids), 'manifest_sha256': sha(args.manifest),
          'coverage': value['totals'], 'app_source_count': len(report_paths),
          'gates_exit': result.returncode, 'run_id': os.environ['GITHUB_RUN_ID'],
          'raw_data_kept': True, 'historical_timeout_unchanged': True})
    print((output / 'gates.log').read_text(encoding='utf-8'), flush=True)
    assert result.returncode == 0, 'Original thresholds not satisfied'

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['partition', 'combine'])
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--partition', choices=['a', 'b'])
    parser.add_argument('--inputs')
    args = parser.parse_args()
    root = Path.cwd().resolve()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    manifest = read(args.manifest)
    write(output / 'campaign-scope.json', {'target_sha': TARGET, 'workflow_sha': os.environ['GITHUB_SHA'],
          'workflow_ref': os.environ['GITHUB_REF'], 'run_id': os.environ['GITHUB_RUN_ID'],
          'audited_checkout': str(root), 'manifest_sha256': sha(args.manifest),
          'mode': args.mode, 'partition': args.partition})
    if args.mode == 'partition':
        assert args.partition and not args.inputs
        partition(args, manifest, root, output)
    else:
        assert args.inputs and not args.partition
        combine(args, manifest, root, output)

if __name__ == '__main__':
    main()
