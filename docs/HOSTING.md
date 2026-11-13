# Activation proposal — no paid deployment yet

Prices checked 12 November 2026; USD before tax. Account credit balance, payment
method and eligibility are not verified. No assumption that a trial removes billing
requirements. No commercial LLM provider is used by this app.

## Memory: known facts versus estimates

The pinned public weight file is **3,207,330,222 bytes** (2.987 GiB on disk), read
from public file-size metadata without downloading weights. Disk size is not VRAM.
Text config: 26 layers, hidden3072, intermediate9216, 32 query heads, 8 KV heads,
head dimension128. LoRA rank16 targets q/k/v/o and gate/up/down, language layers only.
This gives **24,707,072 adapter parameters** per checkpoint; if stored in FP32,
98,828,288 bytes each, approximately **0.184 GiB for both adapters**. This is an
architecture calculation, not a newly read private safetensors header.

A batch1 FP16/BF16 KV cache at8192tokens is **872,415,232 bytes (0.8125GiB)**:
`2 × 26 × 8192 × 8 × 128 × 2`. Add quantisation buffers, activations, vision components,
CUDA kernels and allocator overhead. Original D1500 training recorded9,831,868,928
peak allocated GPU bytes; this proves prior execution, not the peak of this service.

**Proposed: one24GB L4**,16GiB host RAM,2physicalCPUcores,one request at a time.
Expected serving budget roughly6–12GiB VRAM, with CPU embedding/reranking preferred
if the original embedding service can be reproduced exactly.16GB T4 may suffice,
but exact peak with both adapters and the selected context length is unmeasured.
Do not call24GB an experimentally established minimum. Activation acceptance must
measure peak allocated/reserved VRAM for all four conditions and long questions.

## Modal (preferred)

Prepared `backend/modal_app.py`: L4, CPU hard limit2, RAM hard limit16GiB,
min_containers0,max_containers1,60secondscaledown,900secondrequesttimeout.
Platform proxy authentication precedes GPU startup; bearer auth and meeting access
code provide additional boundaries. A persistent100request/6RPM quota is committed
before each generation. Polling the health endpoint can keep a GPU warm and is not free.

[GPU/CPU/RAM pricing](https://modal.com/pricing): L4$0.000222/sec,
CPU$0.0000131/core/sec, RAM$0.00000222/GiB/sec.
At fixed2cores/16GiB, conservative combined compute estimate:
`0.000222 + 2×0.0000131 + 16×0.00000222 = $0.00028372/sec`, **$1.021392/hour**.
Actual CPU/memory billing may be lower than this reservation-based estimate.

- 20min live meeting +10min staging/warm-up +1min idle tail: **$0.5277192** compute.
- 45min total active time: **$0.766044** compute.
-60min uninterrupted active reservation: **$1.021392** compute.
-20GiB private Volume: standard$1.80/month at$0.09/GiB-month, but pricing currently
  includes1TiB free volume storage; verify the account allowance. Original artifacts
  remain in their existing private store; measure staged serving-bundle size rather
  than copying multi-GB training checkpoints/optimizer state.

Starter currently advertises$30/month compute credit. GPU use still requires a valid
payment method per [GPU guide](https://modal.com/docs/guide/gpu). Do not add a payment
method, activate GPU or deploy merely because credits may exist.

**Recommended approval envelope: $2 gross usage for one rehearsal + meeting**, with
**$0 out-of-pocket** spend limit if sufficient credits exist, otherwise a separately
approved$2 spend limit. Set both workspace usage budget and net spend limit in the
[budgets UI](https://modal.com/docs/guide/budgets) before deploying. Other workspace
usage counts against those caps. Provider enforcement/rounding, taxes, data transfer,
build costs and retries mean the time estimate is not an unconditional invoice maximum.
Record the console's cap and credits before activation; stop the app after the meeting.
No quota in application code alone caps cloud charges from repeated cold starts.

## Latency (planning ranges, not measured)

With the volume already staged and model cache populated: budget30–180seconds for
cold start/model load and10–90seconds per answer atup to700tokens. First-time cache
population or dependency build may take5–15minutes. These are broad engineering
estimates; no GPU was activated to benchmark them. Prewarm5–10minutes before the
meeting and keep interactions less than60seconds apart, or explicitly approve a
longer scaledown window for the meeting only. Do not present these as observed results.

The original Nomic embedding service remains a separate unresolved dependency.
No embedding model revision/quantisation is silently substituted. Its hosting or
sidecar resource cost must be added if it cannot run inside this reservation.

## Runpod fallback

[Published pricing](https://www.runpod.io/pricing) lists24GB L4/A5000/3090 serverless
at$0.75/hour equivalent; verify the actual endpoint tier/region quote.30min compute
is$0.375, before storage/idle/extra services. Flex workers scale tozero;
[coldstart, execution and idle are billed](https://docs.runpod.io/serverless/pricing).
20GB network volume at$0.07/GB-month is$1.40/month; container disk is extra.

The supplied Dockerfile prepares a **single GPU Pod HTTP API**, not a serverless
queue handler. An L4 Pod is advertised at$0.59/hour (30min$0.295) plus disk; it must
be stopped explicitly and is less convenient for automatic scale-tozero. Do not
compare a Pod quote directly to an operational serverless implementation. A queue
handler/client adapter would be additional work before choosing Serverless.
Runpod is not configured or activated. Prefer Modal for the first meeting because
its ASGI endpoint matches the frontend protocol and scale-tozero is prepared.

## Approval prerequisites still open

1. Owner selects a Modal workspace and explicitly approves activation budget.
2. Private artifact transfer remains cloud-to-cloud; never download weights to this
   public checkout or commit credentials. Verify the original adapter hashes again.
3. Restore the exact private Chroma index and original Nomic embedding runtime.
   The index's embedding-model revision/quantisation was not recorded in available
   receipts; recover the original service identity, do not claim identical weights.
4. Review metadata allowlist and output-release policy. Excerpt allowlist stays empty.
5. GPU test verifies adapter switching, memory, runtime package compatibility and real
   answers. Then deploy frontend and test its actual public URL.

## 13 November recheck

Official Modal pricing and budget documentation were checked again; the listed
L4/CPU/RAM rates above are unchanged. The proposed2dollar envelope is **not owner
authorization**. A10minuteinitialsmoketest costs about$0.170232 at the conservative
fixed reservation rate; a31minutewarmup/meetingsession about$0.5277192; combined
41minutes about$0.6979512 before any extra embedding service, storage, transfer,
image-build resources and taxes. Account credits/payment setup remain unverified.
Do not activate paid GPU or automatic payments. The free public website preview
runs browser Python and uses no GPU inference service.


## Actual private CPU verification

Both final adapters were recovered and hash-verified in a private hosted CPU job.
Each safetensors file is98,882,136bytes including its header; the identical tensor
layout fingerprints confirm static architecture compatibility. The combined
serving-only archive is189,052,500bytes (about180.3MiB), including tokenizer files,
receipts, private original inference code, frozen screening chunks and a private
manifest. It contains no optimizer checkpoints, training answers, historical
predictions or judge ledgers. This is an adapter bundle, not a base-weight cache.
Base weights remain sourced from the original pinned repository.

The exact existing Chroma index and original Nomic runtime were not recovered.
No index was rebuilt or embedding weights substituted. Consequently the bundle
is labelled ADAPTER_BUNDLE_VERIFIED_RAG_RUNTIME_PENDING and public-generation
approval remainsfalse. GPU loading/latency/VRAM measurements are still pending
owner approval. Full private paths, hashes and receipts remain outside this repo.

Independent hosted whole-bundle readback subsequently passed with notebook privacy
confirmed and all23inventoryentriesverified. Base/SFT can be activated independently
after approval; RAG requests remain unavailable until the original index/service returns.
