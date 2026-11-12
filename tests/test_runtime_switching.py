from contextlib import contextmanager
from types import SimpleNamespace
from backend.runtime import ResearchRuntime
from config.model_registry import ADAPTERS

class Model:
    def __init__(self):self.active='D1000'
    def set_adapter(self,key):self.active=key
    @contextmanager
    def disable_adapter(self):
        prior=self.active;self.active=None
        try:yield
        finally:self.active=prior

def test_actual_runtime_switch_and_prompt_paths():
    r=ResearchRuntime.__new__(ResearchRuntime)
    r.adapter_names=['D1000','D1500'];r.rag_available=True;r.model=Model();r.tokenizer=object()
    calls=[]
    chunks=[{'id':'synthetic-1'}]
    def generate(model,tok,messages,max_new_tokens):
        calls.append((model.active,messages,max_new_tokens))
        return 'SYNTHETIC TEST RESULT',10
    r.core=SimpleNamespace(generate=generate,
        rag=SimpleNamespace(retrieve=lambda *a,**kw: chunks,verify_citations=lambda *a:{'abstained':False,'citations':[]}),
        common=SimpleNamespace(CITATION_RE=None))
    r.harness=SimpleNamespace(build_row_messages=lambda q,c,rag:['open' if rag else 'closed',c])
    r.normalise=lambda raw:{'answer':raw,'final_answer_present':True}
    r.release=SimpleNamespace(release=lambda answer,*a:(answer,[],[]))
    for key,rag in [('D1000',True),('D1500',True),('base',False),('D1000',False)]:
        value=r.generate_answer('Synthetic question',key,rag)
        assert value['checkpoint']==('sha256:'+ADAPTERS[key]['sha256'] if key!='base' else value['revision'])
    assert [c[0] for c in calls]==['D1000','D1500',None,'D1000']
    assert [c[1][0] for c in calls]==['open','open','closed','closed']
    assert calls[2][1][1]['chunks']==[]
    assert all(c[2]==700 for c in calls)
