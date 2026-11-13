# UK Motor Insurance — Small Language Model Research Demo

Tech Mahindra Makers Lab | Policy-Grounded Question Answering

**Website preview is live:** https://peanut-butter116.github.io/insurance-dslm-demo/

**Real inference remains unavailable**, pending owner approval, private asset staging
and recovery of the original embedding/index runtime. The public preview runs the
same Streamlit interface in the browser with generation disabled.
No recorded answers are used. No model service, paid GPU or billing has been activated.

The public Streamlit frontend calls an authenticated private FastAPI backend.
One pinned Ministral 3B base is loaded once; D1000 and D1500 PEFT adapters are selected
under a single inference lock. Base requests explicitly disable adapters.
RAG uses the original private Nomic/Chroma/BGE pipeline (pool24, top6).
No LLM-as-judge panel, training entry point or replay fallback exists.

| Experiment | Actual SFT rows | Checkpoint | Live status |
|---|---:|---|---|
| Base | n/a | pinned original model | not deployed |
| D500 | unknown | no verified checkpoint | disabled |
| D1000 | 751 | verified LoRA adapter | not deployed |
| D1500 | 1,221 | verified LoRA adapter | not deployed |

Exact public-safe identifiers and hashes: [`config/model_registry.py`](config/model_registry.py).
Private artifact accounts/locations are recorded separately in the owner's research
workspace, never in this public repository. The original base model's pinned card
lists Apache2.0: [model source](https://huggingface.co/unsloth/Ministral-3-3B-Instruct-2512-bnb-4bit/tree/8491af399e7ad92759da849790a5f7e6c2fdfbc4).
That does not grant redistribution rights for private adapters or policy data.

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-test.txt
pytest -q
python scripts/audit_public.py
streamlit run app.py
```

The app starts safely without secrets and reports unavailability. Configure a meeting
access code and backend credentials through Streamlit Secrets, never in Git.
Private GPU startup and approval steps: [deployment](docs/DEPLOYMENT.md).
Meeting sequence: [runbook](docs/DEMO_RUNBOOK.md).
Cost/memory estimates: [hosting](docs/HOSTING.md).
Private mount schema: [manifest](docs/PRIVATE_MANIFEST_SCHEMA.md).
Safety and remaining acceptance gates: [audit](docs/ACCEPTANCE.md).

Public preview details: [FRONTEND_PREVIEW.md](docs/FRONTEND_PREVIEW.md).
Week1/D500 recovery: [WEEK1_RECOVERY.md](docs/WEEK1_RECOVERY.md).


Current strict-budget decision: **Modal is blocked** under the owner's $1-credit /
$0-out-of-pocket conditions. A private free-Kaggle meeting route is prepared but
not activated: [instructions](docs/KAGGLE_MEETING.md), [financial assessment](docs/STRICT_ZERO_COST.md).
The public preview stays unchanged and has no live model connection.
