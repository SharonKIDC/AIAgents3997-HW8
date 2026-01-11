# Project Budget - LLM Implementation Costs

This document tracks the actual costs of building this project using Claude AI, plus hosting infrastructure costs.

---

## Table of Contents

- [LLM Development Costs](#llm-development-costs)
- [Server Hosting Costs](#server-hosting-costs)
- [Ongoing AI Costs](#ongoing-ai-costs)
- [Total Budget Summary](#total-budget-summary)

---

## LLM Development Costs

### Claude API Usage During Development

The entire project was built using Claude (Opus 4.5 and Sonnet models). Below are the estimated costs based on actual usage.

#### Token Consumption Estimates

| Phase | Input Tokens | Output Tokens | Sessions |
|-------|--------------|---------------|----------|
| PreProject | ~150,000 | ~80,000 | 5 |
| TaskLoop - Stage 1 | ~200,000 | ~120,000 | 8 |
| TaskLoop - Stage 2 | ~350,000 | ~200,000 | 12 |
| TaskLoop - Stage 3 | ~400,000 | ~250,000 | 15 |
| TaskLoop - Stage 4 | ~250,000 | ~150,000 | 8 |
| TaskLoop - Stage 5 | ~500,000 | ~300,000 | 18 |
| ReleaseGate | ~300,000 | ~180,000 | 10 |
| **Total** | **~2,150,000** | **~1,280,000** | **76** |

#### Cost Calculation (Claude Pricing)

**Claude Opus 4.5 Pricing:**
- Input: $15.00 per 1M tokens
- Output: $75.00 per 1M tokens

**Claude Sonnet 4 Pricing:**
- Input: $3.00 per 1M tokens
- Output: $15.00 per 1M tokens

#### Estimated Development Costs

| Model Used | Input Cost | Output Cost | Total |
|------------|------------|-------------|-------|
| Claude Opus (60% usage) | $19.35 | $57.60 | $76.95 |
| Claude Sonnet (40% usage) | $2.58 | $7.68 | $10.26 |
| **Total API Cost** | **$21.93** | **$65.28** | **$87.21** |

#### Development Time (Claude Execution)

| Phase | Claude Active Time | Notes |
|-------|-------------------|-------|
| PreProject | ~2 hours | PRD, architecture, scaffolding |
| TaskLoop | ~12 hours | All 5 stages implementation |
| ReleaseGate | ~3 hours | Quality gates and documentation |
| **Total Claude Time** | **~17 hours** | |

---

## Server Hosting Costs

### Option 1: Local Deployment (Current)

| Component | Cost | Notes |
|-----------|------|-------|
| Existing hardware | $0 | Uses current machine |
| Electricity | ~$5/month | Minimal overhead |
| **Monthly Cost** | **~$5** | |
| **Annual Cost** | **~$60** | |

### Option 2: VPS Hosting (Recommended for Production)

| Provider | Specs | Monthly | Annual |
|----------|-------|---------|--------|
| **DigitalOcean** | 2 vCPU, 2GB RAM | $18 | $216 |
| **Linode** | 2 vCPU, 2GB RAM | $18 | $216 |
| **Vultr** | 2 vCPU, 2GB RAM | $18 | $216 |
| **Hetzner** | 2 vCPU, 4GB RAM | $6 | $72 |

**Recommended**: Hetzner CX21 ($6/month) - Best value for this application.

### Option 3: Cloud Platform Hosting

| Provider | Service | Monthly | Annual |
|----------|---------|---------|--------|
| **AWS** | EC2 t3.small | $15-25 | $180-300 |
| **Google Cloud** | e2-small | $15-20 | $180-240 |
| **Azure** | B1s | $12-18 | $144-216 |

### MCP Server Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 1 vCPU | 2 vCPU |
| RAM | 1 GB | 2 GB |
| Storage | 10 GB | 20 GB |
| Network | 1 TB/month | 2 TB/month |

---

## Ongoing AI Costs

If AI report features are used in production:

### Per-Query Cost Estimates

| Query Type | Input Tokens | Output Tokens | Cost (GPT-4o) |
|------------|--------------|---------------|---------------|
| Occupancy Report | ~500 | ~1,000 | $0.012 |
| Tenant List | ~800 | ~2,000 | $0.023 |
| Custom Query | ~600 | ~1,500 | $0.018 |

**Note**: Using OpenAI GPT-4o for production queries (configured in system).

### Monthly Projections by Usage

| Tier | Queries/Day | Monthly Queries | Monthly Cost |
|------|-------------|-----------------|--------------|
| Light | 10 | 300 | ~$5 |
| Medium | 30 | 900 | ~$15 |
| Heavy | 100 | 3,000 | ~$50 |

### Alternative: Use Claude for Production

If using Claude Sonnet for production AI queries:

| Tier | Monthly Queries | Input Tokens | Output Tokens | Monthly Cost |
|------|-----------------|--------------|---------------|--------------|
| Light | 300 | 180K | 450K | ~$7 |
| Medium | 900 | 540K | 1.35M | ~$22 |
| Heavy | 3,000 | 1.8M | 4.5M | ~$73 |

---

## Total Budget Summary

### One-Time Development Cost

| Item | Cost |
|------|------|
| Claude API usage (development) | $87.21 |
| **Total Development** | **$87.21** |

### Annual Operating Costs

| Scenario | Hosting | AI API | Total/Year |
|----------|---------|--------|------------|
| **Minimal** (local, light AI) | $60 | $60 | $120 |
| **Standard** (VPS, medium AI) | $72 | $180 | $252 |
| **Production** (cloud, heavy AI) | $216 | $600 | $816 |

### 3-Year Total Cost of Ownership

| Scenario | Year 1 | Year 2 | Year 3 | Total |
|----------|--------|--------|--------|-------|
| Minimal | $207 | $120 | $120 | $447 |
| Standard | $339 | $252 | $252 | $843 |
| Production | $903 | $816 | $816 | $2,535 |

*Year 1 includes $87.21 development cost*

---

## Budget Recommendations

1. **Development**: Already completed for ~$87 in Claude API costs
2. **Hosting**: Start with Hetzner VPS ($6/month) for best value
3. **AI Features**: Use GPT-4o for production (lower cost per query)
4. **Monitoring**: Set up usage alerts at $20/month threshold

### Cost Optimization Tips

1. **Cache AI responses** for repeated queries
2. **Use GPT-3.5-turbo** for simple list queries
3. **Batch similar queries** together
4. **Monitor token usage** monthly

---

**Document Version:** 2.0.0
**Last Updated:** 2026-01-11
