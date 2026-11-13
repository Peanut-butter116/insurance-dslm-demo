"""Assemble only public source into an OFFLINE review directory. Never upload/create."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
FILES=['backend/__init__.py','gradio_app.py','example_questions.py','config/__init__.py','config/model_registry.py','config/deployment.py',
       'backend/runtime.py','backend/privacy.py','backend/smoke_validation.py','backend/meeting.py',
       'backend/hf_delivery.py','backend/artifact_transfer.py','backend/zerogpu_runtime.py','backend/zerogpu_smoke.py']

def build(destination):
    destination=Path(destination)
    if destination.exists():raise ValueError('Use a new source-only staging directory')
    destination.mkdir(parents=True)
    for relative in FILES:
        source=ROOT/relative;target=destination/relative;target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(source.read_bytes())
    (destination/'app.py').write_bytes((ROOT/'deploy/zerogpu/app.py').read_bytes())
    (destination/'requirements.txt').write_bytes((ROOT/'deploy/zerogpu/requirements.txt').read_bytes())
    (destination/'README.md').write_text('---\ntitle: Private insurance SLM compatibility test\nsdk: gradio\nsdk_version: 6.32.0\npython_version: 3.12.12\napp_file: app.py\n---\n\nPrepared source only. Create nothing without owner approval. Private visibility and ZeroGPU hardware must be verified in the platform settings. Generated answer text remains disabled.\n')
    inventory={str(p.relative_to(destination)):hashlib.sha256(p.read_bytes()).hexdigest() for p in destination.rglob('*') if p.is_file()}
    (destination/'source_inventory.json').write_text(json.dumps(inventory,indent=2))
    return inventory

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('destination');args=p.parse_args()
    print(json.dumps({'source_files':len(build(args.destination)),'uploaded':False,'activated':False}))
