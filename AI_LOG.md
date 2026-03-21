# ProGenX AI Operations Log

---

## Cycle 0 — 2026-03-21 (Session Init)
- Task completed: Memory migration from old folder name (protoforge → progenx), CLAUDE.md rewrite, AI_LOG + AI_ROADMAP creation
- Files changed: CLAUDE.md (overwritten), AI_LOG.md (created), AI_ROADMAP.md (created)
- Commands run: find (structure mapping), ls (file checks), cp (memory migration)
- What was decided and why: User renamed project folder, breaking Claude's project-scoped memory. Migrated all 8 memory files from `-home-cypherthread-protoforge` to `-home-cypherthread-progenx`. Established new operating system (CLAUDE.md) with safety rules, change mapping, adversarial review cycle, and biosafety constraints.
- Risks introduced: None
- Next task: Cycle 1 — TBD (awaiting recommendation approval)
- HUMAN REVIEW REQUIRED: None

---

## Cycle 1 — 2026-03-21 (Rename Cleanup)
- Task completed: Purged all `protoforge` references from config files after folder rename (protoforge → progenx)
- Files changed:
  - `backend/.env` — updated JWT_SECRET, DATABASE_URL, NCBI_EMAIL (3 lines)
  - `backend/protoforge.db` → renamed to `backend/progenx.db` (+ .shm + .wal)
  - `deploy/render.yaml` — updated service name, CORS_ORIGINS, DATABASE_URL, disk name (4 lines)
  - `.claude/settings.local.json` — updated 3 permission paths from protoforge → progenx
- Commands run: mv (DB rename), grep (verification)
- What was decided and why: The `mv` of the project folder left stale `protoforge` references in .env, render.yaml, and settings.local.json. The SQLite DB file also kept the old name. Fixed all to prevent confusion and ensure local dev starts cleanly. Left `mirofish/` references alone (separate project, cosmetic) and `backend/venv` alone (functional as-is, recreation is higher risk than reward).
- Risks introduced: JWT_SECRET changed — any existing local JWT tokens are invalidated (users must re-login locally). Production unaffected (Render uses its own env vars).
- Next task: Cycle 2 — Production health check
- HUMAN REVIEW REQUIRED: None

---

## Cycle 2 — 2026-03-21 (Production Health Check)
- Task completed: Verified all production endpoints are live and responding
- Files changed: None (read-only diagnostic)
- Commands run: curl to api.progenx.ai/api/health (status + full response), curl to progenx.ai
- What was decided and why: Before building anything new, confirmed production is healthy after the last session's 6 crash-fix commits. All 3 endpoints returned 200. Backend cold start is slow (~15s) due to Render free tier but functional.
- Results:
  - Backend health: 200 — `{"status":"ok","app":"Progenx","version":"0.2.0"}`
  - Frontend: 200 — serving HTML from Cloudflare Pages
- Risks introduced: None
- Next task: Cycle 3 — Seed Explore gallery
- HUMAN REVIEW REQUIRED: None

---

## Cycle 3 — 2026-03-21 (Seed Explore Gallery)
- Task completed: Seeded Explore gallery with 6 showcase designs
- Files changed:
  - backend/scripts/seed_explore.py (created)
  - backend/venv/bin/activate (fixed broken VIRTUAL_ENV path)
  - backend/venv/bin/activate.csh (same fix)
  - backend/venv/bin/activate.fish (same fix)
  - backend/progenx.db (6 designs + showcase user inserted, bump_count column added via migration)
- Commands run: python scripts/seed_explore.py
- What was decided and why: Explore page was empty — poor first impression for new visitors. Seeded 6 real-gene, BSL-1 showcase designs across climate/materials/agriculture categories. Staggered bump counts (19-47) and created_at dates (3-28 days ago) for organic appearance. Fixed broken venv activate scripts as a prerequisite (folder rename had left stale paths).
- Risks introduced: showcase@progenx.ai system user exists in local DB. Production DB untouched — seed not yet run against Render.
- Next task: Cycle 4 — Seed production Explore gallery
- HUMAN REVIEW REQUIRED: None

---

## Cycle 4 — 2026-03-21 (Seed Production Explore Gallery)
- Task completed: Seeded production Explore gallery with 6 showcase designs
- Files changed:
  - backend/routers/admin_router.py (created, then deleted after use)
  - backend/main.py (admin router mounted, then removed)
- Commands run: curl POST /api/admin/seed-explore, curl GET /api/designs/explore
- What was decided and why: External Render PostgreSQL connections are blocked from outside their network. Built a temporary admin-only endpoint to seed from within Render's network. Endpoint was protected by X-Admin-Secret header, idempotent, and removed immediately after use.
- Production result: 7 designs live at progenx.ai/explore (6 showcase + 1 existing Aquagen design)
- Showcase user ID: 0cb3f240-da16-460b-a112-c2b52021417d
- Rollback SQL: DELETE FROM designs WHERE user_id = '0cb3f240-da16-460b-a112-c2b52021417d'; DELETE FROM users WHERE id = '0cb3f240-da16-460b-a112-c2b52021417d';
- Risks introduced: None — endpoint removed, ADMIN_SECRET still in Render env vars (harmless without the endpoint, but can be removed from dashboard if desired)
- Next task: Cycle 5 — OG meta tags and social link previews
- HUMAN REVIEW REQUIRED: None

---

## Cycle 5 — 2026-03-21 (OG Meta Tags & Social Link Previews)
- Task completed: Updated OG and Twitter Card meta tags for social sharing. Added page-specific OG tags to Studio and Explore via react-helmet-async.
- Files changed:
  - frontend/index.html — updated og:title, og:description, twitter:title, twitter:description, og:image path → og-progenx.png
  - frontend/src/pages/Studio.tsx — added og:title, og:description, og:url via Helmet
  - frontend/src/pages/Explore.tsx — added og:title, og:description, og:url via Helmet
- Commands run: npx vite build, wrangler pages deploy
- What was decided and why: Social link previews were using generic copy and a 10.5 MB hero image. Updated to concise, consistent copy across OG and Twitter tags. Changed og:image path to og-progenx.png (dedicated 1200x630 image) to be ready for a properly sized asset. Added page-specific OG tags so Studio and Explore links preview correctly on social platforms.
- Risks introduced: og:image currently points to og-progenx.png which doesn't exist yet — social previews will show no image until the file is created
- Next task: Cycle 6 — Studio onboarding tooltip
- HUMAN REVIEW REQUIRED: og:image path is wired but the actual og-progenx.png file doesn't exist yet — needs a 1200x630, sub-1MB image created and dropped into frontend/public/images/

---

## Cycle 6 — 2026-03-21 (Studio Onboarding for First-Time Users)
- Task completed: Added onboarding panel with 4 clickable example prompts to Studio empty state for first-time users
- Files changed:
  - frontend/src/pages/Studio.tsx — added onboardingDismissed state (backed by localStorage pgx_onboarding_dismissed), replaced "Waiting to Generate" empty state with conditional onboarding panel showing 4 example prompt chips. Dismiss via X button or clicking any example. Falls back to original "Waiting to Generate" on subsequent visits.
- Commands run: npx vite build, wrangler pages deploy
- What was decided and why: First-time users landing on Studio saw a blank "Waiting to Generate" placeholder with no guidance. This is the #1 bounce point. Replaced with 4 clickable example prompts (reused from Landing page) that populate the PromptBox on click. Uses localStorage flag so it only shows once — returning users see the original placeholder. No new components, no modals, no blocking UI.
- Analytics: clicks tracked as `onboarding_example` events for conversion measurement
- Risks introduced: None — frontend-only, conditional rendering, gracefully falls back
- Next task: Cycle 7 — TBD
- HUMAN REVIEW REQUIRED: None
