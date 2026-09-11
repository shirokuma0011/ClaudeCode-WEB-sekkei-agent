#!/usr/bin/env bash
# Regenerates every PNG in ../images/ from the HTML sources in this directory.
# Requires Playwright (chromium) from /opt/node22/lib/node_modules and IPA Gothic fonts.
# Usage: ./build.sh            -> build all
#        ./build.sh 10_wf_top_pc 11_wf_top_sp   -> build only the named pages
set -euo pipefail
cd "$(dirname "$0")"
export NODE_PATH="${NODE_PATH:-/opt/node22/lib/node_modules}"
node screenshot.js "$@"
echo "--- images ---"
ls -la ../images/*.png
