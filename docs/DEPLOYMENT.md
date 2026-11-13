# Deployment runbook

Status: prepared, not deployed. No live URL or GPU success is claimed.
The owner requires explicit approval before any paid endpoint, GPU activation,
private asset migration or billing commitment. All commands below that create
cloud resources are **approval-only instructions**, not executed actions.

## Non-billable local preparation

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-test.txt modal==1.6.4
pytest -q
python scripts/audit_public.py
python -c 'import backend.modal_app'
streamlit run app.py
```

No model weights are loaded by tests or by an unconfigured frontend. API tests use
explicit synthetic test doubles and do not establish real inference success.
To start a privately provisioned runtime:

```bash
pip install -r requirements-api.txt
uvicorn backend.api:app --host 127.0.0.1 --port 8000 --workers 1 --no-access-log
```

Set `PRIVATE_SERVING_MANIFEST`, `INFERENCE_API_TOKEN` (random32+characters), a persistent
`DEMO_QUOTA_DB`, and a meeting epoch deadline `DEMO_EXPIRES_AT`. Keep environment files
outside Git. Install original GPU/retrieval dependencies in the backend image only.
Do not run the private CUDA model on the frontend or replace it with another model.

## Modal — after explicit approval

1. Sign in to the approved workspace. On Usage & Billing verify available credits,
   set the workspace usage budget and net spend limit from the approved envelope.
   Do not assume Starter credit exists or add a card without approval.
2. Authenticate using `modal token new` in the operator's secure terminal. Do not
   paste tokens into chat, source, build arguments or GitHub.
3. Create private Volume `insurance-slm-private` and Secret `insurance-slm-demo`
   in the Modal dashboard. The Secret contains API token and meeting deadline;
   optionally restricted HF credentials. Artifact tokens must never reach Streamlit.
4. Stage an allowlisted **serving-only** bundle through an approved cloud-to-cloud
   transfer from the existing private research store. Include base cache, two final
   adapters/tokenizers/receipts, private inference Python modules, original index and
   chunks, original embedding runtime. Do not transfer optimizer/trainer state,
   training data, gold questions, historical answers or judge logs into this service.
   Record file sizes and SHA256; keep the exact inventory/paths in the private manifest.
   No public model repository is needed. New persistent volume creation/storage is
   part of the approval, not automatically covered by compute credits.
5. The mounted original research source must include all transitive imports used by
   `experiments.core`, `eval.harness`, `src.rag`, and the normalizer. Verify hashes.
   For retrieval, provide the exact Nomic service's OpenAI-compatible `/v1` URL.
   A new Hugging Face embedding implementation is not an authorized silent substitute.
   If no original service/index can be recovered, leave RAG unavailable and report it.
6. Populate the private manifest using [schema](PRIVATE_MANIFEST_SCHEMA.md). Approve
   public metadata separately; leave excerpt IDs empty. Review output release policy
   before setting `public_generation_approved=true`.
7. Deploy only now:

   ```bash
   modal deploy backend/modal_app.py
   ```

8. Create a Modal workspace proxy token using the dashboard/secure CLI. Record the
   actual HTTPS URL from the successful deploy. Store proxy key/secret and API bearer
   token only in the frontend's server-side Streamlit Secrets. Platform proxy auth
   rejects anonymous requests before GPU startup.
9. Run the five real-model scenarios in DEMO_RUNBOOK.md. Record actual checkpoint
   hash per reply, latency, citations, peak VRAM and any withheld output. Do not mark
   successful because an authenticated `/health` alone returnsready.
10. After the meeting, run `modal app stop insurance-slm-meeting-demo`, verify stopped
    containers and usage in the console, revoke meeting/proxy credentials and turn
    off the frontend backend configuration. Retain protected originals; delete only
    the serving-copy Volume if the owner approves and it is no longer required.

## Streamlit Community Cloud

[Official deployment steps](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy):
GitHub authentication is required. No authenticated Streamlit session is configured
for this task, so these are manual UI steps until the owner completes sign-in.

1. Sign in at `https://share.streamlit.io` using the GitHub account with repo access.
2. Click Create app / Deploy from GitHub. Repository:
   `Peanut-butter116/insurance-dslm-demo`; choose the reviewed branch/commit; mainfile`app.py`.
3. Advanced settings: Python3.11. Add server-side Secrets:

   ```toml
   INFERENCE_API_URL = "https://<actual-approved-backend-url>"
   INFERENCE_API_TOKEN = "<private-bearer-token>"
   DEMO_ACCESS_CODE = "<meeting-only-code>"
   MODAL_PROXY_KEY = "<private-proxy-key>"
   MODAL_PROXY_SECRET = "<private-proxy-secret>"
   ```

4. Deploy. Open the actual assigned HTTPS URL in a fresh browser, enter meeting code
   and execute all five scenarios. Never invent or infer a successful Streamlit URL.
5. Do not add artifact storage tokens, policy documents, adapters or indices to this
   frontend. Public examples are generic questions authored for the app, not benchmark
   records. Excerpts appear only from approved response fields.

## Runpod fallback

After a separate approved account/region/GPU quote, build the supplied backend
Dockerfile, stage private artifacts on approved private storage, and run one GPU Pod
behind HTTPS with access logs disabled and the same auth/quota/deadline settings.
Never bake protected assets or tokens into a public image. Terminate the Pod after
the meeting; stopped Pod storage can remain billable. Serverless would require a
separate queue handler and protocol adaptation, not merely deploying this Dockerfile.

## Resumed implementation — 13 November 2026

A free, verified public browser Streamlit preview is now available; see
[FRONTEND_PREVIEW.md](FRONTEND_PREVIEW.md). This removes the authentication blocker
for **website review**, while the server-side production frontend still requires
Streamlit Community Cloud sign-in. Public preview mode can never connect to Modal.

Activation helper defaults to non-billable preparation:

```bash
python scripts/activate_modal.py
python scripts/preflight.py --manifest /private-assets/serving-manifest.json
```

After actual explicit owner approval and provider budget checks, record permission
in a private receipt (never create this automatically): owner_approved=true,
app=insurance-slm-meeting-demo,gpu=L4,gross_usage_cap_usd<=2,
provider_budget_verified=true,expires_at_epoch within the next2hours.
This is a record of permission, not a substitute for obtaining it.

```bash
python scripts/activate_modal.py --activate --owner-approval-receipt /private-assets/owner-approval.json
```

Immediately after the meeting:

```bash
python scripts/shutdown_modal.py
```

The helper stops this app only and preserves research originals. Verify the provider
console shows stopped containers. Model/index preparation and release review are
still prerequisites; an approved budget does not waive missing runtime dependencies.
