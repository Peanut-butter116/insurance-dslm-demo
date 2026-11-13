"""Bundle a strict public file allowlist for a no-network, no-inference Streamlit preview."""
from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[1]
FILES = ['app.py', 'config/__init__.py', 'config/model_registry.py', 'config/historical_results.py', 'example_questions.py']

def build(output=None):
    target = Path(output) if output else ROOT/'docs/preview'
    target.mkdir(parents=True, exist_ok=True)
    files = {name:(ROOT/name).read_text() for name in FILES}
    files['app.py'] = files['app.py'].replace("import os\n", "import os\nos.environ['PUBLIC_PREVIEW'] = '1'\n", 1)
    (target/'files.json').write_text(json.dumps(files, ensure_ascii=False))
    return files

if __name__ == '__main__':
    build()
