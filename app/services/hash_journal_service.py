"""Hash caller chronology separate from the canonical mutating history."""
from __future__ import annotations
from copy import deepcopy
import hashlib,json
from typing import Any
from flask import session
from app.services.hash_main_service import build_hash_main

KEY='hash_execution_journals'
def digest(history: list[dict[str,Any]]) -> str:
    """Bind observations to the actual session history."""
    return hashlib.sha256(json.dumps(history,sort_keys=True).encode()).hexdigest()
def get_journal(structure_id: str,history: list[dict[str,Any]]) -> list[dict[str,Any]]:
    """Return valid chronology or seed legacy confirmed mutations."""
    journal=session.get(KEY,{}).get(structure_id,{})
    if journal.get('history_digest')==digest(history):return deepcopy(journal.get('entries',[]))
    return deepcopy(history)
def record_journal(structure_id: str,old_history: list[dict[str,Any]],new_history: list[dict[str,Any]],operation: str,payload: dict[str,Any],result: dict[str,Any]) -> str:
    """Append one genuine call, preserving equal queries and absent lookups."""
    entries=get_journal(structure_id,old_history)
    prefix = journal_stdout(entries)
    trace=result.get('execution_trace',{});steps=trace.get('steps',[])
    query=(operation in {'get','contains'} and any(f.get('event_type')=='search_entry' for f in steps)) or (operation in {'keys','values','items'} and any(f.get('event_type')=='formatter_entry' for f in steps))
    query = query or (operation == 'stats' and any(f.get('event_type') == 'stats_entry' for f in steps))
    observed_caller = any(step.get('event_type') == 'caller_printf' for step in steps)
    if query or observed_caller or result['success'] and old_history!=new_history:
        entries.append({'operation':operation,'payload':deepcopy(payload),
                        'caller_stdout':result.get('console_stdout', '')})
    result['console_prefix'] = prefix
    result['console_output'] = prefix + result.get('console_stdout', '')
    if trace:
        trace['console_prefix'] = prefix
    journals=deepcopy(session.get(KEY,{}));journals[structure_id]={'history_digest':digest(new_history),'entries':entries};session[KEY]=journals;session.modified=True
    return build_hash_main(entries)


def journal_stdout(entries: list[dict[str, Any]]) -> str:
    """Restore authentic caller bytes; replay legacy cells rather than invent text."""
    from app.services.hash_structure_service import HashStructureService
    fragments = []
    history = []
    for entry in entries:
        if isinstance(entry.get('caller_stdout'), str):
            fragments.append(entry['caller_stdout'])
            # Canonical history contains only mutations, unlike the journal.
            if entry['operation'] in {'create_table', 'insert', 'remove', 'clear', 'destroy_table'}:
                history.append({'operation': entry['operation'], 'payload': deepcopy(entry['payload'])})
        else:
            result = HashStructureService.execute_operation('hash_table', entry['operation'], deepcopy(entry['payload']), history)
            fragments.append(result.get('console_stdout', ''))
            history = result['history']
    return ''.join(fragments)


def get_stdout(structure_id: str, history: list[dict[str, Any]]) -> str:
    """The session journal output, excluding standalone main's exit epilogue."""
    return journal_stdout(get_journal(structure_id, history))
def get_main(structure_id: str,history: list[dict[str,Any]]) -> str:
    """Build exact C from chronology without running any operation."""
    return build_hash_main(get_journal(structure_id,history))
def clear_journal(structure_id: str) -> None:
    """Reset only this Hash caller observation chronology."""
    journals=deepcopy(session.get(KEY,{}));journals.pop(structure_id,None);session[KEY]=journals;session.modified=True
