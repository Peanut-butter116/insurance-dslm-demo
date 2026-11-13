import pytest
from backend.kaggle_session import NotebookSession,prepare_private_notebook
class FakeEngine:
    rag_available=False
    def __init__(self):self.calls=[]
    def available(self,key,rag=False):return key in ('base','D1000','D1500') and not rag
    def configurations(self):return []
    def generate_answer(self,q,key,rag):
        self.calls.append((q,key,rag))
        return {'answer':'SYNTHETIC TEST RESULT','checkpoint':key,'rag':rag,'error':None}


def test_kaggle_is_never_activated_without_explicit_permission(monkeypatch):
    monkeypatch.delenv('FREE_KAGGLE_SERVING_APPROVED',raising=False)
    monkeypatch.delenv('FREE_KAGGLE_QUOTA_CONFIRMED',raising=False)
    with pytest.raises(RuntimeError,match='explicit free-GPU approval'):prepare_private_notebook()


def test_private_notebook_routes_three_configs_without_network_listener(tmp_path):
    e=FakeEngine();s=NotebookSession(e,tmp_path,ttl_seconds=60)
    try:
        for key in ['base','D1000','D1500']:
            v=s.predict('Synthetic public-safe question',key)
            assert v['checkpoint']==key and v['rag'] is False
        assert [c[1] for c in e.calls]==['base','D1000','D1500']
        assert all(c[2] is False for c in e.calls)
        assert s._client.get('/health').status_code==401
    finally:s.close()
    s.close()  # Idempotent manual stop plus expiry timer.
    with pytest.raises(RuntimeError):s.predict('Synthetic','base')
