"""Generate a code-only, approval-gated private-notebook template. Does not push/run it."""
from pathlib import Path
import json
import subprocess

ROOT=Path(__file__).resolve().parents[1]

def build():
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    def code(text):return {'cell_type':'code','execution_count':None,'metadata':{},'outputs':[],'source':text.splitlines(True)}
    cells=[{'cell_type':'markdown','metadata':{},'source':[
        '# Private supervised Base / D1000 / D1500 demo\n',
        '**Prepared only. Do not start a GPU until the owner approves the free route and free quota is confirmed.**\n',
        'Keep this notebook Private. No paid quota, public tunnel or RAG. The public website preview remains separate.\n']},
      code('''# Defaults deliberately block all execution beyond this cell.
OWNER_APPROVED_FREE_SESSION = False
FREE_GPU_QUOTA_CONFIRMED = False
# Actual private target notebook ref, copied from its URL after saving a CPU-only draft.
MEETING_NOTEBOOK_KERNEL = ''
# Private source identifiers from the owner's verified preparation receipt, not public data.
PRIVATE_BUNDLE_KERNEL = ''
PRIVATE_BUNDLE_VERSION = '38'
PRIVATE_BUNDLE_FILE = ''
assert OWNER_APPROVED_FREE_SESSION and FREE_GPU_QUOTA_CONFIRMED, 'No activation: approval and free quota are required'
assert MEETING_NOTEBOOK_KERNEL and PRIVATE_BUNDLE_KERNEL and PRIVATE_BUNDLE_FILE, 'Configure private notebook refs locally'
'''),
      code('''import os,sys,subprocess
os.environ['CUDA_VISIBLE_DEVICES']='0'
# Original tested CUDA/research pins; installation uses only free notebook time.
subprocess.run([sys.executable,'-m','pip','install','--quiet','torch==2.11.0+cu128','torchvision==0.26.0+cu128','torchaudio==2.11.0+cu128','--index-url','https://download.pytorch.org/whl/cu128'],check=True)
subprocess.run([sys.executable,'-m','pip','install','--quiet','transformers==5.19.0','peft==0.21.2','bitsandbytes==0.50.2','accelerate==1.15.0','tokenizers==0.23.3','mistral-common==1.13.1','jinja2==3.1.6','sentencepiece','protobuf','tiktoken==0.14.0','kaggle==2.2.5','six==1.17.0','fastapi>=0.115,<1','httpx>=0.28,<1','ipywidgets'],check=True)
'''),
      code(f'''from pathlib import Path
DEMO_COMMIT = '{commit}'
checkout=Path('/kaggle')/'working'/'meeting-demo-public-code'
assert not checkout.exists(), 'Use a fresh session; never overwrite an existing checkout'
subprocess.run(['git','clone','--quiet','https://github.com/Peanut-butter116/insurance-dslm-demo.git',str(checkout)],check=True)
subprocess.run(['git','checkout','--quiet',DEMO_COMMIT],cwd=checkout,check=True)
sys.path.insert(0,str(checkout))
from kaggle_secrets import UserSecretsClient
os.environ['KAGGLE_API_TOKEN']=UserSecretsClient().get_secret('KAGGLE_API_TOKEN')
for name in ['MEETING_NOTEBOOK_KERNEL','PRIVATE_BUNDLE_KERNEL','PRIVATE_BUNDLE_VERSION','PRIVATE_BUNDLE_FILE']:
    os.environ[name]=str(globals()[name])
os.environ['FREE_KAGGLE_SERVING_APPROVED']='yes'
os.environ['FREE_KAGGLE_QUOTA_CONFIRMED']='yes'
from backend.kaggle_session import prepare_private_notebook,show_notebook_controls
session=prepare_private_notebook()
print('Private models loaded. Cold load seconds:',round(session.cold_load_seconds,2))
'''),
      code('''# Three new predictions; no judging, evaluation sweep or automatic retry.
question='What conditions apply to getting a courtesy car under this motor policy?'
for condition in ('base','D1000','D1500'):
    result=session.predict(question,condition)
    if result.get('error'):
        print(condition,result['error']['message'])
        break
    print(condition,'checkpoint:',result['checkpoint'])
    print('Actual adapter state:',result.get('actual_selection_proof'))
    print('Latency:',result['latency_seconds'],'GPU:',result.get('gpu_measurements'))
    # Only output-screened answers; keep notebook private and clear output before saving.
    print(result['answer'])
show_notebook_controls(session)
'''),
      code('''# After the meeting, change this flag and run this cell, then click Kaggle Stop Session.
STOP_SESSION_NOW = False
if STOP_SESSION_NOW:
    session.close()
    print('Models released. Click Stop Session in Kaggle now.')
else:
    print('Private controls are ready. At the end, set STOP_SESSION_NOW=True and run this cell.')
''')]
    notebook={'nbformat':4,'nbformat_minor':5,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'}},'cells':cells}
    for i,cell in enumerate(cells):cell['id']='meeting-'+str(i)
    output=ROOT/'notebooks/kaggle_supervised_demo.ipynb';output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(notebook,indent=2)+'\n')
    return output

if __name__=='__main__':print(build())
