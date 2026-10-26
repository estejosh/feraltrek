# data/summaries/<proposal id>.json

```json
{
  "id": "<snapshot proposal id>",
  "space": "aave.eth",
  "title": "<proposal title>",
  "url": "https://snapshot.org/#/<space>/proposal/<id>",
  "headline": "One or two plain sentences: what it changes and why it matters. Free tier.",
  "summary": "Full analysis, 120-250 words: what it does, money or parameters involved, who benefits, open questions. Paid tier.",
  "risk_flags": ["short flags, e.g. 'treasury spend 2M USDC', 'changes fee switch', 'low turnout'"],
  "vote": "current tally in one line, e.g. 'For 82% / Against 15% / Abstain 3%, ends 2026-10-30'",
  "written": "YYYY-MM-DD"
}
```

Rules: facts from the proposal only. No advice on how to vote, no price talk, no invented numbers.
If the proposal text is empty or spam, write headline "Low-information proposal" and keep summary short.

Allegations: if a post accuses a person or company of wrongdoing, never state it as fact. Write 'A forum post alleges ...', name no individuals beyond what the post's title already makes public, and add the flag 'unverified allegation'.
Forum items have no vote yet: set vote to 'Discussion stage, no vote yet'.
Off-topic, spam or personal disputes: write the file with "skip": true so it is marked done but never published or emailed.
