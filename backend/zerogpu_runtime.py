"""ZeroGPU placement adapter; imports neither torch nor spaces until approved startup."""
import sys
import os
from config.model_registry import BASE_MODEL, BASE_REVISION


def load_original_nf4(core, key):
    """Same original loader contract; symbolic device only, never dequantise/requantise."""
    import torch
    from transformers import AutoConfig, AutoModelForCausalLM, Mistral3ForConditionalGeneration, BitsAndBytesConfig
    cfg=core.config()['models'][key]
    if key!='ministral3b' or cfg['id']!=BASE_MODEL or cfg['revision']!=BASE_REVISION:
        raise ValueError('Original model identity required')
    if not torch.cuda.is_available():raise RuntimeError('ZeroGPU CUDA emulation not active')
    dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    quant=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type='nf4',
        bnb_4bit_use_double_quant=True,bnb_4bit_compute_dtype=dtype)
    model_config=AutoConfig.from_pretrained(cfg['id'],revision=cfg['revision'])
    if getattr(model_config,'quantization_config',None):
        model_config.quantization_config['bnb_4bit_compute_dtype']=str(dtype).split('.')[-1]
    cls=Mistral3ForConditionalGeneration if cfg['class']=='mistral3' else AutoModelForCausalLM
    model=cls.from_pretrained(cfg['id'],revision=cfg['revision'],config=model_config,
        quantization_config=quant,device_map='cuda',dtype=dtype,attn_implementation='sdpa')
    if not getattr(model,'is_loaded_in_4bit',False):raise RuntimeError('Original 4-bit loading required')
    tokenizer=core.load_tokenizer(key)
    if tokenizer.pad_token_id is None:tokenizer.pad_token=tokenizer.eos_token
    return model,tokenizer


def require_original_torch_build(torch):
    if str(torch.__version__)!='2.11.0+cu128' or torch.version.cuda!='12.8':
        raise RuntimeError('Original torch2.11.0 CUDA12.8 build required; no silent replacement')


def prepare_runtime(manifest, *, smoke_only=True):
    if os.environ.get('ZEROGPU_STARTUP_APPROVED')!='yes' or os.environ.get('SPACES_ZERO_GPU')!='1':
        raise RuntimeError('Approved private ZeroGPU startup required')
    if 'torch' in sys.modules and 'spaces' not in sys.modules:
        raise RuntimeError('Import spaces before torch; no CPU or paid fallback')
    import spaces  # Must precede ResearchRuntime/PEFT/transformers/torch imports.
    import torch
    require_original_torch_build(torch)
    from backend.runtime import ResearchRuntime
    if manifest.get('retrieval') is not None:raise ValueError('RAG must remain disabled')
    return ResearchRuntime(manifest,private_test=smoke_only,model_loader=load_original_nf4)


def nf4_state_proof(model):
    states=[p.quant_state for p in model.parameters() if getattr(p,'quant_state',None) is not None]
    if not model.is_loaded_in_4bit or not states or any(
        state.quant_type!='nf4' or getattr(state,'state2',None) is None for state in states):
        raise ValueError('Actual nested NF4 parameter state not established')
    return {'quantized_parameter_tensors':len(states),'quant_type':'nf4','double_quant':True}


def measure_prediction(runtime, question, condition):
    """Call ONLY inside a directly bound @spaces.GPU handler; no retries."""
    import torch,time
    from backend.smoke_validation import validate_selection
    from config.model_registry import ADAPTERS
    quant_proof=nf4_state_proof(runtime.model)
    proof=[];original=runtime.core.generate
    def observed(model,*args,**kwargs):
        status=model.get_model_status()
        validate_selection(condition,status.enabled,status.active_adapters)
        proof.append({'enabled':status.enabled,'active_adapters':list(status.active_adapters)})
        return original(model,*args,**kwargs)
    runtime.core.generate=observed
    started=time.monotonic()
    try:
        torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats()
        result=runtime.generate_answer(question,condition,False)
        torch.cuda.synchronize()
        expected=BASE_REVISION if condition=='base' else 'sha256:'+ADAPTERS[condition]['sha256']
        if not proof:raise ValueError('Actual generation/adapter proof absent')
        if not result.get('error') and result.get('checkpoint')!=expected:raise ValueError('Checkpoint differs')
        result['actual_selection_proof']=proof[-1]
        result['gpu_measurements']={'peak_allocated_bytes':torch.cuda.max_memory_allocated(),
            'peak_reserved_bytes':torch.cuda.max_memory_reserved(),
            'total_bytes':torch.cuda.get_device_properties('cuda').total_memory}
        result['allocation_diagnostics']={'gpu_name':torch.cuda.get_device_name(),
            'worker_elapsed_seconds':time.monotonic()-started,'loaded_in_4bit':bool(runtime.model.is_loaded_in_4bit),
            'quantization':quant_proof,
            'compute_dtype':str(getattr(runtime.model.config,'quantization_config',{}).get('bnb_4bit_compute_dtype','unrecorded'))
              if isinstance(getattr(runtime.model.config,'quantization_config',{}),dict) else str(runtime.model.config.quantization_config.bnb_4bit_compute_dtype)}
        return result
    finally:runtime.core.generate=original
