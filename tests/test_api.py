import threading
from fastapi.testclient import TestClient
from backend.api import create_app, Quota

TOKEN = 'test-' + 'x'*40
HEADERS = {'Authorization': 'Bearer '+TOKEN}

class FakeEngine:
    """Synthetic test double only; never packaged as a serving runtime."""
    rag_available = True
    def __init__(self):
        self.calls = []
    def configurations(self):
        return [{'key': k, 'available': k != 'D500'} for k in ('base','D500','D1000','D1500')]
    def available(self, key, rag=False):
        return key in ('base','D1000','D1500')
    def generate_answer(self, question, key, rag):
        self.calls.append((question,key,rag))
        return {'question': question, 'checkpoint': key, 'rag': rag, 'answer': 'SYNTHETIC TEST RESULT', 'error': None}

def client(tmp_path, limit=10, engine=None):
    engine = engine or FakeEngine()
    return TestClient(create_app(engine, TOKEN, Quota(tmp_path/'quota.db', limit, 100))), engine

def test_auth_and_validation(tmp_path):
    c,e = client(tmp_path)
    assert c.get('/health').status_code == 401
    assert c.get('/health', headers=HEADERS).json()['status'] == 'ready'
    for data in ({'question':'x','model_config':'D500'}, {'question':' '*4,'model_config':'base'},
                 {'question':'x'*4001,'model_config':'base'}, {'question':'x','model_config':'base','url':'evil'}):
        assert c.post('/generate', json=data, headers=HEADERS).status_code == 422
    assert e.calls == []

def test_condition_switches_and_no_cache(tmp_path):
    c,e = client(tmp_path)
    for key,rag in [('base',False),('base',True),('D1000',True),('D1500',True),('D1500',True)]:
        r=c.post('/generate',json={'question':'Synthetic question','model_config':key,'use_rag':rag},headers=HEADERS)
        assert r.status_code == 200
        assert r.json()['checkpoint'] == key and r.json()['rag'] == rag
    assert len(e.calls) == 5

def test_persistent_quota(tmp_path):
    c,e = client(tmp_path, limit=1)
    data={'question':'Synthetic question','model_config':'base','use_rag':False}
    assert c.post('/generate',json=data,headers=HEADERS).status_code==200
    c2,_=client(tmp_path,limit=1)
    assert c2.post('/generate',json=data,headers=HEADERS).status_code==429

def test_failure_sanitized(tmp_path):
    e=FakeEngine()
    def fail(*args):
        raise RuntimeError('SECRET protected passage')
    e.generate_answer=fail
    c,_=client(tmp_path,engine=e)
    r=c.post('/generate',json={'question':'test','model_config':'base'},headers=HEADERS)
    assert r.status_code==503 and 'SECRET' not in r.text and 'protected passage' not in r.text

def test_busy_does_not_queue_or_duplicate(tmp_path):
    entered, release = threading.Event(), threading.Event()
    e=FakeEngine()
    def wait(*args):
        entered.set(); release.wait(3)
        return {'answer':'SYNTHETIC TEST RESULT'}
    e.generate_answer=wait
    c,_=client(tmp_path,engine=e)
    data={'question':'test','model_config':'base'}
    thread=threading.Thread(target=lambda:c.post('/generate',json=data,headers=HEADERS))
    thread.start(); assert entered.wait(2)
    assert c.post('/generate',json=data,headers=HEADERS).status_code==429
    release.set(); thread.join()

def test_unavailable_no_call(tmp_path):
    e=FakeEngine(); e.available=lambda *args:False
    c,_=client(tmp_path,engine=e)
    assert c.post('/generate',json={'question':'test','model_config':'D1000'},headers=HEADERS).status_code==503
    assert not e.calls

def test_large_body_and_validation_do_not_echo_input(tmp_path):
    c,e=client(tmp_path)
    r=c.post('/generate',json={'question':'PRIVATE_SENTINEL','model_config':'invalid'},headers=HEADERS)
    assert r.status_code==422 and 'PRIVATE_SENTINEL' not in r.text
    r=c.post('/generate',content='X'*20001,headers=HEADERS)
    assert r.status_code==413 and not e.calls
