# Single-page live GPU meeting demo — prepared, not activated

The Gradio interface is implemented in `gradio_app.py` and reuses the existing
`NotebookSession.predict` / `ResearchRuntime` contract. There is no saved-answer
mode, model substitution, GPU startup, public listener or tunnel on import.
The authenticated loopback preview starts without a model and disables Generate.
All inference tests in this change use explicitly synthetic fixtures.

## Route decision and evidence

| Route | Verified | Still unresolved | Decision |
| --- | --- | --- | --- |
| Kaggle + Gradio share | Gradio documents share links as a reverse-proxy tunnel. The project has private hash-verified artifacts and a compatible session interface. | Kaggle permission for externally relayed supervised serving; actual egress/relay connectivity; successful combined GPU runtime. | Do not activate a share link. Technically plausible, not platform-approved or network-tested. |
| Private Hugging Face ZeroGPU Gradio Space | Current HF docs permit eligible free personal accounts to host two ZeroGPU Spaces. The hardware is documented as free; account-specific availability must be checked. | Actual remaining account quota, private visibility/collaborator access in the intended configuration, private artifact transfer approval, bitsandbytes/CUDA-emulation compatibility. | Preferred tunnel-free candidate, not a verified live deployment. |
| Existing static website → Kaggle localhost | Static preview is available. | Browser cannot access private Kaggle loopback; adding credentials to browser code is prohibited. | Unsuitable without an approved reachable backend. A link to an approved Gradio URL is simpler. |

No end-to-end single-page real-inference route has passed yet. The prior finite
Kaggle smoke stopped in standard venv creation before any model predictions. A
CPU-only diagnostic verified `venv --without-pip --system-site-packages` and pip;
the corrected bootstrap has not been GPU-tested. Do not claim this fixed later
CUDA/model issues or that a CPU test establishes relay connectivity.

Sources checked 13 November 2026:

- [Gradio sharing/authentication](https://gradio.app/guides/sharing-your-app): share links use an external proxy; documented expiry is one week, but the GPU session and our 45-minute expiry are shorter. Basic authentication is not comprehensive access security.
- [Gradio implementation](https://github.com/gradio-app/gradio/blob/main/gradio/blocks.py): sharing sets up a tunnel; automatic notebook share detection is why this preparation uses a FastAPI mount and explicit loopback Uvicorn instead of `launch()`.
- [Kaggle notebook documentation](https://www.kaggle.com/docs/notebooks) and [GPU usage](https://www.kaggle.com/docs/efficient-gpu-usage): finite free GPU sessions/quotas, not a documented general-purpose public app host.
- [Kaggle terms](https://www.kaggle.com/terms) / [acceptable-use page](https://www.kaggle.com/aup): public responses did not provide readable substantive terms in this inspection. No permission or prohibition is inferred from that absence. Clarify externally relayed serving with Kaggle before considering that route.
- [HF ZeroGPU](https://huggingface.co/docs/hub/spaces-zerogpu) and [Space visibility/secrets](https://huggingface.co/docs/hub/spaces-overview): primary sources for the conditional alternative below.

Do not rely on other users' tunnelling examples as platform authorization. A
non-sensitive question the operator may send to Kaggle is: “May a Private free-GPU
notebook run a short, supervised, authenticated research demo through a Gradio
share relay, without keepalive, monetisation or exceeding free quota?” No message
has been sent on the owner's behalf.

## Implemented interface and controls

White single-page layout, named model condition, generic examples, custom question,
new answer, actual checkpoint identity, refusal status, latency, copy answer,
optional actual PEFT/GPU measurements, and a disabled RAG control. D500 remains
unavailable. No GPU measurements or predictions are fabricated in the preview.

The controller calls the existing session once per click. It independently checks
actual enabled/active adapter state and exact checkpoint fingerprint before
releasing an answer. It projects only the answer and approved diagnostics; it
does not forward question echoes, exception messages, arbitrary metadata, files,
raw retrieval results or model-service credentials. Answers use a plain textbox,
not executable HTML. RAG remains off; citations are not manufactured.

- Named login with at least 32-character password, configured server-side.
- At most 12 attempts/session and 3/minute, one active generation, queue of 2.
- 1–4,000 question characters and 20,000-byte POST limit. Errors and withheld outputs consume attempts; no retries.
- Authentication required for app configuration and prediction routes; login capped at 5/minute and 30/session. This is a basic safeguard, not MFA or robust abuse protection.
- HTTP access and callbacks expire; approved sessions cannot outlive their review. Model cleanup waits for active generation. Cleanup does not stop a Kaggle VM: operator must Stop Session and verify quota reservation zero.
- No prompt/answer logging, flagging, examples caching, analytics, public API listing, file upload/download controls or raw exception display.
- Explicitly block private model/research paths from Gradio file serving. File-route tests are not a general filesystem security proof.

## Release approval required before any remote browser inference

The current bundle has `public_generation_approved=false` and empty metadata and
excerpt allowlists. It therefore **does not permit remote Gradio generation**.
`private_test=True` is not an exposure approval. `create_http_app` refuses a real
session without a `ReleaseReview`; it also verifies the runtime manifest's explicit
release flag and matching review ID, audience, bundle hash, expiry and blocked roots.

A private, owner-reviewed release record must identify:

1. Exact verified bundle SHA, current reviewed code commit and intended platform.
2. Named authorised meeting audience; no anonymous access.
3. Permission to release screened generated answers and accept arbitrary questions
   for that audience, despite possible memorisation/short or transformed quotations.
4. Private policy documents, passages, adapters, tokens and index data remain
   non-public. Citation metadata/excerpts stay restricted until separately allowlisted.
5. Maximum duration (45 minutes or less), 12 requests, 3/minute, shutdown procedure,
   platform permission and explicit exposure approval. All required review flags
   default false; no approval record is shipped or synthesized.

Authentication limits who can access answers. Eight-token overlap filtering blocks
some exact quotations. Neither proves that outputs cannot disclose restricted
wording. If this residual release risk is not approved, keep generation disabled;
do not quietly switch models, prompts, corpus or outputs.

## Review the page now without a GPU

```bash
pip install -r requirements-gradio.txt
# Set MEETING_USERNAME and a random MEETING_PASSWORD (32+ characters) privately
# through your shell/secret manager; do not commit or embed them in a URL.
python gradio_app.py
```

Open `http://127.0.0.1:7860`, sign in, and inspect the page. It explicitly reports
inference unavailable. This command loads no weights and binds only loopback.
It does not call `Gradio.launch`, start a share relay or connect to a provider.
Installing requirements into a local CPU environment has no GPU-provider charge.

## Kaggle manual sequence — only if permitted and separately approved

1. Obtain platform clarification and owner approval of the specific relay/audience
   and release policy. No tunnel has been created or tested by this change.
2. Confirm notebook Private, preceding session terminal, sufficient free quota and
   pay-to-scale disabled. No paid quota, upgrade or fallback. Plan a short session
   on one free T4/P100-class 16GB GPU; actual combined memory is still unmeasured.
3. Attach only existing authorised artifact credentials through Kaggle User Secrets.
   Exact private notebook/version/file identifiers remain in the private setup record,
   not this repository. Download the pinned 189MB bundle only inside the private runtime.
4. Use the corrected venv bootstrap, original CUDA/package/model pins, verify all
   inventories and adapter/tokenizer identities. Keep retrieval=None/use_rag=False.
5. Complete one Base/D1000/D1500 GPU smoke with actual selection, memory, latency
   and screened-output proof before attaching a remote UI. No automatic retries.
6. Prepare a separately approved runtime manifest and matching `ReleaseReview`;
   mount this UI with a named meeting login, blocked private roots and finite expiry.
   **No share launcher is provided while platform/exposure permission is unresolved.**
7. Only following that review, implement/test the approved HTTPS route with a
   synthetic-only CPU probe first. It must fail closed, never fall back to another
   relay or public exposure. Share the app URL and login separately, privately.
8. Supervisor uses just the authenticated Gradio page. Operator prepares the notebook
   beforehand and stops it after the meeting. No notebook switch is needed by the
   supervisor, but an operator still manages the session. Expiry is not a VM stop.

Account-specific quota observations are retained in private receipts, not published
here. Recheck remaining time, zero conflicting reservations and pay-to-scale disabled
with `scripts/check_kaggle_quota.py`. Kaggle GPU
availability, idle expiry, package downloads, session restart and outbound relay
connectivity can all fail. No minimum meeting uptime is promised.

## ZeroGPU manual feasibility gates — no Space created

Current docs require a verified
email and an account older than 30 days for up to two free personal ZeroGPU Spaces.
Free signed-in users have 5 GPU minutes/day; anonymous users 2 minutes/day. Quota
resets 24h after first GPU use. **Actual remaining account quota is unverified.**
The default `large` allocation is documented as 48GB; `xlarge` consumes twice the
quota and is unnecessary for this proposal. Use no subscription, storage upgrade,
prepaid credits or paid GPU fallback. If the UI does not confirm $0, stop.

1. Check (without creating) Private visibility with ZeroGPU at $0, remaining quota,
   and how the supervisor will receive collaborator access. Public/protected app
   access is not private; a public Space is not an acceptable silent fallback.
2. Approve copying the exact bundle/adapters and required private code/screening
   corpus into an access-controlled HF location. Do not upload private artifacts to
   a public Space repository or browser. Prefer a narrowly scoped read-only private
   artifact token in Space Secrets; do not transfer broad Kaggle credentials silently.
3. Select Gradio/Python 3.12.12 and original torch2.11/CUDA and research pins. Docs
   support torch2.11 but this does **not** verify bitsandbytes NF4, Mistral multimodal
   loading, PEFT switching, memory or the exact tokenizer in CUDA emulation.
4. ZeroGPU uses CUDA emulation during startup and real GPU inside `@spaces.GPU`.
   The present `ResearchRuntime` requires CUDA and loads quantized weights eagerly.
   Do not just wrap a cold loader in the decorator and claim compatibility. Verify
   startup under emulation and decorate generation, or document an independently
   reviewed loading adaptation that preserves pinned weights/quantisation/prompts.
5. Test the dynamic GPU request, exact adapter state and three genuinely new screened
   outputs within the account's actual remaining quota, including cold-start effects.
   Queue delays and per-call duration can prevent the meeting; no paid extension.
6. Only after artifact/access/release and zero-cost review plus successful GPU test,
   deploy with named access and expiry. No HF deployment or upload is authorised by
   implementation preparation alone. This candidate is not marked deployment-ready.

## Website and meeting sequence

The original [website preview](https://peanut-butter116.github.io/insurance-dslm-demo/)
is preserved. Once a secure Gradio URL passes the above gates, add a plain hyperlink
without embedded credentials. Do not put backend tokens in static JavaScript.
A separate server-side Streamlit proxy would need its own free hosting, approved
backend reachability and secrets review; it does not solve the GPU connectivity gap.

In the approved live page: select Base, ask the courtesy-car example, inspect the
actual checkpoint/answer/refusal/latency; repeat with D1000 and D1500; then ask the
unsupported example if quota permits. Do not promise D1500 improves the answer or
that refusal always occurs. Every click is a new generation; this is not evaluation.
Stop after the meeting and verify the GPU session is terminal. If unavailable,
show the existing interface preview labelled unavailable; do not replay predictions.

## Follow-up compatibility preparation

The identified integer-device placement issue now has a symbolic CUDA loader hook,
source-only Space package and aggregate-only bounded-test template. See
[ZEROGPU_COMPATIBILITY.md](ZEROGPU_COMPATIBILITY.md) for current evidence and gates;
real CUDA emulation and GPU generation remain untested. No route is activated.
