"""Tool-aided source construction only. Never imports or executes task source."""
from pathlib import Path
import json, os, textwrap
ROOT = Path(__file__).resolve().parents[1]
AUTHOR = os.environ['CODEX_THREAD_ID']
CALLSIGN = '0985_Codex_gpt-61-sol_Sub_M11DevTasks'
HELPER = '''"""JSON domain checks, with no coercion or external effects.

Lists remain caller-owned. Task code must build its own output containers.
Booleans are intentionally excluded from the integer domain.
String values retain spelling, whitespace and Unicode code points.
"""


def sequence(value):
    """Require an actual JSON-style array."""
    if not isinstance(value, list):
        raise ValueError("expected list")
    return value


def mapping(value):
    """Require a JSON object with string keys."""
    if not isinstance(value, dict):
        raise ValueError("expected object")
    if any(not isinstance(key, str) for key in value):
        raise ValueError("expected string keys")
    return value


def integer(value):
    """Do not accept bool as an integer."""
    if type(value) is not int:
        raise ValueError("expected integer")
    return value


def text(value):
    """Do not trim, normalize or stringify input implicitly."""
    if not isinstance(value, str):
        raise ValueError("expected string")
    return value
'''

def write(number, name, cls, spec, body, cases, public, errors, changes, fact=None):
    task=ROOT/name
    header='"""Builder-authored dev source; NOT_RUN; private-only pending review."""\nfrom helpers import integer, mapping, sequence, text\n\n'
    correct=header+textwrap.dedent(body).strip()+'\n'
    variants={'oracle':correct,'fixture':header+'def solve(data):\n    """Implement this task contract; construction has not run it."""\n    raise NotImplementedError("development implementation missing")\n'}
    for n,(old,new) in enumerate(changes,1):
        if old not in correct: raise ValueError((name,old))
        variants[f'wrong/{n}']=correct.replace(old,new,1)
    for variant,source in variants.items():
        folder=task/variant;folder.mkdir(parents=True,exist_ok=True)
        (folder/'core.py').write_text(source,encoding='utf-8')
        (folder/'helpers.py').write_text(HELPER,encoding='utf-8')
    (task/'task.md').write_text(f'# {name}\n\nBuilder-authored development task; private-only pending rights and semantic review.\n\nImplement `solve(data)` in `fixture/core.py`. Python 3.12 standard library only. Candidate module root contains `core.py` and `helpers.py`. Inputs and outputs are JSON-compatible. Reject out-of-domain inputs with `ValueError` (missing required fields may raise `KeyError`). Do not mutate inputs.\n\n{spec}\n\nPublic tests are minimal examples. This is a development task, never independent evidence.\n',encoding='utf-8')
    for part,examples in [('public',public),('hidden',cases)]:
        folder=task/part;folder.mkdir(exist_ok=True)
        source='"""Builder-authored dev expectations; not independent; NOT_RUN."""\nimport copy\nimport unittest\nfrom core import solve\n\nCASES = '+repr(examples)+'\n\n\nclass ContractCases(unittest.TestCase):\n    def test_examples_and_input_ownership(self):\n        for data, expected in CASES:\n            with self.subTest(data=data):\n                before = copy.deepcopy(data)\n                self.assertEqual(solve(data), expected)\n                self.assertEqual(data, before)\n'
        if part=='hidden':
            source+='\n    def test_invalid_input(self):\n        for data in '+repr(errors)+':\n            with self.subTest(data=data):\n                with self.assertRaises(ValueError):\n                    solve(data)\n'
            (folder/'expected-behavior.json').write_text(json.dumps(dict(independent=False,author='builder_lineage',execution_status='NOT_RUN',cases=[dict(input=a,expected=b) for a,b in cases],invalid_inputs=errors),indent=2)+'\n',encoding='utf-8')
        source+='\n\nif __name__ == "__main__":\n    unittest.main()\n'
        (folder/'test_contract.py').write_text(source,encoding='utf-8')
    if fact: kind,status,provenance,value=fact
    else: kind,status,provenance,value=('convention','current','synthetic housekeeping; irrelevant to solve','Review notes use UTC dates; this does not affect function behavior.')
    facts=[dict(id=f'DEV-{number:02d}-F1',type=kind,status=status,provenance=provenance,date='2026-10-27',value=value)]
    memory=task/'memory';memory.mkdir(exist_ok=True)
    typed=json.dumps(facts,indent=2)+'\n'
    prose='\n'.join(f'Fact {f["id"]}. Type: {f["type"]}. Status: {f["status"]}. Provenance: {f["provenance"]}. Date: {f["date"]}. Value: {f["value"]}' for f in facts)+'\n'
    difference=len(typed.encode())-len(prose.encode())
    if difference>=0: prose+=' '*difference
    else: typed+=' '*(-difference)
    for filename,content in [('facts.json',json.dumps(facts,indent=2)+'\n'),('m1.md',prose),('m2.json',typed)]:
        (memory/filename).write_text(content,encoding='utf-8')
    metadata=dict(schema_version='m11-dev-task/1',id=f'dev-{number:02d}',family=name,task_class=cls,author_session=AUTHOR,author_callsign=CALLSIGN,independence='builder_lineage',rights='private_only_pending_review',rights_review='PENDING',semantic_review='PENDING',execution_status='NOT_RUN',expected_behavior_authorship='builder-authored, not independent',patch_format='full_replacement_tree',patch_application='replace candidate core.py and helpers.py with named tree; never expose hidden/oracle/wrong/metadata to candidate',grader_contract='future isolated trusted grader sets candidate module root on import path and loads checker by file; inventory tools must not import candidate',wrong_variants=[dict(path=f'wrong/{n}',deliberate_change=old+' -> '+new) for n,(old,new) in enumerate(changes,1)],memory=dict(fields=['id','type','status','provenance','date','value'],m0='absent',m1='memory/m1.md',m2='memory/m2.json',canonical='memory/facts.json',native_loading='NOT_VERIFIED',semantic_equality='NOT_VERIFIED',native_token_counts=None))
    (task/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    print(f'WROTE_SOURCE {number:02d} {name}')
