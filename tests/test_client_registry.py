import pytest
from config.model_registry import REGISTRY, BASE_REVISION
from client.inference_client import InferenceClient
from backend.runtime import verify_files

def test_no_fake_d500():
    d=next(c for c in REGISTRY if c['key']=='D500')
    assert d['adapter_artifact'] is None and 'unavailable' in d['availability']
    assert {c['revision'] for c in REGISTRY}=={BASE_REVISION}

def test_client_absence_and_transport():
    assert InferenceClient().health()['error']['code']=='not_configured'
    for url in ('http://public.example','https://user:pass@example.test','https://example.test?token=bad'):
        with pytest.raises(ValueError):
            InferenceClient(url,'test')

def test_inventory_traversal_or_changed_file(tmp_path):
    (tmp_path/'code.py').write_text('safe')
    with pytest.raises(ValueError):verify_files(tmp_path, {'../escape':'0'*64})
    with pytest.raises(ValueError):verify_files(tmp_path, {'code.py':'0'*64})

def test_missing_rag_does_not_require_a_replacement_index(tmp_path):
    from backend.runtime import retrieval_configured
    manifest={'retrieval':{'path':'retrieval','embedding_url':None}}
    assert not retrieval_configured(tmp_path,manifest)
    home=tmp_path/'retrieval';(home/'chroma').mkdir(parents=True)
    (home/'index_manifest.json').write_text('{}')
    (home/'chroma/chroma.sqlite3').write_bytes(b'synthetic-test-index-placeholder')
    assert not retrieval_configured(tmp_path,manifest)
    manifest['retrieval']['embedding_url']='http://localhost:1234/v1'
    assert retrieval_configured(tmp_path,manifest)
