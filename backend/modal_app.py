"""PREPARED ONLY. Importing this file never deploys or starts a GPU.

After explicit owner approval: modal deploy backend/modal_app.py
Private assets must already be on the operator's access-controlled Modal Volume.
"""
import modal

app = modal.App('insurance-slm-meeting-demo')
image = (modal.Image.debian_slim(python_version='3.11')
    .pip_install('torch==2.11.0', 'torchvision==0.26.0', 'torchaudio==2.11.0', extra_index_url='https://download.pytorch.org/whl/cu128')
    .pip_install('transformers==5.19.0', 'peft==0.21.2', 'bitsandbytes==0.50.2', 'accelerate==1.15.0',
        'tokenizers==0.23.3', 'mistral-common==1.13.1', 'jinja2==3.1.6', 'sentencepiece', 'protobuf',
        'tiktoken==0.14.0', 'sentence-transformers', 'chromadb', 'openai',
        'fastapi>=0.115,<1', 'httpx>=0.28,<1')
    .add_local_python_source('backend', 'config'))
# create_if_missing=False: no silent resource creation or artifact upload.
volume = modal.Volume.from_name('insurance-slm-private', create_if_missing=False)

@app.function(image=image, gpu='L4', cpu=(2, 2), memory=(16384, 16384), min_containers=0,
    max_containers=1, scaledown_window=60, timeout=900,
    volumes={'/private-assets': volume}, secrets=[modal.Secret.from_name('insurance-slm-demo')])
@modal.concurrent(max_inputs=1)
@modal.asgi_app(requires_proxy_auth=True)
def api():
    import os
    os.environ.setdefault('PRIVATE_SERVING_MANIFEST', '/private-assets/serving-manifest.json')
    os.environ.setdefault('DEMO_QUOTA_DB', '/private-assets/demo-quota.sqlite3')
    os.environ.setdefault('HF_HOME', '/private-assets/hf-cache')
    from backend.api import create_app, Quota
    class CommittedQuota(Quota):
        def reserve(self):
            super().reserve()
            volume.commit()
    quota = CommittedQuota(os.environ['DEMO_QUOTA_DB'], limit=100, rpm=6)
    return create_app(quota=quota)
