"""Thin adapter over the original private research inference/retrieval code.

No training, judge, response cache, dataset generation or artifact publication.
Private code/assets are mounted on the backend, never bundled into this repo.
"""
from contextlib import nullcontext
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from config.model_registry import BASE_MODEL, BASE_REVISION, ADAPTERS
from backend.privacy import PublicRelease

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()

def verify_files(root, inventory):
    root = Path(root).resolve()
    if not inventory:
        raise ValueError('Private file inventory required')
    for relative, expected in inventory.items():
        p = (root / relative).resolve()
        if root not in p.parents or not p.is_file() or sha(p) != expected:
            raise ValueError('Private asset or code inventory differs')

class ResearchRuntime:
    @classmethod
    def from_environment(cls):
        manifest = json.loads(Path(os.environ['PRIVATE_SERVING_MANIFEST']).read_text())
        return cls(manifest)

    def __init__(self, manifest):
        self.manifest = manifest
        if manifest.get('public_generation_approved') is not True:
            raise ValueError('Public generation release review required')
        research = Path(manifest['research_root']).resolve()
        verify_files(research, manifest['research_inventory'])
        required = {'experiments/core.py', 'src/rag.py', 'src/common.py', 'eval/harness.py',
                    'experiments/six_model_benchmark.py', 'cloud/d1000/config.json'}
        if not required <= manifest['research_inventory'].keys():
            raise ValueError('Original inference code must be pinned')
        assets = Path(manifest['asset_root']).resolve()
        verify_files(assets, manifest['asset_inventory'])
        sys.path.insert(0, str(research))
        from experiments import core
        self.core = core
        cfg = json.loads((research/'cloud/d1000/config.json').read_text())
        if cfg['models']['ministral3b']['id'] != BASE_MODEL or cfg['models']['ministral3b']['revision'] != BASE_REVISION:
            raise ValueError('Base model pin differs')
        core.config = lambda: cfg
        self.harness = core.load_module('_live_original_harness', 'eval/harness.py')
        from experiments.six_model_benchmark import normalise_answer
        self.normalise = normalise_answer
        self.adapter_names = []
        for key, adapter in manifest.get('adapters', {}).items():
            if key not in ADAPTERS:
                raise ValueError('Unknown checkpoint')
            directory = assets / adapter['path']
            for filename in ('adapter_model.safetensors', 'adapter_config.json', 'tokenizer_config.json'):
                if str(Path(adapter['path'])/filename) not in manifest['asset_inventory']:
                    raise ValueError('Adapter and tokenizer files must be inventoried')
            adapter_cfg = json.loads((directory/'adapter_config.json').read_text())
            if (sha(directory/'adapter_model.safetensors') != ADAPTERS[key]['sha256']
                or adapter_cfg.get('base_model_name_or_path') != BASE_MODEL
                or adapter_cfg.get('peft_type') != 'LORA'
                or adapter.get('training_rows') != ADAPTERS[key]['training_rows']):
                raise ValueError('Adapter compatibility/provenance differs')
            self.adapter_names.append(key)
        self.rag_available = False
        all_chunks = []
        if manifest.get('retrieval'):
            r = manifest['retrieval']
            home = assets / r['path']
            for name in ('index_manifest.json', 'data/chunks.jsonl'):
                if str((home/name).relative_to(assets)) not in manifest['asset_inventory']:
                    raise ValueError('Index manifest and corpus must be inventoried')
            im = json.loads((home/'index_manifest.json').read_text())
            if (im['embedding_model'] != core.common.EMBED_MODEL or im['chunks_sha256'] != sha(home/'data/chunks.jsonl')
                or im['chunks_sha256'] != r['chunks_sha256']):
                raise ValueError('Original index differs')
            if not (home/'chroma/chroma.sqlite3').is_file():
                raise ValueError('Original index missing; do not rebuild silently')
            for p in (home/'chroma').rglob('*'):
                if p.is_file() and str(p.relative_to(assets)) not in manifest['asset_inventory']:
                    raise ValueError('All index files must be inventoried')
            from openai import OpenAI
            # Private operator config only; never taken from user request.
            core.rag._client = OpenAI(base_url=r['embedding_url'], api_key=os.environ.get('EMBEDDING_API_TOKEN', 'private-local'), timeout=120)
            core.rag.CHROMA_DIR = home/'chroma'
            core.rag._collection = None
            if core.rag.reranker() is None:
                raise ValueError('Original BGE reranker unavailable')
            all_chunks = core.rows(home/'data/chunks.jsonl')
            if core.rag.collection().count() != im['n_chunks']:
                raise ValueError('Original index count differs')
            # Prove the exact embedding service is available without generation.
            ids = {m.id for m in core.rag.client().models.list().data}
            if core.common.EMBED_MODEL not in ids:
                raise ValueError('Original Nomic embedding runtime missing')
            self.rag_available = True
        # Even no-RAG public output needs the private corpus overlap guard.
        if not all_chunks:
            raise ValueError('Private wording inventory required for public output screening')
        self.release = PublicRelease(all_chunks, manifest.get('public_display_chunk_ids'), manifest.get('public_metadata_chunk_ids'))
        self.release.resolver = core.rag.verify_citations
        from peft import PeftModel, prepare_model_for_kbit_training
        self.model, self.tokenizer = core.load_model('ministral3b')
        if hashlib.sha256(str(self.tokenizer.chat_template).encode()).hexdigest() != 'a81fa42ad89f88c79d32f8f52c1cc7b1abfce90774437022e1cb22ce741ae86b':
            raise ValueError('Original tokenizer chat template differs')
        from transformers import AutoTokenizer
        for key in self.adapter_names:
            saved = AutoTokenizer.from_pretrained(assets / manifest['adapters'][key]['path'], fix_mistral_regex=True)
            if saved.get_vocab() != self.tokenizer.get_vocab() or saved.chat_template != self.tokenizer.chat_template:
                raise ValueError('Adapter tokenizer differs from pinned base')
        if self.adapter_names:
            self.model = prepare_model_for_kbit_training(self.model, use_gradient_checkpointing=False)
            for i, key in enumerate(self.adapter_names):
                directory = assets / manifest['adapters'][key]['path']
                if i == 0:
                    self.model = PeftModel.from_pretrained(self.model, directory, adapter_name=key, is_trainable=False)
                else:
                    self.model.load_adapter(directory, adapter_name=key, is_trainable=False)
        self.model.eval()
        self.model.config.use_cache = True

    def available(self, key, rag=False):
        return (key == 'base' or key in self.adapter_names) and (not rag or self.rag_available)

    def configurations(self):
        return [{'key': key, 'available': self.available(key), 'training_rows': ADAPTERS.get(key, {}).get('training_rows')}
                for key in ('base', 'D500', 'D1000', 'D1500')]

    def generate_answer(self, question, model_config, use_rag):
        if not self.available(model_config, use_rag):
            raise ValueError('Configuration unavailable')
        start = time.monotonic()
        chunks = self.core.rag.retrieve(question, k=6, pool=24, rerank=True) if use_rag else []
        if use_rag and not chunks:
            raise ValueError('Retrieval empty')
        messages = self.harness.build_row_messages({'question': question, 'persona': 'end_user'}, {'chunks': chunks}, use_rag)
        if model_config == 'base':
            context = self.model.disable_adapter() if self.adapter_names else nullcontext()
        else:
            self.model.set_adapter(model_config)
            context = nullcontext()
        with context:
            raw, _ = self.core.generate(self.model, self.tokenizer, messages, max_new_tokens=700)
        parsed = self.normalise(raw)
        checked = self.core.rag.verify_citations(parsed['answer'], chunks)
        answer, citations, evidence = self.release.release(parsed['answer'], chunks, checked, self.core.common.CITATION_RE)
        if answer is None:
            return {'error': {'code': 'restricted_wording', 'message': 'The generated output was withheld because it reproduced restricted policy wording.'},
                    'serving_status': 'live_output_withheld', 'latency_seconds': time.monotonic()-start}
        return {'question': question, 'model_id': BASE_MODEL, 'revision': BASE_REVISION,
            'checkpoint': 'sha256:'+ADAPTERS[model_config]['sha256'] if model_config != 'base' else BASE_REVISION,
            'sft': model_config != 'base', 'rag': use_rag,
            'dataset_version': model_config if model_config != 'base' else None,
            'training_rows': ADAPTERS.get(model_config, {}).get('training_rows'),
            'answer': answer, 'refused': checked['abstained'], 'citations': citations,
            'citation_identifiers': [c['citation'] for c in citations],
            'retrieved_source_ids': [c['source_id'] for c in evidence],
            'retrieved_evidence': evidence, 'citation_resolution_status': 'resolved' if any(c['resolves'] for c in citations) else 'unverified_or_absent',
            'retrieval_status': 'retrieved' if use_rag else 'disabled',
            'latency_seconds': time.monotonic()-start, 'serving_status': 'live',
            'output_complete': None, 'final_answer_present': parsed['final_answer_present'], 'error': None}
