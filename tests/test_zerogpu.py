import sys,time
from types import SimpleNamespace
import pytest
from backend.zerogpu_runtime import load_original_nf4,prepare_runtime
from backend.zerogpu_smoke import BoundedSmoke,verify_free_quota
from backend.hf_delivery import DeliveryPlan,verify_transfer_approval,download_private_hf_bundle
from config.model_registry import BASE_MODEL,BASE_REVISION


def fresh_quota(remaining=300):
    return {'free_account_verified':True,'no_paid_extension':True,'overquota_used':0,'checked_at':time.time(),'remaining':remaining}


def test_symbolic_nf4_loader_preserves_original_contract(monkeypatch):
    calls={};dtype=SimpleNamespace()
    dtype.__str__=lambda:'torch.bfloat16'
    class Dtype:
        def __str__(self):return 'torch.bfloat16'
    bf=Dtype()
    monkeypatch.setitem(sys.modules,'torch',SimpleNamespace(cuda=SimpleNamespace(is_available=lambda:True,is_bf16_supported=lambda:True),bfloat16=bf,float16='fp16'))
    def quant(**kw):calls['quant']=kw;return kw
    cfg=SimpleNamespace(quantization_config={'bnb_4bit_compute_dtype':'float16'})
    class Model:
        @staticmethod
        def from_pretrained(*a,**kw):calls['load']=(a,kw);return SimpleNamespace(is_loaded_in_4bit=True)
    monkeypatch.setitem(sys.modules,'transformers',SimpleNamespace(AutoConfig=SimpleNamespace(from_pretrained=lambda *a,**kw:cfg),
        AutoModelForCausalLM=Model,Mistral3ForConditionalGeneration=Model,BitsAndBytesConfig=quant))
    tok=SimpleNamespace(pad_token_id=None,eos_token='end')
    core=SimpleNamespace(config=lambda:{'models':{'ministral3b':{'id':BASE_MODEL,'revision':BASE_REVISION,'class':'mistral3'}}},load_tokenizer=lambda key:tok)
    _,t=load_original_nf4(core,'ministral3b')
    assert calls['quant']==dict(load_in_4bit=True,bnb_4bit_quant_type='nf4',bnb_4bit_use_double_quant=True,bnb_4bit_compute_dtype=bf)
    a,kw=calls['load'];assert a==(BASE_MODEL,) and kw['revision']==BASE_REVISION and kw['device_map']=='cuda'
    assert kw['attn_implementation']=='sdpa' and t.pad_token=='end'
    assert cfg.quantization_config['bnb_4bit_compute_dtype']=='bfloat16'


def test_unapproved_startup_never_imports_gpu_libraries(monkeypatch):
    monkeypatch.delenv('ZEROGPU_STARTUP_APPROVED',raising=False)
    with pytest.raises(RuntimeError,match='approval|Approved'):prepare_runtime({})


def test_exact_delivery_approval_and_private_download_gate(tmp_path,monkeypatch):
    plan=DeliveryPlan('synthetic-owner')
    monkeypatch.setenv('SPACE_ID',plan.space_repo)
    with pytest.raises(ValueError):verify_transfer_approval(plan,{})
    approval={'plan':plan.approval_payload(),'owner_transfer_approved':True,'narrow_upload_token_verified':True,'free_storage_verified':True}
    verify_transfer_approval(plan,approval)
    approval['plan']['private']=False
    with pytest.raises(ValueError):verify_transfer_approval(plan,approval)
    class PublicAPI:
        def repo_info(self,**kw):return SimpleNamespace(private=False,author=plan.namespace,sha='a'*40)
    def forbidden(**kw):raise AssertionError('Public repo must never be downloaded')
    with pytest.raises(ValueError,match='identity'):download_private_hf_bundle(plan,'a'*40,tmp_path/'unused',token='synthetic',api=PublicAPI(),download=forbidden)
    with pytest.raises(ValueError,match='Immutable'):download_private_hf_bundle(plan,'main',tmp_path/'unused',token='synthetic',api=PublicAPI(),download=forbidden)


def test_fresh_free_quota_requires_margin_and_no_paid_extension():
    q={'free_account_verified':True,'no_paid_extension':True,'overquota_used':0,'checked_at':time.time(),'remaining':240}
    verify_free_quota(q)
    for override in [{'remaining':239},{'checked_at':time.time()-301},{'overquota_used':1},{'free_account_verified':False}]:
        with pytest.raises(ValueError):verify_free_quota({**q,**override})


def test_smoke_worker_forks_use_single_use_reservations_and_no_answer_output(tmp_path,monkeypatch):
    import backend.zerogpu_runtime as zr
    calls=[]
    def measured(runtime,q,key):
        calls.append(key)
        return {'answer':'SYNTHETIC OUTPUT NOT TO EXPORT','checkpoint':key,'actual_selection_proof':{'enabled':key!='base','active_adapters':[key]},
          'gpu_measurements':{'total_bytes':1000},'allocation_diagnostics':{'loaded_in_4bit':True},'latency_seconds':1,'final_answer_present':True,'refused':False}
    monkeypatch.setattr(zr,'measure_prediction',measured)
    journal=tmp_path/'receipt.sqlite3';s=BoundedSmoke(object(),journal,time.time()+600)
    with pytest.raises(ValueError):s.reserve('D1000',fresh_quota())
    for key in ('base','D1000','D1500'):
        reservation=s.reserve(key,fresh_quota())
        with pytest.raises(ValueError):s.reserve(key,fresh_quota())
        # A fresh Python object represents the separate worker process, sharing disk only.
        worker=BoundedSmoke(object(),journal,s.expires_at)
        row=worker.predict(reservation)
        assert row['status']=='passed' and row['raw_answers_returned'] is False
        assert 'SYNTHETIC OUTPUT' not in str(row) and 'answer' not in row
        with pytest.raises(ValueError):worker.predict(reservation)
    assert calls==['base','D1000','D1500']


def test_failed_or_unknown_case_cannot_be_replayed(tmp_path,monkeypatch):
    import backend.zerogpu_runtime as zr
    s=BoundedSmoke(object(),tmp_path/'receipt.sqlite3',time.time()+600)
    def failed(*a):raise RuntimeError('SYNTHETIC_SECRET_MARKER')
    monkeypatch.setattr(zr,'measure_prediction',failed)
    row=s.predict(s.reserve('base',fresh_quota()));assert row['status']=='failed' and 'SYNTHETIC_SECRET' not in str(row)
    with pytest.raises(ValueError):s.reserve('D1000',fresh_quota())
    with pytest.raises(ValueError):s.reserve('base',fresh_quota())

def test_unapproved_transfer_performs_no_remote_call(tmp_path):
    from backend.hf_delivery import upload_verified_cloud_bundle
    class ForbiddenAPI:
        def __getattr__(self,name):raise AssertionError('No service access without approval')
    with pytest.raises(ValueError,match='approval'):
        upload_verified_cloud_bundle(DeliveryPlan('synthetic-owner'),{},tmp_path/'absent',token='synthetic',api=ForbiddenAPI())


def test_staged_source_is_code_only_and_decorator_is_direct(tmp_path):
    from scripts.build_zerogpu_source import build
    from gradio_app import create_ui
    from backend.meeting import MeetingController
    inventory=build(tmp_path/'source')
    assert not any(p.endswith(('.safetensors','.tar.gz','.jsonl','.sqlite3')) for p in inventory)
    code=(tmp_path/'source/app.py').read_text()
    assert 'ZEROGPU_SMOKE_APPROVED' in code and 'share=False' in code
    assert '@spaces.GPU(duration=DURATION_SECONDS' in code
    pins=(tmp_path/'source/requirements.txt').read_text()
    assert 'torchvision==0.26.0+cu128' in pins and 'torchaudio==2.11.0+cu128' in pins
    marked=[]
    def decorator(fn):marked.append(fn);fn.synthetic_gpu_marker=True;return fn
    ui=create_ui(MeetingController(),gpu_decorator=decorator)
    assert len(marked)==1 and any(getattr(f.fn,'synthetic_gpu_marker',False) for f in ui.fns.values())

def test_actual_nf4_metadata_gate_rejects_other_quantisation():
    from backend.zerogpu_runtime import nf4_state_proof
    state=SimpleNamespace(quant_type='nf4',state2=object())
    model=SimpleNamespace(is_loaded_in_4bit=True,parameters=lambda:iter([SimpleNamespace(quant_state=state)]))
    assert nf4_state_proof(model)['double_quant'] is True
    state.quant_type='fp4'
    with pytest.raises(ValueError):nf4_state_proof(model)
    state.quant_type='nf4';state.state2=None
    with pytest.raises(ValueError):nf4_state_proof(model)

def test_hosted_upload_checks_acl_and_binds_parent_commit(tmp_path,monkeypatch):
    import backend.hf_delivery as delivery
    import backend.artifact_transfer as artifacts
    from pathlib import Path
    original_is_dir=Path.is_dir
    monkeypatch.setattr(Path,'is_dir',lambda p:True if str(p)=='/kaggle/working' else original_is_dir(p))
    monkeypatch.setattr(delivery,'BUNDLE_BYTES',1)
    monkeypatch.setattr(artifacts,'file_sha',lambda p:delivery.BUNDLE_SHA256)
    monkeypatch.setattr(artifacts,'extract_verified_bundle',lambda *a,**k:None)
    archive=tmp_path/'synthetic-only.tar.gz';archive.write_bytes(b'x')
    plan=DeliveryPlan('synthetic-owner',bundle_bytes=1)
    approval={'plan':plan.approval_payload(),'owner_transfer_approved':True,'narrow_upload_token_verified':True,'free_storage_verified':True}
    class API:
        private=False
        def repo_info(self,**kw):return SimpleNamespace(private=self.private,author=plan.namespace,sha='a'*40)
        def upload_file(self,**kw):self.upload=kw;return SimpleNamespace(oid='b'*40)
    api=API()
    with pytest.raises(ValueError,match='privacy'):delivery.upload_verified_cloud_bundle(plan,approval,archive,token='synthetic',api=api)
    assert not hasattr(api,'upload')
    api.private=True
    result=delivery.upload_verified_cloud_bundle(plan,approval,archive,token='synthetic',api=api)
    assert result['revision']=='b'*40 and api.upload['parent_commit']=='a'*40
    assert api.upload['repo_id']==plan.artifact_repo and api.upload['path_in_repo']=='private-serving-bundle.tar.gz'

def test_quota_is_fresh_before_each_reservation_and_scales_with_remaining_cases(tmp_path,monkeypatch):
    import backend.zerogpu_runtime as zr
    s=BoundedSmoke(object(),tmp_path/'bounded.sqlite3',time.time()+600)
    monkeypatch.setattr(zr,'measure_prediction',lambda *a:{'answer':'SYNTHETIC','actual_selection_proof':{},
       'gpu_measurements':{},'allocation_diagnostics':{},'final_answer_present':True})
    with pytest.raises(ValueError):s.reserve('base',fresh_quota(239))
    for key,remaining in [('base',240),('D1000',180),('D1500',120)]:
        stale={**fresh_quota(remaining),'checked_at':time.time()-301}
        with pytest.raises(ValueError):s.reserve(key,stale)
        row=s.predict(s.reserve(key,fresh_quota(remaining)))
        assert row['status']=='passed'

def test_runtime_token_must_be_read_only_and_exactly_resource_scoped():
    from backend.hf_delivery import verify_scoped_token
    model='synthetic-owner/insurance-slm-private-serving';space='synthetic-owner/insurance-slm-private-meeting'
    meta={'name':'synthetic-owner','auth':{'accessToken':{'role':'fineGrained','fineGrained':{'global':[],
       'scoped':[{'entity':{'name':repo},'permissions':['repo.content.read']} for repo in [model,space]]}}}}
    api=SimpleNamespace(whoami=lambda **k:meta)
    assert verify_scoped_token(api,'synthetic',namespace='synthetic-owner',repositories=[model,space])
    meta['auth']['accessToken']['fineGrained']['scoped'][0]['permissions'].append('repo.content.write')
    with pytest.raises(ValueError):verify_scoped_token(api,'synthetic',namespace='synthetic-owner',repositories=[model,space])

def test_authenticated_cpu_reservation_state_carries_to_separate_worker_call(tmp_path,monkeypatch):
    import gradio as gr
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    import backend.zerogpu_runtime as zr
    monkeypatch.setattr(zr,'measure_prediction',lambda *a:{'answer':'SYNTHETIC_PRIVATE_MARKER','actual_selection_proof':{},
       'gpu_measurements':{},'allocation_diagnostics':{},'final_answer_present':True})
    smoke=BoundedSmoke(object(),tmp_path/'state.sqlite3',time.time()+600)
    with gr.Blocks(analytics_enabled=False) as demo:
        cond=gr.Textbox();quota=gr.JSON();state=gr.State();out=gr.JSON();button=gr.Button()
        event=button.click(smoke.reserve,[cond,quota],state,api_name='reserve_smoke',api_visibility='undocumented')
        event.success(smoke.predict,state,out,api_name='generate_smoke',api_visibility='undocumented')
    app=gr.mount_gradio_app(FastAPI(),demo,path='/',auth=('synthetic-owner','x'*40),show_error=False)
    with TestClient(app) as client:
        assert client.post('/gradio_api/run/predict',json={'fn_index':0,'data':['base',fresh_quota()],'session_hash':'fixture'}).status_code==401
        client.post('/login',data={'username':'synthetic-owner','password':'x'*40})
        reserved=client.post('/gradio_api/run/predict',json={'fn_index':0,'data':['base',fresh_quota()],'session_hash':'fixture'})
        assert reserved.status_code==200
        result=client.post('/gradio_api/run/predict',json={'fn_index':1,'data':[None],'session_hash':'fixture'})
        assert result.status_code==200 and result.json()['data'][0]['status']=='passed'
        assert 'SYNTHETIC_PRIVATE_MARKER' not in result.text

def test_hf_permission_schema_ignores_empty_owner_context_but_rejects_owner_grants():
    from backend.hf_delivery import verify_scoped_token
    repo='synthetic-owner/insurance-slm-private-serving'
    fine={'global':[],'scoped':[{'entity':{'name':repo,'type':'model'},'permissions':['repo.access.read','repo.content.read','repo.write']},
          {'entity':{'name':'synthetic-owner','type':'user'},'permissions':[]}]}
    meta={'name':'synthetic-owner','auth':{'accessToken':{'role':'fineGrained','fineGrained':fine}}}
    api=SimpleNamespace(whoami=lambda **k:meta)
    assert verify_scoped_token(api,'synthetic',namespace='synthetic-owner',repositories=[repo],write=True)
    with pytest.raises(ValueError):verify_scoped_token(api,'synthetic',namespace='synthetic-owner',repositories=[repo],write=False)
    fine['scoped'][1]['permissions']=['repo.write']
    with pytest.raises(ValueError):verify_scoped_token(api,'synthetic',namespace='synthetic-owner',repositories=[repo],write=True)

def test_platform_pin_syntax_preserves_exact_cuda_build():
    from backend.zerogpu_runtime import require_original_torch_build
    from packaging.specifiers import SpecifierSet
    from pathlib import Path
    assert SpecifierSet('==2.11.0').contains('2.11.0+cu128')
    pins=(Path(__file__).parents[1]/'deploy/zerogpu/requirements.txt').read_text()
    constraints=(Path(__file__).parents[1]/'deploy/zerogpu/constraints.txt').read_text()
    assert '\ntorch==2.11.0\n' in pins and '-c constraints.txt' in pins
    assert 'torch==2.11.0+cu128' in constraints
    require_original_torch_build(SimpleNamespace(__version__='2.11.0+cu128',version=SimpleNamespace(cuda='12.8')))
    with pytest.raises(RuntimeError):require_original_torch_build(SimpleNamespace(__version__='2.11.0+cu130',version=SimpleNamespace(cuda='13.0')))
