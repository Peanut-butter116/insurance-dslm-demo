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
