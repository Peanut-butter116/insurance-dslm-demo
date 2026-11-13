# Current deployment runbook

## Current verified status

The [public preview](https://peanut-butter116.github.io/insurance-dslm-demo/) is live
on free GitHub Pages/Stlite. It contains no backend credential or model connection.
Actual Base/D1000/D1500 serving is prepared but **not GPU-tested or activated**.
The exact private adapter bundle was recovered, hashed and independently read back.
RAG remains unavailable because original index/embedding artifacts are missing.

**The owner's strict $1-credit/$0-cash requirement supersedes the old $2 proposal.**
Do not activate Modal, create volumes, add payment methods, top up or upgrade plans.
No owner activation receipt exists. [STRICT_ZERO_COST.md](STRICT_ZERO_COST.md)
explains why the provider-set $1 usage budget is not by itself a $0-spend guarantee.

## Non-billable local verification

```bash
pip install -r requirements-test.txt
pytest -q
python scripts/audit_public.py
python scripts/activate_modal.py
```

The last command defaults to preparation only and creates nothing. Imports of Modal
app definitions do not run them; do not use `modal run`/`modal deploy` as a readiness
check. That can build images/create compute before application code executes.

## Proposed free Kaggle route — wait for explicit approval

Read [KAGGLE_MEETING.md](KAGGLE_MEETING.md), then review the code-only notebook template.
Before starting a free GPU, confirm available quota and Private sharing; no paid
Colab linkage or alternative paid quota is permitted. The notebook defaults to false
approval flags and cannot fetch private assets/load models until they are set after
actual owner approval. It preserves exact base/adapter pins and makes RAG unavailable.

The private inference backend uses authenticated in-process ASGI. It exposes no
public port and cannot be called by Streamlit Community Cloud. The signed-in operator
can screenshare the private notebook's live answers while the public preview remains
available for website review. Allocation, widget rendering and combined-model GPU
execution still need a real session test; they are not claimed from synthetic tests.

Shutdown: use Release models, clear notebook outputs, and explicitly Stop Session
in Kaggle. Model cleanup/expiry does not stop the VM's quota clock.

## Exact private transfer mechanism (Modal remains blocked)

The source bundle stays in an authenticated Private Kaggle notebook output at its
verified version. Source refs are supplied only in private configuration. If a later
zero-cash-safe Modal transfer is explicitly approved:

1. An existing approved private Modal Volume is required; the code uses
   `create_if_missing=False`. No volume is created silently.
2. Operator supplies an approved `insurance-slm-artifact-reader` Secret containing
   the existing source account token and `PRIVATE_BUNDLE_KERNEL`,
   `PRIVATE_BUNDLE_VERSION=38`, `PRIVATE_BUNDLE_FILE`. Never paste secrets into chat,
   GitHub, build arguments or the public frontend. No credentials were transferred now.
3. `backend/stage_modal.py` runs one ephemeral CPU worker, not a GPU/public endpoint.
   It verifies source notebook privacy and exact file identity, streams the189MB
   bundle directly into the backend, checks the whole archive plus inventory, rejects
   links/traversal/extra files, and publishes the verified directory atomically.
4. Manifest location is `/private-assets/bundle/serving-manifest.json`. The previous
   root-path mismatch has been corrected. Public generation staysfalse; no excerpt
   allowlist is enabled automatically.

CPU transfer, builds and storage are included in financial approval; they are not
free merely because no GPU is involved. This mechanism is prepared/tested with
synthetic fixtures but has not been executed on Modal.

Activation helper separates private transfer, private smoke and public endpoint
approval scopes. Any future receipt must document actual owner permission, workspace,
credit/expiry, verified zero net-spend/no-top-up controls, provider usage cap<=0.70,
planned all-resource cap<=0.60 and short expiry. No receipt is generated automatically.
Current account evidence fails those requirements, so Modal remains blocked.

## Production Streamlit Community Cloud

Manual sign-in remains necessary at https://share.streamlit.io/:

1. Continue to sign-in and authenticate with the authorized GitHub account.
2. Create app → `Peanut-butter116/insurance-dslm-demo` → reviewed feature branch
   `codex/live-inference-demo` → `app.py` → Python3.11.
3. Without backend secrets this is a safe unavailable frontend. Do not claim live inference.
4. Only after a separately approved reachable backend exists, add **server-side** Secrets:

```toml
INFERENCE_API_URL = "https://<verified-private-backend-url>"
INFERENCE_API_TOKEN = "<scoped-bearer-token>"
DEMO_ACCESS_CODE = "<meeting-only-code>"
MODAL_PROXY_KEY = "<private-proxy-key-if-Modal-is-approved>"
MODAL_PROXY_SECRET = "<private-proxy-secret-if-Modal-is-approved>"
```

Do not add artifact credentials, adapters, indices or policies to the frontend.
The static preview can never hold these credentials. Verify the assigned production
URL and real generation before marking it live; no such URL currently exists.
