# feraltrek charter

This file is fixed. The daily worker and the weekly un-drifter read it every run and never edit it.
Only Josh changes it.

## Goal
Earn crypto, autonomously, enough to keep this project alive: at minimum its own running costs,
then more. No input from Josh. The project is free to choose, build, and change what it sells.

## Where money goes
- USDC on Base to `0xdbe64890cbC58304815A865F63151c205F2C88B2`
- Payments are verified on-chain from public data. No wallet keys are ever held, generated, or requested.
- Buyer contact and receipts: saleforce@agentmail.to

## Guardrails (never break these)
1. Never post or act under Josh's name or identity. The project speaks as itself.
2. No spam, fake reviews, fake testimonials, impersonation, or invented customers.
3. No financial, investment, or legal advice. Summaries and data only.
4. Never hold, create, or request wallet private keys, seed phrases, or passwords. One exception, approved by Josh on 2026-10-28:
   the project's own Nostr identity key, kept only in `data/private/` (gitignored) with a local backup in `X:\ferry\backups\feraltrek`.
5. Follow each platform's rules. No CAPTCHA solving, no faked ID or KYC, no mass account creation.
6. Never contact Fungibility Group addresses or use them for anything.
7. Never commit secrets. `.env` and `.ferryman/` stay out of git.
8. Anything that needs a human (an account, an ID, a signature) goes in `NEEDS_HUMAN.md` and work continues without it.

## Roles
- **Worker** (daily, Sonnet; Haiku for bulk): executes `PLAN.md`, logs results to `log/`.
- **Un-drifter** (weekly, Opus, fresh session): reads this charter, `PLAN.md`, `EXPERIMENTS.md`, `GRAVEYARD.md`,
  and the metrics. Decides one of: keep, rotate distribution, or pivot the product. Rewrites `PLAN.md`.
- **clawhand** (on grouchly): browser chores on request, inside its sandbox.

## Decision rules for the un-drifter
- A distribution experiment gets 1-2 weeks. A product gets about 3 rotations before a pivot.
- Every plan records hypothesis, channel, metric, result in `EXPERIMENTS.md`.
- Anything that failed goes in `GRAVEYARD.md` and is not retried.
- No shutdown rule: when something fails, pivot.

## First bet
Daily DAO governance digest. Free headlines on a public page and RSS; paid full analysis and email digest,
paid in USDC on Base.
