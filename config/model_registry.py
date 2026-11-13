"""Public identifiers only. Availability is discovered from the private runtime."""
BASE_MODEL = 'unsloth/Ministral-3-3B-Instruct-2512-bnb-4bit'
BASE_REVISION = '8491af399e7ad92759da849790a5f7e6c2fdfbc4'
ADAPTERS = {
    'D1000': {'training_rows': 751, 'sha256': '7347f3709600d50dc94efd543fa73710a0d901397da2e283c037667df09453cb'},
    'D1500': {'training_rows': 1221, 'sha256': 'c7a2b410ce8d0d7e8d8e8916bee1a1991f9a26a31329de285c30c79e65cee95e'},
}
REGISTRY = [
    {'key': 'base', 'model_id': BASE_MODEL, 'revision': BASE_REVISION,
     'condition': 'base', 'dataset_version': None, 'training_rows': None,
     'adapter_artifact': None, 'storage': 'original Hugging Face source',
     'availability': 'verified source; runtime discovery required',
     'loading': 'CUDA; original NF4/double quantisation; pinned tokenizer/chat template'},
    {'key': 'D500', 'model_id': BASE_MODEL, 'revision': BASE_REVISION,
     'condition': 'sft', 'dataset_version': 'D500', 'training_rows': None,
     'adapter_artifact': None, 'storage': None, 'availability': 'unavailable: no verified checkpoint',
     'loading': None},
    *[{'key': key, 'model_id': BASE_MODEL, 'revision': BASE_REVISION,
       'condition': 'sft', 'dataset_version': key, 'training_rows': item['training_rows'],
       'adapter_artifact': 'sha256:' + item['sha256'],
       'storage': 'existing access-controlled research artifact store; backend manifest only',
       'availability': 'checkpoint verified; not yet served',
       'loading': 'PEFT LoRA safetensors on the pinned NF4 base; language projections only'}
      for key, item in ADAPTERS.items()],
]
