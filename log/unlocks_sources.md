# Token unlock sources (feasibility gate, 2026-11-24)

Result: PASS. A free, no-key source exists with well over 30 tokens carrying dated unlock events.

## Chosen source: DefiLlama emissions datasets (static JSON, no key)
- Token list: https://defillama-datasets.llama.fi/emissionsProtocolsList (375 slugs on 11-24)
- Per token: https://defillama-datasets.llama.fi/emissions/<slug> (JSON; metadata.unlockEvents with timestamp, per-recipient cliff and linear allocations, amounts in tokens; metadata.token gives the price id; supplyMetrics has maxSupply etc.)
- Summary table: https://defillama-datasets.llama.fi/emissionsBreakdown (no key)
- Prices (free, no key): https://coins.llama.fi/prices/current/<price id>[,<id>] (id from metadata.token, e.g. coingecko:sui). Some ids return no price (arbitrum did on the first try): skip USD for those, never guess.

## Coverage measured 11-24
- 375 listed, 375 fetched without error, 136 have at least one future unlock event, 86 have an event in the next 30 days.
- Target of 30+ tokens with dated events: met.

## Graveyard (needs payment or blocked)
- https://api.llama.fi/emissions and /emission/<slug> answer 402 Payment Required: do not use.
- https://defillama.com/unlocks answers 403 to scripts: do not use.

## Caveats for the build (11-25)
- Amounts are tokens; USD value = tokens x price when a price exists, else leave blank.
- % of circulating needs a circulating supply; the dataset has max supply, not circulating. Use "% of max supply" labelled as such, or omit. No invented numbers.
- Linear allocations carry start/end times and an amount: spread per day only if the page states it as derived.
- Source link on every page: the token's DefiLlama emissions URL. Facts only, no buy/sell language.
