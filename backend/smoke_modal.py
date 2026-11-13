"""APPROVAL ONLY: ephemeral private GPU test, exactly three new predictions, then exit.

No ASGI/public endpoint, no training/judging, no raw answers returned or persisted.
"""
import modal
from config.deployment import APP_NAME,VOLUME_NAME,MANIFEST_PATH
from backend.modal_app import image

app=modal.App(APP_NAME+'-controlled-test')
volume=modal.Volume.from_name(VOLUME_NAME,create_if_missing=False)

@app.function(image=image,gpu='L4',cpu=(2,2),memory=(16384,16384),timeout=900,
              max_containers=1,min_containers=0,scaledown_window=2,
              volumes={'/private-assets':volume})
def test_three():
    import contextlib,hashlib,json,os,time
    from pathlib import Path
    import torch
    from backend.runtime import ResearchRuntime
    from backend.smoke_validation import validate_selection
    os.environ.setdefault('HF_HOME','/private-assets/hf-cache')
    started=time.monotonic()
    # Public release remains disabled; this private SDK function has no HTTP endpoint.
    with open(os.devnull,'w') as sink,contextlib.redirect_stdout(sink),contextlib.redirect_stderr(sink):
        manifest=json.loads(Path(MANIFEST_PATH).read_text())
        runtime=ResearchRuntime(manifest,private_test=True)
        cold_load=time.monotonic()-started
        observed=[]
        original_generate=runtime.core.generate
        expected=[None]
        def proved_generate(model,*args,**kwargs):
            state=model.get_model_status()
            validate_selection(expected[0],state.enabled,state.active_adapters)
            observed.append({'enabled':state.enabled,'active_adapters':list(state.active_adapters)})
            return original_generate(model,*args,**kwargs)
        runtime.core.generate=proved_generate
        rows=[]
        # New generic example question already approved for the public demo.
        question='What conditions apply to getting a courtesy car under this motor policy?'
        for key in ('base','D1000','D1500'):
            expected[0]=key
            torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats()
            result=runtime.generate_answer(question,key,False)
            torch.cuda.synchronize()
            row={'condition':key,'checkpoint':result.get('checkpoint'),
                 'generation_latency_seconds':result.get('latency_seconds'),
                 'peak_allocated_gpu_bytes':torch.cuda.max_memory_allocated(),
                 'peak_reserved_gpu_bytes':torch.cuda.max_memory_reserved(),
                 'selection_proof':observed[-1] if observed else None,
                 'released_prediction':not bool(result.get('error')),
                 'error_code':result.get('error',{}).get('code') if result.get('error') else None,
                 'refused':result.get('refused')}
            if not result.get('error'):
                row['answer_sha256']=hashlib.sha256(result['answer'].encode()).hexdigest()
            rows.append(row)
            # Withheld/error output is a failed test, never an invitation to retry.
            if result.get('error'):break
        runtime.core.generate=original_generate
        # Persist only the already-public base-model cache, never predictions or prompts.
        volume.commit()
    return {'mode':'private_real_gpu_test','test_passed':len(rows)==3 and all(r['released_prediction'] for r in rows),
            'cold_load_seconds':cold_load,'gpu_name':torch.cuda.get_device_name(0),
            'total_gpu_memory_bytes':torch.cuda.get_device_properties(0).total_memory,
            'predictions':rows,'rag_available':runtime.rag_available,'raw_answers_returned':False,
            'new_training_calls':0,'new_judging_calls':0,'new_prediction_calls':len(rows)}

@app.local_entrypoint()
def main():
    # The ephemeral app terminates after this returns. No public endpoint is deployed.
    print(test_three.remote())
