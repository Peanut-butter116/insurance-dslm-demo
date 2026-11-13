# Private ZeroGPU compatibility preparation — no deployment or transfer

This phase prepares the existing Gradio demo, not a replacement model or a new
repository. No Space, model repository, GPU request, private transfer or remote
answer release has been activated. The owner has confirmed Private + ZeroGPU $0
is offered. The account namespace and displayed free quota were subsequently verified in the
signed-in browser without changing settings. Resolved destinations and account
figures are retained in the private approval proposal, not published here. The CLI
still has no authenticated profile; recheck fresh quota immediately before a test.

## Compatibility findings

The original `core.load_model` uses `device_map={'': 0}`. HF's current ZeroGPU
reference explicitly warns against integer CUDA placement and supports symbolic
`device_map='cuda'` specifically for the bitsandbytes loader. It also requires
`import spaces` before CUDA-touching imports, eager module-scope weight placement
under emulation, and a directly registered `@spaces.GPU` event handler.

Implemented in `backend/zerogpu_runtime.py`:

- An optional loader hook in `ResearchRuntime`, leaving the existing loader the
  default for all other routes. Private research files and hashes are unchanged.
- ZeroGPU loader duplicates the original loading arguments with one intentional
  change: symbolic CUDA placement. No CPU fallback, device-ID workaround, alternate
  model, dequantisation, requantisation or precision downgrade.
- Original pinned model `unsloth/Ministral-3-3B-Instruct-2512-bnb-4bit`, revision
  `8491af399e7ad92759da849790a5f7e6c2fdfbc4`.
- NF4, nested/double quantisation, original BF16-if-supported/otherwise-FP16 rule,
  SDPA, original tokenizer loader and chat-template/vocabulary checks. A different
  GPU may select a different compute dtype under that SAME original hardware rule;
  record it in the real test and do not claim numerically identical hardware.
- Existing adapter hash/receipt checks, original rank16/alpha32 PEFT preparation,
  Base adapter disabling and D1000/D1500 switching. Original prompt path and
  deterministic generation limit of 700 tokens are unchanged. No judging/training.
- GPU memory functions use the current CUDA device, not fixed device0. Actual
  enabled/active adapter state is checked inside `core.generate`.
- A decorator hook on the actual Gradio callback, not only on an inner helper.

The inspected official `spaces==0.52.0` wheel contains bitsandbytes integration;
its source uses the modern backend for versions >=0.46. Our original pinned
`bitsandbytes==0.50.2` meets that source branch. Official docs list torch2.11 as
supported. The prepared requirements retain `torch==2.11.0+cu128`, transformers5.19,
PEFT0.21.2 and the original tokenizer/mistral packages; add spaces0.52 and Gradio6.32.

**Evidence level:** loader arguments and branch behaviour are covered by CPU
mocks, source inspection and local tests. No real CUDA emulation/model loading,
NF4 kernel, Mistral multimodal class, adapter attachment, packing/fork restoration,
latency, peak VRAM, CUDA wheel resolution on the Space image or end-to-end answer
has been verified. If the exact pins fail, stop; request review before any dependency
change. Do not use synthetic test success as real inference success.

Primary references (checked 13 November 2026):

- [HF ZeroGPU runtime reference](https://github.com/huggingface/skills/blob/main/skills/huggingface-spaces/references/zerogpu.md)
- [Official spaces package](https://pypi.org/project/spaces/0.52.0/)
- [ZeroGPU supported runtime/quota](https://huggingface.co/docs/hub/spaces-zerogpu)
- [Private repository download tokens](https://huggingface.co/docs/huggingface_hub/guides/download)
- [Read-only quota API](https://huggingface.co/docs/huggingface_hub/guides/manage-spaces#track-your-zerogpu-quota)

## Exact delivery proposal — privately confirmed namespace, never guessed

Proposed immutable slugs:

| Resource | Identifier | Access |
| --- | --- | --- |
| Private model-type artifact repository | `<confirmed-HF-namespace>/insurance-slm-private-serving` | Owner only; no supervisor or organisation-wide grant |
| Bundle file in that repository | `private-serving-bundle.tar.gz` | Same private access; exact size 189,052,500 bytes |
| Private Gradio Space | `<confirmed-HF-namespace>/insurance-slm-private-meeting` | Owner only for technical smoke; named audience separately approved for meeting |
| Runtime artifact revision | Full immutable 40-character HF commit returned by approved upload | Never mutable `main` |

Bundle SHA256: `3acba26cf825e8de838dc474a12fd89e51457f5b3450719c5d83929f6c7d3ac4`.
The same bundle contains both verified adapters, original approved code subset and
private screening corpus. No optimiser/training data, historical responses or judge
ledger is added. Both adapters remain 751/1,221 actual training rows.

The namespace was confirmed from the signed-in HF profile, independently of GitHub
and Kaggle identity. The fully qualified proposed destinations are in the owner
private approval receipt and chat report. No destination has been created or approved.
This public document intentionally uses a placeholder in place of the account ID.
Generate the review payload locally with:

```bash
python -m scripts.prepare_hf_delivery_plan --namespace YOUR_CONFIRMED_HF_NAMESPACE
```

It prints false approval flags and performs no service calls. Submit the exact
resolved IDs and permission list for owner approval before creating either resource.

## Safest transfer and credentials

1. Approve the resolved artifact destination, owner-only ACL, free included storage
   and transfer of all bundle contents to HF as a new private processor. No paid
   storage, organisation billing, subscription or overage option is permitted.
2. Only after that approval, create the **Private model repository** with no broad
   organisation access. This preparatory code deliberately has no `create_repo` call.
3. Create a fine-grained upload token scoped to write ONLY that repository. It needs
   no Space administration, billing, inference-provider or other-repository access.
   Attach it as `HF_BUNDLE_UPLOAD_TOKEN` only to the approved private CPU transfer
   environment. Never enter its value into code, Git, a URL or chat.
4. Run the transfer inside the existing approved private Kaggle CPU environment,
   with accelerator None. The existing Kaggle User Secret retrieves the exact pinned
   v38 bundle inside the host. Do not download weights/policy content to the laptop.
   `upload_verified_cloud_bundle` requires the exact reviewed plan, verifies full
   hash/size and every inventory file, checks destination privacy/owner and uses
   `parent_commit` to reject a concurrent destination change. It uploads ONE file.
5. Record the returned immutable HF commit privately, independently download/read
   back from that commit inside a private CPU environment, verify all hashes, and
   revoke the upload token. Original Kaggle stores/outputs are never modified.
6. After separate Space approval, store a DIFFERENT fine-grained **read-only** token
   scoped to this artifact repository and the exact Private Space (the latter is
   needed only for its metadata/privacy check), as `HF_BUNDLE_READ_TOKEN`.
   No write, administration, billing or unrelated-repository permission.
   The Space receives no Kaggle token, upload token, judge secret or provider key.
7. Do not give a supervisor artifact-repo access merely to use the demo. Approve
   Private Space access separately. Private Space collaborators may see its public-safe
   source; that repository must not contain the protected bundle/weights/corpus.

The transfer function refuses a laptop environment and an unapproved plan before
network access. It refuses public destinations and local private-artifact downloads. The HF reader verifies private
metadata, exact owner and immutable revision before download, then full archive and
inventory hashes. No automatic credential creation, repo creation or permission change.

## Smallest proposed real GPU smoke — separately approved

The smoke is owner-only in the Private Space and displays **technical aggregates
and answer hashes only**, not model-generated answer text. Thus it does not open
the remote answer-release gate. Creating/starting that Private Space, copying assets,
and allocating free GPU nevertheless each require the relevant owner approval.

- One original base loaded at startup under emulation, both verified adapters resident.
- Default `large` ZeroGPU allocation, documented as 48GB. Never `xlarge` or dedicated
  hardware. Actual required/peak memory is unknown until measured; do not claim 48GB
  is an experimentally measured need.
- Three explicit clicks in order: Base, D1000, D1500, one new approved courtesy-car
  question each, RAG off. One request/condition, `duration=60` seconds per request.
- Maximum requested GPU duration 180 seconds total. Require a fresh verified free
  balance >=240 seconds, retaining >=60 seconds unplanned headroom. No credit-backed
  extension, purchase, hardware upgrade, automatic retry or additional prediction.
- This is a bounded *proposal*, not a latency prediction. Loading/packing occurs at
  startup; cold worker restoration and generation count toward the request limit.
  A timeout may leave an unknown intent. Preserve it and stop, never retry it.
- The CPU preflight reserves each case in SQLite BEFORE allocation. Worker claims
  that reservation once and saves a safe receipt. Unknown, failed, withheld and
  repeated cases block continuation. The journal is shared across worker forks.
  Redeployment could reset ephemeral disk: preserve receipts and never restart this
  test to replay a reserved/unknown case. A controller guard cannot prevent every
  authenticated malicious request to a GPU handler; provider free-tier quota is the
  outer spending boundary, not an application claim of perfect enforcement.
- Check current GPU/name/memory in the worker, actual adapter enable/disable state, nested NF4 parameter metadata,
  exact checkpoint, new-answer hash, refusal/final-answer presence, screening result,
  latency and elapsed worker time. Return no raw answer, question echo or evidence.
- Stop on any failure. At the end pause the Private Space, confirm no active request
  and inspect post-test quota. ZeroGPU releases each allocation; do not kill an
  active worker or add keepalive. Capture actual quota delta, not an invented price.

Free accounts currently have a documented 300 GPU seconds/day, resetting 24h after
first use. The owner’s displayed usage was checked in-browser and recorded privately; this
is still a dated display rather than a live API reservation. The read-only helper
`python scripts/check_hf_quota.py` uses an existing profile; this checkout had none.
An operator can also use `hf spaces zero-gpu quota --format json`. The API may need
Billing > read usage permission; do not broaden the artifact token. Prefer the
operator's local read-only query and a fresh manually verified receipt. No token
value should be sent here. If remaining<240, the prepared test will not start.
If the platform rejects a 60-second request or the exact runtime cannot fit in it,
stop and review the plan; do not silently increase duration or split/replay outputs.

## Source package and activation boundaries

```bash
python scripts/build_zerogpu_source.py /tmp/NEW_SOURCE_ONLY_REVIEW_DIRECTORY
```

This builds an allowlisted public-code package, source inventory, pinned requirements
and the guarded `deploy/zerogpu/app.py` template; it does NOT upload or create a Space.
It imports spaces before CUDA dependencies, eagerly loads only after explicit startup
approval, verifies the Space's exact identity/private metadata and registers the GPU
handler directly. There is no tunnel or service-substitution fallback.

Only after approvals, operator configuration includes:

- Variables: `PRIVATE_HF_NAMESPACE`, immutable `PRIVATE_BUNDLE_REVISION`, finite
  `SMOKE_EXPIRES_AT` (<=30min) and explicit
  `ZEROGPU_SMOKE_APPROVED=yes`. Space must supply `SPACES_ZERO_GPU=1` itself.
- Secrets: `HF_BUNDLE_READ_TOKEN`, named `MEETING_USERNAME`, random
  `MEETING_PASSWORD` of at least32 characters. No credentials in the public source.
- Immediately before each technical request, supply the quota receipt through the
  authenticated operator interface/RPC, not a startup environment variable. It contains `remaining`, `overquota_used:0`, `checked_at`,
  `free_account_verified:true`, `no_paid_extension:true`; do not assert these flags
  unless the corresponding account state was actually verified. It expires after5min.

Do not set approval flags while preparing this code. A closed-gate build is expected
to refuse startup. A real test cannot be guaranteed to complete within free quota
until exact runtime latency and current balance are known. With >=240 seconds and
three successful <=60-second allocations, it fits the proposed envelope; otherwise
stop without spending money.

## Separate remote-output review

See [ZEROGPU_OUTPUT_REVIEW.md](ZEROGPU_OUTPUT_REVIEW.md). The verified bundle's release
flag remains false. Future single-page meeting serving must keep quotas in a shared
main-process/durable layer across worker forks; the existing generic in-memory
controller alone is not a ZeroGPU multi-worker quota implementation. It also needs
reviewed named Private Space access, expiry and approved-answer release. The
aggregate-only compatibility template is not presented as the completed meeting app.

The existing Gradio design and [original website preview](https://peanut-butter116.github.io/insurance-dslm-demo/)
are unchanged. No Kaggle tunnel is pursued in this phase.

## Deployment-stage preflight correction

Quota is now checked at each CPU reservation using a fresh operator receipt, after
model startup. It is not frozen into a five-minute Space startup variable. Required
free headroom is 240 seconds before Base, 180 before D1000 and 120 before D1500,
including a 60-second reserve. The authenticated technical RPCs are undocumented,
not anonymous; they return only receipts/hashes and keep the answer gate closed.
The runtime read token is checked for exact fine-grained read-only repository scopes.

The live permission preflight exposed an HF schema detail: scoped tokens can include
an empty owner-context entry, while selected-repository write is named `repo.write`
and implicit selected-repository access is `repo.access.read`. The validator now
ignores only empty entries, checks every active entity against the exact approved
repository set, and rejects active namespace/global grants. No permissions were
changed or broadened to resolve the false-positive preflight.
