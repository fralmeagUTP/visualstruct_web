"""Make specific historical-oracle tests resolve their packaged input bytes."""
import ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FILES=['tests/test_sorting_binsort_instructions.py','tests/test_sorting_mergesort_instructions.py','tests/test_hash_creation_insert_documentation.py']

def migrate(path):
 source=path.read_text(encoding='utf-8');tree=ast.parse(source);lines=source.splitlines(keepends=True);offsets=[0]
 for line in lines:offsets.append(offsets[-1]+len(line))
 changes=[]
 for node in ast.walk(tree):
  if not isinstance(node,ast.Call):continue
  receiver=None
  if isinstance(node.func,ast.Attribute) and node.func.attr in {'read_text','read_bytes','is_file'}:receiver=node.func.value
  elif isinstance(node.func,ast.Attribute) and node.func.attr=='copyfile' and node.args:receiver=node.args[0]
  if receiver is None or (isinstance(receiver,ast.Call) and isinstance(receiver.func,ast.Name) and receiver.func.id=='audit_input_path'):continue
  # AST column offsets are UTF-8 byte positions; convert to character offsets.
  begin=offsets[receiver.lineno-1]+len(lines[receiver.lineno-1].encode()[:receiver.col_offset].decode())
  end=offsets[receiver.end_lineno-1]+len(lines[receiver.end_lineno-1].encode()[:receiver.end_col_offset].decode())
  changes.append((begin,end,'audit_input_path('+source[begin:end]+')'))
 for begin,end,replacement in sorted(changes,reverse=True):source=source[:begin]+replacement+source[end:]
 if 'from scripts.published_test_inputs import audit_input_path' not in source:source+='\n'  # Add above tests, below docstring/future import.
 if 'from scripts.published_test_inputs import audit_input_path' not in source:
  parsed=ast.parse(source);index=0
  if parsed.body and isinstance(parsed.body[0],ast.Expr) and isinstance(parsed.body[0].value,ast.Constant):index=parsed.body[0].end_lineno
  while index<len(lines) and lines[index].startswith('from __future__'):index+=1
  modified=source.splitlines(keepends=True);modified.insert(index,'from scripts.published_test_inputs import audit_input_path\n');source=''.join(modified)
 ast.parse(source);path.write_text(source,encoding='utf-8');print(path.name,len(changes))

if __name__=='__main__':
 for name in FILES:migrate(ROOT/name)
