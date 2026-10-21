---
title: Token Setup - Dual Auth Strategy
aliases: [github tokens, authentication]
tags: [infrastructure, setup]
type: note
created: 2026-09-23
updated: 2026-09-23
status: seedling
related: ["[[AI Email Setup]]"]
---

# Token Setup - GitHub Dual Authentication

## Strategy

Two separate GitHub PATs for different purposes:

### GITHUB_PAT_READONLY
- **Use**: Read-only access to Josh's repos for exploration
- **Scope**: Read access to all estejosh repositories
- **Purpose**: Learning patterns, understanding architecture
- **Repos**: redaktly, ferryman, speakeasy-automations, ursos, telegram-tester, etc.

### GITHUB_PAT_FULL  
- **Use**: Read/write access to haiku-experiments repo
- **Scope**: Full control of estejosh/haiku-experiments
- **Purpose**: Push code, update documentation
- **Repo**: estejosh/haiku-experiments only

## Setup Process

1. Get token values from Josh
2. Run: \.\setup-tokens.ps1 -ReadonlyToken "value1" -FullToken "value2"\
3. Tokens configured locally (not committed)

## Status

- [x] Infrastructure set up (scripts, documentation)
- [ ] Token values received
- [ ] Repos cloned and explored
- [ ] Patterns documented

## Security Notes

- \.env.local\ is gitignored (never committed)
- Tokens only set in local git config
- Each token has minimal required scope

