"""Separate, synthetic Graph replay profile; never an acceptance measurement."""
from __future__ import annotations

import argparse
from contextlib import redirect_stderr, redirect_stdout
import cProfile
import hashlib
import io
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

GATE_NODE = 'tests/test_checkpoint_reconstruction_performance.py::test_reconstruction_p95_stays_below_200_ms_for_all_families'
OUTPUT_NAME = 'graph-reconstruction-profile-result.json'


class _Discard(io.TextIOBase):
    def write(self, text):
        return len(text)


def selected(selection: Path) -> bool:
    """Use the actual collected partition, not an assumed stable shard number."""
    manifest = json.loads(selection.read_text(encoding='utf-8'))
    return hashlib.sha256(GATE_NODE.encode('utf-8')).hexdigest() in manifest['selected']


def approved_functions():
    """Map code objects to literal public-source labels, never profiler paths."""
    from app.domain.graph import book_c_subset as book
    from app.domain.graph import book_application
    from app.adapters.graph_adapter import GraphAdapter
    from app.services.graph_structure_service import GraphStructureService
    from copy import deepcopy
    pairs = {
        'graph.rebuild_adapter': GraphStructureService._rebuild_adapter.__wrapped__,
        'graph.adapter.execute': GraphAdapter.execute,
        'graph.execute_book_operation': book_application.execute_book_operation,
        'graph.compiled_program': book.compiled_program,
        'graph.Program.init': book.Program.__init__,
        'graph.BookSession.init': book.BookSession.__init__,
        'graph.BookSession.call': book.BookSession.call,
        'graph.BookSession.graph_state': book.BookSession.graph_state,
        'graph.GraphMachine.invoke': book.GraphMachine.invoke,
        'graph.GraphMachine.statement': book.GraphMachine.statement,
        'graph.GraphMachine.eval': book.GraphMachine.eval,
        'graph.GraphMachine.evaluate_node': book.GraphMachine._eval,
        'graph.GraphMachine.condition': book.GraphMachine.condition,
        'graph.GraphMachine.ref': book.GraphMachine.ref,
        'graph.GraphMachine.variable': book.GraphMachine.variable,
        'graph.GraphMachine.read': book.GraphMachine.read,
        'graph.GraphMachine.emit': book.GraphMachine.emit,
        'graph.GraphMachine.snapshot': book.GraphMachine.snapshot,
        'copy.deepcopy': deepcopy,
    }
    return {function.__code__: label for label, function in pairs.items()}


def _number(value, *, integer=False):
    if type(value) not in ((int,) if integer else (int, float)) or value < 0 or not math.isfinite(value):
        raise ValueError('Invalid profile metric')
    return value


def safe_profile(entries, approved):
    """Exclude unknown frames, callers, filenames, reprs and arbitrary metadata."""
    rows = []
    for entry in entries:
        label = approved.get(entry.code)
        if label is None:
            continue
        rows.append({'function': label,
                     'calls': _number(entry.callcount, integer=True),
                     'recursive_calls': _number(entry.reccallcount, integer=True),
                     'self_seconds': _number(entry.inlinetime),
                     'cumulative_seconds': _number(entry.totaltime)})
    return sorted(rows, key=lambda row: row['function'])


def run():
    """Warm up and profile the same full replay, in a separate process/phase."""
    from scripts.benchmark_checkpoint_reconstruction import HISTORY_SIZE
    from scripts.benchmark_replay import CASES
    rebuild, structure_id, factory = CASES['graph']
    history = factory(HISTORY_SIZE)
    rebuild(structure_id, history)
    profile = cProfile.Profile()
    for _ in range(5):
        _, valid = profile.runcall(rebuild, structure_id, history)
        if len(valid) != HISTORY_SIZE:
            raise RuntimeError('Incomplete synthetic replay')
    return {'profile_iterations': 5, 'history_operations': HISTORY_SIZE,
            'replay_operations_per_iteration': HISTORY_SIZE,
            'functions': safe_profile(profile.getstats(), approved_functions())}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--selection', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        # Imports/replay/errors cannot emit arbitrary data into the CI log.
        with redirect_stdout(_Discard()), redirect_stderr(_Discard()):
            if not selected(args.selection):
                return 0
            report = run()
            serialized = json.dumps(report, allow_nan=False, sort_keys=True, indent=2) + '\n'
            args.output_dir.mkdir(parents=True, exist_ok=True)
            (args.output_dir / OUTPUT_NAME).write_text(serialized, encoding='utf-8')
    except KeyboardInterrupt:
        # Preserve cancellation status without printing exception text or frames.
        print('Synthetic Graph profile interrupted.', file=sys.stderr)
        return 130
    except BaseException:
        # SystemExit and other termination exceptions can carry private text.
        # They are diagnostic failures, never permission to print that text.
        print('Synthetic Graph profile failed; no exception details exported.', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
