"""Scan only this repository's publishable text, never private assets."""
from pathlib import Path
import re
ROOT = Path(__file__).resolve().parents[1]
errors = []
for path in ROOT.rglob('*'):
    rel = path.relative_to(ROOT)
    if any(part.startswith('.') and part not in ('.github', '.streamlit', '.gitignore', '.env.example') for part in rel.parts):
        continue
    if '__pycache__' in rel.parts or not path.is_file():
        continue
    if path.suffix in {'.pdf', '.safetensors', '.bin', '.pt', '.sqlite3', '.jsonl'} or path.stat().st_size > 500_000:
        errors.append(str(rel) + ': private/binary/oversized asset')
        continue
    try:
        text = path.read_text()
    except UnicodeDecodeError:
        errors.append(str(rel) + ': binary file')
        continue
    patterns = [r'gh[pousr]_[A-Za-z0-9]{20,}', r'hf_[A-Za-z0-9]{20,}', r'sk-[A-Za-z0-9]{20,}',
                r'-----BEGIN .*PRIVATE KEY-----', r'/Users/[^\s]+', r'/kaggle/working/', r'scarletthe0116']
    for pattern in patterns:
        if re.search(pattern, text) and rel != Path('scripts/audit_public.py'):
            errors.append(str(rel) + ': secret/private identity/path pattern')
if errors:
    raise SystemExit('\n'.join(errors))
print('PASS: no detected secrets, personal paths, raw datasets, model weights, indices or oversized files')
