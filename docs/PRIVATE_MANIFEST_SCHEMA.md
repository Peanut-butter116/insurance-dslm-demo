# Private backend manifest (never put real values in Git)

`PRIVATE_SERVING_MANIFEST` points to a private JSON file on an approved backend volume.
The schema below uses placeholders, not actual private artifact paths or accounts.
All paths are resolved under the indicated private roots and all inventories use SHA256.

```json
{
  "public_generation_approved": false,
  "research_root": "/private-assets/research-code",
  "research_inventory": {
    "experiments/core.py": "<sha256>",
    "src/rag.py": "<sha256>",
    "src/common.py": "<sha256>",
    "eval/harness.py": "<sha256>",
    "experiments/six_model_benchmark.py": "<sha256>",
    "cloud/d1000/config.json": "<sha256>"
  },
  "asset_root": "/private-assets/models-and-retrieval",
  "asset_inventory": {
    "d1000/adapter/adapter_model.safetensors": "<sha256>",
    "d1000/adapter/adapter_config.json": "<sha256>",
    "d1000/adapter/tokenizer_config.json": "<sha256>",
    "d1500/adapter/adapter_model.safetensors": "<sha256>",
    "d1500/adapter/adapter_config.json": "<sha256>",
    "d1500/adapter/tokenizer_config.json": "<sha256>",
    "retrieval/index_manifest.json": "<sha256>",
    "retrieval/data/chunks.jsonl": "<sha256>",
    "retrieval/chroma/chroma.sqlite3": "<sha256>"
  },
  "adapters": {
    "D1000": {"path": "d1000/adapter", "training_rows": 751},
    "D1500": {"path": "d1500/adapter", "training_rows": 1221}
  },
  "retrieval": {
    "path": "retrieval",
    "chunks_sha256": "<verified original chunks file hash>",
    "embedding_url": "<private original Nomic OpenAI-compatible endpoint>/v1"
  },
  "public_metadata_chunk_ids": [],
  "public_display_chunk_ids": []
}
```

Include **every** adapter/tokenizer/index/code file used by the runtime, including
Chroma segment files and transitive private Python imports. The example is a schema,
not a runnable inventory. Hash verification fails closed. The public registry binds
the two adapter weight hashes; tokenizer vocabulary and chat template must match.
The base is loaded from the exact original revision and checked chat-template hash.

Use separate directories for immutable mounted artifacts and the mutable quota DB.
Set `public_generation_approved` only after release review. The display allowlist is
empty by default; metadata and excerpts have independent approvals. Original policy
wording is never included as an API field unless a chunk is explicitly display-approved.

The conservative output filter withholds answers sharing any eight-token passage
with restricted chunks, even without RAG. It does not prove absence of every short
quote, transformed leak or memorised fact. For an unrestricted public meeting use
an independently authored, approved synthetic corpus and disclose the corpus change;
otherwise keep authenticated demonstrator access and review output release policy.
No streaming or raw generation logs are enabled.
