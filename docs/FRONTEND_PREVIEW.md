# Public website preview

Verified URL: https://peanut-butter116.github.io/insurance-dslm-demo/

The same `app.py` runs through Stlite in the browser, hosted on free GitHub Pages
from this repository's feature branch `/docs`. This is a functioning interactive
**frontend preview**, not a GPU endpoint or a claim of live inference. It requires
no account or meeting code to review. Initial load downloads the browser Python
runtime and can take a minute. No answers are replayed or simulated.

Verified in a public browser: page renders; SFT toggle enables dataset selection;
D1500 selection displays1221actualtrainingrows and the correct adapter fingerprint;
custom question entry works; Generate Answer stays disabled; historical seed
results are labelled notD500/notlive. The public file bundle contains only the app,
public configuration, aggregate historical metrics and generic example questions.
It excludes client credentials and all backend/private artifacts.

Never put secrets in this static preview. The production Streamlit frontend remains
a separate server-side deployment using Streamlit Secrets and private Modal API.
A public static browser cannot safely hold backend bearer/proxy credentials.
`PUBLIC_PREVIEW=1` forces all backend configuration off even if environment values
exist. No network call is made to an inference service by this preview.

To rebuild after UI changes:

```bash
python scripts/build_preview.py
python scripts/audit_public.py
pytest -q
```

Commit the updated app plus `docs/preview/files.json` on the existing feature branch.
GitHub Pages publishes `/docs`. Check actual browser behavior before reporting a
successful update; HTTP200 alone does not prove the browser Python app initialized.

For Streamlit Community Cloud, the observed page currently requires sign-in at
https://share.streamlit.io/. Manual steps: Continue to sign-in → authenticate with
the authorized GitHub account → Create app → existing repository → reviewed feature
branch → `app.py` → Python3.11 → Deploy. No secrets are required for an unavailable
frontend review. Add server-side meeting/API/proxy secrets only after backend approval.
Full production steps remain in `DEPLOYMENT.md`.
