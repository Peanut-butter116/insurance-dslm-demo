# Proposed private meeting output review — approval NOT granted

## Current policy

`public_generation_approved=false`; metadata and excerpt allowlists are empty.
The compatibility smoke returns safe diagnostics and answer hashes only. It cannot
be treated as permission to show remote generated answers. No approval payload
is completed by the developer or by setting environment flags during preparation.

## Proposed permitted display, only after explicit owner approval

- Named Base/D1000/D1500 model-generated answers/refusals to generic insurance
  questions, generated through the exact pinned pipeline, after the existing
  output filter succeeds. No saved-answer replay or other model substitution.
- Actual checkpoint fingerprint, adapter state, training-row count, latency and
  memory diagnostics. A displayed answer is not a guarantee of policy correctness.
- RAG stays disabled. “No verified policy citation available for this answer.”
  Do not release corpus passages or unsupported citation metadata. Keep both
  metadata and excerpt allowlists empty until separately reviewed.
- Arbitrary typed questions need an explicit audience-scoped approval because they
  can be used for extraction attacks; the technical smoke uses one fixed question.
  No personal, financial, claim, health, identification or insurance-eligibility data.

## Who can access

Owner-only Private Space for the technical test. For the meeting, record the exact
HF usernames of the owner and authorised supervisor, access level and expiry before
adding anyone. No public/protected Space fallback, anonymous users, public link
publication, broad organisation access or automatic contributor grants. Private
artifact repository remains owner-only even if the Space has a named collaborator.
Any code-editor/admin capability also needs explicit approval because it may allow
reading runtime files or using secrets, regardless of the UI's output restrictions.

Private Space access is the outer boundary; add a distinct named meeting login with
server-side credentials, at least32-character random password, finite expiry,
12 attempts and3/minute, one active generation. No credentials embedded in a URL.
Ensure quota accounting persists across ZeroGPU worker forks. Rotate/revoke meeting
access and pause the Space afterwards. Already viewed/copied outputs cannot be revoked.

## Residual risks and corpus sufficiency

The eight-token filter blocks normalised exact phrase overlap with inventoried
restricted chunks. It does NOT prove absence of short quotations, paraphrases,
transformed text, non-textual encodings, identifying details, hallucinated private
facts, extraction through repeated prompts, or material memorised from other sources.
Authentication does not remove those risks for authorised users. Generated text
must use a plain textbox; no raw HTML, file output, unreviewed diagnostics or traceback.

The verified private screening corpus is hash-bound to the serving bundle. Its
presence is sufficient for the **existing exact-overlap check**, but it is NOT
proven to cover every protected policy version, all training targets/sources or
all foundation-model memorisation. No completeness certificate or semantic privacy
screen is available. Do not claim the corpus guarantees safe remote output.

Safest current scope is aggregate-only testing. Before answer display, either:

1. Explicitly accept the residual risk for the small named supervised audience and
   exact corpus/adapter versions, with a no-redistribution instruction; or
2. Keep generated answers unavailable until additional coverage/release review is
   complete. Do not retrain, regenerate or substitute synthetic-policy adapters
   without a separate request.

Gradio authentication is basic, not MFA or a complete attack defence. Lock private
file roots, do not expose upload/download/file browsers, disable analytics/flagging/
examples caching and raw prompt/answer logging, sanitise errors, and verify controls
in the actual hosted app before permitting the supervisor's login. Platform access
logs/session cookies may still be retained by HF; no claim of zero platform retention.

## Exact review to complete privately

- Confirmed artifact repo + immutable commit + bundle SHA256.
- Private Space ID + reviewed public-code commit + exact runtime package pins.
- Owner and supervisor HF identities, roles, login scope and expiry.
- Permission to transfer bundle/code/screening corpus to HF (separate from output).
- Permission to display generated answer text for that audience; arbitrary questions
  yes/no; restricted excerpts/metadata remain no unless explicitly allowlisted.
- Residual-risk acceptance, max attempts/rate, free-only resource envelope, stop plan.

All approvals remain pending. Keep the meeting release gate closed until this exact
review is explicitly approved, irrespective of a successful technical GPU test.
