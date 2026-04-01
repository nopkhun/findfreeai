#!/bin/sh
set -e

CONFIG="/home/node/.openclaw/openclaw.json"
mkdir -p /home/node/.openclaw

echo "[bootstrap] Patching openclaw.json with required gateway settings..."

node -e "
const fs = require('fs');
let c = {};
try { c = JSON.parse(fs.readFileSync('$CONFIG', 'utf8')); } catch(e) {}
c.gateway = c.gateway || {};
if (!c.gateway.mode) c.gateway.mode = 'local';
if (!c.gateway.bind) c.gateway.bind = 'lan';
c.gateway.controlUi = c.gateway.controlUi || {};
c.gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback = true;
if (!c.gateway.auth) {
  c.gateway.auth = { mode: 'token', token: 'e06f5a3d50bfe57b6e188939fb36924138b59a55cc7ccd15' };
}
fs.writeFileSync('$CONFIG', JSON.stringify(c, null, 2));
console.log('[bootstrap] Config patched:', JSON.stringify(c.gateway, null, 2));
"

echo "[bootstrap] Starting OpenClaw gateway..."
exec node dist/index.js gateway --bind lan --port 18789 --allow-unconfigured
