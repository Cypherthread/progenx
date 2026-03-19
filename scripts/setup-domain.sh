#!/bin/bash
# ============================================================================
# Progenx Domain Setup Script
# Run this AFTER purchasing progenx.ai on Cloudflare Registrar
# ============================================================================
#
# Prerequisites:
#   1. Buy progenx.ai on Cloudflare (dash.cloudflare.com → Domain Registration)
#   2. Export your Cloudflare API token:
#      export CF_API_TOKEN="your-token-with-zone-edit-permissions"
#   3. Export your Cloudflare Account ID:
#      export CF_ACCOUNT_ID="9186fbfa465adc3df43c6bf9c833e9cd"
#
# What this script does:
#   - Gets the Zone ID for progenx.ai
#   - Creates DNS records:
#     * progenx.ai → CF Pages (CNAME)
#     * www.progenx.ai → CF Pages (CNAME)
#     * api.progenx.ai → Render (CNAME)
#   - Adds custom domain to CF Pages project
#   - Adds custom domain to Render service
#   - Updates Render env vars (CORS_ORIGINS, FRONTEND_URL)
#
# ============================================================================

set -euo pipefail

CF_API_TOKEN="${CF_API_TOKEN:?Set CF_API_TOKEN}"
CF_ACCOUNT_ID="${CF_ACCOUNT_ID:-9186fbfa465adc3df43c6bf9c833e9cd}"
RENDER_API_KEY="${RENDER_API_KEY:-rnd_pBAAZ3HIufTu041ZU7cheMA4Pd0L}"
RENDER_SERVICE_ID="srv-d6t28pchg0os73fhlb80"
DOMAIN="progenx.ai"

echo "=== Progenx Domain Setup ==="
echo ""

# Step 1: Get Zone ID
echo "[1/6] Getting Zone ID for $DOMAIN..."
ZONE_ID=$(curl -s "https://api.cloudflare.com/client/v4/zones?name=$DOMAIN" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" | python3 -c "import sys,json; print(json.load(sys.stdin)['result'][0]['id'])")
echo "  Zone ID: $ZONE_ID"

# Step 2: Create DNS records
echo "[2/6] Creating DNS records..."

# Root domain → CF Pages
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"type\":\"CNAME\",\"name\":\"$DOMAIN\",\"content\":\"progenx.pages.dev\",\"proxied\":true}" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'  {d[\"result\"][\"name\"]} → {d[\"result\"][\"content\"]} (proxied)' if d['success'] else f'  Error: {d[\"errors\"]}')"

# www → CF Pages
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"type\":\"CNAME\",\"name\":\"www\",\"content\":\"progenx.pages.dev\",\"proxied\":true}" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'  {d[\"result\"][\"name\"]} → {d[\"result\"][\"content\"]} (proxied)' if d['success'] else f'  Error: {d[\"errors\"]}')"

# api → Render
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"type\":\"CNAME\",\"name\":\"api\",\"content\":\"progenx-api.onrender.com\",\"proxied\":false}" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'  {d[\"result\"][\"name\"]} → {d[\"result\"][\"content\"]}' if d['success'] else f'  Error: {d[\"errors\"]}')"

echo ""

# Step 3: Add custom domain to CF Pages
echo "[3/6] Adding progenx.ai to CF Pages..."
curl -s -X POST "https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT_ID/pages/projects/progenx/domains" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"$DOMAIN\"}" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'  Added: {d[\"result\"][\"name\"]}' if d['success'] else f'  Error: {d[\"errors\"]}')"

curl -s -X POST "https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT_ID/pages/projects/progenx/domains" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"www.$DOMAIN\"}" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'  Added: {d[\"result\"][\"name\"]}' if d['success'] else f'  Error: {d[\"errors\"]}')"

echo ""

# Step 4: Add custom domain to Render
echo "[4/6] Adding api.progenx.ai to Render..."
curl -s -X POST "https://api.render.com/v1/services/$RENDER_SERVICE_ID/custom-domains" \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"api.$DOMAIN\"}" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'  Added: {d.get(\"name\", d)}')"

echo ""

# Step 5: Update Render env vars
echo "[5/6] Updating Render env vars..."

# Get current env vars
CURRENT_VARS=$(curl -s "https://api.render.com/v1/services/$RENDER_SERVICE_ID/env-vars" \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Accept: application/json")

# Update CORS_ORIGINS
curl -s -X PUT "https://api.render.com/v1/services/$RENDER_SERVICE_ID/env-vars" \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d "[{\"key\":\"CORS_ORIGINS\",\"value\":\"https://progenx.ai,https://www.progenx.ai\"},{\"key\":\"FRONTEND_URL\",\"value\":\"https://progenx.ai\"}]" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'  Updated {len(d)} env vars')" 2>/dev/null || echo "  Updated env vars"

echo ""

# Step 6: Trigger redeploy
echo "[6/6] Triggering Render redeploy..."
curl -s -X POST "https://api.render.com/v1/services/$RENDER_SERVICE_ID/deploys" \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Accept: application/json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'  Deploy {d[\"id\"]}: {d[\"status\"]}')"

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Verify:"
echo "  Frontend: https://progenx.ai"
echo "  API:      https://api.progenx.ai/api/health"
echo ""
echo "DNS propagation may take 1-5 minutes."
echo ""
echo "IMPORTANT: Also set up www → root redirect:"
echo "  CF Dashboard → Rules → Redirect Rules → Create Rule"
echo "  When: hostname = www.progenx.ai"
echo "  Then: 301 redirect to https://progenx.ai"
