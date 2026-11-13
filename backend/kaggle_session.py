"""Prepared supervised notebook route. No public listener, tunnel or paid service.

No GPU is started by importing this module. Real preparation requires explicit
free-GPU approval, confirmed quota and the private Kaggle environment.
"""
import json
import os
from pathlib import Path
import secrets
import threading
import time
from backend.api import create_app,Quota

class NotebookSession:
    def __init__(self,engine,working,ttl_seconds=2700):
        from fastapi.testclient import TestClient
        self._engine=engine
        self._lock=threading.Lock();self._stopping=False;self._closed=False
        self.deadline=time.time()+ttl_seconds
        self._token=secrets.token_urlsafe(40)
        self._app=create_app(engine=engine,token=self._token,
            quota=Quota(Path(working)/'meeting-quota.sqlite3',limit=12,rpm=3),expires_at=self.deadline)
        # In-process authenticated ASGI: there is no externally reachable port.
        self._client=TestClient(self._app)
        self._timer=threading.Timer(ttl_seconds,self.close);self._timer.daemon=True;self._timer.start()

    def predict(self,question,condition):
        if self._stopping:raise RuntimeError('Meeting session ended')
        with self._lock:
            if self._stopping or time.time()>=self.deadline:raise RuntimeError('Meeting session ended')
            original=None;proof=[]
            if hasattr(self._engine,'core'):
                from backend.smoke_validation import validate_selection
                original=self._engine.core.generate
                def observed(model,*args,**kwargs):
                    state=model.get_model_status()
                    validate_selection(condition,state.enabled,state.active_adapters)
                    proof.append({'enabled':state.enabled,'active_adapters':list(state.active_adapters)})
                    return original(model,*args,**kwargs)
                self._engine.core.generate=observed
            import sys
            torch=sys.modules.get('torch')
            measured=bool(torch is not None and torch.cuda.is_available())
            if measured:
                torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats()
            try:
                response=self._client.post('/generate',headers={'Authorization':'Bearer '+self._token},
                    json={'question':question,'model_config':condition,'use_rag':False})
                value=response.json()
                if response.status_code!=200:
                    return {'error':{'code':'notebook_request_failed','message':'Request rejected, unavailable or quota reached.'}}
                if measured:
                    torch.cuda.synchronize()
                    value['gpu_measurements']={'peak_allocated_bytes':torch.cuda.max_memory_allocated(),
                        'peak_reserved_bytes':torch.cuda.max_memory_reserved(),
                        'total_bytes':torch.cuda.get_device_properties(0).total_memory}
                value['actual_selection_proof']=proof[-1] if proof else None
                return value
            finally:
                if original is not None:self._engine.core.generate=original

    def close(self):
        self._stopping=True
        self._timer.cancel()
        # Let an active request finish; never delete weights beneath generation.
        with self._lock:
            if self._closed:return
            self._closed=True
            client,app=self._client,self._app
            app.state.engine=None;client.close()
            self._client=None;self._app=None;self._engine=None;self._token=None
            del client,app
            import gc,sys
            gc.collect()
            torch=sys.modules.get('torch')
            if torch is not None and torch.cuda.is_available():torch.cuda.empty_cache()
        # Releasing weights does NOT stop the Kaggle VM/quota clock: operator must Stop Session.


def prepare_private_notebook():
    if os.environ.get('FREE_KAGGLE_SERVING_APPROVED')!='yes' or os.environ.get('FREE_KAGGLE_QUOTA_CONFIRMED')!='yes':
        raise RuntimeError('No activation: explicit free-GPU approval and confirmed free quota required')
    home=Path('/kaggle')/'working'
    if not home.is_dir():raise RuntimeError('Private Kaggle notebook required; no local model execution')
    from backend.artifact_transfer import verify_private_kernel
    verify_private_kernel(os.environ['MEETING_NOTEBOOK_KERNEL'])
    from kaggle import api
    from kagglesdk.kernels.types.kernels_api_service import ApiGetAcceleratorQuotaStatisticsRequest
    with api.build_kaggle_client() as client:
        quota=client.kernels.kernels_api_client.get_accelerator_quota_statistics(ApiGetAcceleratorQuotaStatisticsRequest()).gpu_quota
    if quota.is_pay_to_scale_enabled or quota.total_time_allowed<=quota.time_used:
        raise RuntimeError('Free allocation not established; no paid fallback')
    os.environ['CUDA_VISIBLE_DEVICES']='0'
    import torch
    if not torch.cuda.is_available():raise RuntimeError('Free GPU unavailable; no paid fallback')
    from backend.artifact_transfer import download_private_source,extract_verified_bundle
    import contextlib,tempfile
    work=home/'supervised-insurance-demo';work.mkdir(mode=0o700,exist_ok=False)
    with open(os.devnull,'w') as sink,contextlib.redirect_stdout(sink),contextlib.redirect_stderr(sink):
        with tempfile.TemporaryDirectory() as tmp:
            archive=Path(tmp)/'bundle.tar.gz';download_private_source(archive)
            extract_verified_bundle(archive,work/'bundle')
        manifest=json.loads((work/'bundle/serving-manifest.json').read_text())
        manifest['research_root']=str(work/'bundle/research-code')
        manifest['asset_root']=str(work/'bundle/assets')
        manifest['retrieval']=None  # Explicitly no RAG, no embeddings, no reranker load.
        from backend.runtime import ResearchRuntime
        started=time.monotonic()
        runtime=ResearchRuntime(manifest,private_test=True)
        cold_load=time.monotonic()-started
    session=NotebookSession(runtime,work)
    session.cold_load_seconds=cold_load
    return session


def show_notebook_controls(session):
    """Private notebook widgets only. Never exports a public link or bearer token."""
    import html
    import ipywidgets as widgets
    from IPython.display import display,HTML,clear_output
    selection=widgets.Dropdown(options=['base','D1000','D1500'],description='Condition:')
    question=widgets.Textarea(value='What conditions apply to getting a courtesy car under this motor policy?',
        description='Question:',layout=widgets.Layout(width='95%',height='90px'))
    generate=widgets.Button(description='Generate new answer',button_style='primary')
    stop=widgets.Button(description='Release models',button_style='warning')
    output=widgets.Output()
    def clicked(_):
        generate.disabled=True
        with output:
            clear_output(wait=True)
            try:
                value=session.predict(question.value,selection.value)
                if value.get('error'):print(value['error']['message'])
                else:
                    display(HTML('<p>'+html.escape(value['answer'])+'</p>'))
                    display(HTML('<small>Checkpoint: '+html.escape(str(value['checkpoint']))+
                        ' | RAG: disabled | Latency: '+str(round(value['latency_seconds'],2))+'s</small>'))
                    print('Actual adapter state:',value.get('actual_selection_proof'))
                    print('GPU measurements:',value.get('gpu_measurements'))
            except Exception:print('Private inference unavailable; no substitute answer.')
        generate.disabled=session._stopping
    def stopped(_):
        session.close();generate.disabled=True
        with output:print('Models released. Use Kaggle Stop Session now to stop the GPU quota clock.')
    generate.on_click(clicked);stop.on_click(stopped)
    display(widgets.VBox([widgets.HTML('<b>Private meeting-only live inference. RAG disabled. No personal details.</b>'),
                          selection,question,widgets.HBox([generate,stop]),output]))
