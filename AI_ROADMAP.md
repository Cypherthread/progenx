# ProGenX AI Roadmap

## Status: LIVE at https://progenx.ai
Last updated: 2026-03-21

---

## IMMEDIATE (Pre-Launch Blockers)
1. **Resend API key** — sign up at resend.com, set RESEND_API_KEY on Render (transactional emails don't work without this)
2. **Cloudflare Email Routing** — enable in dashboard, add Gmail destination, create catch-all rule
3. **Stripe live mode** — create product ($29/mo), set API keys, configure webhook (Pro tier payments blocked)

## SHORT-TERM (Launch Week)
4. Demo video — 60-sec screen recording for landing page
5. OG image — 1200x630 with real product screenshot
6. Seed Explore gallery — 5-8 showcase designs
7. Studio onboarding — first-time user tooltip/tour
8. Monitoring — BetterUptime + Sentry

## MEDIUM-TERM (Post-Launch)
9. LLC formation — Wyoming LLC + EIN + business bank account
10. Launch announcements — Product Hunt, HN, Reddit, Twitter
11. PostgreSQL upgrade — before April 17 expiry ($7/mo Starter)
12. DMARC policy upgrade — p=none → p=quarantine after 1 week of monitoring

## BACKLOG (Feature Expansion)
- Expand NCBI gene registry to 50+ genes
- Add more chassis codon tables (B. subtilis, S. cerevisiae, CHO, HEK293)
- MoClo Level 0/1 assembly support
- Automated silent mutation for restriction site conflicts
- SecureDNA integration (certificates pending)
- SBOL2 conversion for Benchling/iGEM Registry
- Sequence view on plasmid map zoom
- GPU deployment for ESM-2 650M model
- Bayesian scoring for small-N lab feedback
- User-submitted accession override UI
- Benchling/SnapGene export

## CRITICAL DATES
- **April 17, 2026** — PostgreSQL free tier expires (upgrade to $7/mo)
- **~1 week post-launch** — DMARC p=none → p=quarantine
- **Annual** — progenx.ai domain renewal ($160/yr on Cloudflare)
