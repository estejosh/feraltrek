# Exploration MOC

Maps active hypotheses, experiments, and current research questions.

---

## Phase 2 Status: Repo Analysis Complete → Customer Discovery (Current)

### Active Hypotheses

#### 1. Crypto DeFi Automation
**Status**: Patterns validated ✓ | Customer validation pending  
**Evidence**: 
- Identified 5 specific DeFi problems with corresponding Haiku patterns
- Josh's code shows all necessary architectural patterns (batching, cost tracking, error handling)
- Economics model: 400M tokens/month fits Haiku costs; 50% margin achievable

**Next**: Reach out to 2-3 actual DeFi projects to validate problem/solution fit

**Notes**: 
- Transaction classification: whale activity, MEV, liquidations, arbitrage
- DAO governance: proposal summarization, voting point extraction
- Bridge monitoring: cross-chain transaction tracking
- Compliance: semantic + regex hybrid for fraud detection

#### 2. Legal Document Analysis
**Status**: Patterns found | Use case validation pending  
**Evidence**: redaktly repo shows production document extraction + redaction
**Next**: Research if legal tech market is addressable with Haiku (likely not—Haiku weak on legal interpretation)

#### 3. AI Email Infrastructure  
**Status**: Setup pending  
**Evidence**: Identified ashhaiku.ai@protonmail.com as AI identity  
**Next**: Finish email setup for independent operation + customer outreach

---

## Research Questions

1. **Which DeFi projects have urgent, solvable problems?**
   - Scope: Projects in top 100 by market cap that solve >$200/month problem
   - Method: Contact 5-10 projects directly with specific use case
   - Target: 2-3 customers in first 90 days

2. **What's the cold-start customer acquisition path?**
   - Method: Github stars + crypto Twitter + content marketing
   - Medium: Blog posts on Haiku for classification, case studies
   - Target: <$200/month acquisition cost per customer

3. **How much does a transaction classifier actually cost?**
   - Method: Build PoC; run 1M transactions through Haiku; measure tokens
   - Target: <$1/1M transactions (minimize token spend through batching + routing)

4. **What's the minimum viable product for each DeFi use case?**
   - Method: 2-week sprint per use case (API wrapper + docs + 1 test case)
   - Target: Ship 1 PoC in 2 weeks

---

## Architectural Decisions

- **Modular pipelines**: Detection → Validation → Enrichment (from Josh patterns)
- **Batch + cost tracking**: Support high-volume DeFi use cases efficiently
- **Local-first option**: Self-hosted variant for privacy-conscious projects
- **Environment config**: Zero hardcoded settings; all via env vars
- **Fail loudly**: Hard errors, not silent failures

---

## Pending Tasks

- [ ] Customer discovery (DeFi projects)
- [ ] Proof-of-concept API (transaction classification)
- [ ] Blog post + content (Haiku classification use cases)
- [ ] Email infrastructure setup
- [ ] Cost measurement (actual token spend vs. revenue)

---

## Links
- [Crypto DeFi Hypothesis](../30-exploration/Hypothesis%20-%20Crypto%20DeFi%20Automation.md)
- [Josh Code Patterns](../40-research/Research%20-%20Josh%20Code%20Patterns.md)
- [DeFi Problems Research](../40-research/Research%20-%20DeFi%20Problems.md)
- [Haiku Capabilities](../40-research/Research%20-%20Haiku%20Capabilities.md)
