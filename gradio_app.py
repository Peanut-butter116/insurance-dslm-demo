"""Single-page meeting UI. Default: authenticated loopback preview, no model or tunnel."""
import os
os.environ['GRADIO_ANALYTICS_ENABLED']='False'
import hmac
import time
from pathlib import Path
import gradio as gr
from fastapi import FastAPI
from starlette.responses import JSONResponse
from backend.meeting import MeetingController
from example_questions import EXAMPLES
from config.model_registry import BASE_MODEL,BASE_REVISION

CSS='''
.gradio-container, .dark .gradio-container {
 max-width:1080px!important;background:white;color:#18222e;color-scheme:light;
 --body-background-fill:white;--body-text-color:#18222e;--body-text-color-subdued:#526070;
 --block-background-fill:white;--block-label-text-color:#18222e;--block-title-text-color:#18222e;
 --input-background-fill:#f8fafc;--input-text-color:#18222e;
 --background-fill-primary:white;--background-fill-secondary:#f3f5f8;
 --border-color-primary:#dce1e7;--border-color-accent:#c3cbd6;
 --button-secondary-background-fill:#f3f5f8;--button-secondary-text-color:#18222e;
 --button-secondary-background-fill-hover:#e6eaf0;
}
#heading {border-bottom:1px solid #e6e9ed;padding-bottom:16px;margin-bottom:16px}
.gradio-container .label-wrap {color:#18222e!important}
footer {display:none!important}
'''

def create_ui(controller, *, gpu_decorator=None):
    with gr.Blocks(title='UK Motor Insurance — Small Language Model Research Demo',analytics_enabled=False) as demo:
        gr.Markdown('# UK Motor Insurance — Small Language Model Research Demo\nTech Mahindra Makers Lab | Policy-Grounded Question Answering',elem_id='heading')
        gr.Markdown('Supervised meeting access. Do not enter personal details. Outputs are screened; screening cannot guarantee absence of restricted wording.')
        with gr.Row():
            with gr.Column(scale=1):
                condition=gr.Radio([('Base','base'),('D1000 SFT · 751 training rows','D1000'),('D1500 SFT · 1,221 training rows','D1500')],value='base',label='Model configuration')
                gr.Checkbox(value=False,interactive=False,label='RAG unavailable — original retrieval runtime missing')
                gr.Markdown('D500 unavailable: no verified checkpoint.\n\nDataset labels identify source experiments, not training-row counts.')
                with gr.Accordion('Base model',open=False):gr.Markdown(f'{BASE_MODEL}\n\nRevision: `{BASE_REVISION}`')
            with gr.Column(scale=3):
                preset=gr.Dropdown(list(EXAMPLES),value='Custom question',label='Example question')
                question=gr.Textbox(label='Your question',max_length=4000,lines=3,max_lines=6,placeholder='Ask a UK motor insurance policy question…')
                button=gr.Button('Generate Answer',variant='primary',interactive=controller.session is not None)
                status=gr.Textbox(label='Serving status',interactive=False,value='Inference temporarily unavailable until a verified GPU backend is activated.' if controller.session is None else 'Ready for a new model response. RAG disabled.')
                answer=gr.Textbox(label='Model answer',lines=7,interactive=False,buttons=['copy'])
                checkpoint=gr.Textbox(label='Actual checkpoint identity',interactive=False)
                with gr.Row():
                    refusal=gr.Textbox(label='Refusal status',interactive=False)
                    latency=gr.Number(value=None,label='Generation latency (seconds)',interactive=False)
                with gr.Accordion('Adapter and GPU diagnostics',open=False):details=gr.JSON(label='Measured runtime details')
        def choose(name):return EXAMPLES.get(name,'')
        preset.change(choose,preset,question,api_name=None,api_visibility="private",queue=False)
        def generate(q,c):
            r=controller.predict(q,c)
            refused=r.get('refused')
            return (r['status'],r.get('answer',''),r.get('checkpoint',''),
                    'Refused' if refused is True else 'Not refused' if refused is False else 'Not measured',
                    r.get('latency_seconds'),{'condition':r.get('condition'),'actual_selection':r.get('selection'),'gpu_bytes':r.get('gpu')})
        if gpu_decorator is not None:
            generate=gpu_decorator(generate)
        button.click(generate,[question,condition],[status,answer,checkpoint,refusal,latency,details],
                     api_name=None,api_visibility="private",concurrency_limit=1,concurrency_id='shared-model')
    demo.queue(max_size=2,default_concurrency_limit=1)
    return demo


def create_http_app(controller,username,password,*,remote_review=None,private_roots=()):
    if not username or len(password)<32:raise ValueError('A named meeting login and password of at least 32 characters are required')
    if controller.session is not None and remote_review is None:
        raise ValueError('Real model browser access requires an explicit release review')
    if remote_review is not None:
        controller.verify_remote(remote_review,username)
        if controller.expires_at > remote_review.expires_at:
            raise ValueError('Session must expire no later than its release approval')
        manifest=controller.session._engine.manifest
        roots=[Path(p).resolve() for p in private_roots]
        for key in ('asset_root','research_root'):
            path=Path(manifest[key]).resolve()
            if not any(path==root or root in path.parents for root in roots):
                raise ValueError('Private asset and research roots must be blocked from file serving')
    if os.environ.get('GRADIO_ALLOWED_PATHS'):raise ValueError('File-serving environment override is not allowed')
    app=FastAPI(docs_url=None,redoc_url=None,openapi_url=None)
    login_attempts=[]
    @app.middleware('http')
    async def boundaries(request,call_next):
        if controller.closed or time.time()>=controller.expires_at:
            return JSONResponse({'detail':'Meeting session ended'},status_code=403)
        if request.url.path.endswith('/login') and request.method=='POST':
            now=time.time()
            if len(login_attempts)>=30 or sum(t>now-60 for t in login_attempts)>=5:
                return JSONResponse({'detail':'Login limit reached'},status_code=429)
            login_attempts.append(now)
        if request.method=='POST':
            data=bytearray()
            async for part in request.stream():
                data.extend(part)
                if len(data)>20000:return JSONResponse({'detail':'Request too large'},status_code=413)
            request._body=bytes(data)
        response=await call_next(request)
        response.headers['Cache-Control']='no-store'
        response.headers['Referrer-Policy']='no-referrer'
        response.headers['X-Content-Type-Options']='nosniff'
        return response
    def authenticate(user,secret):
        return (not controller.closed and time.time()<controller.expires_at
                and hmac.compare_digest(str(user),username) and hmac.compare_digest(str(secret),password))
    blocked=[str(Path.cwd().resolve()),str(Path.home().resolve()),*[str(Path(p).resolve()) for p in private_roots]]
    return gr.mount_gradio_app(app,create_ui(controller),path='/',auth=authenticate,
        allowed_paths=[],blocked_paths=blocked,max_file_size=1,show_error=False,
        css=CSS,theme=gr.themes.Base(),footer_links=[])


def main():
    import uvicorn
    # This preview never loads research assets. Explicit loopback binding; no Gradio
    # launch/share call, automatic share detection, forwarding or public deployment.
    app=create_http_app(MeetingController(),os.environ.get('MEETING_USERNAME',''),os.environ.get('MEETING_PASSWORD',''))
    uvicorn.run(app,host='127.0.0.1',port=7860,access_log=False,log_level='critical')

if __name__=='__main__':main()
