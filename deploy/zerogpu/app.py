"""PRIVATE SPACE, AGGREGATES-ONLY SMOKE TEMPLATE. Not a public deployment script."""
import os
if os.environ.get('ZEROGPU_SMOKE_APPROVED')!='yes' or os.environ.get('SPACES_ZERO_GPU')!='1':
    raise RuntimeError('Separate approval and private ZeroGPU environment required')
import spaces  # FIRST before any torch/transformers/PEFT/CUDA-touching library.
import json,time,contextlib
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download
from backend.hf_delivery import DeliveryPlan,download_private_hf_bundle,verify_scoped_token
from backend.zerogpu_runtime import prepare_runtime
from backend.zerogpu_smoke import BoundedSmoke,verify_free_quota,DURATION_SECONDS

# No creation API, hardware request, upload, public share call or paid fallback.
plan=DeliveryPlan(os.environ['PRIVATE_HF_NAMESPACE']);plan.validate()
if os.environ.get('SPACE_ID')!=plan.space_repo:raise RuntimeError('Approved Space identity differs')
token=os.environ['HF_BUNDLE_READ_TOKEN']
api=HfApi(token=token)
verify_scoped_token(api,token,namespace=plan.namespace,repositories=[plan.artifact_repo,plan.space_repo])
if api.space_info(plan.space_repo).private is not True:raise RuntimeError('Private Space required')
expires=float(os.environ['SMOKE_EXPIRES_AT'])
if not time.time()<expires<=time.time()+1800:raise RuntimeError('Finite smoke expiry required')
work=Path('/tmp')/'insurance-private-zerogpu'
work.mkdir(mode=0o700,exist_ok=True)
startup_phase='artifact_readback'
try:
    with open(os.devnull,'w') as sink,contextlib.redirect_stdout(sink),contextlib.redirect_stderr(sink):
        download_private_hf_bundle(plan,os.environ['PRIVATE_BUNDLE_REVISION'],work/'bundle',token=token,api=api,download=hf_hub_download)
        manifest=json.loads((work/'bundle/serving-manifest.json').read_text())
        manifest.update(asset_root=str(work/'bundle/assets'),research_root=str(work/'bundle/research-code'),retrieval=None)
        # Does NOT enable remote answers or alter the bundle release flag.
        os.environ['ZEROGPU_STARTUP_APPROVED']='yes'
        startup_phase='original_runtime_emulation_load'
        runtime=prepare_runtime(manifest,smoke_only=True)  # Eager load under emulation at startup.
except Exception as error:
    import traceback
    diagnostic={'schema':'private-zerogpu-startup/1','phase':startup_phase,
        'error_type':type(error).__name__,
        'frames':[{'function':f.name,'line':f.lineno} for f in traceback.extract_tb(error.__traceback__)[-8:]],
        'gpu_requests':0,'raw_answers_returned':False}
    print(json.dumps(diagnostic))
    raise RuntimeError('Private artifact or emulated model startup failed; no fallback') from None
smoke=BoundedSmoke(runtime,work/'smoke.sqlite3',expires)

@spaces.GPU(duration=DURATION_SECONDS,size='large')
def generate_smoke(reservation):
    # Directly registered event handler, not a hidden decorated inner helper.
    with open(os.devnull,'w') as sink,contextlib.redirect_stdout(sink),contextlib.redirect_stderr(sink):
        try:return smoke.predict(reservation)
        except Exception:return {'status':'blocked','raw_answers_returned':False}

# Named meeting login is required IN ADDITION to the Private Space access layer.
import gradio as gr
from gradio_app import CSS
user=os.environ['MEETING_USERNAME'];password=os.environ['MEETING_PASSWORD']
if len(password)<32:raise RuntimeError('Strong named login required')
with gr.Blocks(title='Private ZeroGPU compatibility smoke',analytics_enabled=False) as demo:
    gr.Markdown('# UK Motor Insurance — Private ZeroGPU Compatibility Test\nThree bounded cases. No generated answer text is released.')
    condition=gr.Radio(['base','D1000','D1500'],value='base',label='Next condition (in this exact order)')
    button=gr.Button('Run one approved smoke case')
    output=gr.JSON(label='Safe technical receipt only')
    reservation=gr.State()
    quota_receipt=gr.JSON(value=None,label='Fresh free-quota receipt (technical operator only)')
    def reserve_cpu(selected,quota):
        try:return smoke.reserve(selected,quota)
        except Exception:raise gr.Error('Test expired, blocked or already attempted. No retry.') from None
    event=button.click(reserve_cpu,[condition,quota_receipt],reservation,concurrency_limit=1,api_name='reserve_smoke',api_visibility='undocumented')
    event.success(generate_smoke,reservation,output,concurrency_limit=1,api_name='generate_smoke',api_visibility='undocumented')
demo.queue(max_size=1,default_concurrency_limit=1)
# Explicit share=False: Spaces provides its own access-controlled HTTPS, no tunnel.
# This file is NEVER executed locally or uploaded without separate owner approval.
if __name__=='__main__':
    import hmac
    def auth(u,p):return time.time()<expires and hmac.compare_digest(u.encode(),user.encode()) and hmac.compare_digest(p.encode(),password.encode())
    demo.launch(share=False,auth=auth,show_error=False,allowed_paths=[],blocked_paths=[str(work),str(Path.home())],
        css=CSS,theme=gr.themes.Base(),footer_links=[],max_file_size=1)
