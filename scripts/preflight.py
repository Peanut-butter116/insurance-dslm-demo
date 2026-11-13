"""CPU-only verification of an already privately staged serving manifest. No network/model load."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.runtime import verify_files, sha
from config.model_registry import ADAPTERS, BASE_MODEL

def inspect_manifest(manifest):
    root=Path(manifest['asset_root'])
    verify_files(root,manifest['asset_inventory'])
    verify_files(manifest['research_root'],manifest['research_inventory'])
    checked=[]
    for key in ('D1000','D1500'):
        item=manifest['adapters'][key]
        folder=root/item['path']
        cfg=json.loads((folder/'adapter_config.json').read_text())
        if sha(folder/'adapter_model.safetensors')!=ADAPTERS[key]['sha256'] or cfg['base_model_name_or_path']!=BASE_MODEL:
            raise ValueError('Adapter identity differs')
        if cfg.get('r')!=16 or cfg.get('lora_alpha')!=32:
            raise ValueError('Incompatible adapter architecture')
        checked.append(key)
    r=manifest.get('retrieval',{})
    index=root/r.get('path','retrieval')
    return {'checked_adapters':checked,'inventory_verified':True,
            'original_chroma_present':(index/'chroma/chroma.sqlite3').is_file(),
            'network_tests_run':False,'model_loaded':False,'paid_resources_started':False}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',required=True)
    args=parser.parse_args()
    try:
        print(json.dumps(inspect_manifest(json.loads(Path(args.manifest).read_text())),indent=2))
    except Exception:
        raise SystemExit('Preflight failed: missing or incompatible private serving assets; no model or network call made')
