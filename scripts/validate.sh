#!/usr/bin/env bash
# Validate DocType JSON + Python syntax without a running bench
set -euo pipefail
cd "$(dirname "$0")/.."
python3 - <<'PY'
import json, sys
from pathlib import Path
root = Path('instacertify/instacertify/doctype')
errors = []
for p in root.rglob('*.json'):
    try:
        data = json.loads(p.read_text())
        assert data.get('doctype') == 'DocType'
        assert data.get('name')
        assert 'fields' in data
    except Exception as e:
        errors.append(f"{p}: {e}")
print(f"Validated {len(list(root.rglob('*.json')))} DocType JSON files")
if errors:
    print('\n'.join(errors)); sys.exit(1)
PY
python3 -m compileall -q instacertify
echo "Python compile OK"
# ensure key files exist
for f in \
  instacertify/hooks.py \
  instacertify/public/css/instacertify_theme.css \
  instacertify/www/ic-quote.html \
  deploy/one-click.sh \
  deploy/apps.json
 do
  [[ -f "$f" ]] || { echo "Missing $f"; exit 1; }
 done
echo "All structural checks passed"
