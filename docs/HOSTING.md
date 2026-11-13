# Hosting decision under the strict $1 credit / $0 cash requirement

**Modal is currently blocked.** The previous $2 proposal is withdrawn. The project has a strict $1 existing-credit ceiling and $0 cash authorization.
An explicit provider $0 net spend limit and credit expiry are unverified. See [STRICT_ZERO_COST.md](STRICT_ZERO_COST.md).
No GPU, volume, image build, paid endpoint, payment method or top-up was activated.

## Safest meeting route

Prepare a supervised, Private Kaggle notebook using an available **free** GPU and
existing private artifacts, with no public tunnel or paid account linkage. The
backend is used in-process by the authenticated notebook operator. The public
website preview remains separate and explicitly unavailable for inference.
[KAGGLE_MEETING.md](KAGGLE_MEETING.md) gives steps, privacy checks and session limits.
The prepared notebook is not activated and free GPU quota/availability remain unverified.

## Model storage and memory facts

Base: pinned `unsloth/Ministral-3-3B-Instruct-2512-bnb-4bit`, revision recorded in
`config/model_registry.py`. Public weight-file size is3,207,330,222bytes; this is
**disk size, not measured serving VRAM**. Original SFT reload audits passed.

Both private adapters are98,882,136bytes each including safetensors headers, with
identical verified tensor layouts. Rank16 over the original seven language projection
targets gives24,707,072parameters per adapter. In FP32 the two adapter payloads total
about0.184GiB. A batch1 FP16/BF16 KV cache at8192tokens is872,415,232bytes (0.8125GiB).
Allocator, quantization, activation and vision-component overhead must be added.

The original D1500 training peak was9,831,868,928allocatedGPUbytes. That proves prior
execution, not the peak/latency of this new combined runtime. A16GB T4 is a plausible
free target because the original pipeline ran on it; combined startup still needs
a real smoke test. Use one visible GPU and one base with two adapters. Never load
three full base models. No exact serving minimum or latency is claimed before measurement.

The private serving archive is189,052,500bytes, with source/tokenizer/receipt metadata
and frozen screening chunks. Independent hosted readback verified privacy, archive
hash and23inventoryentries. It contains no optimizer states, training answers,
research predictions or judge ledgers. The pinned public base is fetched separately.
Original Chroma/Nomic artifacts are missing, so RAG stays disabled.

## Conditional Modal estimates — not authorization

Prepared L4 has24GB VRAM,2physicalCPUcores,16GiBhostRAM,onecontainer maximum and
scale-to-zero. Private test uses a2secondscaledown and900secondmaximumfunctiontime;
production ASGI configuration retains60secondscaledown but is not approved for deployment.

At https://modal.com/pricing rates, fixed GPU/CPU/RAM estimate is$0.00028372/second:
10minutes$0.170232;15minutes$0.255348. CPU transfer, image builds, network, base-model
cache/storage, cold starts and shutdown are additional. They cannot be treated as
zero merely because the model is small. Credits and storage allowances differ.

Do not combine a test plus meeting on the assumption that the whole$1 is safely
available. If Modal ever becomes eligible, use a planned all-resource budget at most
$0.60, verified provider usage cap at most$0.70 and verified$0netspendlimit, leaving
credit margin. The SDK cannot verify all of these controls; current conditions do
not satisfy them. No additional paid plan, Runpod purchase or automatic top-up is
an acceptable fallback. See the strict cost assessment for required evidence.
