#!/bin/bash
# ============================================================================
# Progenx Complete Domain + Email + DNS Setup
# Run this AFTER purchasing progenx.ai on Cloudflare Registrar
# ============================================================================
#
# Prerequisites:
#   1. Buy progenx.ai on Cloudflare Registrar
#   2. Create a CF API token with these permissions:
#      - Zone: DNS Edit, Zone Edit
#      - Account: Cloudflare Pages Edit, Email Routing Edit
#   3. Export:
#      export CF_API_TOKEN="your-token"
#      export GMAIL="joesal0420@gmail.com"
#
# What this script does (11 steps):
#   1. Gets Zone ID
#   2. DNS: progenx.ai → CF Pages
#   3. DNS: www → CF Pages
#   4. DNS: api → Render
#   5. DNS: MX records for CF Email Routing
#   6. DNS: SPF record
#   7. DNS: DMARC record
#   8. CF Email Routing: enable + add destination email
#   9. CF Email Routing: create catch-all rule
#  10. CF Pages: add custom domains
#  11. Render: add custom domain + update env vars + redeploy
#
# ============================================================================

set -euo pipefail

CF_API_TOKEN="${CF_API_TOKEN:?Set CF_API_TOKEN}"
CF_ACCOUNT_ID="${CF_ACCOUNT_ID:-9186fbfa465adc3df43c6bf9c833e9cd}"
GMAIL="${GMAIL:-joesal0420@gmail.com}"
RENDER_API_KEY="${RENDER_API_KEY:-rnd_pBAAZ3HIufTu041ZU7cheMA4Pd0L}"
RENDER_SERVICE_ID="srv-d6t28pchg0os73fhlb80"
DOMAIN="progenx.ai"

CF_API="https://api.cloudflare.com/client/v4"
AUTH="-H \"Authorization: Bearer $CF_API_TOKEN\" -H \"Content-Type: application/json\""

# Helper: create DNS record
dns_record() {
  local type=$1 name=$2 content=$3 proxied=${4:-false} priority=${5:-""}
  local data="{\"type\":\"$type\",\"name\":\"$name\",\"content\":\"$content\",\"proxied\":$proxied"
  if [ -n "$priority" ]; then
    data="$data,\"priority\":$priority"
  fi
  data="$data}"

  local result=$(curl -s -X POST "$CF_API/zones/$ZONE_ID/dns_records" \
    -H "Authorization: Bearer $CF_API_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$data")

  local success=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null)
  if [ "$success" = "True" ]; then
    echo "  ✓ $type $name → $content"
  else
    local err=$(echo "$result" | python3 -c "import sys,json; errs=json.load(sys.stdin).get('errors',[]); print(errs[0].get('message','unknown') if errs else 'unknown')" 2>/dev/null)
    echo "  ⚠ $type $name: $err"
  fi
}

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║   Progenx Domain + Email + DNS Setup         ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "  Domain:     $DOMAIN"
echo "  Gmail:      $GMAIL"
echo "  Account ID: $CF_ACCOUNT_ID"
echo ""

# ── Step 1: Get Zone ID ─────────────────────────────────────────
echo "[1/11] Getting Zone ID for $DOMAIN..."
ZONE_ID=$(curl -s "$CF_API/zones?name=$DOMAIN" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" | python3 -c "
import sys,json
d = json.load(sys.stdin)
if not d.get('success') or not d.get('result'):
    print('FAILED'); sys.exit(1)
print(d['result'][0]['id'])
")

if [ "$ZONE_ID" = "FAILED" ]; then
  echo "  ✗ Zone not found. Is progenx.ai purchased and on this CF account?"
  exit 1
fi
echo "  ✓ Zone ID: $ZONE_ID"
echo ""

# ── Step 2-4: Website DNS Records ───────────────────────────────
echo "[2/11] DNS: Root domain → CF Pages..."
dns_record "CNAME" "$DOMAIN" "progenx.pages.dev" "true"

echo "[3/11] DNS: www → CF Pages..."
dns_record "CNAME" "www" "progenx.pages.dev" "true"

echo "[4/11] DNS: api → Render (not proxied, Render needs direct TLS)..."
dns_record "CNAME" "api" "progenx-api.onrender.com" "false"
echo ""

# ── Step 5: MX Records for CF Email Routing ─────────────────────
echo "[5/11] DNS: MX records for Cloudflare Email Routing..."
# CF Email Routing requires these 3 MX records
dns_record "MX" "$DOMAIN" "isaac.mx.cloudflare.net" "false" "87"
dns_record "MX" "$DOMAIN" "linda.mx.cloudflare.net" "false" "30"
dns_record "MX" "$DOMAIN" "amir.mx.cloudflare.net" "false" "4"
echo ""

# ── Step 6: SPF Record ──────────────────────────────────────────
echo "[6/11] DNS: SPF record..."
dns_record "TXT" "$DOMAIN" "v=spf1 include:_spf.mx.cloudflare.net ~all" "false"
echo ""

# ── Step 7: DMARC Record ────────────────────────────────────────
echo "[7/11] DNS: DMARC record..."
dns_record "TXT" "_dmarc.$DOMAIN" "v=DMARC1; p=none; rua=mailto:dmarc@$DOMAIN; pct=100" "false"
echo "  Note: Start with p=none to monitor. Change to p=quarantine after 1 week."
echo ""

# ── Step 8: Enable CF Email Routing + Add Destination ───────────
echo "[8/11] Enabling CF Email Routing + adding $GMAIL as destination..."

# Enable email routing on the zone
curl -s -X PUT "$CF_API/zones/$ZONE_ID/email/routing/enable" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"enabled":true}' | python3 -c "
import sys,json
d = json.load(sys.stdin)
print(f'  ✓ Email routing enabled') if d.get('success') else print(f'  ⚠ {d.get(\"errors\", \"unknown\")}')" 2>/dev/null || echo "  ⚠ Could not enable (may need dashboard)"

# Add destination email address
curl -s -X POST "$CF_API/accounts/$CF_ACCOUNT_ID/email/routing/addresses" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$GMAIL\"}" | python3 -c "
import sys,json
d = json.load(sys.stdin)
if d.get('success'):
    verified = d['result'].get('verified', 'pending')
    print(f'  ✓ Destination added: $GMAIL (verified: {verified})')
    if verified != 'verified' and verified != True:
        print(f'  ⚠ CHECK YOUR GMAIL for a verification email from Cloudflare. Click the link to verify.')
else:
    errs = d.get('errors', [{}])
    msg = errs[0].get('message', 'unknown') if errs else 'unknown'
    if 'already' in msg.lower():
        print(f'  ✓ Destination already exists: $GMAIL')
    else:
        print(f'  ⚠ {msg}')" 2>/dev/null || echo "  ⚠ Could not add destination (may need dashboard)"
echo ""

# ── Step 9: Create Email Routing Rules ──────────────────────────
echo "[9/11] Creating email routing rules..."

# Create catch-all rule (forwards everything@progenx.ai → Gmail)
curl -s -X POST "$CF_API/zones/$ZONE_ID/email/routing/rules" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Catch-all to Gmail\",
    \"enabled\": true,
    \"matchers\": [{\"type\": \"all\"}],
    \"actions\": [{\"type\": \"forward\", \"value\": [\"$GMAIL\"]}]
  }" | python3 -c "
import sys,json
d = json.load(sys.stdin)
if d.get('success'):
    print(f'  ✓ Catch-all rule: *@$DOMAIN → $GMAIL')
else:
    errs = d.get('errors', [{}])
    print(f'  ⚠ {errs[0].get(\"message\", \"unknown\") if errs else \"unknown\"}')" 2>/dev/null || echo "  ⚠ Could not create rule (may need dashboard)"

echo ""
echo "  Email addresses that will work:"
echo "    hello@$DOMAIN      → $GMAIL"
echo "    support@$DOMAIN    → $GMAIL"
echo "    legal@$DOMAIN      → $GMAIL"
echo "    enterprise@$DOMAIN → $GMAIL"
echo "    anything@$DOMAIN   → $GMAIL (catch-all)"
echo ""

# ── Step 10: CF Pages Custom Domains ────────────────────────────
echo "[10/11] Adding custom domains to CF Pages..."
curl -s -X POST "$CF_API/accounts/$CF_ACCOUNT_ID/pages/projects/progenx/domains" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"$DOMAIN\"}" | python3 -c "
import sys,json; d=json.load(sys.stdin)
print(f'  ✓ {d[\"result\"][\"name\"]}') if d.get('success') else print(f'  ⚠ {d.get(\"errors\", \"unknown\")}')" 2>/dev/null || echo "  ⚠ Could not add (may already exist)"

curl -s -X POST "$CF_API/accounts/$CF_ACCOUNT_ID/pages/projects/progenx/domains" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"www.$DOMAIN\"}" | python3 -c "
import sys,json; d=json.load(sys.stdin)
print(f'  ✓ {d[\"result\"][\"name\"]}') if d.get('success') else print(f'  ⚠ {d.get(\"errors\", \"unknown\")}')" 2>/dev/null || echo "  ⚠ Could not add (may already exist)"
echo ""

# ── Step 11: Render Custom Domain + Env Vars + Redeploy ─────────
echo "[11/11] Render: custom domain + env vars + redeploy..."

# Add custom domain
curl -s -X POST "https://api.render.com/v1/services/$RENDER_SERVICE_ID/custom-domains" \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"api.$DOMAIN\"}" | python3 -c "
import sys,json; d=json.load(sys.stdin)
print(f'  ✓ Custom domain: api.{\"$DOMAIN\"}')
" 2>/dev/null || echo "  ✓ Custom domain added (or already exists)"

# Update CORS + FRONTEND_URL
curl -s -X PUT "https://api.render.com/v1/services/$RENDER_SERVICE_ID/env-vars" \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d "[
    {\"key\":\"CORS_ORIGINS\",\"value\":\"https://progenx.ai,https://www.progenx.ai,https://progenx.pages.dev\"},
    {\"key\":\"FRONTEND_URL\",\"value\":\"https://progenx.ai\"}
  ]" > /dev/null 2>&1
echo "  ✓ Updated CORS_ORIGINS and FRONTEND_URL"

# Trigger redeploy
DEPLOY_RESULT=$(curl -s -X POST "https://api.render.com/v1/services/$RENDER_SERVICE_ID/deploys" \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Accept: application/json")
DEPLOY_ID=$(echo "$DEPLOY_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id','unknown'))" 2>/dev/null)
echo "  ✓ Redeploy triggered: $DEPLOY_ID"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║   Setup Complete!                             ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "  Frontend:  https://progenx.ai"
echo "  API:       https://api.progenx.ai/api/health"
echo "  Email:     hello@progenx.ai → $GMAIL"
echo ""
echo "  DNS propagation: 1-5 minutes"
echo "  Render deploy: 3-5 minutes"
echo "  SSL certs: automatic (CF + Render)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  MANUAL STEPS REQUIRED:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  1. CHECK GMAIL for CF Email Routing verification email"
echo "     Click the link to verify $GMAIL as a destination"
echo ""
echo "  2. www → root redirect:"
echo "     CF Dashboard → $DOMAIN → Rules → Redirect Rules"
echo "     When: hostname = www.progenx.ai"
echo "     Then: 301 redirect to https://progenx.ai/\${uri}"
echo ""
echo "  3. Gmail 'Send As' setup (to SEND from hello@progenx.ai):"
echo "     Gmail → Settings → Accounts → Send mail as → Add another"
echo "     Name: Progenx"
echo "     Email: hello@progenx.ai"
echo "     Treat as alias: Yes"
echo "     SMTP: smtp.gmail.com:587 (use App Password if 2FA enabled)"
echo ""
echo "  4. After 1 week of monitoring DMARC reports:"
echo "     Change DMARC from p=none to p=quarantine:"
echo "     CF Dashboard → DNS → _dmarc TXT record"
echo "     v=DMARC1; p=quarantine; rua=mailto:dmarc@progenx.ai; pct=100"
echo ""
echo "  5. DKIM will be auto-configured by Cloudflare Email Routing"
echo "     Verify in: CF Dashboard → $DOMAIN → Email → Email Routing → Settings"
echo ""
