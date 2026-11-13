# Current decision: Modal blocked; prepare a free supervised Kaggle session

The owner's latest conditions override every earlier $2 proposal: at most $1 of
existing credit, **$0 out of pocket**, no purchases/top-ups/upgrades, no activation
without final explicit approval. The old $2 envelope is withdrawn.

## What is verified

Read-only account checks were performed without creating resources. Actual account
balances, usage, expiry and workspace settings are retained in the owner's private
readiness receipts, not this public repository. An explicit $0 out-of-pocket spend
limit and credit expiry are not established, so Modal remains blocked.

Modal distinguishes gross usage budgets from net out-of-pocket spend limits:
https://modal.com/docs/guide/budgets . A $1 usage limit alone is not evidence of a
$0 net-spend guarantee. The billing SDK does not expose remaining credit/expiry,
payment-method controls or configured spend limits. A logged-in CLI is not proof
that GPU activation satisfies the owner's financial requirements.

**Do not activate Modal or add a payment method under the current verified state.**
Do not change billing settings merely to make the deployment possible. If the
provider cannot enforce an explicit $0 spend limit covering all relevant charges,
Modal must remain unused. Environment-level budgets requiring a paid upgrade are
not an option. The owner must approve any future activation after evidence is reviewed.

## Full resource assessment

Public rates: https://modal.com/pricing . Proposed L4 is $0.000222/s; two physical
CPU cores at $0.0000131/core/s and 16GiB RAM at $0.00000222/GiB/s give a conservative
active reservation estimate of **$0.00028372/s = $1.021392/hour**.

| Item | Cost treatment |
|---|---|
| GPU cold load and three real generations | Same active GPU/CPU/RAM rate; 10min about $0.170232, 15min about $0.255348 |
| CPU-only private transfer | CPU/RAM time is additional; 1core/2GiB for 10min about $0.010524 |
| Image/dependency build | May consume separately billable build CPU/RAM; duration unmeasured; no build started |
| Public base-model download/load | Network/cache/storage plus cold-start time; cannot treat as instantaneous/free |
| Idle window and shutdown | GPU/CPU/RAM continue until the container stops; brief private test uses 2s scaledown |
| Private adapter bundle | 189,052,500bytes, about 0.176GiB; base cache adds about 2.99GiB plus metadata |
| Volume storage | Published $0.09/GiB-month, currently including 1TiB free; account entitlement and charge coverage must be verified |
| Network egress | Published $0.04/GiB beyond included allowance; transfers/allowance must be checked |
| Other workspace usage/tax/fees | Must not be assumed covered by compute credit or this application's request quota |

The API billing summary distinguishes metered cost, adjustments and billed cost.
Record all three before and after any approved run. Do not infer actual charges
from token counts or an estimated GPU runtime.

A brief test might fit the credit, but **testing plus a reliable meeting cannot be
promised within $1** when first-build and cold-start times are unmeasured. Do not plan
to spend the full credit. The activation helper now rejects budgets over $0.60,
requires a verified provider usage cap at most $0.70, a verified $0 net spend limit,
credit/expiry evidence and no auto top-ups. These are safeguards, not authorization;
none of those proof fields is automatically created or treated as currently satisfied.

## Safest next option

Use an existing free Kaggle GPU allocation for a supervised private notebook demo,
with no Colab subscription, paid quota link, third-party tunnel, new cloud storage,
or Modal resources. See KAGGLE_MEETING.md. GPU availability and the owner's remaining
free quota still need confirmation. No GPU session is started by the proposal or tests.
The public website remains an honest no-inference preview throughout.
