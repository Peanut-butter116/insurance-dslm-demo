# Output-release policy

The verified serving bundle's `public_generation_approved` remains **false**. This
prevents the production API from loading a public-serving runtime. Public metadata
and excerpt allowlists remain empty. No policy source document, passage, model
prediction or artifact credential is added to the public repository/preview.

The optional private smoke runner and supervised Kaggle session can load the same
runtime in private-test mode **only after separate explicit activation approval**.
That mode does not change the bundle's public release flag. It still applies the
existing output-screening/citation filter. It is not a public HTTP endpoint.

- Modal private smoke: returns checkpoint identifiers, actual PEFT selection state,
  latency, GPU memory and answer hashes; no raw answers/questions/policy text are
  returned or written into a receipt. A withheld output fails release; no automatic retry.
- Private Kaggle notebook: the signed-in operator sees output-screened live answers
  for the meeting. Requests use an ephemeral random bearer credential over in-process
  ASGI; there is no listening port, public tunnel, relay or public inference URL.
- Notebook sharing remains Private. Target/source privacy is verified through
  authenticated metadata before private assets are fetched. The operator must supply
  the actual target notebook ref, not an unrelated private ref.
- No raw generated responses or user questions are saved by backend code. Notebook
  outputs can be retained by the notebook platform: clear them before saving/sharing.
- Eight-token overlap screening is conservative and can withhold useful output; it
  does not mathematically prove absence of every short/transformed quotation.
  Therefore it is not used to justify unrestricted public generation.

The public preview only runs application controls and approved aggregate history.
It has no backend credentials or model connection. A server-side Streamlit Community
Cloud deployment would require its own approved private endpoint and release review.
No private Kaggle token or Modal credential may be placed in browser JavaScript.

RAG remains disabled until the original Chroma index, Nomic embedding runtime and
BGE dependency identity are recovered; no paid or substitute retrieval service is
activated. No LLM judging, retraining or historical response replay is part of the demo.
