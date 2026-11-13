import time
from types import SimpleNamespace
import pytest
from fastapi.testclient import TestClient
from backend.meeting import MeetingController,ReleaseReview
from config.deployment import BUNDLE_SHA256
from config.model_registry import BASE_REVISION,ADAPTERS
from gradio_app import create_http_app,create_ui

class Session:
    def __init__(self):self.calls=[];self.closed=False
    def predict(self,q,c):
        self.calls.append((q,c))
        return {'answer':'SYNTHETIC UNIT TEST ONLY','checkpoint':BASE_REVISION if c=='base' else 'sha256:'+ADAPTERS[c]['sha256'],
          'actual_selection_proof':{'enabled':c!='base','active_adapters':['D1000'] if c=='base' else [c]},
          'latency_seconds':1.25,'refused':True,'gpu_measurements':{'peak_allocated_bytes':1024,'private_field':'DO_NOT_RETURN'},
          'retrieved_evidence':'RESTRICTED_TEST_MARKER','question':q}
    def close(self):self.closed=True

def test_routes_actual_config_and_projects_only_safe_fields():
    s=Session();c=MeetingController(s)
    for key in ['base','D1000','D1500']:
        r=c.predict('Synthetic question',key)
        assert r['condition']==key and r['refused'] is True
        assert r['gpu']=={'peak_allocated_bytes':1024}
        assert 'RESTRICTED_TEST_MARKER' not in str(r) and 'question' not in r
    assert [x[1] for x in s.calls]==['base','D1000','D1500']
    assert 'limit' in c.predict('Synthetic','base')['status']

def test_errors_withheld_expiry_and_no_model_have_no_answer():
    s=Session();c=MeetingController(s)
    s.predict=lambda *a:{'error':{'message':'SECRET_TEST_MARKER'},'answer':'RESTRICTED_TEST_MARKER'}
    assert 'answer' not in c.predict('Synthetic','base')
    c.expires_at=time.time()-1
    assert 'expired' in c.predict('Synthetic','base')['status']
    assert 'answer' not in MeetingController().predict('Synthetic','base')

def test_checkpoint_selection_and_input_fail_closed():
    s=Session();c=MeetingController(s)
    for q,k in [('', 'base'),('x'*4001,'base'),('Synthetic','D500')]:assert 'answer' not in c.predict(q,k)
    assert not s.calls
    s.predict=lambda *a:{'answer':'NEVER_RETURN','checkpoint':BASE_REVISION,'actual_selection_proof':{'enabled':True,'active_adapters':['D1500']}}
    assert 'answer' not in c.predict('Synthetic','base')
    c.close();assert s.closed and 'answer' not in c.predict('Synthetic','base')

def test_remote_release_does_not_promote_private_test_runtime():
    s=Session();c=MeetingController(s)
    review=ReleaseReview('review-test',BUNDLE_SHA256,('supervisor',),time.time()+600,True,True,True,True)
    with pytest.raises(ValueError,match='Private-test'):c.verify_remote(review,'supervisor')
    s._engine=SimpleNamespace(manifest={'public_generation_approved':True,'meeting_release_review_id':'review-test'})
    c.verify_remote(review,'supervisor')
    with pytest.raises(ValueError):c.verify_remote(review,'stranger')
    with pytest.raises(ValueError):ReleaseReview('review-test',BUNDLE_SHA256,('supervisor',),time.time()+600).verify('supervisor')

def test_http_login_expiry_file_access_and_no_secret_in_configuration(tmp_path):
    c=MeetingController();password='synthetic-login-password-for-test-only'
    app=create_http_app(c,'supervisor',password,private_roots=[tmp_path])
    with TestClient(app) as client:
        assert client.get('/config').status_code==401
        assert client.post('/login',data={'username':'supervisor','password':'wrong'}).status_code==400
        assert client.post('/login',data={'username':'supervisor','password':password}).status_code==200
        config=client.get('/config');assert config.status_code==200 and password not in config.text
        assert config.headers['cache-control']=='no-store'
        p=tmp_path/'restricted.txt';p.write_text('RESTRICTED_TEST_MARKER')
        response=client.get('/gradio_api/file='+str(p))
        assert response.status_code in (403,404) and 'RESTRICTED_TEST_MARKER' not in response.text
        c.expires_at=time.time()-1
        assert client.get('/config').status_code==403

def test_ui_unavailable_and_login_rate_limit():
    c=MeetingController();ui=create_ui(c)
    buttons=[b for b in ui.config['components'] if b['type']=='button']
    assert any(b['props']['value']=='Generate Answer' and b['props']['interactive'] is False for b in buttons)
    app=create_http_app(c,'supervisor','synthetic-password-at-least-thirty-two-characters')
    with TestClient(app) as client:
        for _ in range(5):client.post('/login',data={'username':'bad','password':'bad'})
        assert client.post('/login',data={'username':'bad','password':'bad'}).status_code==429
        assert client.post('/login',content='x'*20001).status_code in (413,429)

def test_real_browser_runtime_requires_review_and_protected_roots(tmp_path):
    s=Session();expiry=time.time()+600;c=MeetingController(s,expires_at=expiry)
    with pytest.raises(ValueError,match='explicit release'):create_http_app(c,'reviewer','x'*40)
    s._engine=SimpleNamespace(manifest={'public_generation_approved':True,'meeting_release_review_id':'fixture',
       'asset_root':str(tmp_path/'assets'),'research_root':str(tmp_path/'code')})
    review=ReleaseReview('fixture',BUNDLE_SHA256,('reviewer',),expiry,True,True,True,True)
    with pytest.raises(ValueError,match='blocked'):create_http_app(c,'reviewer','x'*40,remote_review=review)
    app=create_http_app(c,'reviewer','x'*40,remote_review=review,private_roots=[tmp_path])
    with TestClient(app) as client:
        body={'data':['Synthetic fixture question','D1000'],'fn_index':1}
        assert client.post('/gradio_api/run/predict',json=body).status_code==401
        client.post('/login',data={'username':'reviewer','password':'x'*40})
        response=client.post('/gradio_api/run/predict',json=body)
        assert response.status_code==200
        assert 'SYNTHETIC UNIT TEST ONLY' in response.text
        assert ADAPTERS['D1000']['sha256'] in response.text
        assert 'RESTRICTED_TEST_MARKER' not in response.text
    c.close()
