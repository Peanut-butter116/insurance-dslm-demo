import ast,json,re
from pathlib import Path

def test_notebook_is_code_only_pinned_and_blocks_activation_by_default():
    root=Path(__file__).parents[1]
    nb=json.loads((root/'notebooks/kaggle_supervised_demo.ipynb').read_text())
    assert nb['metadata']['kernelspec']['name']=='python3'
    sources=[''.join(c['source']) for c in nb['cells'] if c['cell_type']=='code']
    assert 'OWNER_APPROVED_FREE_SESSION = False' in sources[0]
    assert 'FREE_GPU_QUOTA_CONFIRMED = False' in sources[0]
    assert 'STOP_SESSION_NOW = False' in sources[-1]
    assert re.search(r"DEMO_COMMIT = '[0-9a-f]{40}'",''.join(sources))
    assert all(not c.get('outputs') for c in nb['cells'])
    for source in sources:ast.parse(source)
