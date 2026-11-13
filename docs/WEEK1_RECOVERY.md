# Week 1 / D500 recovery findings

**D500 status: unavailable.** No checkpoint or evaluation tied to a genuine D500
training population was located in the inspected Week1 notes, October training
receipts, manifests, saved predictions, logs and preserved research directories.
No D500 training was started.

The early Ministral and Qwen3B SFT receipts establish **21actualtrainingrows,
4optimizersteps,2epochs**. These adapters cannot be relabelledD500 even where their
architecture matches a later base. The early Ministral adapter fingerprint is
`9c4a952d43c98a6e0f92aaa6cdb10e78e83f39b1101223f6c9a4dc74a6011c46`.
Both140recordsavedpredictionfiles were hash-checked against the retained deterministic
metric reports. No answer text is imported into this public repository.

The frontend's separate historical view contains only two original aggregate rows
(SFT andSFT+RAG), with citation-resolution, balanced-abstention, refusal and parse
counts. It states that these are **notD500results and notliveinference**.
The benchmark has140mixed-insurance questions (118answerable,22unanswerable), unlike
the later76motor-question D1000/D1500 comparison. Correctness and semantic citation
support are not claimed from deterministic reports. No judge protocol was rerun.

Original prompts, frozen context, source corpus and evaluation-era implementations
remain historical conditions. Parse means refusal ORrecognizedcitation; resolution
means identifier matching, not semantic support. Do not pool these numbers with
later experiments or infer a training-size effect.

Exact private artifact locations and file hashes are recorded in the owner's
private research recovery receipt. Only aggregate values and integrity fingerprints
are public. D1000/D1500 registry entries and experimental results are unchanged.

Additional older Qwen7B logs recorded239/265trainingrows; the inspected directories
contained adapter configuration but no local safetensors weights. They are a different
base and had no verifiedD500binding, so are not added to this3B live registry.
