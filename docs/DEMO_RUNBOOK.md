# Supervisor meeting sequence

**Current status: temporarily unavailable; deployment and real-model verification
pending explicit activation approval.** No saved-answer fallback is shipped publicly.
Use the research performance report offline if activation is not approved in time.

## Before the meeting

Verify spend/credit cap, meeting expiry, allowlist, original private index/embedding
runtime and both checkpoint hashes. Deploy/prewarm only after approval. Open the actual
public Streamlit URL, enter meeting code and confirm Live inference available.
No judge panel is included. Do not assume D1500 is better.

Use the same newly authored example question for scenarios1–4:
“What conditions apply to getting a courtesy car under this motor policy?”
Where the corpus needs a named insurer, specify one whose metadata is approved.
An answerable question may still produce a model refusal; record it honestly.

| Step | SFT | Experiment | RAG | Action and verification |
|---|---|---|---|---|
| 1 | Off | inactive | Off | Generate; check base revision, no verified citations without evidence |
| 2 | Off | inactive | On | Same question; check retrieval status and resolving citation metadata |
| 3 | On | D1000 | On | Generate; verify D1000 adapter hash and751trainingrows |
| 4 | On | D1500 | On | Generate; verify distinct D1500 adapter hash and1221trainingrows |
| 5 | On | D1500 | On | Select unsupported2035premiumquestion; observe actual refusal or failure |

Expand details after each answer. Check the response's configuration, not just sidebar
state: a previously displayed answer keeps its original configuration until Generate
is clicked. Use Copy Answer's text block clipboard control. Excerpts without approval
say “Source reference available; policy excerpt restricted.”

## Acceptance record (must be filled from real deployment)

Record UTC time, public URL, code commit, requested/returned condition and checkpoint,
latency, retrieval source count, citation resolution, actual refusal, peak VRAM and
errors. No correctness/judge evaluation is run. Retest switchingD1000→D1500→Base→D1000
to detect adapter contamination. Hashes must switch, and new generation must execute
each time. Never label the synthetic HTTP tests as these real scenarios.

## Fallback / shutdown

If cold starting, wait for its bounded request rather than clicking repeatedly.
On quota, model-unavailable, output-withheld or retrieval failure, explain the exact
status; do not relabel it as a successful answer/refusal. If the endpoint cannot be
activated, show the existing private performance table separately and state that the
interactive demo is unavailable. No fabricated or replayed live answer.

Stop the Modal app immediately after the meeting, verify the console's stopped state,
revoke access credentials and record actual charges/credits separately. Leave original
research ledgers and checkpoints untouched.
