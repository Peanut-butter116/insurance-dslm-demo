# Free Kaggle meeting-only inference — prepared, not activated

## What this route provides

A private Kaggle GPU notebook can load the same verified base and two adapters and
run the existing FastAPI inference backend in-process. The notebook sends authenticated
ASGI requests internally and presents condition selection/question entry through
private widgets. **No public port, tunnel, relay or external paid service is used.**
The public Streamlit/Stlite preview remains available separately. It cannot connect
to an authenticated private notebook's internal ASGI transport. This proposal is
not a deployed public live-model website or a reliable always-on endpoint.

The backend preserves Base/D1000/D1500 identities, original prompts, sequential
adapter switching, quota and output screening. RAG is explicitly disabled: no
Chroma rebuild, Nomic model download or BGE service is activated.

## Feasibility and privacy checks already completed

- Exact private source bundle and its notebook privacy independently verified.
- Both adapter/archive hashes, training manifests and identical tensor layouts verified.
- Original research already ran this base and separate trained adapters on Kaggle GPU;
  the new combined serving session still needs its own real-GPU test.
- Local tests exercise authenticated in-process requests for Base/D1000/D1500, expiry,
  unavailable-state handling and no activation without explicit free-GPU permission.
- Target notebook privacy is checked through authenticated metadata before private
  assets are fetched. The operator must supply the actual notebook ref from its URL.
- Source weights, prompts, policy chunks and secrets stay in private Kaggle storage.
- No raw policy excerpts are displayed. Generated answers still pass output screening;
  matching restricted passages are withheld. This filter is not a proof against every
  possible short/transformed quotation: use private supervised access only.

**Not yet verified:** current free GPU quota, GPU allocation, widget support in the
chosen live session, exact combined-runtime memory/latency, or meeting reliability.
No actual GPU success is claimed from synthetic tests.

## Exact manual sequence — only after final explicit approval

1. Confirm in Kaggle account/session settings that the accelerator is part of the
   free allocation and enough free quota remains for setup plus the meeting. Do not
   purchase quota, link a paid Colab plan, add payment details or select any paid option.
   If unavailable, stop; there is no paid fallback.
2. Create/open a **Private** notebook. Save its code-only draft without Run All, with
   accelerator **None**, so the notebook has a ref whose privacy can be checked.
   Preserve existing research versions, especially the pinned serving-bundle version38.
3. Import the prepared `notebooks/kaggle_supervised_demo.ipynb`. Keep the notebook
   private and attach the existing authorized Kaggle API secret. Configure the source
   notebook ref, exact version38 and bundle filename using the private recovery receipt;
   those identifiers and tokens are not in this public repository.
4. Only after the owner approves this free supervised run, select an available free
   T4/P100 option. The code selects one GPU rather than loading multiple full models.
   Set the two explicit approval/quota confirmation flags in the notebook. Do not
   set them automatically or treat this document as approval.
5. Install the pinned research runtime, clone the reviewed public code commit, verify
   target/source notebook privacy, download the 189MB bundle inside Kaggle, and verify
   every file before loading. Base weights come from the pinned original public source.
6. Run the same approved generic courtesy-car question once with Base, once with
   D1000 and once with D1500. Verify checkpoint fingerprint, actual PEFT enabled/active
   state, new answer/refusal, generation latency and allocated/reserved GPU memory.
   No retry or judging is automatic. A withheld answer is not a successful release.
7. Use private notebook controls for a few additional supervisor questions. The session
   limits total requests to12 and3/minute, serializes inference, and expires after45min.
   No real responses are placed in GitHub or the public preview.
8. Click Release models, clear notebook outputs before saving, then explicitly click
   **Stop Session / Stop** in Kaggle. Releasing model memory alone does not stop the VM
   or its GPU quota clock. Verify the session is stopped. Do not schedule a keepalive.

## Session and connectivity limitations

Kaggle documents up to12hours for CPU/GPU execution and variable weekly free GPU quota:
https://www.kaggle.com/docs/notebooks and https://www.kaggle.com/docs/efficient-gpu-usage .
GPU availability can queue/fail. Interactive idle limits differ across platform
modes/documentation; the actual session UI is authoritative. Do not promise a minimum
meeting duration. Kernel restarts lose loaded models and require another cold start.
The working directory has a20GB saved-output limit; do not save model caches, source
chunks, copied adapters or responses as newly public notebook outputs.

Only the signed-in operator or explicitly authorized private collaborators can use
the notebook UI. For the meeting, the operator can screenshare it. Public Streamlit
Community Cloud cannot call its private localhost/in-process backend. An external
relay/tunnel would require a separate security/connectivity review and is not prepared
or silently introduced here. If a public live URL is mandatory, this free notebook
proposal does not yet satisfy that acceptance criterion.

If allocation or live tests fail, show the public preview and existing performance
report, clearly stating live inference is unavailable. Never replay an answer as new.


## Read-only quota verification

The official authenticated quota endpoint was checked without creating a session.
Actual account quota figures are stored in the private readiness receipt. Run
`python scripts/check_kaggle_quota.py` immediately before approval/activation to
verify remaining time, current reservations and whether paid scaling is enabled.
Unused quota does not guarantee hardware allocation. No subscription or quota
purchase is part of this proposal.
