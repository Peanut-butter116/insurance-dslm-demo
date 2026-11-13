# Verification and public release audit

## What was actually executed

Non-billable local checks use synthetic fixtures and retained aggregate metadata only.35tests cover API auth,
request validation and body limits, configuration routing, no response cache,
persistent quota, concurrency rejection, sanitized errors, citation metadata/excerpt
allowlists, restricted passage withholding, path/hash validation, actual runtime
adapter set/disable control flow with a test double, and Streamlit controls/startup.
Modal1.6.4 imports the app definition offline without a cloud invocation.
These checks do not load a3Bmodel and are not real-model acceptance results.

Public source scan rejects detected token patterns, personal filesystem paths,
private account identities, raw datasets, PDFs, safetensors, model binaries,
SQLite indices and large files. Only explicitly reviewed application code,
configuration, synthetic tests and deployment documentation are published.
No private research Git history is copied. No provider judge tokens are needed.
The frontend receives only a backend URL, scoped API/proxy credentials and meeting code.
Those secrets remain server-side. No questions/answers are stored by application code;
the quota stores timestamps only. Provider infrastructure logs require separate review.

## Acceptance status

| Requirement | Status |
|---|---|
| Clean public application code, isolated feature branch | implemented |
| Streamlit starts without secrets | locally tested; explicit unavailable status |
| Base model identity | exact pinned ID/revision verified |
| D1000/D1500 checkpoint identity | exact archives/weights/manifests reverified in private CPU job; tensor layouts match |
| D500 | disabled; recovered seed adapters have21rows, notD500; separate historical aggregates imported |
| Question entry/examples/config controls | local synthetic UI tests passed |
| API routing/adapter disable and switch logic | synthetic tests passed |
| Auth, limits, serial inference, quota | locally tested |
| Restricted excerpts / error sanitization | locally tested; empty default allowlists |
| Arbitrary output non-disclosure | not proven; release review required |
| Private serving bundle | 189,052,500byte hosted private archive prepared; no local weight download |
| Original index and Nomic service | not recovered; RAG remains blocked |
| Modal GPU image build and adapter loading | not run; approval required |
| Actual base/RAG/D1000/D1500 inference | not tested on proposed deployment |
| Five real meeting scenarios | pending activation; never replaced by mocks |
| Public website preview | deployed on free GitHub Pages/Stlite and browser-tested; inference disabled |
| Server-side Streamlit Community Cloud | manual sign-in needed; not deployed |
| Paid service/billing activation | not performed |

## Known limits that must not be hidden

Private artifact compatibility passed the original research reload audits, but the
new combined runtime still needs its own GPU test. A single prepared PEFT base is
shared; layernorm/dtype preparation follows the original SFT reload path even when
adapters are disabled. This can differ numerically from the original unprepared base
process and should be disclosed in live-demo comparisons. Original evaluation numbers
are unchanged and are not recomputed from this demo.

Nomic and BGE service names alone are not immutable embedding/reranker revisions.
Do not claim exact retrieval equivalence until original runtime/index is recovered.
Historical comparisons used frozen contexts; arbitrary live questions retrieve new
contexts with the same settings, not saved benchmark context replay.

The eight-token output-overlap filter is deliberately conservative, may suppress
useful answers, and cannot prove absence of all short or transformed quotations.
Empty excerpt allowlists do not by themselves prevent generative leakage. Keep the
public-generation approval gate closed until output release policy is reviewed, or
use an explicitly approved synthetic corpus and disclose the changed corpus.
Citation resolution is identifier matching, not a semantic correctness/support score.

Application request quota does not cap cloud spend from startup/health calls. Use
platform proxy auth, meeting code, expiry, max1container, workspace usage/spend caps,
and explicit shutdown. No automatic retries or second model/provider are used.


Final hosted readback confirmed notebook privacy and the entire189,052,500byte
serving bundle hash; all23inventoriedfiles reverified. No private model archive was
downloaded locally. Base/SFT-only startup no longer depends on missing RAG assets;
private screening chunks and public output-release gates remain required.


Current account/budget decision: Modal authentication works, but $0 net-spend
control/credit expiry are unverified; no Modal resource was created. The private
cloud-transfer helper and real-GPU smoke runner are prepared and unexecuted.
The free-Kaggle session is also unactivated. Synthetic tests cover its authenticated
in-process backend, three condition routes, closure and default activation denial.
Official Kaggle quota was checked read-only; account figures remain in private receipts.
This does not claim GPU allocation or a public notebook inference endpoint.
